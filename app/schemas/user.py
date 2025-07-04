from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class ConfirmRegistrationRequest(BaseModel):
    email: EmailStr
    token: str
    password: str


class ConfirmRegistrationResponse(BaseModel):
    message: str


class CheckAccountResponse(BaseModel):
    message: str
    email: EmailStr
    invite_token: Optional[str] = None


class SignUpRequestSchema(BaseModel):
    email: EmailStr
    token: str


class SignUpResponseSchema(BaseModel):
    email: EmailStr
    message: str


class SignInRequestSchema(BaseModel):
    email: EmailStr
    password: str


class SignUpData(BaseModel):
    email: EmailStr
    token: str
    first_name: str
    last_name: str
    password: constr(min_length=8)


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


class UserToken(BaseModel):
    user_id: int
    company_id: int
    is_admin: bool


class CompleteSignUpRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    company_name: str
    password: str


class CompleteSignUpResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    company_name: str
    password: str


class UserUpdateRequest(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    position_id: Optional[int] = None
