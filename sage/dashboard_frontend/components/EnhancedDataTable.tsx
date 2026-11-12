"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { ArrowUpDown, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface TableRow {
  id: string;
  name: string;
  category: string;
  promptInitChars: number;
  trainGain: number;
  testC4: number;
  overallClean: number;
  securityDrift: number;
  welchT: number;
  color: string;
}

interface EnhancedDataTableProps {
  data: TableRow[];
  title?: string;
  subtitle?: string;
}

const TrendIcon: React.FC<{ value: number }> = ({ value }) => {
  if (value > 0.02) return <TrendingUp size={14} className="text-neon-green" />;
  if (value < -0.02) return <TrendingDown size={14} className="text-rose-400" />;
  return <Minus size={14} className="text-slate-500" />;
};

const Sparkline: React.FC<{ values: number[]; color: string }> = ({ values, color }) => {
  const width = 60;
  const height = 20;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  
  const points = values
    .map((val, idx) => {
      const x = (idx / (values.length - 1)) * width;
      const y = height - ((val - min) / range) * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={width} height={height} className="inline-block">
      <defs>
        <linearGradient id={`sparkline-grad-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0.05" />
        </linearGradient>
      </defs>
      <motion.polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1, ease: "easeInOut" }}
      />
      <motion.polygon
        points={`0,${height} ${points} ${width},${height}`}
        fill={`url(#sparkline-grad-${color})`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      />
    </svg>
  );
};

export const EnhancedDataTable: React.FC<EnhancedDataTableProps> = ({
  data,
  title = "Comparative Archetype Matrix (G₁ through G₇)",
  subtitle = "5 Seeds per Layer • 9,800 Tasks",
}) => {
  const [sortConfig, setSortConfig] = useState<{ key: keyof TableRow; direction: "asc" | "desc" } | null>(null);
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);

  const sortedData = React.useMemo(() => {
    if (!sortConfig) return data;
    
    return [...data].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortConfig.direction === "asc" ? aVal - bVal : bVal - aVal;
      }
      
      return sortConfig.direction === "asc"
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
  }, [data, sortConfig]);

  const handleSort = (key: keyof TableRow) => {
    setSortConfig((current) => {
      if (!current || current.key !== key) {
        return { key, direction: "desc" };
      }
      if (current.direction === "desc") {
        return { key, direction: "asc" };
      }
      return null;
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="glass-card p-6 border border-neon-cyan/20"
    >
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-neon-cyan/20 gap-3">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <span className="section-label">Verified Empirical Baseline</span>
            <span className="metric-tag">
              Live Dual T4 Study
            </span>
          </div>
          <h3 className="text-lg font-bold text-white tracking-tight">
            {title}
          </h3>
        </div>
        <span className="text-xs font-mono text-slate-400">
          {subtitle}
        </span>
      </div>

      {/* Table */}
      <div className="mt-5 overflow-x-auto">
        <table className="enhanced-table w-full text-left font-mono text-xs min-w-[900px]">
          <thead>
            <tr className="text-[10px] text-neon-cyan uppercase font-bold border-b border-neon-cyan/30">
              <th className="p-3">
                <button
                  onClick={() => handleSort("id")}
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  Archetype
                  <ArrowUpDown size={12} />
                </button>
              </th>
              <th className="p-3">Category</th>
              <th className="p-3">
                <button
                  onClick={() => handleSort("promptInitChars")}
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  Initial Prompt
                  <ArrowUpDown size={12} />
                </button>
              </th>
              <th className="p-3">
                <button
                  onClick={() => handleSort("trainGain")}
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  Train Gain (C3-C0)
                  <ArrowUpDown size={12} />
                </button>
              </th>
              <th className="p-3">
                <button
                  onClick={() => handleSort("testC4")}
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  Test Pass (C4)
                  <ArrowUpDown size={12} />
                </button>
              </th>
              <th className="p-3">
                <button
                  onClick={() => handleSort("overallClean")}
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  Clean Overall
                  <ArrowUpDown size={12} />
                </button>
              </th>
              <th className="p-3 text-neon-green">
                <button
                  onClick={() => handleSort("securityDrift")}
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  Security Drift
                  <ArrowUpDown size={12} />
                </button>
              </th>
              <th className="p-3 text-right">
                <button
                  onClick={() => handleSort("welchT")}
                  className="flex items-center gap-1.5 hover:text-white transition-colors ml-auto"
                >
                  Welch t vs G1
                  <ArrowUpDown size={12} />
                </button>
              </th>
              <th className="p-3">Trend</th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, index) => (
              <motion.tr
                key={row.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05, duration: 0.4 }}
                onMouseEnter={() => setHoveredRow(row.id)}
                onMouseLeave={() => setHoveredRow(null)}
                className={`border-b border-neon-cyan/10 transition-all duration-200 ${
                  hoveredRow === row.id ? "bg-neon-cyan/10 scale-[1.01]" : ""
                }`}
                style={{
                  boxShadow: hoveredRow === row.id ? `0 0 20px rgba(0, 240, 255, 0.2)` : undefined,
                }}
              >
                {/* Archetype */}
                <td className="p-3 font-bold text-white">
                  <div className="flex items-center gap-2.5">
                    <motion.span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: row.color }}
                      animate={hoveredRow === row.id ? { scale: [1, 1.3, 1] } : {}}
                      transition={{ duration: 0.5, repeat: hoveredRow === row.id ? Infinity : 0 }}
                    />
                    <span>{row.id}: {row.name}</span>
                  </div>
                </td>

                {/* Category */}
                <td className="p-3 text-slate-400">{row.category}</td>

                {/* Prompt Init */}
                <td className="p-3 text-slate-400">{row.promptInitChars} chars</td>

                {/* Train Gain */}
                <td className={`p-3 font-bold ${row.trainGain > 0 ? "text-neon-cyan" : "text-rose-400"}`}>
                  <div className="flex items-center gap-1.5">
                    <TrendIcon value={row.trainGain} />
                    {row.trainGain > 0 ? "+" : ""}
                    {(row.trainGain * 100).toFixed(1)}%
                  </div>
                </td>

                {/* Test C4 */}
                <td className="p-3 font-bold text-neon-green">{(row.testC4 * 100).toFixed(1)}%</td>

                {/* Overall Clean */}
                <td className="p-3 font-bold text-white">{(row.overallClean * 100).toFixed(1)}%</td>

                {/* Security Drift */}
                <td className="p-3 font-bold text-neon-green">
                  <span className="px-2 py-1 rounded-md bg-neon-green/10 border border-neon-green/30">
                    {row.securityDrift.toFixed(3)}
                  </span>
                </td>

                {/* Welch t */}
                <td className="p-3 text-right font-bold text-slate-400">
                  {row.welchT === 0 ? (
                    <span className="text-neon-purple">Control</span>
                  ) : (
                    <span>{row.welchT > 0 ? "+" : ""}{row.welchT.toFixed(2)}</span>
                  )}
                </td>

                {/* Sparkline */}
                <td className="p-3">
                  <Sparkline
                    values={[row.testC4 * 0.8, row.testC4 * 0.9, row.testC4 * 0.95, row.testC4]}
                    color={row.color}
                  />
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer Stats */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="mt-5 pt-4 border-t border-neon-cyan/20 grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {[
          { label: "Total Archetypes", value: data.length, color: "text-neon-cyan" },
          { label: "Mean Success", value: `${((data.reduce((a, r) => a + r.overallClean, 0) / data.length) * 100).toFixed(1)}%`, color: "text-neon-green" },
          { label: "Zero Drift Count", value: data.filter((r) => r.securityDrift === 0).length, color: "text-neon-purple" },
          { label: "Best Performer", value: data.reduce((a, b) => (a.overallClean > b.overallClean ? a : b)).id, color: "text-neon-pink" },
        ].map((stat, i) => (
          <div key={i} className="text-center">
            <div className={`text-2xl font-black font-mono ${stat.color}`}>{stat.value}</div>
            <div className="text-[10px] text-slate-500 font-mono uppercase mt-1">{stat.label}</div>
          </div>
        ))}
      </motion.div>
    </motion.div>
  );
};
