# SANGAM Platform - Quick Start Guide

## First-Time Setup

### 1. Install PostgreSQL

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- During installation, note your password
- Install PostGIS extension via Stack Builder

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

**Mac:**
```bash
brew install postgresql postgis
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql:
CREATE DATABASE sangam_db;
CREATE USER sangam_user WITH PASSWORD 'sangam_pass';
GRANT ALL PRIVILEGES ON DATABASE sangam_db TO sangam_user;
\q
```

### 3. Backend Setup

```bash
cd sangam/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit .env
copy .env.example .env
# Edit .env with your database credentials

# Initialize database and load demo data
python scripts/init_db.py
```

Expected output:
```
🔧 Initializing database...
✓ PostGIS extension enabled
✓ Database tables created
📚 Loading demo universities...
✓ Loaded 4 universities with expertise
🏭 Loading demo industry partners...
✓ Loaded 4 industry partners
🌍 Loading demo challenges...
✓ Loaded 5 demo challenges
✅ Database initialized successfully!
```

### 4. Frontend Setup

```bash
cd sangam/frontend

# Install dependencies
npm install

# Copy .env (optional, uses defaults)
copy .env.example .env
```

## Running the Application

### Option 1: Use Start Script

**Windows:**
```bash
cd sangam
start.bat
```

**Linux/Mac:**
```bash
cd sangam
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd sangam/backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd sangam/frontend
npm run dev
```

## Access the Platform

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

## Demo Walkthrough

### 1. Home Page
- View platform overview
- See role selector in header
- Review features and workflow

### 2. Submit Challenge (Citizen Role)
1. Select "Citizen" from role dropdown
2. Click "Report a Challenge"
3. Fill form with challenge details
4. Submit and view AI analysis

### 3. AI Analysis
The AI analysis shows:
- **Domain Classification**: e.g., "Water & Environment"
- **Priority Score**: Transparent calculation (0-10)
- **Similar Challenges**: Duplicate detection results
- **University Matches**: Top 3 recommended universities
- **Reasoning**: Why each decision was made

### 4. Government Dashboard
1. Select "Government" from role dropdown
2. Click "Dashboard"
3. View statistics and pending challenges
4. Click "Validate" on a pending challenge

### 5. University Dashboard
1. Select "University" from role dropdown
2. View matched challenges (challenges matched to your expertise)
3. Accept a challenge to create a project

### 6. Student/Team View
1. Select "Student/Team" from role dropdown
2. View assigned project
3. Form team and add members
4. Update milestone progress

### 7. Industry Dashboard
1. Select "Industry" from role dropdown
2. Browse available projects
3. Offer collaboration (mentorship, resources, funding)

### 8. Impact Tracking
1. Switch to "Government" role
2. View Impact Dashboard showing:
   - People reached
   - Communities impacted
   - Projects completed
   - Geographic distribution

## Testing AI Features

### Test Classification
Submit challenges with different keywords:
- **Water**: "flooding", "drinking water", "contamination"
- **Healthcare**: "hospital", "medical", "emergency"
- **Education**: "school", "student", "teacher"
- **Agriculture**: "farming", "crop", "irrigation"

The AI will classify based on keywords and show reasoning.

### Test Priority Scoring
Try different values:
- **High Priority**: 5000+ people affected, urgency: critical
- **Medium Priority**: 500-5000 people affected, urgency: high
- **Low Priority**: <500 people affected, urgency: low

The score breakdown shows exact calculation.

### Test Duplicate Detection
Submit similar challenges to see similarity scores:
1. Submit: "Flooding damaged water pipeline"
2. Submit: "Flood destroyed drinking water infrastructure"
3. AI shows similarity percentage and recommends consolidation

## Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL is running
# Windows: Check Services
# Linux: sudo systemctl status postgresql
# Mac: brew services list

# Verify connection
psql -U sangam_user -d sangam_db
```

### Port Already in Use

**Backend (8000):**
```bash
# Change port
python -m uvicorn app.main:app --reload --port 8001
```

**Frontend (5173):**
Edit `vite.config.js`:
```js
server: { port: 3000 }
```

### AI Model Not Loading
```bash
# Test sentence transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# If fails, AI will use TF-IDF fallback (still works)
```

### Frontend Not Connecting to Backend
- Check backend is running on port 8000
- Verify VITE_API_URL in frontend/.env
- Check browser console for CORS errors

## Common Commands

```bash
# Backend
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Database reset
cd backend
python scripts/init_db.py

# Run tests
cd backend
pytest tests/

# Build frontend for production
cd frontend
npm run build
```

## Next Steps

1. Explore all role-based dashboards
2. Submit test challenges
3. Validate challenges as government
4. Create projects as university
5. Track impact metrics
6. Review API documentation at /api/docs

## For Judges

The complete demo scenario flows through all roles in 3-5 minutes:
1. Citizen reports challenge
2. AI analyzes (live, not mocked)
3. Government validates
4. University accepts
5. Team forms
6. Industry collaborates
7. Milestones tracked
8. Community feedback
9. Impact measured

All AI decisions show transparent reasoning. All demo data is clearly labeled.
