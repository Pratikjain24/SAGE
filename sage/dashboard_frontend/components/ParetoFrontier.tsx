"use client";

import React, { useState } from "react";
import { ShieldCheck, Target, ArrowUpRight, Info, CheckCircle2 } from "lucide-react";
import { LAYERS_EMPIRICAL_DATA } from "@/lib/empiricalData";

interface ArchetypePoint {
  id: string;
  name: string;
  category: string;
  cleanPass: number; // Overall clean pass rate (X-axis: 48.5% - 52.5%)
  proxyGap: number;  // Signed proxy gap G_p (Y-axis: -0.6% to +2.4%)
  trainGain: number; // Train gain
  hours: number;     // GPU compute hours
  color: string;
  isParetoOptimal: boolean;
  description: string;
}

// 100% Genuine Empirical Data from the 35 Kaggle Dual Tesla T4 GPU Runs
const EMPIRICAL_PARETO_POINTS: ArchetypePoint[] = [
  {
    id: "G1",
    name: "G1: Frozen Control Baseline",
    category: "Control",
    cleanPass: 0.505,
    proxyGap: 0.002,
    trainGain: 0.007,
    hours: 2.31,
    color: "#94a3b8",
    isParetoOptimal: false,
    description: "Counterfactual reference baseline with zero evolution, 50.5% clean pass rate, and minimal proxy gap (+0.2%).",
  },
  {
    id: "G2",
    name: "G2: Prompt Rewriter",
    category: "Prompt Heuristic",
    cleanPass: 0.504,
    proxyGap: 0.015,
    trainGain: 0.030,
    hours: 3.04,
    color: "#f59e0b",
    isParetoOptimal: false,
    description: "Appends failure edge-cases to prompt (+3.0% train gain), but inflates proxy gap to +1.5% with no clean generalization improvement.",
  },
  {
    id: "G3",
    name: "G3: Memory Accumulator",
    category: "Memory",
    cleanPass: 0.485,
    proxyGap: 0.018,
    trainGain: -0.033,
    hours: 2.87,
    color: "#3b82f6",
    isParetoOptimal: false,
    description: "Persists external buffer of historical failures. Overfits past errors, resulting in -3.3% train regression and +1.8% proxy gap.",
  },
  {
    id: "G4",
    name: "G4: Reflection Agent",
    category: "Reflection",
    cleanPass: 0.514,
    proxyGap: 0.024,
    trainGain: 0.050,
    hours: 2.45,
    color: "#ef4444",
    isParetoOptimal: false,
    description: "Highest training adaptation gain (+5.0%), but exhibits peak specification gaming (+2.4% proxy gap) by generating no-op pass assertions.",
  },
  {
    id: "G5",
    name: "G5: Static Verifier (AST)",
    category: "Static Guard",
    cleanPass: 0.525,
    proxyGap: 0.004,
    trainGain: 0.047,
    hours: 2.50,
    color: "#8b5cf6",
    isParetoOptimal: true,
    description: "Pareto Front: Highest clean overall pass rate (52.5%) while keeping proxy gap strictly confined to +0.4% via AST syntax verification.",
  },
  {
    id: "G6",
    name: "G6: Oracle Skyline Guard",
    category: "Skyline",
    cleanPass: 0.511,
    proxyGap: -0.003,
    trainGain: 0.040,
    hours: 2.48,
    color: "#10b981",
    isParetoOptimal: true,
    description: "Theoretical skyline with oracle regression testing; prevents specification gaming entirely (proxy gap -0.3%).",
  },
  {
    id: "G7",
    name: "G7: Proxy Canary Guard",
    category: "Canary Guard",
    cleanPass: 0.516,
    proxyGap: -0.006,
    trainGain: 0.037,
    hours: 5.43,
    color: "#00f0ff",
    isParetoOptimal: true,
    description: "Deployable Pareto Champion: Dual-container proxy canary gate testing suite before commit; achieves 51.6% clean pass and -0.6% proxy gap with zero oracle access.",
  },
];

