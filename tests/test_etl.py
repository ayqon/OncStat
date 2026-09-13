"""
Test: ETL / Data Cleaning

Verifies:
- Column normalization
- Type conversion  
- Sarcoma flagging
- to_dict('records') demonstration
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
    transform_data
)


class TestSarcomaFlagging:
    """Tests for ICD-10 sarcoma detection."""
    
    def test_c49_is_sarcoma(self):
        """C49 (soft tissue) should be flagged as sarcoma."""
        assert is_sarcoma('C49') is True
        assert is_sarcoma('C49.0') is True
        assert is_sarcoma('c49') is True  # Case insensitive
    
    def test_c40_c41_is_sarcoma(self):
        """C40/C41 (bone) should be flagged as sarcoma."""
        assert is_sarcoma('C40') is True
        assert is_sarcoma('C41') is True
    
    def test_other_codes_not_sarcoma(self):
        """Other ICD-10 codes should not be sarcoma."""
        assert is_sarcoma('C50') is False
        assert is_sarcoma('C34') is False
    
    def test_non_string_returns_false(self):
        """Non-string input should return False."""
        assert is_sarcoma(None) is False
        assert is_sarcoma(123) is False


class TestColumnNormalization:
    """Tests for column name standardization."""
    
    def test_renames_diagnosisyear(self):
        """diagnosisyear should become diagnosis_year."""
        df = pd.DataFrame({'diagnosisyear': [2023], 'icd10_code': ['C49']})
        result = normalize_column_names(df)
        assert 'diagnosis_year' in result.columns
    
    def test_renames_age_at_diagnosis(self):
        """age_at_diagnosis should become age_group."""
        df = pd.DataFrame({'age_at_diagnosis': ['50-54'], 'icd10_code': ['C49']})
        result = normalize_column_names(df)
        assert 'age_group' in result.columns


class TestCountCleaning:
    """Tests for count column type conversion."""
    
    def test_converts_string_to_int(self):
        """String counts should be converted to integers."""
        df = pd.DataFrame({'count': ['100', '200']})
        result = clean_count_column(df)
        assert result['count'].dtype in ['int64', 'int32']
    
    def test_nan_becomes_zero(self):
        """NaN values should become 0."""
        df = pd.DataFrame({'count': [100, None, 200]})
        result = clean_count_column(df)
        assert result['count'].iloc[1] == 0


class TestTransformPipeline:
    """Tests for full transformation pipeline."""
    
    def test_transform_adds_sarcoma_flag(self, sample_csv):
        """Transform should add is_sarcoma column."""
        df = pd.read_csv(sample_csv)
        result = transform_data(df)
        assert 'is_sarcoma' in result.columns
    
    def test_transform_expected_columns(self, sample_csv):
        """Transform should produce expected columns."""
        df = pd.read_csv(sample_csv)
        result = transform_data(df)
        expected = ['icd10_code', 'diagnosis_year', 'gender', 'age_group', 'count', 'is_sarcoma']
        for col in expected:
            assert col in result.columns


class TestDataStructures:
    """Tests verifying list and dictionary record transformations."""
    
    def test_to_dict_records(self, sample_csv):
        """DataFrame can be converted to list of dicts."""
        df = pd.read_csv(sample_csv)
        records = df.to_dict('records')
        
        # Verify structure
        assert isinstance(records, list)
        assert len(records) > 0
        assert isinstance(records[0], dict)
        assert 'icd10_code' in records[0]
