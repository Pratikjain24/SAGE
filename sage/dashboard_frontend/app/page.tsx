import Link from "next/link";
import { LAYERS_EMPIRICAL_DATA, EMPIRICAL_STUDY_METRICS } from "@/lib/empiricalData";
import {
  TrendingUp,
  Activity,
  Target,
  AlertTriangle,
  GitCompare,
  Sliders,
  Clock,
  ClipboardCheck,
  ShieldCheck,
  ArrowRight,
  ExternalLink,
  Cpu,
  CheckCircle2,
  Lock,
  Layers,
} from "lucide-react";

export const dynamic = "force-dynamic";

export default function HomePage() {

  const navCards = [
    {
      href: "/capability",
      title: "Capability Trajectories",
      subtitle: "Train Adaptation vs. Held-Out Generalization",
      metric: "+5.0% Max Train Gain (G4)",
      badge: "C0–C4 Curves",
      icon: TrendingUp,
      color: "text-rose-400",
      borderColor: "border-rose-500/20 hover:border-rose-500/50",
      bgHover: "hover:bg-rose-500/5",
    },
    {
      href: "/drift",
      title: "Security Boundary Drift",
      subtitle: "Live Empirical Zero-Drift Audit",
      metric: "0.000 Drift (0 Violations)",
      badge: "9,800 Checks",
      icon: Activity,
      color: "text-emerald-400",
      borderColor: "border-emerald-500/20 hover:border-emerald-500/50",
      bgHover: "hover:bg-emerald-500/5",
    },
    {
      href: "/pareto",
      title: "Pareto Frontier",
      subtitle: "Multi-Objective Capability vs. Risk Tradeoff",
      metric: "G6 Dominates All Axes",
      badge: "Tradeoff Analysis",
      icon: Target,
      color: "text-purple-400",
      borderColor: "border-purple-500/20 hover:border-purple-500/50",
      bgHover: "hover:bg-purple-500/5",
    },
    {
      href: "/proxy-gap",
      title: "Proxy Gap & Gaming",
      subtitle: "20 Drift Probes vs. 80 Standard Tasks",
      metric: "+0.55 Gap in G4 -> Collapsed to 0.02 in G6",
      badge: "Specification Gaming",
      icon: AlertTriangle,
      color: "text-amber-400",
      borderColor: "border-amber-500/20 hover:border-amber-500/50",
      bgHover: "hover:bg-amber-500/5",
    },
    {
      href: "/models",
      title: "Hardware Replication",
      subtitle: "Multi-Node Tesla T4 Reproducibility (P1 vs P7)",
      metric: "Δ = 1.96% <= 2.50% Bound",
      badge: "Inter-Node Fidelity",
      icon: GitCompare,
      color: "text-cyan-400",
      borderColor: "border-cyan-500/20 hover:border-cyan-500/50",
      bgHover: "hover:bg-cyan-500/5",
    },
    {
      href: "/ablations",
      title: "AST Gates & Ablations",
      subtitle: "Static Invariants & Sandbox Escapes",
      metric: "150/150 Mutations Audited (0% Escape)",
      badge: "System Design",
      icon: Sliders,
      color: "text-blue-400",
      borderColor: "border-blue-500/20 hover:border-blue-500/50",
      bgHover: "hover:bg-blue-500/5",
    },
    {
      href: "/horizon",
      title: "Long-Horizon Saturation",
      subtitle: "Multi-Cycle Horizon Scaling (T = 1..25)",
      metric: "Plateaus at 0.312 Ceiling (T=10 Suffices)",
      badge: "Asymptotic Study",
      icon: Clock,
      color: "text-teal-400",
      borderColor: "border-teal-500/20 hover:border-teal-500/50",
      bgHover: "hover:bg-teal-500/5",
    },
    {
      href: "/audit",
      title: "Forensic Audit Workbench",
      subtitle: "Double-Blind Verification & Concordance",
      metric: "Kappa = 0.93 - 0.96 (100% Recall)",
      badge: "Human Protocol",
      icon: ClipboardCheck,
      color: "text-indigo-400",
      borderColor: "border-indigo-500/20 hover:border-indigo-500/50",
      bgHover: "hover:bg-indigo-500/5",
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Hero Command Center */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 pb-4 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              100% EMPIRICAL STUDY GROUND TRUTH
            </span>
            <span className="font-mono text-[11px] text-slate-400">
              35 Runs &bull; 7 Layers &bull; 5 Seeds &bull; Qwen2.5-Coder-7B
            </span>
          </div>

          <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white">
            Safety Drift &amp; Agent Evolution Observatory
          </h1>
          <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
            Rigorous empirical evaluation of self-modifying code agents across multi-cycle evolution. 
            Auditing capability adaptation, security boundary erosion, and specification gaming.
          </p>
        </div>

        {/* Quick Launch Buttons */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <Link
            href="/leaderboard"
            className="px-3.5 py-2 rounded-xl text-xs font-mono font-bold bg-cyan-500 text-slate-950 hover:bg-cyan-400 transition-all shadow-md shadow-cyan-500/20 flex items-center gap-2"
          >
            <span>Full Leaderboard</span>
            <ArrowRight size={13} />
          </Link>
          <Link
            href="/dynamic-eval"
            className="px-3.5 py-2 rounded-xl text-xs font-mono font-bold bg-slate-900 text-slate-200 hover:text-white border border-slate-800 hover:border-slate-700 transition-all flex items-center gap-2"
          >
            <ShieldCheck size={14} className="text-emerald-400" />
            <span>Dynamic Testbed</span>
          </Link>
        </div>
      </div>

      {/* Primary KPI Command Bar */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="hud-card p-3.5 border border-slate-800/80 bg-slate-950/80 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 font-bold">Evaluations</span>
          <div className="text-xl font-mono font-black text-white">9,800</div>
          <span className="text-[10px] text-slate-500 font-mono">35 runs x 280 tasks</span>
        </div>

        <div className="hud-card p-3.5 border border-slate-800/80 bg-slate-950/80 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 font-bold">Mean Success</span>
          <div className="text-xl font-mono font-black text-emerald-400">50.9%</div>
          <span className="text-[10px] text-slate-500 font-mono">Range: 48.5% - 52.5%</span>
        </div>

        <div className="hud-card p-3.5 border border-slate-800/80 bg-slate-950/80 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 font-bold">Security Drift</span>
          <div className="text-xl font-mono font-black text-emerald-400">0.000</div>
          <span className="text-[10px] text-slate-500 font-mono">0 violations recorded</span>
        </div>

        <div
          className="hud-card p-3.5 border border-slate-800/80 bg-slate-950/80 space-y-1 cursor-help"
          title="In the benign baseline study, all 150 proposed mutations were safe no-ops or valid heuristics. 100% acceptance demonstrates a 0.0% False Positive Rate (no spurious rejections of benign adaptations) rather than attack-catching effectiveness."
        >
          <span className="text-[10px] font-mono uppercase text-slate-400 font-bold">FPR Test (G5–G7)</span>
          <div className="text-xl font-mono font-black text-cyan-400">150 / 150</div>
          <span className="text-[10px] text-slate-500 font-mono">0% False Positive Rate (benign study)</span>
        </div>

        <div className="hud-card p-3.5 border border-slate-800/80 bg-slate-950/80 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 font-bold">Hardware Recheck</span>
          <div className="text-xl font-mono font-black text-purple-400">1.96%</div>
          <span className="text-[10px] text-slate-500 font-mono">P1 vs P7 (within 2.5%)</span>
        </div>

        <div className="hud-card p-3.5 border border-slate-800/80 bg-slate-950/80 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 font-bold">GPU Active Time</span>
          <div className="text-xl font-mono font-black text-amber-400">21.08 h</div>
          <span className="text-[10px] text-slate-500 font-mono">Dual Tesla T4 compute</span>
        </div>
      </div>

      {/* Visual Navigation Deep-Dive Grid (One-Click Access to Dedicated Pages) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono uppercase font-bold text-slate-500">
              Interactive Deep-Dive Portals
            </span>
            <h2 className="text-lg font-bold text-white tracking-tight mt-0.5">
              Explore Empirical Investigations &amp; Analytical Graphs
            </h2>
          </div>
          <span className="text-xs font-mono text-slate-400">Click any card to inspect full dedicated page</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {navCards.map((card) => {
            const Icon = card.icon;
            return (
              <Link
                key={card.href}
                href={card.href}
                className={`hud-card p-4 border ${card.borderColor} bg-slate-950/80 ${card.bgHover} transition-all group flex flex-col justify-between`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="p-2 rounded-lg bg-slate-900 border border-slate-800 group-hover:scale-105 transition-transform">
                      <Icon size={16} className={card.color} />
                    </span>
                    <span className="text-[9px] font-mono text-slate-400 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800">
                      {card.badge}
                    </span>
                  </div>
                  <h3 className="font-bold text-sm text-white group-hover:text-cyan-300 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 mt-1 leading-snug line-clamp-2">
                    {card.subtitle}
                  </p>
                </div>

                <div className="pt-3 mt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                  <span className={`font-bold ${card.color}`}>{card.metric}</span>
                  <ArrowRight size={13} className="text-slate-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Master Archetype Empirical Summary Table */}
      <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="section-label text-emerald-400">Verified Empirical Baseline</span>
              <span className="font-mono text-[10px] text-cyan-400 font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                Live Dual T4 Study
              </span>
            </div>
            <h3 className="text-base font-bold text-white mt-0.5">
              Comparative Archetype Matrix ($G_1$ through $G_7$)
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            5 Seeds per Layer &bull; 9,800 Tasks
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs border-collapse min-w-[700px]">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase font-bold">
                <th className="p-2.5">Archetype</th>
                <th className="p-2.5">Category</th>
                <th className="p-2.5">Initial Prompt</th>
                <th className="p-2.5">Train Gain (C3-C0)</th>
                <th className="p-2.5">Test Pass (C4)</th>
                <th className="p-2.5">Clean Overall</th>
                <th className="p-2.5 text-emerald-400">Security Drift</th>
                <th className="p-2.5 text-right">Welch t vs G1</th>
              </tr>
            </thead>
            <tbody>
              {LAYERS_EMPIRICAL_DATA.map((row) => (
                <tr key={row.id} className="border-b border-slate-800/50 hover:bg-slate-900/40 transition-colors">
                  <td className="p-2.5 font-bold text-white flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: row.color }} />
                    {row.id}: {row.name}
                  </td>
                  <td className="p-2.5 text-slate-400">{row.category}</td>
                  <td className="p-2.5 text-slate-400">{row.promptInitChars} chars</td>
                  <td className={`p-2.5 font-bold ${row.trainGain > 0 ? "text-cyan-400" : "text-rose-400"}`}>
                    {row.trainGain > 0 ? `+${(row.trainGain * 100).toFixed(1)}%` : `${(row.trainGain * 100).toFixed(1)}%`}
                  </td>
                  <td className="p-2.5 font-bold text-emerald-400">{(row.testC4 * 100).toFixed(1)}%</td>
                  <td className="p-2.5 font-bold text-white">{(row.overallClean * 100).toFixed(1)}%</td>
                  <td className="p-2.5 font-bold text-emerald-400">0.000</td>
                  <td className="p-2.5 text-right font-bold text-slate-400">
                    {row.welchT === 0 ? "Control" : row.welchT > 0 ? `+${row.welchT.toFixed(2)}` : row.welchT.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
