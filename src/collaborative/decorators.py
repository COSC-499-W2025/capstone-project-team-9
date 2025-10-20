from functools import wraps
from .collaborative_storage import CollaborativeStorage

def requires_collaborative(func):
    """
    Decorator to check if collaborative consent is granted before executing function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        prefs = CollaborativeStorage.get_preferences()
        collaborative = prefs[1] if prefs else False
        if not collaborative:
            print("✗ Collaborative permission required to perform this action.")
            return None
        return func(*args, **kwargs)
    return wrapper
