from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from config import DATABASE_PATH
from models import Perfume

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
)

#Prueba temporal
def probar_lectura():
    sentencia = select(Perfume)
    with Session(engine) as session:
        perfumes = session.scalars(sentencia).all()
        for perfume in perfumes:
            print(
                type(perfume),
                perfume.id,
                perfume.marca,
                perfume.nombre,
            )