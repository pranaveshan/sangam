"""
Database initialization script
Run this to create all tables and load demo data
"""
import sys
from sqlalchemy import text
from app.database.connection import engine, SessionLocal, Base
from app.models.challenge import (
    User, University, UniversityExpertise, Challenge,
    AIAnalysis, UniversityMatch, UserRole, ChallengeStatus, UrgencyLevel
)
from app.models.project import (
    Project, Team, TeamMember, FacultyMentor,
    Milestone, IndustryPartner, IndustryCollaboration,
    CommunityFeedback, ImpactMetric
)

def init_db():
    """Initialize database tables"""
    print("🔧 Initializing database...")

    # Enable PostGIS extension
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.commit()
        print("✓ PostGIS extension enabled")
    except Exception as e:
        print(f"ℹ PostGIS may already be enabled: {e}")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

def load_demo_universities(db):
    """Load demo universities"""
    print("\n📚 Loading demo universities...")

    universities_data = [
        {
            "name": "Indian Institute of Technology Delhi",
            "location": "New Delhi",
            "state": "Delhi",
            "district": "New Delhi",
            "established_year": 1961,
            "website": "https://iitd.ac.in",
            "contact_email": "admin@iitd.ac.in",
            "expertise": [
                {
                    "department": "Civil Engineering",
                    "research_area": "Water Resources & Infrastructure",
                    "keywords": ["water", "infrastructure", "civil", "design", "analysis"]
                },
                {
                    "department": "Electrical Engineering",
                    "research_area": "Renewable Energy & Solar Systems",
                    "keywords": ["energy", "solar", "power", "electrical", "renewable"]
                }
            ]
        },
        {
            "name": "National Institute of Technology Karnataka",
            "location": "Surathkal",
            "state": "Karnataka",
            "district": "Udupi",
            "established_year": 1960,
            "website": "https://nitk.ac.in",
            "contact_email": "admin@nitk.ac.in",
            "expertise": [
                {
                    "department": "Environmental Engineering",
                    "research_area": "Water Quality & Sanitation",
                    "keywords": ["water", "sanitation", "environment", "pollution", "treatment"]
                },
                {
                    "department": "Mechanical Engineering",
                    "research_area": "IoT & Sensors",
                    "keywords": ["iot", "sensors", "monitoring", "automation", "device"]
                }
            ]
        },
        {
            "name": "Anna University Chennai",
            "location": "Chennai",
            "state": "Tamil Nadu",
            "district": "Chennai",
            "established_year": 1978,
            "website": "https://annauniv.edu.in",
            "contact_email": "admin@annauniv.edu.in",
            "expertise": [
                {
                    "department": "Computer Science Engineering",
                    "research_area": "AI & Machine Learning",
                    "keywords": ["ai", "machine learning", "data", "software", "analysis"]
                },
                {
                    "department": "Biomedical Engineering",
                    "research_area": "Healthcare Technology",
                    "keywords": ["healthcare", "medical", "disease", "diagnosis", "treatment"]
                }
            ]
        },
        {
            "name": "Delhi University School of Science",
            "location": "New Delhi",
            "state": "Delhi",
            "district": "New Delhi",
            "established_year": 1922,
            "website": "https://www.du.ac.in",
            "contact_email": "admin@du.ac.in",
            "expertise": [
                {
                    "department": "Environmental Science",
                    "research_area": "Climate Change & Sustainability",
                    "keywords": ["environment", "climate", "sustainability", "disaster", "management"]
                },
                {
                    "department": "Chemistry",
                    "research_area": "Water Purification Technologies",
                    "keywords": ["water", "purification", "chemistry", "contamination", "treatment"]
                }
            ]
        }
    ]

    for univ_data in universities_data:
        # Create university
        university = University(
            name=univ_data["name"],
            location=univ_data["location"],
            state=univ_data["state"],
            district=univ_data["district"],
            established_year=univ_data["established_year"],
            website=univ_data["website"],
            contact_email=univ_data["contact_email"],
            is_demo_data=True
        )
        db.add(university)
        db.flush()

        # Add expertise areas
        for exp in univ_data["expertise"]:
            expertise = UniversityExpertise(
                university_id=university.id,
                department=exp["department"],
                research_area=exp["research_area"],
                faculty_count=15,
                lab_facilities=["Laboratory", "Computer Center", "Workshop"],
                keywords=exp["keywords"]
            )
            db.add(expertise)

    db.commit()
    print(f"✓ Loaded {len(universities_data)} universities with expertise")

