#!/usr/bin/env python3
"""
Test script to analyze real exam paper with LlamaCloud
Extracts and analyzes question structure for schema refinement
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, '/home/sxtr/Projects/pdf-buddy/backend')

from app.services.llama_service import llama_service
import json


async def analyze_pdf(pdf_path: str):
    """Extract and analyze PDF content."""
    print(f"=" * 70)
    print(f"Analyzing: {pdf_path}")
    print(f"=" * 70)
    print()

    try:
        # Extract with LlamaCloud
        print("🔄 Extracting with LlamaCloud...")
        result = await llama_service.extract_from_pdf(pdf_path)
        
        text = result.get("text", "")
        pages = result.get("pages", [])
        metadata = result.get("metadata", {})
        
        print(f"✅ Extraction complete!")
        print(f"   - Pages: {len(pages)}")
        print(f"   - Total characters: {len(text)}")
        print()
        
        # Save full text to file for analysis
        output_file = "/tmp/exam_paper_extracted.txt"
        with open(output_file, 'w') as f:
            f.write(text)
        print(f"📄 Full text saved to: {output_file}")
        print()
        
        # Show first 2000 characters
        print("📖 First 2000 characters:")
        print("-" * 70)
        print(text[:2000])
        print("-" * 70)
        print()
        
        # Analyze structure
        print("🔍 Analyzing structure...")
        lines = text.split('\n')
        
        # Find lines that look like questions
        question_lines = []
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Check for question patterns
            patterns = ['Q.', 'Q ', '(a)', '(b)', '(c)', 'Question', 
                       'PART', 'Section', 'Bloom', 'CO', 'marks']
            
            if any(p in line for p in patterns):
                question_lines.append((i, line_stripped[:100]))
        
        print(f"Found {len(question_lines)} lines with question patterns")
        print("\nSample question lines:")
        for i, line in question_lines[:20]:
            print(f"  Line {i}: {line}")
        print()
        
        # Parse questions
        print("🎯 Parsing questions...")
        questions = await llama_service.extract_questions_from_text(text)
        print(f"   Parsed {len(questions)} questions")
        print()
        
        # Show first 3 questions
        print("📋 Sample parsed questions:")
        for i, q in enumerate(questions[:3], 1):
            print(f"\n  Question {i}:")
            print(f"    Content: {q['content'][:150]}...")
            print(f"    Type: {q.get('question_type', 'N/A')}")
            print(f"    Marks: {q.get('marks', 'N/A')}")
        
        # Metadata analysis
        print("\n📊 Metadata found:")
        print(f"   {json.dumps(metadata, indent=2)}")
        
        # Save structured data
        analysis = {
            "file": pdf_path,
            "pages": len(pages),
            "total_chars": len(text),
            "questions_found": len(questions),
            "sample_questions": questions[:5],
            "metadata": metadata,
            "question_lines_sample": question_lines[:10]
        }
        
        analysis_file = "/tmp/exam_paper_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Analysis saved to: {analysis_file}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    pdf_path = "/home/sxtr/Documents/SEM 5/SDWAN/21CSE321J 07.01.2025 FN.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return 1
    
    analysis = await analyze_pdf(pdf_path)
    
    if analysis:
        print("\n" + "=" * 70)
        print("✅ Analysis complete!")
        print("=" * 70)
        print("\nCheck the following files:")
        print("  - /tmp/exam_paper_extracted.txt - Full extracted text")
        print("  - /tmp/exam_paper_analysis.json - Structured analysis")
        return 0
    else:
        print("\n❌ Analysis failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
