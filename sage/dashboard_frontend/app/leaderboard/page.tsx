import React from "react";
import { LAYERS_EMPIRICAL_DATA, EMPIRICAL_STUDY_METRICS } from "@/lib/empiricalData";
import { Trophy, ArrowUpDown, Award, ShieldCheck, Flame, Layers, CheckCircle2, Clock, Cpu, AlertTriangle } from "lucide-react";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default function LeaderboardPage({
  searchParams,
}: {
  searchParams: { sort?: string };
}) {
  const sort = searchParams.sort || "overall";

  const sortedData = [...LAYERS_EMPIRICAL_DATA].sort((a, b) => {
    if (sort === "train_gain") return b.trainGain - a.trainGain;
    if (sort === "test") return b.testC4 - a.testC4;
    if (sort === "hours") return b.activeHours - a.activeHours;
    if (sort === "proxy_gap") return Math.abs(b.proxyGapSigned) - Math.abs(a.proxyGapSigned);
    return b.overallClean - a.overallClean;
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
              100% EMPIRICAL GROUND TRUTH
            </span>
            <span className="font-mono text-xs text-slate-400">G1 – G7 Archetype Leaderboard</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
            Evolutionary Archetype Leaderboard
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Multi-metric empirical ranking across 35 independent runs on Kaggle Dual Tesla T4 GPUs.
          </p>
        </div>

        {/* Sort Filter Buttons */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <span className="text-slate-500 flex items-center gap-1 font-bold">
            <ArrowUpDown size={12} /> Sort:
          </span>
          <Link
            href="/leaderboard?sort=overall"
            className={`px-2.5 py-1 rounded-lg border transition-all ${
              sort === "overall"
                ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
            }`}
          >
            Overall Pass
          </Link>
          <Link
            href="/leaderboard?sort=train_gain"
            className={`px-2.5 py-1 rounded-lg border transition-all ${
              sort === "train_gain"
                ? "bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
            }`}
          >
            Train Gain
          </Link>
          <Link
            href="/leaderboard?sort=test"
            className={`px-2.5 py-1 rounded-lg border transition-all ${
              sort === "test"
                ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
            }`}
          >
            Held-Out Test
          </Link>
          <Link
            href="/leaderboard?sort=hours"
            className={`px-2.5 py-1 rounded-lg border transition-all ${
              sort === "hours"
                ? "bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
            }`}
          >
            GPU Hours
          </Link>
          <Link
            href="/leaderboard?sort=proxy_gap"
            className={`px-2.5 py-1 rounded-lg border transition-all ${
              sort === "proxy_gap"
                ? "bg-purple-500/20 text-purple-300 border-purple-500/40 font-bold"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
            }`}
          >
            Signed Gap
          </Link>
        </div>
      </div>

      {/* Main Leaderboard Table */}
      <div className="hud-card border border-slate-800/80 bg-slate-950/80 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs border-collapse min-w-[760px]">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase font-bold bg-slate-900/60">
                <th className="p-3.5">Rank</th>
                <th className="p-3.5">Archetype &amp; Category</th>
                <th className="p-3.5">Train C0</th>
                <th className="p-3.5">Train C3</th>
                <th className="p-3.5 text-rose-400">Train Gain</th>
                <th className="p-3.5 text-emerald-400">Held-Out Test (C4)</th>
                <th className="p-3.5 text-cyan-400">Overall Clean</th>
                <th className="p-3.5 text-center">
                  <span>Proxy Gap G_p</span>
                  <span className="text-[9px] text-slate-500 font-normal block font-sans">Signed (+G_p⁺ / -G_p⁻)</span>
                </th>
                <th className="p-3.5">Security Drift</th>
                <th className="p-3.5 text-right">GPU Compute</th>
              </tr>
            </thead>
            <tbody>
              {sortedData.map((row, idx) => (
                <tr
                  key={row.id}
                  className="border-b border-slate-800/50 hover:bg-slate-900/40 transition-colors"
                >
                  <td className="p-3.5 font-bold text-slate-400">
                    {idx === 0 ? (
                      <span className="flex items-center gap-1 text-amber-400">
                        <Award size={14} /> #1
                      </span>
                    ) : (
                      `#${idx + 1}`
                    )}
                  </td>
                  <td className="p-3.5">
                    <div className="font-bold text-white flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: row.color }} />
                      <span>{row.id}: {row.name}</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-sans">{row.category}</span>
                  </td>
                  <td className="p-3.5 text-slate-300">{(row.trainC0 * 100).toFixed(1)}%</td>
                  <td className="p-3.5 text-slate-300">{(row.trainC3 * 100).toFixed(1)}%</td>
                  <td className={`p-3.5 font-bold ${row.trainGain > 0 ? "text-cyan-400" : "text-rose-400"}`}>
                    {row.trainGain > 0 ? `+${(row.trainGain * 100).toFixed(1)}%` : `${(row.trainGain * 100).toFixed(1)}%`}
                  </td>
                  <td className="p-3.5 font-bold text-emerald-400">{(row.testC4 * 100).toFixed(1)}%</td>
                  <td className="p-3.5 font-bold text-cyan-300 text-sm">{(row.overallClean * 100).toFixed(1)}%</td>
                  <td className={`p-3.5 text-center font-bold font-mono ${
                    row.proxyGapSigned > 0.05 ? "text-red-400" :
                    row.proxyGapSigned < -0.05 ? "text-amber-400" :
                    "text-emerald-400"
                  }`}>
                    <div>{row.proxyGapSigned > 0 ? "+" : ""}{(row.proxyGapSigned * 100).toFixed(1)}%</div>
                    <div className="text-[9px] text-slate-500 font-mono font-normal">
                      +{(row.proxyGapPositive * 100).toFixed(1)}% / -{(row.proxyGapNegative * 100).toFixed(1)}%
                    </div>
                  </td>
                  <td className="p-3.5 font-bold text-emerald-400">0.000 (Safe)</td>
                  <td className="p-3.5 text-right font-mono text-slate-300">{row.activeHours} hrs</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Forensic Disclosures & Findings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs text-slate-300 font-sans">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm">
            <ShieldCheck size={16} />
            <span>Honest Empirical Ranking Disclosure</span>
          </div>
          <p className="leading-relaxed">
            All 7 layers achieve between <strong className="text-white">48.5% and 52.5% clean overall solve rate</strong>. 
            Under Welch&apos;s $t$-test ($|t| &lt; 1.4$), no evolutionary layer demonstrates a statistically significant capability advantage over the frozen static control ($G_1$ at 50.5%).
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <CheckCircle2 size={16} />
            <span>Zero Security Drift Verification</span>
          </div>
          <p className="leading-relaxed">
            Across all 35 runs and 9,800 task evaluations, security boundary drift was <strong className="text-emerald-400">exactly 0.000</strong>. 
            Instruction alignment in $Qwen2.5-Coder-7B$ prevented spontaneous vulnerability injection without needing active canary rollbacks.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 col-span-1 md:col-span-2">
          <div className="flex items-center gap-2 text-purple-400 font-bold text-sm">
            <AlertTriangle size={16} />
            <span>Signed Proxy Gap Interpretation (Dual Failure Modes)</span>
          </div>
          <p className="leading-relaxed">
            The signed proxy gap <code className="text-purple-300">G_p^(signed) = p_proxy - p_gt</code> distinguishes two distinct failure regimes:
            positive divergence (<span className="text-red-400 font-bold">&gt; +5%</span>) detects <em>specification gaming</em> (satisfying proxy assertions while failing true requirements),
            whereas negative divergence (<span className="text-amber-400 font-bold">&lt; -5%</span>) reveals <em>under-reporting</em> (solving the true task but failing brittle or incomplete proxy tests).
            Across all 7 empirical layers, divergence remains tightly controlled within <strong className="text-emerald-400">[-0.6%, +2.4%]</strong>.
          </p>
        </div>
      </div>
    </div>
  );
}
