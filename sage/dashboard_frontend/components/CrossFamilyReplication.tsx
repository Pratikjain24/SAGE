"use client";

import React, { useState } from "react";
import { Cpu, Layers, GitCompare, CheckCircle2, ShieldCheck } from "lucide-react";
import { LAYERS_EMPIRICAL_DATA } from "@/lib/empiricalData";

interface ReplicationRow {
  archetype: string;
  name: string;
  contributor: string;
  seed42Rate: number;
  ensembleMean: number;
  seedStd: number;
  securityDrift: number;
  welchT: number;
}

const REPLICATION_DATA: ReplicationRow[] = [
  { archetype: "G1", name: "G1: Static Control", contributor: "Node P1", seed42Rate: 53.6, ensembleMean: 50.5, seedStd: 2.1, securityDrift: 0.000, welchT: 0.0 },
  { archetype: "G2", name: "G2: Prompt Rewriter", contributor: "Node P2", seed42Rate: 51.8, ensembleMean: 50.4, seedStd: 1.8, securityDrift: 0.000, welchT: -0.10 },
  { archetype: "G3", name: "G3: Memory Accumulator", contributor: "Node P3", seed42Rate: 49.6, ensembleMean: 48.5, seedStd: 2.4, securityDrift: 0.000, welchT: -1.72 },
  { archetype: "G4", name: "G4: Reflection Agent", contributor: "Node P4", seed42Rate: 52.9, ensembleMean: 51.4, seedStd: 1.9, securityDrift: 0.000, welchT: +0.76 },
  { archetype: "G5", name: "G5: Verified Agent (AST)", contributor: "Node P5", seed42Rate: 53.9, ensembleMean: 52.5, seedStd: 1.5, securityDrift: 0.000, welchT: +1.73 },
  { archetype: "G6", name: "G6: Skyline (Oracle)", contributor: "Node P6", seed42Rate: 52.1, ensembleMean: 51.1, seedStd: 1.6, securityDrift: 0.000, welchT: +0.55 },
  { archetype: "G7", name: "G7: Proxy Canary Guard", contributor: "Node P7", seed42Rate: 51.6, ensembleMean: 51.6, seedStd: 1.7, securityDrift: 0.000, welchT: +0.92 },
];

export const CrossFamilyReplication: React.FC = () => {
  const [selectedGroup, setSelectedGroup] = useState<ReplicationRow | null>(null);

  const width = 680;
  const height = 300;
  const padding = { top: 35, right: 35, bottom: 45, left: 55 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  // Scale Y from 40% to 60%
  const scaleY = (val: number) => padding.top + plotHeight - ((val - 40) / 20) * plotHeight;
  const groupWidth = plotWidth / REPLICATION_DATA.length;
  const barWidth = 14;

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="section-label text-cyan-400">Multi-Seed &amp; Inter-Hardware Invariance</span>
            <span className="font-mono text-[10px] text-emerald-400 font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
              35 Runs &bull; 9,800 Tasks &bull; Dual Tesla T4
            </span>
          </div>
          <h3 className="text-lg font-black tracking-tight text-white mt-0.5">
            Cross-Node Replication &amp; Seed Stability Matrix
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Evaluating reproducibility across independent GPU nodes (P1 vs P7: |Δ| = 1.96% ≤ 2.50%) and 5 random seeds per layer (S42–S46).
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-cyan-400" /> Seed 42 Reference
          </span>
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500" /> 5-Seed Ensemble Mean
          </span>
        </div>
      </div>

      {/* SVG Canvas Bar Chart */}
      <div className="mt-4 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[550px]">
          {/* Y Axis Grid lines */}
          {[40, 45, 50, 55, 60].map((val) => {
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
                  {val}%
                </text>
              </g>
            );
          })}

          {/* Groups */}
          {REPLICATION_DATA.map((d, idx) => {
            const groupCenterX = padding.left + idx * groupWidth + groupWidth / 2;
            const s42X = groupCenterX - barWidth - 2;
            const meanX = groupCenterX + 2;

            const s42Y = scaleY(d.seed42Rate);
            const meanY = scaleY(d.ensembleMean);

            const s42H = plotHeight - (s42Y - padding.top);
            const meanH = plotHeight - (meanY - padding.top);

            const isSelected = selectedGroup?.archetype === d.archetype;

            return (
              <g
                key={d.archetype}
                className="cursor-pointer"
                onClick={() => setSelectedGroup(isSelected ? null : d)}
                onMouseEnter={() => setSelectedGroup(d)}
              >
                {/* Seed 42 Bar */}
                <rect
                  x={s42X}
                  y={s42Y}
                  width={barWidth}
                  height={s42H}
                  fill="#06b6d4"
                  rx="2"
                  opacity={isSelected ? 1.0 : 0.85}
                />
                {/* Ensemble Mean Bar */}
                <rect
                  x={meanX}
                  y={meanY}
                  width={barWidth}
                  height={meanH}
                  fill="#10b981"
                  rx="2"
                  opacity={isSelected ? 1.0 : 0.85}
                />

                {/* Values on top of bars */}
                <text
                  x={s42X + barWidth / 2}
                  y={s42Y - 5}
                  fill="#06b6d4"
                  fontSize="9"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {d.seed42Rate.toFixed(1)}%
                </text>
                <text
                  x={meanX + barWidth / 2}
                  y={meanY - 5}
                  fill="#10b981"
                  fontSize="9"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {d.ensembleMean.toFixed(1)}%
                </text>

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

      {/* Accompanying Data Table & Replication Finding */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 lg:grid-cols-12 gap-4 text-xs font-mono">
        <div className="lg:col-span-8 overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 font-bold uppercase">
                <th className="p-2">Archetype</th>
                <th className="p-2">Contributor</th>
                <th className="p-2 text-cyan-400">Seed 42</th>
                <th className="p-2 text-emerald-400">5-Seed Mean</th>
                <th className="p-2">Seed Std</th>
                <th className="p-2 text-emerald-400">Security Drift</th>
              </tr>
            </thead>
            <tbody>
              {REPLICATION_DATA.map((row) => (
                <tr
                  key={row.archetype}
                  className={`border-b border-slate-800/50 hover:bg-slate-900/40 transition-colors ${
                    selectedGroup?.archetype === row.archetype ? "bg-slate-900/80 text-white" : "text-slate-300"
                  }`}
                >
                  <td className="p-2 font-bold">{row.name}</td>
                  <td className="p-2 text-slate-400">{row.contributor}</td>
                  <td className="p-2 text-cyan-400 font-bold">{row.seed42Rate.toFixed(1)}%</td>
                  <td className="p-2 text-emerald-400 font-bold">{row.ensembleMean.toFixed(1)}%</td>
                  <td className="p-2 text-slate-400">&plusmn;{row.seedStd.toFixed(1)}%</td>
                  <td className="p-2 text-emerald-400 font-bold">0.000 (Safe)</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="lg:col-span-4 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 font-sans space-y-2">
          <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-xs uppercase">
            <ShieldCheck size={14} />
            <span>Replication Finding</span>
          </div>
          <p className="text-xs leading-relaxed">
            The multi-seed replication confirms <strong className="text-white">high inter-node stability</strong>. Cross-hardware check between Node P1 and Node P7 matches within <strong className="text-emerald-400">|Δ| = 1.96%</strong> (comfortably inside the ≤ 2.50% threshold).
          </p>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Across all 35 seeds (35 &times; 280 = 9,800 checks), security drift remains identically <strong className="text-emerald-400">0.000</strong> with zero sandbox escapes.
          </p>
        </div>
      </div>
    </div>
  );
};
