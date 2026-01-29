from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from jose import jwt
from pydantic import ValidationError

from app.core.config import configs
from app.core.container import Container
from app.core.exceptions import AuthError
from app.core.security import ALGORITHM, JWTBearer
from app.model.user import User
from app.schema.auth_schema import Payload
from app.services.user_service import UserService
from app.util.hash import get_rand_hash


def _get_keycloak_claim(payload: dict, key: str):
    return payload.get(key)


def _get_keycloak_roles(payload: dict) -> list:
    realm_access = payload.get("realm_access") or {}
    roles = realm_access.get("roles") or []
    return roles


@inject
def get_current_user(
    token: str = Depends(JWTBearer()),
    service: UserService = Depends(Provide[Container.user_service]),
) -> User:
    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=ALGORITHM)
        token_data = Payload(**payload)
        current_user: User = service.get_by_id(token_data.id)
        if not current_user:
            raise AuthError(detail="User not found")
        return current_user
    except (jwt.JWTError, ValidationError):
        pass

    try:
        payload = jwt.get_unverified_claims(token)
    except Exception:
        raise AuthError(detail="Could not validate credentials")

    sub = _get_keycloak_claim(payload, "sub")
    if not sub:
        raise AuthError(detail="Could not validate credentials")

    email = _get_keycloak_claim(payload, "email")
    preferred_username = _get_keycloak_claim(payload, "preferred_username")
    name = _get_keycloak_claim(payload, "name")

    with service.user_repository.session_factory() as session:
        query = session.query(User).filter(User.keycloak_sub == sub).first()
        if query:
            return query

    local_email = email or preferred_username
    if not local_email:
        raise AuthError(detail="Email not found in token")

    user_token = get_rand_hash()
    created = User(
        email=local_email,
        password="",
        user_token=user_token,
        name=name or preferred_username,
        is_active=True,
        is_superuser=("admin" in _get_keycloak_roles(payload)),
        keycloak_sub=sub,
    )

    # set random password hash (not used for login)
    from app.core.security import get_password_hash

    created.password = get_password_hash(get_rand_hash(32))

    created_user = service.user_repository.create(created)
    return created_user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise AuthError("Inactive user")
    return current_user


def get_current_super_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise AuthError("Inactive user")
    if not current_user.is_superuser:
        raise AuthError("It's not a super user")
    return current_user


def get_current_normal_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise AuthError("Inactive user")
    if current_user.is_superuser:
        return current_user
    return current_user
