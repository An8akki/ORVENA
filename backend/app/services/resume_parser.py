"""Service for parsing resume files and extracting structured data."""

import io
from typing import Dict, Any, Optional
from pypdf import PdfReader
import docx
from app.services.llm import get_llm_provider


class ResumeParser:
    """Parser for extracting text and data from resume files."""

    EXTRACTION_PROMPT = """You are an expert resume parser. Extract structured information from this resume text.

Extract and return a JSON object with the following structure:
{
  "contact_info": {
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "City, State",
    "linkedin": "LinkedIn URL",
    "github": "GitHub URL",
    "portfolio": "Portfolio URL"
  },
  "summary": "Professional summary or objective",
  "education": [
    {
      "institution": "University Name",
      "degree": "Degree Name",
      "field": "Field of Study",
      "graduation_date": "YYYY-MM",
      "gpa": "GPA if mentioned"
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "title": "Job Title",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "description": "Job description",
      "achievements": ["achievement 1", "achievement 2"]
    }
  ],
  "skills": {
    "technical": ["skill1", "skill2"],
    "soft": ["skill1", "skill2"],
    "languages": ["language1", "language2"],
    "tools": ["tool1", "tool2"]
  },
  "projects": [
    {
      "title": "Project Name",
      "description": "Project description",
      "technologies": ["tech1", "tech2"],
      "url": "Project URL if available"
    }
  ],
  "certifications": [
    {
      "name": "Certification Name",
      "issuer": "Issuing Organization",
      "date": "YYYY-MM"
    }
  ]
}

Return ONLY the JSON object, no other text."""

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return "\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            doc_file = io.BytesIO(file_content)
            doc = docx.Document(doc_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            return "\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")

    def extract_text(self, file_content: bytes, file_type: str) -> str:
        """Extract text from resume file based on type."""
        if file_type == "application/pdf":
            return self.extract_text_from_pdf(file_content)
        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            return self.extract_text_from_docx(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    async def parse_resume_with_ai(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text using AI to extract structured data."""
        llm = get_llm_provider()
        
        try:
            response = await llm.generate_with_system(
                system_prompt=self.EXTRACTION_PROMPT,
                user_message=f"Resume Text:\n\n{resume_text[:4000]}",  # Limit to avoid token limits
                temperature=0.3,
                max_tokens=2000,
            )
            
            # Parse JSON response
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                return extracted_data
            else:
                # Return basic structure if parsing fails
                return self._get_default_structure()
                
        except Exception as e:
            print(f"AI parsing error: {str(e)}")
            return self._get_default_structure()

    def _get_default_structure(self) -> Dict[str, Any]:
        """Get default resume structure if AI parsing fails."""
        return {
            "contact_info": {},
            "summary": "",
            "education": [],
            "experience": [],
            "skills": {
                "technical": [],
                "soft": [],
                "languages": [],
                "tools": []
            },
            "projects": [],
            "certifications": []
        }
    
    def basic_extract(self, resume_text: str) -> Dict[str, Any]:
        """
        Basic text-based extraction without AI.
        Fallback method that always works.
        """
        import re
        
        data = self._get_default_structure()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        if emails:
            data['contact_info']['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        phones = re.findall(phone_pattern, resume_text)
        if phones:
            data['contact_info']['phone'] = phones[0]
        
        # Extract years (for experience duration)
        years = re.findall(r'20\d{2}', resume_text)
        if len(years) >= 2:
            # Assume has work experience if multiple years mentioned
            data['experience'].append({
                'company': 'Unknown',
                'title': 'Professional Experience',
                'start_date': years[0],
                'end_date': years[-1],
                'description': 'Experience details extracted from resume',
                'achievements': []
            })
        
        # Extract common tech keywords as skills
        tech_keywords = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes']
        text_lower = resume_text.lower()
        found_skills = [kw for kw in tech_keywords if kw in text_lower]
        if found_skills:
            data['skills']['technical'] = found_skills
        
        # Try to extract name (first line often has name)
        lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
        if lines:
            # First non-empty line is often the name
            potential_name = lines[0]
            if len(potential_name.split()) <= 4 and not '@' in potential_name:
                data['contact_info']['name'] = potential_name
        
        return data


# Singleton instance
resume_parser = ResumeParser()
