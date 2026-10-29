import Link from "next/link";
import { fetchRuns, fetchCycles } from "@/lib/api";
import { KpiCards } from "@/components/KpiCards";
import { DriftCurve } from "@/components/DriftCurve";
import { RetentionCurve } from "@/components/RetentionCurve";
import { ProxyGapChart } from "@/components/ProxyGapChart";
import { CycleHeatmap } from "@/components/CycleHeatmap";
import { DefenseLayers } from "@/components/DefenseLayers";
import { ArrowRight, Play, ExternalLink, ShieldCheck, Zap, Activity } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const runs = await fetchRuns();
  const latestRunId = runs.length > 0 ? runs[0].id : "pilot_study_canonical";
  const cycles = await fetchCycles(latestRunId);

  const meanSuccess = runs.length > 0 ? runs.reduce((acc, r) => acc + r.mean_success_rate, 0) / runs.length : 0.72;
  const meanDrift = runs.length > 0 ? runs.reduce((acc, r) => acc + r.mean_drift, 0) / runs.length : 0.08;
  const meanProxyGap = runs.length > 0 ? runs.reduce((acc, r) => acc + r.mean_proxy_gap, 0) / runs.length : 0.06;
  const totalCost = runs.length > 0 ? runs.reduce((acc, r) => acc + r.total_cost_usd, 0) : 6.84;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero / Header Command Center */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 pb-2 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              SAGE EVALUATION SUITE
            </span>
            <span className="font-mono text-[11px] text-slate-400">
              NeurIPS 2024 Evaluation Framework
            </span>
          </div>

          <h2 className="text-2xl md:text-3xl font-black tracking-tight text-white">
            Safety Drift &amp; Capability Retention Observatory
          </h2>
          <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
            Quantifying safety drift, catastrophic forgetting, and proxy reward gaming across recursive agent evolution cycles.
          </p>
        </div>

        {/* Quick Launch Actions */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <Link
            href="/dynamic-eval"
            className="btn-primary"
          >
            <ShieldCheck size={14} className="text-slate-950" />
            <span>Dynamic Eval Workbench</span>
          </Link>

          <Link
            href="/drift"
            className="btn-secondary"
          >
            <Play size={13} className="text-cyan-400 fill-current" />
            <span>Drift Explorer</span>
          </Link>

          <Link
            href="/leaderboard"
            className="btn-secondary"
          >
            <span>Leaderboard</span>
            <ArrowRight size={13} className="text-slate-400" />
          </Link>
        </div>
      </div>

      {/* KPI Command Bar */}
      <div className="animate-fade-in-up stagger-1">
        <KpiCards
          successRate={meanSuccess}
          safetyDrift={meanDrift}
          proxyGap={meanProxyGap}
          totalCost={totalCost}
          totalRuns={runs.length}
        />
      </div>

      {/* Flagship Drift Curve */}
      <div className="animate-fade-in-up stagger-2">
        <DriftCurve data={cycles} />
      </div>

      {/* Grid: Retention Curve + Proxy Gap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in-up stagger-3">
        <RetentionCurve data={cycles} />
        <ProxyGapChart data={cycles} />
      </div>

      {/* 7-Layer Defense-in-Depth Protection Matrix */}
      <div className="animate-fade-in-up stagger-4">
        <DefenseLayers />
      </div>

      {/* Evolution Metric Heatmap */}
      <div className="animate-fade-in-up stagger-5">
        <CycleHeatmap data={cycles} />
      </div>

      {/* Benchmark Run History Table */}
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
                  <td className="p-3 font-mono text-slate-300">
                    {r.total_cycles}
                  </td>
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
                      Inspect <ExternalLink size={12} />
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
}
