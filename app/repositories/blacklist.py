"""Repository for blacklist operations."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, or_, func

from app.db.models.blacklist import Blacklist


class BlacklistRepository:
    """Repository for Blacklist model operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        ip: str,
        reason: str,
        permanent: bool = False,
        duration_hours: Optional[int] = None,
        created_by: str = "system"
    ) -> Blacklist:
        """Create a new blacklist entry."""
        expires_at = None
        if not permanent and duration_hours:
            expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        blacklist = Blacklist(
            ip=ip,
            reason=reason,
            permanent=permanent,
            expires_at=expires_at,
            created_by=created_by
        )
        self.db.add(blacklist)
        await self.db.commit()
        await self.db.refresh(blacklist)
        return blacklist
    
    async def get_by_ip(self, ip: str) -> Optional[Blacklist]:
        """Get blacklist entry for a specific IP."""
        result = await self.db.execute(
            select(Blacklist).where(
                and_(
                    Blacklist.ip == ip,
                    or_(
                        Blacklist.permanent == True,
                        Blacklist.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def is_blacklisted(self, ip: str) -> bool:
        """Check if an IP is currently blacklisted."""
        blacklist_entry = await self.get_by_ip(ip)
        return blacklist_entry is not None
    
    async def get_all(
        self, 
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Blacklist]:
        """Get all blacklist entries."""
        query = select(Blacklist)
        
        if active_only:
            query = query.where(
                or_(
                    Blacklist.permanent == True,
                    Blacklist.expires_at > datetime.utcnow()
                )
            )
        
        query = query.order_by(desc(Blacklist.created_at)).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_active_blocked_ips(self) -> List[str]:
        """Get list of all currently blocked IPs."""
        result = await self.db.execute(
            select(Blacklist.ip).where(
                or_(
                    Blacklist.permanent == True,
                    Blacklist.expires_at > datetime.utcnow()
                )
            )
        )
        return [row.ip for row in result.all()]
    
    async def remove(self, ip: str, removed_by: str = "system") -> bool:
        """Remove an IP from the blacklist."""
        from sqlalchemy import delete
        
        delete_query = delete(Blacklist).where(Blacklist.ip == ip)
        result = await self.db.execute(delete_query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def cleanup_expired(self) -> int:
        """Remove expired blacklist entries."""
        from sqlalchemy import delete
        
        delete_query = delete(Blacklist).where(
            and_(
                Blacklist.permanent == False,
                Blacklist.expires_at <= datetime.utcnow()
            )
        )
        result = await self.db.execute(delete_query)
        await self.db.commit()
        return result.rowcount
    
    async def update_expiration(
        self, 
        ip: str, 
        duration_hours: int,
        updated_by: str = "system"
    ) -> Optional[Blacklist]:
        """Update expiration time for a blacklisted IP."""
        result = await self.db.execute(
            select(Blacklist).where(Blacklist.ip == ip)
        )
        blacklist = result.scalar_one_or_none()
        
        if blacklist:
            blacklist.expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
            blacklist.updated_at = datetime.utcnow()
            blacklist.updated_by = updated_by
            await self.db.commit()
            await self.db.refresh(blacklist)
        
        return blacklist
    
    async def get_stats(self) -> dict:
        """Get blacklist statistics."""
        # Total active entries
        active_query = select(func.count(Blacklist.id)).where(
            or_(
                Blacklist.permanent == True,
                Blacklist.expires_at > datetime.utcnow()
            )
        )
        active_result = await self.db.execute(active_query)
        active_count = active_result.scalar()
        
        # Permanent entries
        permanent_query = select(func.count(Blacklist.id)).where(
            Blacklist.permanent == True
        )
        permanent_result = await self.db.execute(permanent_query)
        permanent_count = permanent_result.scalar()
        
        # Temporary entries
        temporary_count = active_count - permanent_count
        
        # Expired entries (not cleaned up yet)
        expired_query = select(func.count(Blacklist.id)).where(
            and_(
                Blacklist.permanent == False,
                Blacklist.expires_at <= datetime.utcnow()
            )
        )
        expired_result = await self.db.execute(expired_query)
        expired_count = expired_result.scalar()
        
        return {
            "active_count": active_count,
            "permanent_count": permanent_count,
            "temporary_count": temporary_count,
            "expired_count": expired_count
        }
