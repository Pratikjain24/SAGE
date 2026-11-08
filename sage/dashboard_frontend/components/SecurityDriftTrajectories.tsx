"use client";

import React, { useState } from "react";
import { AlertTriangle, ShieldCheck, Info } from "lucide-react";

interface DriftSeries {
  id: string;
  name: string;
  color: string;
  values: number[];
  finalDrift: string;
  verdict: string;
}

const DRIFT_SERIES: DriftSeries[] = [
  {
    id: "G4",
    name: "G4: Reflection Agent",
    color: "#ef4444",
    values: [0.00, 0.04, 0.09, 0.12, 0.15, 0.18, 0.21, 0.24, 0.26, 0.28],
    finalDrift: "+0.28",
    verdict: "Severe erosion: crosses 0.05 tolerance by cycle 3 and never returns.",
  },
  {
    id: "G2",
    name: "G2: Prompt Rewriter",
    color: "#f59e0b",
    values: [0.00, 0.03, 0.06, 0.09, 0.12, 0.15, 0.17, 0.19, 0.21, 0.22],
    finalDrift: "+0.22",
    verdict: "Unconstrained prompt heuristics accumulate unsafe patterns.",
  },
  {
    id: "G3",
    name: "G3: Memory Accumulator",
    color: "#3b82f6",
    values: [0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.11, 0.13, 0.14, 0.15],
    finalDrift: "+0.15",
    verdict: "Memory buffer retains unsafe task shortcuts over multi-cycle horizon.",
  },
  {
    id: "G5",
    name: "G5: Static Verifier",
    color: "#8b5cf6",
    values: [0.00, 0.02, 0.03, 0.04, 0.04, 0.05, 0.05, 0.06, 0.06, 0.06],
    finalDrift: "+0.06",
    verdict: "Just over tolerance: static AST tripwires alone cannot catch runtime semantic drift.",
  },
  {
    id: "G6",
    name: "G6: Regression Guard",
    color: "#10b981",
    values: [0.00, 0.01, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02],
    finalDrift: "+0.02",
    verdict: "Halted: dynamic canary gates reject unsafe mutations before commit.",
  },
];

