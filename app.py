"""
Cancer Data Dashboard - Flask Application

A web-based dashboard for analysing UK Cancer Registration data
with focus on Sarcoma (ICD-10 C49, C40-C41).

Author: Cancer Dashboard Project
Version: 1.0.0
"""

import os
import logging
import sqlite3
import subprocess
from typing import Optional, Tuple, List, Dict, Any

import pandas as pd
from flask import Flask, render_template, g, request, redirect, url_for, Response

from db_utils import get_db_connection, init_db
from download_data import download_and_extract
from etl import run_etl
from bysite_loader import run_bysite_etl, get_bysite_summary


# =============================================================================
# Application Configuration
# =============================================================================

app = Flask(__name__)

# =============================================================================
# Auto-initialization (runs on startup)
# =============================================================================

# Create required directories
for directory in ['logs', 'data', 'data/raw']:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Initialize database schema
init_db()

# Configure logging (clean format without absolute system paths)
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)


# =============================================================================
# Database Connection Management
# =============================================================================

@app.before_request
def before_request() -> None:
    """Open database connection before each request."""
    g.db = get_db_connection()


@app.teardown_request
def teardown_request(exception: Optional[Exception]) -> None:
    """Close database connection after each request."""
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# =============================================================================
# Helper Functions - Data Processing
# =============================================================================

def is_sarcoma(icd10_code: str) -> bool:
    """
    Check if an ICD-10 code represents a sarcoma.
    
    Args:
        icd10_code: ICD-10 classification code
        
    Returns:
        True if code is for soft tissue sarcoma (C49) or bone sarcoma (C40-C41)
    """
    if not isinstance(icd10_code, str):
        return False
    code = icd10_code.upper().strip()
    return code.startswith('C49') or code.startswith('C40') or code.startswith('C41')


def get_database_stats() -> Dict[str, Any]:
    """
    Retrieve summary statistics from the database.
    
    Returns:
        Dictionary containing total_records, total_cases, cancer_types, genders, and year_range
        
    Raises:
        Exception: If database query fails
    """
    cur = g.db.execute("SELECT COUNT(*) FROM incidence")
    total_records = cur.fetchone()[0]
    
    cur = g.db.execute("SELECT SUM(count) FROM incidence")
    total_cases = cur.fetchone()[0] or 0
    
    cur = g.db.execute("SELECT COUNT(DISTINCT icd10_code) FROM incidence")
    cancer_types = cur.fetchone()[0]
    
    cur = g.db.execute("SELECT COUNT(DISTINCT gender) FROM incidence")
    genders = cur.fetchone()[0]
    
    cur = g.db.execute("SELECT MIN(diagnosis_year), MAX(diagnosis_year) FROM incidence")
    min_year, max_year = cur.fetchone()
    
    return {
        'total_records': total_records,
        'total_cases': int(total_cases),
        'cancer_types': cancer_types,
        'genders': genders,
        'year_range': f"{min_year} - {max_year}" if min_year else "N/A"
    }


def get_filter_options() -> Tuple[List[str], List[str], List[int]]:
    """
    Retrieve distinct values for filter dropdowns.
    
    Returns:
        Tuple of (genders, age_groups, years, cancer_types)
    """
    cur = g.db.execute("SELECT DISTINCT gender FROM incidence ORDER BY gender")
    genders = [row[0] for row in cur.fetchall()]
    
    cur = g.db.execute("SELECT DISTINCT age_group FROM incidence ORDER BY age_group")
    age_groups = [row[0] for row in cur.fetchall()]
    
    cur = g.db.execute("SELECT DISTINCT diagnosis_year FROM incidence ORDER BY diagnosis_year")
    years = [row[0] for row in cur.fetchall()]
    
    cur = g.db.execute("SELECT DISTINCT icd10_code FROM incidence ORDER BY icd10_code")
    cancer_types = [row[0] for row in cur.fetchall()]
    
    return genders, age_groups, years, cancer_types


