"""Resume, portfolio, and skills endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from resume.resume_manager import ResumeManager
from portfolio.portfolio_manager import PortfolioManager
from portfolio.skill_mapper import SkillMapper
from common.schemas import (
    CustomWordingSaveRequest, 
    SimpleMessageResponse,
    PortfolioCustomizationRequest,
    PortfolioCustomizationResponse,
    PortfolioCustomizationListResponse
)
from project_manager import get_project_with_analysis
from resume.item_formatter import ItemFormatter
from portfolio.portfolio_formatter import PortfolioFormatter
from common.schemas import ResumeItemResponse, PortfolioCardResponse

router = APIRouter()


class ResumeGenerateRequest(BaseModel):
    top_projects_count: Optional[int] = 5
    selected_project_ids: Optional[list[int]] = None
    include_skills: Optional[bool] = True
    skills_mode: Optional[str] = "categorized"


class ResumeEditRequest(BaseModel):
    project_id: int
    wording: str


class PortfolioGenerateRequest(BaseModel):
    top_n: Optional[int] = None


class PortfolioEditRequest(BaseModel):
    project_id: int
    custom_data: Optional[dict] = None


class PortfolioSettingsRequest(BaseModel):
    is_public: Optional[bool] = None
    show_timeline: Optional[bool] = None
    show_heatmap: Optional[bool] = None
    show_top_projects: Optional[bool] = None
    show_skills: Optional[bool] = None
    show_stats: Optional[bool] = None

@router.get("/resume/preview/{project_id}", response_model=ResumeItemResponse)
async def get_resume_preview(project_id: int):
    """
    Returns a single project formatted as a Resume Item (Bullet points).
    Used for the 'Edit Resume' modal or live preview.
    """
    # 1. Fetch Raw Data
    project_data = get_project_with_analysis(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
    user_id = project_data.get('user_name', 'default') # fallback if needed
    # Note: Ideally we pass the real user_id from auth context here
    
    user_prefs = {}
    # 3. Format & Return
    return ItemFormatter.format_resume_item(project_data, user_options=user_prefs)


@router.get("/portfolio/card/{project_id}", response_model=PortfolioCardResponse)
async def get_portfolio_card(project_id: int):
    """
    Returns a single project formatted as a Portfolio Card (Rich text/Visuals).
    Used for the main Portfolio Dashboard display.
    """
    # 1. Fetch Raw Data
    project_data = get_project_with_analysis(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Fetch User Preferences (Placeholder for future Portfolio customization)
    user_prefs = {}

    # 3. Format & Return
    # This automatically calls your new logic + Evan's evidence extractor
    return PortfolioFormatter.format_project_card(project_data, user_options=user_prefs)

@router.get("/skills")
async def get_skills(user_name: Optional[str] = Query(None)):
    """Get skills extracted from user's projects."""
    try:
        resume = ResumeManager.get_user_resume(user_name) if user_name else None
        if resume and resume.get('resume_data'):
            data = resume['resume_data']
            return {
                "success": True,
                "skills": data.get('all_skills', []),
                "categorized_skills": data.get('categorized_skills', {}),
                "languages": data.get('languages', []),
                "frameworks": data.get('frameworks', [])
            }
        return {"success": True, "skills": [], "categorized_skills": {}, "languages": [], "frameworks": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving skills: {str(e)}")


@router.get("/resume/{user_id}")
async def get_resume(user_id: str):
    """Get user's resume by ID."""
    try:
        resume = ResumeManager.get_user_resume(user_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return {"success": True, "resume": resume}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resume: {str(e)}")


@router.post("/resume/generate")
async def generate_resume(request: ResumeGenerateRequest, user_name: Optional[str] = Query(None)):
    """Generate a new resume for the user."""
    try:
        if not user_name:
            raise HTTPException(status_code=400, detail="user_name is required")
        selection = {
            "top_projects_count": request.top_projects_count,
            "selected_project_ids": request.selected_project_ids,
            "include_skills": request.include_skills,
            "skills_mode": request.skills_mode
        } if request.selected_project_ids or request.top_projects_count != 5 else None
        resume_data = ResumeManager.generate_user_resume(user_name, request.top_projects_count, selection)
        if not resume_data:
            raise HTTPException(status_code=400, detail="Failed to generate resume. Ensure projects are uploaded.")
        if ResumeManager.store_user_resume(user_name, resume_data):
            return {"success": True, "resume": resume_data}
        raise HTTPException(status_code=500, detail="Failed to store resume")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")


@router.post("/resume/{user_id}/edit")
async def edit_resume(user_id: str, request: ResumeEditRequest):
    """Edit custom wording for a project in the resume."""
    try:
        if ResumeManager.save_custom_project_wording(user_id, request.project_id, request.wording):
            return {"success": True, "message": "Resume updated"}
        raise HTTPException(status_code=500, detail="Failed to update resume")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error editing resume: {str(e)}")

@router.get("/resume/{user_id}/custom-wording")
async def list_resume_custom_wording(user_id: str):
    """List project_ids that have custom wording saved."""
    try:
        project_ids = ResumeManager.list_custom_worded_projects(user_id)
        return {"success": True, "project_ids": project_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing custom wording: {str(e)}")


@router.post("/resume/{user_id}/custom-wording")
async def save_resume_custom_wording(user_id: str, request: CustomWordingSaveRequest):
    """
    Save or overwrite custom wording for a project using a dedicated request schema.
    """
    try:
        if request.project_id <= 0:
            raise HTTPException(status_code=400, detail="project_id must be positive")

        if ResumeManager.save_custom_project_wording(user_id, request.project_id, request.wording):
            return {"success": True, "message": "Custom wording saved"}
        raise HTTPException(status_code=500, detail="Failed to save custom wording")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving custom wording: {str(e)}")


@router.delete("/resume/{user_id}/custom-wording/{project_id}")
async def clear_resume_custom_wording(user_id: str, project_id: int):
    """Clear custom wording for a project."""
    try:
        if project_id <= 0:
            raise HTTPException(status_code=400, detail="project_id must be positive")

        if ResumeManager.clear_custom_project_wording(user_id, project_id):
            return {"success": True, "message": "Custom wording cleared"}
        raise HTTPException(status_code=500, detail="Failed to clear custom wording")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing custom wording: {str(e)}")


@router.delete("/resume/{user_id}")
async def delete_resume(user_id: str):
    """Delete user's resume."""
    try:
        if ResumeManager.delete_user_resume(user_id):
            return {"success": True, "message": "Resume deleted"}
        raise HTTPException(status_code=500, detail="Failed to delete resume")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {str(e)}")


@router.get("/portfolio/public-users")
async def list_public_portfolio_users():
    """List all users who have public portfolios."""
    try:
        from database.user_informations import get_all_users
        users = get_all_users()
        public_users = []
        for user in users:
            settings = ResumeManager.get_portfolio_settings(user['user_name'])
            if settings.get('is_public', False):
                public_users.append({
                    'user_name': user['user_name'],
                    'user_id': user.get('user_id')
                })
        return {"success": True, "users": public_users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing public portfolio users: {str(e)}")


@router.get("/portfolio/public/{user_id}")
async def get_public_portfolio(user_id: str, search: Optional[str] = Query(None), skill_filter: Optional[str] = Query(None)):
    """Get public portfolio (read-only). Only available if user has set portfolio to public."""
    try:
        settings = ResumeManager.get_portfolio_settings(user_id)
        if not settings.get('is_public', False):
            raise HTTPException(status_code=403, detail="This portfolio is private")

        manager = PortfolioManager(user_id)
        result = {}

        if settings.get('show_stats', True):
            portfolio_data = manager.generate_portfolio_report()
            if 'error' not in portfolio_data:
                result['summary'] = portfolio_data.get('summary', {})
                result['skills'] = portfolio_data.get('skills', {})
                all_projects = portfolio_data.get('projects', [])

                if search:
                    search_lower = search.lower()
                    all_projects = [p for p in all_projects
                                    if search_lower in p.get('name', '').lower()
                                    or search_lower in p.get('summary', '').lower()
                                    or search_lower in p.get('primary_language', '').lower()
                                    or any(search_lower in s.lower() for s in p.get('skills', []))
                                    or any(search_lower in f.lower() for f in p.get('frameworks', []))]

                if skill_filter:
                    filter_lower = skill_filter.lower()
                    all_projects = [p for p in all_projects
                                    if any(filter_lower in s.lower() for s in p.get('skills', []))
                                    or any(filter_lower in f.lower() for f in p.get('frameworks', []))
                                    or filter_lower in p.get('primary_language', '').lower()]

                result['projects'] = all_projects

        if settings.get('show_timeline', True):
            result['timeline'] = manager.get_skills_timeline()

        if settings.get('show_heatmap', True):
            result['heatmap'] = manager.get_activity_heatmap()

        if settings.get('show_top_projects', True):
            top_projects = manager.get_top3_showcase()
            if search:
                search_lower = search.lower()
                top_projects = [p for p in top_projects
                                if search_lower in p.get('name', '').lower()
                                or search_lower in p.get('description', '').lower()]
            result['top_projects'] = top_projects

        result['settings'] = {k: v for k, v in settings.items() if k != 'updated_at'}
        result['user_name'] = user_id

        return {"success": True, "portfolio": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving public portfolio: {str(e)}")

def _get_public_settings_or_403(user_id: str) -> dict:
    settings = ResumeManager.get_portfolio_settings(user_id)
    if not settings.get('is_public', False):
        raise HTTPException(status_code=403, detail="This portfolio is private")
    return settings

def _compute_portfolio_stats(user_id: str) -> dict:
    from config.db_config import with_db_cursor
    from common.constants import LANGUAGE_EXTENSIONS

    with with_db_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM uploaded_files WHERE user_name = %s
        """, (user_id,))
        total_projects = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(fc.id),
                   COALESCE(SUM(fc.file_size), 0)
            FROM file_contents fc
            JOIN uploaded_files uf ON uf.id = fc.uploaded_file_id
            WHERE uf.user_name = %s
        """, (user_id,))
        row = cursor.fetchone()
        total_files = row[0]
        total_size = row[1]

        cursor.execute("""
            SELECT DISTINCT fc.file_extension
            FROM file_contents fc
            JOIN uploaded_files uf ON uf.id = fc.uploaded_file_id
            WHERE uf.user_name = %s AND fc.file_extension IS NOT NULL
                AND fc.file_extension != ''
        """, (user_id,))
        extensions = [r[0].lower() for r in cursor.fetchall()]

    languages = set()
    skills = set()
    for ext in extensions:
        if ext in LANGUAGE_EXTENSIONS:
            languages.add(LANGUAGE_EXTENSIONS[ext])
            skills.add(LANGUAGE_EXTENSIONS[ext])

    return {
        "total_projects": total_projects,
        "total_files": total_files,
        "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size else 0,
        "unique_languages": len(languages),
        "unique_skills": len(skills),
        "languages": sorted(list(languages))
    }

@router.get("/portfolio/public/{user_id}/settings")
async def get_public_portfolio_settings(user_id: str):
    """Get public portfolio settings (read-only)."""
    try:
        settings = _get_public_settings_or_403(user_id)
        return {"success": True, "settings": {k: v for k, v in settings.items() if k != 'updated_at'}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving portfolio settings: {str(e)}")

@router.get("/portfolio/public/{user_id}/stats")
async def get_public_portfolio_stats(user_id: str):
    """Public portfolio stats."""
    try:
        settings = _get_public_settings_or_403(user_id)
        if settings.get('show_stats', True) is False:
            return {"success": True, "stats": {}}
        stats = _compute_portfolio_stats(user_id)
        return {"success": True, "stats": stats}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving portfolio stats: {str(e)}")

@router.get("/portfolio/public/{user_id}/timeline")
async def get_public_skills_timeline(user_id: str):
    """Public skills timeline."""
    try:
        settings = _get_public_settings_or_403(user_id)
        if settings.get('show_timeline', True) is False:
            return {"success": True, "data": {}}
        manager = PortfolioManager(user_id)
        timeline_data = manager.get_skills_timeline()
        return {"success": True, "data": timeline_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving skills timeline: {str(e)}")

@router.get("/portfolio/public/{user_id}/heatmap")
async def get_public_activity_heatmap(user_id: str):
    """Public activity heatmap."""
    try:
        settings = _get_public_settings_or_403(user_id)
        if settings.get('show_heatmap', True) is False:
            return {"success": True, "data": {}}
        manager = PortfolioManager(user_id)
        heatmap_data = manager.get_activity_heatmap()
        return {"success": True, "data": heatmap_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving activity heatmap: {str(e)}")

@router.get("/portfolio/public/{user_id}/top-projects")
async def get_public_top_projects(user_id: str, search: Optional[str] = Query(None)):
    """Public top projects showcase."""
    try:
        settings = _get_public_settings_or_403(user_id)
        if settings.get('show_top_projects', True) is False:
            return {"success": True, "projects": []}
        manager = PortfolioManager(user_id)
        top_projects = manager.get_top3_showcase()
        if search:
            search_lower = search.lower()
            top_projects = [p for p in top_projects
                            if search_lower in p.get('name', '').lower()
                            or search_lower in p.get('description', '').lower()]
        return {"success": True, "projects": top_projects}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving top projects: {str(e)}")


@router.get("/portfolio/public/by-username/{user_name}")
async def get_public_portfolio_by_username(
    user_name: str,
    search: Optional[str] = Query(None),
    skill_filter: Optional[str] = Query(None),
):
    """
    Alias endpoint for public portfolio retrieval keyed explicitly by user_name.
    This mirrors /portfolio/public/{user_id} but makes the intent clearer for
    shareable links and future hosted deployments.
    """
    return await get_public_portfolio(user_name, search=search, skill_filter=skill_filter)


@router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str, top_n: Optional[int] = Query(None)):
    """Get user's portfolio by ID."""
    try:
        manager = PortfolioManager(user_id)
        portfolio_data = manager.generate_portfolio_report(top_n=top_n)
        if 'error' in portfolio_data:
            raise HTTPException(status_code=404, detail=portfolio_data['error'])
        return {"success": True, "portfolio": portfolio_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving portfolio: {str(e)}")


@router.post("/portfolio/generate")
async def generate_portfolio(request: PortfolioGenerateRequest, user_name: Optional[str] = Query(None)):
    """Generate a new portfolio for the user."""
    try:
        if not user_name:
            raise HTTPException(status_code=400, detail="user_name is required")
        manager = PortfolioManager(user_name)
        portfolio_data = manager.generate_portfolio_report(top_n=request.top_n)
        if 'error' in portfolio_data:
            raise HTTPException(status_code=400, detail=portfolio_data['error'])
        return {"success": True, "portfolio": portfolio_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating portfolio: {str(e)}")


@router.post("/portfolio/{user_id}/edit")
async def edit_portfolio(user_id: str, request: PortfolioEditRequest):
    """Edit portfolio custom data (placeholder for future enhancements)."""
    try:
        return {"success": True, "message": "Portfolio edit feature coming soon"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error editing portfolio: {str(e)}")


# Portfolio Customization Endpoints

@router.post("/portfolio/{user_id}/custom-data", response_model=PortfolioCustomizationResponse)
async def save_portfolio_customization(user_id: str, request: PortfolioCustomizationRequest):
    """Save or update portfolio customization for a specific project."""
    try:
        if request.project_id <= 0:
            raise HTTPException(status_code=400, detail="project_id must be positive")
        
        custom_data = {
            'custom_title': request.custom_title,
            'custom_description': request.custom_description,
            'custom_role': request.custom_role,
            # Layout / presentation-only controls; backend will persist these
            # but they do NOT alter any verified analysis data.
            'display_order': request.display_order,
            'highlight': request.highlight,
        }
        
        if ResumeManager.save_portfolio_customization(user_id, request.project_id, custom_data):
            # Retrieve the saved customization to return complete data
            saved = ResumeManager.get_portfolio_customization(user_id, request.project_id)
            if saved:
                return PortfolioCustomizationResponse(
                    project_id=saved['project_id'],
                    custom_title=saved['custom_title'],
                    custom_description=saved['custom_description'],
                    custom_role=saved['custom_role'],
                    display_order=saved.get('display_order'),
                    highlight=saved.get('highlight'),
                    created_at=saved['created_at'].isoformat() if saved['created_at'] else None,
                    updated_at=saved['updated_at'].isoformat() if saved['updated_at'] else None,
                )
        raise HTTPException(status_code=500, detail="Failed to save portfolio customization")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving portfolio customization: {str(e)}")


@router.get("/portfolio/{user_id}/custom-data", response_model=PortfolioCustomizationListResponse)
async def list_portfolio_customizations(user_id: str):
    """List all project IDs that have portfolio customizations."""
    try:
        project_ids = ResumeManager.list_customized_portfolio_projects(user_id)
        return PortfolioCustomizationListResponse(project_ids=project_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing portfolio customizations: {str(e)}")


@router.get("/portfolio/{user_id}/custom-data/{project_id}", response_model=PortfolioCustomizationResponse)
async def get_portfolio_customization(user_id: str, project_id: int):
    """Get portfolio customization for a specific project."""
    try:
        if project_id <= 0:
            raise HTTPException(status_code=400, detail="project_id must be positive")
        
        customization = ResumeManager.get_portfolio_customization(user_id, project_id)
        if customization:
            return PortfolioCustomizationResponse(
                project_id=customization['project_id'],
                custom_title=customization['custom_title'],
                custom_description=customization['custom_description'],
                custom_role=customization['custom_role'],
                display_order=customization.get('display_order'),
                highlight=customization.get('highlight'),
                created_at=customization['created_at'].isoformat() if customization['created_at'] else None,
                updated_at=customization['updated_at'].isoformat() if customization['updated_at'] else None,
            )

        return PortfolioCustomizationResponse(
            project_id=project_id,
            custom_title=None,
            custom_description=None,
            custom_role=None,
            created_at=None,
            updated_at=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting portfolio customization: {str(e)}")


@router.delete("/portfolio/{user_id}/custom-data/{project_id}", response_model=SimpleMessageResponse)
async def clear_portfolio_customization(user_id: str, project_id: int):
    """Clear portfolio customization for a specific project."""
    try:
        if project_id <= 0:
            raise HTTPException(status_code=400, detail="project_id must be positive")
        
        if ResumeManager.clear_portfolio_customization(user_id, project_id):
            return SimpleMessageResponse(message="Portfolio customization cleared successfully")
        raise HTTPException(status_code=500, detail="Failed to clear portfolio customization")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing portfolio customization: {str(e)}")


# ──────────────────────────────────────────────
# Portfolio Dashboard Endpoints
# ──────────────────────────────────────────────

@router.get("/portfolio/{user_id}/settings")
async def get_portfolio_settings(user_id: str):
    """Get portfolio visibility and component settings."""
    try:
        settings = ResumeManager.get_portfolio_settings(user_id)
        return {"success": True, "settings": settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving portfolio settings: {str(e)}")


@router.post("/portfolio/{user_id}/settings")
async def save_portfolio_settings(user_id: str, request: PortfolioSettingsRequest):
    """Save portfolio visibility and component settings."""
    try:
        current = ResumeManager.get_portfolio_settings(user_id)
        updated = {
            'is_public': request.is_public if request.is_public is not None else current.get('is_public', False),
            'show_timeline': request.show_timeline if request.show_timeline is not None else current.get('show_timeline', True),
            'show_heatmap': request.show_heatmap if request.show_heatmap is not None else current.get('show_heatmap', True),
            'show_top_projects': request.show_top_projects if request.show_top_projects is not None else current.get('show_top_projects', True),
            'show_skills': request.show_skills if request.show_skills is not None else current.get('show_skills', True),
            'show_stats': request.show_stats if request.show_stats is not None else current.get('show_stats', True),
        }
        if ResumeManager.save_portfolio_settings(user_id, updated):
            return {"success": True, "settings": updated}
        raise HTTPException(status_code=500, detail="Failed to save portfolio settings")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving portfolio settings: {str(e)}")


class TimelineOverrideEntry(BaseModel):
    project_id: int
    hidden_skills: Optional[List[str]] = []
    added_skills: Optional[List[str]] = []
    custom_date: Optional[str] = None


class TimelineOverridesRequest(BaseModel):
    overrides: List[TimelineOverrideEntry]


@router.get("/portfolio/{user_id}/timeline")
async def get_skills_timeline(user_id: str):
    """Get skills timeline showing learning progression and depth."""
    try:
        manager = PortfolioManager(user_id)
        timeline_data = manager.get_skills_timeline()
        return {"success": True, "data": timeline_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving skills timeline: {str(e)}")


@router.post("/portfolio/{user_id}/timeline/overrides")
async def save_timeline_overrides(user_id: str, request: TimelineOverridesRequest):
    """Save timeline skill overrides (hidden/added skills, custom dates) for multiple projects."""
    try:
        saved = 0
        for entry in request.overrides:
            if entry.project_id <= 0:
                continue
            data = {
                'hidden_skills': entry.hidden_skills or [],
                'added_skills': entry.added_skills or [],
                'custom_date': entry.custom_date
            }
            if ResumeManager.save_timeline_override(user_id, entry.project_id, data):
                saved += 1
        return {"success": True, "message": f"Saved {saved} timeline override(s)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving timeline overrides: {str(e)}")


@router.get("/portfolio/{user_id}/timeline/overrides")
async def get_timeline_overrides(user_id: str):
    """Get all timeline overrides for a user."""
    try:
        overrides = ResumeManager.get_timeline_overrides(user_id)
        serializable = {}
        for pid, data in overrides.items():
            serializable[str(pid)] = data
        return {"success": True, "overrides": serializable}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving timeline overrides: {str(e)}")


@router.get("/portfolio/{user_id}/heatmap")
async def get_activity_heatmap(user_id: str):
    """Get activity heatmap data showing productivity over time."""
    try:
        manager = PortfolioManager(user_id)
        heatmap_data = manager.get_activity_heatmap()
        return {"success": True, "data": heatmap_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving activity heatmap: {str(e)}")


@router.get("/portfolio/{user_id}/top-projects")
async def get_top_projects(user_id: str):
    """Get top 3 projects showcase with evolution data."""
    try:
        manager = PortfolioManager(user_id)
        showcase = manager.get_top3_showcase()
        return {"success": True, "projects": showcase}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving top projects: {str(e)}")


@router.get("/portfolio/{user_id}/stats")
async def get_portfolio_stats(user_id: str):
    """Lightweight portfolio stats from database. No ranking required."""
    try:
        stats = _compute_portfolio_stats(user_id)
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving portfolio stats: {str(e)}")
