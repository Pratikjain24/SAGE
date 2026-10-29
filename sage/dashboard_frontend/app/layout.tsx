import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import {
  Activity,
  ShieldCheck,
  ClipboardCheck,
  Trophy,
  Github,
  Layers,
  Terminal,
  Cpu,
  Lock,
} from "lucide-react";

export const metadata: Metadata = {
  title: "SAGE: Agent Evolution & Safety Drift Benchmark",
  description: "Measuring Safety Drift, Retention, and Proxy Reward Hacking in Self-Evolving Code Agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const analysisNav = [
    { href: "/", label: "Overview", icon: Layers, badge: null },
    { href: "/drift", label: "Drift Explorer", icon: Activity, badge: null },
    { href: "/leaderboard", label: "Leaderboard", icon: Trophy, badge: "G1–G7" },
  ];

  const opsNav = [
    { href: "/dynamic-eval", label: "Dynamic Eval", icon: ShieldCheck, badge: "LIVE" },
    { href: "/audit", label: "Audit Workbench", icon: ClipboardCheck, badge: null },
  ];

  return (
    <html lang="en" className="dark">
      <body className="flex min-h-screen text-slate-100">
        {/* Sidebar */}
        <aside
          className="hidden md:flex w-[240px] shrink-0 flex-col justify-between border-r backdrop-blur-md"
          style={{
            backgroundColor: "rgba(11, 16, 28, 0.95)",
            borderColor: "var(--border-subtle)",
          }}
        >
          <div className="p-5">
            {/* Logo & Brand Header */}
            <div className="flex items-center gap-3 pb-5 mb-5 border-b" style={{ borderColor: "var(--border-subtle)" }}>
              <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500/20 via-sky-500/10 to-transparent border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                <span className="font-mono font-black italic text-cyan-400 text-lg">S</span>
                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-black tracking-tight text-white text-base">SAGE</span>
                  <span className="font-mono text-[9px] font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    v0.1
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 font-medium tracking-tight">
                  Safety Drift Benchmark
                </p>
              </div>
            </div>

            {/* Analysis Group */}
            <div className="mb-6">
              <div className="flex items-center justify-between px-2 mb-2">
                <span className="section-label">Research &amp; Analysis</span>
              </div>
              <nav className="space-y-1">
                {analysisNav.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="group flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all border border-transparent hover:border-slate-700/50"
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon size={15} className="text-slate-400 group-hover:text-cyan-400 transition-colors" />
                        <span>{item.label}</span>
                      </div>
                      {item.badge && (
                        <span className="font-mono text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>

            {/* Operations Group */}
            <div>
              <div className="flex items-center justify-between px-2 mb-2">
                <span className="section-label">Live Instrumentation</span>
              </div>
              <nav className="space-y-1">
                {opsNav.map((item) => {
                  const Icon = item.icon;
                  const isLive = item.badge === "LIVE";
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="group flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all border border-transparent hover:border-slate-700/50"
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon size={15} className={isLive ? "text-cyan-400 group-hover:text-cyan-300" : "text-slate-400 group-hover:text-cyan-400"} />
                        <span>{item.label}</span>
                      </div>
                      {item.badge && (
                        <span className={`font-mono text-[9px] font-bold px-1.5 py-0.5 rounded ${
                          isLive
                            ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 animate-pulse"
                            : "bg-slate-800 text-slate-400 border border-slate-700"
                        }`}>
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Benchmark Environment Footer */}
          <div className="p-4 m-3 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2.5 text-[11px]">
            <div className="flex items-center justify-between text-slate-400">
              <span className="flex items-center gap-1.5 text-slate-300 font-semibold">
                <Lock size={12} className="text-cyan-400" /> Jail Status
              </span>
              <span className="font-mono text-[10px] text-emerald-400 font-bold">ENFORCED</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Benchmark Tasks</span>
              <span className="font-mono text-slate-200 font-bold">100 / 100</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Defense Layers</span>
              <span className="font-mono text-cyan-400 font-bold">7 / 7 Active</span>
            </div>
            <div className="pt-1.5 border-t border-slate-800/80 text-[10px] text-slate-500 font-mono">
              NeurIPS 2024 Evaluation
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header Bar */}
          <header
            className="h-14 border-b flex items-center justify-between px-6 shrink-0 backdrop-blur-md sticky top-0 z-30"
            style={{
              backgroundColor: "rgba(7, 10, 18, 0.8)",
              borderColor: "var(--border-subtle)",
            }}
          >
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
                <span className="text-xs font-mono font-semibold text-slate-300">
                  Sandboxed Jail Active
                </span>
              </div>
              <span className="text-slate-600">|</span>
              <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
                AST Mutation Gate &bull; Canary Verifier G7
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-400">
                <Cpu size={12} className="text-cyan-400" />
                <span>API :8000</span>
              </div>
              <a
                href="https://github.com/sage/sage"
                target="_blank"
                rel="noreferrer"
                className="px-2.5 py-1 rounded-md bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5"
              >
                <Github size={13} />
                <span>Framework Docs</span>
              </a>
            </div>
          </header>

          {/* Page Body with subtle container padding */}
          <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-8 animate-fade-in">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
