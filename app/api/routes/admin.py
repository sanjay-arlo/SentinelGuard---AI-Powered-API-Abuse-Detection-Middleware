"""Admin API endpoints for SentinelGuard."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user, get_async_session
from app.repositories.blacklist import BlacklistRepository
from app.repositories.whitelist import WhitelistRepository
from app.repositories.request_log import RequestLogRepository
from app.schemas.admin import BlacklistCreate, WhitelistCreate, BlacklistResponse, WhitelistResponse
from app.core.exceptions import SentinelException

router = APIRouter()


@router.post("/blacklist", response_model=dict)
async def add_to_blacklist(
    blacklist_data: BlacklistCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_admin_user)
):
    """Add an IP to the blacklist."""
    try:
        blacklist_repo = BlacklistRepository(db)
        
        # Check if IP is already blacklisted
        existing = await blacklist_repo.get_by_ip(blacklist_data.ip)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"IP {blacklist_data.ip} is already blacklisted"
            )
        
        # Remove from whitelist if it exists
        whitelist_repo = WhitelistRepository(db)
        await whitelist_repo.remove(blacklist_data.ip, removed_by=current_user.get("username", "admin"))
        
        # Add to blacklist
        blacklist_entry = await blacklist_repo.create(
            ip=blacklist_data.ip,
            reason=blacklist_data.reason,
            permanent=blacklist_data.permanent,
            duration_hours=blacklist_data.duration_hours,
            created_by=current_user.get("username", "admin")
        )
        
        return {
            "message": f"IP {blacklist_data.ip} has been blacklisted",
            "id": blacklist_entry.id,
            "expires_at": blacklist_entry.expires_at.isoformat() if blacklist_entry.expires_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise SentinelException(f"Failed to blacklist IP: {str(e)}")


@router.delete("/blacklist/{ip}", response_model=dict)
async def remove_from_blacklist(
    ip: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_admin_user)
):
    """Remove an IP from the blacklist."""
    try:
        blacklist_repo = BlacklistRepository(db)
        removed = await blacklist_repo.remove(ip, removed_by=current_user.get("username", "admin"))
        
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"IP {ip} is not blacklisted"
            )
        
        return {"message": f"IP {ip} has been removed from the blacklist"}
    except HTTPException:
        raise
    except Exception as e:
        raise SentinelException(f"Failed to remove IP from blacklist: {str(e)}")


@router.post("/whitelist", response_model=dict)
async def add_to_whitelist(
    whitelist_data: WhitelistCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_admin_user)
):
    """Add an IP to the whitelist."""
    try:
        whitelist_repo = WhitelistRepository(db)
        
        # Check if IP is already whitelisted
        existing = await whitelist_repo.get_by_ip(whitelist_data.ip)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"IP {whitelist_data.ip} is already whitelisted"
            )
        
        # Remove from blacklist if it exists
        blacklist_repo = BlacklistRepository(db)
        await blacklist_repo.remove(whitelist_data.ip, removed_by=current_user.get("username", "admin"))
        
        # Add to whitelist
        whitelist_entry = await whitelist_repo.create(
            ip=whitelist_data.ip,
            reason=whitelist_data.reason,
            permanent=whitelist_data.permanent,
            duration_hours=whitelist_data.duration_hours,
            created_by=current_user.get("username", "admin")
        )
        
        return {
            "message": f"IP {whitelist_data.ip} has been whitelisted",
            "id": whitelist_entry.id,
            "expires_at": whitelist_entry.expires_at.isoformat() if whitelist_entry.expires_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise SentinelException(f"Failed to whitelist IP: {str(e)}")


@router.delete("/whitelist/{ip}", response_model=dict)
async def remove_from_whitelist(
    ip: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_admin_user)
):
    """Remove an IP from the whitelist."""
    try:
        whitelist_repo = WhitelistRepository(db)
        removed = await whitelist_repo.remove(ip, removed_by=current_user.get("username", "admin"))
        
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"IP {ip} is not whitelisted"
            )
        
        return {"message": f"IP {ip} has been removed from the whitelist"}
    except HTTPException:
        raise
    except Exception as e:
        raise SentinelException(f"Failed to remove IP from whitelist: {str(e)}")


@router.get("/blacklist", response_model=List[BlacklistResponse])
async def list_blacklist(
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get list of blacklisted IPs."""
    try:
        blacklist_repo = BlacklistRepository(db)
        blacklist_entries = await blacklist_repo.get_all(
            active_only=active_only,
            limit=limit,
            offset=offset
        )
        
        return [
            BlacklistResponse(
                id=entry.id,
                ip=entry.ip,
                reason=entry.reason,
                permanent=entry.permanent,
                expires_at=entry.expires_at,
                created_at=entry.created_at,
                created_by=entry.created_by
            )
            for entry in blacklist_entries
        ]
    except Exception as e:
        raise SentinelException(f"Failed to get blacklist: {str(e)}")


@router.get("/whitelist", response_model=List[WhitelistResponse])
async def list_whitelist(
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get list of whitelisted IPs."""
    try:
        whitelist_repo = WhitelistRepository(db)
        whitelist_entries = await whitelist_repo.get_all(
            active_only=active_only,
            limit=limit,
            offset=offset
        )
        
        return [
            WhitelistResponse(
                id=entry.id,
                ip=entry.ip,
                reason=entry.reason,
                permanent=entry.permanent,
                expires_at=entry.expires_at,
                created_at=entry.created_at,
                created_by=entry.created_by
            )
            for entry in whitelist_entries
        ]
    except Exception as e:
        raise SentinelException(f"Failed to get whitelist: {str(e)}")


@router.get("/stats", response_model=dict)
async def get_admin_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get administrative statistics."""
    try:
        blacklist_repo = BlacklistRepository(db)
        whitelist_repo = WhitelistRepository(db)
        request_repo = RequestLogRepository(db)
        
        blacklist_stats = await blacklist_repo.get_stats()
        whitelist_stats = await whitelist_repo.get_stats()
        recent_stats = await request_repo.get_24h_stats()
        
        return {
            "blacklist": blacklist_stats,
            "whitelist": whitelist_stats,
            "recent_activity": recent_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise SentinelException(f"Failed to get admin stats: {str(e)}")


@router.post("/cleanup", response_model=dict)
async def cleanup_expired_entries(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_admin_user)
):
    """Clean up expired blacklist and whitelist entries."""
    try:
        blacklist_repo = BlacklistRepository(db)
        whitelist_repo = WhitelistRepository(db)
        
        expired_blacklist = await blacklist_repo.cleanup_expired()
        expired_whitelist = await whitelist_repo.cleanup_expired()
        
        return {
            "message": "Cleanup completed",
            "expired_blacklist_entries": expired_blacklist,
            "expired_whitelist_entries": expired_whitelist
        }
    except Exception as e:
        raise SentinelException(f"Failed to cleanup expired entries: {str(e)}")
