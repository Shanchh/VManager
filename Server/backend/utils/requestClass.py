from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class ApiRequest(BaseModel):
    method: str
    content: dict

class CreateUserRequest(BaseModel):
    email: str
    nickname: str

class GetProfileRequest(BaseModel):
    email: str

class oneClickOperationClass(BaseModel):
    operation: str

class oneClickBroadcastClass(BaseModel):
    content: str

class deleteAccountClass(BaseModel):
    data: dict
    
class getServerLogs(BaseModel):
    level: str

class modifyRoleClass(BaseModel):
    role: str
    objId: str