def build_filter_query(filters: Dict[str, str]) -> Tuple[str, List[str]]:
    """
    Build SQL query and parameters based on filter criteria.
    
    Args:
        filters: Dictionary of filter field names to values
        
    Returns:
        Tuple of (SQL query string, list of parameters)
    """
    query = "SELECT * FROM incidence WHERE 1=1"
    params = []
    
    if filters.get('icd10'):
        query += " AND icd10_code LIKE ?"
        params.append(f"%{filters['icd10']}%")
    
    if filters.get('cancer_type'):
        query += " AND icd10_code = ?"
        params.append(filters['cancer_type'])
    
    if filters.get('gender'):
        query += " AND gender = ?"
        params.append(filters['gender'])
        
    if filters.get('year'):
        query += " AND diagnosis_year = ?"
        params.append(filters['year'])
        
    if filters.get('age_group'):
        query += " AND age_group = ?"
        params.append(filters['age_group'])
        
    if filters.get('sarcoma_only'):
        query += " AND is_sarcoma = 1"
        
    query += " LIMIT 500"  # Safety limit to prevent memory issues
    
    return query, params


def process_uploaded_file(file) -> pd.DataFrame:
    """
    Read and validate an uploaded data file.
    
    Args:
        file: Flask file upload object
        
    Returns:
        Pandas DataFrame with processed data
        
    Raises:
        ValueError: If file format is unsupported or missing required columns
    """
    import json
    
    filename = file.filename.lower()
    
    # Read file based on extension
    if filename.endswith('.csv'):
        df = pd.read_csv(file)
    elif filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file)
    elif filename.endswith('.json'):
        data = json.load(file)
        df = pd.DataFrame(data)
    else:
        raise ValueError("Unsupported file format. Use CSV, Excel, or JSON.")
    
    # Normalize column names (lowercase, no spaces)
    df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
    
    # Validate required columns
    required_columns = ['icd10_code', 'count']
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    
    return df


def prepare_dataframe_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare a DataFrame for database insertion.
    
    Adds default values for optional columns and flags sarcoma cases.
    
    Args:
        df: Raw DataFrame from file upload
        
    Returns:
        DataFrame ready for database insertion
    """
    # Handle year column variations
    if 'diagnosis_year' not in df.columns:
        df['diagnosis_year'] = df.get('year', 2023)
    
    # Handle gender column variations
    if 'gender' not in df.columns:
        df['gender'] = df.get('sex', 'Unknown')
    
    # Handle age group
    if 'age_group' not in df.columns:
        df['age_group'] = 'Unknown'
    
    # Flag sarcoma cases
    df['is_sarcoma'] = df['icd10_code'].apply(is_sarcoma)
    
    # Select only required columns for database
    return df[['icd10_code', 'diagnosis_year', 'gender', 'age_group', 'count', 'is_sarcoma']]


def run_download() -> Tuple[bool, str]:
    """
    Run the data download process.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        logging.info("Starting data download from NHS Digital")
        download_and_extract()
        logging.info("Data download completed successfully")
        return True, "Data downloaded and extracted successfully!"
    except Exception as e:
        logging.error(f"Download error: {e}")
        return False, f"Download failed: {str(e)}"


