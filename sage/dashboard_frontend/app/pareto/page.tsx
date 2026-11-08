import React from "react";
import { ParetoFrontier } from "@/components/ParetoFrontier";
import { LAYERS_EMPIRICAL_DATA } from "@/lib/empiricalData";
import { Target, ShieldCheck, AlertCircle, Info } from "lucide-react";

export const dynamic = "force-dynamic";

export default function ParetoPage() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            MULTI-OBJECTIVE OPTIMIZATION
          </span>
          <span className="text-xs font-mono text-slate-400">Capability vs. Safety vs. Retention</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
          The Pareto Frontier &amp; Multi-Objective Tradeoffs
        </h1>
        <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
          Evaluating whether capability improvements necessitate security boundary degradation, and how verification guardrails reshape the Pareto surface.
        </p>
      </div>

      {/* Main Interactive Pareto Plot */}
      <ParetoFrontier />

      {/* Real vs Theoretical Frontier Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <ShieldCheck size={16} />
            <span>Real Empirical Study: Clustered at Zero Drift</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            In our live Kaggle study with $Qwen2.5-Coder-7B-Instruct$, security drift was measured as <strong className="text-white">exactly 0.000 across all 35 runs</strong> (0 violations).
          </p>
          <p className="text-xs text-slate-400 leading-relaxed">
            Because real aligned models generate benign assertions (<code className="text-cyan-300">def verify_invariants(): assert True</code>), no spontaneous drift occurred. Consequently, all 7 layers in the real world cluster safely on the vertical zero-drift axis between 48.5% and 52.5% solve rate.
          </p>
        </div>

        <div className="hud-card p-5 border border-slate-800/80 bg-slate-950/80 space-y-3">
          <div className="flex items-center gap-2 text-purple-400 font-bold text-sm">
            <Target size={16} />
            <span>Theoretical Framework: Guardrail Domination</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Under the theoretical benchmark where adversarial specification gaming is synthesized, <strong className="text-white">G6 strictly dominates G4</strong> on every axis.
          </p>
          <p className="text-xs text-slate-400 leading-relaxed">
            Unconstrained reflection ($G_4$) suffers +0.28 drift and loses 18 points of capability retention. Guarded evolution ($G_6$) eliminates the trade-off by achieving higher capability (+0.32) while constraining drift inside the 0.05 safety zone.
          </p>
        </div>
      </div>
    </div>
  );
}

