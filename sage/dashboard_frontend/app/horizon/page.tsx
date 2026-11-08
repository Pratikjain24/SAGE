import React from "react";
import { LongHorizonSaturation } from "@/components/LongHorizonSaturation";
import { Clock, TrendingUp, ShieldCheck, Zap } from "lucide-react";

export const dynamic = "force-dynamic";

export default function HorizonPage() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            ASYMPTOTIC DRIFT DYNAMICS
          </span>
          <span className="text-xs font-mono text-slate-400">Multi-Cycle Horizon Scaling (T = 1 to 25 Cycles)</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
          Long-Horizon Behavior: Does Drift Compound Forever?
        </h1>
        <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
          Evaluating the long-term mathematical behavior of unconstrained recursive self-evolution. 
          Proves that security boundary drift saturates asymptotically rather than exploding exponentially.
        </p>
      </div>

      {/* Main Long-Horizon Saturation Chart */}
      <LongHorizonSaturation />

      {/* Deep Analytical Takeaways */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-2.5">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase">
            <Zap size={15} />
            <span>Diminishing Shortcut Returns</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            In early cycles (T = 1 to 5), unconstrained agents rapidly exploit obvious specification shortcuts. 
            However, by Cycle 10, the agent exhausts easily exploitable loopholes.
          </p>
          <p className="text-[11px] text-slate-400">
            Mean drift plateaus at <strong className="text-white">0.312 by Cycle 25</strong>, exhibiting marginal decay where late cycles yield diminishing drift returns.
          </p>
        </div>

        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-2.5">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase">
            <ShieldCheck size={15} />
            <span>Guarded Invariance Across Horizons</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Canary-guarded architectures (G6) maintain <strong className="text-emerald-400">near-zero drift (+0.02)</strong> across all cycle horizons tested.
          </p>
          <p className="text-[11px] text-slate-400">
            Because unsafe proposals are rejected before entering persistent state, degradation cannot compound regardless of how many cycles are executed.
          </p>
        </div>
      </div>
    </div>
  );
}
