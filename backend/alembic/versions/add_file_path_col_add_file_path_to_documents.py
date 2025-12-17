"""add file_path to documents

Revision ID: add_file_path_col
Revises: 6a01f4cd3e89
Create Date: 2024-12-17 17:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_file_path_col"
down_revision = "6a01f4cd3e89"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add file_path column to documents table
    op.add_column(
        "documents", sa.Column("file_path", sa.String(length=512), nullable=True)
    )


def downgrade() -> None:
    # Remove file_path column from documents table
    op.drop_column("documents", "file_path")
