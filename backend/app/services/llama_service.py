from llama_parse import LlamaParse
from app.config import settings
from app.schemas.question import ExamPaperMetadata
import logging
from typing import Dict, List
import asyncio
import re

logger = logging.getLogger(__name__)


class LlamaCloudService:
    def __init__(self):
        """Initialize LlamaParse client with API key."""
        try:
            self.parser = LlamaParse(
                api_key=settings.llama_api_key,
                result_type="markdown",  # Get markdown output
                verbose=True,
                language="en",
            )
            logger.info("LlamaParse initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LlamaParse: {e}")
            self.parser = None

    async def extract_from_pdf(self, file_path: str) -> Dict:
        """
        Extract structured data from PDF using LlamaParse API.

        Returns:
        {
            "text": "full markdown content",
            "pages": [...],
            "metadata": {...}
        }
        """
        if not self.parser:
            raise Exception("LlamaParse not initialized. Check LLAMA_API_KEY in .env")

        try:
            logger.info(f"Extracting from PDF: {file_path}")

            # Parse the PDF - LlamaParse handles async internally
            documents = await asyncio.to_thread(
                self.parser.load_data, file_path
            )

            if not documents:
                logger.warning(f"No content extracted from {file_path}")
                return {
                    "text": "",
                    "pages": [],
                    "metadata": {}
                }

            # Combine all document pages
            full_text = "\n\n".join([doc.text for doc in documents])
            
            # Extract metadata
            metadata = {}
            if documents:
                metadata = documents[0].metadata if hasattr(documents[0], 'metadata') else {}

            logger.info(f"Successfully extracted {len(full_text)} characters from {file_path}")

            return {
                "text": full_text,
                "pages": [{"text": doc.text, "page_num": i+1} for i, doc in enumerate(documents)],
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"LlamaParse extraction failed for {file_path}: {e}")
            raise

    async def extract_exam_metadata(self, text: str) -> ExamPaperMetadata:
        """Extract exam paper metadata from header."""
        metadata = ExamPaperMetadata()
        
        lines = text.split('\n')[:30]  # Focus on first 30 lines
        
        for line in lines:
            line = line.strip()
            
            # Extract course code (e.g., "21CSE321J")
            course_match = re.search(r'(\d{2}[A-Z]{3}\d{3}[A-Z]?)', line)
            if course_match and not metadata.course_code:
                metadata.course_code = course_match.group(1)
            
            # Extract course name (usually follows course code)
            if metadata.course_code and metadata.course_code in line:
                # Get text after course code
                parts = line.split(metadata.course_code)
                if len(parts) > 1:
                    course_name = parts[1].strip(' -#')
                    if course_name and len(course_name) > 3:
                        metadata.course_name = course_name
            
            # Extract semester
            semester_match = re.search(r'(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth)\s+Semester', line, re.IGNORECASE)
            if semester_match:
                metadata.semester = semester_match.group(0)
            
            # Extract exam date
            month_match = re.search(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d{4})', line, re.IGNORECASE)
            if month_match:
                metadata.exam_date = month_match.group(0)
            
            # Extract total marks
            marks_match = re.search(r'Max\.\s*Marks?\s*:\s*(\d+)', line, re.IGNORECASE)
            if marks_match:
                metadata.total_marks = int(marks_match.group(1))
            
            # Extract duration
            time_match = re.search(r'Time\s*:\s*(\d+)\s*hours?', line, re.IGNORECASE)
            if time_match:
                metadata.duration_minutes = int(time_match.group(1)) * 60
        
        logger.info(f"Extracted metadata: {metadata.dict()}")
        return metadata

    async def extract_questions_by_parts(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract questions organized by parts (A, B, C).
        Returns: {
            "A": [...],
            "B": [...],
            "C": [...]
        }
        """
        result = {"A": [], "B": [], "C": []}
        
        # Split by PART headers
        part_a_match = re.search(r'#?\s*PART\s*-?\s*A.*?(?=#?\s*PART\s*-?\s*B|$)', text, re.DOTALL | re.IGNORECASE)
        part_b_match = re.search(r'#?\s*PART\s*-?\s*B.*?(?=#?\s*PART\s*-?\s*C|$)', text, re.DOTALL | re.IGNORECASE)
        part_c_match = re.search(r'#?\s*PART\s*-?\s*C.*$', text, re.DOTALL | re.IGNORECASE)
        
        # Extract part marks from headers
        part_a_marks = self._extract_part_marks(part_a_match.group(0) if part_a_match else "")
        part_b_marks = self._extract_part_marks(part_b_match.group(0) if part_b_match else "")
        part_c_marks = self._extract_part_marks(part_c_match.group(0) if part_c_match else "")
        
        # Parse each part
        if part_a_match:
            result["A"] = self._parse_mcq_questions(part_a_match.group(0), "A", part_a_marks)
        if part_b_match:
            result["B"] = self._parse_descriptive_questions(part_b_match.group(0), "B", part_b_marks)
        if part_c_match:
            result["C"] = self._parse_descriptive_questions(part_c_match.group(0), "C", part_c_marks)
        
        total_questions = sum(len(questions) for questions in result.values())
        logger.info(f"Extracted {total_questions} questions by parts: A={len(result['A'])}, B={len(result['B'])}, C={len(result['C'])}")
        
        return result

    def _extract_part_marks(self, part_text: str) -> int:
        """Extract marks from part header like (20 x 1 = 20 Marks)."""
        # Match patterns like "20 x 1 = 20" or "5 x 8 = 40"
        match = re.search(r'(\d+)\s*x\s*(\d+)', part_text[:200])
        if match:
            return int(match.group(2))  # Return individual question marks
        return 0

    def _parse_mcq_questions(self, part_text: str, part_name: str, part_marks: int) -> List[Dict]:
        """Parse MCQ questions from Part A with table format."""
        questions = []
        
        # Split into lines
        lines = part_text.split('\n')
        
        current_question = None
        current_options = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or 'PART' in line or 'Answer ALL' in line:
                continue
            
            # Detect question number at start of line (e.g., "| 1. |")
            q_num_match = re.match(r'\|\s*(\d+)\.\s*\|', line)
            if q_num_match:
                # Save previous question if exists
                if current_question:
                    questions.append({
                        "content": current_question["text"],
                        "question_number": str(current_question["number"]),
                        "part": part_name,
                        "part_marks": part_marks,
                        "is_mcq": True,
                        "options": current_options.copy(),
                        "marks": part_marks,
                        "question_type": "mcq",
                        "is_mandatory": True,
                    })
                
                # Start new question
                question_num = q_num_match.group(1)
                # Extract question text (between first | and last |)
                question_text = re.sub(r'^\|\s*\d+\.\s*\|', '', line)
                question_text = re.sub(r'\|$', '', question_text).strip()
                
                current_question = {"number": question_num, "text": question_text}
                current_options = {}
            
            # Detect options (A), B), C), D) in the line
            elif current_question:
                # Look for pattern "| A) text | B) text | C) text | D) text |"
                option_matches = re.findall(r'([A-D])\)\s*([^|]+)', line)
                for opt_letter, opt_text in option_matches:
                    current_options[opt_letter] = opt_text.strip()
        
        # Don't forget the last question
        if current_question:
            questions.append({
                "content": current_question["text"],
                "question_number": str(current_question["number"]),
                "part": part_name,
                "part_marks": part_marks,
                "is_mcq": True,
                "options": current_options.copy() if current_options else None,
                "marks": part_marks,
                "question_type": "mcq",
                "is_mandatory": True,
            })
        
        logger.info(f"Parsed {len(questions)} MCQ questions from Part {part_name}")
        return questions

    def _parse_descriptive_questions(self, part_text: str, part_name: str, part_marks: int) -> List[Dict]:
        """Parse descriptive questions with OR options."""
        questions = []
        
        lines = part_text.split('\n')
        
        current_question = ""
        current_number = None
        has_or = False
        
        for line in lines:
            line = line.strip()
            if not line or 'PART' in line or 'Answer' in line:
                continue
            
            # Detect question number (e.g., "# 21", "21", "a.", "b.")
            q_num_match = re.match(r'^#?\s*(\d+\.?[a-z]?)\s*\.?\s*$', line)
            if q_num_match:
                # Save previous question
                if current_question and current_number:
                    questions.append({
                        "content": current_question.strip(),
                        "question_number": current_number,
                        "part": part_name,
                        "part_marks": part_marks,
                        "is_mcq": False,
                        "marks": part_marks,
                        "question_type": "descriptive",
                        "is_mandatory": part_name != "C",  # Part C is usually "ANY ONE"
                        "has_or_option": has_or,
                    })
                
                # Start new question
                current_number = q_num_match.group(1)
                current_question = ""
                has_or = False
            
            # Detect (OR) marker
            elif re.match(r'^\(OR\)$', line, re.IGNORECASE):
                # Save previous sub-question
                if current_question and current_number:
                    questions.append({
                        "content": current_question.strip(),
                        "question_number": current_number,
                        "part": part_name,
                        "part_marks": part_marks,
                        "is_mcq": False,
                        "marks": part_marks,
                        "question_type": "descriptive",
                        "is_mandatory": part_name != "C",
                        "has_or_option": True,
                    })
                
                # Reset for OR option
                current_question = ""
                has_or = True
            
            # Detect sub-questions (a., b.)
            elif re.match(r'^[a-z]\.\s', line):
                # This is a sub-question, append to current
                current_question += "\n" + line
            
            # Regular content line
            else:
                current_question += " " + line
        
        # Don't forget the last question
        if current_question and current_number:
            questions.append({
                "content": current_question.strip(),
                "question_number": current_number,
                "part": part_name,
                "part_marks": part_marks,
                "is_mcq": False,
                "marks": part_marks,
                "question_type": "descriptive",
                "is_mandatory": part_name != "C",
                "has_or_option": has_or,
            })
        
        logger.info(f"Parsed {len(questions)} descriptive questions from Part {part_name}")
        return questions

    async def extract_questions_from_text(self, text: str) -> List[Dict]:
        """
        Legacy method - parse questions from text.
        Now primarily uses extract_questions_by_parts for better structure.
        """
        # Use the new part-based extraction
        parts = await self.extract_questions_by_parts(text)
        
        # Combine all parts
        all_questions = []
        for part_questions in parts.values():
            all_questions.extend(part_questions)
        
        return all_questions


llama_service = LlamaCloudService()
