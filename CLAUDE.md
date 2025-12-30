# Universal Orlando Wait Time Tracker

## Project Overview

A portfolio project that collects, stores, analyzes, and visualizes Universal Orlando wait time data. The project demonstrates Python skills, data engineering fundamentals, and analytical thinking.

**Live Dashboard:** https://austin-rose-wait-time-project.streamlit.app/
**Portfolio:** https://austinrose.io

---

## Current Phase

**Phase 1: Project Setup & Data Collection** (Days 1-4)

---

## Quick Reference

### Parks Tracked
| Park | ID |
|------|-----|
| Islands of Adventure | 64 |
| Universal Studios | 65 |
| Epic Universe | 334 |

### API Endpoint
```
https://queue-times.com/en-US/parks/{park_id}/queue_times.json
```

### Key Commands
```bash
# Run data collection manually
python -m src.collector

# Run tests
pytest tests/

# Start dashboard locally
streamlit run dashboard/app.py
```

---

## Project Structure

```
project-wait-time-tracker/
├── .github/workflows/     # GitHub Actions for scheduled collection
├── src/                   # Source code
│   ├── config.py          # Configuration (park IDs, settings)
│   ├── database.py        # SQLite operations
│   └── collector.py       # API data collection
├── tests/                 # Unit tests
├── notebooks/             # Jupyter notebooks for analysis
├── dashboard/             # Streamlit app
├── data/                  # SQLite database (gitignored)
├── CLAUDE.md              # This file
├── README.md              # Public documentation
└── requirements.txt       # Python dependencies
```

---

## Progress Checklist

### Phase 1: Project Setup & Data Collection
- [x] Create CLAUDE.md (this file)
- [x] Initialize git repository
- [x] Create directory structure
- [x] Create .gitignore
- [x] Create requirements.txt
- [x] Create src/config.py
- [x] Create src/database.py
- [x] Create src/collector.py
- [x] Create basic unit tests
- [x] Create README.md

### Phase 2: Automation & Monitoring
- [x] Test collector locally
- [x] Set up GitHub Actions workflow
- [ ] Add logging and monitoring

### Phase 3: Analysis & Insights
- [x] Create exploration notebook
- [ ] Perform EDA (need more data)
- [ ] Document 3+ insights (need more data)

### Phase 4: Dashboard Development
- [x] Build Streamlit app
- [x] Add interactive filters
- [x] Deploy to Streamlit Cloud
- [x] Link from austinrose.io

### Phase 5: Documentation & Case Study
- [ ] Polish README.md
- [ ] Write CASE_STUDY.md
- [ ] Create blog post

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.11+ |
| Data Collection | requests |
| Storage | SQLite |
| Analysis | pandas, jupyter |
| Visualization | Streamlit, plotly |
| Scheduling | GitHub Actions |
| Hosting | Streamlit Cloud |

---

## Notes

- Data collected every 30 minutes via GitHub Actions
- SQLite database committed to repo for persistence
- Dashboard shows historical analysis only (no live API calls)
- Target: 30+ days of data before deep analysis

## Git Commit Guidelines

- Do NOT include "Generated with Claude Code" or Co-Authored-By lines in commit messages
- Keep commit messages concise and descriptive
