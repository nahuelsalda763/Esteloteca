from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from database_orm import crear_clave_catalogo, engine
from models import Perfume



with Session(engine) as session:
    perfumes = session.scalars(select(Perfume)).all()

inconsistencias = []
por_clave = defaultdict(list)

for perfume in perfumes:
    calculada = crear_clave_catalogo(
        perfume.marca,
        perfume.nombre,
        perfume.concentracion,
    )
    por_clave[calculada].append(perfume.id)

    if perfume.catalog_key != calculada:
        inconsistencias.append(
            (perfume.id, perfume.catalog_key, calculada)
        )

colisiones = {
    clave: ids
    for clave, ids in por_clave.items()
    if len(ids) > 1
}

print("Perfumes globales: ", len(perfumes))
print("Claves inconsistentes: ", len(inconsistencias))
print("Colisiones de identidad: ", len(colisiones))

for perfume_id, actual, calculada in inconsistencias:
    print(f"INCONSISTENCIA ID={perfume_id}: {actual!r} -> {calculada!r}")

for clave, ids in colisiones.items():
    print(f"COLISION {clave!r}: ids={ids}")

if inconsistencias or colisiones:
    raise SystemExit(1)

print("Catálogo consistente")