"""add global perfume catalog

Revision ID: c328858523f3
Revises: c82cb1a10afa
Create Date: 2026-08-30 21:10:14.174661

"""

from typing import Sequence, Union

import unicodedata

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c328858523f3"
down_revision: Union[str, Sequence[str], None] = "c82cb1a10afa"
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
    """Upgrade schema."""

    op.create_table(
        "catalog_perfumes",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "marca",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "nombre",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "concentracion",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column(
            "catalog_key",
            sa.String(length=400),
            nullable=False,
        ),
        sa.Column(
            "fragrantica_url",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "catalog_key",
            name="uq_catalog_perfumes_catalog_key",
        ),
    )

    connection = op.get_bind()

    filas = connection.execute(
        sa.text(
            """
            SELECT
                marca,
                nombre,
                concentracion,
                fragrantica_url
            FROM perfumes
            ORDER BY id
            """
        )
    ).mappings()

    catalogo: dict[str, dict] = {}

    for fila in filas:
        clave = _crear_clave_catalogo(
            fila["marca"],
            fila["nombre"],
            fila["concentracion"],
        )

        existente = catalogo.get(clave)

        if existente is None:
            catalogo[clave] = {
                "marca": fila["marca"].strip(),
                "nombre": fila["nombre"].strip(),
                "concentracion": fila["concentracion"].strip(),
                "catalog_key": clave,
                "fragrantica_url": fila["fragrantica_url"],
            }

        elif (
            not existente["fragrantica_url"]
            and fila["fragrantica_url"]
        ):
            existente["fragrantica_url"] = (
                fila["fragrantica_url"]
            )

    tabla_catalogo = sa.table(
        "catalog_perfumes",
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
            "catalog_key",
            sa.String(),
        ),
        sa.column(
            "fragrantica_url",
            sa.String(),
        ),
    )

    if catalogo:
        op.bulk_insert(
            tabla_catalogo,
            list(catalogo.values()),
        )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("catalog_perfumes")