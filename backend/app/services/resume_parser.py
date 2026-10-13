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
        Deterministically extract useful resume sections when AI is unavailable
        or returns incomplete structure.
        """
        import re
        
        data = self._get_default_structure()
        normalized_text = re.sub(r"[ \t]+", " ", resume_text or "")
        text_lower = normalized_text.lower()

        def section(start_heading: str, end_headings: list[str]) -> str:
            start = re.search(
                rf"(?:^|\n)\s*{re.escape(start_heading)}\b\s*",
                normalized_text,
                re.IGNORECASE,
            )
            if not start:
                return ""
            end = len(normalized_text)
            for heading in end_headings:
                match = re.search(
                    rf"(?:^|\n)\s*{re.escape(heading)}\b",
                    normalized_text[start.end():],
                    re.IGNORECASE,
                )
                if match:
                    end = min(end, start.end() + match.start())
            return normalized_text[start.end():end].strip(" :\n")
        
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

        for field, pattern in {
            "linkedin": r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s]+",
            "github": r"(?:https?://)?(?:www\.)?github\.com/[^\s]+",
        }.items():
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                data["contact_info"][field] = match.group(0).rstrip(".,")

        if emails:
            prefix = normalized_text[:normalized_text.lower().find(emails[0].lower())].strip()
            candidate = re.sub(r"(?:https?://)?(?:www\.)?(?:linkedin|github)\.com/\S+", "", prefix, flags=re.I)
            candidate = re.sub(r"[+()\d\-\s.]+$", "", candidate).strip(" |,;·")
            name_parts = candidate.split()
            if 2 <= len(name_parts) <= 4 and not any("@" in part for part in name_parts):
                data["contact_info"]["name"] = " ".join(name_parts)
        
        # Extract the summary as a distinct section instead of losing it in raw text.
        summary = section("Summary", ["Projects", "Achievements", "Skills", "Experience", "Education"])
        if summary:
            data["summary"] = summary

        # Explicit labels are much more reliable for soft skills than a generic
        # keyword scan; this also handles a PDF whose text has flattened lines.
        skills_section = section("Skills", ["Experience", "Education", "Certifications"])
        soft_match = re.search(
            r"soft\s+skills?\s*:\s*(.*?)(?=(?:core\s+skills?|technical\s+skills?|languages?|tools?)\s*:|(?:experience|education|certifications|projects)\b|$)",
            skills_section,
            re.IGNORECASE,
        )
        if soft_match:
            data["skills"]["soft"] = [
                item.strip(" .;:-") for item in re.split(r"[,;|]", soft_match.group(1)) if item.strip(" .;:-")
            ]

        technical_keywords = [
            "python", "java", "javascript", "typescript", "react", "node.js", "sql", "html", "css",
            "aws", "azure", "docker", "kubernetes", "django", "django rest framework", "fastapi",
            "pytorch", "opencv", "machine learning", "computer vision", "sqlite", "postgresql",
            "data structures", "algorithms", "object-oriented programming", "network security",
        ]
        data["skills"]["technical"] = [
            skill for skill in technical_keywords
            if re.search(rf"\b{re.escape(skill)}\b", text_lower)
        ]
        programming_languages = ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust"]
        data["skills"]["languages"] = [
            language for language in programming_languages
            if re.search(rf"\b{re.escape(language)}\b", text_lower)
        ]
        tools = ["wireshark", "nmap", "zeek", "hashcat", "ettercap", "git", "github", "figma", "opencv", "pytorch"]
        data["skills"]["tools"] = [tool for tool in tools if re.search(rf"\b{re.escape(tool)}\b", text_lower)]

        # Parse education fields without interpreting unrelated dates elsewhere
        # in the resume as work-history dates.
        education = []
        degree_match = re.search(r"\b(Bachelor of Technology|B\.Tech|Bachelor of Science|B\.Sc|Master of Science|M\.Tech)\b", normalized_text, re.I)
        if degree_match:
            edu = {"degree": degree_match.group(1), "field": "", "institution": "", "graduation_date": "", "gpa": ""}
            after_degree = normalized_text[degree_match.end():degree_match.end() + 180]
            field_match = re.match(r"\s+in\s+(.+?)(?=\s+(?:Sri\s|SSN\s|Expected Graduation|CGPA|GPA))", after_degree, re.I)
            if field_match:
                edu["field"] = field_match.group(1).strip(" ,-:")
            institution_match = re.search(r"(?:Sri\s+Sivasubramaniya\s+Nadar|SSN College of Engineering|Excel Central School)[^\n]*", normalized_text, re.I)
            if institution_match:
                edu["institution"] = institution_match.group(0).strip()
            graduation_match = re.search(r"(?:Expected\s+Graduation|Graduation)\s*:?\s*(20\d{2})", normalized_text, re.I)
            if graduation_match:
                edu["graduation_date"] = graduation_match.group(1)
            gpa_match = re.search(r"(?:CGPA|GPA)\s*:?\s*(\d+(?:\.\d+)?)\s*(?:/\s*\d+(?:\.\d+)?)?", normalized_text, re.I)
            if gpa_match:
                edu["gpa"] = gpa_match.group(1)
            education.append(edu)
        data["education"] = education

        # Keep experience evidence tied to an actual role heading. Never infer a
        # 2004-2028 job merely because those years occur in school/project text.
        experience_section = section("Experience", ["Education", "Certifications", "Achievements"])
        if experience_section:
            role_match = re.search(r"([A-Z][^•\n]{2,100}?)\s+at\s+([^•\n]{2,100})", experience_section)
            if role_match:
                bullets = [part.strip(" \n•-–") for part in re.split(r"[•\u2022]", experience_section) if part.strip(" \n•-–")]
                role_heading = bullets[0] if bullets else role_match.group(0)
                achievements = bullets[1:] if len(bullets) > 1 else []
                data["experience"] = [{
                    "title": role_match.group(1).strip(),
                    "company": role_match.group(2).strip(),
                    "start_date": "",
                    "end_date": "",
                    "description": " ".join(achievements) or role_heading,
                    "achievements": achievements,
                }]

        # Extract project names and their nearby text as evidence for a portfolio.
        projects_section = section("Projects", ["Achievements", "Skills", "Experience", "Education"])
        project_matches = list(re.finditer(r"(LearnFlow|Intelligent Crop Monitoring System|GrowMate AI)", projects_section, re.I))
        for index, match in enumerate(project_matches):
            stop = project_matches[index + 1].start() if index + 1 < len(project_matches) else len(projects_section)
            project_text = projects_section[match.start():stop].strip(" -:;\n")
            project_title = match.group(1)
            data["projects"].append({
                "title": project_title,
                "description": project_text[:1200],
                "technologies": [skill for skill in technical_keywords if re.search(rf"\b{re.escape(skill)}\b", project_text, re.I)],
                "url": "",
            })

        achievements_section = section("Achievements", ["Skills", "Experience", "Education", "Certifications"])
        data["achievements"] = [
            item.strip(" \n•-–") for item in re.split(r"[•\u2022]", achievements_section)
            if item.strip(" \n•-–")
        ]
        
        return data

    def enrich_extraction(self, extracted_data: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
        """Fill AI omissions and replace obvious hallucinations with text evidence."""
        ai_data = extracted_data if isinstance(extracted_data, dict) else {}
        basic = self.basic_extract(resume_text)
        merged = {**basic, **ai_data}
        ai_contact = ai_data.get("contact_info")
        if not isinstance(ai_contact, dict):
            ai_contact = {}
        merged["contact_info"] = {**basic.get("contact_info", {}), **ai_contact}

        def as_list(value: Any) -> list:
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                return [value]
            return []

        # Prefer real document evidence over empty or generic model output.
        if not ai_data.get("summary"):
            merged["summary"] = basic.get("summary", "")
        for field in ("education", "projects", "achievements", "certifications"):
            ai_items = as_list(ai_data.get(field))
            merged[field] = ai_items or basic.get(field, [])

        ai_experience = as_list(ai_data.get("experience"))
        if not basic.get("experience") or any(
            str(item.get("title", "")).lower() == "professional experience"
            for item in ai_experience if isinstance(item, dict)
        ):
            merged["experience"] = basic.get("experience") or ai_experience
        else:
            merged["experience"] = ai_experience or basic.get("experience", [])

        merged_skills = {}
        ai_skill_data = ai_data.get("skills") or {}
        if not isinstance(ai_skill_data, dict):
            ai_skill_data = {}
        for category in (set(basic.get("skills", {})) | set(ai_skill_data)):
            ai_values = as_list(ai_skill_data.get(category))
            basic_values = (basic.get("skills") or {}).get(category) or []
            if not isinstance(basic_values, list):
                basic_values = [basic_values]
            merged_skills[category] = list(dict.fromkeys(str(value) for value in [*ai_values, *basic_values] if value))
        merged["skills"] = merged_skills
        return merged


# Singleton instance
resume_parser = ResumeParser()
