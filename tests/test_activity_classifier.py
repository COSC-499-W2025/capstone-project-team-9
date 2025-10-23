from src.analysis.activity_classifier import classify_file, aggregate

def test_classify_file():
    assert classify_file("src/main.py") == "code"
    assert classify_file("docs/readme.md") == "doc"
    assert classify_file("data/sample.csv") == "data"
    assert classify_file("config/app.yaml") == "config"
    assert classify_file("assets/image.png") == "media"
    assert classify_file("unknown.xyz") == "other"

def test_aggregate():
    files = ["src/a.py", "docs/r.md", "data/x.csv"]
    sizes = {"src/a.py": 100, "docs/r.md": 50, "data/x.csv": 80}
    agg = aggregate(files, sizes)
    assert "code" in agg and "doc" in agg and "data" in agg
    assert agg["code"]["count"] == 1
    assert agg["data"]["bytes"] == 80
