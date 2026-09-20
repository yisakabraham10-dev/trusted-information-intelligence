"""create document submissions table

Revision ID: 7b1c9e4a2d6f
Revises: 6e37c8ade5eb
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b1c9e4a2d6f"
down_revision: Union[str, Sequence[str], None] = "6e37c8ade5eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "document_submissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "original_filename",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "storage_path",
            sa.String(length=1000),
            nullable=False,
        ),
        sa.Column(
            "content_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "uploaded_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "reviewed_by",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "rejection_reason",
            sa.Text(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "content_hash",
            name="uq_document_submission_content_hash",
        ),
    )


def downgrade() -> None:
    op.drop_table("document_submissions")
