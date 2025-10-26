from external_services.permission_manager import ExternalServicePermission


class AnalysisRouter:

    def __init__(self, user_id='default_user'):
        """
        Initialize the analysis router.
        
        Args:
            user_id (str): User identifier
        """
        self.user_id = user_id
        self.permission_manager = ExternalServicePermission(user_id)
    
    def should_use_external_service(self, service_name='LLM'):
        """
        Check if external service should be used for analysis.
        Sub-issue #38: Conditional logic check.
        
        Args:
            service_name (str): Name of external service
        
        Returns:
            bool: True if external service can be used
        """
        return self.permission_manager.has_permission(service_name)
    
    def get_analysis_strategy(self, analysis_type='project'):
        """
        Determine which analysis strategy to use based on permissions.
        Sub-issue #38: Route to appropriate analysis method.
        
        Args:
            analysis_type (str): Type of analysis ('project', 'skill', 'contribution')
        
        Returns:
            str: 'local' or 'enhanced' (local + external)
        """
        has_external_permission = self.should_use_external_service()
        
        if has_external_permission:
            print(f"ℹ️  Using enhanced analysis (local + external) for {analysis_type}")
            return 'enhanced'
        else:
            print(f"ℹ️  Using local analysis only for {analysis_type}")
            return 'local'
    
    def route_analysis(self, data, analysis_type='project'):
        """
        Route analysis request to appropriate handler.
        This is the main entry point that implements the conditional logic.
        
        Sub-issue #38: Main routing method.
        
        Args:
            data: Data to analyze (file paths, project info, etc.)
            analysis_type (str): Type of analysis needed
        
        Returns:
            dict: Analysis results with metadata about which method was used
        """
        strategy = self.get_analysis_strategy(analysis_type)
        
        # This will be implemented in future PRs
        # For now, we're just setting up the routing logic
        result = {
            'strategy_used': strategy,
            'analysis_type': analysis_type,
            'data': data,
            'status': 'routed'
        }
        
        return result