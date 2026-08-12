from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from config import DATABASE_PATH
from models import Perfume

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

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