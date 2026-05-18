"""
SQLAlchemy ORM models for the Contacts REST API.
 
Defines the database schema for User and Contact entities.
"""
 
from datetime import date, datetime
 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, Boolean, ForeignKey, DateTime
 
 
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass
 
 
class Contact(Base):
    """
    Represents a contact belonging to a user.
 
    :param id: Primary key.
    :param first_name: Contact's first name (max 50 chars).
    :param last_name: Contact's last name (max 50 chars).
    :param email: Contact's unique email address.
    :param phone: Contact's phone number.
    :param birthday: Contact's date of birth.
    :param additional_data: Optional extra information.
    :param user_id: Foreign key referencing the owning User.
    """
 
    __tablename__ = "contacts"
 
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    first_name: Mapped[str] = mapped_column(String(50))

    last_name: Mapped[str] = mapped_column(String(50))

    email: Mapped[str] = mapped_column(String(120), unique=True)

    phone: Mapped[str] = mapped_column(String(20))

    birthday: Mapped[date] = mapped_column(Date)

    additional_data: Mapped[str] = mapped_column(String(250), nullable=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
 
    user = relationship("User", back_populates="contacts")
 
 
class User(Base):
    """
    Represents a registered user account.
 
    :param id: Primary key.
    :param username: Unique username (max 50 chars).
    :param email: Unique email address (max 120 chars).
    :param hashed_password: Bcrypt-hashed password string.
    :param created_at: Date the account was created.
    :param avatar: Optional URL to the user's avatar image.
    :param confirmed: Whether the user's email has been verified.
    :param verification_token: UUID token used for email verification.
    :param role: User role — either ``user`` or ``admin``.
    :param reset_token: UUID token used for password reset.
    :param reset_token_expires: Expiry datetime for the reset token.
    """
 
    __tablename__ = "users"
 
    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(50), unique=True)

    email: Mapped[str] = mapped_column(String(120), unique=True)

    hashed_password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[date] = mapped_column(default=date.today)

    avatar: Mapped[str] = mapped_column(String(255), nullable=True)

    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    verification_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    role: Mapped[str] = mapped_column(String, default="user", nullable=False)

    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    reset_token_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
 
    contacts = relationship("Contact", back_populates="user")