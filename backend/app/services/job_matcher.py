"""
Statistical Job Matching Service

Provides career recommendations without requiring AI.
Uses skill matching, profile analysis, and market data.
"""

from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict
import re


class JobMatcher:
    """Statistical job matching engine - works offline without AI."""
    
    # Comprehensive job database with realistic salaries (October 2026)
    JOB_DATABASE = [
        {
            "role_name": "Software Engineer",
            "category": "Technology",
            "description": "Design, develop, and maintain software applications",
            "required_skills": ["programming", "algorithms", "data structures", "git", "testing"],
            "preferred_skills": ["python", "java", "javascript", "react", "sql", "docker", "aws"],
            "education_level": ["bachelor", "master"],
            "experience_years": 0,
            "salary_min": 75000,
            "salary_max": 150000,
            "growth_rate": "15%",
            "demand": "very_high",
            "industry_trend": "Rapidly growing with AI/ML integration and cloud-native development"
        },
        {
            "role_name": "Full-Stack Developer",
            "category": "Technology",
            "description": "Build complete web applications from frontend to backend",
            "required_skills": ["html", "css", "javascript", "backend", "database"],
            "preferred_skills": ["react", "node", "express", "mongodb", "postgresql", "rest api"],
            "education_level": ["bachelor", "bootcamp"],
            "experience_years": 0,
            "salary_min": 70000,
            "salary_max": 140000,
            "growth_rate": "12%",
            "demand": "very_high",
            "industry_trend": "High demand for versatile developers who can handle entire stack"
        },
        {
            "role_name": "Data Scientist",
            "category": "Technology",
            "description": "Analyze complex data and build predictive models",
            "required_skills": ["python", "statistics", "machine learning", "data analysis"],
            "preferred_skills": ["pandas", "numpy", "scikit-learn", "tensorflow", "sql", "visualization"],
            "education_level": ["bachelor", "master", "phd"],
            "experience_years": 0,
            "salary_min": 85000,
            "salary_max": 170000,
            "growth_rate": "20%",
            "demand": "very_high",
            "industry_trend": "Explosive growth with AI/ML revolution, companies investing heavily in data capabilities"
        },
        {
            "role_name": "Cloud Engineer",
            "category": "Technology",
            "description": "Design and manage cloud infrastructure and services",
            "required_skills": ["cloud", "networking", "security", "automation"],
            "preferred_skills": ["aws", "azure", "gcp", "kubernetes", "docker", "terraform", "jenkins"],
            "education_level": ["bachelor", "associate"],
            "experience_years": 1,
            "salary_min": 80000,
            "salary_max": 160000,
            "growth_rate": "18%",
            "demand": "very_high",
            "industry_trend": "Critical role as companies migrate to cloud, shortage of skilled professionals"
        },
        {
            "role_name": "Cybersecurity Analyst",
            "category": "Technology",
            "description": "Protect systems and data from cyber threats",
            "required_skills": ["security", "networking", "risk assessment", "incident response"],
            "preferred_skills": ["penetration testing", "siem", "firewall", "encryption", "compliance"],
            "education_level": ["bachelor", "associate", "certifications"],
            "experience_years": 0,
            "salary_min": 75000,
            "salary_max": 145000,
            "growth_rate": "22%",
            "demand": "very_high",
            "industry_trend": "Massive demand due to increasing cyber threats, talent shortage"
        },
        {
            "role_name": "DevOps Engineer",
            "category": "Technology",
            "description": "Automate and streamline software development and deployment",
            "required_skills": ["ci/cd", "automation", "linux", "scripting"],
            "preferred_skills": ["jenkins", "docker", "kubernetes", "ansible", "terraform", "git"],
            "education_level": ["bachelor", "associate"],
            "experience_years": 1,
            "salary_min": 80000,
            "salary_max": 155000,
            "growth_rate": "17%",
            "demand": "very_high",
            "industry_trend": "Essential for modern software development, high demand for automation experts"
        },
        {
            "role_name": "Machine Learning Engineer",
            "category": "Technology",
            "description": "Build and deploy AI/ML models at scale",
            "required_skills": ["machine learning", "python", "algorithms", "mathematics"],
            "preferred_skills": ["tensorflow", "pytorch", "scikit-learn", "mlops", "cloud", "docker"],
            "education_level": ["bachelor", "master", "phd"],
            "experience_years": 1,
            "salary_min": 95000,
            "salary_max": 180000,
            "growth_rate": "25%",
            "demand": "extremely_high",
            "industry_trend": "AI revolution creating unprecedented demand, top-paying tech role"
        },
        {
            "role_name": "Frontend Developer",
            "category": "Technology",
            "description": "Create user interfaces and experiences for web applications",
            "required_skills": ["html", "css", "javascript", "responsive design"],
            "preferred_skills": ["react", "vue", "angular", "typescript", "sass", "webpack"],
            "education_level": ["bachelor", "bootcamp", "self-taught"],
            "experience_years": 0,
            "salary_min": 65000,
            "salary_max": 130000,
            "growth_rate": "10%",
            "demand": "high",
            "industry_trend": "Steady demand, focus shifting to React and modern frameworks"
        },
        {
            "role_name": "Backend Developer",
            "category": "Technology",
            "description": "Build server-side logic and database systems",
            "required_skills": ["backend", "database", "api design", "programming"],
            "preferred_skills": ["python", "java", "node", "sql", "nosql", "rest", "graphql"],
            "education_level": ["bachelor", "associate"],
            "experience_years": 0,
            "salary_min": 70000,
            "salary_max": 140000,
            "growth_rate": "13%",
            "demand": "very_high",
            "industry_trend": "Strong demand for scalable backend systems and microservices"
        },
        {
            "role_name": "Product Manager",
            "category": "Business",
            "description": "Lead product strategy and development",
            "required_skills": ["product strategy", "communication", "analytical thinking", "leadership"],
            "preferred_skills": ["agile", "user research", "data analysis", "technical background"],
            "education_level": ["bachelor", "master", "mba"],
            "experience_years": 2,
            "salary_min": 90000,
            "salary_max": 170000,
            "growth_rate": "14%",
            "demand": "high",
            "industry_trend": "Growing need for product leaders who understand both business and technology"
        },
        {
            "role_name": "UX/UI Designer",
            "category": "Design",
            "description": "Design user experiences and interfaces for digital products",
            "required_skills": ["user research", "wireframing", "prototyping", "visual design"],
            "preferred_skills": ["figma", "sketch", "adobe xd", "user testing", "accessibility"],
            "education_level": ["bachelor", "associate", "bootcamp"],
            "experience_years": 0,
            "salary_min": 65000,
            "salary_max": 130000,
            "growth_rate": "11%",
            "demand": "high",
            "industry_trend": "Important role as companies prioritize user experience"
        },
        {
            "role_name": "Data Engineer",
            "category": "Technology",
            "description": "Build and maintain data pipelines and infrastructure",
            "required_skills": ["etl", "data pipeline", "sql", "programming"],
            "preferred_skills": ["spark", "airflow", "kafka", "python", "aws", "big data"],
            "education_level": ["bachelor", "master"],
            "experience_years": 1,
            "salary_min": 85000,
            "salary_max": 165000,
            "growth_rate": "19%",
            "demand": "very_high",
            "industry_trend": "Critical for data-driven companies, high demand with talent shortage"
        }
    ]
    
    def match_jobs(
        self,
        profile: Dict[str, Any],
        skills: List[str],
        education: List[Dict[str, Any]],
        experience: List[Dict[str, Any]],
        preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Match user profile to jobs using statistical methods.
        Returns ranked list of job recommendations.
        """
        preferences = preferences or {}
        matches = []
        
        # Normalize skills
        user_skills = set(s.lower().strip() for s in skills if s)
        from app.services.career_signals import extract_skill_evidence
        user_skills.update(skill.lower() for skill in extract_skill_evidence(" ".join(skills or []), skills))
        
        # Calculate experience years
        total_experience_years = self._calculate_total_experience(experience)
        
        # Get education level
        education_level = self._get_education_level(education)
        
        for job in self.JOB_DATABASE:
            score, details = self._calculate_match_score(
                job,
                user_skills,
                education_level,
                total_experience_years,
                preferences
            )
            
            # Keep the best-fit roles even when the profile has sparse data.
            # The offline recommender must still return useful starting points
            # when no LLM is configured or the student is early in discovery.
            match = {
                "role_name": job["role_name"],
                "category": job["category"],
                "description": job["description"],
                "fit_score": round(score, 2),
                "match_percentage": round(score * 100),
                "salary_range_min": job["salary_min"],
                "salary_range_max": job["salary_max"],
                "salary_currency": "USD",
                "salary_period": "annual",
                "growth_rate": job["growth_rate"],
                "market_demand": job["demand"],
                "industry_trend": job["industry_trend"],
                "matched_skills": details["matched_skills"],
                "missing_skills": details["missing_skills"],
                "strengths": details["strengths"],
                "gaps": details["gaps"],
                "opportunities": details["opportunities"],
                "threats": details["threats"],
                "reasoning": self._generate_reasoning(job, score, details)
            }
            matches.append(match)
        
        # Sort by score descending
        matches.sort(key=lambda x: x["fit_score"], reverse=True)
        
        # Return top 8 matches
        return matches[:8]
    
    def _calculate_match_score(
        self,
        job: Dict[str, Any],
        user_skills: Set[str],
        education_level: str,
        experience_years: float,
        preferences: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Calculate match score between user and job."""
        score = 0.0
        details = {
            "matched_skills": [],
            "missing_skills": [],
            "strengths": [],
            "gaps": [],
            "opportunities": [],
            "threats": []
        }
        
        # 1. Skills Match (40% weight)
        required_skills = set(s.lower() for s in job["required_skills"])
        preferred_skills = set(s.lower() for s in job["preferred_skills"])
        
        # Check required skills
        matched_required = user_skills & required_skills
        skill_match_required = len(matched_required) / len(required_skills) if required_skills else 0
        
        # Check preferred skills
        matched_preferred = user_skills & preferred_skills
        skill_match_preferred = len(matched_preferred) / len(preferred_skills) if preferred_skills else 0
        
        # Combined skill score
        skill_score = (skill_match_required * 0.7 + skill_match_preferred * 0.3)
        score += skill_score * 0.4
        
        # Track matched and missing skills
        details["matched_skills"] = list(matched_required | matched_preferred)
        details["missing_skills"] = list((required_skills | preferred_skills) - user_skills)[:5]
        
        # 2. Education Match (25% weight)
        education_score = 0.0
        if education_level in job["education_level"]:
            education_score = 1.0
        elif education_level == "master" and "bachelor" in job["education_level"]:
            education_score = 1.0  # Master's satisfies bachelor's requirement
        elif education_level == "phd" and ("master" in job["education_level"] or "bachelor" in job["education_level"]):
            education_score = 1.0
        elif education_level == "bachelor" and "associate" in job["education_level"]:
            education_score = 0.9
        else:
            education_score = 0.5  # Partial credit
        
        score += education_score * 0.25
        
        # 3. Experience Match (20% weight)
        required_experience = job["experience_years"]
        if experience_years >= required_experience:
            experience_score = 1.0
        elif experience_years >= required_experience * 0.5:
            experience_score = 0.7
        else:
            experience_score = 0.4  # Entry-level credit
        
        score += experience_score * 0.20
        
        # 4. Market Demand Bonus (10% weight)
        demand_map = {"extremely_high": 1.0, "very_high": 0.9, "high": 0.7, "moderate": 0.5}
        demand_score = demand_map.get(job["demand"], 0.5)
        score += demand_score * 0.10
        
        # 5. Preference Match (5% weight)
        preference_score = 0.5  # Default
        if preferences.get("preferred_category") == job["category"]:
            preference_score = 1.0
        score += preference_score * 0.05

        role_name = job["role_name"].lower()
        if any(
            preferred_role in role_name or role_name in preferred_role
            for preferred_role in preferences.get("preferred_roles", [])
        ):
            score += 0.15
        
        # Generate SWOT analysis
        details["strengths"] = self._identify_strengths(job, user_skills, education_level, experience_years)
        details["gaps"] = self._identify_gaps(job, user_skills, education_level, experience_years)
        details["opportunities"] = self._identify_opportunities(job)
        details["threats"] = self._identify_threats(job)
        
        return min(score, 1.0), details
    
    def _calculate_total_experience(self, experience: List[Dict[str, Any]]) -> float:
        """Calculate total years of relevant experience."""
        if not experience:
            return 0.0
        
        total_months = 0
        for exp in experience:
            start = exp.get("start_date", "")
            end = exp.get("end_date", "Present")
            
            # Extract years
            start_year = self._extract_year(start)
            end_year = self._extract_year(end) if end != "Present" else 2026
            
            if start_year and end_year:
                months = (end_year - start_year) * 12
                total_months += months
        
        return total_months / 12.0
    
    def _extract_year(self, date_str: str) -> int:
        """Extract year from date string."""
        match = re.search(r'20\d{2}', str(date_str))
        return int(match.group()) if match else None
    
    def _get_education_level(self, education: List[Dict[str, Any]]) -> str:
        """Determine highest education level."""
        if not education:
            return "none"
        
        levels = []
        for edu in education:
            degree = (edu.get("degree", "") or "").lower()
            if "phd" in degree or "doctorate" in degree:
                levels.append(("phd", 4))
            elif "master" in degree or "msc" in degree or "mba" in degree:
                levels.append(("master", 3))
            elif "bachelor" in degree or "bsc" in degree or "bs" in degree or "ba" in degree:
                levels.append(("bachelor", 2))
            elif "associate" in degree:
                levels.append(("associate", 1))
        
        if not levels:
            return "bachelor"  # Assume bachelor's if degree type unclear
        
        # Return highest level
        levels.sort(key=lambda x: x[1], reverse=True)
        return levels[0][0]
    
    def _identify_strengths(self, job: Dict, skills: Set[str], edu: str, exp: float) -> List[str]:
        """Identify candidate strengths for this role."""
        strengths = []
        
        required = set(s.lower() for s in job["required_skills"])
        matched = skills & required
        
        if len(matched) >= len(required) * 0.8:
            strengths.append(f"Strong technical match with {len(matched)} relevant skills")
        
        if edu in ["master", "phd"] and "bachelor" in job["education_level"]:
            strengths.append("Advanced education provides competitive advantage")
        
        if exp >= job["experience_years"] + 1:
            strengths.append("Experience exceeds minimum requirements")
        
        if job["demand"] in ["very_high", "extremely_high"]:
            strengths.append("High market demand for this role")
        
        return strengths if strengths else ["Foundation skills present for entry into this field"]
    
    def _identify_gaps(self, job: Dict, skills: Set[str], edu: str, exp: float) -> List[str]:
        """Identify skill gaps and areas for improvement."""
        gaps = []
        
        required = set(s.lower() for s in job["required_skills"])
        missing_required = required - skills
        
        if missing_required:
            gaps.append(f"Develop: {', '.join(list(missing_required)[:3])}")
        
        if exp < job["experience_years"]:
            years_needed = job["experience_years"] - exp
            gaps.append(f"Gain {years_needed:.1f} more years of relevant experience")
        
        preferred = set(s.lower() for s in job["preferred_skills"])
        missing_preferred = (preferred - skills) - missing_required
        if len(missing_preferred) > 3:
            gaps.append(f"Learn preferred skills: {', '.join(list(missing_preferred)[:2])}")
        
        return gaps if gaps else ["Minor skill refinement needed"]
    
    def _identify_opportunities(self, job: Dict) -> List[str]:
        """Identify opportunities for this career path."""
        opportunities = []
        
        growth_rate = float(job["growth_rate"].rstrip('%'))
        if growth_rate >= 15:
            opportunities.append(f"Rapid industry growth ({job['growth_rate']} annually)")
        
        if job["demand"] in ["very_high", "extremely_high"]:
            opportunities.append("High demand with talent shortage - good leverage for candidates")
        
        if job["salary_max"] >= 150000:
            opportunities.append(f"High earning potential (up to ${job['salary_max']:,})")
        
        opportunities.append(f"{job['industry_trend']}")
        
        return opportunities
    
    def _identify_threats(self, job: Dict) -> List[str]:
        """Identify potential challenges or threats."""
        threats = []
        
        if job["category"] == "Technology":
            threats.append("Rapidly evolving field requires continuous learning")
        
        if job["experience_years"] > 0:
            threats.append("Competition from experienced candidates")
        
        # Add market-specific threats
        if "AI" in job["description"] or "ML" in job["description"]:
            threats.append("Highly specialized field with competitive entry")
        
        return threats if threats else ["Standard market competition"]
    
    def _generate_reasoning(self, job: Dict, score: float, details: Dict) -> str:
        """Generate human-readable reasoning for the match."""
        if score >= 0.8:
            return f"Excellent fit! You have {len(details['matched_skills'])} matching skills and strong qualifications for this high-growth role."
        elif score >= 0.6:
            return f"Good match. You possess key skills for this role. Focus on developing: {', '.join(details['missing_skills'][:2])}."
        elif score >= 0.4:
            return f"Promising opportunity with some skill development needed. Market demand is {job['demand']} with {job['growth_rate']} growth."
        else:
            return f"Entry-level opportunity. Requires building foundational skills in: {', '.join(details['missing_skills'][:3])}."


# Singleton instance
job_matcher = JobMatcher()