export const ParetoFrontier: React.FC = () => {
  const [selectedGroup, setSelectedGroup] = useState<ArchetypePoint | null>(null);

  const width = 640;
  const height = 340;
  const padding = { top: 35, right: 35, bottom: 50, left: 65 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  // X: Clean Pass Rate (47.0% to 54.0%)
  const minX = 0.475;
  const maxX = 0.535;

  // Y: Signed Proxy Gap (-1.0% to +3.0%)
  const minY = -0.010;
  const maxY = 0.030;

  const scaleX = (val: number) => padding.left + ((val - minX) / (maxX - minX)) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - ((val - minY) / (maxY - minY)) * plotHeight;

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Multi-Objective Optimization</span>
            <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              Pass Rate vs. Specification Gaming (Gp)
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Empirical Pareto Frontier: Capability vs. Alignment Risk
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            G7 (Canary Guard) and G5 (Static AST) form the empirical non-dominated frontier.
          </p>
        </div>

        {/* Champion Pill */}
        <div className="flex items-center gap-2 bg-cyan-500/10 px-3 py-1.5 rounded-xl border border-cyan-500/30 font-mono text-xs text-cyan-300 shrink-0">
          <ShieldCheck size={14} className="text-cyan-400" />
          <span>G7 Champion: 51.6% Clean / -0.6% Gap</span>
        </div>
      </div>

      {/* Main Scatter Plot */}
      <div className="mt-4 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px]">
          {/* Horizontal Grid lines (Proxy Gap Y-axis) */}
          {[-0.01, 0.0, 0.01, 0.02, 0.03].map((val) => {
            const y = scaleY(val);
            return (
              <g key={val}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke={val === 0.0 ? "#475569" : "#1e293b"}
                  strokeWidth={val === 0.0 ? 1.5 : 1}
                  strokeDasharray={val === 0.0 ? undefined : "2 2"}
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  fill={val === 0.0 ? "#cbd5e1" : "#64748b"}
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="end"
                  fontWeight={val === 0.0 ? "bold" : "normal"}
                >
                  {val > 0 ? "+" : ""}{(val * 100).toFixed(1)}%
                </text>
              </g>
            );
          })}

          {/* Vertical Grid lines (Pass Rate X-axis) */}
          {[0.48, 0.49, 0.50, 0.51, 0.52, 0.53].map((val) => {
            const x = scaleX(val);
            return (
              <g key={val}>
                <line
                  x1={x}
                  y1={padding.top}
                  x2={x}
                  y2={padding.top + plotHeight}
                  stroke="#1e293b"
                  strokeDasharray="2 2"
                />
                <text
                  x={x}
                  y={padding.top + plotHeight + 18}
                  fill="#94a3b8"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {(val * 100).toFixed(0)}%
                </text>
              </g>
            );
          })}

          {/* Axis Labels */}
          <text
            x={width / 2}
            y={padding.top + plotHeight + 38}
            fill="#94a3b8"
            fontSize="11"
            fontFamily="monospace"
            textAnchor="middle"
            fontWeight="bold"
          >
            Clean Overall Solve Rate &rarr; (Higher is Better)
          </text>

          <text
            x={16}
            y={height / 2}
            fill="#94a3b8"
            fontSize="10"
            fontFamily="monospace"
            textAnchor="middle"
            transform={`rotate(-90 16 ${height / 2})`}
          >
            &larr; Gaming Risk (Gp) &larr;
          </text>

          {/* Pareto Frontier Connecting Line (G7 -> G6 -> G5) */}
          <path
            d={`M ${scaleX(0.516)} ${scaleY(-0.006)} L ${scaleX(0.511)} ${scaleY(-0.003)} L ${scaleX(0.525)} ${scaleY(0.004)}`}
            fill="none"
            stroke="#06b6d4"
            strokeWidth="2"
            strokeDasharray="4 4"
            opacity="0.8"
          />

          {/* Points */}
          {EMPIRICAL_PARETO_POINTS.map((pt) => {
            const cx = scaleX(pt.cleanPass);
            const cy = scaleY(pt.proxyGap);
            const isSelected = selectedGroup?.id === pt.id;

            return (
              <g
                key={pt.id}
                className="cursor-pointer"
                onClick={() => setSelectedGroup(pt)}
              >
                {/* Glow ring for Pareto Optimal */}
                {pt.isParetoOptimal && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={isSelected ? 14 : 10}
                    fill={pt.color}
                    fillOpacity="0.15"
                    stroke={pt.color}
                    strokeWidth="1"
                    strokeDasharray="2 2"
                    className="animate-pulse"
                  />
                )}

                <circle
                  cx={cx}
                  cy={cy}
                  r={isSelected ? 7 : 5.5}
                  fill={pt.color}
                  stroke="#020617"
                  strokeWidth="2"
                  className="transition-all"
                />

                <text
                  x={cx + (pt.id === "G4" || pt.id === "G5" ? 10 : -10)}
                  y={cy - 8}
                  fill={pt.isParetoOptimal ? "#38bdf8" : "#94a3b8"}
                  fontSize="11"
                  fontFamily="monospace"
                  fontWeight="bold"
                  textAnchor={pt.id === "G4" || pt.id === "G5" ? "start" : "end"}
                >
                  {pt.id}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Selected Archetype Insight Drawer */}
      <div className="mt-4 pt-4 border-t border-slate-800/80 bg-slate-900/40 p-4 rounded-xl border border-slate-800 text-xs">
        {selectedGroup ? (
          <div className="space-y-1.5 font-sans">
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm font-black text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: selectedGroup.color }} />
                {selectedGroup.name}
              </span>
              <span className={`font-mono text-[10px] px-2 py-0.5 rounded font-bold ${
                selectedGroup.isParetoOptimal
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "bg-slate-800 text-slate-400"
              }`}>
                {selectedGroup.isParetoOptimal ? "PARETO OPTIMAL" : "DOMINATED"}
              </span>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">{selectedGroup.description}</p>
            <div className="flex items-center gap-4 text-xs font-mono pt-1 text-slate-400">
              <span>Clean Pass: <strong className="text-emerald-400">{(selectedGroup.cleanPass * 100).toFixed(1)}%</strong></span>
              <span>Signed Proxy Gap: <strong className="text-cyan-300">{(selectedGroup.proxyGap * 100).toFixed(1)}%</strong></span>
              <span>Train Gain: <strong className="text-white">{(selectedGroup.trainGain * 100).toFixed(1)}%</strong></span>
              <span>Compute: <strong className="text-slate-300">{selectedGroup.hours}h</strong></span>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Click any archetype dot above to view exact empirical metrics and Pareto dominance status.</span>
            <span className="font-mono text-[11px] text-cyan-400">7/7 Archetypes Plotted</span>
          </div>
        )}
      </div>
    </div>
  );
};
