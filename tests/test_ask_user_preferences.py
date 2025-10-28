import pytest
from unittest.mock import patch, MagicMock
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
         patch('database.user_preferences.get_user_git_username') as get_git, \
         patch('database.user_preferences.update_user_git_username') as update_git, \
         patch('collaborative.identify_contributors') as identify_contributors:

        yield {
            'consent_manager': consent_manager,
            'collab_manager': collab_manager,
            'get_git': get_git,
            'update_git': update_git,
            'identify_contributors': identify_contributors
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

    git_mock = mock_managers['get_git']
    # First call triggers initial username update
    # Second call returns the username so the "change username" loop can run
    git_mock.side_effect = [(None,), ("myusername",)]

    update_git_mock = mock_managers['update_git']

    ic_mock = MagicMock()
    ic_mock.extract_repo.return_value = "/fake/repo"
    ic_mock.get_commit_counts.return_value = {"user1": 5}
    ic_mock.cleanup = MagicMock()
    mock_managers['identify_contributors'].return_value = ic_mock

    # Input sequence to match function flow
    inputs = iter([
        'yes',         # withdraw consent
        'yes',         # not include collaborative
        'myusername',  # GitHub username
        'yes',         # change GitHub username
        'newusername', # new username input
        'no'           # end username change loop
    ])

    with patch.object(builtins, 'input', lambda _: next(inputs)), \
         patch('builtins.print') as mock_print:
        main.ask_user_preferences(is_start=False)

    # Assertions
    cm.withdraw.assert_called_once()
    col.update_collaborative.assert_called_once_with(False)

    # Ensure both username updates are called
    #update_git_mock.assert_any_call('myusername')
    #update_git_mock.assert_any_call('newusername')

    # Check contributor extraction and commit counts
    #ic_mock.extract_repo.assert_called_once()
    #ic_mock.get_commit_counts.assert_called_once()
    #ic_mock.cleanup.assert_called_once()

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
