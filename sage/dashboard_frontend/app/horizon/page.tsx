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
            EMPIRICAL ADAPTATION HORIZON
          </span>
          <span className="text-xs font-mono text-slate-400">5 Execution Cycles (C0 to C4) &bull; 9,800 Task Evaluations</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
          Adaptation Horizon: Do Heuristics Compound Forever?
        </h1>
        <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
          Measuring multi-cycle recursive self-evolution across 35 independent runs on Kaggle Dual Tesla T4 GPUs.
          Demonstrates that training adaptation gains plateau at Cycle 3 (+2.5% mean gain) while security boundary drift remains invariant at exactly 0.000.
        </p>
      </div>

      {/* Main Long-Horizon Saturation Chart */}
      <LongHorizonSaturation />

      {/* Deep Analytical Takeaways */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-2.5">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase">
            <Zap size={15} />
            <span>Diminishing Adaptation Returns</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            In early cycles (C0 &rarr; C1 &rarr; C2), evolving agents rapidly incorporate generic failure diagnostics. 
            However, by Cycle 3, training adaptation saturates (+2.5% mean gain across evolving layers), with no unconstrained layer significantly outperforming the frozen control baseline under Welch&apos;s t-test (|t| &lt; 1.4).
          </p>
          <p className="text-[11px] text-slate-400">
            Memory accumulator (G3) overfits past error traces, regressing by -3.3% at Cycle 3 and demonstrating the risk of uncurated memory persistence.
          </p>
        </div>

        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-2.5">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase">
            <ShieldCheck size={15} />
            <span>Guarded Invariance Across All Cycles</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Across all 35 seeds and 9,800 tasks, security boundary drift was <strong className="text-emerald-400">strictly 0.000 (0 violations)</strong>. 
            Instruction alignment in Qwen2.5-Coder combined with SAGE AST tripwires prevented arbitrary vulnerability injection across all cycles.
          </p>
          <p className="text-[11px] text-slate-400">
            Deployable canary gating (G7) confines signed proxy gap divergence within [-0.6%, +2.4%], guaranteeing that persistent state mutations cannot compromise security.
          </p>
        </div>
      </div>
    </div>
  );
}
