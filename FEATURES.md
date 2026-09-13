# 📋 FEATURES - UK Cancer Registry Dashboard

## ✅ Complete Feature Checklist (15/15)

| # | Feature | Status | Implementation |
|---|---------|--------|----------------|
| 1 | Load data from public dataset (CSV) | ✅ | `download_data.py`, `etl.py` |
| 2 | Load data into SQLite database | ✅ | `db_utils.py`, `etl.py` |
| 3 | Handle missing/inconsistent data | ✅ | `etl.py` - `clean_count_column()` |
| 4 | Convert types (dates, numbers) | ✅ | `etl.py` - `pd.to_numeric()` |
| 5 | Create data structures (dict/list) | ✅ | `etl.py` - `df.to_dict('records')` |
| 6 | Filter by criteria (ICD-10, year, age, sex) | ✅ | `/filter` route |
| 7 | Generate summaries (mean, min, max, count) | ✅ | `/dashboard` route |
| 8 | Show trends over time | ✅ | Line chart in `/dashboard` |
| 9 | Grouped results (by region, age, year) | ✅ | Charts in `/dashboard` |
| 10 | Web UI (Flask templates) | ✅ | 7 HTML templates |
| 11 | Charts (matplotlib) | ✅ | 2 chart types |
| 12 | Tables (pandas) | ✅ | Filter results table |
| 13 | CRUD operations | ✅ | `/crud` route |
| 14 | Export CSV | ✅ | `/export` endpoint |
| 15 | Activity logging | ✅ | `logs/app.log` |

---

## 📁 Project Structure

```
cancer/
├── app.py                 # Flask application (routes, logic)
├── config.py              # Configuration settings
├── db_utils.py            # Database utilities
├── download_data.py       # Data download from NHS
├── etl.py                 # ETL pipeline
├── activity_logger.py     # Logging module
├── models.py              # Data models
├── sample_data.csv        # Test data (30 records)
├── requirements.txt       # Dependencies
├── pytest.ini             # Test configuration
├── data/
│   ├── cancer_data.db     # SQLite database
│   └── raw/               # Raw CSV files
├── logs/
│   └── app.log            # Activity log
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Dashboard
│   ├── filter.html        # Filter page
│   ├── dashboard.html     # Charts
│   ├── crud.html          # CRUD operations
│   ├── import.html        # Data import
│   └── logs.html          # Log viewer
└── tests/
    ├── conftest.py        # Pytest fixtures
    ├── test_app.py        # Route tests
    ├── test_data_cleaner.py
    ├── test_data_downloader.py
    ├── test_data_loader.py
    ├── test_database.py
    └── test_activity_logger.py
```

---

## 🚀 API Endpoints (25 Total)

### Page Routes (7)
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Dashboard home |
| `/filter` | GET/POST | Filter interface |
| `/dashboard` | GET | Charts page |
| `/crud` | GET/POST | CRUD operations |
| `/import` | GET/POST | Data import |
| `/export` | GET | CSV download |
| `/logs` | GET | Activity logs |

### API Endpoints
| Route | Method | Description |
|-------|--------|-------------|
| `/api/summary` | GET | Summary statistics |
| `/api/filter` | GET | Filtered data |
| `/api/chart/age` | GET | Age chart |
| `/api/chart/trend` | GET | Trend chart |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_database.py -v

# Run with coverage
python -m pytest tests/ --cov=.
```

---

## 📊 Data Flow

```
NHS Digital ZIP → download_data.py → Extract CSV
       ↓
CSV File → etl.py → Clean & Transform
       ↓
DataFrame → df.to_dict('records') → List of Dicts
       ↓
SQLite DB → db_utils.py → CRUD Operations
       ↓
Flask App → templates/ → Web UI
```

---

## 🔧 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download data
python download_data.py

# 3. Run ETL
python etl.py

# 4. Start server
flask run --port 5001

# 5. Open browser
# http://127.0.0.1:5001
```
