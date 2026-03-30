"""
Gemini-powered deep code analysis.
Provides thorough, AI-driven analysis of project code quality, architecture, and skills.
"""

import json
import re
import time
from typing import Any, Dict, List, Optional

from external_services.gemini_client import generate_text


# Maximum characters to send to Gemini per request
MAX_CODE_CHARS = 50000
# Maximum files to include in analysis
MAX_FILES_TO_ANALYZE = 30
# Retry settings for rate limits
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # seconds


class GeminiAnalyzer:
    """
    Uses Gemini AI to perform deep, nuanced code analysis.
    Provides insights beyond pattern matching - understands code semantics,
    architecture, best practices, and skill demonstration.
    """

    def __init__(self):
        self.analysis_cache = {}

    def analyze_project(
        self,
        file_contents: List[Dict[str, Any]],
        project_name: str = "Unknown Project",
        project_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive Gemini-powered analysis on a project.

        Args:
            file_contents: List of file info dicts with 'file_path', 'file_content', etc.
            project_name: Name of the project being analyzed
            project_context: Optional additional context (languages detected, frameworks, etc.)

        Returns:
            dict: Comprehensive analysis results
        """
        if not file_contents:
            return {"error": "No file contents provided", "success": False}

        # Filter and prepare code files for analysis
        code_files = self._prepare_code_files(file_contents)

        if not code_files:
            return {
                "error": "No analyzable code files found",
                "success": False,
                "file_count": len(file_contents),
            }

        # Build the analysis prompt
        prompt = self._build_analysis_prompt(code_files, project_name, project_context)

        try:
            # Call Gemini with retry logic for rate limits
            response = self._call_gemini_with_retry(
                prompt,
                system_instruction=self._get_system_instruction(),
                temperature=0.3,
            )

            # Parse the response
            analysis = self._parse_analysis_response(response)
            analysis["success"] = True
            analysis["files_analyzed"] = len(code_files)
            analysis["project_name"] = project_name

            return analysis

        except Exception as e:
            error_msg = str(e)
            # Provide helpful message for rate limits
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                error_msg = "API rate limit reached. Please wait a minute and try again."
            return {
                "error": f"Gemini analysis failed: {error_msg}",
                "success": False,
                "files_analyzed": len(code_files),
            }

    def _call_gemini_with_retry(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        """Call Gemini API with exponential backoff retry for rate limits."""
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                return generate_text(
                    prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                )
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Only retry on rate limit errors
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    if attempt < MAX_RETRIES - 1:
                        delay = INITIAL_RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limited, retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})...")
                        time.sleep(delay)
                        continue
                
                # Don't retry other errors
                raise
        
        # All retries exhausted
        raise last_error

    def _prepare_code_files(
        self, file_contents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter and prepare code files for analysis.
        Prioritizes important files and limits total size.
        """
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".swift",
            ".kt",
            ".scala",
            ".vue",
            ".svelte",
        }

        # Priority files (entry points, main logic)
        priority_patterns = [
            "main",
            "app",
            "index",
            "server",
            "api",
            "router",
            "controller",
            "service",
            "model",
            "component",
        ]

        analyzable = []
        total_chars = 0

        for f in file_contents:
            if f.get("is_binary", False):
                continue

            ext = f.get("file_extension", "").lower()
            if ext not in code_extensions:
                continue

            content = f.get("file_content", "")
            if not content:
                continue

            # Handle bytes (from database BYTEA column)
            if isinstance(content, (bytes, memoryview)):
                try:
                    content = bytes(content).decode("utf-8", errors="ignore")
                except Exception:
                    continue

            if not isinstance(content, str) or not content.strip():
                continue

            # Skip very small files (likely empty or minimal)
            if len(content.strip()) < 50:
                continue

            # Calculate priority score
            name_lower = f.get("file_name", "").lower()
            priority = sum(1 for p in priority_patterns if p in name_lower)

            analyzable.append(
                {
                    "path": f.get("file_path", "unknown"),
                    "name": f.get("file_name", "unknown"),
                    "content": content,
                    "extension": ext,
                    "size": len(content),
                    "priority": priority,
                }
            )

        # Sort by priority (high first), then by size (smaller first to include more files)
        analyzable.sort(key=lambda x: (-x["priority"], x["size"]))

        # Select files within limits
        selected = []
        for f in analyzable:
            if len(selected) >= MAX_FILES_TO_ANALYZE:
                break
            if total_chars + f["size"] > MAX_CODE_CHARS:
                # Try to fit smaller files
                continue
            selected.append(f)
            total_chars += f["size"]

        return selected

    def _get_system_instruction(self) -> str:
        """Get the system instruction for Gemini."""
        return """You are an expert code analyst and software engineering mentor. 
Your task is to analyze code projects and provide detailed, actionable insights about:
- Code quality and architecture
- Programming skills demonstrated
- Best practices followed or missed
- Security considerations
- Performance characteristics
- Areas for improvement

Be specific, reference actual code patterns you see, and provide constructive feedback.
Format your response as JSON for easy parsing."""

    def _build_analysis_prompt(
        self,
        code_files: List[Dict[str, Any]],
        project_name: str,
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Build the comprehensive analysis prompt."""

        # Build file content section
        files_section = []
        for f in code_files:
            # Truncate very long files
            content = f["content"]
            if len(content) > 3000:
                content = content[:1500] + "\n\n... [truncated] ...\n\n" + content[-1500:]

            files_section.append(
                f"### File: {f['path']}\n```{f['extension'][1:]}\n{content}\n```"
            )

        files_text = "\n\n".join(files_section)

        # Build context section
        context_text = ""
        if context:
            context_parts = []
            if context.get("primary_language"):
                context_parts.append(f"Primary Language: {context['primary_language']}")
            if context.get("frameworks"):
                context_parts.append(f"Frameworks: {', '.join(context['frameworks'])}")
            if context.get("detected_languages"):
                context_parts.append(
                    f"All Languages: {', '.join(context['detected_languages'])}"
                )
            context_text = "\n".join(context_parts)

        prompt = f"""Analyze the following project code and provide a comprehensive assessment.

## Project: {project_name}
{context_text}

## Code Files ({len(code_files)} files):

{files_text}

## Analysis Request

Please provide a detailed analysis in the following JSON format:

{{
    "overall_assessment": {{
        "quality_score": <1-100 integer>,
        "skill_level": "<junior|mid|senior|expert>",
        "summary": "<2-3 sentence overall assessment>"
    }},
    "project_completion": {{
        "status": "<complete|mostly_complete|partial|incomplete|unknown>",
        "confidence": <0-1 float>,
        "evidence": ["<signals suggesting completeness>"],
        "missing_or_risks": ["<signals suggesting the project is incomplete>"]
    }},
    "architecture": {{
        "patterns_used": ["<list of design patterns/architectural patterns identified>"],
        "structure_quality": "<poor|fair|good|excellent>",
        "separation_of_concerns": "<description of how well code is organized>",
        "modularity": "<assessment of code modularity>"
    }},
    "code_quality": {{
        "readability": {{
            "score": <1-10>,
            "observations": ["<specific observations about code readability>"]
        }},
        "maintainability": {{
            "score": <1-10>,
            "observations": ["<observations about maintainability>"]
        }},
        "error_handling": {{
            "score": <1-10>,
            "observations": ["<observations about error handling>"]
        }},
        "documentation": {{
            "score": <1-10>,
            "observations": ["<observations about documentation/comments>"]
        }}
    }},
    "skills_demonstrated": [
        {{
            "skill": "<skill name>",
            "proficiency": "<beginner|intermediate|advanced|expert>",
            "evidence": "<specific code example or pattern that demonstrates this skill>"
        }}
    ],
    "best_practices": {{
        "followed": ["<list of best practices being followed>"],
        "missing": ["<list of best practices that should be implemented>"]
    }},
    "security": {{
        "score": <1-10>,
        "concerns": ["<any security concerns identified>"],
        "recommendations": ["<security improvements to consider>"]
    }},
    "performance": {{
        "score": <1-10>,
        "observations": ["<performance-related observations>"],
        "optimization_opportunities": ["<potential optimizations>"]
    }},
    "testing": {{
        "coverage_assessment": "<none|minimal|partial|good|comprehensive>",
        "test_quality": "<assessment of test quality if tests exist>",
        "recommendations": ["<testing recommendations>"]
    }},
    "recommendations": {{
        "immediate": ["<high-priority improvements>"],
        "short_term": ["<improvements to make soon>"],
        "long_term": ["<future enhancements to consider>"]
    }},
    "notable_code": [
        {{
            "description": "<what makes this code notable>",
            "file": "<file path>",
            "why_notable": "<explanation of why this is good/interesting code>"
        }}
    ]
}}

Provide specific, actionable insights based on the actual code you see. Be constructive and educational in your feedback."""

        return prompt

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse Gemini's response into structured analysis."""
        # Try to extract JSON from the response
        try:
            # Look for JSON block in the response
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # If JSON parsing fails, return raw response with structure
        return {
            "raw_analysis": response,
            "parse_error": "Could not parse structured response",
            "overall_assessment": {
                "quality_score": 0,
                "skill_level": "unknown",
                "summary": "Analysis completed but response parsing failed. See raw_analysis.",
            },
        }

    def get_quick_summary(
        self, file_contents: List[Dict[str, Any]], project_name: str = "Project"
    ) -> str:
        """
        Get a quick natural language summary of the project.
        Useful for generating project descriptions for resumes/portfolios.
        """
        code_files = self._prepare_code_files(file_contents)

        if not code_files:
            return "Unable to analyze project - no code files found."

        # Build a simpler prompt for quick summary
        files_preview = []
        total_chars = 0
        for f in code_files[:10]:  # Limit to 10 files for quick summary
            content = f["content"][:1000]  # First 1000 chars per file
            if total_chars + len(content) > 15000:
                break
            files_preview.append(f"### {f['path']}\n```\n{content}\n```")
            total_chars += len(content)

        prompt = f"""Based on these code files from "{project_name}", write a concise 2-3 sentence summary 
describing what this project does and what technologies/skills it demonstrates. 
Be specific and professional - this will be used for a resume/portfolio.

{chr(10).join(files_preview)}

Write ONLY the summary, nothing else."""

        try:
            return self._call_gemini_with_retry(
                prompt,
                system_instruction="You are a technical writer creating professional project summaries.",
                temperature=0.4,
            )
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                return "Rate limit reached. Please wait a minute and try again."
            return f"Unable to generate summary: {error_msg}"


def analyze_project_with_gemini(
    file_contents: List[Dict[str, Any]],
    project_name: str = "Project",
    project_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to analyze a project with Gemini.

    Args:
        file_contents: List of file info dicts
        project_name: Name of the project
        project_context: Optional context (languages, frameworks detected)

    Returns:
        dict: Analysis results
    """
    analyzer = GeminiAnalyzer()
    return analyzer.analyze_project(file_contents, project_name, project_context)
