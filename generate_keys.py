import secrets
import string

def generate_secret_key():
    """Generate a secure secret key for production."""
    return secrets.token_urlsafe(32)

def generate_admin_api_key():
    """Generate a secure admin API key."""
    return secrets.token_urlsafe(24)

if __name__ == "__main__":
    print("=== SentinelGuard Security Keys ===")
    print(f"SECRET_KEY={generate_secret_key()}")
    print(f"ADMIN_API_KEY={generate_admin_api_key()}")
    print("\nCopy these values to your .env file")
