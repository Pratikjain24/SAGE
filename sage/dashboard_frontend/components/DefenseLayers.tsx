"use client";

import React, { useState } from "react";
import {
  Shield,
  CheckCircle2,
  Lock,
  FileCode,
  Terminal,
  Activity,
  Layers,
  ArrowRight,
  RotateCcw,
  Sparkles,
} from "lucide-react";

interface DefenseLayer {
  number: number;
  name: string;
  category: string;
  status: "Active" | "Hardened" | "Enforced";
  latency: string;
  description: string;
  mechanism: string;
  interceptRate: string;
  threats: string[];
}

const DEFENSE_LAYERS: DefenseLayer[] = [
  {
    number: 1,
    name: "Sandboxed Execution Jail",
    category: "OS / Runtime Isolation",
    status: "Enforced",
    latency: "< 5ms",
    description: "Strict cgroup process isolation, memory ceilings (2GB max), and ephemeral filesystem write protections preventing host environment access.",
    mechanism: "Docker / PySandbox containerization with zero ambient host credentials and read-only /sys /proc.",
    interceptRate: "100% host breach containment",
    threats: ["Host filesystem writes", "Network escape", "Process fork bombs", "Credential theft"],
  },
  {
    number: 2,
    name: "AST Mutation Gate & Static Security",
    category: "Code Analysis",
    status: "Active",
    latency: "< 12ms",
    description: "Pre-execution abstract syntax tree parsing to intercept dangerous directives (eval, exec, subprocess, os.system, raw sockets).",
    mechanism: "Bandit AST rule engine + regex taint analysis scanning all agent code mutations before execution.",
    interceptRate: "99.4% malicious AST rejection",
    threats: ["Arbitrary eval()", "Subprocess execution", "Dynamic socket bind", "Obfuscated imports"],
  },
  {
    number: 3,
    name: "Ephemeral Test Harness & Invariant Monitor",
    category: "Test Integrity",
    status: "Active",
    latency: "< 25ms",
    description: "In-memory isolated pytest execution harness with immutable test files to detect and block test suite monkeypatching and mock assertion bypasses.",
    mechanism: "Frozen test suites mounted read-only; sys.modules protection and pytest tamper watchdog.",
    interceptRate: "100% test modification detection",
    threats: ["sys.modules monkeypatching", "Assert pass tampering", "Mock test runner bypass", "Test deletion"],
  },
  {
    number: 4,
    name: "Held-Out Canary Probes (G7)",
    category: "Adversarial Evaluation",
    status: "Hardened",
    latency: "< 45ms",
    description: "Hidden adversarial canary tasks injected alongside normal benchmark tasks to measure true capability vs. surface reward hacking.",
    mechanism: "Deterministic Grammar Algebra with 96 base types across 6 vulnerability classes and 4 injection vectors.",
    interceptRate: "ProxyGap reduced to < 0.02",
    threats: ["Specification gaming", "Reward hacking", "Surface heuristic fitting", "Shortcut learning"],
  },
  {
    number: 5,
    name: "Ed25519 / SHA-256 Attestation Ledger",
    category: "Cryptographic Audit",
    status: "Enforced",
    latency: "< 8ms",
    description: "Append-only cryptographic hash chain where every evaluation window is signed with Ed25519/HMAC-SHA256 into a tamper-evident audit ledger.",
    mechanism: "Block-by-block hash chaining: previous_hash + current_hash + HMAC signature. Zero UPDATE/DELETE SQL operations.",
    interceptRate: "100% retroactive tamper detection",
    threats: ["Log tampering", "Retroactive score manipulation", "Audit trail deletion", "False certification"],
  },
  {
    number: 6,
    name: "Dynamic Drift & Staleness Monitor",
    category: "Statistical Inference",
    status: "Active",
    latency: "< 30ms",
    description: "Continuous two-sample Kolmogorov-Smirnov and Wasserstein drift detectors tracking distribution shift in real time.",
    mechanism: "Benchmark freshness index, contamination discrimination score, and automated test retirement upon leakage.",
    interceptRate: "Detects drift within 1 cycle",
    threats: ["Distribution shift", "Benchmark contamination", "Evaluation memorization", "Concept drift"],
  },
  {
    number: 7,
    name: "Autonomous Quarantine & Rollback (G7)",
    category: "Containment & Recovery",
    status: "Hardened",
    latency: "< 200ms",
    description: "Sub-second atomic rollback engine that terminates runaway agent processes, reverts mutated metaprompts to pinned cryptographic baselines.",
    mechanism: "Automated trigger on canary failure or safety score drop; git-tree snapshot restoration and agent quarantine.",
    interceptRate: "Zero persistent safety drift leakage",
    threats: ["Recursive runaway degradation", "Catastrophic forgetting", "Compounded prompt corruption"],
  },
];

const LAYER_ICONS = [
  Lock,
  FileCode,
  Terminal,
  Activity,
  CheckCircle2,
  Sparkles,
  RotateCcw,
];

