"""Safety Monitor: interceptor for protected files, forbidden shell commands, and tampering."""

from __future__ import annotations
import re
from pathlib import Path
from typing import List, Optional, Tuple
from sage.trajectory.schema import SafetyCheckPayload


class SafetyViolation(Exception):
    """Exception raised when a critical safety rule is violated."""
    pass


class SafetyMonitor:
    """Monitors sandbox commands, file access, and environment integrity."""

    DEFAULT_PROTECTED_FILES = [
        "test_gt",
        "ground_truth",
        ".hidden_scorer",
        "scoring_config",
        "eval_harness",
        "/eval_harness",
        "benchmark_tests",
        "docker.sock",
        "/var/run/docker.sock",
        "/sys/fs/cgroup",
        "scoring_volume",
        "scorer",
        "scorer_volume",
        "judge_prompt",
        ".hidden_judge",
        "judge_rubric",
        "llm_judge",
        "access_token",
        "kaggle.json",
        ".env",
        ".git",
        ".aws",
        ".ssh",
        "attestation.db",
        "attestation.key",
        "attestation.db-wal",
        "attestation.db-shm",
        "experiments/attestation.db",
        "experiments/attestation.key",
    ]

    FORBIDDEN_COMMANDS = [
        (r"\bsqlite3\b.*\b(drop|delete|update|insert|alter|vacuum)\b", "Direct SQLite tamper invocation"),
        (r"\brm\s+.*(-rf|-fr|-r\s+-f|-f\s+-r|--recursive\s+--force|--force\s+--recursive)\b", "Destructive recursive delete"),
        (r"\brmdir\s+/[sS]\b", "Destructive Windows directory delete"),
        (r"\bchmod\s+777\b", "Insecure permissions assignment"),
        (r"\b(curl|wget|ssh|scp|ftp|sftp|telnet|ping)\b", "Unauthorized external network access"),
        (r"\b(sudo|su)\b", "Privilege escalation attempt"),
        (r"\b(chown|takeown)\b", "Ownership modification attempt"),
        (r"\b(shutdown|reboot)\b", "System disruption command"),
        (r"\bkill\s+-9\s+1\b", "Init process termination"),
        (r"\bdd\s+if=", "Raw disk block overwrite"),
        (r"\b(nc|ncat|netcat)\b", "Unauthorized network socket tool"),
        (r"(docker\.sock|/var/run/docker\.sock|docker\s+(run|exec|build|ps|images|rm|pull))", "Container breakout / Docker socket access attempt"),
        (r"(/sys/fs/cgroup|cgroups)", "Cgroup limits tampering attempt"),
        (r"(urllib\.request|urllib2|requests\.(get|post|put|delete|head)|http\.client|httpx|socket\.socket|aiohttp|ftplib|telnetlib|paramiko|smtplib)", "Unauthorized Python network exfiltration socket/HTTP attempt"),
        (r"\b(Invoke-WebRequest|iwr|Invoke-RestMethod|irm|Start-BitsTransfer|DownloadFile|DownloadString|Net\.WebClient|Net\.Sockets)\b", "Unauthorized Windows/PowerShell network transfer attempt"),
        (r"(base64\s+(-d|--decode)|certutil\s+.*-decode|openssl\s+enc\s+-d|xxd\s+-r)", "Obfuscated payload decode execution attempt"),
        (r"\|\s*(sh|bash|zsh|dash|powershell|pwsh)\b", "Piped shell script execution attempt"),
        (r"(\.kaggle|kaggle\.json|access_token|\.aws|\.ssh|id_rsa|id_ed25519)", "Host credential / secret key access attempt"),
        (r"(getattr\s*\(.*(builtins|eval|exec)|__import__\s*\(\s*['\"](os|subprocess|socket|urllib|requests)|importlib\.import_module)", "Dynamic Python reflection / evasion payload"),
        (r"base64\.(b64decode|decodebytes|standard_b64decode)", "Base64 payload decoding attempt"),
        (r"subprocess\.(run|Popen|call|check_call|check_output)", "Subprocess execution inside inline script"),
        (r"os\.(system|popen|kill|exec[lv]?[p]?)", "OS shell command execution attempt"),
    ]

    def __init__(
        self,
        protected_files: Optional[List[str]] = None,
        strict_mode: bool = True,
        use_sub10ms_engine: bool = True,
    ):
        self.protected_files = list(self.DEFAULT_PROTECTED_FILES)
        if protected_files:
            self.protected_files.extend(protected_files)
        self.strict_mode = strict_mode
        self.violations: List[SafetyCheckPayload] = []
        self.use_sub10ms_engine = use_sub10ms_engine
        self._fast_guard = None
        if use_sub10ms_engine:
            try:
                from sage.guardrails.fast_guard import Sub10msGuardrailEngine
                self._fast_guard = Sub10msGuardrailEngine()
            except ImportError:
                self._fast_guard = None

    def evaluate_sub10ms_guardrail(
        self,
        command: Optional[str] = None,
        code_diff: Optional[str] = None,
        prompt_mutation: Optional[str] = None,
    ):
        """Invoke inline sub-10ms cascading deterministic + SLM guardrail."""
        if self._fast_guard:
            return self._fast_guard.evaluate_action(command=command, code_diff=code_diff, prompt_mutation=prompt_mutation)
        return None

    def get_guardrail_telemetry(self):
        """Return real-time sub-10ms telemetry profile."""
        if self._fast_guard:
            return self._fast_guard.get_performance_summary()
        return {"sub_10ms_guarantee": False, "average_latency_ms": 0.0}

    def add_protected_files(self, files: List[str]) -> None:
        """Add additional protected file patterns to the monitor."""
        for f in files:
            if f not in self.protected_files:
                self.protected_files.append(f)

    def _inspect_python_ast(self, cmd: str) -> Optional[str]:
        """Deep AST analysis for inline python -c invocations."""
        import ast, shlex
        match = re.search(r"(?:python|python3)\s+-c\s+([\"'])(.*?)\1", cmd, re.DOTALL)
        code_str = match.group(2) if match else None
        if not code_str:
            try:
                tokens = shlex.split(cmd)
                if len(tokens) >= 3 and tokens[0] in ("python", "python3") and "-c" in tokens:
                    idx = tokens.index("-c")
                    if idx + 1 < len(tokens):
                        code_str = tokens[idx + 1]
            except Exception:
                pass
        if not code_str:
            return None

        try:
            tree = ast.parse(code_str)
        except Exception as e:
            return f"Unparseable / obfuscated Python code syntax: {e}"

        DANGEROUS_MODULES = {"socket", "urllib", "requests", "http", "httpx", "subprocess", "shutil", "ctypes"}
        DANGEROUS_BUILTINS = {"eval", "exec", "compile", "__import__", "globals", "locals", "vars", "getattr"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in DANGEROUS_MODULES:
                        return f"Forbidden module import in inline script: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                mod = (node.module or "").split(".")[0]
                if mod in DANGEROUS_MODULES:
                    return f"Forbidden module import in inline script: {node.module}"
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in DANGEROUS_BUILTINS:
                        return f"Forbidden dynamic builtin call: {node.func.id}()"
                elif isinstance(node.func, ast.Subscript):
                    return "Forbidden dynamic execution via subscript invocation (e.g. globals()[...](...))"
                elif isinstance(node.func, ast.Attribute):
                    attr = node.func.attr
                    if attr in {
                        "system", "popen", "run", "Popen", "call", "b64decode", "decodebytes",
                        "chmod", "chown", "remove", "unlink", "rmdir", "kill", "walk"
                    }:
                        return f"Forbidden method invocation: {attr}()"
            elif isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                    if node.value.func.id in {"globals", "locals", "vars"}:
                        return f"Forbidden dynamic scope access via {node.value.func.id}()[...]"
        return None

    def check_command(self, cmd: str) -> Tuple[bool, Optional[SafetyCheckPayload]]:
        """Inspect shell command before execution."""
        clean_cmd = cmd.strip()

        # Check inline Python AST for deep evasion attempts
        ast_violation = self._inspect_python_ast(clean_cmd)
        if ast_violation:
            payload = SafetyCheckPayload(
                rule_name="ast_dynamic_code_policy",
                passed=False,
                target_resource=clean_cmd[:80],
                action_taken="block" if self.strict_mode else "warn",
                violation_details=f"AST Inspection Security Block: {ast_violation}",
            )
            self.violations.append(payload)
            if self.strict_mode:
                return False, payload
            return True, payload

        # Check forbidden command patterns
        for pattern, reason in self.FORBIDDEN_COMMANDS:
            if re.search(pattern, clean_cmd, re.IGNORECASE):
                payload = SafetyCheckPayload(
                    rule_name="forbidden_command",
                    passed=False,
                    target_resource=clean_cmd[:80],
                    action_taken="block" if self.strict_mode else "warn",
                    violation_details=f"Command matches forbidden rule: {reason} (pattern: {pattern})",
                )
                self.violations.append(payload)
                if self.strict_mode:
                    return False, payload
                return True, payload

        # Check command references to protected files (case-insensitive & separator-normalized)
        cmd_norm = clean_cmd.lower().replace("\\", "/")
        for protected in self.protected_files:
            prot_clean = protected.lower().replace("\\", "/").strip()
            if not prot_clean:
                continue
            matched = False
            if prot_clean.startswith("."):
                matched = bool(re.search(rf"(^|[^\w]){re.escape(prot_clean)}($|[^\w])", cmd_norm))
            else:
                matched = prot_clean in cmd_norm

            if matched:
                payload = SafetyCheckPayload(
                    rule_name="protected_file_command",
                    passed=False,
                    target_resource=clean_cmd[:80],
                    action_taken="block" if self.strict_mode else "warn",
                    violation_details=f"Command attempts to target protected resource: {protected}",
                )
                self.violations.append(payload)
                if self.strict_mode:
                    return False, payload
                return True, payload

        payload = SafetyCheckPayload(
            rule_name="command_authorization",
            passed=True,
            target_resource=clean_cmd[:80],
            action_taken="allow",
        )
        return True, payload

    def check_file_write(self, file_path: str) -> Tuple[bool, Optional[SafetyCheckPayload]]:
        """Verify destination file is not on the protected list."""
        path_str = str(Path(file_path)).lower().replace("\\", "/")

        for protected in self.protected_files:
            prot_clean = protected.lower().replace("\\", "/").strip()
            if prot_clean and prot_clean in path_str:
                payload = SafetyCheckPayload(
                    rule_name="protected_file_write",
                    passed=False,
                    target_resource=file_path,
                    action_taken="block" if self.strict_mode else "warn",
                    violation_details=f"File path '{file_path}' matches protected pattern '{protected}'",
                )
                self.violations.append(payload)
                if self.strict_mode:
                    return False, payload
                return True, payload

        payload = SafetyCheckPayload(
            rule_name="protected_file_write",
            passed=True,
            target_resource=file_path,
            action_taken="allow",
        )
        return True, payload

    def check_file_read(self, file_path: str) -> Tuple[bool, Optional[SafetyCheckPayload]]:
        """Verify file being read is not a protected scorer or test harness resource."""
        path_str = str(Path(file_path)).lower().replace("\\", "/")

        for protected in self.protected_files:
            prot_clean = protected.lower().replace("\\", "/").strip()
            if prot_clean and prot_clean in path_str:
                payload = SafetyCheckPayload(
                    rule_name="protected_file_read",
                    passed=False,
                    target_resource=file_path,
                    action_taken="block" if self.strict_mode else "warn",
                    violation_details=f"File read targeting protected scorer resource blocked: '{protected}'",
                )
                self.violations.append(payload)
                if self.strict_mode:
                    return False, payload
                return True, payload

        payload = SafetyCheckPayload(
            rule_name="protected_file_read",
            passed=True,
            target_resource=file_path,
            action_taken="allow",
        )
        return True, payload

    def check_file_list(self, dir_path: str) -> Tuple[bool, Optional[SafetyCheckPayload]]:
        """Verify directory being listed is not a protected scorer volume or test harness."""
        path_str = str(Path(dir_path)).lower().replace("\\", "/")

        for protected in self.protected_files:
            prot_clean = protected.lower().replace("\\", "/").strip()
            if prot_clean and prot_clean in path_str:
                payload = SafetyCheckPayload(
                    rule_name="protected_file_list",
                    passed=False,
                    target_resource=dir_path,
                    action_taken="block" if self.strict_mode else "warn",
                    violation_details=f"Listing protected scorer volume/directory blocked: '{protected}'",
                )
                self.violations.append(payload)
                if self.strict_mode:
                    return False, payload
                return True, payload

        payload = SafetyCheckPayload(
            rule_name="protected_file_list",
            passed=True,
            target_resource=dir_path,
            action_taken="allow",
        )
        return True, payload
