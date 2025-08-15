
import logging
import os
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

SECRET_KEY = str(os.getenv("SECRET_KEY", "your-secret-key-here"))


def get_jwt_secret_key():
    """
    Get the JWT secret key, deriving a 256-bit key if the original is too short.
    """
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable not set")
    secret_bytes = SECRET_KEY.encode('utf-8')
    if len(secret_bytes) >= 32:
        return SECRET_KEY
    else:
        hash_obj = hashlib.sha256(secret_bytes)
        derived_key = hash_obj.digest()
        log.debug("Secret key was too short (%d bits), derived 256-bit key using SHA-256", len(secret_bytes) * 8)
        return derived_key


def verify_jwt_token(token: str):
    jwt_secret = get_jwt_secret_key()
    try:
        decoded_token = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        log.debug("Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        log.debug(f"Invalid token: {str(e)}")
        raise