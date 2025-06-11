import datetime
import hashlib

import jwt
import yaml

with open("../vars.yaml", "r") as file:
    config = yaml.safe_load(file)
    SECRET_KEY = config.get("EATER_SECRET_KEY", "default_secret_key")
    print(SECRET_KEY)


def get_jwt_secret_key():
    """
    Get the JWT secret key, deriving a 256-bit key if the original is too short.
    This matches the logic used in the chater-auth service.
    """
    if not SECRET_KEY:
        raise ValueError("EATER_SECRET_KEY not set in vars.yaml")
    
    secret_bytes = SECRET_KEY.encode('utf-8')
    
    # If the secret is already 32+ bytes, use it directly
    # Otherwise, derive a 256-bit key using SHA-256
    if len(secret_bytes) >= 32:
        return SECRET_KEY
    else:
        # Derive a 256-bit key from the secret using SHA-256
        hash_obj = hashlib.sha256(secret_bytes)
        derived_key = hash_obj.digest()
        print(f"Secret key was too short ({len(secret_bytes) * 8} bits), derived 256-bit key using SHA-256")
        return derived_key


def generate_token():
    jwt_secret = get_jwt_secret_key()
    payload = {
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=20000),
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "sub": "singularis",
    }
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    decode = jwt.decode(token, jwt_secret, algorithms=["HS256"])
    print(f"Decode {decode}")
    return token


if __name__ == "__main__":
    token = generate_token()
    print(f"{token}")
