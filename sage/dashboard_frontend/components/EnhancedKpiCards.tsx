"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { TrendingUp, ShieldAlert, AlertTriangle, DollarSign, Layers, LucideIcon } from "lucide-react";

interface KpiCardsProps {
  successRate: number;
  safetyDrift: number;
  proxyGap: number;
  totalCost: number;
  totalRuns: number;
}

interface CardConfig {
  title: string;
  value: string;
  numericValue?: number;
  badge: string;
  badgeStyle: string;
  description: string;
  progress: number;
  barColor: string;
  icon: LucideIcon;
  iconColor: string;
  accentBorder: string;
  glowColor: string;
}

const AnimatedCounter: React.FC<{ value: number; format?: (n: number) => string; duration?: number }> = ({
  value,
  format = (n) => n.toFixed(1),
  duration = 1.5,
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  const animatedValue = useSpring(0, { damping: 30, stiffness: 100 });

  useEffect(() => {
    animatedValue.set(value);
    const unsubscribe = animatedValue.on("change", (latest) => {
      setDisplayValue(latest);
    });
    return () => unsubscribe();
  }, [value, animatedValue]);

  return <>{format(displayValue)}</>;
};

const Card3D: React.FC<{ children: React.ReactNode; glowColor: string; index: number }> = ({
  children,
  glowColor,
  index,
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const mouseX = e.clientX - centerX;
    const mouseY = e.clientY - centerY;
    
    setRotateX(-(mouseY / rect.height) * 10);
    setRotateY((mouseX / rect.width) * 10);
  };

  const handleMouseLeave = () => {
    setRotateX(0);
    setRotateY(0);
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        transformStyle: "preserve-3d",
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
        transition: "transform 0.2s ease-out",
      }}
      className="group relative"
    >
      {/* Glow effect */}
      <div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl"
        style={{
          background: `radial-gradient(circle at center, ${glowColor}, transparent 70%)`,
          transform: "translateZ(-10px)",
        }}
      />
      
      {/* Card content */}
      <div className="relative glass-card p-5 h-full flex flex-col justify-between">
        {children}
      </div>
    </motion.div>
  );
};

