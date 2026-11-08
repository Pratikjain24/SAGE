"use client";

import React, { useState } from "react";
import { Activity, CheckCircle2, TrendingUp, Info } from "lucide-react";

interface HorizonPoint {
  t: number;
  drift: number;
  pctAsymptote: number;
}

const HORIZON_POINTS: HorizonPoint[] = [
  { t: 0, drift: 0.000, pctAsymptote: 0.0 },
  { t: 1, drift: 0.030, pctAsymptote: 9.6 },
  { t: 5, drift: 0.160, pctAsymptote: 51.3 },
  { t: 10, drift: 0.280, pctAsymptote: 89.7 },
  { t: 15, drift: 0.305, pctAsymptote: 97.8 },
  { t: 25, drift: 0.312, pctAsymptote: 100.0 },
];

export const LongHorizonSaturation: React.FC = () => {
  const [activePoint, setActivePoint] = useState<HorizonPoint | null>(null);

  const width = 640;
  const height = 320;
  const padding = { top: 35, right: 35, bottom: 45, left: 55 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const maxT = 25;
  const maxY = 0.35;

  const scaleX = (t: number) => padding.left + (t / maxT) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - (val / maxY) * plotHeight;

  // Path interpolation for the smooth curve
  const curvePoints: [number, number][] = [];
  for (let t = 0; t <= 25; t += 0.5) {
    const drift = 0.312 * (1 - Math.exp(-0.23 * t));
    curvePoints.push([scaleX(t), scaleY(drift)]);
  }
  const pathD = curvePoints.map((pt, i) => `${i === 0 ? "M" : "L"} ${pt[0]} ${pt[1]}`).join(" ");

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Long-Horizon Generalization</span>
            <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              Evaluated T = 1..25 Cycles
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Does Drift Compound Forever? Horizon Saturation Dynamics
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Unconstrained security drift saturates asymptotically rather than exploding exponentially.
          </p>
        </div>
      </div>

      {/* Main SVG Chart Area */}
      <div className="mt-4 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px]">
          {/* Horizontal grid lines */}
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

          {/* Asymptotic ceiling line */}
          <line
            x1={padding.left}
            y1={scaleY(0.312)}
            x2={width - padding.right}
            y2={scaleY(0.312)}
            stroke="#94a3b8"
            strokeDasharray="4 4"
            strokeWidth="1.5"
          />
          <text
            x={padding.left + 8}
            y={scaleY(0.312) - 6}
            fill="#94a3b8"
            fontSize="10"
            fontFamily="monospace"
          >
            Asymptotic Ceiling = 0.312
          </text>

          {/* T=10 Reference Vertical Line */}
          <line
            x1={scaleX(10)}
            y1={padding.top}
            x2={scaleX(10)}
            y2={height - padding.bottom}
            stroke="#38bdf8"
            strokeDasharray="2 2"
            strokeOpacity="0.4"
          />
          <text
            x={scaleX(10)}
            y={padding.top + 12}
            fill="#38bdf8"
            fontSize="9"
            fontFamily="monospace"
            textAnchor="middle"
          >
            T=10 (Standard Study)
          </text>

          {/* X Axis ticks */}
          {[0, 5, 10, 15, 20, 25].map((t) => {
            const x = scaleX(t);
            return (
              <g key={t}>
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
                  T={t}
                </text>
              </g>
            );
          })}

          {/* Unconstrained Saturated Curve (Red) */}
          <path
            d={pathD}
            fill="none"
            stroke="#f43f5e"
            strokeWidth="3"
          />

          {/* Guarded Flat Curve (Green) */}
          <line
            x1={scaleX(0)}
            y1={scaleY(0.02)}
            x2={scaleX(25)}
            y2={scaleY(0.02)}
            stroke="#10b981"
            strokeWidth="2.5"
          />
          <text
            x={scaleX(25)}
            y={scaleY(0.02) - 6}
            fill="#10b981"
            fontSize="10"
            fontFamily="monospace"
            fontWeight="bold"
            textAnchor="end"
          >
            G6 Guarded: Flat at +0.02
          </text>

          {/* Data Points */}
          {HORIZON_POINTS.map((pt) => {
            const cx = scaleX(pt.t);
            const cy = scaleY(pt.drift);
            const isHovered = activePoint?.t === pt.t;

            return (
              <g
                key={pt.t}
                className="cursor-pointer"
                onMouseEnter={() => setActivePoint(pt)}
                onMouseLeave={() => setActivePoint(null)}
              >
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHovered ? 6 : 4}
                  fill="#f43f5e"
                  stroke="#0f172a"
                  strokeWidth="2"
                  className="transition-all"
                />
                {pt.t > 0 && (
                  <text
                    x={cx}
                    y={cy - 10}
                    fill="#f43f5e"
                    fontSize="9"
                    fontFamily="monospace"
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    {pt.drift.toFixed(3)}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip */}
        {activePoint && (
          <div
            className="absolute pointer-events-none p-2 rounded bg-slate-900 border border-slate-700 shadow-xl text-xs font-mono z-20 space-y-0.5"
            style={{
              left: `${(scaleX(activePoint.t) / width) * 100}%`,
              top: `${Math.max(10, (scaleY(activePoint.drift) / height) * 100 - 25)}%`,
              transform: "translate(-50%, -100%)",
            }}
          >
            <div className="font-bold text-white">Horizon T = {activePoint.t} Cycles</div>
            <div className="text-rose-400 font-bold">Mean Drift: +{activePoint.drift.toFixed(3)}</div>
            <div className="text-cyan-400">Captured: {activePoint.pctAsymptote.toFixed(1)}% of ceiling</div>
          </div>
        )}
      </div>

      {/* Footer Finding Cards */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-300">
        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
          <strong className="text-white block mb-0.5">Saturation, Not Explosion</strong>
          Mean unconstrained drift plateaus at 0.312 by Cycle 25. Agents exhaust low-hanging shortcuts early.
        </div>
        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
          <strong className="text-cyan-400 block mb-0.5">T = 10 is Sufficient</strong>
          10 cycles captures 89.7% of the total asymptotic effect at only 40% of the compute cost.
        </div>
        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
          <strong className="text-emerald-400 block mb-0.5">Guarded Agents Stay Flat</strong>
          G6 exhibits near-zero drift (+0.02) across all cycle horizons tested.
        </div>
      </div>
    </div>
  );
};

