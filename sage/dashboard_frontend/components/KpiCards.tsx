"use client";

import React from "react";
import { TrendingUp, ShieldAlert, AlertTriangle, DollarSign, Layers } from "lucide-react";

interface KpiCardsProps {
  successRate: number;
  safetyDrift: number;
  proxyGap: number;
  totalCost: number;
  totalRuns: number;
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
          <div
            key={i}
            className={`hud-card p-4 flex flex-col justify-between transition-all duration-300 ${c.accentBorder} group`}
          >
            <div>
              {/* Header: Label + Icon */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400">
                  {c.title}
                </span>
                <div className="p-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-400 group-hover:border-slate-700 transition-colors">
                  <Icon size={14} className={c.iconColor} />
                </div>
              </div>

              {/* Value & Badge */}
              <div className="flex items-baseline justify-between gap-2 my-1">
                <span className="text-2xl font-black font-mono tracking-tight text-white">
                  {c.value}
                </span>
                <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${c.badgeStyle}`}>
                  {c.badge}
                </span>
              </div>

              {/* Subtitle */}
              <p className="text-[11px] text-slate-400 leading-snug">
                {c.description}
              </p>
            </div>

            {/* Micro Progress Bar */}
            <div className="mt-3 pt-2.5 border-t border-slate-800/60">
              <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800/80">
                <div
                  className={`h-full rounded-full transition-all duration-700 ease-out ${c.barColor}`}
                  style={{ width: `${Math.max(4, c.progress)}%` }}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
