from datetime import datetime

from sqlalchemy import(
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    false,
    func,
    true,
)

from sqlalchemy.orm import(
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
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

    collections: Mapped[list["Collection"]] = relationship(back_populates="owner")

class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
)

    owner: Mapped["User"] = relationship(back_populates="collections")

    perfumes: Mapped[list["Perfume"]] = relationship(back_populates="collection")
    



class Perfume(Base):
    __tablename__ = "perfumes"
    id: Mapped[int] = mapped_column(primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"), nullable=False)

    marca: Mapped[str]
    nombre: Mapped[str]
    concentracion: Mapped[str]
    tamano_ml: Mapped[int]
    fragrantica_url: Mapped[str | None]
    imagen: Mapped[str | None]

    collection: Mapped["Collection"] = relationship(back_populates="perfumes")
    