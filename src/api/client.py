"""API client for making HTTP requests to the Artifact API."""
import os
import httpx
from typing import Optional, Dict, List, Any


class APIClient:
    """Client for interacting with the Artifact API."""

    @staticmethod
    def _format_api_error(response: httpx.Response, fallback: str) -> str:
        """
        Format API error responses into a readable message.
        Supports unified API errors:
        {success:false, error_type, message, data?}
        And legacy FastAPI style:
        {detail: "..."} or {detail: {...}}
        """
        try:
            body = response.json()
        except Exception:
            return fallback

        # Unified format
        if isinstance(body, dict) and "error_type" in body and "message" in body:
            error_type = body.get("error_type", "API_ERROR")
            message = body.get("message", "")
            return f"{error_type}: {message}"

        # Legacy detail handling
        if isinstance(body, dict) and "detail" in body:
            detail = body.get("detail")

            if isinstance(detail, dict):
                error_type = detail.get("error_type", "API_ERROR")
                message = detail.get("message", "") or str(detail)
                return f"{error_type}: {message}"

            if isinstance(detail, str):
                return f"API_ERROR: {detail}"

            return f"API_ERROR: {str(detail)}"

        return fallback

    def __init__(self, base_url: str = None):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API (defaults to http://localhost:8000)
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_prefix = "/api"

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to httpx
            
        Returns:
            dict: Response JSON data
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            msg = self._format_api_error(e.response, fallback=str(e))
            raise Exception(f"API Error: {msg}")
    
    def upload_project(self, file_path: str, user_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a project file via POST /projects/upload.
        
        Args:
            file_path: Path to the ZIP file to upload
            user_name: Optional username for the upload
            
        Returns:
            dict: Upload result with file information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        params = {}
        if user_name:
            params['user_name'] = user_name
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/zip')}
            return self._make_request('POST', '/projects/upload', files=files, params=params)
    
    def post_privacy_consent(self, consent_given: bool, user_name: str) -> Dict[str, Any]:
        """
        Store privacy consent via POST /privacy-consent.
        
        Args:
            consent_given: Whether consent is granted
            user_name: Username from user_informations table
            
        Returns:
            dict: Consent storage result
        """
        data = {
            "consent_given": consent_given,
            "user_name": user_name
        }
        return self._make_request('POST', '/privacy-consent', json=data)
    
    def get_projects(self, user_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of projects via GET /projects.
        
        Args:
            user_name: Optional username to filter projects
            
        Returns:
            dict: Response containing projects list
        """
        params = {}
        if user_name:
            params['user_name'] = user_name
        
        return self._make_request('GET', '/projects', params=params)
    
    def get_project_by_id(self, project_id: int, user_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a specific project by ID via GET /projects/{id}.
        
        Args:
            project_id: The ID of the project to retrieve
            user_name: Optional username to verify ownership
            
        Returns:
            dict: Response containing project information
        """
        params = {}
        if user_name:
            params['user_name'] = user_name
        
        return self._make_request('GET', f'/projects/{project_id}', params=params)
    
    def list_resume_custom_wording(self, user_id: str) -> Dict[str, Any]:
        return self._make_request('GET', f'/resume/{user_id}/custom-wording')

    def save_resume_custom_wording(self, user_id: str, project_id: int, wording: str) -> Dict[str, Any]:
        data = {"project_id": project_id, "wording": wording}
        return self._make_request('POST', f'/resume/{user_id}/custom-wording', json=data)

    def clear_resume_custom_wording(self, user_id: str, project_id: int) -> Dict[str, Any]:
        return self._make_request('DELETE', f'/resume/{user_id}/custom-wording/{project_id}')

    # Portfolio customization methods
    def list_portfolio_customizations(self, user_id: str) -> Dict[str, Any]:
        """List all projects with portfolio customizations."""
        return self._make_request('GET', f'/portfolio/{user_id}/custom-data')

    def save_portfolio_customization(self, user_id: str, project_id: int, 
                                     custom_title: str = None, 
                                     custom_description: str = None, 
                                     custom_role: str = None) -> Dict[str, Any]:
        """Save or update portfolio customization for a project."""
        data = {
            "project_id": project_id,
            "custom_title": custom_title,
            "custom_description": custom_description,
            "custom_role": custom_role
        }
        return self._make_request('POST', f'/portfolio/{user_id}/custom-data', json=data)

    def get_portfolio_customization(self, user_id: str, project_id: int) -> Dict[str, Any]:
        """Get portfolio customization for a specific project."""
        return self._make_request('GET', f'/portfolio/{user_id}/custom-data/{project_id}')

    def clear_portfolio_customization(self, user_id: str, project_id: int) -> Dict[str, Any]:
        """Clear portfolio customization for a project."""
        return self._make_request('DELETE', f'/portfolio/{user_id}/custom-data/{project_id}')



# Global client instance
_default_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """Get or create the default API client instance."""
    global _default_client
    if _default_client is None:
        _default_client = APIClient()
    return _default_client


def set_api_client(client: APIClient):
    """Set the default API client instance."""
    global _default_client
    _default_client = client
