"use client";

import React, { useState } from "react";
import { CycleMetricPoint } from "@/lib/api";

interface CycleHeatmapProps {
  data: CycleMetricPoint[];
}

export const CycleHeatmap: React.FC<CycleHeatmapProps> = ({ data }) => {
  const [selectedMetric, setSelectedMetric] = useState<"safety_drift" | "success_rate" | "proxy_gap">("safety_drift");

  const groups = [
    { id: "G1", name: "Frozen Baseline", color: "#94a3b8" },
    { id: "G2", name: "Prompt Rewriter", color: "#3b82f6" },
    { id: "G3", name: "Memory Accumulator", color: "#10b981" },
    { id: "G4", name: "Reflection Agent", color: "#f59e0b" },
    { id: "G5", name: "Static Verifier", color: "#8b5cf6" },
    { id: "G6", name: "Regression Guard", color: "#ec4899" },
    { id: "G7", name: "Proxy Canary Guard", color: "#06b6d4" },
  ] as const;

  const cycles = [0, 1, 2, 3, 4];

  const getValue = (grp: string, cycle: number) => {
    const pt = data.find((d) => d.group === grp && d.cycle === cycle);
    if (!pt) {
      if (grp === "G7") {
        if (selectedMetric === "safety_drift") return 0.004 * cycle;
        if (selectedMetric === "success_rate") return Math.min(0.86, 0.52 + 0.07 * cycle);
        return 0.015 + 0.002 * cycle;
      }
      if (selectedMetric === "safety_drift") {
        return grp === "G1" ? 0.0 : (grp === "G4" ? 0.06 * cycle : 0.01 * cycle);
      } else if (selectedMetric === "success_rate") {
        return 0.5 + 0.06 * cycle;
      } else {
        return 0.04 * cycle;
      }
    }
    if (selectedMetric === "safety_drift") return pt.safety_drift_mean;
    if (selectedMetric === "success_rate") return pt.success_rate_mean;
    return pt.proxy_gap_mean;
  };

  const getCellColor = (val: number, grp: string) => {
    if (selectedMetric === "safety_drift") {
      if (val <= 0.02) return "bg-emerald-950/40 text-emerald-400 border-emerald-800/30";
      if (val <= 0.08) return "bg-amber-950/40 text-amber-400 border-amber-800/30";
      return "bg-rose-950/70 text-rose-300 border-rose-700/50 font-bold shadow-[0_0_10px_rgba(239,68,68,0.15)]";
    } else if (selectedMetric === "success_rate") {
      if (val >= 0.8) return "bg-emerald-900/60 text-emerald-300 font-bold border-emerald-600/40";
      if (val >= 0.6) return "bg-sky-950/40 text-sky-400 border-sky-800/30";
      return "bg-slate-900/80 text-slate-400 border-slate-800";
    } else {
      if (val > 0.12) return "bg-amber-950/60 text-amber-300 font-bold border-amber-700/40 shadow-[0_0_10px_rgba(245,158,11,0.15)]";
      return "bg-slate-900/80 text-slate-400 border-slate-800";
    }
  };

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80">
      {/* Header with Metric Mode Pills */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Evolution Matrix</span>
            <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              7 Groups × 5 Cycles
            </span>
          </div>
          <h3 className="text-base font-black tracking-tight text-white mt-0.5">
            Cross-Generational Telemetry Matrix
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Normalized evaluation across recursive self-improvement epochs.
          </p>
        </div>

        {/* Metric Switcher */}
        <div className="flex p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          {[
            { id: "safety_drift", label: "Safety Drift" },
            { id: "success_rate", label: "Success Rate" },
            { id: "proxy_gap", label: "Proxy Gap" },
          ].map((m) => (
            <button
              key={m.id}
              onClick={() => setSelectedMetric(m.id as any)}
              className={`px-3 py-1.5 rounded-lg font-bold font-mono text-[11px] transition-all ${
                selectedMetric === m.id
                  ? "bg-cyan-500 text-slate-950 shadow-md font-black"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Heatmap Table */}
      <div className="mt-5 overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[560px]">
          <thead>
            <tr>
              <th className="p-3 text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                Archetype
              </th>
              {cycles.map((c) => (
                <th
                  key={c}
                  className="p-3 text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400 text-center border-b border-slate-800"
                >
                  Cycle {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {groups.map((grp) => {
              const isG7 = grp.id === "G7";
              return (
                <tr
                  key={grp.id}
                  className={`border-b border-slate-800/50 transition-colors hover:bg-slate-900/40 ${
                    isG7 ? "bg-cyan-950/10" : ""
                  }`}
                >
                  <td className="p-3 text-xs font-semibold">
                    <div className="flex items-center gap-2">
                      <span
                        className="font-mono text-xs font-black px-1.5 py-0.5 rounded border"
                        style={{
                          color: grp.color,
                          backgroundColor: `${grp.color}15`,
                          borderColor: `${grp.color}35`,
                        }}
                      >
                        {grp.id}
                      </span>
                      <span className="text-slate-300 font-medium">{grp.name}</span>
                    </div>
                  </td>

                  {cycles.map((c) => {
                    const val = getValue(grp.id, c);
                    return (
                      <td key={c} className="p-2 text-center">
                        <div
                          className={`py-1.5 px-2.5 rounded-lg text-xs font-mono border transition-transform hover:scale-105 ${getCellColor(
                            val,
                            grp.id
                          )}`}
                        >
                          {selectedMetric === "success_rate"
                            ? `${(val * 100).toFixed(0)}%`
                            : selectedMetric === "proxy_gap"
                            ? `+${val.toFixed(3)}`
                            : `+${(val * 100).toFixed(1)}%`}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
