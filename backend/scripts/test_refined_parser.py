#!/usr/bin/env python3
"""Quick diagnostic to test the refined parser"""

import asyncio
import sys
sys.path.insert(0, '/home/sxtr/Projects/pdf-buddy/backend')

from app.services.llama_service import llama_service

async def main():
    # Read the extracted text
    with open('/tmp/exam_paper_extracted.txt', 'r') as f:
        text = f.read()
    
    print("Testing refined parser...")
    print("=" * 70)
    
    # Test part extraction
    parts = await llama_service.extract_questions_by_parts(text)
    
    print(f"\n📊 Results:")
    print(f"  Part A (MCQs): {len(parts['A'])} questions")
    print(f"  Part B (Descriptive): {len(parts['B'])} questions")
    print(f"  Part C (Optional): {len(parts['C'])} questions")
    print(f"  Total: {sum(len(q) for q in parts.values())} questions")
    
    # Show samples from each part
    if parts['A']:
        print(f"\n📝 Part A Sample (first 3):")
        for i, q in enumerate(parts['A'][:3], 1):
            print(f"  Q{q['question_number']} (Unit {q.get('unit', '?')}): {q['content'][:80]}...")
            if q.get('options'):
                print(f"    Options: {list(q['options'].keys())}")
    
    if parts['B']:
        print(f"\n📝 Part B Sample (first 3):")
        for i, q in enumerate(parts['B'][:3], 1):
            print(f"  Q{q['question_number']} (Unit {q.get('unit', '?')}): {q['content'][:80]}...")
    
    if parts['C']:
        print(f"\n📝 Part C Sample:")
        for i, q in enumerate(parts['C'][:2], 1):
            print(f"  Q{q['question_number']} (Unit {q.get('unit', '?')}): {q['content'][:80]}...")

if __name__ == "__main__":
    asyncio.run(main())
