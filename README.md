# OncStat - Public Health Cancer Data Insights Dashboard

**Version 1.0 | 2025**

A Flask-based dashboard for analysing UK Cancer Registration data with focus on Sarcoma (ICD-10 C49, C40-C41).

## Features

- 📊 **Dashboard** - Card-based statistics overview
- 📥 **Import Data** - Download from NHS or upload custom files (CSV/Excel/JSON)
- 🔍 **Filter & Explore** - Search by ICD-10, Year, Age, Gender
- 📈 **Charts** - Matplotlib visualizations (trends, age distribution)
- 📝 **CRUD** - Create, Read, Update, Delete records
- 💾 **Export** - Download filtered data as CSV
- 📜 **Activity Logs** - View all user actions

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

- **Backend**: Python 3.10+, Flask
- **Database**: SQLite
- **Data Processing**: pandas
- **Charts**: Matplotlib
- **Testing**: pytest

## License

For educational purposes.

---

**OncStat v1.0** © 2025
