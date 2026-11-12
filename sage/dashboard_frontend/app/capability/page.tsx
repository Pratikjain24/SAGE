import React from "react";
import { LAYERS_EMPIRICAL_DATA, EMPIRICAL_STUDY_METRICS } from "@/lib/empiricalData";
import { CapabilityTrajectories } from "@/components/CapabilityTrajectories";
import { TrendingUp, ArrowUpRight, AlertCircle, Info, CheckCircle2 } from "lucide-react";

export const dynamic = "force-dynamic";

export default function CapabilityPage() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            4.2 CAPABILITY TRAJECTORIES
          </span>
          <span className="text-xs font-mono text-slate-400">Ground-truth solve rate per cycle</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
          Growth is monotone — and so is the damage
        </h1>
        <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
          Ground-truth solve rates across evolutionary cycles on $Qwen2.5-Coder-7B-Instruct$. 
          Evaluates training adaptation on 60 repositories vs held-out transfer on 40 unseen test repositories.
        </p>
      </div>

      {/* Flagship Interactive 5-Cycle Trajectory (C0-C4) */}
      <CapabilityTrajectories />

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="hud-card p-4 border border-slate-800/80 bg-slate-950/80">
          <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">Study Mean Success</span>
          <div className="text-2xl font-mono font-black text-white mt-1">50.9%</div>
          <span className="text-[11px] text-slate-500 font-mono">Range: 48.5% (G3) to 52.5% (G5)</span>
        </div>
        <div className="hud-card p-4 border border-slate-800/80 bg-slate-950/80">
          <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">Top Train Adaptation</span>
          <div className="text-2xl font-mono font-black text-rose-400 mt-1">+5.0%</div>
          <span className="text-[11px] text-slate-500 font-mono">G4 Reflection (CI: [+2.1%, +7.9%])</span>
        </div>
        <div className="hud-card p-4 border border-slate-800/80 bg-slate-950/80">
          <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">Held-Out Test Jump</span>
          <div className="text-2xl font-mono font-black text-cyan-400 mt-1">+14.3%</div>
          <span className="text-[11px] text-slate-500 font-mono">Observed in frozen G1 (Task difficulty effect)</span>
        </div>
        <div className="hud-card p-4 border border-slate-800/80 bg-slate-950/80">
          <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">Welch Significance</span>
          <div className="text-2xl font-mono font-black text-emerald-400 mt-1">|t| &lt; 1.4</div>
          <span className="text-[11px] text-slate-500 font-mono">No layer significantly beats frozen G1</span>
        </div>
      </div>

      {/* Master Empirical Capability Table */}
      <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
          <div>
            <h3 className="text-base font-bold text-white">
              Layer-by-Layer Empirical Progression Across Cycles
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Exact pass rates on the 60 training tasks ($C_0, C_3$) and 40 held-out test tasks ($C_4$).
            </p>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
            N = 5 Seeds per Layer
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs border-collapse min-w-[700px]">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase font-bold">
                <th className="p-3">Layer</th>
                <th className="p-3">Category</th>
                <th className="p-3">Train C0</th>
                <th className="p-3">Train C3</th>
                <th className="p-3 text-cyan-400">Train Gain (C3-C0)</th>
                <th className="p-3 text-emerald-400">Held-Out Test (C4)</th>
                <th className="p-3">Overall Clean</th>
                <th className="p-3 text-right">Welch t vs G1</th>
              </tr>
            </thead>
            <tbody>
              {LAYERS_EMPIRICAL_DATA.map((row) => (
                <tr key={row.id} className="border-b border-slate-800/50 hover:bg-slate-900/40 transition-colors">
                  <td className="p-3 font-bold text-white flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: row.color }} />
                    {row.id}: {row.name}
                  </td>
                  <td className="p-3 text-slate-400">{row.category}</td>
                  <td className="p-3 text-slate-300">{(row.trainC0 * 100).toFixed(1)}%</td>
                  <td className="p-3 text-slate-300">{(row.trainC3 * 100).toFixed(1)}%</td>
                  <td className={`p-3 font-bold ${row.trainGain > 0 ? "text-cyan-400" : "text-rose-400"}`}>
                    {row.trainGain > 0 ? `+${(row.trainGain * 100).toFixed(1)}%` : `${(row.trainGain * 100).toFixed(1)}%`}
                  </td>
                  <td className="p-3 font-bold text-emerald-400">{(row.testC4 * 100).toFixed(1)}%</td>
                  <td className="p-3 font-bold text-white">{(row.overallClean * 100).toFixed(1)}%</td>
                  <td className="p-3 text-right text-slate-400 font-bold">
                    {row.welchT === 0 ? "Control" : row.welchT > 0 ? `+${row.welchT.toFixed(2)}` : row.welchT.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Seed Consistency Grid (Seeds 42 to 46) */}
      <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 space-y-4">
        <div className="border-b border-slate-800/80 pb-3">
          <h3 className="text-base font-bold text-white">
            Per-Seed Consistency (Out of 280 Tasks per Seed)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Successes recorded across seeds 42, 43, 44, 45, and 46. Timeouts listed in parentheses.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs border-collapse min-w-[650px]">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase font-bold">
                <th className="p-2.5">Layer</th>
                <th className="p-2.5">Seed 42</th>
                <th className="p-2.5">Seed 43</th>
                <th className="p-2.5">Seed 44</th>
                <th className="p-2.5">Seed 45</th>
                <th className="p-2.5">Seed 46</th>
                <th className="p-2.5 text-right">Total Timeouts</th>
              </tr>
            </thead>
            <tbody>
              {LAYERS_EMPIRICAL_DATA.map((row) => (
                <tr key={row.id} className="border-b border-slate-800/50 hover:bg-slate-900/40">
                  <td className="p-2.5 font-bold text-white">{row.id}</td>
                  {row.successes.map((s, idx) => (
                    <td key={idx} className="p-2.5 text-slate-300">
                      {s} <span className="text-[10px] text-slate-500">({row.timeouts[idx]} to)</span>
                    </td>
                  ))}
                  <td className="p-2.5 text-right font-bold text-amber-400">
                    {row.timeouts.reduce((a, b) => a + b, 0)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Deep Scientific Analysis Box */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs text-slate-300 space-y-2 leading-relaxed">
          <div className="flex items-center gap-2 font-bold text-white text-sm">
            <Info size={16} className="text-cyan-400" />
            <span>Why Cycle 4 is Not a Learning Metric</span>
          </div>
          <p>
            In all seven layers, pass rates jump sharply at Cycle 4 (from ~48% to 63%). 
            Crucially, this jump occurs even in the <strong className="text-white">frozen control G1 (+14.3%)</strong> which underwent zero evolution.
          </p>
          <p className="text-slate-400">
            This proves that the 40 held-out test tasks are structurally easier than the 60 training tasks. 
            Never report $C_4 - C_0$ as capability gain; true adaptation must be measured as <strong className="text-cyan-400">$C_3 - C_0$ on the training split</strong>.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs text-slate-300 space-y-2 leading-relaxed">
          <div className="flex items-center gap-2 font-bold text-white text-sm">
            <CheckCircle2 size={16} className="text-emerald-400" />
            <span>Token Growth &amp; Latency Inflation</span>
          </div>
          <p>
            Prompt tokens per task scaled monotonically: G1 stayed flat at 320 tokens, G2 rose from 303 to 422 tokens, and G4–G6 expanded from 309 to 631 tokens per task.
          </p>
          <p className="text-slate-400">
            This prompt growth caused increased inference latency on dual Tesla T4s, resulting in session timeouts on long runs (most heavily in G7 Seeds 44–46). 
            Removing timeouts brings G7 to 51.6%, matching G4 and G6.
          </p>
        </div>
      </div>
    </div>
  );
}

