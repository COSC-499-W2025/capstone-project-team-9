import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from cli.user_menus import user_account_menu, handle_user_login, handle_user_logout, handle_user_registration, login_menu, get_password_input, set_password_display_mode
from account.user_manager import AuthManager
import cli.user_menus


class TestUserAccountMenu:
    """Test class for user account menu functionality"""
    
    def setup_method(self):
        """Reset the AuthManager state before each test"""
        AuthManager.clear_session()
    
    def teardown_method(self):
        """Clean up after each test"""
        AuthManager.clear_session()
    
    @patch('builtins.input', side_effect=['4'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_user_account_menu_not_logged_in(self, mock_stdout, mock_input):
        """Test user account menu when not logged in"""
        user_account_menu()
        
        output = mock_stdout.getvalue()
        assert "You are not currently logged in" in output
        assert "1. Login to existing account" in output
        assert "2. Create new account" in output
        assert "3. Password display settings" in output
        assert "4. Back to main menu" in output
    
    @patch('builtins.input', side_effect=['3'])  # Back to main menu (option 3 for logged in)
    @patch('sys.stdout', new_callable=StringIO)
    def test_user_account_menu_logged_in(self, mock_stdout, mock_input):
        """Test user account menu when logged in"""
        # Set up a logged in user
        AuthManager._current_user = {
            'user_id': 1,
            'user_name': 'testuser',
            'create_time': '2024-01-01 10:00:00',
            'last_login_time': '2024-01-01 12:00:00'
        }
        
        user_account_menu()
        
        output = mock_stdout.getvalue()
        assert "Currently logged in as: testuser" in output
        assert "User ID: 1" in output
        assert "1. Logout" in output
        assert "2. Password display settings" in output
        assert "3. Back to main menu" in output


class TestUserLoginRegistration:
    """Test user login and registration handlers"""
    
    def setup_method(self):
        """Reset the AuthManager state before each test"""
        AuthManager.clear_session()
    
    def teardown_method(self):
        """Clean up after each test"""
        AuthManager.clear_session()
    
    @patch('builtins.input', side_effect=['', ''])  # Empty username and empty "Press Enter"
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_login_empty_username(self, mock_stdout, mock_input):
        """Test login with empty username"""
        handle_user_login()
        
        output = mock_stdout.getvalue()
        assert "Username cannot be empty" in output
    
    @patch('builtins.input', side_effect=['testuser', ''])  # Username and empty "Press Enter"
    @patch('cli.user_menus.get_password_input', return_value='')  # Empty password
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_login_empty_password(self, mock_stdout, mock_password_input, mock_input):
        """Test login with empty password"""
        handle_user_login()
        
        output = mock_stdout.getvalue()
        assert "Password cannot be empty" in output
    
    @patch('builtins.input', side_effect=['', ''])  # Empty username and empty "Press Enter"
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_empty_username(self, mock_stdout, mock_input):
        """Test registration with empty username"""
        handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "Username cannot be empty" in output
    
    @patch('builtins.input', side_effect=['testuser', ''])  # Username and empty "Press Enter"
    @patch('cli.user_menus.get_password_input', return_value='')  # Empty password
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_empty_password(self, mock_stdout, mock_password_input, mock_input):
        """Test registration with empty password"""
        handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "Password cannot be empty" in output
    
    @patch('builtins.input', side_effect=['testuser', ''])  # Username and empty "Press Enter"
    @patch('cli.user_menus.get_password_input', side_effect=['password123', 'different'])  # Different passwords
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_password_mismatch(self, mock_stdout, mock_password_input, mock_input):
        """Test registration with mismatched passwords"""
        handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "Passwords do not match" in output
    
    @patch('account.user_manager.AuthManager.login')
    @patch('builtins.input', side_effect=['testuser', ''])  # Username and empty "Press Enter"
    @patch('cli.user_menus.get_password_input', return_value='password123')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_login_success(self, mock_stdout, mock_password_input, mock_input, mock_login):
        """Test successful login"""
        mock_login.return_value = {
            'success': True,
            'message': 'Login successful',
            'user_info': {'user_name': 'testuser'}
        }
        
        handle_user_login()
        
        output = mock_stdout.getvalue()
        assert "[SUCCESS] Login successful" in output
        assert "Welcome back, testuser!" in output
    
    @patch('account.user_manager.AuthManager.login')
    @patch('builtins.input', side_effect=['testuser', ''])  # Username and empty "Press Enter"
    @patch('cli.user_menus.get_password_input', return_value='wrongpassword')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_login_failure(self, mock_stdout, mock_password_input, mock_input, mock_login):
        """Test failed login"""
        mock_login.return_value = {
            'success': False,
            'message': 'Invalid username or password',
            'user_info': None
        }
        
        handle_user_login()
        
        output = mock_stdout.getvalue()
        assert "[ERROR] Invalid username or password" in output


class TestLogoutHandler:
    """Test logout handler"""
    
    def setup_method(self):
        """Reset the AuthManager state before each test"""
        AuthManager.clear_session()
    
    def teardown_method(self):
        """Clean up after each test"""
        AuthManager.clear_session()
    
    @patch('builtins.input', side_effect=['y', ''])  # Confirm logout and "Press Enter"
    @patch('account.user_manager.AuthManager.logout')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_logout_success(self, mock_stdout, mock_logout, mock_input):
        """Test successful logout"""
        # Set up logged in user
        AuthManager._current_user = {'user_name': 'testuser', 'user_id': 1}
        
        mock_logout.return_value = {
            'success': True,
            'message': 'Logout successful'
        }
        
        handle_user_logout()
        
        output = mock_stdout.getvalue()
        assert "[SUCCESS] Logout successful" in output
        assert "You have been logged out" in output
    
    @patch('builtins.input', return_value='n')  # Don't confirm logout
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_logout_cancelled(self, mock_stdout, mock_input):
        """Test cancelled logout"""
        # Set up logged in user
        AuthManager._current_user = {'user_name': 'testuser', 'user_id': 1}
        
        handle_user_logout()
        
        # Function should return without doing anything when cancelled
        # Just make sure no error occurs


class TestPasswordDisplaySettings:
    """Test password display settings functionality"""
    
    def setup_method(self):
        """Reset the AuthManager state before each test"""
        AuthManager.clear_session()
        # Reset password display setting to default
        import cli.user_menus
        cli.user_menus.SHOW_PASSWORD_AS_ASTERISK = True
    
    def teardown_method(self):
        """Clean up after each test"""
        AuthManager.clear_session()
    
    @patch('builtins.input', side_effect=['1', ''])  # Choose asterisks and press enter
    @patch('sys.stdout', new_callable=StringIO)
    def test_set_password_display_mode_asterisks(self, mock_stdout, mock_input):
        """Test setting password display to asterisks"""
        from cli.user_menus import set_password_display_mode, SHOW_PASSWORD_AS_ASTERISK
        
        set_password_display_mode()
        
        output = mock_stdout.getvalue()
        assert "Password display set to asterisks (*)" in output
        
        # Import again to check the updated value
        import cli.user_menus
        assert cli.user_menus.SHOW_PASSWORD_AS_ASTERISK is True
    
    @patch('builtins.input', side_effect=['2', ''])  # Choose visible characters and press enter
    @patch('sys.stdout', new_callable=StringIO)
    def test_set_password_display_mode_visible(self, mock_stdout, mock_input):
        """Test setting password display to visible characters"""
        from cli.user_menus import set_password_display_mode
        
        set_password_display_mode()
        
        output = mock_stdout.getvalue()
        assert "Password display set to visible characters" in output
        
        # Import again to check the updated value
        import cli.user_menus
        assert cli.user_menus.SHOW_PASSWORD_AS_ASTERISK is False
    
    @patch('builtins.input', side_effect=['3', ''])  # Keep current setting and press enter
    @patch('sys.stdout', new_callable=StringIO)
    def test_set_password_display_mode_keep_current(self, mock_stdout, mock_input):
        """Test keeping current password display setting"""
        from cli.user_menus import set_password_display_mode
        
        set_password_display_mode()
        
        output = mock_stdout.getvalue()
        assert "Keeping current setting" in output
    
    @patch('builtins.input', side_effect=['invalid', '3', ''])  # Invalid then keep current
    @patch('sys.stdout', new_callable=StringIO)
    def test_set_password_display_mode_invalid_choice(self, mock_stdout, mock_input):
        """Test invalid choice in password display settings"""
        from cli.user_menus import set_password_display_mode
        
        set_password_display_mode()
        
        output = mock_stdout.getvalue()
        assert "Invalid choice. Keeping current setting." in output


class TestPasswordInput:
    """Test the custom password input functionality"""
    
    def test_get_password_input_asterisks(self):
        """Test password input with asterisks (cross-platform)"""
        from cli.user_menus import get_password_input
        
        # Try Windows path first
        try:
            import msvcrt
            # Windows - test with mocked msvcrt.getch
            with patch('msvcrt.getch', side_effect=[b'a', b'b', b'c', b'\r']):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    password = get_password_input("Test: ", show_asterisk=True)
                    
                assert password == "abc"
                output = mock_stdout.getvalue()
                assert "Test: ***" in output  # Should show three asterisks
                
        except ImportError:
            # Linux/Mac - test termios fallback behavior
            with patch('sys.stdin.read', side_effect=['a', 'b', 'c', '\r']):
                try:
                    with patch('termios.tcgetattr'), patch('termios.tcsetattr'), patch('tty.setraw'):
                        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                            password = get_password_input("Test: ", show_asterisk=True)
                            
                        assert password == "abc"
                        output = mock_stdout.getvalue()
                        assert "Test: ***" in output  # Should show three asterisks
                except ImportError:
                    # If termios not available, skip the detailed test
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        password = get_password_input("Test: ", show_asterisk=True)
                        
                    assert password == "abc"
    
    def test_get_password_input_visible(self):
        """Test password input with visible characters (cross-platform)"""
        from cli.user_menus import get_password_input
        
        # Try Windows path first
        try:
            import msvcrt
            # Windows - test with mocked msvcrt.getch
            with patch('msvcrt.getch', side_effect=[b'a', b'b', b'c', b'\r']):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    password = get_password_input("Test: ", show_asterisk=False)
                    
                assert password == "abc"
                output = mock_stdout.getvalue()
                assert "Test: abc" in output  # Should show actual characters
                
        except ImportError:
            # Linux/Mac - test termios fallback behavior
            with patch('sys.stdin.read', side_effect=['a', 'b', 'c', '\r']):
                try:
                    with patch('termios.tcgetattr'), patch('termios.tcsetattr'), patch('tty.setraw'):
                        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                            password = get_password_input("Test: ", show_asterisk=False)
                            
                        assert password == "abc"
                        output = mock_stdout.getvalue()
                        assert "Test: abc" in output  # Should show actual characters
                except ImportError:
                    # If termios not available, skip the detailed test
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        password = get_password_input("Test: ", show_asterisk=False)
                        
                    assert password == "abc"
    
    def test_get_password_input_backspace(self):
        """Test backspace functionality in password input (cross-platform)"""
        from cli.user_menus import get_password_input
        
        # Try Windows path first
        try:
            import msvcrt
            # Windows - test with mocked msvcrt.getch with backspace sequence
            with patch('msvcrt.getch', side_effect=[b'a', b'b', b'\x08', b'c', b'\r']):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    password = get_password_input("Test: ", show_asterisk=True)
                    
                assert password == "ac"  # 'ab' with 'b' removed by backspace, then 'c'
                
        except ImportError:
            # Linux/Mac - test termios fallback with backspace (DEL key = 127)
            backspace_char = chr(127)  # DEL key on Linux
            with patch('sys.stdin.read', side_effect=['a', 'b', backspace_char, 'c', '\r']):
                try:
                    with patch('termios.tcgetattr'), patch('termios.tcsetattr'), patch('tty.setraw'):
                        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                            password = get_password_input("Test: ", show_asterisk=True)
                            
                        assert password == "ac"  # 'ab' with 'b' removed by backspace, then 'c'
                except ImportError:
                    # If termios not available, skip the detailed test
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        password = get_password_input("Test: ", show_asterisk=True)
                        
                    assert password == "abc"  # Can't test backspace without termios
    
    def test_get_password_input_keyboard_interrupt(self):
        """Test Ctrl+C handling in password input (cross-platform)"""
        from cli.user_menus import get_password_input
        
        # Try Windows path first
        try:
            import msvcrt
            # Windows - test with mocked msvcrt.getch with Ctrl+C
            with patch('msvcrt.getch', side_effect=[b'a', b'b', b'\x03']):
                with pytest.raises(KeyboardInterrupt):
                    get_password_input("Test: ", show_asterisk=True)
                    
        except ImportError:
            # Linux/Mac - test termios fallback KeyboardInterrupt behavior
            ctrl_c_char = chr(3)  # Ctrl+C
            with patch('sys.stdin.read', side_effect=['a', 'b', ctrl_c_char]):
                try:
                    with patch('termios.tcgetattr'), patch('termios.tcsetattr'), patch('tty.setraw'):
                        with pytest.raises(KeyboardInterrupt):
                            get_password_input("Test: ", show_asterisk=True)
                except ImportError:
                    # If termios not available, skip this test
                    pytest.skip("termios not available on this platform")


class TestLoginMenu:
    """Test class for login menu functionality"""
    
    def setup_method(self):
        """Reset the AuthManager state before each test"""
        AuthManager.clear_session()
    
    def teardown_method(self):
        """Clean up after each test"""
        AuthManager.clear_session()
    
    @patch('builtins.input', side_effect=['4'])  # Exit option
    @patch('sys.stdout', new_callable=StringIO)
    def test_login_menu_exit(self, mock_stdout, mock_input):
        """Test login menu exit option"""
        result = login_menu()
        
        assert result is False
        output = mock_stdout.getvalue()
        assert "MINING DIGITAL WORK ARTIFACTS - Login Required" in output
        assert "1. Login to existing account" in output
        assert "2. Create new account" in output
        assert "3. Password display settings" in output
        assert "4. Exit" in output
        assert "Goodbye!" in output
    
    @patch('account.user_manager.AuthManager.login')
    @patch('builtins.input', side_effect=['1', 'testuser', ''])  # Choose login, then username and "Press Enter"
    @patch('cli.user_menus.get_password_input', return_value='password123')
    @patch('sys.stdout', new_callable=StringIO)
    def test_login_menu_successful_login(self, mock_stdout, mock_password_input, mock_input, mock_login):
        """Test login menu with successful login"""
        # Mock successful login
        mock_login.return_value = {
            'success': True,
            'message': 'Login successful',
            'user_info': {'user_name': 'testuser'}
        }
        
        # Set up the user as logged in after successful login
        AuthManager._current_user = {
            'user_id': 1,
            'user_name': 'testuser',
            'create_time': '2024-01-01 10:00:00',
            'last_login_time': '2024-01-01 12:00:00'
        }
        
        result = login_menu()
        
        assert result is True
        output = mock_stdout.getvalue()
        assert "MINING DIGITAL WORK ARTIFACTS - Login Required" in output
        assert "[SUCCESS] Login successful" in output
    
    @patch('account.user_manager.AuthManager.register')
    @patch('account.user_manager.AuthManager.login')
    @patch('builtins.input', side_effect=['2', 'newuser', 'y', ''])  # Choose register, username, login now, Press Enter
    @patch('cli.user_menus.get_password_input', side_effect=['password123', 'password123', 'password123'])  # password, confirm, login password
    @patch('sys.stdout', new_callable=StringIO)
    def test_login_menu_successful_registration(self, mock_stdout, mock_password_input, mock_input, mock_login, mock_register):
        """Test login menu with successful registration and immediate login"""
        # Mock successful registration
        mock_register.return_value = {
            'success': True,
            'message': 'Registration successful',
            'user_id': 1
        }
        
        # Mock successful login after registration
        mock_login.return_value = {
            'success': True,
            'message': 'Login successful',
            'user_info': {'user_name': 'newuser'}
        }
        
        # Set up the user as logged in after successful registration and login
        AuthManager._current_user = {
            'user_id': 1,
            'user_name': 'newuser',
            'create_time': '2024-01-01 10:00:00',
            'last_login_time': '2024-01-01 12:00:00'
        }
        
        result = login_menu()
        
        assert result is True
        output = mock_stdout.getvalue()
        assert "MINING DIGITAL WORK ARTIFACTS - Login Required" in output
        assert "[SUCCESS] Registration successful" in output


class TestEOFHandling:
    """Test EOF handling in various functions"""
    
    def setup_method(self):
        """Reset the AuthManager state before each test"""
        AuthManager.clear_session()
    
    def teardown_method(self):
        """Clean up after each test"""
        AuthManager.clear_session()
    
    @patch('builtins.input', side_effect=EOFError())
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_login_eof_username(self, mock_stdout, mock_input):
        """Test EOFError handling during username input in login"""
        handle_user_login()
        
        output = mock_stdout.getvalue()
        assert "EOF detected. Login cancelled." in output
    
    @patch('cli.user_menus.get_password_input', side_effect=KeyboardInterrupt())
    @patch('builtins.input', side_effect=['testuser'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_login_keyboard_interrupt_password(self, mock_stdout, mock_input, mock_password):
        """Test KeyboardInterrupt handling during password input in login"""
        handle_user_login()
        
        output = mock_stdout.getvalue()
        assert "Login cancelled." in output
    
    @patch('builtins.input', side_effect=EOFError())
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_eof_username(self, mock_stdout, mock_input):
        """Test EOFError handling during username input in registration"""
        handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "EOF detected. Registration cancelled." in output
    
    @patch('cli.user_menus.get_password_input', side_effect=KeyboardInterrupt())
    @patch('builtins.input', side_effect=['testuser'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_keyboard_interrupt_password(self, mock_stdout, mock_input, mock_password):
        """Test KeyboardInterrupt handling during password input in registration"""
        handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "Registration cancelled." in output
    
    @patch('cli.user_menus.get_password_input', side_effect=[KeyboardInterrupt()])
    @patch('builtins.input', side_effect=['testuser'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_keyboard_interrupt_confirm_password(self, mock_stdout, mock_input, mock_password):
        """Test KeyboardInterrupt handling during password confirmation in registration"""
        # First password succeeds, second (confirm) raises KeyboardInterrupt
        with patch('cli.user_menus.get_password_input', side_effect=['password123', KeyboardInterrupt()]):
            handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "Registration cancelled." in output
    
    @patch('builtins.input', side_effect=EOFError())
    @patch('sys.stdout', new_callable=StringIO)
    def test_set_password_display_mode_eof(self, mock_stdout, mock_input):
        """Test EOFError handling in password display mode setting"""
        set_password_display_mode()
        
        output = mock_stdout.getvalue()
        assert "EOF detected. Keeping current setting." in output
    
    @patch('builtins.input', side_effect=EOFError())
    @patch('sys.stdout', new_callable=StringIO)
    def test_login_menu_eof(self, mock_stdout, mock_input):
        """Test EOFError handling in login menu"""
        result = login_menu()
        
        assert result is False
        output = mock_stdout.getvalue()
        assert "EOF detected. Exiting..." in output
    
    @patch('account.user_manager.AuthManager.login')
    @patch('builtins.input', side_effect=['testuser', EOFError()])
    @patch('cli.user_menus.get_password_input', return_value='password123')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_login_eof_continue_prompt(self, mock_stdout, mock_password_input, mock_input, mock_login):
        """Test EOFError handling in 'Press Enter to continue' prompt after login"""
        mock_login.return_value = {
            'success': True,
            'message': 'Login successful'
        }
        
        handle_user_login()
        
        output = mock_stdout.getvalue()
        assert "[SUCCESS] Login successful" in output
        # Should handle EOFError gracefully in the continue prompt
    
    @patch('account.user_manager.AuthManager.register')
    @patch('builtins.input', side_effect=['testuser', EOFError(), ''])  # Added empty string for Press Enter
    @patch('cli.user_menus.get_password_input', side_effect=['password123', 'password123'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_eof_login_prompt(self, mock_stdout, mock_password_input, mock_input, mock_register):
        """Test EOFError handling in 'login now' prompt after registration"""
        mock_register.return_value = {
            'success': True,
            'message': 'Registration successful',
            'user_id': 1
        }
        
        handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "[SUCCESS] Registration successful" in output
        # Should handle EOFError gracefully in the login prompt


class TestCrossPlatformPasswordInput:
    """Test password input functionality across different platforms"""
    
    def test_get_password_input_unicode_decode_error(self):
        """Test UnicodeDecodeError handling in Windows password input"""
        # Mock Windows environment
        try:
            import msvcrt
            # Test with actual msvcrt if available
            # Use a valid sequence: invalid byte (0xFF), normal char, enter
            with patch('msvcrt.getch', side_effect=[b'\xff', b'a', b'\r']):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    password = get_password_input("Test: ", show_asterisk=True)
                    
                assert password == "a"  # Invalid byte should be ignored
        except ImportError:
            # If msvcrt not available (Linux), skip this test
            pytest.skip("msvcrt not available on this platform")


class TestAdditionalEdgeCases:
    """Test additional edge cases and boundary conditions"""
    
    def setup_method(self):
        """Reset the AuthManager state before each test"""
        AuthManager.clear_session()
    
    def teardown_method(self):
        """Clean up after each test"""
        AuthManager.clear_session()
    
    def test_get_password_input_default_show_asterisk(self):
        """Test get_password_input with default show_asterisk setting"""
        # Set global setting
        cli.user_menus.SHOW_PASSWORD_AS_ASTERISK = False
        
        try:
            import msvcrt
            # Windows environment
            with patch('msvcrt.getch', side_effect=[b'a', b'b', b'\r']):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    password = get_password_input("Test: ")  # No show_asterisk parameter
                    
                assert password == "ab"
                output = mock_stdout.getvalue()
                assert "Test: ab" in output  # Should show actual characters
        except ImportError:
            # Linux/Unix environment - test the Unix code path
            with patch('sys.stdin.read', side_effect=['a', 'b', '\r']):
                try:
                    with patch('termios.tcgetattr'), patch('termios.tcsetattr'), patch('tty.setraw'):
                        with patch('sys.stdin.isatty', return_value=True):
                            with patch('sys.stdin.fileno', return_value=0):
                                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                                    password = get_password_input("Test: ")
                                    
                                assert password == "ab"
                except ImportError:
                    # If termios is also not available, test the fallback path
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        password = get_password_input("Test: ")
                        
                    assert password == "ab"
        finally:
            # Reset global setting
            cli.user_menus.SHOW_PASSWORD_AS_ASTERISK = True
    
    @patch('account.user_manager.AuthManager.register')
    @patch('account.user_manager.AuthManager.login')
    @patch('builtins.input', side_effect=['testuser', 'yes', ''])
    @patch('cli.user_menus.get_password_input', side_effect=['password123', 'password123'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_success_with_immediate_login(self, mock_stdout, mock_password_input, mock_input, mock_login, mock_register):
        """Test successful registration with immediate login"""
        mock_register.return_value = {
            'success': True,
            'message': 'Registration successful',
            'user_id': 1
        }
        
        mock_login.return_value = {
            'success': True,
            'message': 'Login successful'
        }
        
        handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "[SUCCESS] Registration successful" in output
        assert "[SUCCESS] Login successful" in output
        assert "Welcome, testuser!" in output
    
    @patch('account.user_manager.AuthManager.register')
    @patch('builtins.input', side_effect=['testuser', ''])
    @patch('cli.user_menus.get_password_input', side_effect=['password123', 'password123'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_registration_failure(self, mock_stdout, mock_password_input, mock_input, mock_register):
        """Test failed registration"""
        mock_register.return_value = {
            'success': False,
            'message': 'Username already exists'
        }
        
        handle_user_registration()
        
        output = mock_stdout.getvalue()
        assert "[ERROR] Username already exists" in output
    
    @patch('account.user_manager.AuthManager.logout')
    @patch('builtins.input', side_effect=['yes', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_user_logout_failure(self, mock_stdout, mock_input, mock_logout):
        """Test failed logout"""
        # Set up logged in user
        AuthManager._current_user = {'user_name': 'testuser', 'user_id': 1}
        
        mock_logout.return_value = {
            'success': False,
            'message': 'Logout failed'
        }
        
        handle_user_logout()
        
        output = mock_stdout.getvalue()
        assert "[ERROR] Logout failed" in output
    
    @patch('builtins.input', side_effect=['invalid', '4'])  # Invalid choice then exit
    @patch('sys.stdout', new_callable=StringIO)
    def test_user_account_menu_invalid_choice_not_logged_in(self, mock_stdout, mock_input):
        """Test invalid menu choice when not logged in"""
        user_account_menu()
        
        output = mock_stdout.getvalue()
        assert "Invalid choice. Please enter 1, 2, 3, or 4." in output
    
    @patch('builtins.input', side_effect=['invalid', '3'])  # Invalid then exit
    @patch('sys.stdout', new_callable=StringIO)
    def test_user_account_menu_invalid_choice_logged_in(self, mock_stdout, mock_input):
        """Test invalid menu choice when logged in"""
        # Set up logged in user
        AuthManager._current_user = {
            'user_id': 1,
            'user_name': 'testuser',
            'create_time': '2024-01-01 10:00:00',
            'last_login_time': '2024-01-01 12:00:00'
        }
        
        user_account_menu()
        
        output = mock_stdout.getvalue()
        assert "Invalid choice. Please enter 1, 2, or 3." in output
    
    @patch('builtins.input', side_effect=['invalid', '4'])  # Invalid then exit
    @patch('sys.stdout', new_callable=StringIO)
    def test_login_menu_invalid_choice(self, mock_stdout, mock_input):
        """Test invalid choice in login menu"""
        result = login_menu()
        
        assert result is False
        output = mock_stdout.getvalue()
        assert "Invalid choice. Please enter 1-4." in output


if __name__ == '__main__':
    pytest.main([__file__])