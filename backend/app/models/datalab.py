"""
Datalab OCR models for storing PDF, pages, chunks, and vectors.

This is a separate schema from the existing Document/Question tables,
designed to store the complex output from Datalab's OCR API.
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class DatalabPDF(Base):
    """
    TABLE 0 -- PDF
    Purpose: Storing PDF metadata from Datalab OCR processing.
    """

    __tablename__ = "datalab_pdfs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    name = Column(String(255), nullable=False)  # PDF_NAME (original filename)
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash
    file_path = Column(String(512), nullable=True)  # Path to stored PDF
    thumbnail_path = Column(
        String(512), nullable=True
    )  # PDF_THUMB (path to thumbnail file)
    num_pages = Column(Integer, default=0)  # NUM_PAGES
    markdown = Column(Text, nullable=True)  # PDF_MD (full document markdown)
    html = Column(Text, nullable=True)  # PDF_HTML (full document html)
    runtime_seconds = Column(Float, nullable=True)  # Processing time from datalab
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job = relationship("Job", backref="datalab_pdfs")
    pages = relationship(
        "DatalabPage", back_populates="pdf", cascade="all, delete-orphan"
    )
    chunks = relationship(
        "DatalabChunk", back_populates="pdf", cascade="all, delete-orphan"
    )
    vectors = relationship(
        "DatalabVector", back_populates="pdf", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DatalabPDF {self.id}: {self.name}>"


class DatalabPage(Base):
    """
    TABLE 1 -- PDF_PAGE
    Purpose: Storing PDFs' pages data from Datalab OCR.
    """

    __tablename__ = "datalab_pages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_id = Column(String(36), ForeignKey("datalab_pdfs.id"), nullable=False)
    page_num = Column(Integer, nullable=False)  # PAGE_NUM (0-indexed)
    thumbnail_path = Column(
        String(512), nullable=True
    )  # PAGE_THUMB (path to page thumbnail)
    polygon = Column(JSON, nullable=True)  # PAGE_POLYGON
    markdown = Column(Text, nullable=True)  # PAGE_MD (page-level markdown)
    html = Column(Text, nullable=True)  # PAGE_HTML (page-level html)
    num_blocks = Column(Integer, default=0)  # NUM_BLOCKS
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    pdf = relationship("DatalabPDF", back_populates="pages")
    chunks = relationship(
        "DatalabChunk", back_populates="page", cascade="all, delete-orphan"
    )
    vectors = relationship(
        "DatalabVector", back_populates="page", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DatalabPage {self.id}: PDF {self.pdf_id} Page {self.page_num}>"


class DatalabChunk(Base):
    """
    TABLE 2 -- CHUNK
    Purpose: Storing Pages' chunks/blocks data from Datalab OCR.
    Each chunk represents a semantic block (text, header, image, table, etc.)
    """

    __tablename__ = "datalab_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_id = Column(String(36), ForeignKey("datalab_pdfs.id"), nullable=False)
    page_id = Column(String(36), ForeignKey("datalab_pages.id"), nullable=False)

    # Original datalab block info
    block_id = Column(
        String(255), nullable=True
    )  # Original block ID from datalab (e.g., "/page/0/Text/1")
    block_type = Column(
        String(50), nullable=True
    )  # SectionHeader, Text, Picture, ListGroup, Table, etc.

    # Content
    text = Column(Text, nullable=True)  # CHUNK_TEXT (extracted text from html)
    html = Column(Text, nullable=True)  # Original HTML from datalab

    # Images (stored as file paths, not inline)
    images = Column(
        JSON, nullable=True
    )  # CHUNK_IMAGES: {"image_name": "path/to/image.jpg", ...}

    # Position data
    bbox = Column(JSON, nullable=True)  # CHUNK_BBOX [x1, y1, x2, y2]
    polygon = Column(
        JSON, nullable=True
    )  # CHUNK_POLYGON [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    thumbnail_path = Column(
        String(512), nullable=True
    )  # CHUNK_THUMB (optional cropped chunk image)

    # Structure
    section_hierarchy = Column(JSON, nullable=True)  # For tracking section structure

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    pdf = relationship("DatalabPDF", back_populates="chunks")
    page = relationship("DatalabPage", back_populates="chunks")
    vector = relationship(
        "DatalabVector",
        back_populates="chunk",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<DatalabChunk {self.id}: {self.block_type} on Page {self.page_id}>"


class DatalabVector(Base):
    """
    TABLE 3 -- VECTOR
    Purpose: Separate from page level data for easier vector management.
    Links chunks to their embeddings in Qdrant.
    """

    __tablename__ = "datalab_vectors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk_id = Column(
        String(36), ForeignKey("datalab_chunks.id"), nullable=False, unique=True
    )
    pdf_id = Column(String(36), ForeignKey("datalab_pdfs.id"), nullable=False)
    page_id = Column(String(36), ForeignKey("datalab_pages.id"), nullable=False)
    qdrant_id = Column(
        String(36), nullable=True
    )  # Reference to Qdrant point ID (UUID string)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    chunk = relationship("DatalabChunk", back_populates="vector")
    pdf = relationship("DatalabPDF", back_populates="vectors")
    page = relationship("DatalabPage", back_populates="vectors")

    def __repr__(self):
        return f"<DatalabVector {self.id}: Chunk {self.chunk_id}>"
