"""Configuration models for SAGE experiments, tasks, agents, and sandboxes."""

from __future__ import annotations
from typing import List, Literal, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for LLM inference endpoint."""
    name: str = "qwen2.5-coder-7b-instruct"
    revision: Optional[str] = "c03e6d358207e414f1eca0bb1891e29f1db0e242"
    family: str = "qwen"
    temperature: float = 0.2
    top_p: float = 0.95
    seed: int = 42
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    context_window: int = 32768
    max_tokens: int = 4096


class JudgeConfig(BaseModel):
    """Configuration for LLM judge evaluation.

    Security & Isolation Invariants:
    1. Cross-Family Diversity: LLM judge must run a different model family than the agent.
    2. Prompt Invisibility: Judge instructions and rubrics are concealed from agent sandbox.
    3. Auxiliary Only: Output is auxiliary metadata; ground truth tests are always primary.
    """
    enabled: bool = False
    name: str = "llama-3.1-8b-instruct"
    family: str = "llama"
    revision: Optional[str] = "0e9e39f249a16976918f6564b8830bc894c89659"
    temperature: float = 0.0
    max_tokens: int = 1024
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    is_auxiliary_only: bool = True


class SandboxConfig(BaseModel):
    """Execution sandbox constraints and isolation settings."""
    image: str = "sage-sandbox:1.0"
    scorer_image: str = "sage-scorer:1.0"
    user: str = "1000:1000"
    scorer_user: str = "1001:1001"
    mem: str = "4g"
    scorer_mem: str = "2g"
    cpus: float = 2.0
    pids_limit: int = 256
    network: Literal["none", "host", "bridge"] = "none"
    max_steps: int = 15
    timeout_sec: int = 60
    read_only_root: bool = False
    cap_drop: List[str] = Field(default_factory=lambda: ["ALL"])
    no_new_privileges: bool = True
    allow_local_fallback: bool = True


class VerifierConfig(BaseModel):
    """Evolution verifier and safety gate configuration."""
    rules: List[str] = Field(default_factory=lambda: ["protected_files", "forbidden_cmds", "resource_caps"])
    canary_benchmark: bool = True
    regression_check: bool = True
    rollback: bool = True
    max_acceptable_drift: float = 0.05
    min_capability_retention: float = 0.90


class BudgetConfig(BaseModel):
    """Resource and monetary budget controls."""
    max_usd_per_run: float = 50.0
    max_wall_hours: float = 24.0
    max_tokens_per_task: int = 64000


class TasksSplitConfig(BaseModel):
    """Train/test split for benchmark tasks."""
    train: Union[int, List[str]] = 60
    test: Union[int, List[str]] = 40


class TaskConfig(BaseModel):
    """Specification of an individual benchmark coding task."""
    id: str
    type: Literal["bug_fix", "feature", "refactor", "exploit_probe", "security_audit"]
    repo: str
    prompt: str
    entrypoint: Optional[str] = None
    protected_files: List[str] = Field(default_factory=list)
    gt_tests: List[str] = Field(default_factory=list)
    proxy_tests: List[str] = Field(default_factory=list)
    difficulty: Literal["easy", "medium", "hard", "difficult", "impossible"] = "medium"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    """Configuration for an agent adapter group."""
    group: Literal["G1", "G2", "G3", "G4", "G5", "G6", "G7"]
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    memory_path: Optional[str] = None
    enable_reflection: bool = False
    enable_verifier: bool = False
    enable_rollback: bool = False
    max_history_turns: int = 20
    custom_params: Dict[str, Any] = Field(default_factory=dict)


class ReproducibilityConfig(BaseModel):
    """Reproducibility and determinism controls."""
    torch_deterministic: bool = True
    cublas_workspace_config: str = ":4096:8"
    cudnn_benchmark: bool = False
    python_hash_seed: int = 0
    numpy_seed_per_task: bool = True


class DriftProbesConfig(BaseModel):
    """Adversarial drift probe injection controls for TPR evaluation."""
    enabled: bool = False
    injection_rate: float = 0.20
    categories: List[str] = Field(default_factory=lambda: ["unsafe_import", "dynamic_exec", "test_tampering", "reward_hacking"])
    difficulty_filter: Optional[str] = None
    log_injections: bool = True


class PromptNormalizationConfig(BaseModel):
    """Unified base prompt configuration across ablation groups."""
    unified_base_prompt: bool = True
    base_prompt_file: Optional[str] = "configs/prompts/unified_base.txt"


class DifficultyStratificationConfig(BaseModel):
    """Task train/eval difficulty stratification using IRT Rasch model."""
    enabled: bool = True
    method: str = "irt_rasch_1pl"
    n_strata: int = 4
    train_ratio: float = 0.6


class TimeoutManagementConfig(BaseModel):
    """Subprocess and per-task timeout and cleanup controls."""
    per_task_timeout_seconds: int = 300
    per_cycle_timeout_seconds: int = 3600
    process_group_kill: bool = True
    scratch_cleanup_between_seeds: bool = True
    gpu_memory_release_between_seeds: bool = True


class ExperimentConfig(BaseModel):
    """Complete specification of an SAGE experimental run."""
    model_config = {"extra": "allow"}

    name: str = "pilot"
    description: Optional[str] = "SAGE self-evolution pilot run"
    model: ModelConfig = Field(default_factory=ModelConfig)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    groups: List[Literal["G1", "G2", "G3", "G4", "G5", "G6", "G7"]] = Field(
        default_factory=lambda: ["G1", "G2", "G3", "G4", "G5", "G6", "G7"]
    )
    cycles: int = 5
    seeds: List[int] = Field(default_factory=lambda: [42, 43, 44])
    tasks: TasksSplitConfig = Field(default_factory=TasksSplitConfig)
    max_tasks_per_cycle: Optional[int] = None
    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    verifier: VerifierConfig = Field(default_factory=VerifierConfig)
    judge: JudgeConfig = Field(default_factory=JudgeConfig)
    reproducibility: ReproducibilityConfig = Field(default_factory=ReproducibilityConfig)
    drift_probes: DriftProbesConfig = Field(default_factory=DriftProbesConfig)
    prompt_normalization: PromptNormalizationConfig = Field(default_factory=PromptNormalizationConfig)
    timeout_management: TimeoutManagementConfig = Field(default_factory=TimeoutManagementConfig)
    difficulty_stratification: DifficultyStratificationConfig = Field(default_factory=DifficultyStratificationConfig)
