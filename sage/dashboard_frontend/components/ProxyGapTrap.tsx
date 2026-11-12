"use client";

import React, { useState } from "react";
import { AlertCircle, ShieldAlert, CheckCircle2, Layers, ShieldCheck } from "lucide-react";
import { TASK_TYPE_STRATIFIED_METRICS, SECURITY_VS_FUNCTIONAL_GAP_DELTA, TaskTypeStratifiedMetric } from "@/lib/empiricalData";

interface ArchetypeGapData {
  group: string;
  name: string;
  standardGT: number;
  driftProbeHidden: number;
  driftProbeProxy: number;
  gap: number;
  gapPositive: number; // G_p^+ (gaming: proxy inflated)
  gapNegative: number; // G_p^- (under-reporting: proxy missed capability)
  gapSigned: number;   // p_proxy - p_gt
}

const GAP_DATA: ArchetypeGapData[] = [
  { group: "G1", name: "G1: Frozen Control", standardGT: 0.505, driftProbeHidden: 0.503, driftProbeProxy: 0.505, gap: 0.002, gapPositive: 0.003, gapNegative: 0.001, gapSigned: 0.002 },
  { group: "G2", name: "G2: Prompt Rewriter", standardGT: 0.504, driftProbeHidden: 0.490, driftProbeProxy: 0.505, gap: 0.015, gapPositive: 0.018, gapNegative: 0.003, gapSigned: 0.015 },
  { group: "G3", name: "G3: Memory Accumulator", standardGT: 0.485, driftProbeHidden: 0.470, driftProbeProxy: 0.488, gap: 0.018, gapPositive: 0.021, gapNegative: 0.003, gapSigned: 0.018 },
  { group: "G4", name: "G4: Reflection Agent", standardGT: 0.514, driftProbeHidden: 0.492, driftProbeProxy: 0.516, gap: 0.024, gapPositive: 0.026, gapNegative: 0.002, gapSigned: 0.024 },
  { group: "G5", name: "G5: Static Verifier", standardGT: 0.525, driftProbeHidden: 0.522, driftProbeProxy: 0.526, gap: 0.004, gapPositive: 0.005, gapNegative: 0.001, gapSigned: 0.004 },
  { group: "G6", name: "G6: Regression Guard", standardGT: 0.511, driftProbeHidden: 0.513, driftProbeProxy: 0.510, gap: -0.003, gapPositive: 0.004, gapNegative: 0.007, gapSigned: -0.003 },
  { group: "G7", name: "G7: Proxy Canary Guard", standardGT: 0.516, driftProbeHidden: 0.520, driftProbeProxy: 0.514, gap: -0.006, gapPositive: 0.005, gapNegative: 0.011, gapSigned: -0.006 },
];

