#!/usr/bin/env python3
"""
Production Readiness Test Script for Question Paper Search Backend

Tests:
1. Infrastructure health checks
2. API endpoint functionality
3. PDF upload and processing
4. Semantic search
5. Error handling
6. Performance metrics
"""

import asyncio
import httpx
import time
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import sys

API_BASE = "http://localhost:8000"
TIMEOUT = 30.0


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")


def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")


async def create_realistic_test_pdf(filename: str = "test_questions.pdf") -> Path:
    """Create a realistic test PDF with sample questions."""
    pdf_path = Path(f"/tmp/{filename}")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Computer Science - Data Structures")
    c.drawString(50, height - 70, "Mid-Term Examination 2023")

    # Questions
    c.setFont("Helvetica", 12)
    y_position = height - 120

    questions = [
        ("Q1.", "Explain the concept of binary search tree. What are its advantages over linear search? [5 marks]"),
        ("Q2.", "Write an algorithm to implement quicksort. Analyze its time complexity. [10 marks]"),
        ("Q3.", "What is dynamic programming? Explain with an example of the Fibonacci sequence. [8 marks]"),
        ("Q4.", "Describe the difference between stack and queue data structures. [5 marks]"),
        ("Q5.", "Implement a function to detect a cycle in a linked list. [7 marks]"),
    ]

    for q_num, q_text in questions:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, q_num)
        c.setFont("Helvetica", 12)
        
        # Word wrap for long questions
        words = q_text.split()
        line = ""
        x_offset = 90
        
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 12) < (width - 100):
                line = test_line
            else:
                c.drawString(x_offset, y_position, line)
                y_position -= 20
                line = word + " "
        
        if line:
            c.drawString(x_offset, y_position, line)
        
        y_position -= 40

    c.save()
    buffer.seek(0)

    with open(pdf_path, 'wb') as f:
        f.write(buffer.read())

    print_success(f"Created realistic test PDF: {pdf_path}")
    return pdf_path


