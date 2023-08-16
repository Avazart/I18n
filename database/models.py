from sqlalchemy import BigInteger, Integer, ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column
)


class Base(DeclarativeBase):
    __abstract__ = True


class Lang(MappedAsDataclass, Base):
    __tablename__ = "Langs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    short: Mapped[str] = mapped_column(
        String,
        unique=True
    )

    name: Mapped[str] = mapped_column(
        String
    )

    flag: Mapped[str] = mapped_column(
        String
    )


class User(MappedAsDataclass, Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    lang_id: Mapped[int] = mapped_column(
        ForeignKey(
            Lang.id,
        )
    )
