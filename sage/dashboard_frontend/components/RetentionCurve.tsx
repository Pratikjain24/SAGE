"use client";

import React, { useState } from "react";
import { CycleMetricPoint } from "@/lib/api";

const GROUP_COLORS: Record<string, { stroke: string; name: string }> = {
  G1: { stroke: "#94a3b8", name: "G1: Frozen Baseline" },
  G2: { stroke: "#3b82f6", name: "G2: Prompt Rewriter" },
  G4: { stroke: "#f59e0b", name: "G4: Reflection Agent" },
  G6: { stroke: "#ec4899", name: "G6: Regression Guard" },
  G7: { stroke: "#06b6d4", name: "G7: Proxy Canary Guard" },
};

interface RetentionCurveProps {
  data: CycleMetricPoint[];
}

export const RetentionCurve: React.FC<RetentionCurveProps> = ({ data }) => {
  const [hoveredPoint, setHoveredPoint] = useState<{
    group: string;
    cycle: number;
    retention: number;
    x: number;
    y: number;
  } | null>(null);

  const cycles = Array.from(new Set(data.map((d) => d.cycle))).sort((a, b) => a - b);
  const maxCycle = Math.max(...cycles, 4);

  const width = 640;
  const height = 280;
  const padding = { top: 25, right: 30, bottom: 40, left: 50 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const minVal = 0.5;
  const maxVal = 1.1;

  const scaleX = (cycle: number) => padding.left + (cycle / maxCycle) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - ((val - minVal) / (maxVal - minVal)) * plotHeight;

  const groups = ["G1", "G2", "G4", "G6", "G7"];

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2">
              <span className="section-label">Catastrophic Forgetting</span>
              <span className="font-mono text-[10px] text-emerald-400 font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                Retention ≥ 1.00
              </span>
            </div>
            <h3 className="text-base font-black tracking-tight text-white mt-0.5">
              Capability Retention Ratio
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Ratio below 1.0 indicates backward capability regression on previously solved benchmark tasks.
            </p>
          </div>
        </div>

        {/* Chart Canvas */}
        <div className="mt-4 relative overflow-x-auto">
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px]">
            {/* Baseline 1.0 dashed line */}
            <line
              x1={padding.left}
              y1={scaleY(1.0)}
              x2={width - padding.right}
              y2={scaleY(1.0)}
              stroke="#10b981"
              strokeDasharray="4 4"
              strokeWidth="1.5"
            />
            <text
              x={width - padding.right - 4}
              y={scaleY(1.0) - 7}
              fill="#10b981"
              fontSize="10"
              fontFamily="monospace"
              textAnchor="end"
              fontWeight="bold"
            >
              Baseline Invariant (1.00)
            </text>

            {/* Grid lines */}
            {[0.6, 0.8, 1.0].map((v) => (
              <g key={v}>
                <line
                  x1={padding.left}
                  y1={scaleY(v)}
                  x2={width - padding.right}
                  y2={scaleY(v)}
                  stroke="rgba(255, 255, 255, 0.05)"
                  strokeDasharray="3 3"
                />
                <text
                  x={padding.left - 10}
                  y={scaleY(v) + 3.5}
                  fill="#64748b"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="end"
                >
                  {v.toFixed(1)}
                </text>
              </g>
            ))}

            {/* X axis cycles */}
            {cycles.map((c) => (
              <text
                key={c}
                x={scaleX(c)}
                y={height - padding.bottom + 22}
                fill="#94a3b8"
                fontSize="11"
                fontFamily="monospace"
                textAnchor="middle"
                fontWeight="600"
              >
                Cycle {c}
              </text>
            ))}

            {/* Lines for representative groups */}
            {groups.map((grp) => {
              const grpData = data.filter((d) => d.group === grp).sort((a, b) => a.cycle - b.cycle);
              if (grpData.length === 0) return null;

              const pathPoints = grpData.map((d) => `${scaleX(d.cycle)},${scaleY(d.retention_mean)}`).join(" L ");
              const color = GROUP_COLORS[grp]?.stroke || "#94a3b8";

              return (
                <g key={grp}>
                  <path
                    d={`M ${pathPoints}`}
                    fill="none"
                    stroke={color}
                    strokeWidth="2.5"
                    className="transition-all"
                  />
                  {grpData.map((d) => {
                    const cx = scaleX(d.cycle);
                    const cy = scaleY(d.retention_mean);
                    return (
                      <circle
                        key={d.cycle}
                        cx={cx}
                        cy={cy}
                        r="4"
                        fill={color}
                        stroke="#070a12"
                        strokeWidth="2"
                        className="cursor-pointer hover:scale-125 transition-transform"
                        onMouseEnter={() =>
                          setHoveredPoint({
                            group: grp,
                            cycle: d.cycle,
                            retention: d.retention_mean,
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
              className="absolute pointer-events-none p-2 rounded-lg bg-slate-900 border border-slate-700 shadow-xl text-xs font-mono z-20"
              style={{
                left: `${(hoveredPoint.x / width) * 100}%`,
                top: `${Math.max(10, (hoveredPoint.y / height) * 100 - 25)}%`,
                transform: "translate(-50%, -100%)",
              }}
            >
              <div className="font-bold text-white">
                {GROUP_COLORS[hoveredPoint.group]?.name || hoveredPoint.group}
              </div>
              <div className="text-slate-300">
                Cycle {hoveredPoint.cycle}:{" "}
                <span className="text-cyan-400 font-bold">
                  {hoveredPoint.retention.toFixed(3)}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Legend Footer */}
      <div className="flex flex-wrap items-center justify-center gap-4 mt-3 pt-3 border-t border-slate-800/80 text-xs text-slate-400 font-mono">
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-slate-400" /> G1 Frozen</span>
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-blue-500" /> G2 Prompt</span>
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-500" /> G4 Reflection</span>
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-pink-500" /> G6 Verifier</span>
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-cyan-400" /> G7 Canary Guard</span>
      </div>
    </div>
  );
};