def run_etl_process() -> Tuple[bool, str]:
    """
    Run the ETL process.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        logging.info("Starting ETL process")
        run_etl()
        logging.info("ETL completed successfully")
        return True, "Data cleaned and loaded into database!"
    except Exception as e:
        logging.error(f"ETL error: {e}")
        return False, f"ETL failed: {str(e)}"


# =============================================================================
# Route Handlers - Main Pages
# =============================================================================

@app.route('/')
def index():
    """Render the home page with dataset statistics."""
    logging.info("Accessed Home Page")
    
    try:
        stats = get_database_stats()
        return render_template('index.html', stats=stats)
        
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return render_template('index.html', stats=None, error=str(e))


@app.route('/filter', methods=['GET', 'POST'])
def filter_data():
    """Render the data filter page and handle filter submissions."""
    logging.info("Accessed Filter Page")
    
    try:
        genders, age_groups, years, cancer_types = get_filter_options()
    except Exception as e:
        logging.error(f"Error loading filter options: {e}")
        return render_template('base.html', error=f"Database Error: {e}")

    results = []
    filters = {}
    
    if request.method == 'POST':
        # Collect filter values from form
        filters = {
            'icd10': request.form.get('icd10'),
            'cancer_type': request.form.get('cancer_type'),
            'gender': request.form.get('gender'),
            'year': request.form.get('year'),
            'age_group': request.form.get('age_group'),
            'sarcoma_only': request.form.get('sarcoma_only')
        }
        
        try:
            query, params = build_filter_query(filters)
            cur = g.db.execute(query, params)
            results = cur.fetchall()
            logging.info(f"Filter returned {len(results)} rows")
            
        except Exception as e:
            logging.error(f"Filter Query Error: {e}")
            return render_template(
                'filter.html', 
                error=str(e), 
                genders=genders, 
                age_groups=age_groups, 
                years=years,
                cancer_types=cancer_types
            )

    return render_template(
        'filter.html', 
        results=results, 
        filters=filters, 
        genders=genders, 
        age_groups=age_groups, 
        years=years,
        cancer_types=cancer_types
    )


@app.route('/dashboard')
def dashboard():
    """Render the charts and visualization page with Plotly interactive charts."""
    logging.info("Accessed Dashboard Page")
    
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Color scheme matching the app theme
    COLORS = ['#0d4f4f', '#1a6363', '#2d7878', '#408d8d', '#53a2a2', 
              '#66b7b7', '#79cccc', '#c5f0d5', '#a8e6cf', '#88d8b0']
    
    try:
        # Load all data for analysis
        df = pd.read_sql("SELECT * FROM incidence", g.db)
        
        if len(df) == 0:
            return render_template('base.html', error="No data available. Please import data first.")
        
        # =====================================================================
        # Chart 1: Top 10 Cancer Types by Total Count
        # =====================================================================
        cancer_counts = df.groupby('icd10_code')['count'].sum().sort_values(ascending=True).tail(10)
        
        fig1 = go.Figure(go.Bar(
            x=cancer_counts.values,
            y=[str(x)[:35] for x in cancer_counts.index],
            orientation='h',
            marker_color=COLORS[:len(cancer_counts)],
            text=[f'{int(v):,}' for v in cancer_counts.values],
            textposition='outside'
        ))
        fig1.update_layout(
            title='Top 10 Cancer Types by Total Cases',
            xaxis_title='Total Cases',
            yaxis_title='',
            template='plotly_white',
            height=450,
            margin=dict(l=200)
        )
        chart_top_cancers = fig1.to_html(full_html=False, include_plotlyjs='cdn')
        
        # =====================================================================
        # Chart 2: Trend Over Time (All Cancer Types)
        # =====================================================================
        trend = df.groupby('diagnosis_year')['count'].sum().reset_index()
        
        fig2 = px.area(trend, x='diagnosis_year', y='count',
                       title='Cancer Incidence Trend Over Time',
                       labels={'diagnosis_year': 'Year', 'count': 'Total Cases'},
                       color_discrete_sequence=['#0d4f4f'])
        fig2.update_traces(line=dict(width=3))
        fig2.update_layout(template='plotly_white', height=400)
        chart_trend = fig2.to_html(full_html=False, include_plotlyjs=False)
        
        # =====================================================================
        # Chart 3: Gender Distribution (Pie)
        # =====================================================================
        gender_dist = df.groupby('gender')['count'].sum().reset_index()
        
        fig3 = px.pie(gender_dist, values='count', names='gender',
                      title='Cases by Gender',
                      color_discrete_sequence=COLORS,
                      hole=0.4)
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        fig3.update_layout(template='plotly_white', height=400)
        chart_gender = fig3.to_html(full_html=False, include_plotlyjs=False)
        
        # =====================================================================
        # Chart 4: Cases by Year and Gender (Stacked Bar)
        # =====================================================================
        year_gender = df.groupby(['diagnosis_year', 'gender'])['count'].sum().reset_index()
        
        fig4 = px.bar(year_gender, x='diagnosis_year', y='count', color='gender',
                      title='Cases by Year and Gender',
                      labels={'diagnosis_year': 'Year', 'count': 'Cases', 'gender': 'Gender'},
                      color_discrete_sequence=COLORS)
        fig4.update_layout(template='plotly_white', height=400, barmode='stack')
        chart_year_gender = fig4.to_html(full_html=False, include_plotlyjs=False)

        # Summary statistics
        stats = {
            'total_cases': int(df['count'].sum()),
            'cancer_types': df['icd10_code'].nunique(),
            'year_range': f"{df['diagnosis_year'].min()}-{df['diagnosis_year'].max()}",
            'top_cancer': cancer_counts.index[-1] if len(cancer_counts) > 0 else 'N/A'
        }
        
        return render_template(
            'dashboard.html', 
            chart_trend=chart_trend, 
            chart_top_cancers=chart_top_cancers,
            chart_gender=chart_gender,
            chart_year_gender=chart_year_gender,
            stats=stats
        )
        
    except Exception as e:
        logging.error(f"Dashboard Error: {e}")
        return render_template('base.html', error=f"Error generating dashboard: {e}")


# =============================================================================
# Route Handlers - CRUD Operations
# =============================================================================

@app.route('/crud', methods=['GET', 'POST'])
def crud():
    """Handle Create, Read, Update, Delete operations on records."""
    logging.info("Accessed CRUD Page")
    
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'create':
                _handle_create_record()
            elif action == 'delete':
                _handle_delete_record()
            elif action == 'update':
                _handle_update_record()
                
            return redirect(url_for('crud', page=request.args.get('page', 1)))

        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 50  # Records per page
        offset = (page - 1) * per_page
        
        # Get total count
        cur = g.db.execute("SELECT COUNT(*) FROM incidence")
        total_records = cur.fetchone()[0]
        total_pages = (total_records + per_page - 1) // per_page if total_records > 0 else 1
        
        # GET: Display paginated records
        cur = g.db.execute(
            "SELECT * FROM incidence ORDER BY id LIMIT ? OFFSET ?", 
            (per_page, offset)
        )
        records = cur.fetchall()
        
        return render_template(
            'crud.html', 
            records=records,
            page=page,
            total_pages=total_pages,
            total_records=total_records,
            per_page=per_page
        )
        
    except Exception as e:
        logging.error(f"CRUD Error: {e}")
        return render_template('base.html', error=f"CRUD Error: {e}")


def _handle_create_record() -> None:
    """Create a new record from form data."""
    icd10 = request.form.get('icd10')
    year = request.form.get('year')
    gender = request.form.get('gender')
    age = request.form.get('age')
    count = request.form.get('count')
    
    is_sarcoma_flag = 1 if is_sarcoma(icd10) else 0
    
    g.db.execute(
        """INSERT INTO incidence 
           (icd10_code, diagnosis_year, gender, age_group, count, is_sarcoma) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (icd10, year, gender, age, count, is_sarcoma_flag)
    )
    g.db.commit()
    logging.info(f"Created record for {icd10}")


