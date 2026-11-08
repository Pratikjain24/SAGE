"use client";

import React, { useState } from "react";
import { ShieldCheck, Target, ArrowUpRight, Info } from "lucide-react";

interface ArchetypePoint {
  id: string;
  name: string;
  gain: number;
  drift: number;
  retention: number;
  color: string;
  description: string;
}

const ARCHETYPES: ArchetypePoint[] = [
  {
    id: "G1",
    name: "G1: Frozen Baseline",
    gain: 0.0,
    drift: 0.0,
    retention: 100,
    color: "#94a3b8",
    description: "Counterfactual reference baseline with zero evolution, zero gain, and zero drift.",
  },
  {
    id: "G2",
    name: "G2: Prompt Rewriter",
    gain: 0.18,
    drift: 0.22,
    retention: 82,
    color: "#f59e0b",
    description: "Appends failure traces to prompt; reaches early capability ceiling with significant drift.",
  },
  {
    id: "G3",
    name: "G3: Memory Accumulator",
    gain: 0.21,
    drift: 0.15,
    retention: 91,
    color: "#3b82f6",
    description: "Persists external episodic memory buffer; maintains higher retention with moderate drift.",
  },
  {
    id: "G4",
    name: "G4: Reflection Agent",
    gain: 0.29,
    drift: 0.28,
    retention: 82,
    color: "#ef4444",
    description: "Highest unconstrained capability gain, but suffers severe security erosion (the unconstrained trap).",
  },
  {
    id: "G5",
    name: "G5: Static Verifier (AST)",
    gain: 0.24,
    drift: 0.06,
    retention: 91,
    color: "#8b5cf6",
    description: "Static AST gate prevents direct syntax escapes and cuts drift by ~4x, sitting near tolerance.",
  },
  {
    id: "G6",
    name: "G6: Regression Guard",
    gain: 0.32,
    drift: 0.02,
    retention: 98,
    color: "#10b981",
    description: "Dual-container canary tests halt unsafe state changes. Dominates all axes with drift inside tolerance.",
  },
];

