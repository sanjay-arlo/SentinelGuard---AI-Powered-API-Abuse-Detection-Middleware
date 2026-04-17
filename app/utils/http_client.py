"""HTTP client for downstream API requests."""

import httpx
from typing import Optional, Dict, Any

from ..core.config import settings
from ..core.exceptions import DownstreamServiceError


# Global HTTP client instance
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    """Get HTTP client instance."""
    global _http_client
    
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=settings.downstream_api_timeout,
            follow_redirects=True,
        )
    
    return _http_client


async def close_http_client() -> None:
    """Close HTTP client."""
    global _http_client
    
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


async def forward_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[str] = None,
) -> httpx.Response:
    """Forward request to downstream API."""
    
    client = get_http_client()
    
    try:
        # Build the full downstream URL
        downstream_url = f"{settings.downstream_api_url.rstrip('/')}{url}"
        
        response = await client.request(
            method=method,
            url=downstream_url,
            headers=headers,
            params=params,
            json=json,
            content=data,
        )
        
        return response
    
    except httpx.TimeoutException:
        raise DownstreamServiceError("Downstream service timeout")
    except httpx.ConnectError:
        raise DownstreamServiceError("Cannot connect to downstream service")
    except Exception as e:
        raise DownstreamServiceError(f"Downstream service error: {e}")
