"""Resume export: HTML (Jinja2), PDF (WeasyPrint / reportlab fallback), Markdown."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List

from resume.resume_schema import FullResumeData, ResumeContact, ResumeEducation, ResumeExperience, ResumeProject


def _format_date(s: str | None) -> str:
    """Convert YYYY-MM or YYYY-MM-DD to 'Mon YYYY'. Return as-is if already display format or empty."""
    if not s or not isinstance(s, str):
        return ""
    s = s.strip()
    if not s:
        return ""
    if len(s) >= 7 and s[4] == "-":
        try:
            y, m = int(s[:4]), int(s[5:7])
            if 1 <= m <= 12:
                return datetime(y, m, 1).strftime("%b %Y")
        except (ValueError, TypeError):
            pass
    return s  # already display format e.g. "Sep 2022 – Apr 2026"


def _legacy_to_export_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert legacy API shape to template/FullResumeData shape."""
    contact = ResumeContact(name="", email="")
    if isinstance(data.get("contact"), dict):
        c = data["contact"]
        contact = ResumeContact(
            name=(c.get("name") or "").strip(),
            email=(c.get("email") or "").strip(),
            phone=(c.get("phone") or "").strip() or None,
            location=(c.get("location") or "").strip() or None,
            linkedin_url=(c.get("linkedin_url") or "").strip() or None,
            github_url=(c.get("github_url") or "").strip() or None,
            portfolio_url=(c.get("portfolio_url") or "").strip() or None,
        )
    else:
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        links = data.get("links") or []
        link_map = {l.get("label", "").lower(): l.get("url") for l in links if l.get("label")}
        contact = ResumeContact(
            name=name,
            email=email,
            phone=None,
            location=None,
            linkedin_url=link_map.get("linkedin"),
            github_url=link_map.get("github"),
            portfolio_url=link_map.get("website"),
        )

    education_raw = data.get("education") or []
    education = []
    for e in education_raw:
        if isinstance(e, dict):
            dates = (e.get("dates") or "").strip()
            start_date = e.get("start_date") or (dates.split("–")[0].strip() if "–" in dates else (dates or None))
            end_date = e.get("end_date") or (dates.split("–")[1].strip() if "–" in dates and len(dates.split("–")) > 1 else None)
            education.append({
                "institution": (e.get("school") or e.get("institution") or "").strip(),
                "degree": (e.get("degree") or "").strip(),
                "field_of_study": (e.get("major") or e.get("field_of_study") or "").strip(),
                "location": (e.get("location") or "").strip() or None,
                "start_date": start_date,
                "end_date": end_date,
                "is_current": bool(e.get("is_current")),
                "gpa": str(e.get("gpa", "") or "").strip() or None,
            })
        else:
            education.append({
                "institution": "", "degree": "", "field_of_study": "", "location": None,
                "start_date": None, "end_date": None, "is_current": False, "gpa": None,
            })

    experience_raw = data.get("experience") or []
    experience = []
    for ex in experience_raw:
        if isinstance(ex, dict):
            experience.append({
                "company_name": (ex.get("company_name") or "").strip(),
                "job_title": (ex.get("job_title") or "").strip(),
                "location": (ex.get("location") or "").strip() or None,
                "is_remote": bool(ex.get("is_remote")),
                "start_date": ex.get("start_date"),
                "end_date": ex.get("end_date"),
                "is_current": bool(ex.get("is_current")),
                "responsibilities": ex.get("responsibilities") or [],
                "achievements": ex.get("achievements") or [],
            })
        else:
            experience.append({
                "company_name": "", "job_title": "", "location": None, "is_remote": False,
                "start_date": None, "end_date": None, "is_current": False,
                "responsibilities": [], "achievements": [],
            })

    projects_raw = data.get("projects") or []
    projects = []
    for p in projects_raw:
        if isinstance(p, dict):
            projects.append({
                "title": (p.get("title") or "").strip(),
                "technologies": p.get("skills") or p.get("technologies") or [],
                "highlights": p.get("bullets") or p.get("highlights") or [],
                "date_label": (p.get("dates") or p.get("date_label") or "").strip() or None,
            })
        else:
            projects.append({"title": "", "technologies": [], "highlights": [], "date_label": None})

    skills_raw = data.get("skills") or {}
    if isinstance(skills_raw, dict):
        skills = {k: (v if isinstance(v, list) else []) for k, v in skills_raw.items()}
    else:
        skills = {"Skills": skills_raw if isinstance(skills_raw, list) else []}

    return {
        "contact": contact,
        "summary": (data.get("summary") or "").strip() or None,
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": skills,
    }


