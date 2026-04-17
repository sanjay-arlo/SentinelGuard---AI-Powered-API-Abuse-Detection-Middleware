"""Constants used throughout the SentinelGuard application."""

from enum import IntEnum

# Rate limiting penalties
BURST_PENALTY = 15
OVER_LIMIT_PENALTY = 30
REGULAR_INTERVAL_PENALTY = 20
SEQUENTIAL_ACCESS_PENALTY = 25
FAILED_AUTH_PENALTY = 20
SUSPICIOUS_UA_PENALTY = 10

# Risk score range
MIN_RISK_SCORE = 0
MAX_RISK_SCORE = 100

# Block duration multipliers based on score
BLOCK_MULTIPLIERS = {
    90: 3.0,  # score >= 90
    70: 2.0,  # score >= 70
    50: 1.0,  # score >= 50 (default)
}

# Additional multipliers for specific patterns
PATTERN_MULTIPLIERS = {
    "auth_failures": 1.5,
    "sequential_access": 1.5,
}

# Redis key patterns
RATE_LIMIT_KEY = "rate:{fingerprint}:{endpoint}"
RISK_SCORE_KEY = "score:{fingerprint}"
BLOCK_KEY = "block:{ip_address}"
REQUEST_HISTORY_KEY = "history:{fingerprint}"
WHITELIST_KEY = "whitelist:{ip_address}"
ENDPOINT_CONFIG_KEY = "config:endpoint:{pattern}"

# Redis TTL values (seconds)
RATE_LIMIT_TTL_FACTOR = 1  # window_seconds + 1
RISK_SCORE_TTL = 300
WHITELIST_TTL = 60
ENDPOINT_CONFIG_TTL = 300
REQUEST_HISTORY_MAX_LENGTH = 100

# HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503

# Request status values
REQUEST_STATUS_ALLOWED = "allowed"
REQUEST_STATUS_BLOCKED = "blocked"
REQUEST_STATUS_WHITELISTED = "whitelisted"

# Headers
X_FORWARDED_FOR = "X-Forwarded-For"
X_REAL_IP = "X-Real-IP"
X_FORWARDED_PROTO = "X-Forwarded-Proto"
X_RATE_LIMIT_LIMIT = "X-RateLimit-Limit"
X_RATE_LIMIT_REMAINING = "X-RateLimit-Remaining"
X_RATE_LIMIT_RESET = "X-RateLimit-Reset"
X_SENTINEL_SCORE = "X-Sentinel-Score"
X_SENTINEL_FINGERPRINT = "X-Sentinel-Fingerprint"
X_REQUEST_ID = "X-Request-ID"
X_SKIP_RATE_LIMIT = "X-Skip-Rate-Limit"

# Time constants
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400
MILLISECONDS_PER_SECOND = 1000

# Pattern detection thresholds
INTERVAL_CV_THRESHOLD = 0.1  # Coefficient of variation for regular intervals
SEQUENTIAL_DETECTION_COUNT = 3  # Minimum consecutive IDs for sequential detection
FAILED_AUTH_THRESHOLD = 3  # Failed auth attempts to trigger penalty
HISTORY_SIZE_FOR_DETECTION = 5  # Number of history items to analyze

# Bot user agent patterns
SUSPICIOUS_UA_PATTERNS = [
    "bot",
    "crawler",
    "spider",
    "scraper",
    "curl",
    "wget",
    "python-requests",
    "httpie",
    "postman",
]

# CIDR ranges for private networks
PRIVATE_NETWORKS = [
    "10.0.0.0/8",
    "172.16.0.0/12", 
    "192.168.0.0/16",
    "127.0.0.0/8",
]

# Default endpoint patterns that require stricter limits
SENSITIVE_ENDPOINTS = [
    "/api/auth/login",
    "/api/auth/register", 
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
    "/api/admin/",
]

# Cache sizes
CONFIG_CACHE_SIZE = 1000
WHITELIST_CACHE_SIZE = 10000


class BlockReason(IntEnum):
    """Enumeration of block reasons."""
    
    RATE_LIMIT_EXCEEDED = 1
    HIGH_RISK_SCORE = 2
    REGULAR_INTERVAL_PATTERN = 3
    SEQUENTIAL_ACCESS_PATTERN = 4
    FAILED_AUTHENTICATION = 5
    SUSPICIOUS_USER_AGENT = 6
    MANUAL_BLOCK = 7


class DetectionType(IntEnum):
    """Enumeration of detection types."""
    
    BURST_DETECTION = 1
    REGULAR_INTERVAL = 2
    SEQUENTIAL_ACCESS = 3
    FAILED_AUTH = 4
    SUSPICIOUS_UA = 5
