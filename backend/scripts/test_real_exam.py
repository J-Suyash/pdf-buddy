#!/usr/bin/env python3
"""
End-to-end test with real exam paper
Tests the complete pipeline: Upload → Extract → Parse → Index → Search
"""

import asyncio
import httpx
import time
import sys
import json

API_BASE = "http://localhost:8000"
PDF_PATH = "/home/sxtr/Documents/SEM 5/SDWAN/21CSE321J 07.01.2025 FN.pdf"


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


async def main():
    print("=" * 70)
    print("Real Exam Paper End-to-End Test")
    print("=" * 70)
    print(f"Testing with: {PDF_PATH}")
    print()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # 1. Upload the PDF
            print_info("Step 1: Uploading exam paper...")
            with open(PDF_PATH, 'rb') as f:
                files = {'files': (f'{PDF_PATH.split("/")[-1]}', f, 'application/pdf')}
                response = await client.post(f"{API_BASE}/api/v1/upload", files=files)
            
            if response.status_code != 200:
                print_error(f"Upload failed: {response.status_code}")
                print(response.text)
                return 1
            
            upload_data = response.json()
            job_id = upload_data['job_id']
            print_success(f"Uploaded successfully. Job ID: {job_id}")
            print()

            # 2. Monitor processing
            print_info("Step 2: Monitoring processing...")
            start_time = time.time()
            last_progress = -1
            last_status = None
            
            while True:
                response = await client.get(f"{API_BASE}/api/v1/jobs/{job_id}")
                if response.status_code != 200:
                    print_error(f"Job status check failed: {response.status_code}")
                    break
                
                job_data = response.json()
                status = job_data['status']
                progress = job_data.get('progress', 0)
                
                if progress != last_progress or status != last_status:
                    elapsed = time.time() - start_time
                    print(f"  [{elapsed:.1f}s] Status: {status} | Progress: {progress}% | Questions: {job_data.get('total_questions', 0)}")
                    last_progress = progress
                    last_status = status
                
                if status == 'completed':
                    elapsed = time.time() - start_time
                    print_success(f"Processing completed in {elapsed:.1f}s")
                    print()
                    
                    # Show results
                    print("📊 Processing Results:")
                    print(f"  Total Questions: {job_data['total_questions']}")
                    print(f"  Processed Pages: {job_data['processed_pages']}")
                    print()
                    break
                
                elif status == 'failed':
                    print_error(f"Processing failed: {job_data.get('error_message', 'Unknown error')}")
                    return 1
                
                await asyncio.sleep(2)
            
            # 3. Check extracted metadata in database
            print_info("Step 3: Verifying extracted metadata...")
            # We'll query the database directly for this
            print_info("  (Metadata verification requires direct DB access)")
            print()

            # 4. Test search
            print_info("Step 4: Testing semantic search...")
            test_queries = [
                "SD-WAN architecture",
                "VLAN network",
                "spanning tree protocol",
                "BGP routing",
                "cloud managed IT",
            ]
            
            search_results_count = 0
            for query in test_queries:
                response = await client.get(
                    f"{API_BASE}/api/v1/search",
                    params={'q': query, 'limit': 3}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data['results']
                    search_results_count += len(results)
                    
                    if results:
                        print_success(f"Query: '{query}' - Found {len(results)} results")
                        # Show top result
                        top = results[0]
                        print(f"    Top result (score: {top['score']:.3f})")
                        print(f"    Part: {top.get('part', 'N/A')} | Q#: {top.get('question_number', 'N/A')} | Type: {top.get('question_type', 'N/A')}")
                        print(f"    {top['content'][:100]}...")
                    else:
                        print_error(f"Query: '{query}' - No results")
                else:
                    print_error(f"Search failed: {response.status_code}")
            
            print()

            # Summary
            print("=" * 70)
            print("Test Summary")
            print("=" * 70)
            print_success(f"Uploaded and processed successfully")
            print_success(f"Extracted {job_data['total_questions']} questions")
            print_success(f"Search working - {search_results_count} total results from {len(test_queries)} queries")
            print()
            
            # Recommendations
            if job_data['total_questions'] < 27:
                print_info(f"Note: Expected ~27 questions, got {job_data['total_questions']}")
                print_info("  MCQ parsing may need further refinement")
            
            return 0

    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
