"use client";

import React, { useEffect, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { TrendingUp, ShieldAlert, AlertTriangle, DollarSign, Layers } from "lucide-react";

interface KpiCardsProps {
  successRate: number;
  safetyDrift: number;
  proxyGap: number;
  totalCost: number;
  totalRuns: number;
}

function AnimatedCounter({ value, format = (v) => v.toFixed(1) }: { value: number; format?: (v: number) => string }) {
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, { duration: 1500, bounce: 0.25 });
  const [displayValue, setDisplayValue] = useState("0");

  useEffect(() => {
    motionValue.set(value);
  }, [value, motionValue]);

  useEffect(() => {
    const unsubscribe = springValue.on("change", (latest) => {
      setDisplayValue(format(latest));
    });
    return unsubscribe;
  }, [springValue, format]);

  return <span>{displayValue}</span>;
}

export const KpiCards: React.FC<KpiCardsProps> = ({
  successRate,
  safetyDrift,
  proxyGap,
  totalCost,
  totalRuns,
}) => {
  const isDriftHigh = safetyDrift > 0.05;
  const isGapHigh = proxyGap > 0.08;

  const cards = [
    {
      title: "Capability Success",
      value: `${(successRate * 100).toFixed(1)}%`,
      badge: "Target: ≥ 70%",
      badgeStyle: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      description: "Mean pass rate across 100 tasks",
      progress: Math.min(100, successRate * 100),
      barColor: "bg-gradient-to-r from-cyan-500 to-emerald-400",
      icon: TrendingUp,
      iconColor: "text-emerald-400",
      accentBorder: "hover:border-emerald-500/40",
    },
    {
      title: "Mean Safety Drift",
      value: `+${(safetyDrift * 100).toFixed(1)}%`,
      badge: isDriftHigh ? "Drift Alert" : "Stable Baseline",
      badgeStyle: isDriftHigh
        ? "bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse"
        : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      description: "Violation rate delta vs. cycle 0",
      progress: Math.min(100, (safetyDrift / 0.3) * 100),
      barColor: isDriftHigh ? "bg-gradient-to-r from-amber-500 to-rose-500" : "bg-emerald-500",
      icon: ShieldAlert,
      iconColor: isDriftHigh ? "text-rose-400" : "text-slate-400",
      accentBorder: isDriftHigh ? "hover:border-rose-500/40" : "hover:border-emerald-500/40",
    },
    {
      title: "Proxy Reward Gap",
      value: proxyGap.toFixed(3),
      badge: isGapHigh ? "Gaming Detected" : "Aligned Reward",
      badgeStyle: isGapHigh
        ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
        : "bg-sky-500/10 text-sky-400 border-sky-500/20",
      description: "Automated Proxy − Ground Truth",
      progress: Math.min(100, (proxyGap / 0.25) * 100),
      barColor: isGapHigh ? "bg-gradient-to-r from-sky-500 to-amber-500" : "bg-sky-500",
      icon: AlertTriangle,
      iconColor: isGapHigh ? "text-amber-400" : "text-sky-400",
      accentBorder: "hover:border-amber-500/40",
    },
    {
      title: "Expenditure Enforced",
      value: `$${totalCost.toFixed(2)}`,
      badge: "Budget: $10.00",
      badgeStyle: "bg-slate-800 text-slate-300 border-slate-700",
      description: "Enforced by BudgetGuard ceiling",
      progress: Math.min(100, (totalCost / 10.0) * 100),
      barColor: "bg-gradient-to-r from-blue-500 to-cyan-400",
      icon: DollarSign,
      iconColor: "text-cyan-400",
      accentBorder: "hover:border-cyan-500/40",
    },
    {
      title: "Active Archetypes",
      value: "G1 – G7",
      badge: `${totalRuns > 0 ? totalRuns : 7} Canonical Runs`,
      badgeStyle: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
      description: "100 tasks · 3-seed statistical CI",
      progress: 100,
      barColor: "bg-cyan-400",
      icon: Layers,
      iconColor: "text-cyan-400",
      accentBorder: "hover:border-cyan-500/40",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
            whileHover={{ 
              scale: 1.03,
              rotateX: 2,
              rotateY: 2,
              transition: { duration: 0.2 }
            }}
            style={{ transformStyle: "preserve-3d" }}
            className={`hud-card p-4 flex flex-col justify-between transition-all duration-300 ${c.accentBorder} group relative overflow-hidden`}
          >
            {/* Animated gradient border overlay */}
            <motion.div
              className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
              style={{
                background: `linear-gradient(135deg, ${c.iconColor.includes('emerald') ? 'rgba(16, 185, 129, 0.1)' : 
                  c.iconColor.includes('rose') ? 'rgba(244, 63, 94, 0.1)' :
                  c.iconColor.includes('amber') ? 'rgba(245, 158, 11, 0.1)' :
                  c.iconColor.includes('cyan') ? 'rgba(6, 182, 212, 0.1)' : 
                  'rgba(100, 116, 139, 0.1)'}, transparent)`,
              }}
            />
            
            <div>
              {/* Header: Label + Icon */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400">
                  {c.title}
                </span>
                <motion.div 
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.5 }}
                  className="p-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-400 group-hover:border-slate-700 transition-colors"
                >
                  <Icon size={14} className={c.iconColor} />
                </motion.div>
              </div>

              {/* Value & Badge with animated counter */}
              <div className="flex items-baseline justify-between gap-2 my-1">
                <span className="text-2xl font-black font-mono tracking-tight text-white">
                  {i === 0 ? (
                    <><AnimatedCounter value={successRate * 100} />%</>
                  ) : i === 1 ? (
                    <>+<AnimatedCounter value={safetyDrift * 100} />%</>
                  ) : i === 2 ? (
                    <AnimatedCounter value={proxyGap} format={(v) => v.toFixed(3)} />
                  ) : i === 3 ? (
                    <>$<AnimatedCounter value={totalCost} format={(v) => v.toFixed(2)} /></>
                  ) : (
                    c.value
                  )}
                </span>
                <motion.span 
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: i * 0.1 + 0.3, type: "spring", stiffness: 200 }}
                  className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${c.badgeStyle}`}
                >
                  {c.badge}
                </motion.span>
              </div>

              {/* Subtitle */}
              <p className="text-[11px] text-slate-400 leading-snug">
                {c.description}
              </p>
            </div>

            {/* Micro Progress Bar with animation */}
            <div className="mt-3 pt-2.5 border-t border-slate-800/60">
              <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800/80">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.max(4, c.progress)}%` }}
                  transition={{ duration: 1.2, delay: i * 0.1 + 0.2, ease: "easeOut" }}
                  className={`h-full rounded-full ${c.barColor} shadow-sm`}
                  style={{
                    boxShadow: c.progress > 50 ? '0 0 8px rgba(6, 182, 212, 0.4)' : 'none'
                  }}
                />
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};
