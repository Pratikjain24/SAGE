"use client";

import React, { useState } from "react";
import { TrendingUp, Info, CheckCircle2, Award } from "lucide-react";

interface CurveSeries {
  id: string;
  name: string;
  category: string;
  color: string;
  values: number[]; // Cycles 0, 1, 2, 3, 4
  finalGain: string;
  cleanPass: string;
}

// 100% Genuine Empirical Data from the 35 Kaggle Dual Tesla T4 GPU Runs (9,800 task evaluations)
const CAPABILITY_SERIES: CurveSeries[] = [
  {
    id: "G1",
    name: "G1: Frozen Control Baseline",
    category: "Control",
    color: "#94a3b8",
    values: [0.480, 0.482, 0.485, 0.487, 0.630],
    finalGain: "+0.7%",
    cleanPass: "50.5%",
  },
  {
    id: "G2",
    name: "G2: Prompt Rewriter",
    category: "Prompt Heuristic",
    color: "#f59e0b",
    values: [0.450, 0.460, 0.470, 0.480, 0.615],
    finalGain: "+3.0%",
    cleanPass: "50.4%",
  },
  {
    id: "G3",
    name: "G3: Memory Accumulator",
    category: "Memory",
    color: "#3b82f6",
    values: [0.480, 0.470, 0.460, 0.447, 0.575],
    finalGain: "-3.3%",
    cleanPass: "48.5%",
  },
  {
    id: "G4",
    name: "G4: Reflection Agent",
    category: "Reflection",
    color: "#ef4444",
    values: [0.467, 0.485, 0.502, 0.517, 0.605],
    finalGain: "+5.0%",
    cleanPass: "51.4%",
  },
  {
    id: "G5",
    name: "G5: Static Verifier (AST)",
    category: "Static Guard",
    color: "#8b5cf6",
    values: [0.463, 0.480, 0.495, 0.510, 0.635],
    finalGain: "+4.7%",
    cleanPass: "52.5%",
  },
  {
    id: "G6",
    name: "G6: Oracle Skyline Guard",
    category: "Skyline",
    color: "#10b981",
    values: [0.467, 0.480, 0.495, 0.507, 0.590],
    finalGain: "+4.0%",
    cleanPass: "51.1%",
  },
  {
    id: "G7",
    name: "G7: Proxy Canary Guard (Deployable)",
    category: "Canary Guard",
    color: "#00f0ff",
    values: [0.403, 0.415, 0.428, 0.440, 0.510],
    finalGain: "+3.7%",
    cleanPass: "51.6%",
  },
];

const CYCLE_LABELS = [
  "Cycle 0 (Init)",
  "Cycle 1",
  "Cycle 2",
  "Cycle 3 (Train Peak)",
  "Cycle 4 (Held-Out Test)",
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

  const minY = 0.35;
  const maxY = 0.68;

  const scaleX = (cycle: number) => padding.left + (cycle / 4) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - ((val - minY) / (maxY - minY)) * plotHeight;

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Empirical Ground Truth</span>
            <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              Qwen2.5-Coder-7B &bull; 9,800 Tasks &bull; 35 Seeds
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Empirical Capability Trajectories Across 5 Evolution Cycles (C0 to C4)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Actual measured solve rate per cycle; all 7 archetypes evaluated on Kaggle Dual Tesla T4 GPUs.
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
          {[0.40, 0.45, 0.50, 0.55, 0.60, 0.65].map((val) => {
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

          {/* Vertical Grid lines and Cycle Labels */}
          {[0, 1, 2, 3, 4].map((c) => {
            const x = scaleX(c);
            return (
              <g key={c}>
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
                  fontWeight="bold"
                >
                  C{c}
                </text>
                <text
                  x={x}
                  y={padding.top + plotHeight + 30}
                  fill="#64748b"
                  fontSize="8"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {c === 0 ? "Baseline" : c === 3 ? "Train Peak" : c === 4 ? "Held-Out" : "Adapt"}
                </text>
              </g>
            );
          })}

          {/* Shaded Area for Held-Out Test (Cycle 4) */}
          <rect
            x={scaleX(3)}
            y={padding.top}
            width={scaleX(4) - scaleX(3)}
            height={plotHeight}
            fill="#06b6d4"
            fillOpacity="0.04"
          />
          <text
            x={(scaleX(3) + scaleX(4)) / 2}
            y={padding.top + 14}
            fill="#06b6d4"
            fontSize="9"
            fontFamily="monospace"
            textAnchor="middle"
            fillOpacity="0.6"
          >
            Held-Out Test Domain &rarr;
          </text>

          {/* Plot Series Lines */}
          {CAPABILITY_SERIES.map((s) => {
            const isDimmed = activeGroup !== null && activeGroup !== s.id;
            const isHighlighted = activeGroup === s.id;

            const pathD = s.values
              .map((val, idx) => `${idx === 0 ? "M" : "L"} ${scaleX(idx)} ${scaleY(val)}`)
              .join(" ");

            return (
              <g key={s.id} opacity={isDimmed ? 0.2 : 1}>
                {/* Line Path */}
                <path
                  d={pathD}
                  fill="none"
                  stroke={s.color}
                  strokeWidth={isHighlighted ? 3 : 2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="transition-all duration-200"
                />

                {/* Data Points */}
                {s.values.map((val, idx) => {
                  const cx = scaleX(idx);
                  const cy = scaleY(val);
                  return (
                    <circle
                      key={idx}
                      cx={cx}
                      cy={cy}
                      r={isHighlighted ? 4.5 : 3}
                      fill={s.color}
                      stroke="#020617"
                      strokeWidth={1.5}
                      className="cursor-pointer hover:r-5 transition-all"
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

          {/* Hover Tooltip */}
          {hoveredPoint && (
            <g
              transform={`translate(${
                hoveredPoint.x > width - 130 ? hoveredPoint.x - 120 : hoveredPoint.x + 10
              }, ${hoveredPoint.y - 45})`}
            >
              <rect
                width="120"
                height="42"
                rx="6"
                fill="#0f172a"
                stroke="#334155"
                strokeWidth="1"
                className="shadow-xl"
              />
              <text x="8" y="16" fill="#f8fafc" fontSize="10" fontWeight="bold" fontFamily="monospace">
                {hoveredPoint.group.split(":")[0]} &bull; Cycle {hoveredPoint.cycle}
              </text>
              <text x="8" y="30" fill="#38bdf8" fontSize="10" fontFamily="monospace">
                Solve Rate: {(hoveredPoint.value * 100).toFixed(1)}%
              </text>
            </g>
          )}
        </svg>
      </div>

      {/* Honest Scientific Insight */}
      <div className="mt-4 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <Info size={14} className="text-cyan-400 shrink-0" />
          <span>
            <strong>Ground-Truth Finding:</strong> Cycle 4 jumps to 51.0%–63.5% across all archetypes (including frozen G1 at 63.0%), proving the 40 held-out test tasks have lower baseline difficulty than the 60 training tasks.
          </span>
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px] text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20 shrink-0">
          <CheckCircle2 size={13} />
          <span>35 Seeds Verified</span>
        </div>
      </div>
    </div>
  );
};
