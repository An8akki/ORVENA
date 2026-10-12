"""
Structured Resume Parser

Parses resume text into structured sections: contact info, education,
work experience, skills, projects, certifications, etc.

Uses pattern matching and heuristics - works offline without ML/AI.
"""
import re
import logging
from typing import Optional
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParsedResume:
    """Structured resume data."""
    
    # Contact Information
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    
    # Professional Summary
    summary: Optional[str] = None
    
    # Education
    education: List[Dict[str, Any]] = field(default_factory=list)
    
    # Work Experience
    experience: List[Dict[str, Any]] = field(default_factory=list)
    
    # Skills
    skills: List[str] = field(default_factory=list)
    
    # Projects
    projects: List[Dict[str, Any]] = field(default_factory=list)
    
    # Certifications
    certifications: List[Dict[str, Any]] = field(default_factory=list)
    
    # Languages
    languages: List[str] = field(default_factory=list)
    
    # Raw sections (for debugging/reference)
    raw_sections: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    parse_confidence: float = 0.0
    sections_found: List[str] = field(default_factory=list)


class StructuredResumeParser:
    """
    Parses resume text into structured sections.
    
    Uses pattern matching and section headers to identify and extract:
    - Contact information (email, phone, links)
    - Education history
    - Work experience
    - Skills lists
    - Projects
    - Certifications
    """
    
    # Common section headers (case-insensitive patterns)
    SECTION_PATTERNS = {
        'education': [
            r'^education$',
            r'^academic background$',
            r'^degrees?$',
            r'^qualifications?$'
        ],
        'experience': [
            r'^(?:work\s+)?experience$',
            r'^(?:professional\s+)?(?:work\s+)?history$',
            r'^employment$',
            r'^career\s+history$'
        ],
        'skills': [
            r'^skills?$',
            r'^technical\s+skills?$',
            r'^core\s+competenc(?:y|ies)$',
            r'^expertise$'
        ],
        'projects': [
            r'^projects?$',
            r'^(?:personal|academic)\s+projects?$',
            r'^portfolio$'
        ],
        'certifications': [
            r'^certifications?$',
            r'^certificates?$',
            r'^professional\s+certifications?$',
            r'^licenses?$'
        ],
        'summary': [
            r'^(?:professional\s+)?summary$',
            r'^objective$',
            r'^career\s+objective$',
            r'^profile$',
            r'^about\s+me$'
        ]
    }
    
    # Regex patterns for extraction
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}|\b\d{3}-\d{4}\b'
    LINKEDIN_PATTERN = r'(?:linkedin\.com/in/|linkedin\.com/pub/)[\w-]+'
    GITHUB_PATTERN = r'github\.com/[\w-]+'
    URL_PATTERN = r'https?://(?:www\.)?[\w\-\.]+\.\w{2,}(?:/[\w\-\./?%&=]*)?'
    
    def parse(self, text: str) -> ParsedResume:
        """
        Parse resume text into structured data.
        
        Args:
            text: Raw resume text
            
        Returns:
            ParsedResume with extracted structured data
        """
        resume = ParsedResume()
        
        # Normalize text
        text = self._normalize_text(text)
        
        # Extract contact information
        self._extract_contact_info(text, resume)
        
        # Split text into sections
        sections = self._split_into_sections(text)
        resume.raw_sections = sections
        resume.sections_found = list(sections.keys())
        
        # Parse each section
        for section_name, section_text in sections.items():
            if section_name == 'education':
                resume.education = self._parse_education(section_text)
            elif section_name == 'experience':
                resume.experience = self._parse_experience(section_text)
            elif section_name == 'skills':
                resume.skills = self._parse_skills(section_text)
            elif section_name == 'projects':
                resume.projects = self._parse_projects(section_text)
            elif section_name == 'certifications':
                resume.certifications = self._parse_certifications(section_text)
            elif section_name == 'summary':
                resume.summary = section_text.strip()
        
        # Calculate parse confidence
        resume.parse_confidence = self._calculate_confidence(resume)
        
        return resume
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text formatting."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def _extract_contact_info(self, text: str, resume: ParsedResume) -> None:
        """Extract contact information from text."""
        # Email
        email_matches = re.findall(self.EMAIL_PATTERN, text)
        if email_matches:
            resume.email = email_matches[0]
        
        # Phone
        phone_matches = re.findall(self.PHONE_PATTERN, text)
        if phone_matches:
            resume.phone = phone_matches[0]
        
        # LinkedIn
        linkedin_matches = re.findall(self.LINKEDIN_PATTERN, text, re.IGNORECASE)
        if linkedin_matches:
            resume.linkedin = f"https://{linkedin_matches[0]}"
        
        # GitHub
        github_matches = re.findall(self.GITHUB_PATTERN, text, re.IGNORECASE)
        if github_matches:
            resume.github = f"https://{github_matches[0]}"
        
        # Name (heuristic: first line if it doesn't contain common keywords)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line_clean = line.strip()
            if len(line_clean) > 3 and len(line_clean) < 50:
                # Check if it looks like a name (no @ symbol, no numbers except spaces)
                if '@' not in line_clean and not re.search(r'\d{4}', line_clean):
                    if not any(kw in line_clean.lower() for kw in ['resume', 'cv', 'curriculum']):
                        resume.name = line_clean
                        break
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Split text into sections based on headers."""
        sections = {}
        lines = text.split('\n')
        
        current_section = 'header'
        current_content = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this line is a section header
            section_found = None
            for section_key, patterns in self.SECTION_PATTERNS.items():
                for pattern in patterns:
                    if re.match(pattern, line_stripped, re.IGNORECASE):
                        section_found = section_key
                        break
                if section_found:
                    break
            
            if section_found:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = section_found
                current_content = []
            else:
                # Add to current section
                if line_stripped:
                    current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _parse_education(self, text: str) -> List[Dict[str, Any]]:
        """Parse education section."""
        education_entries = []
        
        # Split by double newlines (assume each degree is separated)
        entries = re.split(r'\n\s*\n', text)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            edu = {
                'raw_text': entry.strip(),
                'degree': None,
                'field_of_study': None,
                'institution': None,
                'graduation_year': None
            }
            
            # Extract year (4-digit number, prefer later years)
            years = re.findall(r'\b(19\d{2}|20\d{2})\b', entry)
            if years:
                edu['graduation_year'] = int(years[-1])  # Take most recent
            
            # Extract degree keywords
            degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma', 'b.s.', 'm.s.', 'b.a.', 'm.a.']
            for keyword in degree_keywords:
                if keyword in entry.lower():
                    # Extract the line containing the degree
                    for line in entry.split('\n'):
                        if keyword in line.lower():
                            edu['degree'] = line.strip()
                            break
            
            # Extract institution (heuristic: line without degree keywords)
            lines = entry.split('\n')
            for line in lines:
                line_clean = line.strip()
                if len(line_clean) > 5 and not any(kw in line_clean.lower() for kw in degree_keywords):
                    # Likely institution name
                    if not edu['institution']:
                        edu['institution'] = line_clean
            
            education_entries.append(edu)
        
        return education_entries
    
    def _parse_experience(self, text: str) -> List[Dict[str, Any]]:
        """Parse work experience section."""
        experience_entries = []
        
        # Split by job title patterns (lines that look like titles followed by company/dates)
        # First try splitting by double newlines, then by recognizing job title patterns
        lines = text.split('\n')
        
        current_entry = []
        for line in lines:
            line = line.strip()
            if not line:
                if current_entry:
                    # Process accumulated entry
                    entry_text = '\n'.join(current_entry)
                    if self._looks_like_job_title(current_entry[0]):
                        exp = self._parse_single_experience(entry_text)
                        if exp:
                            experience_entries.append(exp)
                    current_entry = []
                continue
            
            # Check if this line starts a new job entry
            if self._looks_like_job_title(line) and current_entry:
                # Process previous entry
                entry_text = '\n'.join(current_entry)
                exp = self._parse_single_experience(entry_text)
                if exp:
                    experience_entries.append(exp)
                current_entry = [line]
            else:
                current_entry.append(line)
        
        # Process last entry
        if current_entry:
            entry_text = '\n'.join(current_entry)
            exp = self._parse_single_experience(entry_text)
            if exp:
                experience_entries.append(exp)
        
        return experience_entries
    
    def _looks_like_job_title(self, line: str) -> bool:
        """Check if a line looks like a job title."""
        job_keywords = ['engineer', 'developer', 'manager', 'analyst', 'designer', 
                       'scientist', 'architect', 'consultant', 'specialist', 'lead',
                       'director', 'coordinator', 'administrator', 'intern']
        line_lower = line.lower()
        
        # Has job keyword and not a bullet point
        if any(keyword in line_lower for keyword in job_keywords):
            if not line.startswith(('•', '-', '*', '◦')):
                return True
        
        return False
    
    def _parse_single_experience(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse a single work experience entry."""
        if not entry.strip():
            return None
        
        exp = {
            'raw_text': entry.strip(),
            'title': None,
            'company': None,
            'start_date': None,
            'end_date': None,
            'current': False,
            'description': []
        }
        
        # Extract dates
        date_patterns = [
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4})',
            r'((?:Present|Current|Now))'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, entry, re.IGNORECASE)
            dates.extend(matches)
        
        if dates:
            exp['start_date'] = dates[0] if len(dates) > 0 else None
            if len(dates) > 1:
                if dates[1].lower() in ['present', 'current', 'now']:
                    exp['current'] = True
                    exp['end_date'] = 'Present'
                else:
                    exp['end_date'] = dates[1]
            elif exp['start_date'] and exp['start_date'].lower() not in ['present', 'current', 'now']:
                # Only one date found, might be current job
                if 'present' in entry.lower() or 'current' in entry.lower():
                    exp['current'] = True
                    exp['end_date'] = 'Present'
        
        # Extract title and company (heuristic: first two non-empty lines)
        lines = [l.strip() for l in entry.split('\n') if l.strip()]
        if len(lines) >= 1:
            exp['title'] = lines[0]
        if len(lines) >= 2:
            # Second line is usually company | dates
            exp['company'] = lines[1]
        
        # Extract bullet points as description
        bullet_lines = [l for l in lines if l.startswith(('•', '-', '*', '◦'))]
        if bullet_lines:
            exp['description'] = [l.lstrip('•-*◦ ').strip() for l in bullet_lines]
        
        return exp
    
    def _parse_skills(self, text: str) -> List[str]:
        """Parse skills section."""
        skills = []
        
        # Split by common delimiters
        text_normalized = text.replace('\n', ',')
        text_normalized = re.sub(r'\s*[,;|•·]\s*', ',', text_normalized)
        
        # Split and clean
        for skill in text_normalized.split(','):
            skill_clean = skill.strip()
            if skill_clean and len(skill_clean) > 1 and len(skill_clean) < 50:
                # Remove common prefixes
                skill_clean = re.sub(r'^(?:proficient in|experienced with|knowledge of)\s+', '', skill_clean, flags=re.IGNORECASE)
                skills.append(skill_clean)
        
        return skills
    
    def _parse_projects(self, text: str) -> List[Dict[str, Any]]:
        """Parse projects section."""
        project_entries = []
        
        # Split by double newlines or project name patterns
        lines = text.split('\n')
        current_project = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_project:
                    project = self._parse_single_project('\n'.join(current_project))
                    if project:
                        project_entries.append(project)
                    current_project = []
                continue
            
            # Check if this looks like a new project title
            # Must: not be a bullet point, reasonable length, not a description line
            is_bullet = line.startswith(('•', '-', '*', '◦'))
            looks_like_description = line.lower().startswith(('implemented', 'built', 'developed', 'created', 'designed', 'achieved', 'personal', 'team', 'solo'))
            has_tech_mention = re.search(r'\b(?:using|with|technologies?:|built with)\b', line, re.IGNORECASE)
            
            if (not is_bullet and 
                not looks_like_description and
                not has_tech_mention and
                5 < len(line) < 100 and
                current_project):
                # Likely new project
                project = self._parse_single_project('\n'.join(current_project))
                if project:
                    project_entries.append(project)
                current_project = [line]
            else:
                current_project.append(line)
        
        # Process last project
        if current_project:
            project = self._parse_single_project('\n'.join(current_project))
            if project:
                project_entries.append(project)
        
        return project_entries
    
    def _parse_single_project(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse a single project entry."""
        if not entry.strip():
            return None
        
        project = {
            'raw_text': entry.strip(),
            'name': None,
            'description': None,
            'technologies': []
        }
        
        # First line is usually project name
        lines = [l.strip() for l in entry.split('\n') if l.strip()]
        if lines:
            project['name'] = lines[0]
            if len(lines) > 1:
                project['description'] = ' '.join(lines[1:])
        
        # Extract technologies (heuristic: words after "using", "with", "technologies:", etc.)
        tech_patterns = [
            r'technologies?:\s+(.+)',
            r'(?:using|with)\s+(.+?)(?:\n|$)',
            r'built\s+(?:with|using)\s+(.+)',
            r'stack:\s+(.+)'
        ]
        
        for pattern in tech_patterns:
            tech_match = re.search(pattern, entry, re.IGNORECASE | re.MULTILINE)
            if tech_match:
                tech_text = tech_match.group(1)
                # Split by common separators
                techs = re.split(r'[,;]|\s+and\s+', tech_text)
                # Clean up and filter
                cleaned_techs = []
                for t in techs:
                    t = t.strip()
                    # Remove leading bullet points or extra text
                    t = re.sub(r'^[•\-\*◦]\s*', '', t)
                    # Take only the tech names (before any punctuation or new sentence)
                    t = re.split(r'[.!?\n]', t)[0].strip()
                    if t and len(t) > 1 and len(t) < 50:
                        cleaned_techs.append(t)
                
                if cleaned_techs:
                    project['technologies'] = cleaned_techs
                    break
        
        return project
    
    def _parse_certifications(self, text: str) -> List[Dict[str, Any]]:
        """Parse certifications section."""
        cert_entries = []
        
        # Split by newlines (each cert typically on one line)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        for line in lines:
            cert = {
                'raw_text': line,
                'name': line,
                'issuer': None,
                'year': None
            }
            
            # Extract year
            years = re.findall(r'\b(19|20)\d{2}\b', line)
            if years:
                cert['year'] = int(years[-1])
            
            # Extract issuer (text after '-' or 'by')
            issuer_match = re.search(r'(?:-|by)\s+(.+?)(?:\s+\d{4}|$)', line, re.IGNORECASE)
            if issuer_match:
                cert['issuer'] = issuer_match.group(1).strip()
                cert['name'] = line.split('-')[0].strip() if '-' in line else line.split('by')[0].strip()
            
            cert_entries.append(cert)
        
        return cert_entries
    
    def _calculate_confidence(self, resume: ParsedResume) -> float:
        """Calculate confidence score for the parse."""
        score = 0.0
        
        # Contact info found
        if resume.email:
            score += 0.2
        if resume.phone:
            score += 0.1
        
        # Key sections found
        if resume.education:
            score += 0.2
        if resume.experience:
            score += 0.2
        if resume.skills:
            score += 0.15
        
        # Additional sections
        if resume.projects:
            score += 0.075
        if resume.certifications:
            score += 0.075
        
        return min(score, 1.0)
