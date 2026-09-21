# SANGAM Database Schema

Default engine: **SQLite** (`sangam.db`). Optional: PostgreSQL via `DATABASE_URL`.

Tables (created automatically by SQLAlchemy on startup):

| Table | Purpose |
|-------|---------|
| `users` | Demo role users (citizen, government, university, student, industry) |
| `universities` | Prototype institution expertise profiles (**Demo Data**) |
| `industry_partners` | Prototype CSR/industry partners (**Demo Data**) |
| `challenges` | Societal challenge reports + AI fields + status |
| `projects` | Accepted challenge workspaces (e.g. AquaGuard) |
| `milestones` | Project milestone checklist |
| `industry_collaborations` | Mentorship/tech/equipment offers (no payments) |
| `community_feedback` | Post-pilot community ratings |

Provenance columns: `is_demo`, `provenance` (`demo` | `user` | `system`).

Challenge / project status flow:

`submitted → under_review → validated → matched → university_accepted → team_formed → industry_collaboration → prototype → testing → pilot → completed`

Geo: `latitude` / `longitude` on challenges (map markers). **PostGIS** is a future integration for spatial SQL.
