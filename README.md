# OncStat - Public Health Cancer Data Insights Dashboard

[![Live Demo](https://img.shields.io/badge/Live_Demo-oncstat.onrender.com-00C7B7?style=for-the-badge&logo=render&logoColor=white)](https://oncstat.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Tests-91%20Passing-success?style=for-the-badge&logo=pytest&logoColor=white)](https://github.com/ayqon/OncStat)

> 🌐 **Live Web Application:** [https://oncstat.onrender.com/](https://oncstat.onrender.com/)

A full-stack epidemiology and data analytics dashboard for analysing UK Cancer Registration data with clinical focus on **Sarcomas** (ICD-10 `C49`, `C40-C41`).

## Features

- 📊 **Dashboard** - Real-time statistics overview and summary cards
- 📥 **Import Data** - Automated ingestion from NHS Digital, US CDC (`BYSITE.TXT`), or custom CSV/Excel/JSON
- 🔍 **Filter & Explore** - Multi-criteria clinical search by ICD-10, diagnosis year, age, and sex
- 📈 **Interactive Charts** - Plotly-powered dynamic visualizations (incidence trends, top cancer sites, demographic breakdowns)
- 📝 **CRUD Operations** - Paginated Create, Read, Update, and Delete records with automatic sarcoma tagging
- 💾 **Multi-Format Export** - Download filtered subsets in CSV, Excel (`.xlsx`), JSON, or TXT
- 📜 **Activity Logs** - Live audit trail tracking all user operations

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download and process data
python download_data.py
python etl.py

# Run the server
flask run --port 5001
```

Open **http://127.0.0.1:5001** in your browser.

## Project Structure

```
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── db_utils.py         # Database utilities  
├── etl.py              # ETL pipeline
├── download_data.py    # Data download script
├── activity_logger.py  # Logging module
├── models.py           # Data models
├── requirements.txt    # Dependencies
├── data/               # Database & raw data
├── logs/               # Activity logs
├── templates/          # HTML templates
└── tests/              # Pytest tests
```

## Data Source

NHS Digital Cancer Registrations 2023  
https://files.digital.nhs.uk/16/5B8561/Cancer_registrations_2023_machine_readable_files.zip

## Technology Stack
 
- **Backend**: Python 3.10+, Flask, Gunicorn
- **Database**: SQLite3
- **Data Engineering / ETL**: pandas, NumPy, openpyxl
- **Visualizations**: Plotly (interactive), Matplotlib
- **Testing & QA**: pytest (91 unit & integration tests)
- **Deployment**: Render / Docker / Procfile-ready

## Author

Created by [@ayqon](https://github.com/ayqon).

---

**OncStat v1.0** © 2025

