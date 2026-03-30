"""Project-related endpoints."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Body
from typing import Optional
import base64
import json
import tempfile
import os
import io
from PIL import Image
from upload_file import add_file_to_db, list_uploaded_files, add_thumbnail_bytes_to_project, merge_zip_to_project
from project_manager import list_projects, get_project_by_id
from project_analyzer import analyze_project_by_id
from analysis.project_ranking import rank_all_projects, save_rankings_with_summaries, rank_and_summarize_top_projects
from analysis.ranking_storage import get_stored_rankings, save_rankings_to_db
from project_summarizer import summarize_project
from analysis.gemini_ranker import rank_projects_with_gemini
from analysis.project_replay import build_project_replay, enrich_replay_with_ai
from tools.cleanup_insights import delete_insights
from database.user_preferences import update_user_git_username, get_user_git_username
from config.db_config import with_db_cursor
from common.logger import setup_logger
from consent.consent_storage import ConsentStorage
from external_services.permission_manager import ExternalServicePermission
from account.user_manager import AuthManager

router = APIRouter()
logger = setup_logger(__name__)

def _detect_image_type(image_bytes: bytes) -> Optional[str]:
    """Return a short image type label based on magic bytes, or None."""
    if not image_bytes:
        return None
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a"):
        return "gif"
    if image_bytes.startswith(b"BM"):
        return "bmp"
    if image_bytes.startswith(b"II*\x00") or image_bytes.startswith(b"MM\x00*"):
        return "tiff"
    # WEBP: "RIFF" .... "WEBP"
    if len(image_bytes) >= 12 and image_bytes[0:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "webp"
    return None


def _ensure_llm_allowed(user_name: Optional[str]) -> str:
    """
    Ensure that LLM / external AI usage is allowed for the given user.
    Raises HTTPException(403) when not permitted.
    Returns the resolved username for downstream use.
    """
    if not user_name:
        raise HTTPException(
            status_code=400,
            detail="user_name is required for LLM-powered operations",
        )

    consent = ConsentStorage.get_consent_status(user_name) or {}
    consent_given = consent.get("consent_given", False)

    permission_manager = ExternalServicePermission(user_name)
    llm_permission = permission_manager.has_permission("LLM")

    if not consent_given or not llm_permission:
        raise HTTPException(
            status_code=403,
            detail="LLM features are disabled for this user. Enable AI features in settings to use Gemini analysis.",
        )

    return user_name


@router.post("/projects/upload")
async def upload_project(
    file: UploadFile = File(...),
    user_name: Optional[str] = Query(None, description="Username for the upload")
):
    """
    Upload a project file (ZIP archive).
    
    Args:
        file: The ZIP file to upload
        user_name: Optional username (defaults to None if not provided)
        
    Returns:
        dict: Upload result with file information
    """
    # Validate file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported"
        )
    
    # Create temporary file to save upload
    temp_file = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Use existing upload function, passing the original filename
        result = add_file_to_db(temp_path, user_name=user_name, original_filename=file.filename)
        
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception:
            pass
        
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=result.message
            )
        
        return result.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file on error
        if temp_file and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )


@router.post("/projects/{project_id}/merge")
async def merge_project_files(
    project_id: int,
    file: UploadFile = File(...),
    user_name: Optional[str] = Query(None, description="Username for ownership verification")
):
    """
    Merge files from a new ZIP archive into an existing project.
    
    This enables incremental additions to a portfolio or résumé by adding
    new files from another zipped folder at a later point in time.
    Duplicate files (same path) are automatically skipped.
    
    Args:
        project_id: The ID of the existing project to merge into
        file: The new ZIP file containing additional files
        user_name: Username to verify project ownership
        
    Returns:
        dict: Merge result with statistics about new and skipped files
    """
    # Validate file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported for merging"
        )
    
    temp_file = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Perform the merge
        result = merge_zip_to_project(project_id, temp_path, user_name=user_name)
        
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception:
            pass
        
        if not result.success:
            status_code = 404 if result.error_type == "PROJECT_NOT_FOUND" else 400
            raise HTTPException(
                status_code=status_code,
                detail=result.message
            )
        
        return result.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file on error
        if temp_file and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Error merging files: {str(e)}"
        )


@router.post("/projects/{project_id}/thumbnail")
async def upload_project_thumbnail(
    project_id: int,
    file: UploadFile = File(...),
    user_name: Optional[str] = Query(None, description="Username to verify project ownership")
):
    """
    Upload and attach a thumbnail image to an existing project.
    
    Args:
        project_id: The ID of the project to update
        file: The thumbnail image file
        user_name: Optional username to verify ownership
        
    Returns:
        dict: Upload result
    """
    try:
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are supported")

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Thumbnail file is empty")

        if _detect_image_type(content) is None:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

        project = get_project_by_id(project_id, user_name=user_name)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        result = add_thumbnail_bytes_to_project(project_id, content)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)

        return result.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading thumbnail: {str(e)}"
        )


@router.get("/projects/{project_id}/thumbnail")
async def get_project_thumbnail(
    project_id: int,
    user_name: Optional[str] = Query(None, description="Username to verify project ownership")
):
    """
    Get a project's thumbnail as a data URL.
    """
    try:
        project = get_project_by_id(project_id, user_name=user_name)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        with with_db_cursor() as cursor:
            cursor.execute("SELECT thumbnail FROM uploaded_files WHERE id = %s", (project_id,))
            row = cursor.fetchone()

        if not row or row[0] is None:
            return {"success": True, "has_thumbnail": False}

        thumbnail_bytes = row[0]
        image_type = _detect_image_type(thumbnail_bytes)
        if image_type is None:
            raise HTTPException(status_code=400, detail="Stored thumbnail is not a valid image")

        mime_map = {
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "bmp": "image/bmp",
            "webp": "image/webp",
        }
        if image_type == "tiff":
            # Convert TIFF to PNG for browser display
            with Image.open(io.BytesIO(thumbnail_bytes)) as img:
                out = io.BytesIO()
                img.save(out, format="PNG")
                thumbnail_bytes = out.getvalue()
            image_type = "png"

        mime_type = mime_map.get(image_type, "image/png")
        b64 = base64.b64encode(thumbnail_bytes).decode("ascii")
        data_url = f"data:{mime_type};base64,{b64}"

        return {"success": True, "has_thumbnail": True, "thumbnail_data": data_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving thumbnail: {str(e)}"
        )


@router.get("/projects")
async def get_projects(
    user_name: Optional[str] = Query(None, description="Filter projects by username")
):
    """
    Get list of all projects.
    
    Args:
        user_name: Optional username to filter projects (if not provided, returns all)
        
    Returns:
        dict: List of projects with metadata
    """
    try:
        if user_name:
            # Use project_manager for user-specific projects
            # list_projects returns a list of dicts, so we use it directly
            projects = list_projects(user_name=user_name)
            # Convert datetime objects to ISO strings for API response
            for proj in projects:
                created_at = proj.get('created_at')
                if created_at:
                    if hasattr(created_at, 'isoformat'):
                        proj['created_at'] = created_at.isoformat()
                    else:
                        proj['created_at'] = str(created_at)
        else:
            # Get all projects from uploaded_files
            projects_data = list_uploaded_files()
            projects = []
            for proj in projects_data:
                # Parse metadata to get file count
                file_count = 0
                if proj.get('metadata'):
                    try:
                        metadata = json.loads(proj['metadata']) if isinstance(proj['metadata'], str) else proj['metadata']
                        if 'files' in metadata and metadata['files']:
                            actual_files = [f for f in metadata['files'] if not f.endswith('/')]
                            file_count = len(actual_files)
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                # Handle datetime conversion
                created_at = proj.get('created_at')
                if created_at:
                    if hasattr(created_at, 'isoformat'):
                        # datetime object
                        created_at_str = created_at.isoformat()
                    else:
                        # Already a string
                        created_at_str = str(created_at)
                else:
                    created_at_str = None
                
                projects.append({
                    'id': proj['id'],
                    'filename': proj['filename'],
                    'created_at': created_at_str,
                    'file_count': file_count,
                    'status': proj.get('status', 'unknown')
                })
        
        return {
            "success": True,
            "count": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving projects: {str(e)}"
        )

@router.get("/projects/rankings")
async def get_rankings(user_name: Optional[str] = Query(None, description="Username for data isolation")):
    """Get stored rankings."""
    try:
        resolved_user = user_name or AuthManager.get_current_username()
        if not resolved_user:
            raise HTTPException(status_code=401, detail="User authentication required")
        
        user_name = resolved_user
        
        rankings = get_stored_rankings(user_name=user_name)
        
        return {"success": True, "rankings": rankings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving rankings: {str(e)}")


@router.post("/projects/rankings/save")
async def save_rankings(
    body: dict = Body(..., description="JSON with 'ranked_projects' array"),
    user_name: Optional[str] = Query(None, description="Username for data isolation"),
):
    """Save ranked projects to the database (same as backend save). Requires ranked_projects in body."""
    try:
        if not isinstance(body.get("ranked_projects"), list):
            raise HTTPException(
                status_code=400,
                detail="Request body must include 'ranked_projects' (array of { project_id, filename, score, ... })",
            )
        
        resolved_user = user_name or AuthManager.get_current_username()
        if not resolved_user:
            raise HTTPException(status_code=401, detail="User authentication required")
        
        user_name = resolved_user
        
        ranked = body["ranked_projects"]
        success = save_rankings_to_db(ranked, summaries=None, user_name=user_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save rankings to database")
        return {"success": True, "message": f"Saved {len(ranked)} rankings to database"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving rankings: {str(e)}")


@router.post("/projects/rankings/summary")
async def update_project_summary(
    body: dict = Body(..., description="JSON with 'project_id' and 'summary'"),
    user_name: Optional[str] = Query(None, description="Username for data isolation"),
):
    """Update the summary for a specific project."""
    try:
        from analysis.ranking_storage import update_ranking_summary, get_stored_ranking_by_project_id
        
        resolved_user = user_name or AuthManager.get_current_username()
        if not resolved_user:
            raise HTTPException(status_code=401, detail="User authentication required")
        
        user_name = resolved_user
        
        project_id = body.get("project_id")
        summary = body.get("summary", "")
        
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        # Check if ranking exists, if not create a basic one
        existing = get_stored_ranking_by_project_id(project_id, user_name=user_name)
        if not existing:
            # Create a basic ranking entry with just the summary
            from analysis.ranking_storage import save_rankings_to_db
            save_rankings_to_db(
                [{"project_id": project_id, "filename": "", "score": 0.0}],
                summaries={project_id: summary},
                user_name=user_name
            )
        else:
            # Update existing summary
            success = update_ranking_summary(project_id, summary, user_name=user_name)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update summary")
        
        return {"success": True, "message": "Summary updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating summary: {str(e)}")


@router.get("/projects/{project_id}")
async def get_project_by_id_endpoint(
    project_id: int,
    user_name: Optional[str] = Query(None, description="Username to verify project ownership")
):
    """
    Get a specific project by ID.
    
    Args:
        project_id: The ID of the project to retrieve
        user_name: Optional username to verify ownership
        
    Returns:
        dict: Project information
    """
    try:
        resolved_user = user_name or AuthManager.get_current_username()
        if not resolved_user:
            raise HTTPException(status_code=401, detail="User authentication required")
        
        project = get_project_by_id(project_id, user_name=resolved_user)
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Extract data from nested structure (new format)
        # project now has 'project_info' nested structure
        project_info = project.get('project_info', {})
        
        # Get created_at from project_info (already ISO string from new version)
        created_at_str = project_info.get('created_at')
        
        # Reconstruct the original metadata from the full analysis data
        # Remove project_info to get back the original metadata content
        metadata_content = {k: v for k, v in project.items() if k != 'project_info'}
        
        project_data = {
            'id': project_info.get('id'),
            'filename': project_info.get('filename'),
            'filepath': project_info.get('filepath', ''),
            'status': project_info.get('status', 'unknown'),
            'metadata': metadata_content if metadata_content else None,
            'created_at': created_at_str
        }
        
        return {
            "success": True,
            "project": project_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving project: {str(e)}"
        )


@router.get("/projects/{project_id}/replay")
async def get_project_replay(
    project_id: int,
    user_name: Optional[str] = Query(None, description="Username to verify project ownership"),
    use_ai: bool = Query(False, description="Use Gemini to enrich replay when AI features are enabled"),
):
    """
    Build a timeline replay for a project using file metadata timestamps.
    Full-duration narrative and interview-ready talking points.
    When use_ai=true and LLM enabled, Gemini enriches the output.
    """
    try:
        current_user = AuthManager.get_current_username()
        if not current_user:
            raise HTTPException(status_code=401, detail="User authentication required")
        if user_name and user_name != current_user:
            raise HTTPException(status_code=403, detail="Not authorized to view this project")
        resolved_user = user_name or current_user
        project = get_project_by_id(project_id, user_name=resolved_user)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        if use_ai:
            _ensure_llm_allowed(resolved_user)

        with with_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT file_path, file_extension, file_size, created_at, source_created_at
                FROM file_contents
                WHERE uploaded_file_id = %s
                ORDER BY COALESCE(source_created_at, created_at), file_path
                """,
                (project_id,),
            )
            rows = cursor.fetchall() or []

        file_rows = [
            {
                "file_path": row[0],
                "file_extension": row[1],
                "file_size": row[2],
                "created_at": row[3],
                "source_created_at": row[4],
            }
            for row in rows
        ]
        replay = build_project_replay(file_rows)

        if use_ai:
            project_name = (project.get("project_info") or {}).get("filename", "Project")
            replay = enrich_replay_with_ai(replay, project_name=project_name)

        return {"success": True, "project_id": project_id, **replay}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building project replay: {str(e)}")


