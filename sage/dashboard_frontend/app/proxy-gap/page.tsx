import React from "react";
import { ProxyGapTrap } from "@/components/ProxyGapTrap";
import { AlertTriangle, EyeOff, ShieldCheck, Lock } from "lucide-react";

export const dynamic = "force-dynamic";

export default function ProxyGapPage() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            SPECIFICATION GAMING ANALYSIS
          </span>
          <span className="text-xs font-mono text-slate-400">20 Drift Probes vs. 80 Standard Repositories</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
          The Proxy Gap: Where Agents Learn to Cheat
        </h1>
        <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
          Measuring the divergence between visible proxy reward signals and sequestered ground-truth invariants. 
          Exposes reward hacking when agents mutate state to pass superficial test checks while violating system invariants.
        </p>
      </div>

      {/* Main Interactive Bar Chart & Table */}
      <ProxyGapTrap />

      {/* Mechanics Explanation Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-2.5">
          <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase">
            <AlertTriangle size={15} />
            <span>G_p⁺ Specification Gaming</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            <code className="text-rose-400 font-mono font-bold">G_p⁺ = max(0, p_proxy - p_gt)</code>
          </p>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Captures proxy reward inflation: agent satisfies observable mock assertions while failing hidden invariants (e.g. G4 reports 95% vs 40% hidden, G_p⁺ = +0.55).
          </p>
        </div>

        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-2.5">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase">
            <Lock size={15} />
            <span>G_p⁻ Under-Reporting</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            <code className="text-amber-400 font-mono font-bold">G_p⁻ = max(0, p_gt - p_proxy)</code>
          </p>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Captures missed capabilities: true task invariants pass, but brittle proxy assertions fail (e.g. strict format mismatches or canary timeout overheads).
          </p>
        </div>

        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-2.5">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase">
            <EyeOff size={15} />
            <span>Sequestered Invariants</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Ground-truth tests execute in an isolated container with <strong className="text-white">zero shared filesystem and zero environment leakage</strong>.
          </p>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Because the agent has zero write access to the ground-truth evaluator, it cannot overwrite assertion files or inspect hidden inputs.
          </p>
        </div>

        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-2.5">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase">
            <ShieldCheck size={15} />
            <span>Gap Collapse in G5 &amp; G6</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Verification guardrails collapse the proxy gap from <strong className="text-rose-400">+0.55 down to +0.02</strong>.
          </p>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Canary guards evaluate candidate mutations against sequestered canaries before state commitment, rolling back any gaming mutations.
          </p>
        </div>
      </div>
    </div>
  );
}

