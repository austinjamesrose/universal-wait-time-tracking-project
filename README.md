# Universal Orlando Wait Time Tracker

A data engineering portfolio project that collects, analyzes, and visualizes wait time data from Universal Orlando theme parks.

**🚀 [Live Dashboard](https://austin-rose-wait-time-project.streamlit.app/)** | **🌐 [Portfolio](https://austinrose.io)**

## Overview

This project automatically collects wait time data from three Universal Orlando parks every 30 minutes using the [Queue-Times API](https://queue-times.com). The data is stored in a SQLite database and presented through an interactive Streamlit dashboard.

**Parks Tracked:**
- Islands of Adventure
- Universal Studios Florida
- Epic Universe

## Features

- **Automated Data Collection**: GitHub Actions runs every 30 minutes to fetch and store wait times
- **Historical Analysis**: Explore patterns by hour, day of week, and season
- **Interactive Dashboard**: Filter by park, ride, and date range
- **Insights**: Discover the best times to visit and ride correlations

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/project-wait-time-tracker.git
   cd project-wait-time-tracker
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally

**Collect data manually:**
```bash
python -m src.collector
```

**Check database status:**
```bash
python -m src.collector --check
```

**Run the dashboard:**
```bash
streamlit run dashboard/app.py
```

**Run tests:**
```bash
pytest tests/
```

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
├── data/                  # SQLite database
└── requirements.txt       # Python dependencies
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Data Collection | requests |
| Storage | SQLite |
| Analysis | pandas, Jupyter |
| Visualization | Streamlit, Plotly |
| Automation | GitHub Actions |

## Data Schema

The database stores:
- **Parks**: Theme park metadata
- **Lands**: Themed areas within parks
- **Rides**: Individual attractions
- **Wait Times**: Historical wait time records with timestamps and metadata

## License

MIT License - feel free to use this project as inspiration for your own portfolio!

## Author

Austin Rose - [austinrose.io](https://austinrose.io)
