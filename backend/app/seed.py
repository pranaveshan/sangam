"""Seed DEMO DATA for the SIH AquaGuard demonstration journey."""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .models import (
    User, University, IndustryPartner, Challenge, Project,
    Milestone, IndustryCollaboration, CommunityFeedback,
    ChallengeStatus, DataProvenance,
)


DEFAULT_MILESTONES = [
    "Requirement Analysis",
    "Research",
    "Prototype Design",
    "Prototype Development",
    "Field Testing",
    "Community Validation",
    "Pilot Deployment",
]


def seed_database(db: Session, force: bool = False) -> None:
    existing = db.query(User).filter(User.email == "citizen.demo@sangam.local").first()
    if existing and not force:
        return
    if force:
        for model in (
            CommunityFeedback, IndustryCollaboration, Milestone, Project,
            Challenge, IndustryPartner, University, User,
        ):
            db.query(model).delete()
        db.commit()

    users = [
        User(
            name="Priya Sharma", email="citizen.demo@sangam.local", role="citizen",
            district="Barmer", phone="+91-90000-00001", is_demo=True,
            provenance=DataProvenance.DEMO.value,
        ),
        User(
            name="Admin Officer", email="gov.demo@sangam.local", role="government",
            organization="District Innovation Cell (DEMO)", district="Barmer",
            is_demo=True, provenance=DataProvenance.DEMO.value,
        ),
        User(
            name="Dr. Ananya Rao", email="uni.demo@sangam.local", role="university",
            organization="Desert Tech University (DEMO)", district="Jodhpur",
            is_demo=True, provenance=DataProvenance.DEMO.value,
        ),
        User(
            name="Arjun Mehta", email="student.demo@sangam.local", role="student",
            organization="AquaGuard Team (DEMO)", district="Jodhpur",
            is_demo=True, provenance=DataProvenance.DEMO.value,
        ),
        User(
            name="Neha Kapoor", email="industry.demo@sangam.local", role="industry",
            organization="HydroSense Labs CSR (DEMO)", district="Jaipur",
            is_demo=True, provenance=DataProvenance.DEMO.value,
        ),
    ]
    db.add_all(users)
    db.flush()

    universities = [
        University(
            name="Desert Tech University (DEMO)",
            short_name="DTU-DEMO",
            state="Rajasthan",
            district="Jodhpur",
            departments=[
                "Civil Engineering", "Environmental Engineering",
                "Computer Science", "Electronics & IoT",
            ],
            research_areas=[
                "Water Resources", "Water Infrastructure", "Flood Resilience",
                "Low-cost Sensing", "Rural WASH",
            ],
            faculty_expertise=[
                "Civil Engineering", "Environmental Engineering", "Hydrology", "IoT",
            ],
            laboratory_capabilities=[
                "Water Quality Lab", "IoT Prototyping Lab", "Field Sensors Workshop",
            ],
            student_skills=["IoT", "Embedded Systems", "Data Analysis", "Field Survey"],
            incubation_facilities=["DTU Innovation Hub (DEMO)", "Hardware Maker Space"],
            domains=["Water", "Environment", "Disaster Management", "Energy"],
            is_demo=True,
            notes="DEMO DATA — Fictional prototype institution. Not a real partnership.",
        ),
        University(
            name="Aravali Institute of Technology (DEMO)",
            short_name="AIT-DEMO",
            state="Rajasthan",
            district="Jaipur",
            departments=["Public Health", "Computer Science", "Social Sciences"],
            research_areas=["Public Health Informatics", "Community Health", "GIS"],
            faculty_expertise=["Public Health", "Data Science", "Mobile Apps"],
            laboratory_capabilities=["Health Analytics Lab"],
            student_skills=["App Development", "Survey Design"],
            incubation_facilities=["AIT Startup Cell (DEMO)"],
            domains=["Healthcare", "Public Administration", "Accessibility"],
            is_demo=True,
            notes="DEMO DATA — Fictional prototype institution.",
        ),
        University(
            name="Green Valley Agricultural University (DEMO)",
            short_name="GVAU-DEMO",
            state="Rajasthan",
            district="Udaipur",
            departments=["Agricultural Engineering", "Soil Science", "Rural Development"],
            research_areas=["Irrigation Systems", "Crop Advisory", "Soil Health"],
            faculty_expertise=["Agricultural Engineering", "IoT", "Soil Science"],
            laboratory_capabilities=["Precision Ag Lab", "Soil Testing Lab"],
            student_skills=["IoT", "Field Extension"],
            incubation_facilities=["AgriTech Incubator (DEMO)"],
            domains=["Agriculture", "Rural Livelihoods", "Water"],
            is_demo=True,
            notes="DEMO DATA — Fictional prototype institution.",
        ),
        University(
            name="Metro Civic University (DEMO)",
            short_name="MCU-DEMO",
            state="Rajasthan",
            district="Ajmer",
            departments=["Urban Planning", "Civil Engineering", "Public Policy"],
            research_areas=["Urban Mobility", "Municipal Services", "Housing"],
            faculty_expertise=["Urban Planning", "GIS", "Public Policy"],
            laboratory_capabilities=["Urban Simulation Lab"],
            student_skills=["GIS", "Policy Research"],
            incubation_facilities=["Civic Tech Lab (DEMO)"],
            domains=["Urban Development", "Public Administration", "Energy"],
            is_demo=True,
            notes="DEMO DATA — Fictional prototype institution.",
        ),
    ]
    db.add_all(universities)
    db.flush()

    partners = [
        IndustryPartner(
            name="HydroSense Labs CSR (DEMO)",
            sector="Water Technology / CSR",
            support_types=["mentorship", "technology", "equipment", "sponsorship"],
            focus_domains=["Water", "Environment", "Disaster Management"],
            description="DEMO partner offering IoT sensor mentorship and prototype kits.",
            notes="DEMO DATA — No real CSR partnership or funding.",
        ),
        IndustryPartner(
            name="AgriLink Solutions (DEMO)",
            sector="AgriTech",
            support_types=["mentorship", "technology"],
            focus_domains=["Agriculture", "Rural Livelihoods", "Water"],
            description="DEMO partner for farm-tech collaboration.",
            notes="DEMO DATA — Prototype only.",
        ),
        IndustryPartner(
            name="CivicForge Industries (DEMO)",
            sector="Smart Infrastructure",
            support_types=["equipment", "sponsorship", "mentorship"],
            focus_domains=["Urban Development", "Energy", "Accessibility"],
            description="DEMO industrial partner for civic infrastructure pilots.",
            notes="DEMO DATA — Prototype only.",
        ),
    ]
    db.add_all(partners)
    db.flush()

    citizen = users[0]
    dtu = universities[0]
    hydrosense = partners[0]

    # Similar flood-water reports (for duplicate detection demo)
    similar_reports = [
        Challenge(
            title="Handpump water contaminated after monsoon flooding",
            description=(
                "After recent floods, several handpumps in nearby villages show muddy "
                "and foul-smelling water. Residents fear contamination of drinking sources."
            ),
            category="Water",
            location="Village Cluster B, Barmer Rural",
            district="Barmer",
            state="Rajasthan",
            latitude=25.75, longitude=71.38,
            community_impact="Families relying on handpumps for daily drinking water.",
            people_affected=1800,
            urgency="high",
            severity="high",
            geographic_spread="local",
            contact_name="Ramesh Kumar",
            status=ChallengeStatus.VALIDATED.value,
            domain="Water & Environment",
            subdomain="Water Quality",
            priority_score=72.0,
            priority_label="High",
            required_expertise=["Environmental Engineering", "Water Quality", "IoT"],
            reporter_id=citizen.id,
            is_demo=True,
            provenance=DataProvenance.DEMO.value,
            evidence_score=0.5,
            ai_analysis={"note": "DEMO seeded similar report"},
        ),
        Challenge(
            title="Broken water pipelines after flood damage",
            description=(
                "Flooding damaged distribution pipelines connecting the overhead tank "
                "to household taps. Temporary tanker supply is irregular."
            ),
            category="Water",
            location="Panchayat Ward 3, Barmer",
            district="Barmer",
            state="Rajasthan",
            latitude=25.76, longitude=71.40,
            community_impact="Interrupted piped water to ~400 households.",
            people_affected=2200,
            urgency="high",
            severity="medium",
            geographic_spread="local",
            status=ChallengeStatus.UNDER_REVIEW.value,
            domain="Water & Environment",
            subdomain="Water Infrastructure",
            priority_score=68.0,
            priority_label="High",
            required_expertise=["Civil Engineering", "Water Infrastructure"],
            reporter_id=citizen.id,
            is_demo=True,
            provenance=DataProvenance.DEMO.value,
            evidence_score=0.4,
        ),
        Challenge(
            title="School closed due to unsafe drinking water post flood",
            description=(
                "Local primary school closed midday classes because drinking water "
                "storage tanks were flooded and may be contaminated."
            ),
            category="Water",
            location="Govt Primary School, Barmer Block",
            district="Barmer",
            state="Rajasthan",
            latitude=25.74, longitude=71.35,
            community_impact="Affects student attendance and mid-day meal hygiene.",
            people_affected=450,
            urgency="medium",
            severity="high",
            geographic_spread="local",
            status=ChallengeStatus.SUBMITTED.value,
            domain="Water & Environment",
            subdomain="Water Quality",
            priority_score=58.0,
            priority_label="Medium",
            required_expertise=["Environmental Engineering", "Public Health"],
            is_demo=True,
            provenance=DataProvenance.DEMO.value,
            evidence_score=0.35,
        ),
    ]
    db.add_all(similar_reports)
    db.flush()

    # Main AquaGuard challenge — advanced in lifecycle for demo
    main = Challenge(
        title="Flooding has damaged drinking-water infrastructure in a rural community",
        description=(
            "Recent monsoon flooding has damaged drinking-water infrastructure in a rural "
            "community near Barmer. Pipelines are ruptured, storage tanks are silted, and "
            "residents report turbid water from remaining taps and handpumps. Communities "
            "need low-cost monitoring and temporary safe-water guidance while infrastructure "
            "is restored. Multiple nearby villages report similar issues."
        ),
        category="Water",
        location="Gram Panchayat Rohili, Barmer Rural",
        district="Barmer",
        state="Rajasthan",
        latitude=25.752, longitude=71.396,
        community_impact=(
            "Unsafe drinking water risk for flood-affected households; women and children "
            "travel farther for tanker water; school and anganwadi operations disrupted."
        ),
        people_affected=5200,
        urgency="high",
        severity="high",
        geographic_spread="district",
        contact_name="Priya Sharma",
        contact_email="citizen.demo@sangam.local",
        contact_phone="+91-90000-00001",
        status=ChallengeStatus.PILOT.value,
        domain="Water & Environment",
        subdomain="Water Infrastructure",
        priority_score=78.5,
        priority_label="High",
        required_expertise=[
            "Civil Engineering", "Environmental Engineering", "IoT", "Hydrology",
        ],
        similar_challenge_ids=[c.id for c in similar_reports],
        matched_university_id=dtu.id,
        reporter_id=citizen.id,
        is_demo=True,
        provenance=DataProvenance.DEMO.value,
        evidence_score=0.7,
        ai_analysis={
            "domain": "Water & Environment",
            "subdomain": "Water Infrastructure",
            "priority": "High",
            "estimated_impact": "High",
            "required_expertise": [
                "Civil Engineering", "Environmental Engineering", "IoT",
            ],
            "similar_reports": 3,
            "recommended_action": "Consolidate and validate",
            "disclaimer": (
                "DEMO journey preloaded. AI methods: local keyword NLP + TF-IDF similarity "
                "+ transparent weighted scoring."
            ),
        },
    )
    db.add(main)
    db.flush()

    # Mark similar as consolidated into main
    for c in similar_reports:
        c.consolidated_into_id = main.id
        if c.status == ChallengeStatus.SUBMITTED.value:
            c.status = ChallengeStatus.CONSOLIDATED.value

    project = Project(
        name="AquaGuard",
        goal=(
            "Develop a low-cost water-quality monitoring system for flood-affected communities."
        ),
        challenge_id=main.id,
        university_id=dtu.id,
        status=ChallengeStatus.PILOT.value,
        proposal=(
            "AquaGuard proposes a solar-powered IoT sensing kit measuring turbidity, TDS, "
            "and temperature, with SMS/offline alerts for panchayat volunteers and a "
            "dashboard for district officers. Kits will be assembled with student makers "
            "and field-tested in Barmer villages. "
            "[DEMO DATA — Proposal text for SIH demonstration]"
        ),
        team_name="AquaGuard",
        team_members=[
            {"name": "Arjun Mehta", "role": "Team Lead / IoT", "year": "4th Year"},
            {"name": "Sana Qureshi", "role": "Environmental Eng.", "year": "3rd Year"},
            {"name": "Vikram Singh", "role": "Civil / Field Ops", "year": "4th Year"},
            {"name": "Meera Iyer", "role": "Data & Dashboard", "year": "3rd Year"},
        ],
        faculty_mentors=[
            {
                "name": "Dr. Ananya Rao",
                "department": "Environmental Engineering",
                "expertise": "Water Resources & WASH",
            },
            {
                "name": "Prof. Kabir Desai",
                "department": "Electronics & IoT",
                "expertise": "Low-cost Sensing",
            },
        ],
        match_explanation=(
            "Matched because the institution has Civil Engineering + Water Resources "
            "expertise; IoT prototyping lab; and flood-resilience research (DEMO university)."
        ),
        match_score=92.0,
        people_impacted=3200,
        communities_reached=4,
        pilot_location="Rohili & Cluster B villages, Barmer",
        pilot_notes=(
            "Pilot kits deployed at 6 water points. Volunteers trained. "
            "DEMO DATA — Simulated pilot for SIH demo journey."
        ),
        is_demo=True,
        provenance=DataProvenance.DEMO.value,
    )
    db.add(project)
    db.flush()

    now = datetime.utcnow()
    milestone_defs = [
        ("Requirement Analysis", "completed", 20),
        ("Research", "completed", 16),
        ("Prototype Design", "completed", 12),
        ("Prototype Development", "completed", 8),
        ("Field Testing", "completed", 5),
        ("Community Validation", "completed", 2),
        ("Pilot Deployment", "in_progress", 0),
    ]
    for i, (title, status, days_ago) in enumerate(milestone_defs):
        db.add(Milestone(
            project_id=project.id,
            title=title,
            description=f"AquaGuard milestone: {title}",
            order_index=i + 1,
            status=status,
            completed_at=(now - timedelta(days=days_ago)) if status == "completed" else None,
        ))

    db.add(IndustryCollaboration(
        project_id=project.id,
        partner_id=hydrosense.id,
        support_type="mentorship",
        details=(
            "HydroSense Labs CSR (DEMO) provides technical mentorship on sensor calibration "
            "and loaner turbidity probe kits. DEMO sponsorship — no real funds transferred."
        ),
        status="active",
        is_demo=True,
        provenance=DataProvenance.DEMO.value,
        financial_note="DEMO / PROTOTYPE — No real financial transactions.",
    ))

    db.add_all([
        CommunityFeedback(
            project_id=project.id,
            user_id=citizen.id,
            rating=4,
            feedback=(
                "The monitoring board near the handpump helps us know when water looks unsafe. "
                "Still need more tanker coordination."
            ),
            problem_improvement="Water turbidity alerts are clearer; pipeline repair still pending.",
            deployment_confirmed=True,
            is_demo=True,
            provenance=DataProvenance.DEMO.value,
        ),
        CommunityFeedback(
            project_id=project.id,
            rating=5,
            feedback="Volunteers explained the colour indicators well. Useful during monsoon.",
            problem_improvement="Fewer stomach complaints reported this week (anecdotal).",
            deployment_confirmed=True,
            is_demo=True,
            provenance=DataProvenance.DEMO.value,
        ),
    ])

    # Extra challenges for gov dashboard variety (all DEMO)
    extras = [
        ("Intermittent electricity affecting cold-chain vaccines", "Energy", "Healthcare",
         "Ajmer", ChallengeStatus.MATCHED.value, 2100),
        ("Open waste dumping near residential colony", "Environment", "Environment",
         "Jaipur", ChallengeStatus.VALIDATED.value, 3500),
        ("Farmers need advisory for drip irrigation adoption", "Agriculture", "Agriculture",
         "Udaipur", ChallengeStatus.TEAM_FORMED.value, 800),
        ("Inaccessible ramp at community health centre", "Accessibility", "Accessibility",
         "Jodhpur", ChallengeStatus.UNDER_REVIEW.value, 120),
        ("Digital literacy gap among SHG members", "Education", "Rural Livelihoods",
         "Bikaner", ChallengeStatus.SUBMITTED.value, 600),
    ]
    for title, category, domain, district, status, people in extras:
        db.add(Challenge(
            title=title,
            description=f"DEMO challenge seed: {title}. Created for dashboard statistics.",
            category=category,
            location=f"Demo location, {district}",
            district=district,
            state="Rajasthan",
            community_impact="DEMO impact narrative for SIH statistics.",
            people_affected=people,
            urgency="medium",
            severity="medium",
            geographic_spread="local",
            status=status,
            domain=domain,
            subdomain="General",
            priority_score=50.0,
            priority_label="Medium",
            required_expertise=["Interdisciplinary Research"],
            is_demo=True,
            provenance=DataProvenance.DEMO.value,
            latitude=26.0 + hash(district) % 10 / 10,
            longitude=73.0 + hash(title) % 20 / 10,
        ))

    db.commit()


def ensure_default_milestones(db: Session, project_id: int) -> None:
    existing = db.query(Milestone).filter(Milestone.project_id == project_id).count()
    if existing:
        return
    for i, title in enumerate(DEFAULT_MILESTONES):
        db.add(Milestone(
            project_id=project_id,
            title=title,
            description=f"Project milestone: {title}",
            order_index=i + 1,
            status="pending",
        ))
    db.commit()
