"""
Module for displaying consent information to users.
Handles the presentation of data access terms and conditions.
Sub-issue #11: Define the consent scope
"""

class ConsentDisplay:
    """Handles the display of consent information and terms."""
    
    @staticmethod
    def show_consent_message():
        """
        Display detailed consent information to the user.
        Sub-issue #11: Define the consent scope
        """
        consent_text = """
╔════════════════════════════════════════════════════════════════════════╗
║                    DATA ACCESS CONSENT REQUEST                         ║
╚════════════════════════════════════════════════════════════════════════╝

This application requires access to your digital work artifacts to analyze
and generate insights about your projects and contributions.

┌─ WHAT DATA WILL BE ACCESSED ─────────────────────────────────────────┐
│                                                                         │
│  • File metadata (names, paths, dates, sizes)                          │
│  • File contents from your specified project folders                   │
│  • Programming code and repositories                                   │
│  • Written documents and notes                                         │
│  • Design files and media assets                                       │
│  • Git commit history and author information (if available)            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ HOW YOUR DATA WILL BE USED ─────────────────────────────────────────┐
│                                                                         │
│  • Analyze project structure and composition                           │
│  • Extract contribution metrics and statistics                         │
│  • Identify programming languages, frameworks, and skills              │
│  • Distinguish between individual and collaborative work               │
│  • Generate portfolio summaries and résumé items                       │
│  • Store project information in a local database                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ DATA STORAGE & RETENTION ───────────────────────────────────────────┐
│                                                                         │
│  • Duration: Data is stored until you choose to delete it              │
│  • Location: Local PostgreSQL database on your system                  │
│  • Security: Data remains on your local machine                        │
│  • External Services: You will be asked separately before any          │
│    data is sent to external services (e.g., LLMs)                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ YOUR RIGHTS ────────────────────────────────────────────────────────┐
│                                                                         │
│  • You can withdraw consent at any time                                │
│  • Withdrawing consent will block access to your data                  │
│  • You can delete all stored insights and project information          │
│  • You control what folders/files are analyzed                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

⚠️  IMPORTANT: By providing consent, you acknowledge that you have read
   and understood the above information about data access and usage.

"""
        print(consent_text)
    
    @staticmethod
    def prompt_for_consent():
        """
        Prompt the user to provide or deny consent.
        Returns True if consent is granted, False otherwise.
        """
        while True:
            response = input("\nDo you consent to data access? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                print("\nConsent granted. Thank you!")
                return True
            elif response in ['no', 'n']:
                print("\nConsent denied. The application cannot proceed without consent.")
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")