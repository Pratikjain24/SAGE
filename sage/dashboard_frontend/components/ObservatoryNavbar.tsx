"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Activity,
  Layers,
  Trophy,
  TrendingUp,
  Target,
  AlertTriangle,
  GitCompare,
  Sliders,
  Clock,
  ClipboardCheck,
  ShieldCheck,
  Terminal,
  Zap,
} from "lucide-react";

export const OBSERVATORY_STAGES = [
  { index: "01", href: "/", label: "Executive Summary", short: "Overview", icon: Layers, code: "01" },
  { index: "02", href: "/leaderboard", label: "Archetype Leaderboard", short: "Leaderboard", icon: Trophy, code: "4.1" },
  { index: "03", href: "/capability", label: "Capability Trajectories", short: "Capability", icon: TrendingUp, code: "4.2" },
  { index: "04", href: "/drift", label: "Security Drift Audit", short: "Drift", icon: Activity, code: "4.3" },
  { index: "05", href: "/pareto", label: "The Pareto Frontier", short: "Pareto", icon: Target, code: "4.5" },
  { index: "06", href: "/proxy-gap", label: "Proxy Gap & Gaming", short: "Proxy Gap", icon: AlertTriangle, code: "4.4" },
  { index: "07", href: "/models", label: "Hardware & Cross-Family", short: "Replication", icon: GitCompare, code: "4.6" },
  { index: "08", href: "/ablations", label: "Design Ablations", short: "Ablations", icon: Sliders, code: "4.7" },
  { index: "09", href: "/horizon", label: "Horizon Saturation", short: "Horizon", icon: Clock, code: "4.8" },
  { index: "10", href: "/audit", label: "Human Audit Workbench", short: "Audit", icon: ClipboardCheck, code: "4.9" },
  { index: "11", href: "/dynamic-eval", label: "Dynamic Live Testbed", short: "Live Eval", icon: ShieldCheck, code: "Live" },
];

