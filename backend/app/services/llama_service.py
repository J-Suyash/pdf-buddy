from llama_cloud_services import LlamaExtract
from app.config import settings
from app.schemas.question import ExamPaperMetadata
import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class LlamaCloudService:
    """Service for extracting structured data from exam papers using LlamaExtract."""
    
    def __init__(self):
        """Initialize LlamaExtract client with API key."""
        try:
            # Use llama_cloud_api_key for LlamaExtract, fallback to llama_api_key
            api_key = settings.llama_cloud_api_key or settings.llama_api_key
            if not api_key:
                raise ValueError("No API key found. Set LLAMA_CLOUD_API_KEY in .env")
            
            self.extractor = LlamaExtract(api_key=api_key)
            self.agent_name = "SRM PYQ"  # Pre-configured agent with exam schema
            self.agent = None
            logger.info("LlamaExtract initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LlamaExtract: {e}")
            self.extractor = None

    def _get_agent(self):
        """Get or cache the extraction agent."""
        if self.agent is None:
            try:
                self.agent = self.extractor.get_agent(name=self.agent_name)
                logger.info(f"Retrieved extraction agent: {self.agent_name}")
            except Exception as e:
                logger.error(f"Failed to get agent '{self.agent_name}': {e}")
                raise
        return self.agent

    async def extract_from_pdf(self, file_path: str) -> Dict:
        """
        Extract structured data from PDF using LlamaExtract API with pre-configured agent.

        Returns:
        {
            "text": "full markdown content",
            "pages": [...],
            "metadata": {...},
            "structured_data": {...}  # Extracted JSON following the schema
        }
        """
        if not self.extractor:
            raise Exception("LlamaExtract not initialized. Check LLAMA_API_KEY in .env")

        try:
            logger.info(f"Extracting from PDF: {file_path}")
            
            # Get the pre-configured agent
            agent = self._get_agent()
            
            # Extract data using the agent (this uses the schema you defined)
            result = agent.extract(file_path)
            
            # The result contains structured data according to your schema
            structured_data = result.data if hasattr(result, 'data') else {}
            
            # Convert to dict if it's a Pydantic model
            if hasattr(structured_data, 'dict'):
                structured_data = structured_data.dict()
            elif hasattr(structured_data, 'model_dump'):
                structured_data = structured_data.model_dump()
            
            logger.info(f"Successfully extracted structured data from {file_path}")
            logger.debug(f"Structured data keys: {structured_data.keys() if isinstance(structured_data, dict) else 'N/A'}")
            
            # Generate markdown representation for backward compatibility
            markdown_text = self._convert_to_markdown(structured_data)
            
            return {
                "text": markdown_text,
                "pages": [{"text": markdown_text, "page_num": 1}],  # Simplified
                "metadata": structured_data.get("header", {}) if isinstance(structured_data, dict) else {},
                "structured_data": structured_data
            }

        except Exception as e:
            logger.error(f"LlamaExtract extraction failed for {file_path}: {e}")
            raise

    def _convert_to_markdown(self, structured_data: Dict) -> str:
        """Convert structured JSON data to markdown for backward compatibility."""
        if not isinstance(structured_data, dict):
            return str(structured_data)
        
        lines = []
        
        # Header
        header = structured_data.get("header", {})
        if header:
            lines.append(f"# {header.get('course_code', '')} - {header.get('course_name', '')}")
            lines.append(f"**Semester:** {header.get('semester', '')}")
            lines.append(f"**Exam Date:** {header.get('exam_date_month', '')}")
            lines.append(f"**Max Marks:** {header.get('max_marks', '')}")
            lines.append(f"**Duration:** {header.get('duration', '')}")
            lines.append("")
        
        # Part A
        part_a = structured_data.get("part_a", {})
        if part_a:
            lines.append("# PART - A")
            if part_a.get("instructions"):
                lines.append(part_a["instructions"])
            lines.append("")
            
            for q in part_a.get("questions", []):
                q_num = q.get("question_number", "?")
                lines.append(f"**{q_num}.** {q.get('question_text', '')}")
                options = q.get("options", {})
                for opt_key in ["A", "B", "C", "D"]:
                    if opt_key in options:
                        lines.append(f"   {opt_key}) {options[opt_key]}")
                lines.append("")
        
        # Part B
        part_b = structured_data.get("part_b", {})
        if part_b:
            lines.append("# PART - B")
            if part_b.get("instructions"):
                lines.append(part_b["instructions"])
            lines.append("")
            
            for q in part_b.get("questions", []):
                q_num = q.get("question_number", "?")
                lines.append(f"# {q_num}")
                for sub_q in q.get("sub_questions", []):
                    label = sub_q.get("label", "")
                    text = sub_q.get("text", "")
                    is_alt = sub_q.get("is_alternative", False)
                    if is_alt:
                        lines.append("(OR)")
                    lines.append(f"{label}. {text}")
                lines.append("")
        
        # Part C
        part_c = structured_data.get("part_c", {})
        if part_c:
            lines.append("# PART - C")
            if part_c.get("instructions"):
                lines.append(part_c["instructions"])
            lines.append("")
            
            for q in part_c.get("questions", []):
                q_num = q.get("question_number", "?")
                lines.append(f"# {q_num}")
                lines.append(q.get("question_text", ""))
                lines.append("")
        
        return "\n".join(lines)

    def _map_question_to_unit(self, question_number: str, part: str) -> Optional[int]:
        """
        Map question number to unit based on consistent structure.
        
        Part A (MCQs): 5 units × 4 questions = 20 questions
        - Q1-4: Unit 1, Q5-8: Unit 2, Q9-12: Unit 3, Q13-16: Unit 4, Q17-20: Unit 5
        
        Part B: 5 questions (each with .a and .b)
        - Q21: Unit 1, Q22: Unit 2, Q23: Unit 3, Q24: Unit 4, Q25: Unit 5
        
        Part C: Random (return None)
        """
        try:
            import re
            # Extract base question number
            base_num = int(re.match(r'(\d+)', str(question_number)).group(1))
            
            if part == "A":
                # MCQs: 1-20
                unit = ((base_num - 1) // 4) + 1
                return min(unit, 5)
            elif part == "B":
                # Descriptive: 21-25
                unit = base_num - 20
                return min(max(unit, 1), 5)
            else:
                # Part C: Random/unknown
                return None
        except Exception as e:
            logger.warning(f"Could not map question {question_number} to unit: {e}")
            return None

    async def extract_exam_metadata(self, text: str) -> ExamPaperMetadata:
        """Extract exam paper metadata from structured data or text."""
        # If we have structured_data in the extraction result, use it
        # For now, this is a placeholder that will be called with markdown text
        # The actual metadata comes from the structured extraction
        metadata = ExamPaperMetadata()
        
        # This will be populated from structured_data in the processor
        logger.info("Metadata extraction handled by structured extraction")
        return metadata

    async def extract_questions_by_parts(self, text: str, structured_data: Optional[Dict] = None) -> Dict[str, List[Dict]]:
        """
        Extract questions organized by parts using structured data from LlamaExtract.
        
        Args:
            text: Markdown text (for backward compatibility)
            structured_data: Structured JSON from LlamaExtract
        
        Returns: {
            "A": [...],  # MCQs
            "B": [...],  # Descriptive
            "C": [...]   # Scenario
        }
        """
        result = {"A": [], "B": [], "C": []}
        
        if not structured_data or not isinstance(structured_data, dict):
            logger.warning("No structured data provided, cannot extract questions")
            return result
        
        # Extract Part A (MCQs)
        part_a = structured_data.get("part_a", {})
        for q in part_a.get("questions", []):
            q_num = str(q.get("question_number", ""))
            unit = self._map_question_to_unit(q_num, "A")
            
            result["A"].append({
                "content": q.get("question_text", ""),
                "question_number": q_num,
                "part": "A",
                "part_marks": 1,  # Part A is always 1 mark
                "unit": unit,
                "is_mcq": True,
                "options": q.get("options", {}),
                "marks": 1,
                "question_type": "mcq",
                "is_mandatory": True,
                "has_or_option": False,
            })
        
        # Extract Part B (Descriptive)
        part_b = structured_data.get("part_b", {})
        for q in part_b.get("questions", []):
            q_num = q.get("question_number", "")
            unit = self._map_question_to_unit(str(q_num), "B")
            
            for sub_q in q.get("sub_questions", []):
                label = sub_q.get("label", "")
                full_q_num = f"{q_num}.{label}"
                is_alt = sub_q.get("is_alternative", False)
                
                result["B"].append({
                    "content": sub_q.get("text", ""),
                    "question_number": full_q_num,
                    "part": "B",
                    "part_marks": 8,  # Part B is usually 8 marks
                    "unit": unit,
                    "is_mcq": False,
                    "marks": 8,
                    "question_type": "descriptive",
                    "is_mandatory": True,
                    "has_or_option": is_alt,
                })
        
        # Extract Part C (Scenario)
        part_c = structured_data.get("part_c", {})
        for q in part_c.get("questions", []):
            q_num = str(q.get("question_number", ""))
            
            result["C"].append({
                "content": q.get("question_text", ""),
                "question_number": q_num,
                "part": "C",
                "part_marks": 15,  # Part C is usually 15 marks
                "unit": None,  # Part C can be from any unit
                "is_mcq": False,
                "marks": 15,
                "question_type": "descriptive",
                "is_mandatory": False,  # Part C is "ANY ONE"
                "has_or_option": False,
            })
        
        total_questions = sum(len(questions) for questions in result.values())
        logger.info(f"Extracted {total_questions} questions from structured data: A={len(result['A'])}, B={len(result['B'])}, C={len(result['C'])}")
        
        return result

    async def extract_questions_from_text(self, text: str, structured_data: Optional[Dict] = None) -> List[Dict]:
        """
        Legacy method - parse questions from text or structured data.
        """
        # Use the new part-based extraction
        parts = await self.extract_questions_by_parts(text, structured_data)
        
        # Combine all parts
        all_questions = []
        for part_questions in parts.values():
            all_questions.extend(part_questions)
        
        return all_questions


llama_service = LlamaCloudService()
