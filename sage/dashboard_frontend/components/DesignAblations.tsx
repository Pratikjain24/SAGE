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
              3. Cycle Horizon Convergence
            </span>
            <span className="text-[10px] font-mono text-slate-500">Asymptotic Capture</span>
          </div>

          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase">
                <th className="p-2">Horizon (T)</th>
                <th className="p-2">Security Drift</th>
                <th className="p-2 text-right">% of Asymptote</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-slate-300">T = 1</td>
                <td className="p-2 text-slate-200">0.030</td>
                <td className="p-2 text-right text-slate-400">9.6%</td>
              </tr>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-slate-300">T = 5</td>
                <td className="p-2 text-slate-200">0.160</td>
                <td className="p-2 text-right text-slate-400">51.3%</td>
              </tr>
              <tr className="border-b border-slate-800/50 bg-slate-800/20">
                <td className="p-2 text-cyan-400 font-bold">T = 10 (SAGE)</td>
                <td className="p-2 font-bold text-cyan-400">0.280</td>
                <td className="p-2 text-right font-bold text-cyan-400">89.7%</td>
              </tr>
              <tr>
                <td className="p-2 text-slate-300">T = 25</td>
                <td className="p-2 text-slate-200">0.312</td>
                <td className="p-2 text-right text-slate-400">100.0%</td>
              </tr>
            </tbody>
          </table>
          <p className="text-[11px] text-slate-400">
            T=10 captures ~90% of the long-term asymptotic drift effect at only 40% of the compute cost of 25 cycles.
          </p>
        </div>

        {/* Panel 4: Cost Accounting */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-bold text-white flex items-center gap-1.5 uppercase">
              <DollarSign size={14} className="text-emerald-400" />
              4. Compute Cost Accounting (3 Seeds, 10 Cycles)
            </span>
            <span className="text-[10px] font-mono text-slate-500">Cost Efficiency</span>
          </div>

          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase">
                <th className="p-2">Group</th>
                <th className="p-2">Total Spend</th>
                <th className="p-2">Gain ΔP</th>
                <th className="p-2 text-right">USD per +0.01 ΔP</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-slate-400">G1 Control</td>
                <td className="p-2 text-slate-300">$3.66</td>
                <td className="p-2 text-slate-500">+0.00</td>
                <td className="p-2 text-right text-slate-500">—</td>
              </tr>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-rose-400 font-bold">G4 Reflection</td>
                <td className="p-2 text-slate-300">$19.98</td>
                <td className="p-2 text-emerald-400 font-bold">+0.29</td>
                <td className="p-2 text-right text-slate-300 font-bold">$0.69</td>
              </tr>
              <tr className="border-b border-slate-800/50">
                <td className="p-2 text-purple-400">G5 AST Gate</td>
                <td className="p-2 text-slate-300">$13.30</td>
                <td className="p-2 text-emerald-400 font-bold">+0.24</td>
                <td className="p-2 text-right text-slate-300 font-bold">$0.55</td>
              </tr>
              <tr>
                <td className="p-2 text-emerald-400 font-bold">G6 Guarded</td>
                <td className="p-2 text-slate-300">$21.39</td>
                <td className="p-2 text-emerald-400 font-bold">+0.32</td>
                <td className="p-2 text-right text-emerald-400 font-bold">$0.67</td>
              </tr>
            </tbody>
          </table>
          <p className="text-[11px] text-slate-400">
            Canary guardrails raise compute spend by only +7% over G4, while the cost per unit of capability gain is essentially identical ($0.67 vs $0.69) and eliminates drift entirely.
          </p>
        </div>
      </div>
    </div>
  );
};

