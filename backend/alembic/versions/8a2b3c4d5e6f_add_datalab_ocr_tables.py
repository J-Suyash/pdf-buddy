"""Add datalab OCR tables

Revision ID: 8a2b3c4d5e6f
Revises: 6a01f4cd3e89
Create Date: 2025-01-20 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8a2b3c4d5e6f"
down_revision = "add_file_path_col"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create datalab_pdfs table
    op.create_table(
        "datalab_pdfs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("file_path", sa.String(512), nullable=True),
        sa.Column("thumbnail_path", sa.String(512), nullable=True),
        sa.Column("num_pages", sa.Integer, default=0),
        sa.Column("markdown", sa.Text, nullable=True),
        sa.Column("html", sa.Text, nullable=True),
        sa.Column("runtime_seconds", sa.Float, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_datalab_pdfs_job_id", "datalab_pdfs", ["job_id"])
    op.create_index("ix_datalab_pdfs_file_hash", "datalab_pdfs", ["file_hash"])

    # Create datalab_pages table
    op.create_table(
        "datalab_pages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "pdf_id", sa.String(36), sa.ForeignKey("datalab_pdfs.id"), nullable=False
        ),
        sa.Column("page_num", sa.Integer, nullable=False),
        sa.Column("thumbnail_path", sa.String(512), nullable=True),
        sa.Column("polygon", sa.JSON, nullable=True),
        sa.Column("markdown", sa.Text, nullable=True),
        sa.Column("html", sa.Text, nullable=True),
        sa.Column("num_blocks", sa.Integer, default=0),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_datalab_pages_pdf_id", "datalab_pages", ["pdf_id"])
    op.create_index("ix_datalab_pages_page_num", "datalab_pages", ["page_num"])

    # Create datalab_chunks table
    op.create_table(
        "datalab_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "pdf_id", sa.String(36), sa.ForeignKey("datalab_pdfs.id"), nullable=False
        ),
        sa.Column(
            "page_id", sa.String(36), sa.ForeignKey("datalab_pages.id"), nullable=False
        ),
        sa.Column("block_id", sa.String(255), nullable=True),
        sa.Column("block_type", sa.String(50), nullable=True),
        sa.Column("text", sa.Text, nullable=True),
        sa.Column("html", sa.Text, nullable=True),
        sa.Column("images", sa.JSON, nullable=True),
        sa.Column("bbox", sa.JSON, nullable=True),
        sa.Column("polygon", sa.JSON, nullable=True),
        sa.Column("thumbnail_path", sa.String(512), nullable=True),
        sa.Column("section_hierarchy", sa.JSON, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_datalab_chunks_pdf_id", "datalab_chunks", ["pdf_id"])
    op.create_index("ix_datalab_chunks_page_id", "datalab_chunks", ["page_id"])
    op.create_index("ix_datalab_chunks_block_type", "datalab_chunks", ["block_type"])

    # Create datalab_vectors table
    op.create_table(
        "datalab_vectors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "chunk_id",
            sa.String(36),
            sa.ForeignKey("datalab_chunks.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "pdf_id", sa.String(36), sa.ForeignKey("datalab_pdfs.id"), nullable=False
        ),
        sa.Column(
            "page_id", sa.String(36), sa.ForeignKey("datalab_pages.id"), nullable=False
        ),
        sa.Column("qdrant_id", sa.String(36), nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_datalab_vectors_chunk_id", "datalab_vectors", ["chunk_id"])
    op.create_index("ix_datalab_vectors_pdf_id", "datalab_vectors", ["pdf_id"])
    op.create_index("ix_datalab_vectors_page_id", "datalab_vectors", ["page_id"])
    op.create_index("ix_datalab_vectors_qdrant_id", "datalab_vectors", ["qdrant_id"])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("datalab_vectors")
    op.drop_table("datalab_chunks")
    op.drop_table("datalab_pages")
    op.drop_table("datalab_pdfs")