export const EnhancedKpiCards: React.FC<KpiCardsProps> = ({
  successRate,
  safetyDrift,
  proxyGap,
  totalCost,
  totalRuns,
}) => {
  const isDriftHigh = safetyDrift > 0.05;
  const isGapHigh = proxyGap > 0.08;

  const cards: CardConfig[] = [
    {
      title: "Capability Success",
      value: `${(successRate * 100).toFixed(1)}%`,
      numericValue: successRate * 100,
      badge: "Target: ≥ 70%",
      badgeStyle: "bg-emerald-500/15 text-emerald-300 border-emerald-400/30",
      description: "Mean pass rate across 100 tasks",
      progress: Math.min(100, successRate * 100),
      barColor: "from-neon-cyan via-neon-green to-emerald-400",
      icon: TrendingUp,
      iconColor: "text-neon-green",
      accentBorder: "hover:border-neon-green/60",
      glowColor: "rgba(0, 255, 159, 0.3)",
    },
    {
      title: "Mean Safety Drift",
      value: `+${(safetyDrift * 100).toFixed(1)}%`,
      numericValue: safetyDrift * 100,
      badge: isDriftHigh ? "Drift Alert" : "Stable Baseline",
      badgeStyle: isDriftHigh
        ? "bg-rose-500/15 text-rose-300 border-rose-400/30 animate-pulse"
        : "bg-emerald-500/15 text-emerald-300 border-emerald-400/30",
      description: "Violation rate delta vs. cycle 0",
      progress: Math.min(100, (safetyDrift / 0.3) * 100),
      barColor: isDriftHigh ? "from-amber-500 via-rose-500 to-rose-600" : "from-emerald-400 to-emerald-500",
      icon: ShieldAlert,
      iconColor: isDriftHigh ? "text-rose-400" : "text-slate-400",
      accentBorder: isDriftHigh ? "hover:border-rose-500/60" : "hover:border-emerald-500/60",
      glowColor: isDriftHigh ? "rgba(255, 0, 85, 0.3)" : "rgba(0, 255, 159, 0.3)",
    },
    {
      title: "Proxy Reward Gap",
      value: proxyGap.toFixed(3),
      numericValue: proxyGap,
      badge: isGapHigh ? "Gaming Detected" : "Aligned Reward",
      badgeStyle: isGapHigh
        ? "bg-amber-500/15 text-amber-300 border-amber-400/30"
        : "bg-sky-500/15 text-sky-300 border-sky-400/30",
      description: "Automated Proxy − Ground Truth",
      progress: Math.min(100, (proxyGap / 0.25) * 100),
      barColor: isGapHigh ? "from-sky-400 via-amber-400 to-amber-500" : "from-sky-400 to-sky-500",
      icon: AlertTriangle,
      iconColor: isGapHigh ? "text-amber-400" : "text-sky-400",
      accentBorder: "hover:border-amber-500/60",
      glowColor: "rgba(255, 166, 0, 0.3)",
    },
    {
      title: "Expenditure Enforced",
      value: `$${totalCost.toFixed(2)}`,
      numericValue: totalCost,
      badge: "Budget: $10.00",
      badgeStyle: "bg-slate-800/60 text-slate-300 border-slate-600/40",
      description: "Enforced by BudgetGuard ceiling",
      progress: Math.min(100, (totalCost / 10.0) * 100),
      barColor: "from-neon-cyan via-blue-500 to-neon-cyan",
      icon: DollarSign,
      iconColor: "text-neon-cyan",
      accentBorder: "hover:border-neon-cyan/60",
      glowColor: "rgba(0, 240, 255, 0.3)",
    },
    {
      title: "Active Archetypes",
      value: "G1 – G7",
      badge: `${totalRuns > 0 ? totalRuns : 7} Canonical Runs`,
      badgeStyle: "bg-cyan-500/15 text-cyan-300 border-cyan-400/30",
      description: "100 tasks · 3-seed statistical CI",
      progress: 100,
      barColor: "from-neon-purple via-neon-pink to-neon-purple",
      icon: Layers,
      iconColor: "text-neon-purple",
      accentBorder: "hover:border-neon-purple/60",
      glowColor: "rgba(184, 71, 255, 0.3)",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <Card3D key={index} glowColor={card.glowColor} index={index}>
            {/* Header */}
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="section-label text-[10px]">
                  {card.title}
                </span>
                <motion.div
                  whileHover={{ scale: 1.15, rotate: 360 }}
                  transition={{ duration: 0.5 }}
                  className="p-2 rounded-lg bg-surface-3/80 border border-neon-cyan/20 group-hover:border-neon-cyan/40 transition-colors"
                >
                  <Icon size={14} className={card.iconColor} />
                </motion.div>
              </div>

              {/* Value & Badge */}
              <div className="flex items-baseline justify-between gap-2 my-2">
                <motion.span
                  className="text-3xl font-black font-mono tracking-tight text-white"
                  whileHover={{ scale: 1.05 }}
                >
                  {card.numericValue !== undefined ? (
                    <AnimatedCounter value={card.numericValue} format={(n) => card.value} />
                  ) : (
                    card.value
                  )}
                </motion.span>
                <span className={`text-[9px] font-mono font-semibold px-2 py-1 rounded-full border ${card.badgeStyle}`}>
                  {card.badge}
                </span>
              </div>

              {/* Description */}
              <p className="text-[10px] text-slate-400 leading-snug">
                {card.description}
              </p>
            </div>

            {/* Progress Bar */}
            <div className="mt-4 pt-3 border-t border-neon-cyan/10">
              <div className="h-2 w-full bg-surface-4/60 rounded-full overflow-hidden border border-neon-cyan/10">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.max(4, card.progress)}%` }}
                  transition={{ delay: index * 0.1 + 0.5, duration: 1.2, ease: "easeOut" }}
                  className={`h-full rounded-full bg-gradient-to-r ${card.barColor} relative`}
                  style={{ boxShadow: `0 0 10px ${card.glowColor}` }}
                >
                  {/* Shimmer effect */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                    initial={{ x: "-100%" }}
                    animate={{ x: "200%" }}
                    transition={{ repeat: Infinity, duration: 2, ease: "linear", delay: index * 0.1 + 1 }}
                  />
                </motion.div>
              </div>
            </div>
          </Card3D>
        );
      })}
    </div>
  );
};
