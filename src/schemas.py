from datetime import date
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

    class Config:
        from_attributes = True