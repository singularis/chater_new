import datetime

import jwt
import yaml

with open("../vars.yaml", "r") as file:
    config = yaml.safe_load(file)
    SECRET_KEY = config.get("EATER_SECRET_KEY", "default_secret_key")
    print(SECRET_KEY)


def generate_token():
    payload = {
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=20000),
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "sub": "singularis",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    decode = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print(f"Decode {decode}")
    return token


if __name__ == "__main__":
    token = generate_token()
    print(f"{token}")