async def test_health_check():
    """Test health endpoint."""
    print_info("Testing health check endpoint...")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check passed: {data}")
                return True
            else:
                print_error(f"Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False


async def test_upload(pdf_path: Path):
    """Test file upload endpoint."""
    print_info(f"Testing upload endpoint with {pdf_path.name}...")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(pdf_path, 'rb') as f:
                files = {'files': (pdf_path.name, f, 'application/pdf')}
                start_time = time.time()
                response = await client.post(f"{API_BASE}/api/v1/upload", files=files)
                upload_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                print_success(f"Upload successful (took {upload_time:.2f}s)")
                print_info(f"  Job ID: {data['job_id']}")
                print_info(f"  Status: {data['status']}")
                print_info(f"  Files: {data['files']}")
                return data['job_id']
            else:
                print_error(f"Upload failed: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print_error(f"Upload error: {e}")
        return None


async def test_job_status(job_id: str, max_wait: int = 120):
    """Test job status endpoint and wait for completion."""
    print_info(f"Monitoring job status for {job_id}...")
    
    start_time = time.time()
    last_progress = -1
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            while True:
                response = await client.get(f"{API_BASE}/api/v1/jobs/{job_id}")
                
                if response.status_code != 200:
                    print_error(f"Job status check failed: {response.status_code}")
                    return None
                
                data = response.json()
                status = data['status']
                progress = data['progress']
                
                # Show progress updates
                if progress != last_progress:
                    print_info(f"  Status: {status} | Progress: {progress}% | Questions: {data.get('total_questions', 0)}")
                    last_progress = progress
                
                if status == 'completed':
                    elapsed = time.time() - start_time
                    print_success(f"Job completed in {elapsed:.2f}s")
                    print_info(f"  Total questions: {data['total_questions']}")
                    print_info(f"  Processed pages: {data['processed_pages']}")
                    return data
                
                elif status == 'failed':
                    print_error(f"Job failed: {data.get('error_message', 'Unknown error')}")
                    return None
                
                # Check timeout
                if time.time() - start_time > max_wait:
                    print_warning(f"Job still processing after {max_wait}s, stopping monitor")
                    return data
                
                await asyncio.sleep(2)
                
    except Exception as e:
        print_error(f"Job status error: {e}")
        return None


async def test_search(query: str, expected_min_results: int = 1):
    """Test search endpoint."""
    print_info(f"Testing search with query: '{query}'...")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            start_time = time.time()
            response = await client.get(
                f"{API_BASE}/api/v1/search",
                params={'q': query, 'limit': 10}
            )
            search_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                result_count = data['total']
                
                if result_count >= expected_min_results:
                    print_success(f"Search successful (took {search_time*1000:.0f}ms)")
                    print_info(f"  Query: {data['query']}")
                    print_info(f"  Results: {result_count}")
                    
                    # Show top results
                    for i, result in enumerate(data['results'][:3], 1):
                        print_info(f"  [{i}] Score: {result['score']:.3f} - {result['content'][:80]}...")
                    
                    return True
                else:
                    print_warning(f"Search returned {result_count} results (expected >= {expected_min_results})")
                    return False
            else:
                print_error(f"Search failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print_error(f"Search error: {e}")
        return False


async def test_error_handling():
    """Test error handling for invalid requests."""
    print_info("Testing error handling...")
    
    tests_passed = 0
    total_tests = 3
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Test 1: Upload without files
        try:
            response = await client.post(f"{API_BASE}/api/v1/upload", files={})
            if response.status_code in [400, 422]:
                print_success("  Invalid upload rejected correctly")
                tests_passed += 1
            else:
                print_error(f"  Invalid upload not rejected: {response.status_code}")
        except Exception as e:
            print_error(f"  Error test failed: {e}")
        
        # Test 2: Job status with invalid ID
        try:
            response = await client.get(f"{API_BASE}/api/v1/jobs/invalid-job-id")
            if response.status_code == 404:
                print_success("  Invalid job ID rejected correctly")
                tests_passed += 1
            else:
                print_error(f"  Invalid job ID not rejected: {response.status_code}")
        except Exception as e:
            print_error(f"  Error test failed: {e}")
        
        # Test 3: Search with too short query
        try:
            response = await client.get(f"{API_BASE}/api/v1/search", params={'q': 'ab'})
            if response.status_code == 422:
                print_success("  Short query rejected correctly")
                tests_passed += 1
            else:
                print_error(f"  Short query not rejected: {response.status_code}")
        except Exception as e:
            print_error(f"  Error test failed: {e}")
    
    return tests_passed == total_tests


async def test_api_docs():
    """Test API documentation endpoints."""
    print_info("Testing API documentation...")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test OpenAPI schema
            response = await client.get(f"{API_BASE}/openapi.json")
            if response.status_code == 200:
                print_success("OpenAPI schema accessible")
                return True
            else:
                print_error(f"OpenAPI schema not accessible: {response.status_code}")
                return False
    except Exception as e:
        print_error(f"API docs error: {e}")
        return False


async def main():
    print("=" * 70)
    print("Question Paper Search - Production Readiness Test")
    print("=" * 70)
    print()

    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }

    # Test 1: Health Check
    print("\n[1/7] Health Check")
    print("-" * 70)
    if await test_health_check():
        results['passed'] += 1
    else:
        results['failed'] += 1
        print_error("Backend is not healthy. Stopping tests.")
        sys.exit(1)

    # Test 2: API Documentation
    print("\n[2/7] API Documentation")
    print("-" * 70)
    if await test_api_docs():
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Test 3: Create Test PDF
    print("\n[3/7] PDF Creation")
    print("-" * 70)
    pdf_path = await create_realistic_test_pdf()

    # Test 4: Upload
    print("\n[4/7] File Upload")
    print("-" * 70)
    job_id = await test_upload(pdf_path)
    if job_id:
        results['passed'] += 1
    else:
        results['failed'] += 1
        print_error("Upload failed. Skipping remaining tests.")
        sys.exit(1)

    # Test 5: Job Processing
    print("\n[5/7] Job Processing")
    print("-" * 70)
    job_result = await test_job_status(job_id, max_wait=120)
    if job_result and job_result.get('status') == 'completed':
        results['passed'] += 1
    else:
        results['failed'] += 1
        print_warning("Job processing incomplete or failed. Search tests may fail.")

    # Test 6: Search
    print("\n[6/7] Semantic Search")
    print("-" * 70)
    search_queries = [
        ("binary search tree", 1),
        ("quicksort algorithm", 1),
        ("dynamic programming", 1),
    ]
    
    search_passed = 0
    for query, min_results in search_queries:
        if await test_search(query, min_results):
            search_passed += 1
        await asyncio.sleep(1)
    
    if search_passed == len(search_queries):
        results['passed'] += 1
    elif search_passed > 0:
        results['warnings'] += 1
        print_warning(f"Only {search_passed}/{len(search_queries)} search queries passed")
    else:
        results['failed'] += 1

    # Test 7: Error Handling
    print("\n[7/7] Error Handling")
    print("-" * 70)
    if await test_error_handling():
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"{Colors.GREEN}Passed:{Colors.END}   {results['passed']}")
    print(f"{Colors.RED}Failed:{Colors.END}   {results['failed']}")
    print(f"{Colors.YELLOW}Warnings:{Colors.END} {results['warnings']}")
    print()

    if results['failed'] == 0:
        print_success("All tests passed! Backend is production ready.")
        return 0
    else:
        print_error(f"{results['failed']} test(s) failed. Backend needs attention.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
