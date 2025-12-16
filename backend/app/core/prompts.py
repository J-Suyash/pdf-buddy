"""
System prompts and parsing instructions for LlamaCloud extraction.
"""

EXAM_PAPER_PARSING_INSTRUCTION = """
This document is a university end-semester examination paper. It follows a strict structure that must be preserved:

1. **Header Information**:
   - Course Code (e.g., 21CSE321J)
   - Course Name
   - Semester (e.g., Fifth Semester)
   - Exam Date/Month
   - Max Marks and Duration

2. **Part A (MCQs)**:
   - Contains exactly 20 Multiple Choice Questions numbered 1 to 20.
   - Each question has 4 options labeled A, B, C, D.
   - **Unit Mapping**:
     - Q1-Q4: Unit 1
     - Q5-Q8: Unit 2
     - Q9-Q12: Unit 3
     - Q13-Q16: Unit 4
     - Q17-Q20: Unit 5
   - Format: "1. Question Text... A) Option B) Option..."

3. **Part B (Descriptive)**:
   - Contains exactly 5 main questions numbered 21 to 25.
   - **Unit Mapping**:
     - Q21: Unit 1
     - Q22: Unit 2
     - Q23: Unit 3
     - Q24: Unit 4
     - Q25: Unit 5
   - Structure: Each question usually has two sub-questions labeled 'a' and 'b' separated by '(OR)'.
     - Example: "21. a. Question... (OR) b. Question..."

4. **Part C (Descriptive/Scenario)**:
   - Contains 1 or 2 questions (usually Q26, Q27).
   - These are scenario-based or application-oriented questions.
   - Can be from any unit.

Please extract the text preserving this structure. Ensure tables (especially for MCQs) are converted to clear markdown. Keep the '(OR)' markers and sub-question labels ('a', 'b') intact.
"""

EXAM_PAPER_SCHEMA_PROMPT = """
Extract the exam paper content into the following JSON schema:

{
  "metadata": {
    "course_code": "string",
    "course_name": "string",
    "semester": "string",
    "exam_date": "string",
    "total_marks": "integer",
    "duration_minutes": "integer"
  },
  "questions": [
    {
      "number": "string (e.g., '1', '21.a')",
      "part": "string (A, B, or C)",
      "unit": "integer (1-5)",
      "type": "string (MCQ or Descriptive)",
      "content": "string",
      "options": {
        "A": "string",
        "B": "string",
        "C": "string",
        "D": "string"
      },
      "marks": "integer",
      "is_mandatory": "boolean",
      "has_or_option": "boolean"
    }
  ]
}

Rules for Extraction:
1. **Unit Inference**:
   - For Part A (Q1-20): Unit = ceil(QuestionNumber / 4)
   - For Part B (Q21-25): Unit = QuestionNumber - 20
   - For Part C: Unit is null/unknown unless explicitly stated.
2. **MCQs**: Extract options A, B, C, D into the options object.
3. **Descriptive**: Split 'a' and 'b' parts of questions (e.g., 21.a and 21.b) into separate question entries.
"""
