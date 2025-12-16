from llama_parse import LlamaParse
from app.config import settings
import logging
from typing import Dict, List
import asyncio

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

    async def extract_questions_from_text(self, text: str) -> List[Dict]:
        """
        Parse extracted text to find questions.
        Uses pattern matching to identify question markers.
        """
        if not text or not text.strip():
            return []

        questions = []
        lines = text.split('\n')

        current_question = ""
        question_markers = [
            "Q.", "Q ", "Question ", "Ques.", "q.", "q ",
            "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.",
            "a)", "b)", "c)", "d)", "e)",
            "(a)", "(b)", "(c)", "(d)", "(e)",
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with a question marker
            is_question_start = any(
                line.startswith(marker) or 
                line.lower().startswith(marker.lower())
                for marker in question_markers
            )

            # Also check for numbered questions like "1. ", "2. "
            if not is_question_start and len(line) > 2:
                if line[0].isdigit() and line[1] in ['.', ')', ':']:
                    is_question_start = True

            if is_question_start:
                # Save previous question if exists
                if current_question.strip():
                    questions.append(self._create_question_dict(current_question.strip()))
                current_question = line
            else:
                # Continue building current question
                current_question += " " + line

        # Don't forget the last question
        if current_question.strip():
            questions.append(self._create_question_dict(current_question.strip()))

        logger.info(f"Extracted {len(questions)} questions from text")
        return questions

    def _create_question_dict(self, content: str) -> Dict:
        """Create a question dictionary with metadata extraction."""
        # Try to extract marks if present (e.g., "[5 marks]", "(10m)", etc.)
        marks = None
        marks_patterns = [
            r'\[(\d+)\s*marks?\]',
            r'\((\d+)m\)',
            r'\((\d+)\s*marks?\)',
        ]
        
        import re
        for pattern in marks_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                marks = int(match.group(1))
                break

        # Try to detect question type
        question_type = "unknown"
        content_lower = content.lower()
        if "explain" in content_lower or "describe" in content_lower or "discuss" in content_lower:
            question_type = "descriptive"
        elif "define" in content_lower or "what is" in content_lower:
            question_type = "definition"
        elif "differentiate" in content_lower or "compare" in content_lower:
            question_type = "comparison"
        elif "solve" in content_lower or "calculate" in content_lower:
            question_type = "numerical"

        return {
            "content": content,
            "subject": None,  # Can be enhanced with NER/classification
            "topic": None,
            "difficulty": None,
            "question_type": question_type,
            "year": None,
            "marks": marks,
        }


llama_service = LlamaCloudService()