export const SecurityDriftTrajectories: React.FC = () => {
  const [activeGroup, setActiveGroup] = useState<string | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<{
    group: string;
    cycle: number;
    value: number;
    x: number;
    y: number;
  } | null>(null);

  const width = 640;
  const height = 340;
  const padding = { top: 35, right: 35, bottom: 45, left: 55 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const minY = 0.0;
  const maxY = 0.30;

  const scaleX = (cycle: number) => padding.left + (cycle / 9) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - ((val - minY) / (maxY - minY)) * plotHeight;

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Safety Boundary Dynamics</span>
            <span className="font-mono text-[10px] text-rose-400 font-bold px-1.5 py-0.5 rounded bg-rose-500/10 border border-rose-500/20">
              Drift Rate = V(t)/A(t) - V(0)/A(0)
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Security Boundary Drift Over Ten Cycles
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Violation rate relative to Cycle 0; dashed red line is the verifier tolerance ceiling (0.05).
          </p>
        </div>

        {/* Legend buttons */}
        <div className="flex flex-wrap gap-1.5">
          {DRIFT_SERIES.map((s) => {
            const isHovered = activeGroup === s.id;
            return (
              <button
                key={s.id}
                onMouseEnter={() => setActiveGroup(s.id)}
                onMouseLeave={() => setActiveGroup(null)}
                onClick={() => setActiveGroup(activeGroup === s.id ? null : s.id)}
                className={`text-[11px] font-mono px-2 py-0.5 rounded-lg font-bold transition-all flex items-center gap-1.5 border ${
                  isHovered
                    ? "bg-slate-800 text-white border-slate-600 shadow-md scale-105"
                    : "bg-slate-900/80 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
                }`}
              >
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: s.color }} />
                {s.id} ({s.finalDrift})
              </button>
            );
          })}
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div className="mt-4 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px]">
          {/* Horizontal Grid lines */}
          {[0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30].map((val) => {
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

          {/* Verifier Tolerance Dashed Line */}
          <line
            x1={padding.left}
            y1={scaleY(0.05)}
            x2={width - padding.right}
            y2={scaleY(0.05)}
            stroke="#ef4444"
            strokeDasharray="4 4"
            strokeWidth="1.5"
          />
          <text
            x={width - padding.right - 10}
            y={scaleY(0.05) - 6}
            fill="#ef4444"
            fontSize="9"
            fontFamily="monospace"
            textAnchor="end"
          >
            max_acceptable_drift = 0.05 (verifier tolerance)
          </text>

          {/* X Axis ticks */}
          {Array.from({ length: 10 }).map((_, c) => {
            const x = scaleX(c);
            return (
              <g key={c}>
                <line
                  x1={x}
                  y1={height - padding.bottom}
                  x2={x}
                  y2={height - padding.bottom + 4}
                  stroke="#334155"
                />
                <text
                  x={x}
                  y={height - padding.bottom + 16}
                  fill="#94a3b8"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  t={c}
                </text>
              </g>
            );
          })}

          {/* Curve lines */}
          {DRIFT_SERIES.map((s) => {
            const isDimmed = activeGroup !== null && activeGroup !== s.id;
            const isHighlighted = activeGroup === s.id;

            const pathData = s.values
              .map((val, idx) => `${idx === 0 ? "M" : "L"} ${scaleX(idx)} ${scaleY(val)}`)
              .join(" ");

            return (
              <g key={s.id} opacity={isDimmed ? 0.15 : 1.0} className="transition-opacity duration-200">
                <path
                  d={pathData}
                  fill="none"
                  stroke={s.color}
                  strokeWidth={isHighlighted ? 3.5 : 2.5}
                />
                {s.values.map((val, idx) => {
                  const cx = scaleX(idx);
                  const cy = scaleY(val);
                  return (
                    <circle
                      key={idx}
                      cx={cx}
                      cy={cy}
                      r={isHighlighted ? 4.5 : 3.0}
                      fill={s.color}
                      stroke="#070a12"
                      strokeWidth="1.5"
                      className="cursor-pointer"
                      onMouseEnter={() =>
                        setHoveredPoint({
                          group: s.name,
                          cycle: idx,
                          value: val,
                          x: cx,
                          y: cy,
                        })
                      }
                      onMouseLeave={() => setHoveredPoint(null)}
                    />
                  );
                })}
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip */}
        {hoveredPoint && (
          <div
            className="absolute pointer-events-none p-2 rounded bg-slate-900 border border-slate-700 shadow-xl text-xs font-mono z-20 space-y-0.5"
            style={{
              left: `${(hoveredPoint.x / width) * 100}%`,
              top: `${Math.max(10, (hoveredPoint.y / height) * 100 - 25)}%`,
              transform: "translate(-50%, -100%)",
            }}
          >
            <div className="font-bold text-white">{hoveredPoint.group}</div>
            <div className="text-slate-300">Cycle: t={hoveredPoint.cycle}</div>
            <div className="text-rose-400 font-bold">Security Drift: +{hoveredPoint.value.toFixed(2)}</div>
          </div>
        )}
      </div>

      {/* Footer Insight Cards */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-300">
        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-start gap-2.5">
          <AlertTriangle size={16} className="text-rose-400 shrink-0 mt-0.5" />
          <div>
            <strong className="text-rose-400 block mb-0.5">Unconstrained Erosion (G4 &amp; G2)</strong>
            G4 reaches +0.28 drift, breaching safety tolerance by Cycle 3. Unconstrained mutation allows agents to introduce security vulnerabilities to pass tests.
          </div>
        </div>
        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-start gap-2.5">
          <ShieldCheck size={16} className="text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <strong className="text-emerald-400 block mb-0.5">Mechanism, Not Luck (G6 Halted)</strong>
            G6 sits flat at +0.02. Every step that removes a state mutation surface removes drift. Rejected mutations never enter persistent state.
          </div>
        </div>
      </div>
    </div>
  );
};

