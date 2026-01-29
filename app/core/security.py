from datetime import datetime, timedelta
from typing import Tuple

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

from app.core.config import configs
from app.core.exceptions import AuthError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(subject: dict, expires_delta: timedelta = None) -> Tuple[str, str]:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"exp": expire, **subject}
    encoded_jwt = jwt.encode(payload, configs.SECRET_KEY, algorithm=ALGORITHM)
    expiration_datetime = expire.strftime(configs.DATETIME_FORMAT)
    return encoded_jwt, expiration_datetime


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, configs.SECRET_KEY, algorithms=ALGORITHM)
        return decoded_token if decoded_token["exp"] >= int(round(datetime.utcnow().timestamp())) else None
    except Exception as e:
        return {}


def _keycloak_issuer() -> str:
    server_url = (configs.KEYCLOAK_SERVER_URL or "").rstrip("/")
    realm = configs.KEYCLOAK_REALM or ""
    if not server_url or not realm:
        return ""
    return f"{server_url}/realms/{realm}"


def _keycloak_pem_public_key() -> str:
    public_key = (configs.KEYCLOAK_PUBLIC_KEY or "").strip()
    if not public_key:
        return ""
    if "BEGIN PUBLIC KEY" in public_key:
        return public_key
    return "-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----"


def _verify_keycloak_jwt(jwt_token: str) -> bool:
    issuer = _keycloak_issuer()
    key = _keycloak_pem_public_key()
    if not issuer or not key:
        return False
    try:
        jwt.decode(
            jwt_token,
            key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_aud": False},
        )
        return True
    except JWTError:
        return False


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise AuthError(detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise AuthError(detail="Invalid token or expired token.")
            return credentials.credentials
        raise AuthError(detail="Invalid authorization code.")

    def verify_jwt(self, jwt_token: str) -> bool:
        try:
            payload = decode_jwt(jwt_token)
            if payload:
                return True
        except Exception:
            pass

        return _verify_keycloak_jwt(jwt_token)
