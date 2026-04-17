"""Repository for request log operations."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.db.models.request_log import RequestLog


class RequestLogRepository:
    """Repository for RequestLog model operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, **kwargs) -> RequestLog:
        """Create a new request log entry."""
        request_log = RequestLog(**kwargs)
        self.db.add(request_log)
        await self.db.commit()
        await self.db.refresh(request_log)
        return request_log
    
    async def get_by_ip(self, ip: str, limit: int = 100) -> List[RequestLog]:
        """Get recent requests for a specific IP."""
        result = await self.db.execute(
            select(RequestLog)
            .where(RequestLog.ip == ip)
            .order_by(desc(RequestLog.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent_requests(
        self, 
        hours: int = 24, 
        limit: int = 1000
    ) -> List[RequestLog]:
        """Get recent requests within the specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = await self.db.execute(
            select(RequestLog)
            .where(RequestLog.created_at >= cutoff)
            .order_by(desc(RequestLog.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_suspicious_ips(
        self, 
        hours: int = 24, 
        min_requests: int = 100,
        min_score: int = 50
    ) -> List[Dict[str, Any]]:
        """Get IPs with suspicious activity patterns."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(
            RequestLog.ip,
            func.count(RequestLog.id).label('request_count'),
            func.avg(RequestLog.risk_score).label('avg_score'),
            func.max(RequestLog.risk_score).label('max_score'),
            func.count(func.nullif(RequestLog.blocked, False)).label('blocked_count')
        ).where(
            and_(
                RequestLog.created_at >= cutoff,
                RequestLog.risk_score >= min_score
            )
        ).group_by(
            RequestLog.ip
        ).having(
            func.count(RequestLog.id) >= min_requests
        ).order_by(
            desc(func.avg(RequestLog.risk_score))
        )
        
        result = await self.db.execute(query)
        return [
            {
                "ip": row.ip,
                "request_count": row.request_count,
                "avg_score": float(row.avg_score),
                "max_score": row.max_score,
                "blocked_count": row.blocked_count,
                "risk_score": float(row.avg_score)  # For compatibility
            }
            for row in result.all()
        ]
    
    async def get_24h_stats(self) -> Dict[str, Any]:
        """Get statistics for the last 24 hours."""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        # Total requests
        total_query = select(func.count(RequestLog.id)).where(
            RequestLog.created_at >= cutoff
        )
        total_result = await self.db.execute(total_query)
        total_requests = total_result.scalar()
        
        # Unique IPs
        unique_ips_query = select(func.count(func.distinct(RequestLog.ip))).where(
            RequestLog.created_at >= cutoff
        )
        unique_ips_result = await self.db.execute(unique_ips_query)
        unique_ips = unique_ips_result.scalar()
        
        # Blocked requests
        blocked_query = select(func.count(RequestLog.id)).where(
            and_(
                RequestLog.created_at >= cutoff,
                RequestLog.blocked == True
            )
        )
        blocked_result = await self.db.execute(blocked_query)
        blocked_requests = blocked_result.scalar()
        
        # High risk IPs
        high_risk_query = select(func.count(func.distinct(RequestLog.ip))).where(
            and_(
                RequestLog.created_at >= cutoff,
                RequestLog.risk_score >= 80
            )
        )
        high_risk_result = await self.db.execute(high_risk_query)
        high_risk_ips = high_risk_result.scalar()
        
        # Top attack types (by endpoint)
        attack_types_query = select(
            RequestLog.endpoint,
            func.count(RequestLog.id).label('count')
        ).where(
            and_(
                RequestLog.created_at >= cutoff,
                RequestLog.blocked == True
            )
        ).group_by(
            RequestLog.endpoint
        ).order_by(
            desc(func.count(RequestLog.id))
        ).limit(10)
        
        attack_types_result = await self.db.execute(attack_types_query)
        top_attack_types = [
            {"endpoint": row.endpoint, "count": row.count}
            for row in attack_types_result.all()
        ]
        
        return {
            "total_requests": total_requests,
            "unique_ips": unique_ips,
            "blocked_requests": blocked_requests,
            "high_risk_ips": high_risk_ips,
            "top_attack_types": top_attack_types
        }
    
    async def delete_old_logs(self, cutoff_date: datetime) -> int:
        """Delete request logs older than the cutoff date."""
        from sqlalchemy import delete
        
        delete_query = delete(RequestLog).where(
            RequestLog.created_at < cutoff_date
        )
        result = await self.db.execute(delete_query)
        await self.db.commit()
        return result.rowcount
    
    async def get_ip_activity_summary(
        self, 
        ip: str, 
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get activity summary for a specific IP."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(
            func.count(RequestLog.id).label('total_requests'),
            func.avg(RequestLog.risk_score).label('avg_score'),
            func.max(RequestLog.risk_score).label('max_score'),
            func.count(func.nullif(RequestLog.blocked, False)).label('blocked_count'),
            func.min(RequestLog.created_at).label('first_seen'),
            func.max(RequestLog.created_at).label('last_seen')
        ).where(
            and_(
                RequestLog.ip == ip,
                RequestLog.created_at >= cutoff
            )
        )
        
        result = await self.db.execute(query)
        row = result.first()
        
        if not row:
            return {
                "ip": ip,
                "total_requests": 0,
                "avg_score": 0,
                "max_score": 0,
                "blocked_count": 0,
                "first_seen": None,
                "last_seen": None
            }
        
        return {
            "ip": ip,
            "total_requests": row.total_requests,
            "avg_score": float(row.avg_score) if row.avg_score else 0,
            "max_score": row.max_score or 0,
            "blocked_count": row.blocked_count,
            "first_seen": row.first_seen.isoformat() if row.first_seen else None,
            "last_seen": row.last_seen.isoformat() if row.last_seen else None
        }
