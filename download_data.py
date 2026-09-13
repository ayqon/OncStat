"""
Data Download Module

Downloads and extracts cancer registration data from NHS Digital.

Author: Cancer Dashboard Project
Version: 1.0.0
"""

import os
import zipfile
from typing import List

import requests


# =============================================================================
# Configuration
# =============================================================================

DATA_URL = "https://files.digital.nhs.uk/16/5B8561/Cancer_registrations_2023_machine_readable_files.zip"
ZIP_PATH = "data/cancer_data.zip"
EXTRACT_PATH = "data/raw"


# =============================================================================
# Download Functions
# =============================================================================

def ensure_data_directory() -> None:
    """Create the data directory if it doesn't exist."""
    if not os.path.exists("data"):
        os.makedirs("data")


def download_zip(url: str, destination: str, force: bool = False) -> bool:
    """
    Download a file from URL to local destination.
    
    Args:
        url: Source URL to download from
        destination: Local file path to save to
        force: If True, download even if file exists
        
    Returns:
        True if download was performed, False if skipped
        
    Raises:
        requests.RequestException: If download fails
    """
    if os.path.exists(destination) and not force:
        print("Zip already exists.")
        return False
    
    print(f"Downloading from {url}...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    
    with open(destination, "wb") as f:
        f.write(response.content)
    
    print("Download complete.")
    return True


def extract_zip(zip_path: str, extract_to: str) -> List[str]:
    """
    Extract contents of a zip file.
    
    Args:
        zip_path: Path to the zip file
        extract_to: Directory to extract files to
        
    Returns:
        List of extracted file names
    """
    print(f"Extracting to {extract_to}...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        files = zip_ref.namelist()
    
    return files


def list_extracted_files(files: List[str]) -> None:
    """
    Print the list of extracted files.
    
    Args:
        files: List of file names
    """
    print("Files found in zip:")
    for file in files:
        print(f" - {file}")


# =============================================================================
# Main Pipeline
# =============================================================================

def download_and_extract() -> List[str]:
    """
    Execute the complete download and extraction pipeline.
    
    Returns:
        List of extracted file names
    """
    # Ensure directories exist
    ensure_data_directory()
    
    # Download if needed
    download_zip(DATA_URL, ZIP_PATH)
    
    # Extract
    files = extract_zip(ZIP_PATH, EXTRACT_PATH)
    
    # Report results
    list_extracted_files(files)
    
    return files


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    download_and_extract()
