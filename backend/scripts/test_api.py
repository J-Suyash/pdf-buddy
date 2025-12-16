import asyncio
import httpx
import time
from pathlib import Path
from reportlab.pdfgen import canvas
from io import BytesIO

API_BASE = "http://localhost:8000"


async def create_test_pdf(filename: str = "test.pdf") -> Path:
    """Create a test PDF file."""
    pdf_path = Path(f"/tmp/{filename}")

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, 'Test Question Paper')
    c.drawString(50, 700, 'Q1. What is binary search?')
    c.drawString(50, 650, 'Q2. Explain quicksort algorithm')
    c.drawString(50, 600, 'Q3. What is dynamic programming?')
    c.save()
    pdf_buffer.seek(0)

    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())

    print(f"✓ Created test PDF: {pdf_path}")
    return pdf_path


async def test_health():
    """Test health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/health")
        print(f"✓ Health check: {response.status_code}")
        return response.json()


async def test_upload(pdf_path: Path):
    """Test file upload."""
    async with httpx.AsyncClient() as client:
        with open(pdf_path, 'rb') as f:
            files = {'files': ('test.pdf', f, 'application/pdf')}
            response = await client.post(f"{API_BASE}/api/v1/upload", files=files)

        print(f"✓ Upload: {response.status_code}")
        data = response.json()
        print(f"  Job ID: {data['job_id']}")
        print(f"  Status: {data['status']}")
        return data['job_id']


async def test_job_status(job_id: str):
    """Test job status endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/api/v1/jobs/{job_id}")
        print(f"✓ Job status: {response.status_code}")
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Progress: {data['progress']}%")
        return data


async def test_search(query: str):
    """Test search endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/api/v1/search",
            params={'q': query, 'limit': 5}
        )
        print(f"✓ Search: {response.status_code}")
        data = response.json()
        print(f"  Query: {data['query']}")
        print(f"  Results: {data['total']}")
        return data


async def main():
    print("=" * 50)
    print("Question Paper Search - API Test Script")
    print("=" * 50)

    try:
        # Test health
        await test_health()

        # Create test PDF
        pdf_path = await create_test_pdf()

        # Test upload
        job_id = await test_upload(pdf_path)

        # Test job status
        await test_job_status(job_id)

        # Wait for processing (in real scenario)
        print("\n⏳ Waiting for processing (3 seconds)...")
        await asyncio.sleep(3)

        # Test search
        await test_search("binary search")

        print("\n✓ All tests completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
