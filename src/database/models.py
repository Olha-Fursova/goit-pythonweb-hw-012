from datetime import date

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, Boolean, ForeignKey


class Base(DeclarativeBase):
    pass


class Contact(Base):
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
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(50), unique=True)

    email: Mapped[str] = mapped_column(String(120), unique=True)

    hashed_password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[date] = mapped_column(default=date.today)

    avatar: Mapped[str] = mapped_column(String(255), nullable=True)

    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    verification_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    contacts = relationship("Contact", back_populates="user")