def render_html(data: Dict[str, Any]) -> str:
    """Render resume data to HTML using Jinja2 template. Accepts legacy or FullResumeData-like dict."""
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    export_data = _legacy_to_export_data(data)
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["format_date"] = lambda s: _format_date(s)
    template = env.get_template("resume_jake.html")
    return template.render(**export_data)


def export_pdf(data: Dict[str, Any]) -> bytes:
    """Render resume to PDF. Uses WeasyPrint if available, else reportlab fallback."""
    try:
        import weasyprint
        html_string = render_html(data)
        return weasyprint.HTML(string=html_string).write_pdf()
    except ImportError:
        return _reportlab_fallback(data)


def _reportlab_fallback(data: Dict[str, Any]) -> bytes:
    """Generate PDF using reportlab when WeasyPrint is not available."""
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    export_data = _legacy_to_export_data(data)
    contact = export_data["contact"]
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=18, spaceAfter=6)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=11, spaceBefore=10, spaceAfter=4)
    body_style = styles["Normal"]

    def esc(s: str) -> str:
        return (s or "").replace("&", "&amp;").replace("<", "&lt;")

    story = []
    if contact.name:
        story.append(Paragraph(esc(contact.name), title_style))
    contact_parts = []
    if contact.phone:
        contact_parts.append(esc(contact.phone))
    if contact.email:
        contact_parts.append(f'<a href="mailto:{contact.email}">{esc(contact.email)}</a>')
    if contact.linkedin_url:
        contact_parts.append(f'<a href="{esc(contact.linkedin_url)}">LinkedIn</a>')
    if contact.github_url:
        contact_parts.append(f'<a href="{esc(contact.github_url)}">GitHub</a>')
    if contact.portfolio_url:
        contact_parts.append(f'<a href="{esc(contact.portfolio_url)}">Portfolio</a>')
    if contact.location:
        contact_parts.append(esc(contact.location))
    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), body_style))
    story.append(Spacer(1, 0.2 * inch))
    if export_data.get("summary"):
        story.append(Paragraph("SUMMARY", heading_style))
        story.append(Paragraph(esc(export_data["summary"]), body_style))
        story.append(Spacer(1, 0.1 * inch))

    if export_data["education"]:
        story.append(Paragraph("EDUCATION", heading_style))
    for edu in export_data["education"]:
        dates = f"{_format_date(edu.get('start_date'))} – {_format_date(edu.get('end_date')) or 'Present'}"
        inst = edu.get("institution", "").strip()
        degree = (edu.get('degree', '') + (' in ' + edu.get('field_of_study', '') if edu.get('field_of_study') else '')).strip()
        loc = (edu.get("location") or "").strip()
        story.append(Paragraph(esc(inst) + " &nbsp;&nbsp;&nbsp;&nbsp; " + esc(dates), body_style))
        if degree or loc:
            story.append(Paragraph(esc(degree) + (" &nbsp;&nbsp;&nbsp;&nbsp; " + esc(loc) if loc else ""), body_style))
        if edu.get("gpa"):
            story.append(Paragraph("GPA: " + esc(edu["gpa"]), body_style))
    if export_data["education"]:
        story.append(Spacer(1, 0.1 * inch))

    if export_data["experience"]:
        story.append(Paragraph("EXPERIENCE", heading_style))
    for exp in export_data["experience"]:
        dates = _format_date(exp.get("start_date")) + " – " + (_format_date(exp.get("end_date")) or "Present")
        story.append(Paragraph("<b>" + esc(exp.get("company_name", "")) + "</b> &nbsp;&nbsp;&nbsp;&nbsp; " + esc(dates), body_style))
        title_loc = esc(exp.get("job_title", ""))
        if exp.get("location"):
            title_loc += " &nbsp;&nbsp;&nbsp;&nbsp; " + esc(exp["location"])
        story.append(Paragraph(title_loc, body_style))
        for b in (exp.get("responsibilities") or []) + (exp.get("achievements") or []):
            if b:
                story.append(Paragraph(esc(b), body_style))
    if export_data["experience"]:
        story.append(Spacer(1, 0.1 * inch))

    if export_data["projects"]:
        story.append(Paragraph("PROJECTS", heading_style))
    for p in export_data["projects"]:
        tech = ", ".join(p.get("technologies") or [])
        title_line = esc(p.get("title", ""))
        if tech:
            title_line += " | " + esc(tech)
        if p.get("date_label"):
            title_line += " &nbsp;&nbsp;&nbsp;&nbsp; " + esc(p["date_label"])
        story.append(Paragraph("<b>" + title_line + "</b>", body_style))
        for h in p.get("highlights") or []:
            if h:
                story.append(Paragraph(esc(h), body_style))
        story.append(Spacer(1, 0.05 * inch))
    if export_data["projects"]:
        story.append(Spacer(1, 0.05 * inch))

    if export_data["skills"]:
        story.append(Paragraph("TECHNICAL SKILLS", heading_style))
        for cat, skill_list in export_data["skills"].items():
            if skill_list:
                story.append(Paragraph(f"<b>{esc(cat)}:</b> {', '.join(esc(s) for s in skill_list)}", body_style))

    doc.build(story)
    return buf.getvalue()


