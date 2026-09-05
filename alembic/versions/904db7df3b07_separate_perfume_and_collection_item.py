"""separate perfume and collection item

Revision ID: 904db7df3b07
Revises: c328858523f3
Create Date: 2026-09-01 19:43:25.817234

"""
from typing import Sequence, Union

import unicodedata

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '904db7df3b07'
down_revision: Union[str, Sequence[str], None] = 'c328858523f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _normalizar_valor_catalogo(valor: str) -> str:
    texto = unicodedata.normalize("NFKC", valor)
    texto = " ".join(texto.strip().split())
    return texto.casefold()

def _crear_clave_catalogo(
        marca: str,
        nombre: str,
        concentracion: str,
) -> str:
    return "|".join(
        (
            _normalizar_valor_catalogo(marca),
            _normalizar_valor_catalogo(nombre),
            _normalizar_valor_catalogo(concentracion),
        )
    )
def upgrade() -> None:
    connection = op.get_bind()

    filas = connection.execute(
        sa.text(
            """
            SELECT
                id,
                collection_id,
                marca,
                nombre,
                concentracion,
                tamano_ml,
                fragrantica_url,
                imagen
            FROM perfumes
            ORDER BY id
            """
        )
    ).mappings().all()

    items_migrar: list[dict] = []
    urls_completar: list[dict] = []

    for fila in filas:
        catalog_key = _crear_clave_catalogo(
            fila["marca"],
            fila["nombre"],
            fila["concentracion"],
        )

        perfume_global = connection.execute(
            sa.text(
                """
                SELECT id, fragrantica_url
                FROM catalog_perfumes
                WHERE catalog_key = :catalog_key
                """
            ),
            {
                "catalog_key": catalog_key,
            },
        ).mappings().one_or_none()

        if perfume_global is None:
            raise RuntimeError(
                "No existe perfume global para la fila "
                f"histórica id={fila['id']}."
            )

        items_migrar.append(
            {
                "id": fila["id"],
                "collection_id": fila["collection_id"],
                "perfume_id": perfume_global["id"],
                "tamano_ml": fila["tamano_ml"],
                "imagen": fila["imagen"],
            }
        )

        if (
            not perfume_global["fragrantica_url"]
            and fila["fragrantica_url"]
        ):
            urls_completar.append(
                {
                    "perfume_id": perfume_global["id"],
                    "fragrantica_url": fila["fragrantica_url"],
                }
            )

    op.create_table(
        "collection_items",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "collection_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "perfume_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "tamano_ml",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "imagen",
            sa.String(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.id"],
            name=(
                "fk_collection_items_"
                "collection_id_collections"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["perfume_id"],
            ["catalog_perfumes.id"],
            name=(
                "fk_collection_items_"
                "perfume_id_catalog_perfumes"
            ),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_collection_items_collection_id",
        "collection_items",
        ["collection_id"],
        unique=False,
    )

    op.create_index(
        "ix_collection_items_perfume_id",
        "collection_items",
        ["perfume_id"],
        unique=False,
    )

    if items_migrar:
        tabla_items = sa.table(
            "collection_items",
            sa.column(
                "id",
                sa.Integer(),
            ),
            sa.column(
                "collection_id",
                sa.Integer(),
            ),
            sa.column(
                "perfume_id",
                sa.Integer(),
            ),
            sa.column(
                "tamano_ml",
                sa.Integer(),
            ),
            sa.column(
                "imagen",
                sa.String(),
            ),
        )

        op.bulk_insert(
            tabla_items,
            items_migrar,
        )

    total_migrado = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM collection_items"
        )
    ).scalar_one()

    if total_migrado != len(filas):
        raise RuntimeError(
            "La cantidad migrada a collection_items "
            "no coincide con perfumes."
        )

    for datos_url in urls_completar:
        connection.execute(
            sa.text(
                """
                UPDATE catalog_perfumes
                SET fragrantica_url = :fragrantica_url
                WHERE id = :perfume_id
                  AND fragrantica_url IS NULL
                """
            ),
            datos_url,
        )

    if (
        connection.dialect.name == "postgresql"
        and items_migrar
    ):
        connection.execute(
            sa.text(
                """
                SELECT setval(
                    pg_get_serial_sequence(
                        'collection_items',
                        'id'
                    ),
                    (
                        SELECT MAX(id)
                        FROM collection_items
                    ),
                    true
                )
                """
            )
        )

    op.drop_table("perfumes")


def downgrade() -> None:
    op.create_table(
        "perfumes",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "marca",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "nombre",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "concentracion",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "tamano_ml",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "fragrantica_url",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "imagen",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "collection_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.id"],
            name=(
                "fk_perfumes_"
                "collection_id_collections"
            ),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    connection = op.get_bind()

    filas = connection.execute(
        sa.text(
            """
            SELECT
                ci.id,
                p.marca,
                p.nombre,
                p.concentracion,
                ci.tamano_ml,
                p.fragrantica_url,
                ci.imagen,
                ci.collection_id
            FROM collection_items AS ci
            JOIN catalog_perfumes AS p
              ON p.id = ci.perfume_id
            ORDER BY ci.id
            """
        )
    ).mappings().all()

    if filas:
        tabla_perfumes = sa.table(
            "perfumes",
            sa.column(
                "id",
                sa.Integer(),
            ),
            sa.column(
                "marca",
                sa.String(),
            ),
            sa.column(
                "nombre",
                sa.String(),
            ),
            sa.column(
                "concentracion",
                sa.String(),
            ),
            sa.column(
                "tamano_ml",
                sa.Integer(),
            ),
            sa.column(
                "fragrantica_url",
                sa.String(),
            ),
            sa.column(
                "imagen",
                sa.String(),
            ),
            sa.column(
                "collection_id",
                sa.Integer(),
            ),
        )

        op.bulk_insert(
            tabla_perfumes,
            [
                dict(fila)
                for fila in filas
            ],
        )

    if (
        connection.dialect.name == "postgresql"
        and filas
    ):
        connection.execute(
            sa.text(
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

    op.drop_index(
        "ix_collection_items_perfume_id",
        table_name="collection_items",
    )

    op.drop_index(
        "ix_collection_items_collection_id",
        table_name="collection_items",
    )

    op.drop_table(
        "collection_items"
    )
