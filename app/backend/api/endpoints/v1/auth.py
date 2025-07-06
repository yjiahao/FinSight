from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

from sqlalchemy.orm import Session

from app.backend.database.database import User

from app.backend.models.user import CreateUserRequest
from app.backend.models.token import Token

from app.backend.services.auth_service import get_db, hash_password, authenticate_user, create_access_token, get_current_user

router = APIRouter(tags=['auth'])

# endpoint to register a new user
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    db: Annotated[Session, Depends(get_db)],
    create_user_request: CreateUserRequest
):
    '''
    Endpoint to register a new user.
    It takes a CreateUserRequest object which contains the email and password.
    It hashes the password and saves the user to the database.

    Args:
        db (Session): The database session.
        create_user_request (CreateUserRequest): The request object containing user details.
    
    Returns:
        None: If the user is created successfully, it returns nothing.
    '''
    create_user_model = User(
        email=create_user_request.email,
        # hash the password with bcrypt
        hashed_password=hash_password(create_user_request.password)
    )

    db.add(create_user_model)
    db.commit()

# login endpoint
@router.post("/login", response_model=Token)
async def login_for_access(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    '''
    Endpoint to login a user and return an access token.
    It uses OAuth2PasswordRequestForm to get the username and password.
    It authenticates the user and creates an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the access token and token type.
    '''
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token(user.email, user.id)

    return {'access_token': token, 'token_type': 'bearer'}

# testing endpoint to get current user
@router.get("/me")
async def read_user(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    '''
    Endpoint to get the current authenticated user.
    It uses the get_current_user dependency to retrieve the user from the token.
    If the user is not authenticated, it raises an HTTPException with status code 401.

    Args:
        current_user (dict): The current user retrieved from the JWT token.

    Returns:
        dict: A dictionary containing the current user information.
    '''
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return {"user": current_user}