def export_markdown(data: Dict[str, Any]) -> str:
    """Render resume to Markdown string."""
    export_data = _legacy_to_export_data(data)
    contact = export_data["contact"]
    lines = [f"# {contact.name}", ""]
    parts = [contact.email] if contact.email else []
    if contact.phone:
        parts.append(contact.phone)
    if contact.linkedin_url:
        parts.append(contact.linkedin_url)
    if contact.github_url:
        parts.append(contact.github_url)
    if contact.portfolio_url:
        parts.append(contact.portfolio_url)
    if contact.location:
        parts.append(contact.location)
    if parts:
        lines.append(" | ".join(parts))
    lines.append("")

    if export_data["summary"]:
        lines.extend(["## Summary", "", export_data["summary"], ""])

    if export_data["education"]:
        lines.append("## Education")
        for edu in export_data["education"]:
            line = f"**{edu.get('institution', '')}** — {edu.get('degree', '')}"
            if edu.get("field_of_study"):
                line += f" in {edu['field_of_study']}"
            line += f" ({_format_date(edu.get('start_date'))} – {_format_date(edu.get('end_date')) or 'Present'})"
            if edu.get("location"):
                line += f" | {edu['location']}"
            if edu.get("gpa"):
                line += f" | GPA: {edu['gpa']}"
            lines.append(line)
        lines.append("")

    if export_data["experience"]:
        lines.append("## Experience")
        for exp in export_data["experience"]:
            lines.append(f"**{exp.get('company_name', '')}** | {exp.get('job_title', '')} | {_format_date(exp.get('start_date'))} – {_format_date(exp.get('end_date')) or 'Present'}")
            for b in (exp.get("responsibilities") or []) + (exp.get("achievements") or []):
                if b:
                    lines.append(f"- {b}")
        lines.append("")

    if export_data["projects"]:
        lines.append("## Projects")
        for p in export_data["projects"]:
            tech = ", ".join(p.get("technologies") or [])
            lines.append(f"**{p.get('title', '')}** | {tech} | {p.get('date_label') or ''}")
            for h in p.get("highlights") or []:
                if h:
                    lines.append(f"- {h}")
        lines.append("")

    if export_data["skills"]:
        lines.append("## Technical Skills")
        for cat, skill_list in export_data["skills"].items():
            if skill_list:
                lines.append(f"**{cat}:** {', '.join(skill_list)}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