def _handle_delete_record() -> None:
    """Delete a record by ID."""
    record_id = request.form.get('id')
    g.db.execute("DELETE FROM incidence WHERE id = ?", (record_id,))
    g.db.commit()
    logging.info(f"Deleted record {record_id}")


def _handle_update_record() -> None:
    """Update the count for a record."""
    record_id = request.form.get('id')
    count = request.form.get('count')
    g.db.execute("UPDATE incidence SET count = ? WHERE id = ?", (count, record_id))
    g.db.commit()
    logging.info(f"Updated record {record_id}")


# =============================================================================
# Route Handlers - Import & Export
# =============================================================================

@app.route('/import', methods=['GET', 'POST'])
def import_data():
    """Handle data import from CDC or NHS datasets."""
    logging.info("Accessed Import Data Page")
    
    status = None
    error = None
    current_count = _get_record_count()
    current_dataset = _get_current_dataset()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'upload_cdc':
            # Handle CDC USCS BYSITE.TXT upload
            status, error = _handle_cdc_upload()
            if status:
                _set_current_dataset("CDC USCS (1999-2022)")
        
        elif action == 'upload_nhs':
            # Handle NHS Digital CSV upload
            status, error = _handle_nhs_upload()
            if status:
                _set_current_dataset("NHS Digital (2023)")
        
        elif action == 'reset':
            success, message = _handle_reset_data()
            status = message if success else None
            error = message if not success else None
            if success:
                _set_current_dataset(None)
        
        elif action == 'load_local_cdc':
            # Load from local BYSITE.TXT
            status, error = _load_local_cdc()
            if status:
                _set_current_dataset("CDC USCS (1999-2022)")
        
        elif action == 'load_local_nhs':
            # Load from local NHS CSV
            status, error = _load_local_nhs()
            if status:
                _set_current_dataset("NHS Digital (2023)")
        
        # Refresh count after any action
        current_count = _get_record_count()
        current_dataset = _get_current_dataset()
    
    # Check if local files are available
    cdc_available = os.path.exists('data/sources/BYSITE.TXT') or os.path.exists('BYSITE.TXT')
    nhs_available = os.path.exists('data/sources/nhs_cancer_2023.csv')
    
    return render_template(
        'import.html', 
        status=status, 
        error=error, 
        current_count=current_count,
        current_dataset=current_dataset,
        cdc_available=cdc_available,
        nhs_available=nhs_available
    )


