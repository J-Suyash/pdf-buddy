"""
Script to update existing documents with file_path if PDFs still exist in /tmp
Run this once after migration to fix existing documents.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.config import settings
from app.models import Document
import shutil

# Directories
TEMP_DIR = "/tmp/qp_uploads"
PERMANENT_DIR = settings.permanent_storage_dir

# Ensure permanent directory exists
os.makedirs(PERMANENT_DIR, exist_ok=True)


async def migrate_existing_pdfs():
    """Find existing PDFs in temp and move to permanent storage."""
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get all documents without file_path
        stmt = select(Document).where(Document.file_path.is_(None))
        result = await session.execute(stmt)
        documents = result.scalars().all()

        print(f"Found {len(documents)} documents without file_path")

        if not os.path.exists(TEMP_DIR):
            print(f"Temp directory {TEMP_DIR} does not exist")
            return

        # List all files in temp directory
        temp_files = os.listdir(TEMP_DIR) if os.path.exists(TEMP_DIR) else []
        print(f"Found {len(temp_files)} files in temp directory")

        migrated = 0
        not_found = 0

        for doc in documents:
            # Try to find the file in temp directory
            matching_files = [f for f in temp_files if doc.filename in f]

            if matching_files:
                temp_path = os.path.join(TEMP_DIR, matching_files[0])
                permanent_path = os.path.join(
                    PERMANENT_DIR, f"{doc.file_hash}_{doc.filename}"
                )

                # Copy to permanent storage
                shutil.copy2(temp_path, permanent_path)

                # Update database
                await session.execute(
                    update(Document)
                    .where(Document.id == doc.id)
                    .values(file_path=permanent_path)
                )

                print(f"✓ Migrated: {doc.filename}")
                migrated += 1
            else:
                print(f"✗ Not found in temp: {doc.filename}")
                not_found += 1

        await session.commit()

        print(f"\nMigration complete!")
        print(f"  - Migrated: {migrated}")
        print(f"  - Not found: {not_found}")
        print(f"  - Total: {len(documents)}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate_existing_pdfs())
