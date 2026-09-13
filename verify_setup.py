import os
import pandas as pd
from download_data import ZIP_PATH, EXTRACT_PATH

def run_checks():
    print("Checking Zip...")
    if not os.path.exists(ZIP_PATH):
        raise Exception("Zip missing")
    
    print("Checking Extract...")
    if not os.path.exists(EXTRACT_PATH):
        raise Exception("Extract path missing")
    
    files = os.listdir(EXTRACT_PATH)
    if "Table_2_cancer_incidence_by_icd10_2023.csv" not in files:
        raise Exception("Target CSV missing")
    
    print("Checking CSV columns...")
    path = os.path.join(EXTRACT_PATH, "Table_2_cancer_incidence_by_icd10_2023.csv")
    df = pd.read_csv(path, nrows=5)
    
    expected_cols = ["icd10_code", "diagnosisyear", "gender", "age_at_diagnosis", "count"]
    for col in expected_cols:
        if col not in df.columns:
            raise Exception(f"Missing column {col}")
            
    print("All checks passed!")

if __name__ == "__main__":
    run_checks()
