"""Authentication endpoints for user login/logout."""
from fastapi import APIRouter, HTTPException, status
from api.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    RegisterRequest,
    RegisterResponse,
    UserInfo,
)
from database.user_informations import (
    verify_password,
    login_user,
    logout_user,
    get_user_by_username,
)
from account.user_manager import AuthManager

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user with username and password.

    Returns user information on success.
    Failures raise HTTPException and are normalized by global handlers.
    """
    username = (request.username or "").strip()
    password = request.password

    # Validate input
    if not username:
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "VALIDATION_ERROR",
                "message": "Username cannot be empty",
            },
        )

    if not password:
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "VALIDATION_ERROR",
                "message": "Password cannot be empty",
            },
        )

    # Attempt login (route-level behavior uses DB auth helpers directly)
    if not login_user(username, password):
        raise HTTPException(
            status_code=401,
            detail={
                "error_type": "INVALID_CREDENTIALS",
                "message": "Invalid username or password",
            },
        )

    # Fetch user info after login and keep AuthManager in sync
    user_data = get_user_by_username(username)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail={
                "error_type": "USER_INFO_MISSING",
                "message": "Login succeeded but user information could not be retrieved",
            },
        )

    # Sync the server-side session so AuthManager.get_current_username() works
    AuthManager._current_user = user_data

    user_info = UserInfo(
        user_id=user_data["user_id"],
        user_name=user_data["user_name"],
        create_time=user_data.get("create_time"),
        last_login_time=user_data.get("last_login_time"),
        is_login=user_data.get("is_login", True),
    )

    return LoginResponse(success=True, message="Login successful", user=user_info)


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    Creates a new user with the provided username and password.
    Password must be at least 6 characters long.
    """
    username = request.username.strip()
    password = request.password
    
    # Validate input
    if not username:
        return RegisterResponse(
            success=False,
            message="Username cannot be empty",
            user_id=None
        )
    
    if not password or len(password) < 6:
        return RegisterResponse(
            success=False,
            message="Password must be at least 6 characters long",
            user_id=None
        )
    
    # Use AuthManager to register the user
    result = AuthManager.register(username, password)
    
    return RegisterResponse(
        success=result['success'],
        message=result['message'],
        user_id=result.get('user_id')
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(request: LogoutRequest):
    """
    Logout a user by username.

    Updates the login status in the database.
    Failures raise HTTPException and are normalized by global handlers.
    """
    username = (request.username or "").strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "VALIDATION_ERROR",
                "message": "Username cannot be empty",
            },
        )

    user_data = get_user_by_username(username)
    if not user_data:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "USER_NOT_FOUND",
                "message": f"User '{username}' not found",
            },
        )

    if not user_data.get("is_login", False):
        raise HTTPException(
            status_code=409,
            detail={
                "error_type": "NOT_LOGGED_IN",
                "message": f"User '{username}' is not currently logged in",
            },
        )

    if not logout_user(username):
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "LOGOUT_FAILED",
                "message": "Logout failed, user may not exist or is not logged in",
            },
        )
    # Keep AuthManager in sync for CLI/local session tracking.
    AuthManager.clear_session()
    return LogoutResponse(success=True, message="Logout successful")


@router.get("/me", response_model=LoginResponse)
async def get_current_user(username: str):
    """
    Get current user information by username.

    This is a simple endpoint that checks if a user exists and is logged in.
    For proper session management, JWT tokens should be implemented in a future PR.
    """
    username_clean = (username or "").strip()
    if not username_clean:
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "VALIDATION_ERROR",
                "message": "Username parameter is required",
            },
        )

    user_data = get_user_by_username(username_clean)
    if not user_data:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "USER_NOT_FOUND",
                "message": "User not found",
            },
        )

    if not user_data.get("is_login", False):
        raise HTTPException(
            status_code=401,
            detail={
                "error_type": "NOT_LOGGED_IN",
                "message": "User is not logged in",
            },
        )

    # Re-hydrate server-side session on page reload / session check
    AuthManager._current_user = user_data

    user_info = UserInfo(
        user_id=user_data["user_id"],
        user_name=user_data["user_name"],
        create_time=user_data.get("create_time"),
        last_login_time=user_data.get("last_login_time"),
        is_login=user_data.get("is_login", False),
    )

    return LoginResponse(success=True, message="User is authenticated", user=user_info)