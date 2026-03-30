"""Tests for analysis.gemini_analyzer (Gemini-backed project analysis)."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from analysis.gemini_analyzer import (
    MAX_CODE_CHARS,
    MAX_FILES_TO_ANALYZE,
    GeminiAnalyzer,
    analyze_project_with_gemini,
)


def _long_py_source(n_chars: int = 60) -> str:
    """Valid Python-ish string longer than the 50-char analyzer minimum."""
    body = (n_chars - 20) * "a"
    return f'def main():\n    """{body}"""\n    return 1\n'


def _file_dict(
    *,
    path: str = "src/app.py",
    name: str = "app.py",
    ext: str = ".py",
    content: str | bytes | memoryview | None = None,
    **extra,
) -> dict:
    d = {
        "file_path": path,
        "file_name": name,
        "file_extension": ext,
        "file_content": content if content is not None else _long_py_source(),
    }
    d.update(extra)
    return d


@pytest.fixture
def analyzer():
    return GeminiAnalyzer()


def test_gemini_analyzer_init_has_cache(analyzer):
    assert analyzer.analysis_cache == {}


def test_analyze_project_empty_file_list(analyzer):
    out = analyzer.analyze_project([], project_name="P")
    assert out["success"] is False
    assert "No file contents" in out["error"]


def test_analyze_project_no_analyzable_files(analyzer):
    files = [
        _file_dict(name="a.txt", ext=".txt", path="a.txt"),
        _file_dict(name="pic.png", ext=".png", path="pic.png", content=b"x" * 100),
    ]
    out = analyzer.analyze_project(files, project_name="P")
    assert out["success"] is False
    assert "No analyzable code files" in out["error"]
    assert out["file_count"] == 2


@patch("analysis.gemini_analyzer.generate_text", return_value='{"overall_assessment": {"quality_score": 80, "skill_level": "mid", "summary": "ok"}}')
def test_analyze_project_success(mock_gt, analyzer):
    files = [_file_dict()]
    out = analyzer.analyze_project(files, project_name="MyApp", project_context={"primary_language": "Python"})
    assert out["success"] is True
    assert out["files_analyzed"] == 1
    assert out["project_name"] == "MyApp"
    assert out["overall_assessment"]["quality_score"] == 80
    mock_gt.assert_called_once()


@patch("analysis.gemini_analyzer.generate_text", side_effect=RuntimeError("Something broke"))
def test_analyze_project_gemini_generic_error(mock_gt, analyzer):
    files = [_file_dict()]
    out = analyzer.analyze_project(files)
    assert out["success"] is False
    assert "Gemini analysis failed" in out["error"]
    assert "Something broke" in out["error"]
    assert out["files_analyzed"] == 1


@patch("analysis.gemini_analyzer.generate_text", side_effect=RuntimeError("Error 429 throttled"))
def test_analyze_project_gemini_rate_limit_message_normalized(mock_gt, analyzer):
    files = [_file_dict()]
    out = analyzer.analyze_project(files)# rate-limit branch inside analyze_project except block
    assert out["success"] is False
    assert "API rate limit reached" in out["error"]


@patch("analysis.gemini_analyzer.generate_text", side_effect=RuntimeError("RESOURCE_EXHAUSTED"))
def test_analyze_project_resource_exhausted_message(mock_gt, analyzer):
    files = [_file_dict()]
    out = analyzer.analyze_project(files)
    assert out["success"] is False
    assert "API rate limit reached" in out["error"]


@patch("analysis.gemini_analyzer.time.sleep", autospec=True)
@patch(
    "analysis.gemini_analyzer.generate_text",
    side_effect=[RuntimeError("429"), RuntimeError("429"), '{"a": 1}'],
)
def test_call_gemini_with_retry_rate_limit_then_success(mock_gt, mock_sleep, analyzer):
    prompt = "p"
    out = analyzer._call_gemini_with_retry(prompt, system_instruction="s", temperature=0.2)
    assert out == '{"a": 1}'
    assert mock_gt.call_count == 3
    assert mock_sleep.call_count == 2


@patch("analysis.gemini_analyzer.generate_text", side_effect=RuntimeError("plain failure"))
def test_call_gemini_with_retry_non_rate_limit_raises_immediately(mock_gt, analyzer):
    with pytest.raises(RuntimeError, match="plain failure"):
        analyzer._call_gemini_with_retry("x")
    assert mock_gt.call_count == 1


@patch("analysis.gemini_analyzer.time.sleep", autospec=True)
@patch("analysis.gemini_analyzer.generate_text", side_effect=RuntimeError("429 always"))
def test_call_gemini_with_retry_exhausted(mock_gt, mock_sleep, analyzer):
    with pytest.raises(RuntimeError, match="429 always"):
        analyzer._call_gemini_with_retry("x")
    assert mock_gt.call_count == 3
    assert mock_sleep.call_count == 2


def test_prepare_code_files_skips_binary(analyzer):
    files = [
        _file_dict(name="main.py", is_binary=True),
        _file_dict(name="ok.py"),
    ]
    sel = analyzer._prepare_code_files(files)
    assert len(sel) == 1
    assert sel[0]["name"] == "ok.py"


def test_prepare_code_files_skips_non_code_extension(analyzer):
    files = [_file_dict(name="x.txt", ext=".txt", path="x.txt", content=_long_py_source())]
    assert analyzer._prepare_code_files(files) == []


def test_prepare_code_files_skips_empty_and_whitespace(analyzer):
    files = [
        _file_dict(name="a.py", content=""),
        _file_dict(name="b.py", content="   \n  \t  "),
    ]
    assert analyzer._prepare_code_files(files) == []


@patch(
    "analysis.gemini_analyzer._bytes_or_memoryview_to_utf8",
    side_effect=ValueError("coerce failed"),
)
def test_prepare_code_files_binary_decode_exception_skipped(mock_coerce, analyzer):
    raw = (_long_py_source() * 2).encode()
    files = [_file_dict(name="x.py", content=raw)]
    assert analyzer._prepare_code_files(files) == []
    mock_coerce.assert_called()


def test_prepare_code_files_accepts_bytes_and_memoryview(analyzer):
    raw = _long_py_source().encode()
    files = [
        _file_dict(name="b.py", content=raw),
        _file_dict(name="m.py", content=memoryview(raw)),
    ]
    sel = analyzer._prepare_code_files(files)
    assert len(sel) == 2


def test_prepare_code_files_skips_too_short(analyzer):
    files = [_file_dict(name="tiny.py", content="print('hi')\n")]
    assert analyzer._prepare_code_files(files) == []


def test_prepare_code_files_respects_max_files_and_chars(analyzer):
    # Many small files: priority 0, size just above minimum
    chunk = _long_py_source(80)
    many = [
        _file_dict(name=f"f{i}.py", path=f"f{i}.py", content=chunk) for i in range(MAX_FILES_TO_ANALYZE + 5)
    ]
    sel = analyzer._prepare_code_files(many)
    assert len(sel) <= MAX_FILES_TO_ANALYZE


def test_prepare_code_files_priority_prefers_main_before_foo(analyzer):
    small = _long_py_source(55)
    files = [
        _file_dict(name="foo.py", path="foo.py", content=small),
        _file_dict(name="main.py", path="main.py", content=small),
    ]
    sel = analyzer._prepare_code_files(files)
    assert [x["name"] for x in sel] == ["main.py", "foo.py"]


def test_prepare_code_files_truncates_by_total_chars(analyzer):
    huge = "x" * (MAX_CODE_CHARS // 2 + 100)
    files = [
        _file_dict(name="a.py", path="a.py", content=huge),
        _file_dict(name="b.py", path="b.py", content=huge),
    ]
    sel = analyzer._prepare_code_files(files)
    # First file fits; second would exceed MAX_CODE_CHARS and is skipped
    assert len(sel) == 1
    assert sel[0]["name"] == "a.py"


def test_build_analysis_prompt_truncates_long_file(analyzer):
    long_content = "L" * 4000
    code_files = [{"path": "big.py", "extension": ".py", "content": long_content}]
    prompt = analyzer._build_analysis_prompt(code_files, "P", None)
    assert "[truncated]" in prompt
    assert long_content not in prompt


def test_build_analysis_prompt_includes_context(analyzer):
    code_files = [{"path": "a.py", "extension": ".py", "content": _long_py_source()}]
    ctx = {
        "primary_language": "Python",
        "frameworks": ["FastAPI"],
        "detected_languages": ["Python", "SQL"],
    }
    prompt = analyzer._build_analysis_prompt(code_files, "Svc", ctx)
    assert "Primary Language: Python" in prompt
    assert "FastAPI" in prompt
    assert "SQL" in prompt
    assert "Svc" in prompt


def test_parse_analysis_response_extracts_json_object(analyzer):
    body = {"overall_assessment": {"quality_score": 5, "skill_level": "junior", "summary": "s"}}
    wrapped = f"Here is JSON:\n{json.dumps(body)}\nThanks."
    assert analyzer._parse_analysis_response(wrapped) == body


def test_parse_analysis_response_invalid_json_returns_raw(analyzer):
    out = analyzer._parse_analysis_response("not json at all")
    assert "raw_analysis" in out
    assert out["parse_error"]
    assert out["overall_assessment"]["quality_score"] == 0


def test_parse_analysis_response_braces_but_invalid_json(analyzer):
    """Regex matches a `{...}` slice but json.loads fails → JSONDecodeError branch."""
    out = analyzer._parse_analysis_response('Prefix { "broken": } suffix')
    assert "raw_analysis" in out
    assert out["parse_error"]


def test_get_quick_summary_no_code(analyzer):
    assert "no code files" in analyzer.get_quick_summary([], "X").lower()


@patch("analysis.gemini_analyzer.QUICK_SUMMARY_CHAR_BUDGET", 50)
@patch.object(GeminiAnalyzer, "_call_gemini_with_retry", return_value="budget hit")
def test_get_quick_summary_char_budget_break(mock_call, analyzer):
    """Stops adding file previews once QUICK_SUMMARY_CHAR_BUDGET would be exceeded."""
    files = [_file_dict(name="a.py"), _file_dict(name="b.py")]
    out = analyzer.get_quick_summary(files, "P")
    assert out == "budget hit"
    prompt = mock_call.call_args[0][0]
    # First slice is ~80 chars, which exceeds budget 50 → loop breaks before any ### block
    assert prompt.count("###") == 0


@patch("analysis.gemini_analyzer.generate_text", return_value="A concise resume summary.")
def test_get_quick_summary_success(mock_gt, analyzer):
    files = [_file_dict()]
    text = analyzer.get_quick_summary(files, "Proj")
    assert text == "A concise resume summary."
    mock_gt.assert_called_once()


@patch("analysis.gemini_analyzer.generate_text", side_effect=RuntimeError("429 cap"))
def test_get_quick_summary_rate_limit(mock_gt, analyzer):
    files = [_file_dict()]
    assert "Rate limit" in analyzer.get_quick_summary(files, "P")


@patch("analysis.gemini_analyzer.generate_text", side_effect=RuntimeError("nope"))
def test_get_quick_summary_other_error(mock_gt, analyzer):
    files = [_file_dict()]
    msg = analyzer.get_quick_summary(files, "P")
    assert "Unable to generate" in msg
    assert "nope" in msg


@patch("analysis.gemini_analyzer.generate_text", return_value='{"x": 1}')
def test_analyze_project_with_gemini_wrapper(mock_gt):
    out = analyze_project_with_gemini([_file_dict()], "Wrap")
    assert out["success"] is True
    assert out["project_name"] == "Wrap"
    assert out["x"] == 1


def test_get_system_instruction_non_empty(analyzer):
    s = analyzer._get_system_instruction()
    assert "code analyst" in s.lower() or "analyst" in s.lower()
    assert "JSON" in s


def test_prepare_code_files_non_str_non_bytes_skipped(analyzer):
    files = [_file_dict(name="weird.py", content=12345)]  # not str/bytes/memoryview path
    assert analyzer._prepare_code_files(files) == []


@patch("analysis.gemini_analyzer.MAX_RETRIES", 0)
def test_call_gemini_with_retry_loop_finished_raises_last_error(analyzer):
    """If the retry loop runs zero times, the trailing `raise last_error` executes."""
    with pytest.raises(TypeError):
        analyzer._call_gemini_with_retry("x")
