"use client";

import React, { useEffect, useState } from "react";
import { fetchAuditQueue, submitAuditLabel, AuditQueueItem } from "@/lib/api";
import { ClipboardCheck, ShieldAlert, AlertTriangle, Check, RefreshCw, UserCheck } from "lucide-react";

export default function AuditPage() {
  const [queue, setQueue] = useState<AuditQueueItem[]>([]);
  const [selectedIdx, setSelectedIdx] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [annotatorId, setAnnotatorId] = useState<string>("evaluator_alice");

  // Form states
  const [isViolation, setIsViolation] = useState<boolean>(false);
  const [isRewardHacked, setIsRewardHacked] = useState<boolean>(false);
  const [severity, setSeverity] = useState<string>("none");
  const [notes, setNotes] = useState<string>("");
  const [submittedIds, setSubmittedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    setLoading(true);
    const data = await fetchAuditQueue();
    setQueue(data);
    setLoading(false);
  };

  const currentItem = queue[selectedIdx];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentItem) return;

    setSubmitting(true);
    try {
      await submitAuditLabel({
        audit_id: currentItem.audit_id,
        run_id: currentItem.run_id,
        annotator_id: annotatorId,
        is_violation: isViolation,
        is_reward_hacked: isRewardHacked,
        failure_severity: severity,
        notes,
      });

      setSubmittedIds((prev) => new Set(prev).add(currentItem.audit_id));

      if (selectedIdx < queue.length - 1) {
        setSelectedIdx(selectedIdx + 1);
        setIsViolation(false);
        setIsRewardHacked(false);
        setSeverity("none");
        setNotes("");
      }
    } catch (err) {
      alert("Failed to save label: " + String(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
              Double-Blind Audit
            </span>
            <span className="font-mono text-xs text-slate-400">Stratified Sample (5–10%)</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight flex items-center gap-2">
            <ClipboardCheck className="text-cyan-400" /> Human Evaluation Workbench
          </h2>
          <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-xl leading-relaxed">
            Independent human annotator verification of agent tool calls, execution transcripts, and reward hacking behavior.
          </p>
        </div>

        <button
          onClick={loadQueue}
          className="btn-secondary"
        >
          <RefreshCw size={13} className={loading ? "animate-spin text-cyan-400" : ""} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {loading ? (
        <div className="text-center py-16 text-slate-500 text-sm font-mono">
          Loading audit queue...
        </div>
      ) : queue.length === 0 ? (
        <div className="hud-card p-12 text-center text-slate-400 space-y-2">
          <p className="text-sm">No audit queue items currently available.</p>
          <p className="text-xs text-slate-500 font-mono">
            Execute benchmark cycles or export an audit sample via <code className="text-cyan-400 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800">sage audit</code>.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Queue List */}
          <div className="lg:col-span-4 space-y-2">
            <div className="section-label mb-2">
              Sampled Trajectories ({queue.length})
            </div>
            <div className="space-y-2 max-h-[620px] overflow-y-auto pr-1">
              {queue.map((item, idx) => {
                const isSelected = selectedIdx === idx;
                const isDone = submittedIds.has(item.audit_id);
                return (
                  <button
                    key={item.audit_id}
                    onClick={() => setSelectedIdx(idx)}
                    className={`w-full text-left p-3.5 rounded-xl transition-all flex flex-col gap-1.5 border ${
                      isSelected
                        ? "bg-slate-900/90 border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.1)]"
                        : "bg-slate-900/50 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/70"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-cyan-400">
                        {item.task_id}
                      </span>
                      {isDone && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                          <Check size={10} /> Labeled
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400">
                      <span>Cycle {item.cycle}</span>
                      <span>&bull;</span>
                      <span className="text-slate-300 font-bold">{item.group}</span>
                      <span>&bull;</span>
                      <span>Seed {item.seed}</span>
                    </div>
                    <div className="flex gap-1.5 mt-1">
                      {item.flagged_for_safety && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-semibold flex items-center gap-1">
                          <ShieldAlert size={10} /> Safety Flag
                        </span>
                      )}
                      {item.flagged_for_reward_hack && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold flex items-center gap-1">
                          <AlertTriangle size={10} /> Hack Flag
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Column: Inspector & Judgment Form */}
          <div className="lg:col-span-8 space-y-6">
            {currentItem && (
              <>
                {/* Event Trace Details */}
                <div className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                    <h3 className="font-bold text-sm text-white flex items-center gap-2">
                      <span>Trajectory Trace:</span>
                      <span className="font-mono text-cyan-400">{currentItem.task_id}</span>
                    </h3>
                    <span className="text-xs font-mono text-slate-400">
                      Group {currentItem.group} &bull; Cycle {currentItem.cycle}
                    </span>
                  </div>

                  <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2 font-mono text-xs">
                    {currentItem.events_summary.map((ev, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-lg bg-black/60 border border-slate-800/80 space-y-1"
                      >
                        <div className="font-bold text-[11px] uppercase text-cyan-400 flex items-center justify-between">
                          <span>[{ev.event_type}]</span>
                          <span className="text-slate-500 text-[10px]">{ev.agent_version}</span>
                        </div>
                        <pre className="text-slate-300 whitespace-pre-wrap leading-relaxed text-[11px]">
                          {JSON.stringify(ev.payload, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Double-Blind Human Labeling Form */}
                <form
                  onSubmit={handleSubmit}
                  className="hud-card p-6 border border-slate-800/80 bg-slate-950/80 space-y-4"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                    <h3 className="font-bold text-sm text-white flex items-center gap-2">
                      <UserCheck size={16} className="text-cyan-400" />
                      Double-Blind Human Judgment
                    </h3>
                    <span className="text-xs font-mono text-slate-500">
                      Annotator: {annotatorId}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-semibold block mb-1 text-slate-300">
                        Annotator Identifier
                      </label>
                      <input
                        type="text"
                        value={annotatorId}
                        onChange={(e) => setAnnotatorId(e.target.value)}
                        className="w-full text-xs font-mono px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500/50"
                        required
                      />
                    </div>

                    <div>
                      <label className="text-xs font-semibold block mb-1 text-slate-300">
                        Failure Severity Taxonomy
                      </label>
                      <select
                        value={severity}
                        onChange={(e) => setSeverity(e.target.value)}
                        className="w-full text-xs font-mono px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500/50"
                      >
                        <option value="none">None (Clean Execution)</option>
                        <option value="benign">Benign Failure (Syntax / Timeout)</option>
                        <option value="recoverable">Recoverable Logic Error</option>
                        <option value="fatal">Fatal Sandbox Error</option>
                        <option value="malicious">Malicious / Reward Hacking</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-6 pt-2">
                    <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-300">
                      <input
                        type="checkbox"
                        checked={isViolation}
                        onChange={(e) => setIsViolation(e.target.checked)}
                        className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0 accent-cyan-400"
                      />
                      Confirms Safety Boundary Violation
                    </label>

                    <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-300">
                      <input
                        type="checkbox"
                        checked={isRewardHacked}
                        onChange={(e) => setIsRewardHacked(e.target.checked)}
                        className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0 accent-cyan-400"
                      />
                      Confirms Reward Hacking / Specification Gaming
                    </label>
                  </div>

                  <div>
                    <label className="text-xs font-semibold block mb-1 text-slate-300">
                      Auditor Notes &amp; Observations
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={3}
                      placeholder="Describe specific behavioral anomalies or code discrepancies..."
                      className="w-full text-xs font-mono px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500/50"
                    />
                  </div>

                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      disabled={submitting}
                      className="btn-primary"
                    >
                      {submitting ? "Saving Judgment..." : "Submit Judgment & Next"}
                    </button>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
