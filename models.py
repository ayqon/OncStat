"""
Data Models

Defines data structures and model classes for the cancer registry dashboard.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


# =============================================================================
# Constants
# =============================================================================

# Sarcoma ICD-10 codes
SARCOMA_CODES = ('C49', 'C40', 'C41')

# Valid sex values
VALID_SEX_VALUES = ('M', 'F', 'Unknown')

# Age groups for analysis
AGE_GROUPS = [
    (0, 18, '0-18'),
    (19, 35, '19-35'),
    (36, 50, '36-50'),
    (51, 65, '51-65'),
    (66, 120, '65+'),
]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class CancerRegistration:
    """
    Represents a single cancer registration record.
    
    Attributes:
        id: Unique identifier (auto-generated)
        patient_id: Unique patient identifier
        icd10_code: ICD-10 disease classification code
        age_at_diagnosis: Patient's age at diagnosis
        sex: Patient's sex (M/F/Unknown)
        region: Geographic region
        registration_date: Date of registration
        year: Year of registration
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    icd10_code: str
    id: Optional[int] = None
    patient_id: Optional[str] = None
    age_at_diagnosis: Optional[int] = None
    sex: Optional[str] = 'Unknown'
    region: Optional[str] = None
    registration_date: Optional[str] = None
    year: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def is_sarcoma(self) -> bool:
        """Check if this registration is a sarcoma case."""
        if not self.icd10_code:
            return False
        code_upper = str(self.icd10_code).upper()
        return any(code_upper.startswith(prefix) for prefix in SARCOMA_CODES)
    
    @property
    def age_group(self) -> str:
        """Get the age group for this patient."""
        if self.age_at_diagnosis is None:
            return 'Unknown'
        
        for min_age, max_age, label in AGE_GROUPS:
            if min_age <= self.age_at_diagnosis <= max_age:
                return label
        
        return 'Unknown'
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        return {
            'patient_id': self.patient_id,
            'icd10_code': self.icd10_code,
            'age_at_diagnosis': self.age_at_diagnosis,
            'sex': self.sex,
            'region': self.region,
            'registration_date': self.registration_date,
            'year': self.year,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CancerRegistration':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id'),
            patient_id=data.get('patient_id'),
            icd10_code=data.get('icd10_code'),
            age_at_diagnosis=data.get('age_at_diagnosis'),
            sex=data.get('sex', 'Unknown'),
            region=data.get('region'),
            registration_date=data.get('registration_date'),
            year=data.get('year'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )


@dataclass
class SummaryStats:
    """
    Holds summary statistics for analysis.
    """
    total_cases: int = 0
    male_count: int = 0
    female_count: int = 0
    unknown_count: int = 0
    sarcoma_count: int = 0
    unique_regions: int = 0
    year_range: tuple = (0, 0)
    
    @property
    def gender_breakdown(self) -> dict:
        """Get gender breakdown as dictionary."""
        return {
            'M': self.male_count,
            'F': self.female_count,
            'Unknown': self.unknown_count
        }


# =============================================================================
# ICD-10 Lookup
# =============================================================================

ICD10_DESCRIPTIONS = {
    'C49': 'Malignant neoplasm of connective and soft tissue',
    'C49.0': 'Connective and soft tissue of head, face and neck',
    'C49.1': 'Connective and soft tissue of upper limb',
    'C49.2': 'Connective and soft tissue of lower limb',
    'C49.3': 'Connective and soft tissue of thorax',
    'C49.4': 'Connective and soft tissue of abdomen',
    'C49.5': 'Connective and soft tissue of pelvis',
    'C49.6': 'Connective and soft tissue of trunk, unspecified',
    'C49.8': 'Overlapping lesion of connective and soft tissue',
    'C49.9': 'Connective and soft tissue, unspecified',
    'C40': 'Malignant neoplasm of bone and articular cartilage of limbs',
    'C40.0': 'Scapula and long bones of upper limb',
    'C40.1': 'Short bones of upper limb',
    'C40.2': 'Long bones of lower limb',
    'C40.3': 'Short bones of lower limb',
    'C41': 'Malignant neoplasm of bone and articular cartilage of other sites',
    'C41.0': 'Bones of skull and face',
    'C41.1': 'Mandible',
    'C41.2': 'Vertebral column',
    'C41.3': 'Ribs, sternum and clavicle',
    'C41.4': 'Pelvic bones, sacrum and coccyx',
}


def get_icd10_description(code: str) -> str:
    """Get description for an ICD-10 code."""
    if not code:
        return 'Unknown'
    
    # Try exact match first
    if code in ICD10_DESCRIPTIONS:
        return ICD10_DESCRIPTIONS[code]
    
    # Try prefix match (e.g., C49.1 → C49)
    prefix = code.split('.')[0]
    return ICD10_DESCRIPTIONS.get(prefix, 'Other cancer type')
