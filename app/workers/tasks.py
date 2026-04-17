"""Celery tasks for SentinelGuard background processing."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app

from app.db.session import get_async_session
from app.repositories.request_log import RequestLogRepository
from app.repositories.blacklist import BlacklistRepository
from app.repositories.whitelist import WhitelistRepository
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task class with database session management."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Clean up after successful task completion."""
        pass
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failures."""
        logger.error(f"Task {task_id} failed: {exc}")


@celery_app.task(bind=True, base=DatabaseTask)
def log_request(self, request_data: Dict[str, Any]) -> bool:
    """Log request data asynchronously."""
    try:
        # This would typically log to database or external system
        logger.info(f"Logging request: {request_data.get('ip', 'unknown')} - {request_data.get('endpoint', 'unknown')}")
        return True
    except Exception as e:
        logger.error(f"Failed to log request: {e}")
        return False


@celery_app.task(bind=True, base=DatabaseTask)
def cleanup_old_data(self) -> Dict[str, int]:
    """Clean up old request logs and expired data."""
    try:
        async with get_async_session() as db:
            request_repo = RequestLogRepository(db)
            
            # Delete logs older than retention period (default 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            deleted_count = await request_repo.delete_old_logs(cutoff_date)
            
            logger.info(f"Cleaned up {deleted_count} old request logs")
            
            return {
                "deleted_logs": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        return {"deleted_logs": 0, "error": str(e)}


@celery_app.task(bind=True, base=DatabaseTask)
def update_ip_reputation(self) -> Dict[str, int]:
    """Update IP reputation scores based on recent activity."""
    try:
        async with get_async_session() as db:
            request_repo = RequestLogRepository(db)
            blacklist_repo = BlacklistRepository(db)
            whitelist_repo = WhitelistRepository(db)
            
            # Get IPs with high request rates or suspicious patterns
            suspicious_ips = await request_repo.get_suspicious_ips(
                hours=24, 
                min_requests=1000,
                min_score=70
            )
            
            auto_blacklisted = 0
            for ip_data in suspicious_ips:
                ip = ip_data["ip"]
                score = ip_data["risk_score"]
                
                # Auto-blacklist if score is very high
                if score >= 90:
                    await blacklist_repo.create(
                        ip=ip,
                        reason=f"Auto-blacklisted: High risk score ({score})",
                        permanent=False,
                        duration_hours=24
                    )
                    auto_blacklisted += 1
                    logger.info(f"Auto-blacklisted {ip} with score {score}")
            
            logger.info(f"Updated IP reputation: {auto_blacklisted} auto-blacklisted")
            
            return {
                "suspicious_ips_found": len(suspicious_ips),
                "auto_blacklisted": auto_blacklisted
            }
    except Exception as e:
        logger.error(f"Failed to update IP reputation: {e}")
        return {"suspicious_ips_found": 0, "auto_blacklisted": 0, "error": str(e)}


@celery_app.task(bind=True, base=DatabaseTask)
def generate_threat_report(self) -> Dict[str, Any]:
    """Generate daily threat intelligence report."""
    try:
        async with get_async_session() as db:
            request_repo = RequestLogRepository(db)
            blacklist_repo = BlacklistRepository(db)
            
            # Get statistics for the last 24 hours
            stats = await request_repo.get_24h_stats()
            blocked_ips = await blacklist_repo.get_active_blocked_ips()
            
            report = {
                "generated_at": datetime.utcnow().isoformat(),
                "period_hours": 24,
                "total_requests": stats.get("total_requests", 0),
                "unique_ips": stats.get("unique_ips", 0),
                "blocked_requests": stats.get("blocked_requests", 0),
                "top_attack_types": stats.get("top_attack_types", []),
                "currently_blocked_ips": len(blocked_ips),
                "high_risk_ips": stats.get("high_risk_ips", 0)
            }
            
            logger.info(f"Generated threat report: {report['total_requests']} requests analyzed")
            
            return report
    except Exception as e:
        logger.error(f"Failed to generate threat report: {e}")
        return {"error": str(e), "generated_at": datetime.utcnow().isoformat()}


@celery_app.task(bind=True, base=DatabaseTask)
def check_system_health(self) -> Dict[str, Any]:
    """Perform system health checks."""
    try:
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Check database connectivity
        try:
            async with get_async_session() as db:
                await db.execute("SELECT 1")
                health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["checks"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check Redis connectivity (if implemented)
        # This would require Redis client implementation
        
        logger.info(f"System health check: {health_status['status']}")
        
        return health_status
    except Exception as e:
        logger.error(f"Failed to perform health check: {e}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        }
