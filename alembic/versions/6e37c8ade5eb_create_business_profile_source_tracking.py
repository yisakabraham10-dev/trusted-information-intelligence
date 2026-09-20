"""create business profile source tracking

Revision ID: 6e37c8ade5eb
Revises: a9794054a5c9
Create Date: 2026-09-20 09:19:35.986743

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6e37c8ade5eb"
down_revision: Union[str, Sequence[str], None] = "a9794054a5c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "business_profile_sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("business_profile_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["business_profile_id"],
            ["business_profiles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "business_profile_id",
            "source_id",
            name="uq_business_profile_source",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("business_profile_sources")
