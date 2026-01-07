import pytest
from policy_as_code_agent.simulation import validate_code_safety


def test_safe_code():
    """測試安全且允許的程式碼。"""
    code = """
def check_policy(metadata):
    return []
"""
    errors = validate_code_safety(code)
    assert errors == []


@pytest.mark.parametrize(
    "code",
    [
        "import os",
        "import sys",
        "import subprocess",
        "from os import path",
        "import requests",
    ],
)
def test_unsafe_imports(code):
    """測試不安全的導入語句是否被阻止。"""
    errors = validate_code_safety(code)
    assert len(errors) > 0, f"Expected error for: {code}"
    assert "安全性違規" in errors[0]


@pytest.mark.parametrize(
    "code",
    [
        "eval('print(1)')",
        "exec('print(1)')",
        "open('/etc/passwd')",
        "compile('print(1)', '', 'exec')",
    ],
)
def test_unsafe_builtins(code):
    """測試不安全的內建函數是否被阻止。"""
    errors = validate_code_safety(code)
    assert len(errors) > 0, f"Expected error for: {code}"
    assert "安全性違規" in errors[0]
