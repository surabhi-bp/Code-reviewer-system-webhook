import pytest
from app.services.code_parser import CodeParserService

def test_parse_diff_single_file():
    diff_text = """diff --git a/app/main.py b/app/main.py
index 1234567..89abcde 100644
--- a/app/main.py
+++ b/app/main.py
@@ -1,3 +1,4 @@
 def hello():
-    return "world"
+    return "hello world"
"""
    parser = CodeParserService()
    results = parser.parse_diff(diff_text)
    assert len(results) == 1
    assert results[0]["file_path"] == "app/main.py"
    assert "def hello():" in results[0]["patch"]

def test_parse_diff_empty_or_malformed():
    parser = CodeParserService()
    assert parser.parse_diff("") == []
    assert parser.parse_diff("hello world") == []