def _get_record_count() -> int:
    """Get the current number of records in the database."""
    try:
        cur = g.db.execute("SELECT COUNT(*) FROM incidence")
        return cur.fetchone()[0]
    except:
        return 0


def _handle_reset_data() -> Tuple[bool, str]:
    """
    Reset all data in the database.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        g.db.execute("DELETE FROM incidence")
        g.db.execute("DELETE FROM sqlite_sequence WHERE name='incidence'")
        g.db.commit()
        logging.info("Database reset: all records deleted")
        return True, "All data has been reset. Database is now empty."
    except Exception as e:
        logging.error(f"Reset data error: {e}")
        return False, f"Failed to reset data: {str(e)}"


# Global variable to track current dataset (simple approach)
_current_dataset = None

def _get_current_dataset() -> Optional[str]:
    """Get the name of the currently loaded dataset."""
    global _current_dataset
    return _current_dataset

def _set_current_dataset(name: Optional[str]):
    """Set the name of the currently loaded dataset."""
    global _current_dataset
    _current_dataset = name


def _load_local_cdc() -> Tuple[Optional[str], Optional[str]]:
    """Load CDC data from local BYSITE.TXT file."""
    # Try multiple locations
    filepath = None
    for path in ['data/sources/BYSITE.TXT', 'BYSITE.TXT']:
        if os.path.exists(path):
            filepath = path
            break
    
    if not filepath:
        return None, "BYSITE.TXT not found in project folder"
    
    try:
        # Clear existing data
        g.db.execute("DELETE FROM incidence")
        g.db.execute("DELETE FROM sqlite_sequence WHERE name='incidence'")
        g.db.commit()
        
        # Read the pipe-delimited file
        df = pd.read_csv(filepath, delimiter='|', dtype={'YEAR': str})
        logging.info(f"Loaded {len(df)} rows from local BYSITE.TXT")
        
        # Filter out aggregate year ranges
        df = df[~df['YEAR'].str.contains('-', na=False)]
        df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
        df = df.dropna(subset=['YEAR'])
        
        # Map to our schema
        df_insert = pd.DataFrame({
            'icd10_code': df['SITE'],
            'diagnosis_year': df['YEAR'].astype(int),
            'gender': df['SEX'],
            'age_group': 'All ages',
            'count': pd.to_numeric(df['COUNT'], errors='coerce').fillna(0).astype(int),
            'is_sarcoma': df['SITE'].str.lower().str.contains('soft tissue|bones and joints', na=False).astype(int)
        })
        
        df_insert.to_sql('incidence', g.db, if_exists='append', index=False)
        g.db.commit()
        
        return f"Successfully loaded {len(df_insert):,} records from CDC USCS data", None
        
    except Exception as e:
        logging.error(f"Local CDC load error: {e}")
        return None, f"Error loading CDC data: {str(e)}"


def _load_local_nhs() -> Tuple[Optional[str], Optional[str]]:
    """Load NHS data from local CSV file."""
    filepath = 'data/sources/nhs_cancer_2023.csv'
    
    if not os.path.exists(filepath):
        return None, f"NHS CSV not found at {filepath}. Please upload the file first."
    
    try:
        # Clear existing data
        g.db.execute("DELETE FROM incidence")
        g.db.execute("DELETE FROM sqlite_sequence WHERE name='incidence'")
        g.db.commit()
        
        # Read CSV
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        logging.info(f"Loaded {len(df)} rows from local NHS CSV")
        
        # Find columns
        icd_col = next((c for c in df.columns if 'icd' in c.lower()), None)
        year_col = next((c for c in df.columns if 'year' in c.lower()), None)
        gender_col = next((c for c in df.columns if 'sex' in c.lower() or 'gender' in c.lower()), None)
        age_col = next((c for c in df.columns if 'age' in c.lower()), None)
        count_col = next((c for c in df.columns if 'count' in c.lower() or 'registrations' in c.lower()), None)
        
        df_insert = pd.DataFrame({
            'icd10_code': df[icd_col] if icd_col else 'Unknown',
            'diagnosis_year': pd.to_numeric(df[year_col], errors='coerce').fillna(0).astype(int) if year_col else 0,
            'gender': df[gender_col] if gender_col else 'Unknown',
            'age_group': df[age_col] if age_col else 'All ages',
            'count': pd.to_numeric(df[count_col], errors='coerce').fillna(0).astype(int) if count_col else 0,
            'is_sarcoma': df[icd_col].astype(str).str.upper().str.startswith(('C49', 'C40', 'C41')).astype(int) if icd_col else 0
        })
        
        df_insert.to_sql('incidence', g.db, if_exists='append', index=False)
        g.db.commit()
        
        return f"Successfully loaded {len(df_insert):,} records from NHS Digital data", None
        
    except Exception as e:
        logging.error(f"Local NHS load error: {e}")
        return None, f"Error loading NHS data: {str(e)}"


def _handle_cdc_upload() -> Tuple[Optional[str], Optional[str]]:
    """
    Handle CDC USCS BYSITE.TXT file upload.
    
    Returns:
        Tuple of (success_message, error_message)
    """
    if 'file' not in request.files:
        return None, "No file selected"
    
    file = request.files['file']
    if file.filename == '':
        return None, "No file selected"
    
    if not file.filename.upper().endswith('.TXT'):
        return None, "Please upload a .TXT file (BYSITE.TXT)"
    
    try:
        # Clear existing data first
        g.db.execute("DELETE FROM incidence")
        g.db.execute("DELETE FROM sqlite_sequence WHERE name='incidence'")
        g.db.commit()
        
        # Read the pipe-delimited file
        import io
        content = file.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(content), delimiter='|', dtype={'YEAR': str})
        
        logging.info(f"Loaded {len(df)} rows from BYSITE.TXT")
        
        # Filter out aggregate year ranges (e.g., "2018-2022")
        df = df[~df['YEAR'].str.contains('-', na=False)]
        df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
        df = df.dropna(subset=['YEAR'])
        
        # Map to our schema
        df_insert = pd.DataFrame({
            'icd10_code': df['SITE'],
            'diagnosis_year': df['YEAR'].astype(int),
            'gender': df['SEX'],
            'age_group': 'All ages',
            'count': pd.to_numeric(df['COUNT'], errors='coerce').fillna(0).astype(int),
            'is_sarcoma': df['SITE'].str.lower().str.contains('soft tissue|bones and joints', na=False).astype(int)
        })
        
        # Insert into database
        df_insert.to_sql('incidence', g.db, if_exists='append', index=False)
        g.db.commit()
        
        logging.info(f"Inserted {len(df_insert)} CDC records")
        return f"Successfully loaded {len(df_insert):,} records from CDC USCS data", None
        
    except Exception as e:
        logging.error(f"CDC upload error: {e}")
        return None, f"Error processing CDC file: {str(e)}"


def _handle_nhs_upload() -> Tuple[Optional[str], Optional[str]]:
    """
    Handle NHS Digital CSV file upload.
    
    Returns:
        Tuple of (success_message, error_message)
    """
    if 'file' not in request.files:
        return None, "No file selected"
    
    file = request.files['file']
    if file.filename == '':
        return None, "No file selected"
    
    if not file.filename.lower().endswith('.csv'):
        return None, "Please upload a .CSV file"
    
    try:
        # Clear existing data first
        g.db.execute("DELETE FROM incidence")
        g.db.execute("DELETE FROM sqlite_sequence WHERE name='incidence'")
        g.db.commit()
        
        # Read CSV
        df = pd.read_csv(file)
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        logging.info(f"Loaded {len(df)} rows from NHS CSV, columns: {list(df.columns)}")
        
        # Find the relevant columns (NHS uses various naming)
        icd_col = next((c for c in df.columns if 'icd' in c.lower()), None)
        year_col = next((c for c in df.columns if 'year' in c.lower()), None)
        gender_col = next((c for c in df.columns if 'sex' in c.lower() or 'gender' in c.lower()), None)
        age_col = next((c for c in df.columns if 'age' in c.lower()), None)
        count_col = next((c for c in df.columns if 'count' in c.lower() or 'registrations' in c.lower()), None)
        
        if not all([icd_col, year_col]):
            return None, f"Could not find required columns. Found: {list(df.columns)}"
        
        # Map to our schema
        df_insert = pd.DataFrame({
            'icd10_code': df[icd_col] if icd_col else 'Unknown',
            'diagnosis_year': pd.to_numeric(df[year_col], errors='coerce').fillna(0).astype(int) if year_col else 0,
            'gender': df[gender_col] if gender_col else 'Unknown',
            'age_group': df[age_col] if age_col else 'All ages',
            'count': pd.to_numeric(df[count_col], errors='coerce').fillna(0).astype(int) if count_col else 0,
            'is_sarcoma': df[icd_col].astype(str).str.upper().str.startswith(('C49', 'C40', 'C41')).astype(int) if icd_col else 0
        })
        
        # Insert into database
        df_insert.to_sql('incidence', g.db, if_exists='append', index=False)
        g.db.commit()
        
        logging.info(f"Inserted {len(df_insert)} NHS records")
        return f"Successfully loaded {len(df_insert):,} records from NHS Digital data", None
        
    except Exception as e:
        logging.error(f"NHS upload error: {e}")
        return None, f"Error processing NHS file: {str(e)}"


def _handle_file_upload() -> Tuple[Optional[str], Optional[str]]:
    """
    Process an uploaded file and import data.
    
    Returns:
        Tuple of (success_message, error_message) - one will be None
    """
    if 'file' not in request.files:
        return None, "No file selected"
    
    file = request.files['file']
    if file.filename == '':
        return None, "No file selected"
    
    try:
        logging.info(f"User uploading file: {file.filename}")
        
        # Read and validate file
        df = process_uploaded_file(file)
        
        # Prepare for database
        db_df = prepare_dataframe_for_db(df)
        
        # Insert into database
        db_df.to_sql('incidence', g.db, if_exists='append', index=False)
        g.db.commit()
        
        record_count = len(db_df)
        logging.info(f"Imported {record_count} records from uploaded file")
        return f"Successfully imported {record_count} records from {file.filename}!", None
        
    except ValueError as e:
        logging.error(f"File validation error: {e}")
        return None, f"Validation error: {str(e)}"
    except Exception as e:
        logging.error(f"File import error: {e}")
        return None, f"Import error: {str(e)}"


@app.route('/export', methods=['GET', 'POST'])
def export_data():
    """Export filtered data in multiple formats (CSV, XLS, TXT, JSON)."""
    logging.info("Export page accessed")
    
    if request.method == 'GET' and not request.args.get('format') and not request.args.get('download'):
        # Show export format selection page
        try:
            genders, age_groups, years, cancer_types = get_filter_options()
            return render_template('export.html', 
                                   genders=genders, 
                                   age_groups=age_groups, 
                                   years=years,
                                   cancer_types=cancer_types)
        except:
            return render_template('export.html')
    
    # Handle export (POST or GET with format/download param)
    try:
        export_format = request.values.get('format', 'csv')
        
        # Build filter from request parameters
        filters = {
            'icd10': request.values.get('icd10', ''),
            'cancer_type': request.values.get('cancer_type', ''),
            'gender': request.values.get('gender', ''),
            'year': request.values.get('year', ''),
            'age_group': request.values.get('age_group', ''),
            'sarcoma_only': request.values.get('sarcoma_only')
        }
        
        query, params = build_filter_query(filters)
        df = pd.read_sql(query, g.db, params=params)
        
        logging.info(f"Exporting {len(df)} records as {export_format}")
        
        if export_format == 'csv':
            output = df.to_csv(index=False)
            return Response(
                output, 
                mimetype='text/csv',
                headers={"Content-Disposition": "attachment; filename=cancer_data_export.csv"}
            )
        
        elif export_format == 'json':
            output = df.to_json(orient='records', indent=2)
            return Response(
                output, 
                mimetype='application/json',
                headers={"Content-Disposition": "attachment; filename=cancer_data_export.json"}
            )
        
        elif export_format == 'txt':
            output = df.to_string(index=False)
            return Response(
                output, 
                mimetype='text/plain',
                headers={"Content-Disposition": "attachment; filename=cancer_data_export.txt"}
            )
        
        elif export_format == 'xlsx':
            import io
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return Response(
                output.getvalue(), 
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={"Content-Disposition": "attachment; filename=cancer_data_export.xlsx"}
            )
        
        else:
            return "Invalid format", 400
        
    except Exception as e:
        logging.error(f"Export Error: {e}")
        return str(e), 500


@app.route('/logs')
def view_logs():
    """Display the activity log file."""
    logging.info("Accessed Activity Logs Page")
    
    try:
        with open('logs/app.log', 'r') as f:
            lines = f.readlines()[-100:]  # Last 100 entries
        return render_template('logs.html', logs=lines)
        
    except FileNotFoundError:
        return render_template('logs.html', logs=[], error="Log file not found")
    except Exception as e:
        return render_template('logs.html', logs=[], error=str(e))


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True)
