# tests/test_user_preferences.py

import pytest
from database.user_preferences import (
    init_user_preferences_table,
    update_user_preferences,
    get_user_preferences
)

def test_preferences_table_create_and_update():
    # Ensure table is created
    init_user_preferences_table()

    # Update preference
    update_user_preferences(True)
    prefs = get_user_preferences()
    assert prefs is not None
    assert prefs[0] == True

    # Update again with False
    update_user_preferences(False)
    prefs = get_user_preferences()
    assert prefs[0] == False
