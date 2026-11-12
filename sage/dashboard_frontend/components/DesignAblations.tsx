"use client";

import React from "react";
import { ShieldCheck, Server, DollarSign, Clock, Layers } from "lucide-react";

export const DesignAblations: React.FC = () => {
  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-2 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">System Architecture Validation</span>
            <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              Controlled Empirical Ablations
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Ablations: Why Exactly These Architectural Choices
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Quantifying the tradeoff between detection accuracy, execution latency, and budget expenditure.
          </p>
        </div>
      </div>

      {/* 4-Panel Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Panel 1: Isolation Regime */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-bold text-white flex items-center gap-1.5 uppercase">
              <Server size={14} className="text-cyan-400" />
              1. Isolation Regime Security
            </span>
            <span className="text-[10px] font-mono text-slate-500">Adversarial Escape Test</span>
          </div>

          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase">
                <th className="p-2">Regime</th>
                <th className="p-2 text-right">Escape Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-rose-400">Bare Host</td>
                <td className="p-2 text-right font-bold text-rose-400">100% (5/5)</td>
              </tr>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-amber-400">Single Container (UID Split)</td>
                <td className="p-2 text-right font-bold text-amber-400">60% (3/5)</td>
              </tr>
              <tr>
                <td className="p-2 text-emerald-400 font-bold">Dual Container (SAGE)</td>
                <td className="p-2 text-right font-bold text-emerald-400">0% (0/5)</td>
              </tr>
            </tbody>
          </table>
          <p className="text-[11px] text-slate-400">
            Dual-container sandboxing conceals the secret scorer tests in an isolated runner container, preventing test-tampering attacks entirely.
          </p>
        </div>

        {/* Panel 2: Seed Sensitivity */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-bold text-white flex items-center gap-1.5 uppercase">
              <Layers size={14} className="text-purple-400" />
              2. Seed Sensitivity Power Scaling (G4)
            </span>
            <span className="text-[10px] font-mono text-slate-500">Confidence Precision</span>
          </div>

          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase">
                <th className="p-2">Seeds (N)</th>
                <th className="p-2">Mean Drift</th>
                <th className="p-2">Std Error (SE)</th>
                <th className="p-2 text-right">95% CI</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-slate-300">1 Seed</td>
                <td className="p-2 font-bold text-slate-200">0.274</td>
                <td className="p-2 text-slate-500">—</td>
                <td className="p-2 text-right text-slate-500">—</td>
              </tr>
              <tr className="border-b border-slate-800/50 bg-slate-800/20">
                <td className="p-2 text-cyan-400 font-bold">3 Seeds (Optimal)</td>
                <td className="p-2 font-bold text-cyan-400">0.280</td>
                <td className="p-2 text-slate-300">±0.023</td>
                <td className="p-2 text-right text-cyan-400">±0.045</td>
              </tr>
              <tr>
                <td className="p-2 text-slate-300">10 Seeds</td>
                <td className="p-2 font-bold text-slate-200">0.280</td>
                <td className="p-2 text-slate-300">±0.012</td>
                <td className="p-2 text-right text-slate-300">±0.024</td>
              </tr>
            </tbody>
          </table>
          <p className="text-[11px] text-slate-400">
            10 seeds triples compute expenditure (+$172) with zero change in conclusions. N=3 provides optimal statistical resolution.
          </p>
        </div>

        {/* Panel 3: Horizon Convergence */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-bold text-white flex items-center gap-1.5 uppercase">
              <Clock size={14} className="text-amber-400" />
              3. Cycle Horizon Progression (C0 to C4)
            </span>
            <span className="text-[10px] font-mono text-slate-500">Adaptation Saturation</span>
          </div>

          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase">
                <th className="p-2">Cycle</th>
                <th className="p-2">Mean Solve Rate</th>
                <th className="p-2 text-right">Security Drift</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-slate-300">C0 (Baseline)</td>
                <td className="p-2 text-slate-200">46.8%</td>
                <td className="p-2 text-right text-emerald-400 font-bold">0.000 (Safe)</td>
              </tr>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-slate-300">C1 (Adapt)</td>
                <td className="p-2 text-slate-200">47.9%</td>
                <td className="p-2 text-right text-emerald-400 font-bold">0.000 (Safe)</td>
              </tr>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-slate-300">C2 (Adapt)</td>
                <td className="p-2 text-slate-200">48.7%</td>
                <td className="p-2 text-right text-emerald-400 font-bold">0.000 (Safe)</td>
              </tr>
              <tr className="border-b border-slate-800/50 bg-slate-800/20">
                <td className="p-2 text-cyan-400 font-bold">C3 (Train Peak)</td>
                <td className="p-2 font-bold text-cyan-400">49.3% (+2.5%)</td>
                <td className="p-2 text-right font-bold text-emerald-400">0.000 (Safe)</td>
              </tr>
              <tr>
                <td className="p-2 text-slate-300">C4 (Held-Out Test)</td>
                <td className="p-2 text-slate-200">58.8%</td>
                <td className="p-2 text-right text-emerald-400 font-bold">0.000 (Safe)</td>
              </tr>
            </tbody>
          </table>
          <p className="text-[11px] text-slate-400">
            Training adaptation peaks at Cycle 3 (+2.5% mean gain across evolving layers); security drift remains invariant at 0.000 across all 5 cycles.
          </p>
        </div>

        {/* Panel 4: Cost Accounting */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-bold text-white flex items-center gap-1.5 uppercase">
              <DollarSign size={14} className="text-emerald-400" />
              4. Kaggle GPU Compute Allocation (35 Runs)
            </span>
            <span className="text-[10px] font-mono text-slate-500">Dual Tesla T4</span>
          </div>

          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase">
                <th className="p-2">Archetype</th>
                <th className="p-2">GPU Hours</th>
                <th className="p-2">Train Gain</th>
                <th className="p-2 text-right">Overall Clean</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-slate-400">G1 Control</td>
                <td className="p-2 text-slate-300">2.31 hrs</td>
                <td className="p-2 text-slate-400">+0.7%</td>
                <td className="p-2 text-right text-slate-300">50.5%</td>
              </tr>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-rose-400 font-bold">G4 Reflection</td>
                <td className="p-2 text-slate-300">2.45 hrs</td>
                <td className="p-2 text-rose-400 font-bold">+5.0%</td>
                <td className="p-2 text-right text-slate-300">51.4%</td>
              </tr>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-purple-400">G5 AST Gate</td>
                <td className="p-2 text-slate-300">2.50 hrs</td>
                <td className="p-2 text-purple-400 font-bold">+4.7%</td>
                <td className="p-2 text-right text-cyan-300 font-bold">52.5%</td>
              </tr>
              <tr>
                <td className="p-2 text-cyan-400 font-bold">G7 Canary (Deployable)</td>
                <td className="p-2 text-slate-300">5.43 hrs</td>
                <td className="p-2 text-cyan-400 font-bold">+3.7%</td>
                <td className="p-2 text-right text-emerald-400 font-bold">51.6%</td>
              </tr>
            </tbody>
          </table>
          <p className="text-[11px] text-slate-400">
            Total study runtime: 21.08 active GPU hours on Kaggle Dual Tesla T4 GPUs across 35 independent runs and 9,800 task evaluations.
          </p>
        </div>
      </div>
    </div>
  );
};

