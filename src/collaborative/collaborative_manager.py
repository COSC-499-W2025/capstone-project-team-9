from .collaborative_storage import CollaborativeStorage
from .collaborative_display import CollaborativeDisplay
from .decorators import requires_collaborative

class CollaborativeManager:
    """
    Manager to handle user collaborative logic.
    """

    def __init__(self):
        CollaborativeStorage.init_table()
        self.consent, self.collaborative, self.last_updated = self.get_preferences()

    def get_preferences(self):
        prefs = CollaborativeStorage.get_preferences()
        if prefs:
            return prefs
        return False, False, None

    def request_collaborative_if_needed(self) -> bool:
        """Check and request collaborative consent if not already granted."""
        if not self.collaborative:
            granted = CollaborativeDisplay.request_collaborative()
            CollaborativeStorage.update_collaborative(granted)
            self.collaborative = granted
        return self.collaborative

    def update_consent(self, consent: bool):
        """Update consent preference."""
        CollaborativeStorage.update_consent(consent)
        self.consent = consent

    def update_collaborative(self, collaborative: bool):
        """Update collaborative preference."""
        CollaborativeStorage.update_collaborative(collaborative)
        self.collaborative = collaborative
