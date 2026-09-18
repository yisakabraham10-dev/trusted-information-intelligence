"""add entity uniqueness constraint

Revision ID: 821576f75331
Revises: 3b436163edfa
Create Date: 2026-09-18
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "821576f75331"
down_revision: Union[str, Sequence[str], None] = "3b436163edfa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_entities_type_name",
        "entities",
        ["entity_type", "name"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_entities_type_name",
        "entities",
        type_="unique",
    )