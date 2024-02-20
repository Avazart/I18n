from sqlalchemy import BigInteger
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    __abstract__ = True


class User(MappedAsDataclass, Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    locale: Mapped[str | None] = mapped_column(nullable=True)
