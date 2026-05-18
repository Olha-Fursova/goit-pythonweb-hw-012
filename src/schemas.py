from datetime import date, datetime
from pydantic import BaseModel, EmailStr


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: str | None = None


class ContactResponse(ContactModel):
    id: int

    class Config:
        from_attributes = True

class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None = None
    role: str

    class Config:
        from_attributes = True

class UserCache(BaseModel):
    id: int
    username: str
    email: str
    avatar: str | None = None
    confirmed: bool
    created_at: datetime | None = None
    role: str

class ForgotPasswordModel(BaseModel):
    email: EmailStr

class ResetPasswordModel(BaseModel):
    token: str
    new_password: str