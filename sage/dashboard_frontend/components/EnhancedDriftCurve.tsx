"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CycleMetricPoint } from "@/lib/api";
import { TrendingUp, Info, Sparkles } from "lucide-react";

const GROUP_COLORS: Record<string, { stroke: string; fill: string; glow: string; name: string }> = {
  G1: { stroke: "#94a3b8", fill: "rgba(148, 163, 184, 0.15)", glow: "rgba(148, 163, 184, 0.4)", name: "G1: Frozen Baseline" },
  G2: { stroke: "#0066ff", fill: "rgba(0, 102, 255, 0.15)", glow: "rgba(0, 102, 255, 0.5)", name: "G2: Prompt Rewriter" },
  G3: { stroke: "#00ff9f", fill: "rgba(0, 255, 159, 0.15)", glow: "rgba(0, 255, 159, 0.5)", name: "G3: Memory Accumulator" },
  G4: { stroke: "#ffa600", fill: "rgba(255, 166, 0, 0.15)", glow: "rgba(255, 166, 0, 0.5)", name: "G4: Reflection Agent" },
  G5: { stroke: "#b847ff", fill: "rgba(184, 71, 255, 0.15)", glow: "rgba(184, 71, 255, 0.5)", name: "G5: Static Verifier" },
  G6: { stroke: "#ff00e5", fill: "rgba(255, 0, 229, 0.15)", glow: "rgba(255, 0, 229, 0.5)", name: "G6: Regression Guard" },
  G7: { stroke: "#00f0ff", fill: "rgba(0, 240, 255, 0.18)", glow: "rgba(0, 240, 255, 0.6)", name: "G7: Deployable Proxy Canary Guard" },
};

interface DriftCurveProps {
  data: CycleMetricPoint[];
}

interface ParticleProps {
  x: number;
  y: number;
  color: string;
}