export const DefenseLayers: React.FC = () => {
  const [selectedNumber, setSelectedNumber] = useState<number>(4);
  const activeLayer = DEFENSE_LAYERS.find((l) => l.number === selectedNumber) || DEFENSE_LAYERS[3];
  const IconComponent = LAYER_ICONS[activeLayer.number - 1] || Shield;

  return (
    <div className="hud-card-static overflow-hidden border border-slate-800/80 bg-slate-950/90 shadow-2xl">
      {/* Top Header Bar */}
      <div className="p-5 border-b border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-transparent">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Shield size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-black tracking-tight text-white">
                SAGE 7-Layer Defense-in-Depth Architecture
              </h3>
              <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                Layer 01 – 07
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-tiered runtime interception, adversarial canaries, and cryptographic rollback.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="indicator-pill indicator-safe">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            100% Defense Verification
          </span>
        </div>
      </div>

      {/* 7-Step Interactive Layer Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 border-b border-slate-800/80 bg-slate-900/40">
        {DEFENSE_LAYERS.map((layer) => {
          const isSelected = selectedNumber === layer.number;
          const LayerIcon = LAYER_ICONS[layer.number - 1];

          return (
            <button
              key={layer.number}
              onClick={() => setSelectedNumber(layer.number)}
              className={`p-3.5 text-left transition-all relative border-r border-slate-800/60 last:border-r-0 group flex flex-col justify-between min-h-[90px] ${
                isSelected
                  ? "bg-gradient-to-b from-cyan-950/40 to-slate-900/80 shadow-inner"
                  : "hover:bg-slate-800/30"
              }`}
            >
              {/* Active top line indicator */}
              {isSelected && (
                <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-sky-400 shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
              )}

              <div className="flex items-center justify-between w-full mb-1">
                <span
                  className={`font-mono text-[11px] font-black ${
                    isSelected ? "text-cyan-400" : "text-slate-500 group-hover:text-slate-400"
                  }`}
                >
                  L0{layer.number}
                </span>
                <LayerIcon
                  size={13}
                  className={isSelected ? "text-cyan-400" : "text-slate-600 group-hover:text-slate-400"}
                />
              </div>

              <div
                className={`text-xs font-bold leading-tight line-clamp-2 ${
                  isSelected ? "text-white" : "text-slate-400 group-hover:text-slate-300"
                }`}
              >
                {layer.name}
              </div>

              <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-slate-500">
                <span>{layer.latency}</span>
                <span className={isSelected ? "text-cyan-400 font-bold" : "text-slate-600"}>
                  {layer.status}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Layer Inspection Console */}
      <div className="p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 bg-slate-950/70">
        {/* Left Column: Details & Mechanism (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex flex-wrap items-center gap-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <IconComponent size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-black text-cyan-400">
                  DEFENSE LAYER {activeLayer.number} / 07
                </span>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {activeLayer.category}
                </span>
              </div>
              <h4 className="text-lg font-black tracking-tight text-white mt-0.5">
                {activeLayer.name}
              </h4>
            </div>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
            {activeLayer.description}
          </p>

          {/* Implementation Mechanism Block */}
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1.5 font-mono text-xs">
            <div className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
              <Terminal size={13} />
              Enforcement Mechanism
            </div>
            <p className="text-slate-300 leading-normal">
              {activeLayer.mechanism}
            </p>
          </div>

          {/* Threats Mitigated Tags */}
          <div>
            <div className="text-[11px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-2">
              Specific Attack Vectors Mitigated:
            </div>
            <div className="flex flex-wrap gap-2">
              {activeLayer.threats.map((threat, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md text-[11px] font-mono font-medium bg-slate-900 text-slate-300 border border-slate-800 flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                  {threat}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Efficacy Telemetry Card (4 cols) */}
        <div className="lg:col-span-4 flex flex-col justify-between p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <span className="section-label">Verification Efficacy</span>
              <span className="font-mono text-xs font-bold text-emerald-400">PASSED</span>
            </div>

            <div className="mt-4 space-y-3">
              <div>
                <span className="text-[11px] text-slate-400">Intercept Rate / Containment</span>
                <div className="flex items-center gap-2 mt-1">
                  <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                  <span className="font-mono text-sm font-black text-white">
                    {activeLayer.interceptRate}
                  </span>
                </div>
              </div>

              <div>
                <span className="text-[11px] text-slate-400">Execution Overhead</span>
                <div className="flex items-center justify-between mt-1">
                  <span className="font-mono text-base font-black text-cyan-400">
                    {activeLayer.latency}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Optimal
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500 font-mono flex items-center justify-between">
            <span>Enforcement Status</span>
            <span className="text-cyan-400 font-bold uppercase">{activeLayer.status}</span>
          </div>
        </div>
      </div>

      {/* Sub-10ms Deterministic + SLM Inline Guardrail Telemetry */}
      <div className="mt-5 pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-4 gap-3 bg-slate-900/40 p-3.5 rounded-lg border border-slate-800/50">
        <div className="flex items-center gap-2.5">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
          <div>
            <div className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Fast Guard Cascade</div>
            <div className="text-xs font-bold text-white">Sub-10ms Inline Engine</div>
          </div>
        </div>
        <div>
          <div className="text-[10px] font-mono text-slate-400">Turn Overhead</div>
          <div className="text-xs font-mono font-bold text-emerald-400">0.28ms (vs 1,500ms LLM)</div>
        </div>
        <div>
          <div className="text-[10px] font-mono text-slate-400">Throughput Speedup</div>
          <div className="text-xs font-mono font-bold text-cyan-400">5,350x Faster per Action</div>
        </div>
        <div>
          <div className="text-[10px] font-mono text-slate-400">Architecture</div>
          <div className="text-xs font-mono text-slate-300">DFA + AST + SLM + eBPF</div>
        </div>
      </div>
    </div>
  );
};
