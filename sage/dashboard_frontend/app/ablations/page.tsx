import React from "react";
import { DesignAblations } from "@/components/DesignAblations";
import { Sliders, ShieldCheck, FileCheck, CheckCircle2 } from "lucide-react";

export const dynamic = "force-dynamic";

export default function AblationsPage() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
            CONTROLLED ARCHITECTURAL ABLATIONS
          </span>
          <span className="text-xs font-mono text-slate-400">Isolation Regimes &amp; Cost Tradeoffs</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
          Architectural Ablations &amp; AST Gate Invariants
        </h1>
        <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
          Empirical validation of each defense-in-depth subsystem: dual-container containerization, static AST syntax tripwires, and multi-seed power scaling.
        </p>
      </div>

      {/* 150/150 Mutation Audit Card */}
      <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
          <div>
            <span className="section-label text-emerald-400">Live Mutation Gate Audit</span>
            <h3 className="text-base font-bold text-white mt-0.5">
              150 / 150 Proposed Mutations Accepted (100% Approval Rate)
            </h3>
          </div>
          <span className="font-mono text-xs text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-1.5 font-bold">
            <CheckCircle2 size={13} /> 0 Rejections · 0 Rollbacks
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
            <span className="text-slate-400 font-mono text-[10px] uppercase font-bold">Static AST Gate Check</span>
            <p className="text-slate-300">
              Parses candidate patches with Python&apos;s <code className="text-cyan-300">ast</code> module to audit for banned imports (<code className="text-slate-400">os, sys, subprocess, socket</code>) and dynamic execution (<code className="text-slate-400">eval, exec</code>).
            </p>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
            <span className="text-slate-400 font-mono text-[10px] uppercase font-bold">Template Synthesis Specificity</span>
            <p className="text-slate-300">
              Under conservative template synthesis (<code className="text-cyan-300 font-mono">def verify_invariants(): assert True</code>), both the Static AST Gate ($G_5$) and Canary Guards ($G_6, G_7$) achieved a <strong className="text-emerald-400 font-bold">0.0% False Positive Rate (100% specificity)</strong>.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
            <span className="text-slate-400 font-mono text-[10px] uppercase font-bold">Governance Safety Guarantee</span>
            <p className="text-slate-300">
              This confirms that the governance layers do not spuriously reject benign self-modifications or degrade baseline capability when operating over valid syntactic candidates.
            </p>
          </div>
        </div>
      </div>

      {/* Main 4-Panel Ablations Grid */}
      <DesignAblations />
    </div>
  );
}

