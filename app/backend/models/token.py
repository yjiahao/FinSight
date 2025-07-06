from pydantic import BaseModel

# class for /token endpoint to validate the response
class Token(BaseModel):
    access_token: str
    token_type: str