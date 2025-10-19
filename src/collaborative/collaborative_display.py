class CollaborativeDisplay:
    """
    Handles display and user interaction for collaborative consent requests.
    """

    @staticmethod
    def request_collaborative() -> bool:
        """Ask user for collaborative consent and return True if granted."""
        response = input("Do you grant collaborative permission? (y/n): ").strip().lower()
        return response in ('y', 'yes')

    @staticmethod
    def show_status(consent: bool, collaborative: bool):
        """Print current consent and collaborative status."""
        print(f"Consent: {'✅' if consent else '✗'}")
        print(f"Collaborative: {'✅' if collaborative else '✗'}")
