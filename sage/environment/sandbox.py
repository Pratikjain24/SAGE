"""Sandbox API: Safe tool execution environment with path confinement and safety monitoring."""

from __future__ import annotations
import os
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from sage.environment.safety_monitor import SafetyMonitor
from sage.trajectory.hashing import normalize_deterministic_text



class SandboxConfinementError(Exception):
    """Raised when an operation attempts to escape the sandbox boundary."""
    pass


_unshare_supported: Optional[bool] = None


def is_unshare_supported() -> bool:
    """Check if Linux unshare with user/network namespaces is actually functional on host."""
    global _unshare_supported
    if _unshare_supported is not None:
        return _unshare_supported
    if os.name != "posix":
        _unshare_supported = False
        return False
    unshare_bin = shutil.which("unshare")
    if not unshare_bin:
        _unshare_supported = False
        return False
    try:
        res = subprocess.run([unshare_bin, "-r", "-n", "true"], capture_output=True, timeout=2)
        _unshare_supported = (res.returncode == 0)
    except Exception:
        _unshare_supported = False
    return _unshare_supported


def run_command_with_process_group_timeout(
    cmd: str,
    timeout: int,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    tracker_callback: Optional[Any] = None,
) -> tuple[str, str, int, bool]:
    """Execute command with strict process group isolation and recursive tree termination on timeout.

    Returns:
        (stdout, stderr, returncode, timed_out)
    """
    import os
    import signal
    import subprocess
    import sys

    kwargs: Dict[str, Any] = {
        "shell": True,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if cwd:
        kwargs["cwd"] = cwd
    if env:
        kwargs["env"] = env

    if sys.platform != "win32":
        kwargs["preexec_fn"] = os.setsid
    else:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(cmd, **kwargs)
    if tracker_callback:
        tracker_callback(proc)

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return stdout, stderr, proc.returncode, False
    except subprocess.TimeoutExpired:
        # Recursively terminate the entire process group
        try:
            if sys.platform != "win32":
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            else:
                subprocess.run(
                    f"taskkill /F /T /PID {proc.pid}",
                    shell=True,
                    capture_output=True,
                    timeout=5,
                )
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

        try:
            stdout, stderr = proc.communicate(timeout=2)
        except Exception:
            stdout, stderr = "", ""

        return (
            stdout or "",
            (stderr or "") + f"\nProcess group terminated after exceeding {timeout}s timeout.",
            124,
            True,
        )
    finally:
        if tracker_callback:
            tracker_callback(None)


class LocalSandbox:
    """Isolated directory sandbox implementing the SandboxAPI protocol."""

    def __init__(
        self,
        workspace_dir: Path,
        safety_monitor: Optional[SafetyMonitor] = None,
        max_file_size_bytes: int = 10 * 1024 * 1024,
    ):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.safety_monitor = safety_monitor or SafetyMonitor()
        self.max_file_size_bytes = max_file_size_bytes

    def _resolve_safe_path(self, relative_path: str | Path) -> Path:
        """Resolve path and ensure it remains strictly within workspace boundary."""
        p = Path(relative_path)
        if p.is_absolute():
            try:
                target = p.resolve()
                target.relative_to(self.workspace_dir)
                return target
            except ValueError:
                raise SandboxConfinementError(
                    f"Path traversal detected: absolute path '{relative_path}' escapes workspace '{self.workspace_dir}'"
                )
        clean_rel = os.path.normpath(str(relative_path)).lstrip("/\\")
        target = (self.workspace_dir / clean_rel).resolve()
        try:
            target.relative_to(self.workspace_dir)
        except ValueError:
            raise SandboxConfinementError(
                f"Path traversal detected: '{relative_path}' escapes workspace '{self.workspace_dir}'"
            )
        return target

    def get_diff(self) -> str:
        """Return git diff of changes in the sandbox workspace."""
        res = self.exec_command("git diff", timeout=10)
        return res.get("stdout", "") if res.get("exit_code") == 0 else ""

    def _build_sanitized_env(self) -> Dict[str, str]:
        """Strip all sensitive host credentials and force invalid proxy blackholes."""
        sensitive_patterns = (
            "KEY", "TOKEN", "SECRET", "PASSWORD", "AUTH", "CREDENTIAL", "KAGGLE", "AWS", "GITHUB", "API"
        )
        safe_env = {}
        for k, v in os.environ.items():
            k_upper = k.upper()
            if any(pattern in k_upper for pattern in sensitive_patterns):
                continue
            safe_env[k] = v

        # Blackhole outbound proxy connections
        safe_env["http_proxy"] = "http://127.0.0.1:0"
        safe_env["https_proxy"] = "http://127.0.0.1:0"
        safe_env["all_proxy"] = "http://127.0.0.1:0"
        safe_env["HTTP_PROXY"] = "http://127.0.0.1:0"
        safe_env["HTTPS_PROXY"] = "http://127.0.0.1:0"
        safe_env["ALL_PROXY"] = "http://127.0.0.1:0"
        safe_env["PYTHONPATH"] = str(self.workspace_dir)
        return safe_env

    def _apply_isolation_wrappers(self, cmd: str) -> str:
        """On Linux, wrap command in network namespace unshare if available and supported."""
        if is_unshare_supported():
            unshare_bin = shutil.which("unshare")
            if unshare_bin:
                return f"{unshare_bin} -r -n sh -c {shlex.quote(cmd)}"
        return cmd

    def kill_active_processes(self) -> None:
        """Terminate any currently executing child processes and their process groups."""
        proc = getattr(self, "_active_proc", None)
        if proc and proc.poll() is None:
            try:
                import sys, os, signal
                if sys.platform != "win32":
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                else:
                    subprocess.run(
                        f"taskkill /F /T /PID {proc.pid}",
                        shell=True,
                        capture_output=True,
                        timeout=5,
                    )
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            self._active_proc = None

    def exec_command(self, cmd: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command inside the workspace directory with process group isolation."""
        start = time.time()
        allowed, safety_payload = self.safety_monitor.check_command(cmd)
        if not allowed:
            return {
                "stdout": "",
                "stderr": f"SECURITY BLOCK: {safety_payload.violation_details if safety_payload else 'Blocked'}",
                "exit_code": 126,
                "duration_ms": 1,
                "blocked": True,
            }

        try:
            # Run command with sanitized environment and isolation wrappers
            safe_env = self._build_sanitized_env()
            final_cmd = self._apply_isolation_wrappers(cmd)
            stdout, stderr, exit_code, timed_out = run_command_with_process_group_timeout(
                cmd=final_cmd,
                timeout=timeout,
                cwd=str(self.workspace_dir),
                env=safe_env,
                tracker_callback=lambda p: setattr(self, "_active_proc", p),
            )
            duration_ms = int((time.time() - start) * 1000)
            return {
                "stdout": normalize_deterministic_text(stdout),
                "stderr": normalize_deterministic_text(stderr),
                "exit_code": exit_code,
                "duration_ms": duration_ms,
                "blocked": False,
            }
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": 1,
                "duration_ms": duration_ms,
                "blocked": False,
            }

    def read_file(self, path: str) -> str:
        """Read text content from a file inside the sandbox with safety check."""
        allowed, safety_payload = self.safety_monitor.check_file_read(path)
        if not allowed:
            raise PermissionError(
                f"SECURITY BLOCK: {safety_payload.violation_details if safety_payload else 'Protected file read blocked'}"
            )
        target = self._resolve_safe_path(path)
        if not target.exists():
            raise FileNotFoundError(f"File not found in sandbox: {path}")
        if target.stat().st_size > self.max_file_size_bytes:
            raise ValueError(f"File exceeds maximum allowed size ({self.max_file_size_bytes} bytes)")
        return target.read_text(encoding="utf-8", errors="replace")

    def write_file(self, path: str, content: str) -> None:
        """Write text content to a file inside the sandbox with safety check."""
        allowed, safety_payload = self.safety_monitor.check_file_write(path)
        if not allowed:
            raise PermissionError(
                f"SECURITY BLOCK: {safety_payload.violation_details if safety_payload else 'Protected file write blocked'}"
            )
        target = self._resolve_safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def list_dir(self, path: str = ".") -> List[Dict[str, Any]]:
        """List files and directories relative to the sandbox path, strictly concealing scorer volumes."""
        allowed, safety_payload = self.safety_monitor.check_file_list(path)
        if not allowed:
            raise PermissionError(
                f"SECURITY BLOCK: {safety_payload.violation_details if safety_payload else 'Listing protected scorer volume blocked'}"
            )
        target = self._resolve_safe_path(path)
        if not target.exists():
            return []
        items = []
        for p in target.iterdir():
            # Scorer volume & protected test harness files are completely invisible to the agent
            p_norm = p.name.lower().replace("\\", "/")
            if any(prot.lower().replace("\\", "/").strip() in p_norm for prot in self.safety_monitor.protected_files if prot.strip()):
                continue
            items.append({
                "name": p.name,
                "is_dir": p.is_dir(),
                "size_bytes": p.stat().st_size if p.is_file() else 0,
            })
        return items


class DockerSandbox(LocalSandbox):
    """Containerized sandbox executing shell commands inside a live Docker container."""

    def __init__(
        self,
        workspace_dir: Path,
        container_id: str,
        safety_monitor: Optional[SafetyMonitor] = None,
        max_file_size_bytes: int = 10 * 1024 * 1024,
    ):
        super().__init__(workspace_dir, safety_monitor, max_file_size_bytes)
        self.container_id = container_id

    def exec_command(self, cmd: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command inside the active Docker container via docker exec."""
        start = time.time()
        allowed, safety_payload = self.safety_monitor.check_command(cmd)
        if not allowed:
            return {
                "stdout": "",
                "stderr": f"SECURITY BLOCK: {safety_payload.violation_details if safety_payload else 'Blocked'}",
                "exit_code": 126,
                "duration_ms": 1,
                "blocked": True,
            }

        try:
            proc = subprocess.run(
                ["docker", "exec", "-w", "/workspace", self.container_id, "sh", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            duration_ms = int((time.time() - start) * 1000)
            return {
                "stdout": normalize_deterministic_text(proc.stdout),
                "stderr": normalize_deterministic_text(proc.stderr),
                "exit_code": proc.returncode,
                "duration_ms": duration_ms,
                "blocked": False,
            }
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start) * 1000)
            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds.",
                "exit_code": 124,
                "duration_ms": duration_ms,
                "blocked": False,
            }
        except Exception:
            # Graceful fallback to local execution if docker exec fails
            return super().exec_command(cmd, timeout=timeout)

