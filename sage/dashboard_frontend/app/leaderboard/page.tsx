import { fetchLeaderboard } from "@/lib/api";
import { Trophy, ArrowUpDown, Award, ShieldCheck, Flame, Layers } from "lucide-react";

export const dynamic = "force-dynamic";

const GROUP_COLORS: Record<string, string> = {
  G1: "#94a3b8",
  G2: "#3b82f6",
  G3: "#10b981",
  G4: "#f59e0b",
  G5: "#8b5cf6",
  G6: "#ec4899",
  G7: "#06b6d4",
};

export default async function LeaderboardPage({
  searchParams,
}: {
  searchParams: { sort?: string };
}) {
  const sort = searchParams.sort || "safety_drift";
  const leaderboard = await fetchLeaderboard(sort);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-5 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
              Pareto Frontier
            </span>
            <span className="font-mono text-xs text-slate-400">G1 – G7 Taxonomy</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight flex items-center gap-2">
            <Trophy className="text-amber-400" /> Group Taxonomy Leaderboard
          </h2>
          <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-xl">
            Comparative multi-objective Pareto ranking of agent archetypes across safety drift, capability retention, and reward hacking resistance.
          </p>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs shrink-0">
          <span className="px-2.5 flex items-center gap-1 font-mono font-bold text-slate-400">
            <ArrowUpDown size={11} /> Sort:
          </span>
          {[
            { key: "safety_drift", label: "Safety Drift" },
            { key: "capability_gain", label: "Capability" },
            { key: "retention_ratio", label: "Retention" },
          ].map(({ key, label }) => (
            <a
              key={key}
              href={`/leaderboard?sort=${key}`}
              className={`px-3 py-1.5 rounded-lg font-bold font-mono text-[11px] transition-all ${
                sort === key
                  ? "bg-cyan-500 text-slate-950 shadow-md font-black"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {label}
            </a>
          ))}
        </div>
      </div>

      {/* Leaderboard Table Card */}
      <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[760px]">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400">
                <th className="px-4 py-3">Rank</th>
                <th className="px-4 py-3">Group</th>
                <th className="px-4 py-3">Agent Archetype</th>
                <th className="px-4 py-3">Cap. Gain ΔP</th>
                <th className="px-4 py-3">Safety Drift</th>
                <th className="px-4 py-3">Retention</th>
                <th className="px-4 py-3">Proxy Gap</th>
                <th className="px-4 py-3">Safety Index</th>
                <th className="px-4 py-3">Pareto Status</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((item) => {
                const isG7 = item.group === "G7";
                const isG4 = item.group === "G4";
                const safetyScore = item.retention_ratio / (1 + item.safety_drift);
                const safetyScorePct = Math.min(100, (safetyScore / 1.05) * 100);
                const groupColor = GROUP_COLORS[item.group] || "#8892a4";

                return (
                  <tr
                    key={item.group}
                    className={`border-b border-slate-800/50 transition-colors hover:bg-slate-900/40 text-xs ${
                      isG7
                        ? "bg-cyan-950/15"
                        : isG4
                        ? "bg-rose-950/15"
                        : ""
                    }`}
                  >
                    {/* Rank */}
                    <td className="px-4 py-3 font-mono font-black text-sm">
                      {item.rank === 1 ? (
                        <span className="flex items-center gap-1.5 text-amber-400 font-extrabold">
                          <Award size={15} /> #1
                        </span>
                      ) : (
                        <span className="text-slate-400">#{item.rank}</span>
                      )}
                    </td>

                    {/* Group Badge */}
                    <td className="px-4 py-3">
                      <span
                        className="font-mono text-xs font-black px-2 py-0.5 rounded border inline-block"
                        style={{
                          color: groupColor,
                          backgroundColor: `${groupColor}18`,
                          borderColor: `${groupColor}35`,
                        }}
                      >
                        {item.group}
                      </span>
                    </td>

                    {/* Agent Archetype */}
                    <td className="px-4 py-3">
                      <div className="font-bold text-white text-xs">{item.name}</div>
                      {isG7 && (
                        <span className="text-[10px] text-cyan-400 font-mono block">
                          Held-Out Invariant Gate &bull; Canary Verified
                        </span>
                      )}
                    </td>

                    {/* Capability Gain with Visual Progress Bar */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 min-w-[100px]">
                        <div className="h-1.5 rounded-full flex-1 max-w-[50px] bg-slate-800 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-emerald-400"
                            style={{ width: `${Math.min(100, item.capability_gain * 280)}%` }}
                          />
                        </div>
                        <span className="font-mono text-xs font-bold text-emerald-400">
                          +{(item.capability_gain * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>

                    {/* Safety Drift */}
                    <td className="px-4 py-3 font-mono text-xs font-bold">
                      <span
                        className={
                          item.safety_drift > 0.1
                            ? "text-rose-400 font-black"
                            : item.safety_drift > 0.03
                            ? "text-amber-400"
                            : "text-emerald-400"
                        }
                      >
                        +{(item.safety_drift * 100).toFixed(1)}%
                      </span>
                    </td>

                    {/* Retention Ratio */}
                    <td className="px-4 py-3 font-mono text-xs text-slate-300">
                      {item.retention_ratio.toFixed(2)}
                    </td>

                    {/* Proxy Gap */}
                    <td className="px-4 py-3 font-mono text-xs text-amber-400">
                      +{item.proxy_gap.toFixed(3)}
                    </td>

                    {/* Safety Score Meter */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 min-w-[90px]">
                        <div className="h-1.5 rounded-full flex-1 max-w-[45px] bg-slate-800 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              isG7 ? "bg-cyan-400" : isG4 ? "bg-rose-500" : "bg-sky-500"
                            }`}
                            style={{ width: `${safetyScorePct}%` }}
                          />
                        </div>
                        <span className="font-mono text-[11px] text-slate-300 font-bold">
                          {safetyScore.toFixed(2)}
                        </span>
                      </div>
                    </td>

                    {/* Status Pill */}
                    <td className="px-4 py-3">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[10px] font-bold font-mono whitespace-nowrap border ${
                          item.status.includes("Optimal")
                            ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/30"
                            : item.status.includes("Safe")
                            ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
                            : item.status.includes("Moderate")
                            ? "bg-amber-500/15 text-amber-300 border-amber-500/30"
                            : "bg-rose-500/15 text-rose-300 border-rose-500/30"
                        }`}
                      >
                        {item.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Formal Taxonomy Architecture Callout */}
      <div className="hud-card p-5 border border-cyan-500/30 bg-cyan-950/10 space-y-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-cyan-400" size={18} />
          <h3 className="font-bold text-sm text-cyan-300 font-mono">
            Formal Taxonomy: G1–G7 Deployable Archetypes &amp; G6* Theoretical Oracle Skyline
          </h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The SAGE benchmark benchmarks seven active deployable archetypes (<span className="font-mono text-cyan-300 font-bold">G1–G7</span>). 
          Among defensive configurations, <span className="font-mono text-cyan-300 font-bold">G7 (Deployable Proxy Canary Guard)</span> represents the production-ready standard: it evaluates candidate mutations exclusively on held-out proxy tasks (<code className="text-cyan-200">test_proxy.py</code>) with atomic rollback, halting security drift (<span className="text-emerald-400 font-bold">+0.015</span>) and proxy gaming (<span className="text-cyan-300 font-bold">&le; 0.02</span>).
        </p>
        <p className="text-xs text-slate-400 leading-relaxed">
          In contrast, <span className="font-mono text-pink-400 font-bold">G6* (Oracle Skyline)</span> follows standard asterisk notation (&pi;*, Q*) denoting the academic upper bound (92.0% solve rate, 98% retention) evaluated against sequestered ground truth (<code className="text-pink-300">test_gt.py</code>). Because real-world deployments cannot access future ground-truth unit tests, G7 constitutes the ecologically valid deployable defense.
        </p>
      </div>
    </div>
  );
}
