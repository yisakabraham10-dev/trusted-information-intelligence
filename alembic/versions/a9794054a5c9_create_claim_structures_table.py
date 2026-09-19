"""create claim structures table

Revision ID: a9794054a5c9
Revises: 8cf2f5c06b9c
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a9794054a5c9"
down_revision: Union[str, Sequence[str], None] = "8cf2f5c06b9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "claim_structures",
        sa.Column(
            "claim_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "structure_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "structure",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["claim_id"],
            ["claims.id"],
        ),
        sa.PrimaryKeyConstraint("claim_id"),
    )


def downgrade() -> None:
    op.drop_table("claim_structures")
