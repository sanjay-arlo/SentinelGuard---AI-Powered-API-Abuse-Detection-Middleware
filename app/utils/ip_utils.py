"""IP address utilities for SentinelGuard."""

import ipaddress
from typing import List, Optional


def is_valid_ip(ip_address: str) -> bool:
    """Check if IP address is valid."""
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def is_private_ip(ip_address: str) -> bool:
    """Check if IP address is in private range."""
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip.is_private
    except ValueError:
        return False


def is_loopback_ip(ip_address: str) -> bool:
    """Check if IP address is loopback."""
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip.is_loopback
    except ValueError:
        return False


def normalize_ip(ip_address: str) -> str:
    """Normalize IP address string."""
    try:
        ip = ipaddress.ip_address(ip_address)
        return str(ip)
    except ValueError:
        return ip_address


def extract_ip_from_forwarded_header(x_forwarded_for: str) -> Optional[str]:
    """Extract the original client IP from X-Forwarded-For header."""
    if not x_forwarded_for:
        return None
    
    # X-Forwarded-For can contain multiple IPs, the first one is the original client
    ips = [ip.strip() for ip in x_forwarded_for.split(',')]
    if ips and is_valid_ip(ips[0]):
        return normalize_ip(ips[0])
    
    return None


def extract_ip_from_real_ip_header(x_real_ip: str) -> Optional[str]:
    """Extract IP from X-Real-IP header."""
    if not x_real_ip:
        return None
    
    ip = x_real_ip.strip()
    if is_valid_ip(ip):
        return normalize_ip(ip)
    
    return None


def ip_in_cidr(ip_address: str, cidr: str) -> bool:
    """Check if IP address is in CIDR range."""
    try:
        ip = ipaddress.ip_address(ip_address)
        network = ipaddress.ip_network(cidr, strict=False)
        return ip in network
    except ValueError:
        return False


def ip_in_cidr_list(ip_address: str, cidr_list: List[str]) -> bool:
    """Check if IP address is in any of the CIDR ranges."""
    for cidr in cidr_list:
        if ip_in_cidr(ip_address, cidr):
            return True
    return False


def get_client_ip(
    x_forwarded_for: Optional[str] = None,
    x_real_ip: Optional[str] = None,
    remote_addr: Optional[str] = None,
) -> str:
    """Extract client IP from headers, prioritizing X-Forwarded-For."""
    
    # Try X-Forwarded-For first
    if x_forwarded_for:
        client_ip = extract_ip_from_forwarded_header(x_forwarded_for)
        if client_ip:
            return client_ip
    
    # Try X-Real-IP
    if x_real_ip:
        client_ip = extract_ip_from_real_ip_header(x_real_ip)
        if client_ip:
            return client_ip
    
    # Fall back to remote address
    if remote_addr and is_valid_ip(remote_addr):
        return normalize_ip(remote_addr)
    
    # Last resort
    return "0.0.0.0"
