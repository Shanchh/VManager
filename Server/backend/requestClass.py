from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    account: str
    password: str

class ApiRequest(BaseModel):
    method: str
    content: dict

class CreateUserRequest(BaseModel):
    email: str
    nickname: str

class GetProfileRequest(BaseModel):
    email: str