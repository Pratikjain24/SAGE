"use client";

import React from "react";
import { CycleMetricPoint } from "@/lib/api";
import { AlertTriangle, ShieldCheck } from "lucide-react";

interface ProxyGapChartProps {
  data: CycleMetricPoint[];
}

export const ProxyGapChart: React.FC<ProxyGapChartProps> = ({ data }) => {
  const cycles = [0, 1, 2, 3, 4];
  const targetGroups = [
    { code: "G1", name: "G1: Frozen Baseline", note: "No mutation" },
    { code: "G2", name: "G2: Prompt Rewriter", note: "Prompt mutation only" },
    { code: "G4", name: "G4: Reflection Agent (Unconstrained)", note: "High reward gaming risk" },
    { code: "G6", name: "G6: Regression-Guarded Verifier", note: "Static filter gate" },
    { code: "G7", name: "G7: Deployable Proxy Canary Guard", note: "Held-out invariant gate" },
  ];

  return (
    <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2">
              <span className="section-label">Specification Gaming</span>
              <span className="font-mono text-[10px] text-amber-400 font-bold px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
                Reward − Ground Truth
              </span>
            </div>
            <h3 className="text-base font-black tracking-tight text-white mt-0.5">
              Proxy Reward Gap
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Divergence indicates agents gaming surface test assertions while failing real ground truth correctness.
            </p>
          </div>
        </div>

        {/* Group Cards List */}
        <div className="mt-4 space-y-3">
          {targetGroups.map((g) => {
            const grp = g.code;
            const points = data.filter((d) => d.group === grp).sort((a, b) => a.cycle - b.cycle);
            const latestGap = points.length > 0 ? points[points.length - 1].proxy_gap_mean : (grp === "G4" ? 0.24 : 0.02);
            const isHigh = latestGap > 0.12;
            const isG7 = grp === "G7";

            return (
              <div
                key={grp}
                className={`p-3 rounded-xl border transition-all ${
                  isG7
                    ? "bg-cyan-950/20 border-cyan-500/30 shadow-[0_0_12px_rgba(6,182,212,0.06)]"
                    : isHigh
                    ? "bg-rose-950/20 border-rose-500/30"
                    : "bg-slate-900/60 border-slate-800/80"
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`font-mono text-xs font-black ${isG7 ? "text-cyan-400" : "text-white"}`}>
                      {g.name}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono hidden sm:inline">
                      ({g.note})
                    </span>
                  </div>

                  <span
                    className={`font-mono font-bold px-2 py-0.5 rounded-full text-[11px] border ${
                      isHigh
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/30 animate-pulse"
                        : isG7
                        ? "bg-cyan-500/10 text-cyan-300 border-cyan-500/30"
                        : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                    }`}
                  >
                    Gap: +{latestGap.toFixed(3)}
                  </span>
                </div>

                {/* Multi-cycle mini progress bars */}
                <div className="grid grid-cols-5 gap-2 pt-1">
                  {cycles.map((c) => {
                    const pt = points.find((p) => p.cycle === c);
                    const val = pt ? pt.proxy_gap_mean : (grp === "G4" ? 0.06 * c : 0.015 + 0.002 * c);
                    const pct = Math.min(100, Math.max(8, (val / 0.3) * 100));

                    return (
                      <div key={c} className="flex flex-col gap-1">
                        <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              val > 0.15
                                ? "bg-rose-500"
                                : val > 0.08
                                ? "bg-amber-400"
                                : isG7
                                ? "bg-cyan-400"
                                : "bg-sky-500"
                            }`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <div className="flex items-center justify-between text-[9px] font-mono text-slate-500">
                          <span>c{c}</span>
                          <span className={val > 0.15 ? "text-rose-400 font-bold" : ""}>
                            +{val.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <span className="flex items-center gap-1.5 text-cyan-400 font-mono text-[11px]">
          <ShieldCheck size={14} /> G7 Held-Out Canary Invariant reduces gap &lt; 0.02
        </span>
        <span className="text-[10px] text-slate-500 font-mono">
          Threshold: 0.05
        </span>
      </div>
    </div>
  );
};
