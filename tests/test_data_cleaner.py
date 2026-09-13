"""
Test: Data Cleaner (ETL Transformations)

Tests data cleaning functions including:
- Column normalization
- Type conversion
- Missing value handling
- Sarcoma flagging
"""

import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl import (
    is_sarcoma,
    normalize_column_names,
    clean_count_column,
    add_sarcoma_flag,
    remove_invalid_rows,
    transform_data
)


class TestSarcomaDetection:
    """Tests for ICD-10 sarcoma classification."""
    
    def test_soft_tissue_sarcoma_c49(self):
        """C49 codes should be identified as sarcoma."""
        assert is_sarcoma('C49') is True
        assert is_sarcoma('C49.0') is True
        assert is_sarcoma('C49.9') is True
    
    def test_bone_sarcoma_c40(self):
        """C40 codes should be identified as sarcoma."""
        assert is_sarcoma('C40') is True
        assert is_sarcoma('C40.0') is True
    
    def test_bone_sarcoma_c41(self):
        """C41 codes should be identified as sarcoma."""
        assert is_sarcoma('C41') is True
    
    def test_case_insensitive(self):
        """Sarcoma detection should be case insensitive."""
        assert is_sarcoma('c49') is True
        assert is_sarcoma('C49') is True
    
    def test_non_sarcoma_codes(self):
        """Other cancer codes should not be sarcoma."""
        assert is_sarcoma('C50') is False  # Breast
        assert is_sarcoma('C34') is False  # Lung
        assert is_sarcoma('C18') is False  # Colon
    
    def test_invalid_input(self):
        """Invalid inputs should return False."""
        assert is_sarcoma(None) is False
        assert is_sarcoma(123) is False
        assert is_sarcoma('') is False


class TestColumnNormalization:
    """Tests for column name standardization."""
    
    def test_diagnosisyear_renamed(self):
        """diagnosisyear should become diagnosis_year."""
        df = pd.DataFrame({
            'icd10_code': ['C49'],
            'diagnosisyear': [2023],
            'gender': ['Male']
        })
        result = normalize_column_names(df)
        assert 'diagnosis_year' in result.columns
        assert 'diagnosisyear' not in result.columns
    
    def test_age_at_diagnosis_renamed(self):
        """age_at_diagnosis should become age_group."""
        df = pd.DataFrame({
            'icd10_code': ['C49'],
            'age_at_diagnosis': ['50-54']
        })
        result = normalize_column_names(df)
        assert 'age_group' in result.columns


class TestCountCleaning:
    """Tests for count column type conversion."""
    
    def test_string_to_integer(self):
        """String counts should convert to integers."""
        df = pd.DataFrame({'count': ['100', '200', '300']})
        result = clean_count_column(df)
        assert result['count'].dtype in ['int64', 'int32']
        assert list(result['count']) == [100, 200, 300]
    
    def test_nan_to_zero(self):
        """NaN values should become 0."""
        df = pd.DataFrame({'count': [100, None, 200]})
        result = clean_count_column(df)
        assert result['count'].iloc[1] == 0
    
    def test_non_numeric_to_zero(self):
        """Non-numeric values should become 0."""
        df = pd.DataFrame({'count': ['100', 'N/A', '200']})
        result = clean_count_column(df)
        assert result['count'].iloc[1] == 0


class TestSarcomaFlagging:
    """Tests for adding sarcoma flag column."""
    
    def test_adds_is_sarcoma_column(self):
        """Should add is_sarcoma boolean column."""
        df = pd.DataFrame({'icd10_code': ['C49', 'C50', 'C40']})
        result = add_sarcoma_flag(df)
        assert 'is_sarcoma' in result.columns
    
    def test_correct_flags(self):
        """Should correctly flag sarcoma records."""
        df = pd.DataFrame({'icd10_code': ['C49', 'C50', 'C40', 'C34']})
        result = add_sarcoma_flag(df)
        expected = [True, False, True, False]
        assert list(result['is_sarcoma']) == expected


class TestTransformPipeline:
    """Tests for complete transformation pipeline."""
    
    def test_full_transform(self, sample_csv):
        """Full transform should produce expected output."""
        df = pd.read_csv(sample_csv)
        result = transform_data(df)
        
        # Check expected columns
        expected_cols = ['icd10_code', 'diagnosis_year', 'gender', 
                        'age_group', 'count', 'is_sarcoma']
        for col in expected_cols:
            assert col in result.columns
    
    def test_transform_row_count(self, sample_csv):
        """Transform should not lose valid rows."""
        df = pd.read_csv(sample_csv)
        result = transform_data(df)
        assert len(result) > 0