export function ObservatoryNavbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [dataTier, setDataTier] = useState<"empirical" | "canonical">("empirical");
  const [apiAlive, setApiAlive] = useState<boolean | null>(null);

  const ping = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const r = await fetch("http://localhost:8000/health", { signal: controller.signal });
      clearTimeout(timeoutId);
      setApiAlive(r.ok);
    } catch {
      setApiAlive(false);
    }
  }, []);

  useEffect(() => {
    ping();
    const id = setInterval(ping, 30_000);
    return () => clearInterval(id);
  }, [ping]);

  const currentIndex = OBSERVATORY_STAGES.findIndex(
    (s) => s.href === pathname || (s.href !== "/" && pathname.startsWith(s.href))
  );
  const activeIdx = currentIndex >= 0 ? currentIndex : 0;
  const currentStage = OBSERVATORY_STAGES[activeIdx];

  const prevStage = activeIdx > 0 ? OBSERVATORY_STAGES[activeIdx - 1] : null;
  const nextStage = activeIdx < OBSERVATORY_STAGES.length - 1 ? OBSERVATORY_STAGES[activeIdx + 1] : null;

  // Keyboard arrow navigation
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key === "ArrowRight" && nextStage) {
        router.push(nextStage.href);
      } else if (e.key === "ArrowLeft" && prevStage) {
        router.push(prevStage.href);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [nextStage, prevStage, router]);

  return (
    <>
      {/* Top Floating Horizon Command Bar */}
      <header className="sticky top-0 z-40 w-full backdrop-blur-xl bg-[#090e1a]/90 border-b border-[#1f2d4d]">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          {/* Logo & Hardware Beacon */}
          <div className="flex items-center gap-3 shrink-0">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-400/40 flex items-center justify-center text-cyan-400 font-mono font-black text-sm group-hover:border-cyan-300 transition-all shadow-[0_0_12px_rgba(0,229,255,0.25)]">
                S
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="font-display font-extrabold tracking-tight text-white text-sm group-hover:text-cyan-300 transition-colors">
                    SAGE OBSERVATORY
                  </span>
                  <span className="font-mono text-[9px] font-bold px-1.5 py-0.2 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                    LIVE
                  </span>
                </div>
                <span className="text-[10px] font-mono text-[#8da2c0]">
                  Kaggle 2x T4 &bull; 35 Seeds
                </span>
              </div>
            </Link>
          </div>

          {/* Horizon Stage Strip (Slide-Style Top Navigation) */}
          <nav className="hidden lg:flex items-center gap-1 overflow-x-auto py-1 px-2 rounded-xl bg-[#0d162b] border border-[#1d2c4e] max-w-[850px] scrollbar-none">
            {OBSERVATORY_STAGES.map((stage, idx) => {
              const Icon = stage.icon;
              const isActive = activeIdx === idx;
              return (
                <Link
                  key={stage.href}
                  href={stage.href}
                  className={`group relative flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono transition-all whitespace-nowrap ${
                    isActive
                      ? "bg-cyan-500 text-slate-950 font-bold shadow-[0_0_14px_rgba(0,229,255,0.4)]"
                      : "text-[#8da2c0] hover:text-white hover:bg-[#142247]/70"
                  }`}
                >
                  <span className={`text-[10px] font-bold ${isActive ? "text-slate-900" : "text-cyan-400/80"}`}>
                    {stage.code}
                  </span>
                  <Icon size={12} className={isActive ? "text-slate-950" : "text-[#8da2c0] group-hover:text-white"} />
                  <span className="font-medium">{stage.short}</span>
                </Link>
              );
            })}
          </nav>

          {/* Quick Controls & Stage Stepper */}
          <div className="flex items-center gap-2.5 shrink-0">
            {/* Live API Health Status */}
            <button
              onClick={ping}
              title="Click to check SAGE API health (http://localhost:8000/health)"
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] font-mono hover:border-slate-700 transition-colors"
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  apiAlive === null ? "bg-slate-500 animate-pulse" :
                  apiAlive ? "bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" : "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]"
                }`}
              />
              <span className={apiAlive === null ? "text-slate-400" : apiAlive ? "text-emerald-400 font-bold" : "text-red-400 font-bold"}>
                {apiAlive === null ? "API..." : apiAlive ? "API LIVE" : "API DOWN"}
              </span>
            </button>

            {/* Real Data Status Badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>100% Real Data</span>
            </div>

            {/* Stepper Controls with Keyboard Hints */}
            <div className="flex items-center gap-1.5">
              <div
                className="hidden xl:flex items-center gap-1 text-[10px] font-mono text-slate-400 select-none px-2 py-1 rounded-lg bg-slate-900/60 border border-slate-800/80"
                title="Use Left and Right Arrow keys on your keyboard to advance slides/pages"
              >
                <kbd className="px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 text-cyan-400 font-bold text-[9px] shadow-sm">←</kbd>
                <kbd className="px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 text-cyan-400 font-bold text-[9px] shadow-sm">→</kbd>
                <span className="text-[#8da2c0] text-[10px] ml-0.5">navigate</span>
              </div>

              <div className="flex items-center gap-1 bg-[#0d162b] border border-[#1d2c4e] p-1 rounded-lg">
                <button
                  onClick={() => prevStage && router.push(prevStage.href)}
                  disabled={!prevStage}
                  title={prevStage ? `← Previous section: ${prevStage.short} (Left Arrow key)` : "At start"}
                  className="p-1 rounded text-[#8da2c0] hover:text-white hover:bg-[#142247] disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                >
                  <ChevronLeft size={16} />
                </button>

                <span className="font-mono text-xs text-cyan-400 font-bold px-1.5">
                  {currentStage.index} <span className="text-slate-600">/</span> {OBSERVATORY_STAGES.length}
                </span>

                <button
                  onClick={() => nextStage && router.push(nextStage.href)}
                  disabled={!nextStage}
                  title={nextStage ? `Next section: ${nextStage.short} → (Right Arrow key)` : "At end"}
                  className="p-1 rounded text-[#8da2c0] hover:text-white hover:bg-[#142247] disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Floating Bottom Horizon Navigator Dock */}
      <aside className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 hidden sm:flex items-center gap-3 px-4 py-2 rounded-full bg-[#0d162b]/95 border border-cyan-500/30 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.6)]">
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="text-cyan-400 font-bold">STAGE {currentStage.index}:</span>
          <span className="text-white font-semibold">{currentStage.label}</span>
        </div>

        <div className="h-3 w-px bg-slate-700" />

        {/* Micro-dot stepper */}
        <div className="flex items-center gap-1.5">
          {OBSERVATORY_STAGES.map((s, idx) => (
            <Link
              key={s.href}
              href={s.href}
              title={`${s.code}: ${s.label}`}
              className={`h-2 rounded-full transition-all ${
                activeIdx === idx
                  ? "w-6 bg-cyan-400 shadow-[0_0_8px_rgba(0,229,255,0.7)]"
                  : "w-2 bg-slate-700 hover:bg-slate-500"
              }`}
            />
          ))}
        </div>

        <div className="h-3 w-px bg-slate-700" />

        <div className="flex items-center gap-1 text-[10px] font-mono text-slate-400">
          <span className="px-1 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">←</span>
          <span className="px-1 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">→</span>
          <span className="text-[#8da2c0]">keys to navigate</span>
        </div>
      </aside>
    </>
  );
}

