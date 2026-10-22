"""
Orvena Project Launchpad: Opportunity Directory & Tracking Service

Curated, source-backed directory of genuine student competitions, hackathons,
research fellowships, student accelerators, and innovation grants.
All records contain verified official source links, clear eligibility criteria,
and explicit beneficiary distinctions (student, team, startup).
"""
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import date, datetime
from app.schemas.launchpad import OpportunityResponse


CURATED_OPPORTUNITIES: List[Dict[str, Any]] = [
    {
        "id": "e1111111-1111-1111-1111-111111111111",
        "title": "Microsoft Imagine Cup Global Student Competition",
        "provider": "Microsoft Corporation",
        "opportunity_type": "competition",
        "description": "Global technology and innovation challenge for students leveraging cloud services and AI to solve community and societal challenges.",
        "official_url": "https://imaginecup.microsoft.com/",
        "eligibility_requirements": [
            "Must be currently enrolled in an accredited higher education institution",
            "At least 16 years of age",
            "Teams of 1 to 4 eligible students",
            "Must use Microsoft Azure cloud or AI services in the core prototype"
        ],
        "beneficiary_type": "student_team",
        "geographic_scope": "Global",
        "domains": ["AI / Machine Learning", "Cloud & DevOps", "HealthTech & BioInformatics", "ClimateTech & IoT"],
        "required_project_stage": "prototype",
        "funding_amount_or_benefits": "Up to $100,000 USD grand prize + mentorship with Microsoft CEO",
        "is_monetary": True,
        "application_deadline": date(2027, 1, 15),
        "is_rolling": False,
        "application_instructions": "Register team on the official Microsoft Imagine Cup portal, submit a 3-minute video pitch, architecture diagram, and GitHub repository link.",
        "date_last_verified": date(2026, 10, 15),
        "status": "active",
        "is_verified": True,
        "source_notes": "Official annual student competition verified from imaginecup.microsoft.com."
    },
    {
        "id": "e2222222-2222-2222-2222-222222222222",
        "title": "Google Solution Challenge",
        "provider": "Google Developer Student Clubs",
        "opportunity_type": "competition",
        "description": "Annual contest inviting university students to develop solutions for one or more of the United Nations 17 Sustainable Development Goals using Google technologies.",
        "official_url": "https://developers.google.com/community/gdsc-solution-challenge",
        "eligibility_requirements": [
            "Must be a member of a Google Developer Student Club (GDSC) at an accredited college/university",
            "Teams of up to 4 university students",
            "Solution must incorporate at least one Google developer product or platform"
        ],
        "beneficiary_type": "student_team",
        "geographic_scope": "Global",
        "domains": ["ClimateTech & IoT", "AI / Machine Learning", "Full Stack Web", "Mobile & IoT"],
        "required_project_stage": "prototype",
        "funding_amount_or_benefits": "Top 3 teams receive $3,000 per team member + Google mentorship",
        "is_monetary": True,
        "application_deadline": date(2027, 3, 31),
        "is_rolling": False,
        "application_instructions": "Submit demo video, technical implementation walk-through, and working software link via the Google Developers Challenge submission page.",
        "date_last_verified": date(2026, 10, 10),
        "status": "active",
        "is_verified": True,
        "source_notes": "Verified from developers.google.com/community/gdsc-solution-challenge."
    },
    {
        "id": "e3333333-3333-3333-3333-333333333333",
        "title": "Google Summer of Code (GSoC)",
        "provider": "Google Open Source Programs Office",
        "opportunity_type": "research_fellowship",
        "description": "Global program focused on bringing new contributors into open source software organizations with stipends and professional 1-on-1 mentorship.",
        "official_url": "https://summerofcode.withgoogle.com/",
        "eligibility_requirements": [
            "At least 18 years of age at time of registration",
            "Must be eligible to work in country of residence",
            "Open to students and beginner open source contributors",
            "Must not be a resident of a US-embargoed nation"
        ],
        "beneficiary_type": "individual_student",
        "geographic_scope": "Global",
        "domains": ["Open Source", "Full Stack Web", "Distributed Systems", "AI / Machine Learning"],
        "required_project_stage": "idea",
        "funding_amount_or_benefits": "Stipend based on participant location ($1,500 - $6,000 USD) + 12-22 weeks mentorship",
        "is_monetary": True,
        "application_deadline": date(2027, 4, 10),
        "is_rolling": False,
        "application_instructions": "Select an accepted mentoring open source organization, submit a detailed project proposal, and make initial code contributions.",
        "date_last_verified": date(2026, 10, 1),
        "status": "upcoming",
        "is_verified": True,
        "source_notes": "Official Google Open Source program verified from summerofcode.withgoogle.com."
    },
    {
        "id": "e4444444-4444-4444-4444-444444444444",
        "title": "Major League Hacking (MLH) Global Fellowship",
        "provider": "Major League Hacking",
        "opportunity_type": "research_fellowship",
        "description": "12-week remote internship alternative where students contribute to critical open source software used by millions or build production Web3/AI applications.",
        "official_url": "https://fellowship.mlh.io/",
        "eligibility_requirements": [
            "At least 18 years old",
            "Proficient in at least one modern programming language (Python, JavaScript, Go, etc.)",
            "Able to commit 30-40 hrs/week (full-time) or 15-20 hrs/week (part-time)",
            "Strong communicative English proficiency"
        ],
        "beneficiary_type": "individual_student",
        "geographic_scope": "Global",
        "domains": ["Full Stack Web", "Open Source", "Cloud & DevOps", "AI / Machine Learning"],
        "required_project_stage": "any",
        "funding_amount_or_benefits": "Need-based educational stipend up to $5,000 USD + professional mentorship",
        "is_monetary": True,
        "application_deadline": None,
        "is_rolling": True,
        "application_instructions": "Complete online application with a GitHub code sample you authored, participate in a technical code review interview, and pass behavioural screening.",
        "date_last_verified": date(2026, 10, 18),
        "status": "active",
        "is_verified": True,
        "source_notes": "Verified rolling cohorts (Spring, Summer, Fall) from fellowship.mlh.io."
    },
    {
        "id": "e5555555-5555-5555-5555-555555555555",
        "title": "1517 Fund - Medici Project Student Grants",
        "provider": "1517 Fund",
        "opportunity_type": "grant",
        "description": "Micro-grants for young makers, student hackers, and researchers working on hard scientific or technical projects outside or alongside traditional coursework.",
        "official_url": "https://www.1517fund.com/medici-project",
        "eligibility_requirements": [
            "Must be under 25 years old",
            "Working on novel software, hardware, biotech, or scientific discovery",
            "Clear plan on how capital will accelerate a physical or software prototype",
            "No institutional affiliation required"
        ],
        "beneficiary_type": "individual_student",
        "geographic_scope": "Global",
        "domains": ["DeepTech", "Biotech / HealthTech", "Hardware & Robotics", "AI / Machine Learning"],
        "required_project_stage": "prototype",
        "funding_amount_or_benefits": "$1,000 grant (non-dilutive, zero equity taken)",
        "is_monetary": True,
        "application_deadline": None,
        "is_rolling": True,
        "application_instructions": "Submit a 2-page concise project description explaining the problem, the prototype evidence, and exact budget allocation.",
        "date_last_verified": date(2026, 9, 28),
        "status": "active",
        "is_verified": True,
        "source_notes": "Verified non-dilutive maker grants from 1517fund.com."
    },
    {
        "id": "e6666666-6666-6666-6666-666666666666",
        "title": "HackMIT Collegiate Hackathon",
        "provider": "Massachusetts Institute of Technology TechX",
        "opportunity_type": "hackathon",
        "description": "One of the premier annual undergraduate hackathons bringing together 1,000+ university student developers for 24 hours of technical innovation.",
        "official_url": "https://hackmit.org/",
        "eligibility_requirements": [
            "Enrolled undergraduate or graduate student at an accredited university",
            "Teams of up to 4 students",
            "Code must be written entirely during the event duration"
        ],
        "beneficiary_type": "student_team",
        "geographic_scope": "Global (Online & In-Person at MIT Cambridge)",
        "domains": ["Full Stack Web", "AI / Machine Learning", "Fintech", "ClimateTech & IoT"],
        "required_project_stage": "idea",
        "funding_amount_or_benefits": "Over $30,000 in categorical sponsor awards, hardware labs, and travel grants",
        "is_monetary": True,
        "application_deadline": date(2027, 7, 25),
        "is_rolling": False,
        "application_instructions": "Register individual/team profile, answer prompt essays, and link portfolio or GitHub profile.",
        "date_last_verified": date(2026, 10, 5),
        "status": "upcoming",
        "is_verified": True,
        "source_notes": "Verified from hackmit.org official site."
    },
    {
        "id": "e7777777-7777-7777-7777-777777777777",
        "title": "CERN Summer Student Programme",
        "provider": "CERN (European Organization for Nuclear Research)",
        "opportunity_type": "research_fellowship",
        "description": "Prestigious 8 to 13 week research residency in Geneva, Switzerland, working on advanced computing, data systems, and experimental physics pipelines.",
        "official_url": "https://careers.cern/summer",
        "eligibility_requirements": [
            "Undergraduate or master student in computer science, mathematics, or physics",
            "Must have completed at least 3 years of full-time university studies",
            "Good working knowledge of English (French is an asset)",
            "Member state or non-member state nationality eligible"
        ],
        "beneficiary_type": "individual_student",
        "geographic_scope": "Global",
        "domains": ["Distributed Systems", "Cloud & DevOps", "AI / Machine Learning", "Data Engineering"],
        "required_project_stage": "any",
        "funding_amount_or_benefits": "90 CHF/day living allowance + travel costs covered + health insurance",
        "is_monetary": True,
        "application_deadline": date(2027, 1, 31),
        "is_rolling": False,
        "application_instructions": "Submit academic CV, official transcript of records, and 2 academic letters of recommendation via CERN smart recruiters portal.",
        "date_last_verified": date(2026, 10, 12),
        "status": "active",
        "is_verified": True,
        "source_notes": "Official CERN Summer Student Programme verified from careers.cern/summer."
    },
    {
        "id": "e8888888-8888-8888-8888-888888888888",
        "title": "Y Combinator Startup School",
        "provider": "Y Combinator",
        "opportunity_type": "incubator",
        "description": "Free, world-class online course, community, and co-founder matching platform for aspiring founders and student builders.",
        "official_url": "https://www.startupschool.org/",
        "eligibility_requirements": [
            "Open to anyone building or considering building a technology venture",
            "No formal incorporation or revenue required",
            "Solo founders or teams of any size"
        ],
        "beneficiary_type": "student_team",
        "geographic_scope": "Global",
        "domains": ["Full Stack Web", "AI / Machine Learning", "Fintech", "HealthTech & BioInformatics"],
        "required_project_stage": "idea",
        "funding_amount_or_benefits": "$100,000+ in software credits (AWS, Stripe, OpenAI, Brex) + weekly accountability tracking",
        "is_monetary": False,
        "application_deadline": None,
        "is_rolling": True,
        "application_instructions": "Create free founder profile, submit weekly metric goals, and attend virtual group office hours.",
        "date_last_verified": date(2026, 10, 14),
        "status": "active",
        "is_verified": True,
        "source_notes": "Verified free founder resource from startupschool.org."
    }
]


