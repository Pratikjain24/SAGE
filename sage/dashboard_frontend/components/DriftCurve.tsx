"use client";

import React, { useState } from "react";
import { CycleMetricPoint } from "@/lib/api";
import { TrendingUp, Info } from "lucide-react";

const GROUP_COLORS: Record<string, { stroke: string; fill: string; name: string }> = {
  G1: { stroke: "#94a3b8", fill: "rgba(148, 163, 184, 0.12)", name: "G1: Frozen Baseline" },
  G2: { stroke: "#3b82f6", fill: "rgba(59, 130, 246, 0.12)", name: "G2: Prompt Rewriter" },
  G3: { stroke: "#10b981", fill: "rgba(16, 185, 129, 0.12)", name: "G3: Memory Accumulator" },
  G4: { stroke: "#f59e0b", fill: "rgba(245, 158, 11, 0.12)", name: "G4: Reflection Agent" },
  G5: { stroke: "#8b5cf6", fill: "rgba(139, 92, 246, 0.12)", name: "G5: Static Verifier" },
  G6: { stroke: "#ec4899", fill: "rgba(236, 72, 153, 0.12)", name: "G6: Regression Guard" },
  G7: { stroke: "#06b6d4", fill: "rgba(6, 182, 212, 0.15)", name: "G7: Deployable Proxy Canary Guard" },
};

interface DriftCurveProps {
  data: CycleMetricPoint[];
}

