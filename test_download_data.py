import pytest
import os
import pandas as pd
from download_data import ZIP_PATH, EXTRACT_PATH

def test_zip_exists():
    assert os.path.exists(ZIP_PATH)

def test_extracted_files_exist():
    assert os.path.exists(EXTRACT_PATH)
    files = os.listdir(EXTRACT_PATH)
    assert len(files) >= 3
    assert "Table_2_cancer_incidence_by_icd10_2023.csv" in files

def test_csv_readable():
    # Basic check that we can read the main file
    path = os.path.join(EXTRACT_PATH, "Table_2_cancer_incidence_by_icd10_2023.csv")
    df = pd.read_csv(path, nrows=5)
    assert not df.empty
    # Validating the columns we found in our research
    expected_cols = ["icd10_code", "diagnosisyear", "gender", "age_at_diagnosis", "count"]
    for col in expected_cols:
        assert col in df.columns, f"Missing column {col}"