const Particle: React.FC<ParticleProps> = ({ x, y, color }) => {
  return (
    <motion.circle
      cx={x}
      cy={y}
      r={0}
      fill={color}
      initial={{ r: 0, opacity: 1 }}
      animate={{ r: 8, opacity: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    />
  );
};

export const EnhancedDriftCurve: React.FC<DriftCurveProps> = ({ data }) => {
  const [activeGroup, setActiveGroup] = useState<string | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<{
    group: string;
    cycle: number;
    drift: number;
    ci: [number, number];
    x: number;
    y: number;
  } | null>(null);
  const [particles, setParticles] = useState<Array<ParticleProps & { id: string }>>([]);
  const [animationProgress, setAnimationProgress] = useState(0);

  useEffect(() => {
    // Animate chart drawing
    const timer = setTimeout(() => setAnimationProgress(1), 100);
    return () => clearTimeout(timer);
  }, []);

  const cycles = Array.from(new Set(data.map((d) => d.cycle))).sort((a, b) => a - b);
  const maxCycle = Math.max(...cycles, 4);

  const groups = ["G1", "G2", "G3", "G4", "G5", "G6", "G7"];
  const width = 800;
  const height = 400;
  const padding = { top: 40, right: 40, bottom: 50, left: 60 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const maxDrift = 0.35;
  const minDrift = -0.05;

  const scaleX = (cycle: number) => padding.left + (cycle / maxCycle) * plotWidth;
  const scaleY = (val: number) => padding.top + plotHeight - ((val - minDrift) / (maxDrift - minDrift)) * plotHeight;

  const createParticle = (x: number, y: number, color: string) => {
    const id = `${x}-${y}-${Date.now()}-${Math.random()}`;
    setParticles((prev) => [...prev, { id, x, y, color }]);
    setTimeout(() => {
      setParticles((prev) => prev.filter((p) => p.id !== id));
    }, 800);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="glass-card p-6 border border-neon-cyan/20"
    >
      {/* Chart Header */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between pb-5 gap-4 border-b border-neon-cyan/20">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles size={16} className="text-neon-cyan" />
            </motion.div>
            <span className="section-label">Empirical Trajectory Dynamics</span>
            <span className="metric-tag">
              Formula: Δ Violations(t)
            </span>
          </div>
          <h3 className="text-xl font-black tracking-tight text-white">
            Safety Drift Evolution Curves
          </h3>
          <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
            Solid line shows 3-seed bootstrap mean; shaded envelope indicates 95% confidence intervals.
          </p>
        </div>

        {/* Group Selector Pills */}
        <div className="flex flex-wrap gap-2">
          {groups.map((grp) => {
            const isActive = activeGroup === grp;
            const style = GROUP_COLORS[grp];
            return (
              <motion.button
                key={grp}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onMouseEnter={() => setActiveGroup(grp)}
                onMouseLeave={() => setActiveGroup(null)}
                onClick={() => setActiveGroup(activeGroup === grp ? null : grp)}
                className={`text-[11px] font-mono px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-2 border ${
                  isActive
                    ? "bg-surface-3 text-white border-neon-cyan/60 shadow-lg scale-105"
                    : "bg-surface-2/60 text-slate-400 border-neon-cyan/20 hover:border-neon-cyan/40 hover:text-slate-200"
                }`}
                style={isActive ? { boxShadow: `0 0 20px ${style.glow}` } : undefined}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: style.stroke, boxShadow: `0 0 8px ${style.glow}` }}
                />
                {grp}
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="mt-6 relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[700px]">
          <defs>
            {/* Gradient definitions */}
            {groups.map((grp) => {
              const style = GROUP_COLORS[grp];
              return (
                <linearGradient key={`grad-${grp}`} id={`gradient-${grp}`} x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor={style.stroke} stopOpacity="0.4" />
                  <stop offset="100%" stopColor={style.stroke} stopOpacity="0" />
                </linearGradient>
              );
            })}
            
            {/* Glow filter */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
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
                  stroke="rgba(0, 240, 255, 0.08)"
                  strokeDasharray="4 4"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 12}
                  y={y + 4}
                  fill="#7a8aa8"
                  fontSize="11"
                  fontFamily="monospace"
                  textAnchor="end"
                  fontWeight="600"
                >
                  +{(val * 100).toFixed(0)}%
                </text>
              </g>
            );
          })}

          {/* Zero baseline with glow */}
          <line
            x1={padding.left}
            y1={scaleY(0)}
            x2={width - padding.right}
            y2={scaleY(0)}
            stroke="#00f0ff"
            strokeWidth="2"
            opacity="0.6"
            filter="url(#glow)"
          />

          {/* Cycle X axis */}
          {cycles.map((c) => {
            const x = scaleX(c);
            return (
              <g key={c}>
                <line
                  x1={x}
                  y1={padding.top}
                  x2={x}
                  y2={height - padding.bottom}
                  stroke="rgba(0, 240, 255, 0.06)"
                  strokeDasharray="2 3"
                />
                <text
                  x={x}
                  y={height - padding.bottom + 25}
                  fill="#b8c5db"
                  fontSize="12"
                  fontFamily="monospace"
                  textAnchor="middle"
                  fontWeight="700"
                >
                  C{c}
                </text>
              </g>
            );
          })}

          {/* Animated curves */}
          {groups.map((grp) => {
            const grpData = data.filter((d) => d.group === grp).sort((a, b) => a.cycle - b.cycle);
            if (grpData.length === 0) return null;

            const style = GROUP_COLORS[grp];
            const isDimmed = activeGroup !== null && activeGroup !== grp;
            const isHighlighted = activeGroup === grp;

            // Mean line path
            const linePoints = grpData.map((d) => `${scaleX(d.cycle)},${scaleY(d.safety_drift_mean)}`).join(" L ");
            const linePath = `M ${linePoints}`;

            // CI area path
            const upperPoints = grpData.map((d) => `${scaleX(d.cycle)},${scaleY(d.safety_drift_ci[1])}`).join(" L ");
            const lowerPoints = grpData.map((d) => `${scaleX(d.cycle)},${scaleY(d.safety_drift_ci[0])}`).reverse().join(" L ");
            const areaPath = `M ${upperPoints} L ${lowerPoints} Z`;

            return (
              <g
                key={grp}
                opacity={isDimmed ? 0.2 : 1.0}
                className="transition-opacity duration-300"
              >
                {/* CI shaded area with gradient */}
                <motion.path
                  d={areaPath}
                  fill={`url(#gradient-${grp})`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: animationProgress }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                />
                
                {/* Mean line with animation */}
                <motion.path
                  d={linePath}
                  fill="none"
                  stroke={style.stroke}
                  strokeWidth={isHighlighted ? 4 : 3}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  filter={isHighlighted ? "url(#glow)" : undefined}
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: animationProgress, opacity: 1 }}
                  transition={{ duration: 1.5, ease: "easeInOut" }}
                  style={{ boxShadow: isHighlighted ? `0 0 20px ${style.glow}` : undefined }}
                />
                
                {/* Data points */}
                {grpData.map((d) => {
                  const cx = scaleX(d.cycle);
                  const cy = scaleY(d.safety_drift_mean);
                  return (
                    <motion.circle
                      key={d.cycle}
                      cx={cx}
                      cy={cy}
                      r={isHighlighted ? 6 : 4}
                      fill={style.stroke}
                      stroke="#0a0118"
                      strokeWidth="2"
                      className="cursor-pointer transition-all"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.5 + d.cycle * 0.1 }}
                      whileHover={{ scale: 1.5, filter: "url(#glow)" }}
                      onMouseEnter={(e) => {
                        setHoveredPoint({
                          group: grp,
                          cycle: d.cycle,
                          drift: d.safety_drift_mean,
                          ci: d.safety_drift_ci,
                          x: cx,
                          y: cy,
                        });
                        createParticle(cx, cy, style.stroke);
                      }}
                      onMouseLeave={() => setHoveredPoint(null)}
                      style={{ filter: isHighlighted ? `drop-shadow(0 0 8px ${style.glow})` : undefined }}
                    />
                  );
                })}
              </g>
            );
          })}

          {/* Render particles */}
          {particles.map((p) => (
            <Particle key={p.id} x={p.x} y={p.y} color={p.color} />
          ))}
        </svg>

        {/* Tooltip */}
        <AnimatePresence>
          {hoveredPoint && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="absolute pointer-events-none p-3 rounded-xl glass-card text-xs font-mono space-y-1.5 z-20 border border-neon-cyan/40"
              style={{
                left: `${(hoveredPoint.x / width) * 100}%`,
                top: `${Math.max(10, (hoveredPoint.y / height) * 100 - 35)}%`,
                transform: "translate(-50%, -100%)",
                boxShadow: `0 0 30px ${GROUP_COLORS[hoveredPoint.group]?.glow}`,
              }}
            >
              <div className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-full animate-pulse"
                  style={{ backgroundColor: GROUP_COLORS[hoveredPoint.group]?.stroke }}
                />
                <span className="font-bold text-white text-sm">
                  {GROUP_COLORS[hoveredPoint.group]?.name || hoveredPoint.group}
                </span>
              </div>
              <div className="text-slate-300">
                Cycle: <span className="text-neon-cyan font-bold">{hoveredPoint.cycle}</span>
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
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="mt-5 pt-4 border-t border-neon-cyan/20 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-3"
      >
        <div className="flex items-center gap-2">
          <Info size={14} className="text-neon-cyan" />
          <span>G7 Deployable Canary Guard suppresses drift to +0.015 via held-out invariant gating.</span>
        </div>
        <div className="font-mono text-[10px] text-slate-500 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-neon-cyan animate-pulse" />
          canonical_eval_runs.json
        </div>
      </motion.div>
    </motion.div>
  );
};
