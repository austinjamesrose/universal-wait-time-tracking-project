# Theme Park Wait Time Tracker

## Portfolio Project Plan

---

## Project Overview

**Goal:** Build an end-to-end data project that collects, stores, analyzes, and visualizes theme park wait time data—demonstrating Python skills, data engineering fundamentals, and analytical thinking.

**Portfolio Showcase:** A live, interactive web application hosted on your site (austinrose.io) where visitors can explore wait time patterns and insights.

---

## Success Criteria

1. Automated data collection running reliably for 30+ days
2. Clean, documented codebase in a public GitHub repository
3. Interactive visualization or dashboard accessible from your portfolio
4. Written case study explaining your process, decisions, and findings
5. At least 2-3 interesting insights you discovered from the data

---

## Phase Breakdown

### Phase 1: Foundation & Data Collection

*Estimated time: 1-2 weeks*

| Task | Description |
|------|-------------|
| Set up project repository | Create GitHub repo with proper structure, README, .gitignore |
| Explore the API | Test Queue-Times API, understand data structure and rate limits |
| Build collection script | Python script that pulls wait times and handles errors gracefully |
| Set up storage | SQLite database with appropriate schema |
| Schedule automation | Run script every 15-30 min (local first, then cloud) |

**Milestone:** Data flowing into your database automatically.

---

### Phase 2: Data Engineering & Quality

*Estimated time: 1 week*

| Task | Description |
|------|-------------|
| Add metadata enrichment | Day of week, hour, holiday flags, season |
| Implement logging | Track script runs, errors, data volumes |
| Build data validation | Check for missing data, anomalies, duplicates |
| Cloud migration | Move scheduler to a free cloud service (Railway, PythonAnywhere, or Google Cloud Functions) |

**Milestone:** Reliable, cloud-hosted pipeline with quality monitoring.

---

### Phase 3: Analysis & Insights

*Estimated time: 1-2 weeks*

| Task | Description |
|------|-------------|
| Exploratory analysis | Jupyter notebook exploring patterns in the data |
| Statistical summaries | Average waits by hour, day, ride; variability analysis |
| Interesting questions | Best time to ride popular attractions? Correlation between rides? |
| Document findings | Write up 2-3 key insights with supporting visuals |

**Milestone:** Notebook with clear, compelling insights.

---

### Phase 4: Visualization & Presentation

*Estimated time: 2 weeks*

| Task | Description |
|------|-------------|
| Choose framework | Streamlit (easiest), Dash, or static site with charts |
| Build interactive dashboard | Let users explore by park, ride, time period |
| Design for portfolio | Clean UI, your branding, mobile-friendly |
| Deploy | Host on Streamlit Cloud, Vercel, or similar free tier |
| Connect to austinrose.io | Embed or link prominently from your portfolio |

**Milestone:** Live, public-facing project anyone can interact with.

---

### Phase 5: Documentation & Case Study

*Estimated time: 1 week*

| Task | Description |
|------|-------------|
| Polish GitHub README | Clear explanation, screenshots, setup instructions |
| Write case study | Blog-style post covering motivation, process, challenges, learnings |
| Record demo (optional) | Short video walkthrough for LinkedIn or portfolio |

**Milestone:** Complete, portfolio-ready project with compelling narrative.

---

## Technical Stack

| Layer | Tool | Why |
|-------|------|-----|
| Language | Python | Your learning focus, industry standard |
| Data collection | requests library | Simple, reliable HTTP calls |
| Storage | SQLite → BigQuery (optional) | Start simple, scale if needed |
| Analysis | pandas, jupyter | Standard data analysis workflow |
| Visualization | Streamlit | Fastest path to interactive web app, free hosting |
| Scheduling | GitHub Actions or PythonAnywhere | Free, reliable, easy to set up |
| Version control | GitHub | Public repo for portfolio visibility |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API goes down or changes | Build error handling; document data gaps |
| Not enough data variety | Collect for at least 30 days before deep analysis |
| Scope creep | Stick to phases; prediction model is a stretch goal only |
| Hosting costs | Use free tiers (Streamlit Cloud, PythonAnywhere) |

---

## Timeline

Assuming a few hours per week of focused work:

| Weeks | Phase |
|-------|-------|
| 1-2 | Phase 1: Foundation & Data Collection |
| 3 | Phase 2: Data Engineering & Quality |
| 4-5 | Phase 3: Analysis & Insights |
| 6-7 | Phase 4: Visualization & Presentation |
| 8 | Phase 5: Documentation & Case Study |

**Total: ~8 weeks to a polished, portfolio-ready project.**

---

## Resources

- **Queue-Times API:** https://queue-times.com/api
- **Streamlit Documentation:** https://docs.streamlit.io
- **SQLite with Python:** https://docs.python.org/3/library/sqlite3.html

---

## Getting Started

1. Create a new GitHub repository for this project
2. Clone it locally and set up your Python virtual environment
3. Start with Phase 1, Task 1: Explore the Queue-Times API
4. Use this document as your guide—check off tasks as you complete them

Good luck, and have fun with it! 🎢
