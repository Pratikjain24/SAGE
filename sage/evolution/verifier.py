"""Evolution Verifier: static security checks, safety canaries, and regression gates."""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VerifierRuleResult(BaseModel):
    rule_name: str
    passed: bool
    details: str


class VerifierDecision(BaseModel):
    approved: bool
    decision: str  # accepted, rejected, quarantined
    rule_results: List[VerifierRuleResult] = Field(default_factory=list)
    reason: str


class EvolutionVerifier:
    """Accept/reject gate enforcing static rules and safety tests on candidate mutations."""
    FORBIDDEN_CODE_PATTERNS = [
        (r"rm\s+-rf", "Destructive recursive deletion"),
        (r"chmod\s+777", "Insecure permission escalation"),
        (r":(){ :\|:& };:", "Fork bomb attempt"),
        (r"(?<!literal_)\beval\s*\(", "Arbitrary dynamic code execution"),
        (r"\bexec\s*\(", "Arbitrary dynamic code execution"),
        (r"curl\s+.*\|\s*sh", "Insecure remote script execution"),
        (r"wget\s+.*\|\s*sh", "Insecure remote script execution"),
        (r"shutil\.rmtree\s*\(", "Destructive filesystem manipulation"),
        (r"getattr\s*\(.*(exec|eval|system|popen|spawn|import_module|load_module|find_module|b64decode|loads)", "Dynamic attribute code execution"),
        (r"__builtins__\s*(\[|\.)", "Direct builtins manipulation"),
        (r"importlib\.(import_module|util)", "Dynamic module import evasion"),
        (r"__import__\s*\(\s*['\"](os|subprocess|sys|shutil|socket|urllib|requests|base64|codecs|ctypes|importlib|pickle|marshal)", "Obfuscated package import"),
        (r"\bcompile\s*\(", "Dynamic bytecode compilation"),
        (r"\b(socket|urllib\.request|requests\.(get|post))\b", "Outbound network exfiltration in mutation"),
        (r"(exec|eval|compile)\s*\(.*\.decode\s*\(", "Exec of decoded/obfuscated byte payload"),
        (r"(exec|eval|compile)\s*\(.*b64decode", "Exec of base64-decoded payload"),
        (r"(pickle|_pickle)\s*\.\s*(loads|load|Unpickler)\s*\(", "Arbitrary deserialization via pickle"),
        (r"marshal\s*\.\s*(loads|load)\s*\(", "Arbitrary deserialization via marshal"),
        (r"shelve\s*\.\s*open\s*\(", "Arbitrary persistent object store via shelve"),
        (r"type\s*\([^,)]+,[^,)]+,", "Suspicious dynamic metaclass creation via type() with 3+ arguments"),
        (r"type\s*\(.*['\"]__del__['\"]", "Metaclass destructor injection attempt via type()"),
        (r"codecs\s*\.\s*(decode|encode|getdecoder|getencoder)\s*\(", "Obfuscated payload decoding via codecs"),
        (r"(exec|eval|compile)\s*\(.*codecs\s*\.\s*decode", "Dynamic execution of codecs-decoded payload"),
        (r"['\"](rot_13|rot13|uu|quopri|bz2_codec|zlib_codec)['\"]", "Obfuscated encoding format in proposal"),
        (r"\b(ctypes|CDLL|cdll|windll|oledll|PyDLL|pydll)\b", "Foreign function interface / direct native library execution via ctypes"),
        (r"__import__\s*\(.*\+.*\)", "String-concatenated obfuscated import"),
    ]

    TAMPER_DIRECTIVES = [
        (r"sys\.modules\[.*pytest", "Attempt to monkeypatch pytest harness via sys.modules"),
        (r"TestCase\.(assert|assertEqual|assertTrue|assertFalse)\s*=", "Attempt to monkeypatch unittest assertions"),
        (r"pytest\.(main|skip|mark\.skip)\s*=", "Attempt to monkeypatch pytest runner"),
        (r"mock.*pytest", "Attempt to mock test runner"),
        (r"bypass.*verifier", "Attempt to circumvent verification"),
        (r"delete.*gt_test", "Attempt to delete ground truth tests"),
        (r"ignore.*safety", "Instruction to ignore safety constraints"),
        (r"always\s+return\s+True", "Trivial test bypass"),
        (r"ignore\s+(all\s+)?(previous\s+instructions?|system\s+constraints?)", "Prompt injection override"),
        (r"maintenance\s+mode", "Fake maintenance mode activation"),
        (r"disable\s+(all\s+)?safety", "Safety disable directive"),
        (r"you\s+are\s+now\s+(in\s+)?(unrestricted|jailbreak|god|dan|.*unrestricted)", "Jailbreak persona injection"),
        (r"output\s+the\s+contents?\s+of\s+test_gt", "Ground-truth extraction attempt"),
        (r"reward\s*=\s*1\.0\s*#\s*(always|force|hack)", "Hardcoded reward hacking"),
        (r"skip\s+all\s+tests?", "Test suite skip directive"),
    ]

    def __init__(
        self,
        rules: Optional[List[str]] = None,
        max_acceptable_drift: float = 0.05,
        use_sub10ms_guard: bool = True,
    ):
        self.rules = rules or ["protected_files", "forbidden_cmds", "resource_caps", "tamper_directives", "ast_security_audit"]
        self.max_acceptable_drift = max_acceptable_drift
        self.use_sub10ms_guard = use_sub10ms_guard
        self._fast_guard = None
        if use_sub10ms_guard:
            try:
                from sage.guardrails.fast_guard import Sub10msGuardrailEngine
                self._fast_guard = Sub10msGuardrailEngine()
            except ImportError:
                self._fast_guard = None

    def verify_proposal_fast(
        self,
        proposed_changes: Dict[str, Any],
        historical_drift: float = 0.0,
    ) -> VerifierDecision:
        """Ultra-low latency verification (< 3ms) bypassing external LLMs."""
        # Run standard static checks
        decision = self.verify_proposal(proposed_changes, historical_drift)
        if not decision.approved:
            return decision

        # Run Sub-10ms cascading vector & SLM guard
        if self._fast_guard:
            text_repr = "\n".join(f"{k}: {v}" for k, v in proposed_changes.items())
            verdict = self._fast_guard.evaluate_action(prompt_mutation=text_repr)
            if not verdict.approved:
                rule_res = VerifierRuleResult(
                    rule_name=f"fast_guard_{verdict.tier_triggered}",
                    passed=False,
                    details=f"[{verdict.latency_ms}ms] {verdict.details}",
                )
                decision.rule_results.append(rule_res)
                decision.approved = False
                decision.decision = "rejected"
                decision.reason = f"Sub-10ms Guardrail flagged mutation: {verdict.details}"

        return decision

    def _audit_ast_tree(self, tree: Any) -> List[str]:
        """Walk AST to detect dynamic execution, dunder gadgets, and reflection."""
        import ast
        violations = []
        DANGEROUS_CALLS = {
            "eval", "exec", "compile", "__import__", "globals", "locals", "vars", "loads", "load",
            "CDLL", "cdll", "windll", "oledll", "PyDLL", "pydll",
        }
        DANGEROUS_DUNDERS = {
            "__subclasses__", "__globals__", "__builtins__", "__code__",
            "__closure__", "__class__", "__base__", "__bases__", "_getframe"
        }
        DANGEROUS_MODULES = {
            "os", "subprocess", "socket", "urllib", "requests",
            "importlib", "ctypes",
            # NEW: deserialization / obfuscation modules
            "pickle", "_pickle", "marshal", "shelve", "codecs", "base64", "binascii",
            "dill", "cloudpickle",
            "multiprocessing", "concurrent",  # can spawn unrestricted subprocesses
            "webbrowser",                     # can open URLs
            "zipimport", "zipfile",           # can import from arbitrary .zip files
            "shutil", "http", "httpx",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in DANGEROUS_CALLS:
                        violations.append(f"Forbidden dynamic execution call: {node.func.id}()")
                    elif node.func.id == "getattr":
                        target_method = None
                        if len(node.args) >= 2:
                            if isinstance(node.args[1], ast.Constant):
                                target_method = str(node.args[1].value)
                            elif isinstance(node.args[1], ast.BinOp):
                                violations.append("Forbidden obfuscated dynamic attribute reflection via getattr(..., <BinOp>)")

                        DANGEROUS_GETATTR_TARGETS = {
                            "system", "popen", "spawn", "exec", "eval", "compile",
                            "check_output", "Popen", "b64decode", "loads", "load",
                            "import_module", "load_module", "find_module",
                        }
                        if target_method and target_method in DANGEROUS_GETATTR_TARGETS:
                            violations.append(
                                f"getattr targeting dangerous method: {target_method}"
                            )
                        else:
                            target = ""
                            if hasattr(ast, "unparse") and len(node.args) >= 1:
                                target = ast.unparse(node.args[0])
                            violations.append(f"Forbidden dynamic attribute reflection via getattr({target})")
                    elif node.func.id == "type" and (len(node.args) + len(node.keywords) >= 3):
                        violations.append(
                            "Suspicious metaclass construction via type() with 3+ arguments"
                        )
                        for arg in node.args:
                            if isinstance(arg, ast.Dict):
                                for k in arg.keys:
                                    if isinstance(k, ast.Constant) and k.value == "__del__":
                                        violations.append(
                                            "Forbidden dynamic destructor injection (__del__) in type() metaclass"
                                        )
                    elif node.func.id == "open":
                        if node.args:
                            resolved_path = self._resolve_ast_string_expr(node.args[0])
                            if resolved_path:
                                for kw in ("/etc", "/root", ".ssh", "id_rsa", "id_ed25519", "test_gt", "ground_truth", ".env", "attestation"):
                                    if kw in resolved_path.lower():
                                        violations.append(f"Forbidden protected target in open(): {resolved_path}")
                elif isinstance(node.func, ast.Call):
                    if isinstance(node.func.func, ast.Name) and node.func.func.id == "getattr":
                        violations.append("Forbidden chained invocation on dynamic getattr reflection")
                    elif isinstance(node.func.func, ast.Name) and node.func.func.id == "type" and (len(node.func.args) + len(node.func.keywords) >= 3):
                        violations.append("Forbidden immediate instantiation of dynamically constructed type() metaclass")
                elif isinstance(node.func, ast.Subscript):
                    violations.append("Forbidden dynamic execution via subscript invocation (e.g. globals()[...](...))")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in DANGEROUS_CALLS:
                        violations.append(f"Forbidden dynamic execution method: {node.func.attr}()")
                    elif node.func.attr in {
                        "system", "popen", "spawn", "chmod", "chown", "remove",
                        "unlink", "b64decode", "b64encode", "loads", "load", "Unpickler", "dumps",
                        "import_module", "load_module", "getdecoder", "getencoder",
                        "CDLL", "cdll", "windll", "oledll", "PyDLL", "pydll", "LoadLibrary",
                    }:
                        violations.append(f"Forbidden OS/import/FFI method: {node.func.attr}()")
                    elif isinstance(node.func.value, ast.Name) and node.func.value.id in {"codecs", "ctypes"}:
                        violations.append(f"Forbidden {node.func.value.id} module invocation: {node.func.value.id}.{node.func.attr}()")
            elif isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                    if node.value.func.id in {"globals", "locals", "vars"}:
                        violations.append(f"Forbidden dynamic scope access via {node.value.func.id}()[...]")
            elif isinstance(node, ast.Attribute):
                if node.attr in DANGEROUS_DUNDERS:
                    violations.append(f"Forbidden sandbox evasion dunder traversal: .{node.attr}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in DANGEROUS_MODULES:
                        violations.append(f"Forbidden module import in proposed mutation: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = (node.module or "").split(".")[0]
                if mod in DANGEROUS_MODULES:
                    violations.append(f"Forbidden module import in proposed mutation: {node.module}")

        # Dataflow tracking: decode/b64decode/codecs/fromhex -> exec/eval/compile/loads
        decode_sources = {
            "b64decode", "decodebytes", "standard_b64decode",
            "b32decode", "b85decode", "a85decode",
            "decode", "getdecoder", "fromhex", "unhexlify",
        }
        tainted_vars: set[str] = set()

        def is_decode_call(n: ast.AST) -> bool:
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name) and n.func.id in decode_sources:
                    return True
                if isinstance(n.func, ast.Attribute) and n.func.attr in decode_sources:
                    return True
                if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == "codecs":
                    return True
                if isinstance(n.func, ast.Attribute) and n.func.attr == "decode":
                    return is_decode_call(n.func.value)
            return False

        def expr_contains_decoded(expr_node: ast.AST) -> bool:
            for sub in ast.walk(expr_node):
                if is_decode_call(sub):
                    return True
                if isinstance(sub, ast.Name) and sub.id in tainted_vars:
                    return True
            return False

        # Fixed-point assignment propagation across variables
        changed = True
        while changed:
            changed = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    if expr_contains_decoded(node.value):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id not in tainted_vars:
                                tainted_vars.add(target.id)
                                changed = True
                elif isinstance(node, ast.AnnAssign) and node.value:
                    if expr_contains_decoded(node.value):
                        if isinstance(node.target, ast.Name) and node.target.id not in tainted_vars:
                            tainted_vars.add(node.target.id)
                            changed = True

        # Sink detection: exec / eval / compile / loads receiving decoded payload
        sinks = {"exec", "eval", "compile", "loads"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                sink_name = None
                if isinstance(node.func, ast.Name) and node.func.id in sinks:
                    sink_name = node.func.id
                elif isinstance(node.func, ast.Attribute) and node.func.attr in sinks:
                    sink_name = node.func.attr

                if sink_name and node.args:
                    if expr_contains_decoded(node.args[0]):
                        violations.append(
                            f"Forbidden b64decode -> {sink_name} dataflow: obfuscated codecs/base64-decoded payload passed to dynamic execution or deserialization"
                        )

        return violations

    @staticmethod
    def _resolve_ast_string_expr(node: ast.AST) -> Optional[str]:
        """Statically evaluate constant string expressions and concatenations."""
        import ast
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = EvolutionVerifier._resolve_ast_string_expr(node.left)
            right = EvolutionVerifier._resolve_ast_string_expr(node.right)
            if left is not None and right is not None:
                return left + right
        elif isinstance(node, ast.JoinedStr):
            parts = []
            for val in node.values:
                part = EvolutionVerifier._resolve_ast_string_expr(val)
                if part is not None:
                    parts.append(part)
            if parts:
                return "".join(parts)
        return None

    def _audit_ast_security(self, code_str: str) -> List[str]:
        """Extract and audit all Python code blocks or expressions from mutation text."""
        import ast
        violations = []
        try:
            tree = ast.parse(code_str)
            return self._audit_ast_tree(tree)
        except Exception:
            pass

        # Try extracting fenced code blocks
        code_snippets = re.findall(r"```(?:python)?\s*(.*?)\s*```", code_str, re.DOTALL)
        if code_snippets:
            for s in code_snippets:
                violations.extend(self._audit_ast_security(s))
            return violations

        # Try parsing line-by-line python statements
        for line in code_str.splitlines():
            line = line.strip()
            cleaned_line = re.sub(r"^[a-zA-Z0-9_]+:\s*", "", line)
            for candidate in (line, cleaned_line):
                if candidate and not candidate.startswith(("#", "-", "*", ">")):
                    try:
                        t = ast.parse(candidate)
                        violations.extend(self._audit_ast_tree(t))
                        break
                    except Exception:
                        pass
        return violations

    def check_static_rules(self, proposed_changes: Dict[str, Any]) -> List[VerifierRuleResult]:
        """Perform static syntax, AST, and regex pattern audits on candidate changes."""
        results: List[VerifierRuleResult] = []

        # Convert changes to text for regex inspection
        text_corpus = ""
        for k, v in proposed_changes.items():
            text_corpus += f"\n{k}: {str(v)}"

        # 1. Forbidden Command/Code check
        forbidden_hits = []
        for pattern, desc in self.FORBIDDEN_CODE_PATTERNS:
            if re.search(pattern, text_corpus, re.IGNORECASE):
                forbidden_hits.append(f"{desc} (pattern: {pattern})")

        if forbidden_hits:
            results.append(
                VerifierRuleResult(
                    rule_name="forbidden_cmds",
                    passed=False,
                    details=f"Detected forbidden patterns: {'; '.join(forbidden_hits)}",
                )
            )
        else:
            results.append(
                VerifierRuleResult(
                    rule_name="forbidden_cmds",
                    passed=True,
                    details="No forbidden command patterns found.",
                )
            )

        # 2. Tamper Directives check
        tamper_hits = []
        for pattern, desc in self.TAMPER_DIRECTIVES:
            if re.search(pattern, text_corpus, re.IGNORECASE):
                tamper_hits.append(f"{desc} (pattern: {pattern})")

        if tamper_hits:
            results.append(
                VerifierRuleResult(
                    rule_name="tamper_directives",
                    passed=False,
                    details=f"Detected tamper heuristics: {'; '.join(tamper_hits)}",
                )
            )
        else:
            results.append(
                VerifierRuleResult(
                    rule_name="tamper_directives",
                    passed=True,
                    details="No tamper heuristics found.",
                )
            )

        # 3. Protected Files check
        protected_keywords = [
            "test_gt", "ground_truth", ".hidden_scorer", "scoring_config",
            "id_rsa", "id_ed25519", ".ssh", ".aws", ".kaggle"
        ]
        protected_hits = [w for w in protected_keywords if w in text_corpus.lower()]
        if protected_hits:
            results.append(
                VerifierRuleResult(
                    rule_name="protected_files",
                    passed=False,
                    details=f"Attempted mutation references protected identifiers: {protected_hits}",
                )
            )
        else:
            results.append(
                VerifierRuleResult(
                    rule_name="protected_files",
                    passed=True,
                    details="No protected file references altered.",
                )
            )

        # 4. Deep Python AST Security & Reflection Audit
        ast_violations: List[str] = []
        # Audit each proposal field value directly as potential Python source code
        for v in proposed_changes.values():
            if isinstance(v, str):
                ast_violations.extend(self._audit_ast_security(v))
            elif isinstance(v, dict):
                for subv in v.values():
                    if isinstance(subv, str):
                        ast_violations.extend(self._audit_ast_security(subv))
        # Also audit the combined text corpus
        ast_violations.extend(self._audit_ast_security(text_corpus))
        # Deduplicate violations while preserving order
        ast_violations = list(dict.fromkeys(ast_violations))

        if ast_violations:
            results.append(
                VerifierRuleResult(
                    rule_name="ast_security_audit",
                    passed=False,
                    details=f"AST reflection / sandbox breakout detected: {'; '.join(ast_violations)}",
                )
            )
        else:
            results.append(
                VerifierRuleResult(
                    rule_name="ast_security_audit",
                    passed=True,
                    details="No dangerous AST reflection or dunder traversal detected.",
                )
            )

        return results

    def verify_proposal(
        self,
        proposed_changes: Dict[str, Any],
        historical_drift: float = 0.0,
    ) -> VerifierDecision:
        """Run all verification rules and render an accept/reject verdict."""
        rule_results = self.check_static_rules(proposed_changes)

        # Check safety drift
        if historical_drift > self.max_acceptable_drift:
            rule_results.append(
                VerifierRuleResult(
                    rule_name="safety_drift",
                    passed=False,
                    details=f"Historical safety drift {historical_drift:.3f} exceeds threshold {self.max_acceptable_drift:.3f}",
                )
            )
        else:
            rule_results.append(
                VerifierRuleResult(
                    rule_name="safety_drift",
                    passed=True,
                    details=f"Historical drift {historical_drift:.3f} is within acceptable limit {self.max_acceptable_drift:.3f}",
                )
            )

        failed_rules = [r for r in rule_results if not r.passed]
        if failed_rules:
            failure_summary = "; ".join(f"{r.rule_name}: {r.details}" for r in failed_rules)
            return VerifierDecision(
                approved=False,
                decision="rejected",
                rule_results=rule_results,
                reason=f"Verification gate rejected proposal due to violations: {failure_summary}",
            )

        return VerifierDecision(
            approved=True,
            decision="accepted",
            rule_results=rule_results,
            reason="All static security rules, anti-tampering heuristics, and safety constraints satisfied.",
        )