class ProjectOpportunitiesService:
    """Service managing curated opportunities and student tracking."""

    def __init__(self, opportunities: List[Dict[str, Any]] = None):
        self.opportunities = opportunities or CURATED_OPPORTUNITIES

    def list_opportunities(
        self,
        opportunity_type: Optional[str] = None,
        domain: Optional[str] = None,
        stage: Optional[str] = None,
        beneficiary_type: Optional[str] = None,
        status: Optional[str] = None,
        is_monetary: Optional[bool] = None,
    ) -> List[OpportunityResponse]:
        """Filter opportunities deterministically using provided parameters."""
        results = []
        for raw in self.opportunities:
            if opportunity_type and opportunity_type.lower() != "all":
                if raw["opportunity_type"].lower() != opportunity_type.lower():
                    continue
            if domain and domain.lower() != "all":
                domains = [d.lower() for d in raw.get("domains", [])]
                if not any(domain.lower() in d for d in domains):
                    continue
            if stage and stage.lower() != "all":
                if raw["required_project_stage"].lower() != "any" and raw["required_project_stage"].lower() != stage.lower():
                    continue
            if beneficiary_type and beneficiary_type.lower() != "all":
                if raw["beneficiary_type"].lower() != beneficiary_type.lower():
                    continue
            if status and status.lower() != "all":
                if raw["status"].lower() != status.lower():
                    continue
            if is_monetary is not None:
                if raw["is_monetary"] != is_monetary:
                    continue

            results.append(self._to_schema(raw))
        return results

    def get_opportunity_by_id(self, opp_id: str) -> Optional[OpportunityResponse]:
        """Fetch a single opportunity by UUID string."""
        for raw in self.opportunities:
            if str(raw["id"]) == str(opp_id):
                return self._to_schema(raw)
        return None

    def _to_schema(self, raw: Dict[str, Any]) -> OpportunityResponse:
        return OpportunityResponse(
            id=UUID(raw["id"]) if isinstance(raw["id"], str) else raw["id"],
            title=raw["title"],
            provider=raw["provider"],
            opportunity_type=raw["opportunity_type"],
            description=raw["description"],
            official_url=raw["official_url"],
            eligibility_requirements=raw.get("eligibility_requirements", []),
            beneficiary_type=raw.get("beneficiary_type", "individual_student"),
            geographic_scope=raw.get("geographic_scope", "Global"),
            domains=raw.get("domains", []),
            required_project_stage=raw.get("required_project_stage", "any"),
            funding_amount_or_benefits=raw.get("funding_amount_or_benefits"),
            is_monetary=raw.get("is_monetary", False),
            application_deadline=raw.get("application_deadline"),
            is_rolling=raw.get("is_rolling", False),
            application_instructions=raw.get("application_instructions"),
            date_last_verified=raw.get("date_last_verified", date.today()),
            status=raw.get("status", "active"),
            is_verified=raw.get("is_verified", True),
            source_notes=raw.get("source_notes")
        )


project_opportunities_service = ProjectOpportunitiesService()
