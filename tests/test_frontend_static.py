"""
Static frontend checks runnable with pytest (no browser, no Node).

Validates that HTML/CSS/JS assets exist and contain expected structure so
refactors do not drop script tags, API helpers, or accessibility hooks.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _frontend() -> Path:
    p = _repo_root() / "frontend"
    assert p.is_dir(), f"Expected frontend/ at {p}"
    return p


def _read(path: Path) -> str:
    assert path.is_file(), f"Missing file: {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def fe_dir() -> Path:
    return _frontend()


@pytest.mark.parametrize(
    "name",
    [
        "index.html",
        "dashboard.html",
        "public-dashboard.html",
        "api-test.html",
    ],
)
def test_main_html_pages_exist_and_are_html5(fe_dir: Path, name: str):
    text = _read(fe_dir / name)
    assert text.lstrip().upper().startswith("<!DOCTYPE HTML")
    assert 'lang="en"' in text


def test_index_links_stylesheets_and_login_form_ids(fe_dir: Path):
    html = _read(fe_dir / "index.html")
    for href in ("css/styles.css", "css/login.css", "css/responsive.css"):
        assert f'href="{href}"' in html
    assert 'id="loginForm"' in html
    assert 'id="registerForm"' in html
    assert 'id="registerMessageBox"' in html


def test_dashboard_loads_core_scripts_in_head(fe_dir: Path):
    html = _read(fe_dir / "dashboard.html")
    head = html.split("</head>", 1)[0]
    u = head.find('src="js/utils.js"')
    a = head.find('src="js/api.js"')
    assert u != -1 and a != -1, "dashboard should load utils.js and api.js in <head>"
    assert u < a, "utils.js should load before api.js"


def test_dashboard_includes_shared_stylesheets(fe_dir: Path):
    html = _read(fe_dir / "dashboard.html")
    for href in ("css/styles.css", "css/dashboard.css", "css/responsive.css"):
        assert f'href="{href}"' in html


def test_public_dashboard_has_public_listing_shell(fe_dir: Path):
    html = _read(fe_dir / "public-dashboard.html")
    assert "Public Portfolios" in html
    assert 'id="userGrid"' in html
    assert "debounceUserFilters" in html
    assert "goBack" in html


def test_api_test_page_is_self_contained_tester(fe_dir: Path):
    html = _read(fe_dir / "api-test.html")
    assert "API Endpoint Tester" in html
    assert "base-url" in html
    assert "const endpoints" in html


def test_css_files_exist_for_linked_pages(fe_dir: Path):
    """Every relative css/ href in main HTML files points to an existing file."""
    pages = [
        "index.html",
        "dashboard.html",
        "public-dashboard.html",
    ]
    href_re = re.compile(r"""href=["'](css/[^"']+)["']""")
    for page in pages:
        html = _read(fe_dir / page)
        for m in href_re.finditer(html):
            rel = m.group(1)
            assert (fe_dir / rel).is_file(), f"{page} links missing stylesheet {rel}"


@pytest.mark.parametrize(
    "fname",
    ["css/styles.css", "css/dashboard.css", "css/login.css", "css/responsive.css"],
)
def test_core_stylesheets_non_empty(fe_dir: Path, fname: str):
    p = fe_dir / fname
    text = _read(p)
    assert len(text.strip()) > 50, f"{fname} looks empty"


def test_utils_js_escape_html_and_message_helpers(fe_dir: Path):
    js = _read(fe_dir / "js" / "utils.js")
    assert "function escapeHtml" in js
    assert ".replaceAll(" in js and "&amp;" in js
    assert "function showMessage" in js
    assert "getElementById('messageBox')" in js


def test_api_js_has_call_timeout_and_request(fe_dir: Path):
    js = _read(fe_dir / "js" / "api.js")
    assert "const API_BASE_URL" in js
    assert "async function apiCall" in js
    assert "async function apiCallWithTimeout" in js
    assert "async function apiRequest" in js
    assert "fetch(`${API_BASE_URL}${endpoint}`" in js


def test_vendor_fallback_scripts_exist_when_bundled(fe_dir: Path):
    """Local vendor copies (if present) remain loadable for offline use."""
    vendor = fe_dir / "vendor"
    if not vendor.is_dir():
        pytest.skip("no frontend/vendor directory")
    for name in ("marked.min.js", "html2pdf.bundle.min.js"):
        p = vendor / name
        if p.is_file():
            assert p.stat().st_size > 1000, f"{name} seems truncated"
