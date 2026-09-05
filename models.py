from datetime import datetime

from sqlalchemy import(
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
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

    items: Mapped[list["CollectionItem"]] = relationship (back_populates="collection")

class Perfume(Base):
    __tablename__ = "catalog_perfumes"
    __table_args__ = UniqueConstraint(
        "catalog_key",
        name="uq_catalog_perfumes_catalog_key",
    ),

    id: Mapped[int] = mapped_column(primary_key=True)

    marca: Mapped[str] = mapped_column(String(100), nullable=False)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    concentracion: Mapped[str] = mapped_column(String(80), nullable=False)

    catalog_key: Mapped[str] = mapped_column(String(400), nullable=False)

    fragrantica_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    collection_items: Mapped[list["CollectionItem"]] = relationship(back_populates="perfume")

class CollectionItem(Base):
    __tablename__ = "collection_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    collection_id: Mapped[int] = mapped_column(
        ForeignKey(
            "collections.id",
            name="fk_collection_items_collection_id_collections",
        ),
        nullable=False,
        index=True,
    )

    perfume_id: Mapped[int] = mapped_column(
        ForeignKey(
            "catalog_perfumes.id",
            name="fk_collection_items_perfume_id_catalog_perfumes",
        ),
        nullable=False,
        index=True,
    )

    tamano_ml: Mapped[int] = mapped_column(nullable=False)

    imagen: Mapped[str | None] = mapped_column(nullable=True)

    collection: Mapped["Collection"] = relationship(back_populates="items")

    perfume: Mapped["Perfume"] = relationship(back_populates="collection_items")