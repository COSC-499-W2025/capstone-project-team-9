from .service_config import ServiceConfig


class ExternalServicePermission:
    """
    Manages permissions for using external services like LLMs.
    Implements Requirement #4: Request user permission before using external services.
    """
    
    def __init__(self, user_id='default_user'):
        """
        Initialize the external service permission manager.
        
        Args:
            user_id (str): User identifier
        """
        self.user_id = user_id
        self.config = ServiceConfig()
    
    def initialize(self):
        """Initialize the external service permission system."""
        try:
            self.config.initialize_table()
            return True
        except Exception as e:
            print(f"✗ Failed to initialize external service permissions: {e}")
            return False
    
    def has_permission(self, service_name='LLM'):
        """
        Check if user has granted permission for a specific service.
        This is used by the conditional logic in analysis_router.
        
        Args:
            service_name (str): Name of the external service
        
        Returns:
            bool: True if permission granted, False otherwise
        """
        permission = self.config.get_permission(self.user_id, service_name)
        return permission if permission is not None else False