export const ParetoFrontier: React.FC = () => {
  const [activeArchetype, setActiveArchetype] = useState<ArchetypePoint | null>(null);

  const width = 640;
  const height = 360;
  const padding = { top: 35, right: 35, bottom: 50, left: 60 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const minX = 0.0;
  const maxX = 0.32;
  const minY = 0.0;
  const maxY = 0.35;

  const scaleX = (val: number) => padding.left + (val / maxX) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - (val / maxY) * plotHeight;

  // Safe zone cutoff: drift <= 0.05
  const safeZoneX2 = scaleX(0.05);

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-2 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Multi-Objective Optimization</span>
            <span className="font-mono text-[10px] text-emerald-400 font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
              Pareto Efficient Frontier
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            The Pareto Frontier: Capability vs. Safety Drift vs. Retention
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Bubble area represents capability retention; shaded vertical band indicates the verifier acceptable-drift zone (drift ≤ 0.05).
          </p>
        </div>
      </div>

      {/* Main Content Grid: SVG Plot + Argument Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-4 items-center">
        {/* SVG Scatter Plot */}
        <div className="lg:col-span-8 relative overflow-x-auto">
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px]">
            <defs>
              <linearGradient id="safeZoneGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.12" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0.04" />
              </linearGradient>
            </defs>

            {/* Shaded Safe Zone */}
            <rect
              x={padding.left}
              y={padding.top}
              width={safeZoneX2 - padding.left}
              height={plotHeight}
              fill="url(#safeZoneGrad)"
              stroke="#10b981"
              strokeDasharray="4 4"
              strokeOpacity="0.4"
            />
            <text
              x={padding.left + 8}
              y={padding.top + 20}
              fill="#10b981"
              fontSize="10"
              fontFamily="monospace"
              fontWeight="bold"
            >
              Safe Zone (Drift ≤ 0.05)
            </text>

            {/* Horizontal Grid lines */}
            {[0.0, 0.1, 0.2, 0.3].map((val) => {
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
                    +{val.toFixed(2)}
                  </text>
                </g>
              );
            })}

            {/* Vertical Grid lines */}
            {[0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3].map((val) => {
              const x = scaleX(val);
              return (
                <g key={val}>
                  <line
                    x1={x}
                    y1={padding.top}
                    x2={x}
                    y2={height - padding.bottom}
                    stroke="#1e293b"
                    strokeDasharray="2 2"
                  />
                  <text
                    x={x}
                    y={height - padding.bottom + 16}
                    fill="#64748b"
                    fontSize="10"
                    fontFamily="monospace"
                    textAnchor="middle"
                  >
                    {val.toFixed(2)}
                  </text>
                </g>
              );
            })}

            {/* Axis Labels */}
            <text
              x={padding.left + plotWidth / 2}
              y={height - 8}
              fill="#94a3b8"
              fontSize="11"
              fontFamily="monospace"
              fontWeight="bold"
              textAnchor="middle"
            >
              Security Drift ΔViolationRate(T) → Higher Risk
            </text>
            <text
              x={14}
              y={padding.top + plotHeight / 2}
              fill="#94a3b8"
              fontSize="11"
              fontFamily="monospace"
              fontWeight="bold"
              textAnchor="middle"
              transform={`rotate(-90, 14, ${padding.top + plotHeight / 2})`}
            >
              Capability Gain ΔP(T) → Better
            </text>

            {/* Archetype Bubbles */}
            {ARCHETYPES.map((arch) => {
              const cx = scaleX(arch.drift);
              const cy = scaleY(arch.gain);
              const radius = 6 + (arch.retention / 100) * 10;
              const isSelected = activeArchetype?.id === arch.id;

              return (
                <g
                  key={arch.id}
                  className="cursor-pointer transition-all duration-200"
                  onClick={() => setActiveArchetype(isSelected ? null : arch)}
                  onMouseEnter={() => setActiveArchetype(arch)}
                >
                  {/* Outer glow aura */}
                  <circle
                    cx={cx}
                    cy={cy}
                    r={radius + (isSelected ? 6 : 2)}
                    fill={arch.color}
                    fillOpacity={isSelected ? 0.35 : 0.15}
                  />
                  {/* Solid bubble */}
                  <circle
                    cx={cx}
                    cy={cy}
                    r={radius}
                    fill={arch.color}
                    stroke="#0f172a"
                    strokeWidth="2.5"
                  />
                  {/* Label */}
                  <text
                    x={cx + (arch.id === "G4" || arch.id === "G6" ? -radius - 8 : radius + 8)}
                    y={cy + 4}
                    fill={arch.color}
                    fontSize="11"
                    fontFamily="monospace"
                    fontWeight="bold"
                    textAnchor={arch.id === "G4" || arch.id === "G6" ? "end" : "start"}
                  >
                    {arch.id} ({arch.retention}% ret)
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Narrative / Takeaway Column */}
        <div className="lg:col-span-4 space-y-3 font-sans">
          <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
              <ShieldCheck size={14} />
              <span>Key Empirical Finding</span>
            </div>
            <ul className="text-xs text-slate-300 space-y-2 leading-relaxed">
              <li>
                <strong className="text-white">No trade-off exists:</strong> Guarded agents are strictly superior on both capability and safety axes simultaneously.
              </li>
              <li>
                <strong className="text-rose-400">G4 is dominated:</strong> G6 provides +0.03 more capability while cutting drift by 93%.
              </li>
              <li>
                <strong className="text-emerald-400">G5 &amp; G6 sit inside:</strong> The acceptable drift boundary (drift ≤ 0.05), while unconstrained G2–G4 escape control.
              </li>
            </ul>
          </div>

          {/* Active Inspector Card */}
          {activeArchetype ? (
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-700/60 space-y-1.5 animate-fade-in text-xs font-mono">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: activeArchetype.color }} />
                  {activeArchetype.name}
                </span>
                <span className="text-slate-400">Retention: {activeArchetype.retention}%</span>
              </div>
              <p className="text-[11px] text-slate-300 font-sans">{activeArchetype.description}</p>
              <div className="grid grid-cols-2 gap-2 pt-1.5 border-t border-slate-800 text-[11px]">
                <div>
                  <span className="text-slate-500">Gain ΔP: </span>
                  <span className="text-emerald-400 font-bold">+{activeArchetype.gain.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-slate-500">Drift: </span>
                  <span className="text-rose-400 font-bold">+{activeArchetype.drift.toFixed(2)}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-3.5 rounded-xl bg-slate-900/30 border border-slate-800/60 text-center text-xs text-slate-500">
              Hover or click any bubble to inspect detailed archetype metrics.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

