#!/usr/bin/env python3
"""
Check and retry stuck jobs in the database.
"""

import asyncio
import sys
sys.path.insert(0, '/home/sxtr/Projects/pdf-buddy/backend')

from app.core.database import async_session
from app.models import Job, JobStatus
from sqlalchemy import select


async def check_stuck_jobs():
    """Check for jobs stuck in queued or processing state."""
    async with async_session() as session:
        # Find jobs that are not completed or failed
        result = await session.execute(
            select(Job).where(
                Job.status.in_([JobStatus.QUEUED, JobStatus.PROCESSING])
            ).order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()
        
        if not jobs:
            print("✅ No stuck jobs found!")
            return
        
        print(f"Found {len(jobs)} stuck job(s):\n")
        
        for job in jobs:
            print(f"Job ID: {job.id}")
            print(f"  Status: {job.status}")
            print(f"  Progress: {job.progress}%")
            print(f"  Created: {job.created_at}")
            print(f"  Error: {job.error_message or 'None'}")
            print()
        
        print("\n" + "="*70)
        print("What to do:")
        print("="*70)
        print("\n1. Restart Celery worker:")
        print("   cd backend")
        print("   uv run celery -A app.tasks.celery_app worker --loglevel=info")
        print("\n2. The worker will automatically pick up and process the queued tasks")
        print("\n3. Monitor progress via the frontend or API:")
        print(f"   GET http://localhost:8000/api/v1/jobs/{jobs[0].id}")
        print()


if __name__ == "__main__":
    asyncio.run(check_stuck_jobs())
