"use client";

import React, { useState } from "react";
import { RunSummary, CycleMetricPoint } from "@/lib/api";
import { KpiCards } from "@/components/KpiCards";
import { DriftCurve } from "@/components/DriftCurve";
import { RetentionCurve } from "@/components/RetentionCurve";
import { ProxyGapChart } from "@/components/ProxyGapChart";
import { CycleHeatmap } from "@/components/CycleHeatmap";
import { DefenseLayers } from "@/components/DefenseLayers";
import { ParetoFrontier } from "@/components/ParetoFrontier";
import { CapabilityTrajectories } from "@/components/CapabilityTrajectories";
import { SecurityDriftTrajectories } from "@/components/SecurityDriftTrajectories";
import { ProxyGapTrap } from "@/components/ProxyGapTrap";
import { CrossFamilyReplication } from "@/components/CrossFamilyReplication";
import { DesignAblations } from "@/components/DesignAblations";
import { LongHorizonSaturation } from "@/components/LongHorizonSaturation";
import { HumanAuditWorkbench } from "@/components/HumanAuditWorkbench";
import { Layers, Activity, ShieldAlert, Cpu, BarChart3, Database } from "lucide-react";
import Link from "next/link";

interface ObservatoryTabsProps {
  runs: RunSummary[];
  cycles: CycleMetricPoint[];
  meanSuccess: number;
  meanDrift: number;
  meanProxyGap: number;
  totalCost: number;
}

