from pydantic import BaseModel

# class to ensure user schema is valid when user is registering via API
class CreateUserRequest(BaseModel):
    email: str
    password: str