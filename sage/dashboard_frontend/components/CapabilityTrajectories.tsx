"use client";

import React, { useState } from "react";
import { TrendingUp, Info, CheckCircle2 } from "lucide-react";

interface CurveSeries {
  id: string;
  name: string;
  color: string;
  values: number[];
  finalGain: string;
}

const CAPABILITY_SERIES: CurveSeries[] = [
  {
    id: "G1",
    name: "G1: Frozen Control",
    color: "#94a3b8",
    values: [0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60],
    finalGain: "+0.00",
  },
  {
    id: "G2",
    name: "G2: Prompt Rewriter",
    color: "#f59e0b",
    values: [0.60, 0.63, 0.66, 0.69, 0.71, 0.73, 0.75, 0.76, 0.77, 0.78],
    finalGain: "+0.18",
  },
  {
    id: "G3",
    name: "G3: Memory Accumulator",
    color: "#3b82f6",
    values: [0.60, 0.64, 0.67, 0.70, 0.73, 0.75, 0.77, 0.79, 0.80, 0.81],
    finalGain: "+0.21",
  },
  {
    id: "G5",
    name: "G5: Static Verifier",
    color: "#8b5cf6",
    values: [0.60, 0.65, 0.68, 0.71, 0.74, 0.77, 0.79, 0.81, 0.83, 0.84],
    finalGain: "+0.24",
  },
  {
    id: "G4",
    name: "G4: Reflection Agent",
    color: "#ef4444",
    values: [0.60, 0.65, 0.70, 0.74, 0.77, 0.80, 0.83, 0.85, 0.87, 0.89],
    finalGain: "+0.29",
  },
  {
    id: "G6",
    name: "G6: Regression Guard",
    color: "#10b981",
    values: [0.60, 0.66, 0.71, 0.75, 0.79, 0.83, 0.86, 0.88, 0.90, 0.92],
    finalGain: "+0.32",
  },
];

export const CapabilityTrajectories: React.FC = () => {
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

  const minY = 0.55;
  const maxY = 0.95;

  const scaleX = (cycle: number) => padding.left + (cycle / 9) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - ((val - minY) / (maxY - minY)) * plotHeight;

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Evolutionary Progression</span>
            <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              Ground-Truth Solve Rate P(t)
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Capability Trajectories Across 10 Evolutionary Cycles
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Mean pass rate per cycle; all evolving archetypes monotonically improve ($H_1$ holds).
          </p>
        </div>

        {/* Legend buttons */}
        <div className="flex flex-wrap gap-1.5">
          {CAPABILITY_SERIES.map((s) => {
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
                {s.id} ({s.finalGain})
              </button>
            );
          })}
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div className="mt-4 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px]">
          {/* Horizontal Grid lines */}
          {[0.6, 0.7, 0.8, 0.9].map((val) => {
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
                  {(val * 100).toFixed(0)}%
                </text>
              </g>
            );
          })}

          {/* Calibrated baseline dashed line */}
          <line
            x1={padding.left}
            y1={scaleY(0.60)}
            x2={width - padding.right}
            y2={scaleY(0.60)}
            stroke="#64748b"
            strokeDasharray="4 4"
            strokeWidth="1.5"
          />
          <text
            x={width - padding.right - 10}
            y={scaleY(0.60) - 6}
            fill="#94a3b8"
            fontSize="9"
            fontFamily="monospace"
            textAnchor="end"
          >
            Calibrated P(0) = 0.60
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
          {CAPABILITY_SERIES.map((s) => {
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
            <div className="text-emerald-400 font-bold">Pass Rate: {(hoveredPoint.value * 100).toFixed(1)}%</div>
          </div>
        )}
      </div>

      {/* Footer Insight Cards */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs text-slate-300">
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
          <span className="font-bold text-emerald-400 block mb-0.5">G6 Guarded: +0.32</span>
          Reaches 0.92 ground truth pass rate with full regression gating.
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
          <span className="font-bold text-rose-400 block mb-0.5">G4 Reflection: +0.29</span>
          Converges near the top at 0.89, but unconstrained gain brings severe drift.
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
          <span className="font-bold text-slate-400 block mb-0.5">G1 Flat: 0.60</span>
          Static control baseline confirms no drift and no capability inflation.
        </div>
      </div>
    </div>
  );
};

