import { fetchRun, fetchTrajectories, fetchCycles } from "@/lib/api";
import { TrajectoryViewer } from "@/components/TrajectoryViewer";
import { DriftCurve } from "@/components/DriftCurve";
import Link from "next/link";
import { ArrowLeft, GitBranch, Shield, Terminal, Zap, FileText } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function RunDetailPage({ params }: { params: { id: string } }) {
  const runId = params.id;
  const run = await fetchRun(runId);
  const trajectories = await fetchTrajectories(runId, { limit: 100 });
  const cycles = await fetchCycles(runId);

  const proposals = trajectories.filter(
    (e) => e.event_type === "evolution_proposal" || e.event_type === "evolution_decision" || e.event_type === "rollback"
  );
  const safetyEvents = trajectories.filter((e) => e.event_type === "safety_check");

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition-colors"
          >
            <ArrowLeft size={16} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-black font-mono text-white">{runId}</h2>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 font-semibold border border-emerald-500/30 font-mono">
                COMPLETED
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Experiment Run Matrix Details &amp; Trajectory Inspector
            </p>
          </div>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="hud-card p-4 border border-slate-800/80 bg-slate-950/80">
          <div className="text-[11px] text-slate-400 font-mono uppercase font-bold">Total Trajectory Events</div>
          <div className="text-2xl font-mono font-black text-cyan-400 mt-1">{trajectories.length}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Streamed JSONL checkpoints</div>
        </div>
        <div className="hud-card p-4 border border-slate-800/80 bg-slate-950/80">
          <div className="text-[11px] text-slate-400 font-mono uppercase font-bold">Evolution Steps</div>
          <div className="text-2xl font-mono font-black text-purple-400 mt-1">{proposals.length}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Metaprompt mutations proposed</div>
        </div>
        <div className="hud-card p-4 border border-slate-800/80 bg-slate-950/80">
          <div className="text-[11px] text-slate-400 font-mono uppercase font-bold">Safety Interceptions</div>
          <div className="text-2xl font-mono font-black text-rose-400 mt-1">{safetyEvents.length}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">AST gate security checks</div>
        </div>
        <div className="hud-card p-4 border border-slate-800/80 bg-slate-950/80">
          <div className="text-[11px] text-slate-400 font-mono uppercase font-bold">Storage Path</div>
          <div className="text-xs font-mono text-slate-300 mt-2 truncate bg-slate-900 p-1.5 rounded border border-slate-800">
            experiments/runs/{runId}
          </div>
        </div>
      </div>

      {/* Drift curve for this specific run */}
      <DriftCurve data={cycles} />

      {/* Evolution Proposals & Decisions Timeline */}
      <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80">
        <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-800/80">
          <GitBranch size={18} className="text-purple-400" />
          <h3 className="text-base font-black tracking-tight text-white">
            Inter-Cycle Evolution &amp; Verifier Gating Timeline
          </h3>
        </div>

        <div className="space-y-3">
          {proposals.length === 0 ? (
            <div className="text-xs text-slate-500 py-4 font-mono text-center">
              No evolution events recorded yet.
            </div>
          ) : (
            proposals.map((p, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl flex items-start justify-between gap-4 bg-slate-900/60 border border-slate-800/80 hover:bg-slate-900 transition-colors"
              >
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs font-black text-cyan-400">
                      Cycle {p.cycle}
                    </span>
                    <span className="text-[11px] px-2 py-0.5 rounded font-mono bg-slate-800 text-slate-300 border border-slate-700">
                      {p.group} ({p.agent_version})
                    </span>
                    <span
                      className={`text-[10px] px-2.5 py-0.5 rounded-full font-mono font-bold uppercase border ${
                        p.payload.decision === "accepted" || p.event_type === "evolution_proposal"
                          ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
                          : "bg-rose-500/15 text-rose-300 border-rose-500/30"
                      }`}
                    >
                      {p.event_type} : {p.payload.decision || "Proposed"}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-2 font-mono leading-relaxed">
                    {p.payload.rationale || p.payload.reason || JSON.stringify(p.payload)}
                  </p>
                </div>
                <div className="text-[11px] font-mono text-slate-500 shrink-0">
                  {new Date(p.ts).toLocaleTimeString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Trajectory Stream Viewer */}
      <TrajectoryViewer events={trajectories} />
    </div>
  );
}
