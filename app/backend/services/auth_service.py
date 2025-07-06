from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from typing import Annotated, Union

from fastapi import Depends, HTTPException, status

import jwt
from jwt.exceptions import InvalidTokenError

from app.backend.core.config import settings

from app.backend.database.session import SessionLocal

from app.backend.database.database import User

from app.backend.core.security import bcrypt_context, oauth2_bearer

def get_db():
    '''
    Get a database session.
    '''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    '''
    Hash a password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    '''
    return bcrypt_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Union[User, bool]:
    '''
    Authenticate a user by checking the email and password.

    Args:
        db (Session): The database session.
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        User: The authenticated user if the email and password are correct, otherwise False.
    '''
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        # verify the password with bcrypt
        return False
    return user

def create_access_token(email: str, id: int, expires_delta: timedelta=None) -> str:
    '''
    Creates a JWT access token for the user and encodes it.

    Args:
        email (str): The user's email.
        id (int): The user's ID.
        expires_delta (timedelta, optional): The expiration time for the token. If None, the token does not expire.

    Returns:
        str: The encoded JWT token.
    '''
    to_encode = {'sub': email, 'id': id}
    if expires_delta:
        expires = datetime.datetime.now(timezone.utc) + expires_delta
        to_encode.update({'exp': expires})
    # if expires_delta is None, no 'exp' claim is set (token never expires)
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Annotated[Session, Depends(get_db)]):
    '''
    Get the current user from the JWT token.

    Args:
        token (str): The JWT token from the request.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the user's email and ID if the token is valid.
    '''
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {'email': email, 'id': user_id}
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
