"""
NeuroScan AI - Source Package
This file initializes the src directory as a Python package and 
exposes key components for easier access across the application.
"""

from .database import DatabaseManager
from .auth import (
    hash_password, 
    verify_password, 
    create_token, 
    validate_session
)
from .inference import MedicalEngine, BrainTumorClassifier, TumorSizeCalculator
from .utils import (
    validate_image, 
    medical_header, 
    logger, 
    set_page_container_style
)

# Define versioning for the package
__version__ = "1.0.0"
__author__ = "Medical AI Team"

# This ensures that when someone does 'from src import *', 
# only these specific classes/functions are exported.
__all__ = [
    'DatabaseManager',
    'hash_password',
    'verify_password',
    'create_token',
    'validate_session',
    'MedicalEngine',
    'BrainTumorClassifier',
    'TumorSizeCalculator',
    'validate_image',
    'medical_header',
    'logger',
    'set_page_container_style'
]