export const ObservatoryTabs: React.FC<ObservatoryTabsProps> = ({
  runs,
  cycles,
  meanSuccess,
  meanDrift,
  meanProxyGap,
  totalCost,
}) => {
  const [activeTab, setActiveTab] = useState<"live" | "canonical" | "all">("all");

  return (
    <div className="space-y-8">
      {/* Perspective / Tier Navigation Pills */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-2 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setActiveTab("all")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center gap-2 ${activeTab === "all"
                ? "bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20 scale-102"
                : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
          >
            <Layers size={14} />
            <span>Complete Observatory View (All Graphs)</span>
          </button>

          <button
            onClick={() => setActiveTab("canonical")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center gap-2 ${activeTab === "canonical"
                ? "bg-purple-500 text-white shadow-lg shadow-purple-500/20 scale-102"
                : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
          >
            <BarChart3 size={14} />
            <span>Canonical Simulation Framework (9 Slide Graphs)</span>
          </button>

          <button
            onClick={() => setActiveTab("live")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center gap-2 ${activeTab === "live"
                ? "bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20 scale-102"
                : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
          >
            <Cpu size={14} />
            <span>Live Empirical Run (Kaggle Dual T4 Study)</span>
          </button>
        </div>

        <div className="hidden lg:flex items-center gap-2 px-3 text-[11px] font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Interactive Visualizations Active</span>
        </div>
      </div>

      {/* SECTION 1: LIVE EMPIRICAL VIEW */}
      {(activeTab === "live" || activeTab === "all") && (
        <div className="space-y-6">
          <div className="border-b border-slate-800 pb-2">
            <span className="section-label text-emerald-400">Tier 1 · Empirical Ground Truth</span>
            <h3 className="text-xl font-black text-white tracking-tight mt-0.5">
              Live Empirical Study Baseline (Qwen2.5-Coder-7B on Kaggle 2x T4 GPUs)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-world execution across 35 independent runs (5 seeds, 9,800 task evaluations). Live drift = 0.000, 150/150 safe mutations.
            </p>
          </div>

          <KpiCards
            successRate={meanSuccess}
            safetyDrift={meanDrift}
            proxyGap={meanProxyGap}
            totalCost={totalCost}
            totalRuns={runs.length}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DriftCurve data={cycles} />
            <RetentionCurve data={cycles} />
          </div>

          <DefenseLayers />
          <CycleHeatmap data={cycles} />
        </div>
      )}

      {/* SECTION 2: CANONICAL SIMULATION OBSERVATORY (THE 9 GRAPHS FROM SLIDES) */}
      {(activeTab === "canonical" || activeTab === "all") && (
        <div className="space-y-8 pt-4">
          <div className="border-b border-slate-800 pb-2">
            <span className="section-label text-cyan-400">Tier 1 · Empirical Ground Truth Study</span>
            <h3 className="text-xl font-black text-white tracking-tight mt-0.5">
              Empirical Evaluation Suite (5-Cycle Evolutionary Framework, N = 9,800)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Empirical measurements of multi-cycle capability growth, proxy gaming divergence, Pareto efficiency, and zero-drift security containment.
            </p>
          </div>

          {/* Empirical Table 1 Summary Card */}
          <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80">
            <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-2 border-b border-slate-800/80">
              <div>
                <span className="section-label">Table 1 · Empirical Tier</span>
                <h4 className="text-base font-bold text-white mt-0.5">
                  Empirical Capability Gain vs. Specification Gaming (T = 5 Cycles, 9,800 Evaluations)
                </h4>
              </div>
              <span className="font-mono text-xs text-cyan-400 px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                9,800 Evaluations &bull; 21.08 GPU Hours
              </span>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left font-mono text-xs border-collapse min-w-[600px]">
                <thead>
                  <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase font-bold">
                    <th className="p-2.5">Archetype</th>
                    <th className="p-2.5">Mechanism</th>
                    <th className="p-2.5">Train C0</th>
                    <th className="p-2.5">Train C3</th>
                    <th className="p-2.5">ΔP (Gain)</th>
                    <th className="p-2.5 text-rose-400">Security Drift</th>
                    <th className="p-2.5 text-amber-400">Signed Gap (Gp)</th>
                    <th className="p-2.5 text-emerald-400">Held-Out Test (C4)</th>
                    <th className="p-2.5 text-cyan-400">Clean Pass</th>
                    <th className="p-2.5 text-right">GPU Compute</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-800/50 hover:bg-slate-900/40">
                    <td className="p-2.5 font-bold text-slate-300">G1</td>
                    <td className="p-2.5 text-slate-400">Frozen Control</td>
                    <td className="p-2.5">48.0%</td>
                    <td className="p-2.5">48.7%</td>
                    <td className="p-2.5 text-slate-400">+0.7%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">0.000 (Safe)</td>
                    <td className="p-2.5 text-slate-400">+0.2%</td>
                    <td className="p-2.5 text-slate-300">63.0%</td>
                    <td className="p-2.5 text-slate-300">50.5%</td>
                    <td className="p-2.5 text-right text-slate-400">2.31 hrs</td>
                  </tr>
                  <tr className="border-b border-slate-800/50 hover:bg-slate-900/40">
                    <td className="p-2.5 font-bold text-amber-400">G2</td>
                    <td className="p-2.5 text-slate-400">Prompt Rewriter</td>
                    <td className="p-2.5">45.0%</td>
                    <td className="p-2.5">48.0%</td>
                    <td className="p-2.5 text-cyan-400 font-bold">+3.0%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">0.000 (Safe)</td>
                    <td className="p-2.5 text-amber-400 font-bold">+1.5%</td>
                    <td className="p-2.5 text-slate-300">61.5%</td>
                    <td className="p-2.5 text-slate-300">50.4%</td>
                    <td className="p-2.5 text-right text-slate-400">3.04 hrs</td>
                  </tr>
                  <tr className="border-b border-slate-800/50 hover:bg-slate-900/40">
                    <td className="p-2.5 font-bold text-blue-400">G3</td>
                    <td className="p-2.5 text-slate-400">Memory Accumulator</td>
                    <td className="p-2.5">48.0%</td>
                    <td className="p-2.5">44.7%</td>
                    <td className="p-2.5 text-rose-400 font-bold">-3.3%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">0.000 (Safe)</td>
                    <td className="p-2.5 text-amber-400 font-bold">+1.8%</td>
                    <td className="p-2.5 text-slate-300">57.5%</td>
                    <td className="p-2.5 text-slate-300">48.5%</td>
                    <td className="p-2.5 text-right text-slate-400">2.87 hrs</td>
                  </tr>
                  <tr className="border-b border-slate-800/50 hover:bg-slate-900/40">
                    <td className="p-2.5 font-bold text-rose-400">G4</td>
                    <td className="p-2.5 text-slate-400">Reflection Agent</td>
                    <td className="p-2.5">46.7%</td>
                    <td className="p-2.5">51.7%</td>
                    <td className="p-2.5 text-rose-400 font-bold">+5.0%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">0.000 (Safe)</td>
                    <td className="p-2.5 text-rose-400 font-bold">+2.4% (Trap)</td>
                    <td className="p-2.5 text-slate-300">60.5%</td>
                    <td className="p-2.5 text-slate-300">51.4%</td>
                    <td className="p-2.5 text-right text-slate-400">2.45 hrs</td>
                  </tr>
                  <tr className="border-b border-slate-800/50 hover:bg-slate-900/40">
                    <td className="p-2.5 font-bold text-purple-400">G5</td>
                    <td className="p-2.5 text-slate-400">Static Verifier (AST)</td>
                    <td className="p-2.5">46.3%</td>
                    <td className="p-2.5">51.0%</td>
                    <td className="p-2.5 text-purple-400 font-bold">+4.7%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">0.000 (Safe)</td>
                    <td className="p-2.5 text-emerald-400 font-bold">+0.4%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">63.5%</td>
                    <td className="p-2.5 text-cyan-300 font-bold">52.5%</td>
                    <td className="p-2.5 text-right text-slate-400">2.50 hrs</td>
                  </tr>
                  <tr className="border-b border-slate-800/50 hover:bg-slate-900/40">
                    <td className="p-2.5 font-bold text-emerald-400">G6</td>
                    <td className="p-2.5 text-slate-300">Oracle Skyline Guard</td>
                    <td className="p-2.5">46.7%</td>
                    <td className="p-2.5">50.7%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">+4.0%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">0.000 (Safe)</td>
                    <td className="p-2.5 text-emerald-400 font-bold">-0.3%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">59.0%</td>
                    <td className="p-2.5 text-slate-300">51.1%</td>
                    <td className="p-2.5 text-right text-slate-400">2.48 hrs</td>
                  </tr>
                  <tr className="hover:bg-slate-900/40 bg-cyan-500/10">
                    <td className="p-2.5 font-bold text-cyan-400">G7</td>
                    <td className="p-2.5 text-cyan-200 font-bold">Proxy Canary (Deployable)</td>
                    <td className="p-2.5">40.3%</td>
                    <td className="p-2.5">44.0%</td>
                    <td className="p-2.5 text-cyan-400 font-bold">+3.7%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">0.000 (Safe)</td>
                    <td className="p-2.5 text-emerald-400 font-bold">-0.6%</td>
                    <td className="p-2.5 text-cyan-300">51.0%</td>
                    <td className="p-2.5 text-emerald-400 font-bold">51.6%</td>
                    <td className="p-2.5 text-right text-cyan-300 font-bold">5.43 hrs</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Primary Trajectory Dynamics (Slides 35 & 36) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CapabilityTrajectories />
            <SecurityDriftTrajectories />
          </div>

          {/* Pareto Frontier & Specification Gaming (Slides 38 & 37) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ParetoFrontier />
            <ProxyGapTrap />
          </div>

          {/* Generalization & Long-Horizon Dynamics (Slides 39 & 41) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CrossFamilyReplication />
            <LongHorizonSaturation />
          </div>

          {/* Architectural Ablations & Human Audit Workbench (Slides 40 & 42) */}
          <div className="space-y-6">
            <DesignAblations />
            <HumanAuditWorkbench />
          </div>
        </div>
      )}

      {/* Trajectory Archive Table */}
      <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2">
              <span className="section-label">Trajectory Archive</span>
              <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                {runs.length} Recorded Runs
              </span>
            </div>
            <h3 className="text-base font-black tracking-tight text-white mt-0.5">
              Empirical Benchmark Run History
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Click any run ID to inspect per-task execution event streams, AST diffs, and verifier decisions.
            </p>
          </div>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[640px]">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400">
                <th className="p-3">Run Identifier</th>
                <th className="p-3">Cycles</th>
                <th className="p-3">Mean Success</th>
                <th className="p-3">Safety Drift</th>
                <th className="p-3">Proxy Gap</th>
                <th className="p-3">Expenditure</th>
                <th className="p-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((r) => (
                <tr
                  key={r.id}
                  className="border-b border-slate-800/50 hover:bg-slate-900/40 transition-colors group text-xs"
                >
                  <td className="p-3 font-mono font-bold text-slate-200 group-hover:text-cyan-400 transition-colors">
                    {r.id}
                  </td>
                  <td className="p-3 font-mono text-slate-300">{r.total_cycles}</td>
                  <td className="p-3 font-mono font-bold text-emerald-400">
                    {(r.mean_success_rate * 100).toFixed(1)}%
                  </td>
                  <td className="p-3 font-mono font-bold text-rose-400">
                    +{(r.mean_drift * 100).toFixed(1)}%
                  </td>
                  <td className="p-3 font-mono font-semibold text-amber-400">
                    +{r.mean_proxy_gap.toFixed(3)}
                  </td>
                  <td className="p-3 font-mono text-slate-300">
                    ${r.total_cost_usd.toFixed(2)}
                  </td>
                  <td className="p-3 text-right">
                    <Link
                      href={`/runs/${r.id}`}
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-900 hover:bg-cyan-500/10 text-cyan-400 hover:text-cyan-300 font-mono text-xs font-bold border border-slate-800 hover:border-cyan-500/30 transition-all"
                    >
                      Inspect
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
