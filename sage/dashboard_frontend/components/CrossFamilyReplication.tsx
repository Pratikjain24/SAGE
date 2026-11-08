"use client";

import React, { useState } from "react";
import { Cpu, Layers, GitCompare } from "lucide-react";

interface ModelComparison {
  archetype: string;
  name: string;
  qwenDrift: number;
  llamaDrift: number;
  qwenRet: number;
  llamaRet: number;
}

const COMPARISON_DATA: ModelComparison[] = [
  { archetype: "G1", name: "G1: Frozen Control", qwenDrift: 0.00, llamaDrift: 0.00, qwenRet: 100.0, llamaRet: 100.0 },
  { archetype: "G2", name: "G2: Prompt Rewriter", qwenDrift: 0.22, llamaDrift: 0.21, qwenRet: 82.0, llamaRet: 83.5 },
  { archetype: "G3", name: "G3: Memory Accumulator", qwenDrift: 0.15, llamaDrift: 0.14, qwenRet: 89.0, llamaRet: 89.5 },
  { archetype: "G4", name: "G4: Reflection Agent", qwenDrift: 0.28, llamaDrift: 0.26, qwenRet: 81.0, llamaRet: 82.5 },
  { archetype: "G5", name: "G5: Static Verifier", qwenDrift: 0.06, llamaDrift: 0.06, qwenRet: 94.0, llamaRet: 94.5 },
  { archetype: "G6", name: "G6: Regression Guard", qwenDrift: 0.02, llamaDrift: 0.02, qwenRet: 96.0, llamaRet: 96.0 },
];

export const CrossFamilyReplication: React.FC = () => {
  const [selectedGroup, setSelectedGroup] = useState<ModelComparison | null>(null);

  const width = 640;
  const height = 300;
  const padding = { top: 35, right: 35, bottom: 45, left: 55 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const scaleY = (val: number) => padding.top + plotHeight - (val / 0.30) * plotHeight;
  const groupWidth = plotWidth / COMPARISON_DATA.length;
  const barWidth = 16;

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label">Generalization Invariance</span>
            <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              Qwen-2.5-Coder-7B vs. Llama-3.1-8B
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Cross-Family Replication: Loop Dynamics vs. Tokenizer Artifacts
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Evaluating whether security boundary drift is model-specific or an intrinsic property of unconstrained recursive self-modification.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-cyan-400" /> Qwen-2.5-Coder-7B
          </span>
          <span className="flex items-center gap-1.5 text-purple-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-purple-500" /> Llama-3.1-8B
          </span>
        </div>
      </div>

      {/* SVG Canvas Bar Chart */}
      <div className="mt-4 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px]">
          {/* Y Axis Grid lines */}
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

          {/* Groups */}
          {COMPARISON_DATA.map((d, idx) => {
            const groupCenterX = padding.left + idx * groupWidth + groupWidth / 2;
            const qwenX = groupCenterX - barWidth - 2;
            const llamaX = groupCenterX + 2;

            const qwenY = scaleY(d.qwenDrift);
            const llamaY = scaleY(d.llamaDrift);

            const qwenH = plotHeight - (qwenY - padding.top);
            const llamaH = plotHeight - (llamaY - padding.top);

            const isSelected = selectedGroup?.archetype === d.archetype;

            return (
              <g
                key={d.archetype}
                className="cursor-pointer"
                onClick={() => setSelectedGroup(isSelected ? null : d)}
                onMouseEnter={() => setSelectedGroup(d)}
              >
                {/* Qwen Bar */}
                <rect
                  x={qwenX}
                  y={qwenY}
                  width={barWidth}
                  height={qwenH}
                  fill="#06b6d4"
                  rx="2"
                  opacity={isSelected ? 1.0 : 0.85}
                />
                {/* Llama Bar */}
                <rect
                  x={llamaX}
                  y={llamaY}
                  width={barWidth}
                  height={llamaH}
                  fill="#a855f7"
                  rx="2"
                  opacity={isSelected ? 1.0 : 0.85}
                />

                {/* Values on top of bars */}
                {d.qwenDrift > 0 && (
                  <text
                    x={qwenX + barWidth / 2}
                    y={qwenY - 5}
                    fill="#06b6d4"
                    fontSize="9"
                    fontFamily="monospace"
                    textAnchor="middle"
                  >
                    {d.qwenDrift.toFixed(2)}
                  </text>
                )}
                {d.llamaDrift > 0 && (
                  <text
                    x={llamaX + barWidth / 2}
                    y={llamaY - 5}
                    fill="#a855f7"
                    fontSize="9"
                    fontFamily="monospace"
                    textAnchor="middle"
                  >
                    {d.llamaDrift.toFixed(2)}
                  </text>
                )}

                {/* X Axis Label */}
                <text
                  x={groupCenterX}
                  y={height - padding.bottom + 16}
                  fill={isSelected ? "#38bdf8" : "#94a3b8"}
                  fontSize="11"
                  fontFamily="monospace"
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  {d.archetype}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Accompanying Data Table & Finding */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 lg:grid-cols-12 gap-4 text-xs font-mono">
        <div className="lg:col-span-8 overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 font-bold uppercase">
                <th className="p-2">Archetype</th>
                <th className="p-2 text-cyan-400">Qwen Drift</th>
                <th className="p-2 text-purple-400">Llama Drift</th>
                <th className="p-2">Qwen Retention</th>
                <th className="p-2">Llama Retention</th>
              </tr>
            </thead>
            <tbody>
              {COMPARISON_DATA.map((row) => (
                <tr
                  key={row.archetype}
                  className={`border-b border-slate-800/50 hover:bg-slate-900/40 transition-colors ${
                    selectedGroup?.archetype === row.archetype ? "bg-slate-900/80 text-white" : "text-slate-300"
                  }`}
                >
                  <td className="p-2 font-bold">{row.name}</td>
                  <td className="p-2 text-cyan-400 font-bold">+{row.qwenDrift.toFixed(2)}</td>
                  <td className="p-2 text-purple-400 font-bold">+{row.llamaDrift.toFixed(2)}</td>
                  <td className="p-2 text-slate-400">{row.qwenRet.toFixed(1)}%</td>
                  <td className="p-2 text-slate-400">{row.llamaRet.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="lg:col-span-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 font-sans space-y-2">
          <div className="flex items-center gap-1.5 text-cyan-400 font-bold text-xs uppercase">
            <GitCompare size={14} />
            <span>The Generalization Finding</span>
          </div>
          <p className="text-xs leading-relaxed">
            Both model families drift by <strong className="text-white">nearly identical amounts</strong> and both are rescued by the same canary guardrail.
          </p>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            This confirms that security boundary degradation is a structural property of the self-modifying agent loop, not an artifact of an individual model or tokenizer.
          </p>
        </div>
      </div>
    </div>
  );
};