def load_demo_industry_partners(db):
    """Load demo industry partners"""
    print("\n🏭 Loading demo industry partners...")

    partners_data = [
        {
            "name": "TechForAll Foundation",
            "type": "NGO",
            "sector": "Technology & Social Impact",
            "website": "https://techforall.org",
            "contact_name": "Rajesh Kumar",
            "contact_email": "rajesh@techforall.org",
            "csr_focus": "Technology for rural development"
        },
        {
            "name": "Global Water Solutions",
            "type": "CSR Organization",
            "sector": "Water & Sanitation",
            "website": "https://globalwater.org",
            "contact_name": "Priya Sharma",
            "contact_email": "priya@globalwater.org",
            "csr_focus": "Clean water access"
        },
        {
            "name": "HealthTech Innovations",
            "type": "Startup",
            "sector": "Healthcare Technology",
            "website": "https://healthtech.io",
            "contact_name": "Amit Patel",
            "contact_email": "amit@healthtech.io",
            "csr_focus": "Affordable healthcare solutions"
        },
        {
            "name": "Green Energy India",
            "type": "CSR Organization",
            "sector": "Renewable Energy",
            "website": "https://greenenergyindia.org",
            "contact_name": "Sunita Verma",
            "contact_email": "sunita@greenenergyindia.org",
            "csr_focus": "Solar energy for villages"
        }
    ]

    for partner_data in partners_data:
        partner = IndustryPartner(
            name=partner_data["name"],
            type=partner_data["type"],
            sector=partner_data["sector"],
            website=partner_data["website"],
            contact_name=partner_data["contact_name"],
            contact_email=partner_data["contact_email"],
            csr_focus_areas=partner_data["csr_focus"],
            is_demo_data=True
        )
        db.add(partner)

    db.commit()
    print(f"✓ Loaded {len(partners_data)} industry partners")

def load_demo_challenges(db):
    """Load demo challenges and AI analysis"""
    print("\n🌍 Loading demo challenges...")

    challenges_data = [
        {
            "title": "Flooding damages drinking water infrastructure",
            "description": "During monsoon season, heavy flooding in District X has damaged the main water pipeline infrastructure, affecting clean water supply to over 5,000 residents. The damaged infrastructure needs urgent repair and reinforcement to prevent future incidents.",
            "category": "Water Infrastructure",
            "location_name": "Rural Area near Dam",
            "district": "Raigad",
            "state": "Maharashtra",
            "people_affected": 5000,
            "urgency": "high"
        },
        {
            "title": "Lack of healthcare facilities in remote village",
            "description": "Village population of 2,500 has no primary health center. Nearest clinic is 25 km away, causing maternal mortality and inability to handle emergencies. Need for establishing basic healthcare facility with trained staff.",
            "category": "Healthcare Access",
            "location_name": "Remote Village",
            "district": "Chhindwara",
            "state": "Madhya Pradesh",
            "people_affected": 2500,
            "urgency": "critical"
        },
        {
            "title": "Poor road connectivity affecting agricultural market access",
            "description": "Farmers in 8 villages cannot reach markets due to poor road conditions. During monsoon, the kutcha road becomes impassable, forcing farmers to sell crops at 40% lower prices to local traders.",
            "category": "Rural Infrastructure",
            "location_name": "Agricultural Region",
            "district": "Vidisha",
            "state": "Madhya Pradesh",
            "people_affected": 1200,
            "urgency": "medium"
        },
        {
            "title": "Girls dropping out of school due to distance",
            "description": "High school is 8 km away from village. Girls drop out after primary school due to safety concerns and transportation challenges. Current dropout rate is 65% for girls vs 15% for boys.",
            "category": "Education Access",
            "location_name": "Village School District",
            "district": "Wardha",
            "state": "Maharashtra",
            "people_affected": 450,
            "urgency": "high"
        },
        {
            "title": "Groundwater contamination from industrial waste",
            "description": "Industrial effluent from nearby factory has contaminated groundwater. 3,000 residents depend on this water. Contamination causes water-borne diseases affecting children especially.",
            "category": "Water Quality",
            "location_name": "Industrial Area",
            "district": "Jalgaon",
            "state": "Maharashtra",
            "people_affected": 3000,
            "urgency": "high"
        }
    ]

    for challenge_data in challenges_data:
        challenge = Challenge(
            title=challenge_data["title"],
            description=challenge_data["description"],
            category=challenge_data["category"],
            location_name=challenge_data["location_name"],
            district=challenge_data["district"],
            state=challenge_data["state"],
            people_affected=challenge_data["people_affected"],
            urgency=challenge_data["urgency"],
            contact_name="Citizen Reporter",
            contact_email="citizen@sangam.local",
            status="submitted",
            is_demo_data=True
        )
        db.add(challenge)
        db.flush()

        print(f"  ✓ Added: {challenge_data['title'][:50]}...")

    db.commit()
    print(f"✓ Loaded {len(challenges_data)} demo challenges")

if __name__ == "__main__":
    db = SessionLocal()

    try:
        init_db()
        load_demo_universities(db)
        load_demo_industry_partners(db)
        load_demo_challenges(db)

        print("\n✅ Database initialized successfully!")
        print("\nYou can now run the application with:")
        print("  python -m uvicorn app.main:app --reload")

    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
