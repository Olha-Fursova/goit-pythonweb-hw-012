"""
Pydantic schemas for request/response validation.
"""
 
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
 
 
class ContactModel(BaseModel):
    """Schema for creating or updating a contact."""
 
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: date
    additional_data: Optional[str] = Field(default=None, max_length=250)
 
 
class ContactResponse(ContactModel):
    """Schema for returning a contact in API responses."""
 
    id: int
 
    model_config = {"from_attributes": True}
 
 
class UserModel(BaseModel):
    """Schema for user registration."""
 
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
 
 
class UserResponse(BaseModel):
    """Schema for returning a user in API responses."""
 
    id: int
    username: str
    email: EmailStr
    confirmed: bool
    role: str
 
    model_config = {"from_attributes": True}
 
 
class UserCache(BaseModel):
    """Schema for caching user data in Redis."""
 
    id: int
    username: str
    email: str
    avatar: Optional[str] = None
    confirmed: bool
    created_at: Optional[str] = None
    role: str
 
    model_config = {"from_attributes": True}
 
 
class TokenModel(BaseModel):
    """Schema for JWT token response."""
 
    access_token: str
    token_type: str = "bearer"
 
 
class ForgotPasswordModel(BaseModel):
    """Schema for forgot-password request."""
 
    email: EmailStr
 
 
class ResetPasswordModel(BaseModel):
    """Schema for reset-password request."""
 
    token: str
    new_password: str = Field(min_length=6)