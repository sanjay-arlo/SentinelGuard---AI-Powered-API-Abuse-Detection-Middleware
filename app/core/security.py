"""Security utilities for SentinelGuard."""

import hashlib
import hmac
from typing import Optional
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from starlette.status import HTTP_401_UNAUTHORIZED

from .config import settings
from .exceptions import AuthenticationError


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm="HS256"
    )
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise AuthenticationError("Invalid token")


def verify_api_key(api_key: str, expected_key: Optional[str] = None) -> bool:
    """Verify admin API key."""
    if not api_key:
        return False
    
    # Use provided key or default to settings
    key_to_check = expected_key or settings.admin_api_key
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(
        api_key.encode('utf-8'),
        key_to_check.encode('utf-8')
    )


def hash_string(data: str, salt: Optional[str] = None) -> str:
    """Hash a string using SHA-256."""
    if salt:
        data = f"{data}{salt}"
    
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def generate_fingerprint_hash(components: list[str]) -> str:
    """Generate SHA256 hash for fingerprint components."""
    # Join components with a separator
    combined = "|".join(str(comp) for comp in components if comp)
    
    # Generate SHA256 hash
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def normalize_user_agent(user_agent: str) -> str:
    """Normalize user agent by removing version numbers."""
    if not user_agent:
        return ""
    
    # Common patterns to normalize version numbers
    patterns = [
        (r'Chrome/\d+\.\d+\.\d+\.\d+', 'Chrome/*'),
        (r'Firefox/\d+\.\d+', 'Firefox/*'),
        (r'Safari/\d+\.\d+\.\d+', 'Safari/*'),
        (r'Edge/\d+\.\d+\.\d+\.\d+', 'Edge/*'),
        (r'Opera/\d+\.\d+\.\d+\.\d+', 'Opera/*'),
        (r'PostmanRuntime/\d+\.\d+\.\d+', 'Postman/*'),
        (r'python-requests/\d+\.\d+', 'python-requests/*'),
        (r'curl/\d+\.\d+\.\d+', 'curl/*'),
        (r'wget/\d+\.\d+\.\d+', 'wget/*'),
        (r'httpie/\d+\.\d+\.\d+', 'httpie/*'),
    ]
    
    import re
    normalized = user_agent
    
    for pattern, replacement in patterns:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    
    return normalized


def is_private_ip(ip_address: str) -> bool:
    """Check if IP address is in private range."""
    import ipaddress
    
    try:
        ip = ipaddress.ip_address(ip_address)
        
        # Check private ranges
        private_ranges = [
            ipaddress.ip_network('10.0.0.0/8'),
            ipaddress.ip_network('172.16.0.0/12'),
            ipaddress.ip_network('192.168.0.0/16'),
            ipaddress.ip_network('127.0.0.0/8'),
        ]
        
        return any(ip in network for network in private_ranges)
    
    except ValueError:
        return False


def is_trusted_proxy(ip_address: str) -> bool:
    """Check if IP address is in trusted proxies list."""
    import ipaddress
    
    try:
        ip = ipaddress.ip_address(ip_address)
        
        for proxy in settings.trusted_proxies:
            # Check if it's a CIDR range
            if '/' in proxy:
                network = ipaddress.ip_network(proxy, strict=False)
                if ip in network:
                    return True
            else:
                # Check exact IP match
                if ip == ipaddress.ip_address(proxy):
                    return True
    
    except ValueError:
        pass
    
    return False


def extract_client_ip(
    x_forwarded_for: Optional[str] = None,
    x_real_ip: Optional[str] = None,
    remote_addr: Optional[str] = None
) -> str:
    """Extract client IP from headers, accounting for trusted proxies."""
    
    # Try X-Forwarded-For header (comma-separated list)
    if x_forwarded_for:
        # Get the leftmost IP (original client)
        ips = [ip.strip() for ip in x_forwarded_for.split(',')]
        for ip in ips:
            if ip and not is_trusted_proxy(ip):
                return ip
    
    # Try X-Real-IP header
    if x_real_ip:
        ip = x_real_ip.strip()
        if ip and not is_trusted_proxy(ip):
            return ip
    
    # Fall back to remote address
    if remote_addr:
        return remote_addr.strip()
    
    # Last resort
    return "0.0.0.0"