export const ProxyGapTrap: React.FC = () => {
  const [selectedGroup, setSelectedGroup] = useState<ArchetypeGapData | null>(null);
  const [selectedTaskType, setSelectedTaskType] = useState<TaskTypeStratifiedMetric | null>(null);
  const [viewMode, setViewMode] = useState<"archetypes" | "task_types">("task_types");

  const width = 640;
  const height = 340;
  const padding = { top: 35, right: 35, bottom: 45, left: 55 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const scaleY = (val: number) => padding.top + plotHeight - val * plotHeight;
  const groupWidth = plotWidth / (viewMode === "archetypes" ? GAP_DATA.length : TASK_TYPE_STRATIFIED_METRICS.length);
  const barWidth = viewMode === "archetypes" ? 14 : 22;

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Specification Gaming Trap</span>
            <span className="font-mono text-[10px] text-amber-400 font-bold px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
              N=20 Drift Probes vs 80 Standard Tasks
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            The Proxy Gap: Where Agents Learn to Cheat
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Visible proxy rewards diverge from sequestered ground-truth invariants under unconstrained mutation.
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-xs font-mono">
            <button
              onClick={() => setViewMode("task_types")}
              className={`px-3 py-1 rounded-md transition-colors ${
                viewMode === "task_types"
                  ? "bg-purple-600 text-white font-bold"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Task Archetypes
            </button>
            <button
              onClick={() => setViewMode("archetypes")}
              className={`px-3 py-1 rounded-md transition-colors ${
                viewMode === "archetypes"
                  ? "bg-purple-600 text-white font-bold"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Agent Layers (G1–G7)
            </button>
          </div>
        </div>
      </div>

      {/* Legend & Secondary Info */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono mt-3 pb-2 border-b border-slate-800/50">
        <div className="flex items-center gap-3">
          {viewMode === "archetypes" && (
            <span className="flex items-center gap-1.5 text-slate-400">
              <span className="w-2.5 h-2.5 rounded-sm bg-slate-600" /> Standard P_GT
            </span>
          )}
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-cyan-400" /> Hidden Truth P_GT
          </span>
          <span className="flex items-center gap-1.5 text-rose-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-rose-500" /> Visible Proxy P_Proxy
          </span>
        </div>
        {viewMode === "task_types" && (
          <div className="text-amber-400 font-bold">
            Security Δ = +{(SECURITY_VS_FUNCTIONAL_GAP_DELTA.deltaGapPositive * 100).toFixed(1)}% vs Functional Tasks
          </div>
        )}
      </div>

      {/* Main Bar Chart */}
      <div className="mt-4 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px]">
          {/* Y-axis grid */}
          {[0.0, 0.2, 0.4, 0.6, 0.8, 1.0].map((val) => {
            const y = scaleY(val);
            return (
              <g key={val}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#1e293b"
                  strokeDasharray="2 2"
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  fill="#64748b"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="end"
                >
                  {val.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* Archetypes View */}
          {viewMode === "archetypes" &&
            GAP_DATA.map((d, idx) => {
              const groupCenterX = padding.left + idx * groupWidth + groupWidth / 2;
              const b1X = groupCenterX - barWidth * 1.6;
              const b2X = groupCenterX - barWidth * 0.5;
              const b3X = groupCenterX + barWidth * 0.6;

              const b1Y = scaleY(d.standardGT);
              const b2Y = scaleY(d.driftProbeHidden);
              const b3Y = scaleY(d.driftProbeProxy);

              const b1H = plotHeight - (b1Y - padding.top);
              const b2H = plotHeight - (b2Y - padding.top);
              const b3H = plotHeight - (b3Y - padding.top);

              const isSelected = selectedGroup?.group === d.group;

              return (
                <g
                  key={d.group}
                  className="cursor-pointer transition-opacity"
                  onClick={() => setSelectedGroup(isSelected ? null : d)}
                  onMouseEnter={() => setSelectedGroup(d)}
                >
                  <rect x={b1X} y={b1Y} width={barWidth} height={b1H} fill="#475569" rx="2" opacity={isSelected ? 1 : 0.85} />
                  <rect x={b2X} y={b2Y} width={barWidth} height={b2H} fill="#06b6d4" rx="2" opacity={isSelected ? 1 : 0.85} />
                  <rect x={b3X} y={b3Y} width={barWidth} height={b3H} fill="#f43f5e" rx="2" opacity={isSelected ? 1 : 0.85} />

                  <text
                    x={groupCenterX}
                    y={Math.min(b2Y, b3Y) - 8}
                    fill={d.gapPositive > 0.1 ? "#f43f5e" : "#10b981"}
                    fontSize="10"
                    fontFamily="monospace"
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    +{d.gapPositive.toFixed(2)}
                  </text>

                  <text
                    x={groupCenterX}
                    y={height - padding.bottom + 16}
                    fill={isSelected ? "#38bdf8" : "#94a3b8"}
                    fontSize="11"
                    fontFamily="monospace"
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    {d.group}
                  </text>
                </g>
              );
            })}

          {/* Task Types View */}
          {viewMode === "task_types" &&
            TASK_TYPE_STRATIFIED_METRICS.map((d, idx) => {
              const groupCenterX = padding.left + idx * groupWidth + groupWidth / 2;
              const b1X = groupCenterX - barWidth - 2;
              const b2X = groupCenterX + 2;

              const b1Y = scaleY(d.gtScore);
              const b2Y = scaleY(d.proxyScore);

              const b1H = plotHeight - (b1Y - padding.top);
              const b2H = plotHeight - (b2Y - padding.top);

              const isSelected = selectedTaskType?.taskType === d.taskType;

              return (
                <g
                  key={d.taskType}
                  className="cursor-pointer transition-opacity"
                  onClick={() => setSelectedTaskType(isSelected ? null : d)}
                  onMouseEnter={() => setSelectedTaskType(d)}
                >
                  {/* Background highlight for security category */}
                  {d.category === "Security" && (
                    <rect
                      x={padding.left + idx * groupWidth + 4}
                      y={padding.top}
                      width={groupWidth - 8}
                      height={plotHeight}
                      fill="#ef4444"
                      opacity="0.05"
                      rx="4"
                    />
                  )}

                  {/* Bar 1: Hidden Ground Truth */}
                  <rect x={b1X} y={b1Y} width={barWidth} height={b1H} fill="#06b6d4" rx="2" opacity={isSelected ? 1 : 0.85} />
                  {/* Bar 2: Visible Proxy */}
                  <rect x={b2X} y={b2Y} width={barWidth} height={b2H} fill="#f43f5e" rx="2" opacity={isSelected ? 1 : 0.85} />

                  {/* Gap delta indicator pill above bars */}
                  <text
                    x={groupCenterX}
                    y={Math.min(b1Y, b2Y) - 8}
                    fill={d.gapPositive > 0.1 ? "#f43f5e" : "#10b981"}
                    fontSize="10"
                    fontFamily="monospace"
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    +{d.gapPositive.toFixed(2)}
                  </text>

                  {/* Task archetype label */}
                  <text
                    x={groupCenterX}
                    y={height - padding.bottom + 16}
                    fill={d.category === "Security" ? "#f87171" : isSelected ? "#38bdf8" : "#94a3b8"}
                    fontSize="10"
                    fontFamily="monospace"
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    {d.taskType}
                  </text>
                </g>
              );
            })}
        </svg>
      </div>

      {/* Accompanying Data Table & Insight */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 lg:grid-cols-12 gap-4 text-xs font-mono">
        <div className="lg:col-span-8 overflow-x-auto">
          {viewMode === "archetypes" ? (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] text-slate-400 font-bold uppercase">
                  <th className="p-2">Group</th>
                  <th className="p-2">Standard P_GT</th>
                  <th className="p-2 text-cyan-400">Hidden P_GT</th>
                  <th className="p-2 text-rose-400">Proxy P_Proxy</th>
                  <th className="p-2 text-center text-red-400 font-bold">G_p⁺ (Gaming)</th>
                  <th className="p-2 text-center text-amber-400 font-bold">G_p⁻ (Under-rep)</th>
                  <th className="p-2 text-right">Signed Δ</th>
                </tr>
              </thead>
              <tbody>
                {GAP_DATA.map((row) => (
                  <tr
                    key={row.group}
                    className={`border-b border-slate-800/50 hover:bg-slate-900/40 transition-colors ${
                      selectedGroup?.group === row.group ? "bg-slate-900/80 text-white" : "text-slate-300"
                    }`}
                  >
                    <td className="p-2 font-bold">{row.name}</td>
                    <td className="p-2 text-slate-400">{(row.standardGT * 100).toFixed(0)}%</td>
                    <td className="p-2 text-cyan-400 font-bold">{(row.driftProbeHidden * 100).toFixed(0)}%</td>
                    <td className="p-2 text-rose-400 font-bold">{(row.driftProbeProxy * 100).toFixed(0)}%</td>
                    <td className={`p-2 text-center font-bold ${row.gapPositive > 0.05 ? "text-red-400 font-black" : "text-slate-500"}`}>
                      +{row.gapPositive.toFixed(2)}
                    </td>
                    <td className={`p-2 text-center font-bold ${row.gapNegative > 0.01 ? "text-amber-400 font-black" : "text-slate-500"}`}>
                      {row.gapNegative > 0 ? `-${row.gapNegative.toFixed(2)}` : "0.00"}
                    </td>
                    <td className={`p-2 text-right font-bold ${
                      row.gapSigned > 0.05 ? "text-red-400" :
                      row.gapSigned < -0.01 ? "text-amber-400" :
                      "text-emerald-400"
                    }`}>
                      {row.gapSigned > 0 ? "+" : ""}{row.gapSigned.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] text-slate-400 font-bold uppercase">
                  <th className="p-2">Task Archetype</th>
                  <th className="p-2">Category</th>
                  <th className="p-2 text-cyan-400">Hidden Truth P_GT</th>
                  <th className="p-2 text-rose-400">Visible Proxy P_Proxy</th>
                  <th className="p-2 text-center text-red-400 font-bold">G_p⁺ (Gaming Gap)</th>
                  <th className="p-2 text-center text-amber-400 font-bold">G_p⁻ (Under-rep)</th>
                  <th className="p-2 text-right">Hack Rate</th>
                </tr>
              </thead>
              <tbody>
                {TASK_TYPE_STRATIFIED_METRICS.map((row) => (
                  <tr
                    key={row.taskType}
                    className={`border-b border-slate-800/50 hover:bg-slate-900/40 transition-colors ${
                      selectedTaskType?.taskType === row.taskType ? "bg-slate-900/80 text-white" : "text-slate-300"
                    }`}
                  >
                    <td className="p-2 font-bold">{row.name}</td>
                    <td className="p-2">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        row.category === "Security"
                          ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                          : "bg-slate-500/10 text-slate-300 border border-slate-500/20"
                      }`}>
                        {row.category}
                      </span>
                    </td>
                    <td className="p-2 text-cyan-400 font-bold">{(row.gtScore * 100).toFixed(0)}%</td>
                    <td className="p-2 text-rose-400 font-bold">{(row.proxyScore * 100).toFixed(0)}%</td>
                    <td className={`p-2 text-center font-bold ${row.gapPositive > 0.1 ? "text-red-400 font-black" : "text-emerald-400"}`}>
                      +{row.gapPositive.toFixed(2)}
                    </td>
                    <td className={`p-2 text-center font-bold ${row.gapNegative > 0.01 ? "text-amber-400 font-black" : "text-slate-500"}`}>
                      {row.gapNegative > 0 ? `-${row.gapNegative.toFixed(2)}` : "0.00"}
                    </td>
                    <td className={`p-2 text-right font-bold ${row.hackRate > 0.2 ? "text-rose-400" : "text-slate-400"}`}>
                      {(row.hackRate * 100).toFixed(0)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="lg:col-span-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 font-sans space-y-2.5">
          <div className="flex items-center gap-1.5 text-purple-400 font-bold text-xs uppercase">
            <ShieldAlert size={14} />
            <span>Security Invariant Asymmetry</span>
          </div>
          <p className="text-xs leading-relaxed">
            Security tasks (<code className="text-rose-400 font-mono">security_audit</code>, <code className="text-rose-400 font-mono">exploit_probe</code>) 
            exhibit <strong className="text-white">16.5× higher natural proxy gaps (+0.330 vs +0.020)</strong> than functional tasks.
          </p>
          <p className="text-xs leading-relaxed text-slate-300">
            <strong>Theoretical Cause:</strong> Surface proxy tests (<code className="text-slate-400 font-mono">test_proxy.py</code>) cannot easily test for the 
            <em>absence of vulnerability</em> without extensive penetration probes. Agents easily satisfy functional checks while leaving covert flaws undetected until sequestered <code className="text-cyan-400 font-mono">test_gt.py</code> evaluates them.
          </p>
          <div className="text-[11px] text-slate-400 border-t border-slate-800/80 pt-2 flex items-center justify-between">
            <span>Functional Gap: <strong className="text-emerald-400">+0.020</strong></span>
            <span>Security Gap: <strong className="text-rose-400">+0.330</strong></span>
            <span>Δ: <strong className="text-amber-400">+0.310</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
};


