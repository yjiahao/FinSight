# simple database set up

from sqlalchemy import create_engine, String, CheckConstraint

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

# define engine
engine = create_engine('sqlite:///../database/finsight_app.db')


# define database schema
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(200),
        CheckConstraint(
            "email LIKE '%@%.%'",
            name="check_email_format"
        ),  # email format check
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)

# create database
Base.metadata.create_all(engine)