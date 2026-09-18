"""add entity uniqueness constraint

Revision ID: 821576f75331
Revises: d1fdddab439c
Create Date: 2026-09-18 14:52:27.690141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '821576f75331'
down_revision: Union[str, Sequence[str], None] = 'd1fdddab439c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
