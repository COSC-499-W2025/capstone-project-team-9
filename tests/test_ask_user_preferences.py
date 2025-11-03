import pytest
from unittest.mock import patch, MagicMock, ANY
import builtins
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import main

@pytest.fixture
def mock_managers():
    with patch('main.consent_manager') as consent_manager, \
         patch('main.collab_manager') as collab_manager, \
         patch('main.get_user_git_username') as get_git, \
         patch('main.update_user_git_username') as update_git, \
         patch('main.identify_contributors') as identify_contributors:

        yield {
            'consent_manager': consent_manager,
            'collab_manager': collab_manager,
            'get_git': get_git,
        }

def test_ask_user_preferences_full(mock_managers):
    cm = mock_managers['consent_manager']
    cm.has_access.return_value = True
    cm.request_consent_if_needed.return_value = True
    cm.withdraw = MagicMock()

    col = mock_managers['collab_manager']
    col.get_preferences.return_value = (True, True)
    col.request_collaborative_if_needed.return_value = True
    col.update_collaborative = MagicMock()

    # Input sequence to match function flow
    inputs = iter([
        'yes',         # withdraw consent
        'yes',         # confirm withdraw
        'yes',         # not include collaborative
        'yes',         # change GitHub username
        'myusername'   # new username input
    ])

    with patch.object(builtins, 'input', lambda _: next(inputs)), \
         patch('builtins.print') as mock_print:
        main.ask_user_preferences(is_start=False)

    # Assertions
    cm.withdraw.assert_called_once()
    col.update_collaborative.assert_called_once_with(False)

def test_ask_user_preferences_no_access(mock_managers):
    cm = mock_managers['consent_manager']
    cm.has_access.return_value = False
    cm.request_consent_if_needed.return_value = False

    col = mock_managers['collab_manager']
    col.get_preferences.return_value = None
    col.request_collaborative_if_needed.return_value = False

    git_mock = mock_managers['get_git']
    git_mock.return_value = ("user",)

    with patch.object(builtins, 'input', return_value='no'), \
         patch('builtins.print') as mock_print:
        main.ask_user_preferences(is_start=True)

    # Consent and collaborative should have been requested
    cm.request_consent_if_needed.assert_called_once()
    col.request_collaborative_if_needed.assert_called_once()
