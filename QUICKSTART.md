# 🚀 QUICKSTART Guide

## Get Running in 2 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download Data (Optional - if not already done)
```bash
python download_data.py
```

### Step 3: Load Data to Database
```bash
python etl.py
```

### Step 4: Start the Server
```bash
flask run --port 5001
```

### Step 5: Open Your Browser
Navigate to: **http://127.0.0.1:5001**

---

## 📖 Using the Dashboard

### Home Page (`/`)
- View key statistics (total records, sarcoma cases)
- See data status indicators
- Quick navigation to all features

### Filter & Explore (`/filter`)
1. Select filter criteria (ICD-10, Year, Gender, Age)
2. Toggle "Sarcoma Only" for focused analysis
3. Click "Apply Filters"
4. View results in table format

### Charts (`/dashboard`)
- **Trend Chart**: Incidence over time
- **Age Distribution**: Cases by age group
- Auto-generated using Matplotlib

### Import Data (`/import`)
1. Click "Download Data" to fetch NHS dataset
2. Click "Run ETL" to process and load
3. Or upload your own CSV/Excel/JSON file

### Manage Records (`/crud`)
- **Create**: Add new records
- **Read**: View all records
- **Update**: Edit existing records
- **Delete**: Remove records

### Export (`/export`)
- Downloads all data as CSV file
- Ready for Excel or other tools

### Activity Logs (`/logs`)
- View all user actions
- Track imports, exports, filters
- Debug any issues

---

## 🔍 Common Tasks

### Import Sample Data
```bash
# The sample_data.csv contains 30 sarcoma test records
# Upload via /import page or copy to data/raw/
```

### Run Tests
```bash
python -m pytest tests/ -v
```

### Check Logs
```bash
cat logs/app.log
```

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | Use `flask run --port 5001` |
| No data showing | Run `python etl.py` first |
| Import fails | Check file format (CSV/Excel/JSON) |
| Charts not loading | Ensure matplotlib is installed |
