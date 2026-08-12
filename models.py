from sqlalchemy.orm import(
    DeclarativeBase,
    Mapped,
    mapped_column,
)

class Base(DeclarativeBase):
    pass

class Perfume(Base):
    __tablename__ = "perfumes"
    id: Mapped[int] = mapped_column(primary_key=True)

    marca: Mapped[str]
    nombre: Mapped[str]
    concentracion: Mapped[str]
    tamano_ml: Mapped[int]
    fragrantica_url: Mapped[str | None]
    imagen: Mapped[str | None]
    