from argparse import ArgumentParser
from pathlib import Path
import sys

from sqlalchemy import (
    create_engine,
    func,
    select,
    text,
)
from sqlalchemy.orm import Session


# Permite importar módulos ubicados en la raíz del proyecto.
ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from config import DATABASE_URL
from models import Perfume


def obtener_argumentos():
    parser = ArgumentParser(
        description=(
            "Migra los perfumes de una base SQLite "
            "hacia PostgreSQL."
        )
    )

    parser.add_argument(
        "--sqlite-path",
        required=True,
        help="Ruta del archivo SQLite de origen.",
    )

    return parser.parse_args()


def main():
    argumentos = obtener_argumentos()

    sqlite_path = Path(
        argumentos.sqlite_path
    ).expanduser().resolve()

    if not sqlite_path.is_file():
        raise SystemExit(
            f"No existe la base SQLite: {sqlite_path}"
        )

    sqlite_engine = create_engine(
        f"sqlite:///{sqlite_path}"
    )

    postgres_engine = create_engine(
        DATABASE_URL
    )

    if (
        postgres_engine.url.get_backend_name()
        != "postgresql"
    ):
        raise SystemExit(
            "DATABASE_URL no apunta a PostgreSQL."
        )

    with Session(sqlite_engine) as session:
        perfumes_origen = session.scalars(
            select(Perfume).order_by(Perfume.id)
        ).all()

        datos_perfumes = [
            {
                "id": perfume.id,
                "marca": perfume.marca,
                "nombre": perfume.nombre,
                "concentracion": perfume.concentracion,
                "tamano_ml": perfume.tamano_ml,
                "fragrantica_url": perfume.fragrantica_url,
                "imagen": perfume.imagen,
            }
            for perfume in perfumes_origen
        ]

    print(
        "Perfumes encontrados en SQLite:",
        len(datos_perfumes),
    )

    with Session(postgres_engine) as session:
        cantidad_destino = session.scalar(
            select(func.count()).select_from(
                Perfume
            )
        )

        if cantidad_destino:
            raise SystemExit(
                "PostgreSQL ya contiene perfumes. "
                "Migración cancelada."
            )

        nuevos_perfumes = [
            Perfume(**datos)
            for datos in datos_perfumes
        ]

        session.add_all(nuevos_perfumes)
        session.flush()

        # Al preservar los IDs históricos, también
        # sincronizamos la secuencia de PostgreSQL.
        if datos_perfumes:
            session.execute(
                text(
                    """
                    SELECT setval(
                        pg_get_serial_sequence(
                            'perfumes',
                            'id'
                        ),
                        (
                            SELECT MAX(id)
                            FROM perfumes
                        ),
                        true
                    )
                    """
                )
            )

        session.commit()

    with Session(postgres_engine) as session:
        cantidad_final = session.scalar(
            select(func.count()).select_from(
                Perfume
            )
        )

    if cantidad_final != len(datos_perfumes):
        raise SystemExit(
            "La cantidad final no coincide "
            "con la base SQLite."
        )

    print(
        "Migración completada correctamente."
    )
    print(
        "Perfumes en PostgreSQL:",
        cantidad_final,
    )


if __name__ == "__main__":
    main()