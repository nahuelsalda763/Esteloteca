from sqlalchemy import (create_engine, or_, select,)
from sqlalchemy.orm import Session

from config import DATABASE_URL
from models import Perfume



engine = create_engine(
    DATABASE_URL,
)


    
def obtener_perfumes():
    sentencia = (
        select(Perfume)
        .order_by(Perfume.id.desc())
    )

    with Session(engine) as session:
        perfumes = session.scalars(sentencia).all()
        return perfumes

def obtener_perfume_por_id(perfume_id: int,):
    sentencia =(
        select(Perfume)
        .where(Perfume.id == perfume_id)
    )
    with Session(engine) as session:
        perfume = session.scalar(sentencia)
        return perfume

def buscar_perfumes(termino: str,):
    termino = termino.strip()

    if not termino:
        return obtener_perfumes()

    patron = f"%{termino}%"
    sentencia = (
        select(Perfume)
        .where(
            or_(
                Perfume.marca.ilike(patron),
                Perfume.nombre.ilike(patron),
            )
        )
        .order_by(
            Perfume.marca,
            Perfume.nombre,
        )
    )

    with Session(engine) as session:
        perfumes = session.scalars(sentencia).all()
        return perfumes

def agregar_perfume (
        marca: str,
        nombre: str,
        concentracion: str,
        tamano_ml: int,
        fragrantica_url: str | None,
        imagen: str | None,
):
    nuevo_perfume = Perfume(
        marca = marca,
        nombre = nombre,
        concentracion = concentracion,
        tamano_ml = tamano_ml,
        fragrantica_url = fragrantica_url,
        imagen = imagen,
    )

    with Session(engine) as session:
        session.add( nuevo_perfume )

        session.commit()


def actualizar_perfume(
        perfume_id: int,
        marca: str,
        nombre: str,
        concentracion: str,
        tamano_ml: int,
        fragrantica_url: str | None,
        imagen: str | None,
) -> bool:

    with Session(engine) as session:
        perfume = session.get (Perfume, perfume_id)

        if perfume is None:
            return False

        perfume.marca = marca
        perfume.nombre = nombre
        perfume.concentracion = concentracion
        perfume.tamano_ml = tamano_ml
        perfume.fragrantica_url = fragrantica_url
        perfume.imagen = imagen

        session.commit()

        return True

def eliminar_perfume(
        perfume_id: int,
) -> bool:
    with Session(engine) as session:
        perfume = session.get(
            Perfume,
            perfume_id,
        )
        if perfume is None:
            return False

        session.delete( perfume )
        session.commit()

        return True