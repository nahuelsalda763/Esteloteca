from datetime import datetime

from sqlalchemy import(
    Boolean,
    DateTime,
    String,
    func,
    true
)

from sqlalchemy.orm import(
    DeclarativeBase,
    Mapped,
    mapped_column,
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=true(),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

class Perfume(Base):
    __tablename__ = "perfumes"
    id: Mapped[int] = mapped_column(primary_key=True)

    marca: Mapped[str]
    nombre: Mapped[str]
    concentracion: Mapped[str]
    tamano_ml: Mapped[int]
    fragrantica_url: Mapped[str | None]
    imagen: Mapped[str | None]
    