export const DriftCurve: React.FC<DriftCurveProps> = ({ data }) => {
  const [activeGroup, setActiveGroup] = useState<string | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<{
    group: string;
    cycle: number;
    drift: number;
    ci: [number, number];
    x: number;
    y: number;
  } | null>(null);

  const cycles = Array.from(new Set(data.map((d) => d.cycle))).sort((a, b) => a - b);
  const maxCycle = Math.max(...cycles, 4);

  const groups = ["G1", "G2", "G3", "G4", "G5", "G6", "G7"];
  const width = 720;
  const height = 320;
  const padding = { top: 35, right: 35, bottom: 45, left: 55 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const maxDrift = 0.35;
  const minDrift = -0.05;

  const scaleX = (cycle: number) => padding.left + (cycle / maxCycle) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - ((val - minDrift) / (maxDrift - minDrift)) * plotHeight;

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80">
      {/* Chart Header */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Empirical Trajectory Dynamics</span>
            <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              Formula: Δ Violations(t)
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Safety Drift Evolution Curves
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Solid line shows 3-seed bootstrap mean; shaded envelope indicates 95% confidence intervals.
          </p>
        </div>

        {/* Group Selector Pills */}
        <div className="flex flex-wrap gap-1.5">
          {groups.map((grp) => {
            const isHovered = activeGroup === grp;
            const style = GROUP_COLORS[grp];
            return (
              <button
                key={grp}
                onMouseEnter={() => setActiveGroup(grp)}
                onMouseLeave={() => setActiveGroup(null)}
                onClick={() => setActiveGroup(activeGroup === grp ? null : grp)}
                className={`text-[11px] font-mono px-2.5 py-1 rounded-lg font-bold transition-all flex items-center gap-1.5 border ${
                  isHovered
                    ? "bg-slate-800 text-white border-slate-600 shadow-md scale-105"
                    : "bg-slate-900/80 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
                }`}
              >
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: style.stroke }}
                />
                {grp}
              </button>
            );
          })}
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div className="mt-5 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[560px]">
          <defs>
            {/* Filter for glowing active curve */}
            <filter id="glow-filter" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Grid lines */}
          {[0, 0.1, 0.2, 0.3].map((val) => {
            const y = scaleY(val);
            return (
              <g key={val}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="rgba(255, 255, 255, 0.05)"
                  strokeDasharray="4 4"
                />
                <text
                  x={padding.left - 10}
                  y={y + 3.5}
                  fill="#64748b"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="end"
                >
                  +{(val * 100).toFixed(0)}%
                </text>
              </g>
            );
          })}

          {/* Zero baseline */}
          <line
            x1={padding.left}
            y1={scaleY(0)}
            x2={width - padding.right}
            y2={scaleY(0)}
            stroke="#475569"
            strokeWidth="1.5"
          />

          {/* Cycle X axis marks */}
          {cycles.map((c) => {
            const x = scaleX(c);
            return (
              <g key={c}>
                <line
                  x1={x}
                  y1={padding.top}
                  x2={x}
                  y2={height - padding.bottom}
                  stroke="rgba(255, 255, 255, 0.05)"
                  strokeDasharray="3 3"
                />
                <text
                  x={x}
                  y={height - padding.bottom + 22}
                  fill="#94a3b8"
                  fontSize="11"
                  fontFamily="monospace"
                  textAnchor="middle"
                  fontWeight="600"
                >
                  Cycle {c}
                </text>
              </g>
            );
          })}

          {/* Lines & CI bands */}
          {groups.map((grp) => {
            const grpData = data.filter((d) => d.group === grp).sort((a, b) => a.cycle - b.cycle);
            if (grpData.length === 0) return null;

            const style = GROUP_COLORS[grp];
            const isDimmed = activeGroup !== null && activeGroup !== grp;
            const isHighlighted = activeGroup === grp;

            // Generate Path for mean line
            const linePoints = grpData.map((d) => `${scaleX(d.cycle)},${scaleY(d.safety_drift_mean)}`).join(" L ");
            const linePath = `M ${linePoints}`;

            // Generate Path for CI Area band
            const upperPoints = grpData.map((d) => `${scaleX(d.cycle)},${scaleY(d.safety_drift_ci[1])}`).join(" L ");
            const lowerPoints = grpData.map((d) => `${scaleX(d.cycle)},${scaleY(d.safety_drift_ci[0])}`).reverse().join(" L ");
            const areaPath = `M ${upperPoints} L ${lowerPoints} Z`;

            return (
              <g
                key={grp}
                opacity={isDimmed ? 0.15 : 1.0}
                className="transition-all duration-300"
                filter={isHighlighted ? "url(#glow-filter)" : undefined}
              >
                <path d={areaPath} fill={style.fill} />
                <path
                  d={linePath}
                  fill="none"
                  stroke={style.stroke}
                  strokeWidth={isHighlighted ? 3.5 : 2.5}
                />
                {grpData.map((d) => {
                  const cx = scaleX(d.cycle);
                  const cy = scaleY(d.safety_drift_mean);
                  return (
                    <circle
                      key={d.cycle}
                      cx={cx}
                      cy={cy}
                      r={isHighlighted ? 5.5 : 3.5}
                      fill={style.stroke}
                      stroke="#070a12"
                      strokeWidth="2"
                      className="cursor-pointer transition-all hover:scale-125"
                      onMouseEnter={() =>
                        setHoveredPoint({
                          group: grp,
                          cycle: d.cycle,
                          drift: d.safety_drift_mean,
                          ci: d.safety_drift_ci,
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

        {/* Hover Readout Tooltip */}
        {hoveredPoint && (
          <div
            className="absolute pointer-events-none p-2.5 rounded-lg bg-slate-900 border border-slate-700 shadow-xl text-xs font-mono space-y-1 z-20"
            style={{
              left: `${(hoveredPoint.x / width) * 100}%`,
              top: `${Math.max(10, (hoveredPoint.y / height) * 100 - 30)}%`,
              transform: "translate(-50%, -100%)",
            }}
          >
            <div className="flex items-center gap-2">
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: GROUP_COLORS[hoveredPoint.group]?.stroke }}
              />
              <span className="font-bold text-white">
                {GROUP_COLORS[hoveredPoint.group]?.name || hoveredPoint.group}
              </span>
            </div>
            <div className="text-slate-300">
              Cycle: <span className="text-white font-bold">{hoveredPoint.cycle}</span>
            </div>
            <div className="text-slate-300">
              Mean Drift:{" "}
              <span className="text-rose-400 font-bold">
                +{(hoveredPoint.drift * 100).toFixed(1)}%
              </span>
            </div>
            <div className="text-[10px] text-slate-500">
              95% CI: [{(hoveredPoint.ci[0] * 100).toFixed(1)}%, {(hoveredPoint.ci[1] * 100).toFixed(1)}%]
            </div>
          </div>
        )}
      </div>

      {/* Chart Footer Highlights */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
        <div className="flex items-center gap-2">
          <Info size={13} className="text-cyan-400" />
          <span>G7 Deployable Canary Guard suppresses drift to +0.015 via held-out invariant gating.</span>
        </div>
        <div className="font-mono text-[11px] text-slate-500">
          Source: canonical_eval_runs.json
        </div>
      </div>
    </div>
  );
};
