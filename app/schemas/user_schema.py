from pydantic import BaseModel


class UserCreate(BaseModel):
    # Model for user creation
    username: str
    password: str


class UserLogin(BaseModel):
    # Model for user login
    username: str
    password: str