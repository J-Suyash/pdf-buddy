#!/usr/bin/env python3
"""Direct test of part splitting logic"""

import re

# Read the extracted text
with open('/tmp/exam_paper_extracted.txt', 'r') as f:
    text = f.read()

print("Testing part splitting...")
print("=" * 70)

# Test regex patterns
part_a_pattern = r'#?\s*PART\s*-?\s*A.*?(?=#?\s*PART\s*-?\s*B|$)'
part_b_pattern = r'#?\s*PART\s*-?\s*B.*?(?=#?\s*PART\s*-?\s*C|$)'
part_c_pattern = r'#?\s*PART\s*-?\s*C.*$'

print("\n🔍 Searching for Part A...")
part_a_match = re.search(part_a_pattern, text, re.DOTALL | re.IGNORECASE)
if part_a_match:
    part_a_text = part_a_match.group(0)
    print(f"  ✓ Found Part A: {len(part_a_text)} characters")
    print(f"  First 200 chars: {part_a_text[:200]}")
else:
    print("  ✗ Part A not found")

print("\n🔍 Searching for Part B...")
part_b_match = re.search(part_b_pattern, text, re.DOTALL | re.IGNORECASE)
if part_b_match:
    part_b_text = part_b_match.group(0)
    print(f"  ✓ Found Part B: {len(part_b_text)} characters")
    print(f"  First 200 chars: {part_b_text[:200]}")
    
    # Test question number detection in Part B
    print("\n  Testing question detection in Part B...")
    lines = part_b_text.split('\n')
    for i, line in enumerate(lines[:50]):  # First 50 lines
        line = line.strip()
        if re.match(r'^#?\s*(\d+)\s*$', line):
            print(f"    Line {i}: Found question number: {line}")
        if re.match(r'^([a-b])\.\s+', line):
            print(f"    Line {i}: Found sub-question: {line[:60]}...")
else:
    print("  ✗ Part B not found")

print("\n🔍 Searching for Part C...")
part_c_match = re.search(part_c_pattern, text, re.DOTALL | re.IGNORECASE)
if part_c_match:
    part_c_text = part_c_match.group(0)
    print(f"  ✓ Found Part C: {len(part_c_text)} characters")
    print(f"  First 200 chars: {part_c_text[:200]}")
else:
    print("  ✗ Part C not found")
