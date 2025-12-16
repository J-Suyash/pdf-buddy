#!/usr/bin/env python3
"""
Single test run of LlamaExtract with the SRM PYQ agent.
CAUTION: This uses API credits. Run sparingly.
"""

import asyncio
import sys
import json

sys.path.insert(0, '/home/sxtr/Projects/pdf-buddy/backend')

from app.services.llama_service import llama_service


async def main():
    pdf_path = "/home/sxtr/Documents/SEM 5/SDWAN/21CSE321J 07.01.2025 FN.pdf"
    
    print("=" * 70)
    print("LlamaExtract Test with Agent: SRM PYQ")
    print("=" * 70)
    print(f"PDF: {pdf_path}")
    print()
    print("⚠️  This will use API credits!")
    print()

    try:
        # Extract with LlamaExtract
        print("🔄 Extracting with LlamaExtract agent...")
        result = await llama_service.extract_from_pdf(pdf_path)
        
        structured_data = result.get("structured_data", {})
        markdown_text = result.get("text", "")
        
        # Save structured JSON
        json_output = "/tmp/llama_extract_result.json"
        with open(json_output, 'w') as f:
            json.dump(structured_data, f, indent=2)
        print(f"✅ Structured JSON saved to: {json_output}")
        
        # Save markdown
        md_output = "/tmp/llama_extract_result.md"
        with open(md_output, 'w') as f:
            f.write(markdown_text)
        print(f"✅ Markdown saved to: {md_output}")
        
        # Analyze results
        print()
        print("📊 Extraction Results:")
        print("-" * 70)
        
        # Header
        header = structured_data.get("header", {})
        if header:
            print(f"Course: {header.get('course_code')} - {header.get('course_name')}")
            print(f"Semester: {header.get('semester')}")
            print(f"Exam Date: {header.get('exam_date_month')}")
            print(f"Max Marks: {header.get('max_marks')}")
            print(f"Duration: {header.get('duration')}")
        
        # Part A
        part_a = structured_data.get("part_a", {})
        part_a_count = len(part_a.get("questions", []))
        print(f"\nPart A (MCQs): {part_a_count} questions")
        if part_a_count > 0:
            sample = part_a["questions"][0]
            print(f"  Sample Q{sample.get('question_number')}: {sample.get('question_text', '')[:60]}...")
            print(f"  Options: {list(sample.get('options', {}).keys())}")
            print(f"  Unit: {sample.get('unit_mapping')}")
        
        # Part B
        part_b = structured_data.get("part_b", {})
        part_b_questions = part_b.get("questions", [])
        part_b_count = sum(len(q.get("sub_questions", [])) for q in part_b_questions)
        print(f"\nPart B (Descriptive): {part_b_count} sub-questions from {len(part_b_questions)} main questions")
        if part_b_questions:
            sample = part_b_questions[0]
            print(f"  Sample Q{sample.get('question_number')}: {len(sample.get('sub_questions', []))} sub-questions")
            print(f"  Unit: {sample.get('unit_mapping')}")
            if sample.get('sub_questions'):
                sub = sample['sub_questions'][0]
                print(f"    {sub.get('label')}: {sub.get('text', '')[:60]}...")
        
        # Part C
        part_c = structured_data.get("part_c", {})
        part_c_count = len(part_c.get("questions", []))
        print(f"\nPart C (Scenario): {part_c_count} questions")
        
        # Total
        total = part_a_count + part_b_count + part_c_count
        print(f"\n📈 Total Questions Extracted: {total}")
        print(f"   Expected: ~32 (20 MCQs + 10 descriptive + 2 scenario)")
        
        # Test question extraction
        print()
        print("🎯 Testing question extraction...")
        questions_by_parts = await llama_service.extract_questions_by_parts(
            markdown_text,
            structured_data=structured_data
        )
        
        for part, questions in questions_by_parts.items():
            print(f"  Part {part}: {len(questions)} questions")
            if questions:
                sample = questions[0]
                print(f"    Sample: Q{sample['question_number']} (Unit {sample.get('unit', '?')})")
        
        print()
        print("=" * 70)
        print("✅ Test Complete!")
        print("=" * 70)
        print(f"\nReview the output files:")
        print(f"  - {json_output}")
        print(f"  - {md_output}")
        
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
