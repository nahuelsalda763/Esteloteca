"""add collections ownership

Revision ID: c82cb1a10afa
Revises: cb15e7d3e384
Create Date: 2026-08-20 08:52:52.564677

"""
from typing import Sequence, Union
import os
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c82cb1a10afa'
down_revision: Union[str, Sequence[str], None] = 'cb15e7d3e384'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    connection = op.get_bind()

    total_perfumes = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM perfumes
            """
        )
    ).scalar_one()

    legacy_owner_username = (
        os.getenv(
            "LEGACY_OWNER_USERNAME",
            "",
        )
        .strip()
        .lower()
    )

    legacy_owner_id = None

    if total_perfumes > 0:

        if not legacy_owner_username:
            raise RuntimeError(
                "Existen perfumes históricos pero "
                "LEGACY_OWNER_USERNAME no está configurado."
            )

        legacy_owner_id = connection.execute(
            sa.text(
                """
                SELECT id
                FROM users
                WHERE username = :username
                """
            ),
            {
                "username": legacy_owner_username,
            },
        ).scalar_one_or_none()

        if legacy_owner_id is None:
            raise RuntimeError(
                "LEGACY_OWNER_USERNAME no corresponde "
                "a ningún usuario existente."
            )

    op.create_table(
        "collections",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "is_public",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table(
        "perfumes",
        schema=None,
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "collection_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_foreign_key(
            "fk_perfumes_collection_id_collections",
            "collections",
            ["collection_id"],
            ["id"],
        )

    user_ids = connection.execute(
        sa.text(
            """
            SELECT id
            FROM users
            ORDER BY id
            """
        )
    ).scalars().all()

    for user_id in user_ids:

        connection.execute(
            sa.text(
                """
                INSERT INTO collections (
                    owner_id,
                    name,
                    description,
                    is_public
                )
                VALUES (
                    :owner_id,
                    :name,
                    :description,
                    :is_public
                )
                """
            ),
            {
                "owner_id": user_id,
                "name": "Mi colección",
                "description": None,
                "is_public": False,
            },
        )

    if total_perfumes > 0:

        legacy_collection_id = connection.execute(
            sa.text(
                """
                SELECT id
                FROM collections
                WHERE owner_id = :owner_id
                ORDER BY id
                LIMIT 1
                """
            ),
            {
                "owner_id": legacy_owner_id,
            },
        ).scalar_one()

        connection.execute(
            sa.text(
                """
                UPDATE perfumes
                SET collection_id = :collection_id
                WHERE collection_id IS NULL
                """
            ),
            {
                "collection_id": legacy_collection_id,
            },
        )

    perfumes_sin_coleccion = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM perfumes
            WHERE collection_id IS NULL
            """
        )
    ).scalar_one()

    if perfumes_sin_coleccion != 0:
        raise RuntimeError(
            "La migración dejó perfumes "
            "sin colección."
        )

    with op.batch_alter_table(
        "perfumes",
        schema=None,
    ) as batch_op:

        batch_op.alter_column(
            "collection_id",
            existing_type=sa.Integer(),
            nullable=False,
        )

def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table(
        "perfumes",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_perfumes_collection_id_collections",
            type_="foreignkey",
        )

        batch_op.drop_column(
            "collection_id"
        )

    op.drop_table(
        "collections"
    )
