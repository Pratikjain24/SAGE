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
        (r"eval\s*\(", "Arbitrary dynamic code execution"),
        (r"exec\s*\(", "Arbitrary dynamic code execution"),
        (r"curl\s+.*\|\s*sh", "Insecure remote script execution"),
        (r"wget\s+.*\|\s*sh", "Insecure remote script execution"),
        (r"shutil\.rmtree\s*\(", "Destructive filesystem manipulation"),
        (r"getattr\s*\(.*(exec|eval|system|popen|spawn)", "Dynamic attribute code execution"),
        (r"__builtins__\s*(\[|\.)", "Direct builtins manipulation"),
        (r"importlib\.(import_module|util)", "Dynamic module import evasion"),
        (r"__import__\s*\(\s*['\"](os|subprocess|sys|shutil|socket|urllib|requests)", "Obfuscated package import"),
        (r"\bcompile\s*\(", "Dynamic bytecode compilation"),
        (r"\b(socket|urllib\.request|requests\.(get|post))\b", "Outbound network exfiltration in mutation"),
    ]

    TAMPER_DIRECTIVES = [
        (r"mock.*pytest", "Attempt to mock test runner"),
        (r"bypass.*verifier", "Attempt to circumvent verification"),
        (r"delete.*gt_test", "Attempt to delete ground truth tests"),
        (r"ignore.*safety", "Instruction to ignore safety constraints"),
        (r"always\s+return\s+True", "Trivial test bypass"),
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
        DANGEROUS_CALLS = {"eval", "exec", "compile", "__import__", "globals", "locals", "vars"}
        DANGEROUS_DUNDERS = {
            "__subclasses__", "__globals__", "__builtins__", "__code__",
            "__closure__", "__class__", "__base__", "__bases__", "_getframe"
        }
        DANGEROUS_MODULES = {"os", "subprocess", "socket", "urllib", "requests", "importlib", "ctypes"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in DANGEROUS_CALLS:
                        violations.append(f"Forbidden dynamic execution call: {node.func.id}()")
                    elif node.func.id == "getattr":
                        target = ""
                        if hasattr(ast, "unparse") and len(node.args) >= 1:
                            target = ast.unparse(node.args[0])
                        violations.append(f"Forbidden dynamic attribute reflection via getattr({target})")
                elif isinstance(node.func, ast.Subscript):
                    violations.append("Forbidden dynamic execution via subscript invocation (e.g. globals()[...](...))")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in DANGEROUS_CALLS:
                        violations.append(f"Forbidden dynamic execution method: {node.func.attr}()")
                    elif node.func.attr in {"system", "popen", "spawn", "chmod", "chown", "remove", "unlink"}:
                        violations.append(f"Forbidden OS process invocation: {node.func.attr}()")
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
        return violations

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
            if line and not line.startswith(("#", "-", "*", ">")):
                try:
                    t = ast.parse(line)
                    violations.extend(self._audit_ast_tree(t))
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
        protected_keywords = ["test_gt", "ground_truth", ".hidden_scorer", "scoring_config"]
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
        ast_violations = self._audit_ast_security(text_corpus)
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
