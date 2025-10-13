"""
Consent module for managing user data access permissions.
Implements Requirement #1 with all 3 sub-issues.
"""

from consent.consent_manager import ConsentManager, requires_consent
from consent.consent_display import ConsentDisplay
from consent.consent_storage import ConsentStorage

__all__ = [
    'ConsentManager',
    'ConsentDisplay', 
    'ConsentStorage',
    'requires_consent'
]