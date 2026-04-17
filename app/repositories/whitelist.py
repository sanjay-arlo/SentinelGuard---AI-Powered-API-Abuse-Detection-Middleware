"""Repository for whitelist operations."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, or_, func

from app.db.models.whitelist import Whitelist


class WhitelistRepository:
    """Repository for Whitelist model operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        ip: str,
        reason: str,
        permanent: bool = False,
        duration_hours: Optional[int] = None,
        created_by: str = "system"
    ) -> Whitelist:
        """Create a new whitelist entry."""
        expires_at = None
        if not permanent and duration_hours:
            expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        whitelist = Whitelist(
            ip=ip,
            reason=reason,
            permanent=permanent,
            expires_at=expires_at,
            created_by=created_by
        )
        self.db.add(whitelist)
        await self.db.commit()
        await self.db.refresh(whitelist)
        return whitelist
    
    async def get_by_ip(self, ip: str) -> Optional[Whitelist]:
        """Get whitelist entry for a specific IP."""
        result = await self.db.execute(
            select(Whitelist).where(
                and_(
                    Whitelist.ip == ip,
                    or_(
                        Whitelist.permanent == True,
                        Whitelist.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def is_whitelisted(self, ip: str) -> bool:
        """Check if an IP is currently whitelisted."""
        whitelist_entry = await self.get_by_ip(ip)
        return whitelist_entry is not None
    
    async def get_all(
        self, 
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Whitelist]:
        """Get all whitelist entries."""
        query = select(Whitelist)
        
        if active_only:
            query = query.where(
                or_(
                    Whitelist.permanent == True,
                    Whitelist.expires_at > datetime.utcnow()
                )
            )
        
        query = query.order_by(desc(Whitelist.created_at)).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_active_whitelisted_ips(self) -> List[str]:
        """Get list of all currently whitelisted IPs."""
        result = await self.db.execute(
            select(Whitelist.ip).where(
                or_(
                    Whitelist.permanent == True,
                    Whitelist.expires_at > datetime.utcnow()
                )
            )
        )
        return [row.ip for row in result.all()]
    
    async def remove(self, ip: str, removed_by: str = "system") -> bool:
        """Remove an IP from the whitelist."""
        from sqlalchemy import delete
        
        delete_query = delete(Whitelist).where(Whitelist.ip == ip)
        result = await self.db.execute(delete_query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def cleanup_expired(self) -> int:
        """Remove expired whitelist entries."""
        from sqlalchemy import delete
        
        delete_query = delete(Whitelist).where(
            and_(
                Whitelist.permanent == False,
                Whitelist.expires_at <= datetime.utcnow()
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
    ) -> Optional[Whitelist]:
        """Update expiration time for a whitelisted IP."""
        result = await self.db.execute(
            select(Whitelist).where(Whitelist.ip == ip)
        )
        whitelist = result.scalar_one_or_none()
        
        if whitelist:
            whitelist.expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
            whitelist.updated_at = datetime.utcnow()
            whitelist.updated_by = updated_by
            await self.db.commit()
            await self.db.refresh(whitelist)
        
        return whitelist
    
    async def get_stats(self) -> dict:
        """Get whitelist statistics."""
        # Total active entries
        active_query = select(func.count(Whitelist.id)).where(
            or_(
                Whitelist.permanent == True,
                Whitelist.expires_at > datetime.utcnow()
            )
        )
        active_result = await self.db.execute(active_query)
        active_count = active_result.scalar()
        
        # Permanent entries
        permanent_query = select(func.count(Whitelist.id)).where(
            Whitelist.permanent == True
        )
        permanent_result = await self.db.execute(permanent_query)
        permanent_count = permanent_result.scalar()
        
        # Temporary entries
        temporary_count = active_count - permanent_count
        
        # Expired entries (not cleaned up yet)
        expired_query = select(func.count(Whitelist.id)).where(
            and_(
                Whitelist.permanent == False,
                Whitelist.expires_at <= datetime.utcnow()
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