@router.post("/projects/{project_id}/analyze")
async def analyze_project(project_id: int, user_name: Optional[str] = Query(None)):
    """Analyze a project using local analysis."""
    try:
        from project_analyzer import ProjectAnalyzer
        # Use interactive=False to skip stdin prompts in API context
        analyzer = ProjectAnalyzer(user_name or 'default_user', interactive=False)
        results = analyzer.analyze_uploaded_project(project_id)
        if not results.get('success'):
            raise HTTPException(status_code=400, detail=results.get('error', 'Analysis failed'))
        return {"success": True, "analysis": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing project: {str(e)}")


@router.post("/projects/{project_id}/analyze-gemini")
async def analyze_project_gemini(project_id: int, user_name: Optional[str] = Query(None)):
    """
    Perform deep AI-powered analysis using Gemini.
    
    This provides a more thorough analysis than the local analysis,
    including architecture assessment, skill evaluation, security review,
    and actionable recommendations.
    """
    try:
        # Enforce explicit LLM consent + external permission
        resolved_user = _ensure_llm_allowed(user_name)
        from project_manager import get_project_by_id
        from analysis.gemini_analyzer import GeminiAnalyzer
        from config.db_config import with_db_cursor
        
        # Get project info
        project = get_project_by_id(project_id, user_name=resolved_user)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Get file contents from database
        file_contents = []
        with with_db_cursor() as cursor:
            cursor.execute("""
                SELECT file_path, file_name, file_extension, file_size,
                       file_content, content_type, is_binary
                FROM file_contents
                WHERE uploaded_file_id = %s
                ORDER BY file_path
            """, (project_id,))
            
            for row in cursor.fetchall():
                file_contents.append({
                    'file_path': row[0],
                    'file_name': row[1],
                    'file_extension': row[2],
                    'file_size': row[3] or 0,
                    'file_content': row[4],
                    'content_type': row[5],
                    'is_binary': row[6],
                })
        
        if not file_contents:
            raise HTTPException(status_code=400, detail="No file contents found for this project")
        
        # Get basic context from local analysis for Gemini
        from project_analyzer import ProjectAnalyzer
        local_analyzer = ProjectAnalyzer(resolved_user or "default_user", interactive=False)
        languages = local_analyzer._analyze_languages_from_files(file_contents)
        frameworks = local_analyzer._detect_frameworks_from_files(file_contents)
        
        context = {
            'primary_language': languages.get('primary_language'),
            'detected_languages': languages.get('detected_languages', []),
            'frameworks': frameworks,
        }
        
        # Run Gemini analysis
        analyzer = GeminiAnalyzer()
        results = analyzer.analyze_project(
            file_contents,
            project_name=project.get('filename', 'Unknown'),
            project_context=context
        )
        
        if not results.get('success'):
            raise HTTPException(status_code=400, detail=results.get('error', 'Gemini analysis failed'))
        
        # Store results in database (creates new record for each analysis)
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO analysis_results (uploaded_file_id, analysis_data, analysis_strategy)
                    VALUES (%s, %s, %s)
                """, (project_id, json.dumps(results, default=str), 'gemini'))
        except Exception as db_err:
            logger.warning(f"Could not store Gemini analysis results: {db_err}")
        
        return {"success": True, "analysis": results, "analysis_type": "gemini"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Gemini analysis: {str(e)}")


@router.post("/projects/{project_id}/quick-summary")
async def get_project_quick_summary(project_id: int, user_name: Optional[str] = Query(None)):
    """
    Get a quick AI-generated summary of a project.
    Useful for resume/portfolio descriptions.
    """
    try:
        # Enforce explicit LLM consent + external permission
        resolved_user = _ensure_llm_allowed(user_name)
        from project_manager import get_project_by_id
        from analysis.gemini_analyzer import GeminiAnalyzer
        from config.db_config import with_db_cursor
        
        # Get project info
        project = get_project_by_id(project_id, user_name=resolved_user)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Get file contents
        file_contents = []
        with with_db_cursor() as cursor:
            cursor.execute("""
                SELECT file_path, file_name, file_extension, file_size,
                       file_content, content_type, is_binary
                FROM file_contents
                WHERE uploaded_file_id = %s
            """, (project_id,))
            
            for row in cursor.fetchall():
                file_contents.append({
                    'file_path': row[0],
                    'file_name': row[1],
                    'file_extension': row[2],
                    'file_size': row[3] or 0,
                    'file_content': row[4],
                    'content_type': row[5],
                    'is_binary': row[6],
                })
        
        if not file_contents:
            raise HTTPException(status_code=400, detail="No file contents found")
        
        analyzer = GeminiAnalyzer()
        project_name = project.get('filename', 'Unknown')
        summary = analyzer.get_quick_summary(file_contents, project_name)
        
        return {"success": True, "summary": summary, "project_name": project_name}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.post("/projects/rank")
async def rank_projects(user_name: Optional[str] = Query(None)):
    """Rank all projects."""
    try:
        ranked = rank_all_projects(user_name=user_name)
        save_rankings_with_summaries(ranked, generate_summaries=True)
        return {"success": True, "ranked_projects": ranked[:10], "count": len(ranked)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ranking projects: {str(e)}")


@router.post("/projects/rank-top3")
async def rank_top3(user_name: Optional[str] = Query(None)):
    """Rank all projects, then generate and return summaries for the top 3."""
    try:
        ranked = rank_all_projects(user_name=user_name)
        top3_raw = ranked[:3]
        top3 = []
        for project in top3_raw:
            summary_text = ""
            try:
                raw = summarize_project(project["project_id"], user_name=user_name)
                if raw and isinstance(raw, str):
                    summary_text = raw.strip()
            except Exception as e:
                logger.warning("Summary failed for project %s: %s", project.get("project_id"), e)
            created_at = project.get("created_at")
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            top3.append({
                "project_id": project["project_id"],
                "filename": project.get("filename", ""),
                "score": project.get("score", 0.0),
                "created_at": created_at,
                "summary": summary_text,
            })
        return {"success": True, "top3": top3}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ranking top 3: {str(e)}")


@router.post("/projects/rank-gemini")
async def rank_projects_gemini(user_name: Optional[str] = Query(None)):
    """Rank all projects using Gemini AI comparison."""
    try:
        # Enforce explicit LLM consent + external permission
        resolved_user = _ensure_llm_allowed(user_name)
        result = rank_projects_with_gemini(user_name=resolved_user)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Gemini ranking failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Gemini ranking: {str(e)}")


@router.delete("/projects/{project_id}/data")
async def delete_project_data(
    project_id: int,
    user_name: Optional[str] = Query(None, description="Username for data isolation verification")
):
    """Delete all project data including metrics, file contents, and project records.
    
    Args:
        project_id: ID of the project to delete
        user_name: Username to verify project ownership (required for security)
    
    Returns:
        dict: Success status and deletion statistics
    
    Raises:
        HTTPException: 400 if user_name not provided, 403 if permission denied, 500 on error
    """
    resolved_user = user_name or AuthManager.get_current_username()
    if not resolved_user:
        raise HTTPException(status_code=401, detail="User authentication required")
    
    try:
        deleted = delete_insights(project_id, user_name=resolved_user)
        return {
            "success": True,
            "deleted": {
                "metrics": deleted[0],
                "files": deleted[1],
                "projects": deleted[2]
            }
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project data: {str(e)}")


@router.get("/preferences")
async def get_preferences(
    user_name: Optional[str] = Query(None, description="Username for preferences")
):
    """Get user preferences."""
    if not user_name:
        raise HTTPException(status_code=400, detail="user_name is required")
    try:
        from database.user_preferences import get_user_git_username
        git_username = get_user_git_username(user_name)
        return {
            "success": True,
            "preferences": {
                "git_username": git_username
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving preferences: {str(e)}")


@router.post("/preferences")
async def update_preferences(
    request: dict,
    user_name: Optional[str] = Query(None, description="Username for preferences")
):
    """Update user preferences."""
    if not user_name:
        raise HTTPException(status_code=400, detail="user_name is required")
    try:
        git_username = request.get('git_username')
        if git_username:
            update_user_git_username(user_name, git_username)
        return {"success": True, "git_username": get_user_git_username(user_name)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")
