"""
Resume Scoring Service with Statistical Fallback

Provides resume analysis and scoring without requiring AI.
AI enhancement is optional for richer insights.
"""

import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
import asyncio


class ResumeScorer:
    """Statistical resume scoring engine - works offline without AI."""
    
    # Industry keywords for keyword matching
    TECH_KEYWORDS = {
        'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'swift', 'kotlin'],
        'web': ['html', 'css', 'react', 'angular', 'vue', 'node', 'django', 'flask', 'express', 'next.js', 'frontend', 'backend'],
        'database': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'cassandra', 'elasticsearch', 'database'],
        'cloud': ['aws', 'azure', 'gcp', 'kubernetes', 'docker', 'terraform', 'jenkins', 'ci/cd', 'devops'],
        'data': ['data analysis', 'machine learning', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'sql'],
        'soft_skills': ['leadership', 'communication', 'team', 'collaboration', 'problem solving', 'analytical', 'creative']
    }
    
    ACTION_VERBS = [
        'led', 'managed', 'developed', 'designed', 'implemented', 'created', 'built',
        'improved', 'increased', 'reduced', 'achieved', 'delivered', 'launched',
        'optimized', 'established', 'coordinated', 'executed', 'drove', 'spearheaded'
    ]
    
    def score_resume(self, extracted_data: Dict[str, Any], resume_text: str = "") -> Dict[str, Any]:
        """
        Score resume comprehensively using statistical methods.
        Returns detailed score breakdown and suggestions.
        """
        scores = {}
        
        # 1. Completeness Score (20%)
        scores['completeness'] = self._score_completeness(extracted_data)
        
        # 2. Experience Score (25%)
        scores['experience'] = self._score_experience(extracted_data.get('experience', []))
        
        # 3. Education Score (15%)
        scores['education'] = self._score_education(extracted_data.get('education', []))
        
        # 4. Skills Score (20%)
        scores['skills'] = self._score_skills(extracted_data.get('skills', {}), resume_text)
        
        # 5. Formatting & Presentation (10%)
        scores['formatting'] = self._score_formatting(resume_text, extracted_data)
        
        # 6. Keyword Optimization (10%)
        scores['keywords'] = self._score_keywords(resume_text)
        
        # Calculate overall score
        weights = {
            'completeness': 0.20,
            'experience': 0.25,
            'education': 0.15,
            'skills': 0.20,
            'formatting': 0.10,
            'keywords': 0.10
        }
        
        overall_score = sum(scores[key] * weights[key] for key in scores)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(scores, extracted_data)
        
        # Identify strengths
        strengths = self._identify_strengths(scores, extracted_data)
        
        # Calculate missing elements
        missing_elements = self._find_missing_elements(extracted_data)
        role_fit = self._score_role_fit(resume_text, extracted_data)
        
        return {
            'overall_score': round(overall_score, 1),
            'score_grade': self._get_grade(overall_score),
            'category_scores': {k: round(v, 1) for k, v in scores.items()},
            'suggestions': suggestions,
            'strengths': strengths,
            'missing_elements': missing_elements,
            'role_fit': role_fit,
            'ats_friendly': self._check_ats_friendly(resume_text, extracted_data),
            'estimated_pass_rate': self._estimate_pass_rate(overall_score)
        }
    
    def _score_completeness(self, data: Dict[str, Any]) -> float:
        """Score based on presence of essential sections."""
        sections = {
            'contact_info': data.get('contact_info', {}),
            'summary': data.get('summary', ''),
            'experience': data.get('experience', []),
            'education': data.get('education', []),
            'skills': data.get('skills', {})
        }
        
        score = 0.0
        weights = {'contact_info': 0.25, 'summary': 0.15, 'experience': 0.30, 'education': 0.20, 'skills': 0.10}
        
        # Contact info
        contact = sections['contact_info']
        if contact:
            contact_score = 0
            if contact.get('name'): contact_score += 0.3
            if contact.get('email'): contact_score += 0.3
            if contact.get('phone'): contact_score += 0.2
            if contact.get('location'): contact_score += 0.1
            if contact.get('linkedin') or contact.get('github'): contact_score += 0.1
            score += contact_score * weights['contact_info'] * 100
        
        # Summary
        if sections['summary'] and len(sections['summary']) > 50:
            score += weights['summary'] * 100
        
        # Experience
        if len(sections['experience']) > 0:
            score += weights['experience'] * 100
        
        # Education
        if len(sections['education']) > 0:
            score += weights['education'] * 100
        
        # Skills
        if sections['skills'] and any(sections['skills'].values()):
            score += weights['skills'] * 100
        
        return min(score, 100.0)
    
    def _score_experience(self, experiences: List[Dict[str, Any]]) -> float:
        """Score work experience quality."""
        if not experiences:
            return 30.0  # Minimum score for entry-level
        
        score = 0.0
        
        for exp in experiences:
            exp_score = 0
            
            # Duration (longer is better, up to 5 years per role)
            duration_months = self._calculate_duration(exp.get('start_date'), exp.get('end_date'))
            duration_score = min(duration_months / 60, 1.0) * 20  # Max 20 points
            exp_score += duration_score
            
            # Achievements (3-5 bullets is ideal)
            achievements = exp.get('achievements', [])
            if achievements:
                achievement_score = min(len(achievements) / 5, 1.0) * 30  # Max 30 points
                exp_score += achievement_score
                
                # Quantification (numbers in achievements)
                quantified_count = sum(1 for ach in achievements if self._has_quantification(ach))
                if quantified_count > 0:
                    quantification_score = (quantified_count / len(achievements)) * 30  # Max 30 points
                    exp_score += quantification_score
            
            # Action verbs
            description = exp.get('description', '') + ' ' + ' '.join(achievements)
            if self._contains_action_verbs(description):
                exp_score += 20  # Max 20 points
            
            score += exp_score
        
        # Average score across all experiences
        avg_score = score / len(experiences)
        return min(avg_score, 100.0)
    
    def _score_education(self, education: List[Dict[str, Any]]) -> float:
        """Score education background."""
        if not education:
            return 50.0  # Neutral score if no formal education
        
        score = 60.0  # Base score for having education
        
        for edu in education:
            # Degree level
            degree = (edu.get('degree', '') or '').lower()
            if 'phd' in degree or 'doctorate' in degree:
                score += 20
            elif 'master' in degree or 'msc' in degree or 'mba' in degree:
                score += 15
            elif 'bachelor' in degree or 'bsc' in degree or 'bs' in degree:
                score += 10
            else:
                score += 5
            
            # GPA mentioned (shows achievement)
            if edu.get('gpa'):
                try:
                    gpa_text = str(edu['gpa'])
                    gpa_parts = re.split(r"\s*/\s*", gpa_text)
                    gpa = float(gpa_parts[0])
                    scale = float(gpa_parts[1]) if len(gpa_parts) > 1 else 4.0
                    normalized_gpa = (gpa / scale) * 4 if scale else 0
                    if normalized_gpa >= 3.5:
                        score += 10
                    elif normalized_gpa >= 3.0:
                        score += 5
                except:
                    pass
        
        return min(score, 100.0)
    
    def _score_skills(self, skills: Dict[str, List[str]], resume_text: str) -> float:
        """Score skills comprehensiveness and relevance."""
        score = 0.0
        
        # Extract all skills into one list
        all_skills = []
        for skill_type, skill_list in skills.items():
            if isinstance(skill_list, list):
                all_skills.extend(skill_list)
        
        if not all_skills:
            return 40.0  # Low score if no skills listed
        
        # Quantity (10-20 skills is good)
        quantity_score = min(len(all_skills) / 20, 1.0) * 30
        score += quantity_score
        
        # Category diversity
        categories_present = sum(1 for v in skills.values() if v)
        diversity_score = (categories_present / max(len(skills), 1)) * 20
        score += diversity_score
        
        # Technical depth (specific technologies)
        tech_skills = skills.get('technical', [])
        if len(tech_skills) >= 5:
            score += 30
        elif len(tech_skills) >= 3:
            score += 20
        elif len(tech_skills) >= 1:
            score += 10
        
        # Soft skills mentioned
        soft_skills = skills.get('soft', [])
        if len(soft_skills) >= 3:
            score += 20
        elif len(soft_skills) >= 1:
            score += 10
        
        return min(score, 100.0)
    
    def _score_formatting(self, resume_text: str, data: Dict[str, Any]) -> float:
        """Score formatting and presentation quality."""
        score = 70.0  # Base score
        
        # Length (1-2 pages is ideal)
        word_count = len(resume_text.split())
        if 400 <= word_count <= 1000:
            score += 15  # Optimal length
        elif 300 <= word_count < 400 or 1000 < word_count <= 1200:
            score += 10  # Acceptable length
        elif word_count < 300:
            score -= 20  # Too short
        elif word_count > 1500:
            score -= 10  # Too long
        
        # Bullet points usage (good for ATS)
        bullet_count = resume_text.count('•') + resume_text.count('-') + resume_text.count('*')
        if bullet_count >= 5:
            score += 10
        
        # Consistent date formatting
        dates_found = re.findall(r'\d{4}', resume_text)
        if len(dates_found) >= 2:
            score += 5
        
        return min(score, 100.0)
    
    def _score_keywords(self, resume_text: str) -> float:
        """Score industry keyword optimization."""
        text_lower = resume_text.lower()
        score = 0.0
        
        keyword_matches = 0
        total_keywords = 0
        
        for category, keywords in self.TECH_KEYWORDS.items():
            total_keywords += len(keywords)
            for keyword in keywords:
                if keyword in text_lower:
                    keyword_matches += 1
        
        # Calculate percentage of keywords present
        if total_keywords > 0:
            keyword_coverage = (keyword_matches / total_keywords) * 100
            score = min(keyword_coverage * 2, 100.0)  # Scale up
        
        return score
    
    def _generate_suggestions(self, scores: Dict[str, float], data: Dict[str, Any]) -> List[str]:
        """Generate actionable suggestions based on scores."""
        suggestions = []
        
        if scores['completeness'] < 80:
            missing = self._find_missing_elements(data)
            if missing:
                suggestions.append(f"Add missing sections: {', '.join(missing)}")
        
        if scores['experience'] < 70:
            suggestions.append("Quantify your achievements with numbers and metrics (e.g., 'Increased sales by 25%')")
            suggestions.append("Use strong action verbs to start each bullet point")
            suggestions.append("Add 3-5 bullet points per role highlighting key accomplishments")
        
        if scores['education'] < 60:
            suggestions.append("Include your education details with degree, institution, and graduation date")
        
        if scores['skills'] < 70:
            suggestions.append("Add more relevant technical skills specific to your target role")
            suggestions.append("Include both hard skills (technologies) and soft skills (communication, leadership)")
        
        if scores['formatting'] < 75:
            suggestions.append("Keep resume length to 1-2 pages (400-1000 words)")
            suggestions.append("Use bullet points for better readability")
        
        if scores['keywords'] < 60:
            suggestions.append("Include more industry-specific keywords relevant to your target role")
            suggestions.append("Research job descriptions and incorporate key terms naturally")
        
        # Limit to top 5 suggestions
        return suggestions[:5]
    
    def _identify_strengths(self, scores: Dict[str, float], data: Dict[str, Any]) -> List[str]:
        """Identify resume strengths."""
        strengths = []
        
        if scores['experience'] >= 80:
            exp_count = len(data.get('experience', []))
            strengths.append(f"Strong work experience with {exp_count} relevant role(s)")
        
        if scores['education'] >= 85:
            strengths.append("Impressive educational background")
        
        if scores['skills'] >= 80:
            skill_count = sum(len(v) for v in data.get('skills', {}).values() if isinstance(v, list))
            strengths.append(f"Comprehensive skill set ({skill_count} skills listed)")
        
        if scores['completeness'] >= 90:
            strengths.append("Well-structured resume with all essential sections")
        
        if scores['keywords'] >= 75:
            strengths.append("Good keyword optimization for ATS systems")
        
        return strengths if strengths else ["Resume shows potential with room for improvement"]
    
    def _find_missing_elements(self, data: Dict[str, Any]) -> List[str]:
        """Find missing resume elements."""
        missing = []
        
        if not data.get('contact_info', {}).get('email'):
            missing.append('email address')
        
        if not data.get('summary'):
            missing.append('professional summary')
        
        if not data.get('experience') or len(data.get('experience', [])) == 0:
            missing.append('work experience')
        
        if not data.get('skills') or not any(data.get('skills', {}).values()):
            missing.append('skills section')

        if not data.get('projects'):
            missing.append('project portfolio')

        skills = data.get('skills') or {}
        if not skills.get('soft'):
            missing.append('explicit soft skills')
        
        return missing

    def _score_role_fit(self, resume_text: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare resume evidence with common entry-level technology role skills."""
        profiles = {
            "Software Engineer": ["programming", "algorithms", "testing", "git", "api design", "database", "communication"],
            "Full-Stack Developer": ["javascript", "react", "html", "css", "api design", "database", "backend"],
            "Frontend Engineer": ["javascript", "react", "html", "css", "design", "testing", "communication"],
            "AI/ML Engineer": ["python", "machine learning", "computer vision", "statistics", "api design", "testing", "cloud"],
            "Data Engineer": ["python", "database", "data pipeline", "cloud", "automation", "testing", "linux"],
            "Cybersecurity Analyst": ["networking", "security", "incident response", "linux", "python", "communication", "critical thinking"],
        }
        evidence = (resume_text or "").lower()
        evidence += " " + " ".join(
            str(skill).lower()
            for group in (data.get("skills") or {}).values()
            if isinstance(group, list)
            for skill in group
        )
        from app.services.career_signals import extract_skill_evidence
        evidenced_skills = {skill.lower() for skill in extract_skill_evidence(evidence)}
        results = []
        for role, requirements in profiles.items():
            matched = [skill for skill in requirements if skill in evidenced_skills or skill in evidence]
            missing = [skill for skill in requirements if skill not in evidenced_skills and skill not in evidence]
            results.append({
                "role": role,
                "score": round(100 * len(matched) / len(requirements)),
                "matched_skills": matched,
                "priority_gaps": missing[:4],
                "assessment": (
                    f"Strong evidence for {len(matched)} of {len(requirements)} core requirements."
                    if matched else "Add role-specific skills and evidence before targeting this role."
                ),
            })
        return sorted(results, key=lambda item: item["score"], reverse=True)
    
    def _check_ats_friendly(self, resume_text: str, data: Dict[str, Any]) -> bool:
        """Check if resume is ATS-friendly."""
        # Simple heuristics
        has_standard_sections = all([
            data.get('experience'),
            data.get('education'),
            data.get('skills')
        ])
        
        # Check for excessive formatting characters
        special_chars = sum(resume_text.count(c) for c in ['│', '┃', '║', '▪', '▫'])
        minimal_special_formatting = special_chars < 10
        
        return has_standard_sections and minimal_special_formatting
    
    def _estimate_pass_rate(self, overall_score: float) -> str:
        """Estimate ATS pass rate based on score."""
        if overall_score >= 85:
            return "High (80-95%)"
        elif overall_score >= 70:
            return "Good (60-80%)"
        elif overall_score >= 55:
            return "Moderate (40-60%)"
        else:
            return "Low (20-40%)"
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    # Helper methods
    
    def _calculate_duration(self, start_date: str, end_date: str) -> int:
        """Calculate duration in months between two dates."""
        try:
            start = self._parse_date(start_date)
            end = self._parse_date(end_date) if end_date and 'present' not in end_date.lower() else datetime.now()
            
            months = (end.year - start.year) * 12 + (end.month - start.month)
            return max(months, 1)
        except:
            return 12  # Default to 1 year if parsing fails
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in various formats."""
        if not date_str:
            return datetime.now()
        
        # Try common formats
        formats = ['%Y-%m', '%Y', '%m/%Y', '%Y/%m']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # Extract year if all else fails
        year_match = re.search(r'20\d{2}', date_str)
        if year_match:
            return datetime(int(year_match.group()), 1, 1)
        
        return datetime.now()
    
    def _has_quantification(self, text: str) -> bool:
        """Check if text contains quantifiable metrics."""
        # Look for numbers, percentages, dollar amounts
        patterns = [r'\d+%', r'\$\d+', r'\d+\+', r'\d+x', r'\d+ (?:million|thousand|hundred)']
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    def _contains_action_verbs(self, text: str) -> bool:
        """Check if text contains strong action verbs."""
        text_lower = text.lower()
        return any(verb in text_lower for verb in self.ACTION_VERBS)


# Singleton instance
resume_scorer = ResumeScorer()
