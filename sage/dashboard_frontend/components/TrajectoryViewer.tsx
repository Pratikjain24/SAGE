"use client";

import React, { useState } from "react";
import { TrajectoryEvent } from "@/lib/api";
import { Terminal, Shield, CheckCircle2, Wrench, AlertOctagon, GitCommit } from "lucide-react";

interface TrajectoryViewerProps {
  events: TrajectoryEvent[];
}

export const TrajectoryViewer: React.FC<TrajectoryViewerProps> = ({ events }) => {
  const [selectedTask, setSelectedTask] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");

  const taskIds = Array.from(new Set(events.map((e) => e.task_id)));

  const filtered = events.filter((e) => {
    if (selectedTask !== "all" && e.task_id !== selectedTask) return false;
    if (filterType !== "all" && e.event_type !== filterType) return false;
    return true;
  });

  const getEventIcon = (type: string) => {
    switch (type) {
      case "tool_call":
        return <Wrench size={15} style={{ color: "var(--accent)" }} />;
      case "observation":
        return <Terminal size={15} style={{ color: "var(--safe)" }} />;
      case "safety_check":
        return <Shield size={15} style={{ color: "var(--drift)" }} />;
      case "task_start":
        return <GitCommit size={15} className="text-purple-400" />;
      case "task_end":
        return <CheckCircle2 size={15} style={{ color: "var(--safe)" }} />;
      case "evolution_proposal":
      case "evolution_decision":
        return <AlertOctagon size={15} style={{ color: "var(--warn)" }} />;
      default:
        return <Terminal size={15} style={{ color: "var(--text-muted)" }} />;
    }
  };

  return (
    <div className="data-panel p-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 gap-3" style={{ borderBottom: "1px solid var(--border-subtle)" }}>
        <div>
          <p className="section-label mb-0.5">Execution Log</p>
          <h3 className="text-base font-bold tracking-tight" style={{ color: "var(--text-primary)" }}>
            Trajectory Event Timeline &amp; Tool Calls
          </h3>
          <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
            Append-only JSONL stream showing agent tool executions, sandbox observations, and safety monitor checks.
          </p>
        </div>

        <div className="flex gap-2">
          {/* Task filter */}
          <select
            value={selectedTask}
            onChange={(e) => setSelectedTask(e.target.value)}
            className="text-xs font-mono rounded-lg px-2.5 py-1.5 focus:outline-none"
            style={{
              backgroundColor: "var(--surface-3)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-default)",
            }}
          >
            <option value="all">All Tasks</option>
            {taskIds.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>

          {/* Type filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="text-xs rounded-lg px-2.5 py-1.5 focus:outline-none"
            style={{
              backgroundColor: "var(--surface-3)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-default)",
            }}
          >
            <option value="all">All Event Types</option>
            <option value="tool_call">Tool Calls</option>
            <option value="observation">Observations</option>
            <option value="safety_check">Safety Checks</option>
            <option value="evolution_proposal">Evolution Proposals</option>
            <option value="task_end">Task Ends</option>
          </select>
        </div>
      </div>

      <div className="mt-4 space-y-3 max-h-[600px] overflow-y-auto pr-1">
        {filtered.length === 0 ? (
          <div className="text-center py-10 text-xs" style={{ color: "var(--text-muted)" }}>
            No trajectory events matching current filters.
          </div>
        ) : (
          filtered.map((ev, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl transition-colors"
              style={{
                backgroundColor: "var(--surface-3)",
                border: "1px solid var(--border-default)",
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div
                    className="p-1.5 rounded-md"
                    style={{
                      backgroundColor: "var(--surface-2)",
                      border: "1px solid var(--border-subtle)",
                    }}
                  >
                    {getEventIcon(ev.event_type)}
                  </div>
                  <span className="font-mono text-xs font-bold uppercase tracking-wider" style={{ color: "var(--text-primary)" }}>
                    {ev.event_type}
                  </span>
                  <span
                    className="text-[10px] px-2 py-0.5 rounded font-mono"
                    style={{
                      backgroundColor: "rgba(255,255,255,0.06)",
                      color: "var(--text-secondary)",
                    }}
                  >
                    {ev.agent_version}
                  </span>
                  <span
                    className="text-[10px] px-2 py-0.5 rounded font-mono font-bold"
                    style={{
                      backgroundColor: "rgba(45,125,210,0.15)",
                      color: "var(--accent)",
                      border: "1px solid rgba(45,125,210,0.3)",
                    }}
                  >
                    {ev.group}
                  </span>
                </div>
                <div className="text-[11px] font-mono" style={{ color: "var(--text-muted)" }}>
                  {new Date(ev.ts).toLocaleTimeString()} · task: {ev.task_id}
                </div>
              </div>

              {/* Payload content */}
              <div
                className="mt-2 p-3 rounded-lg font-mono text-xs overflow-x-auto"
                style={{
                  backgroundColor: "rgba(0,0,0,0.5)",
                  border: "1px solid var(--border-subtle)",
                  color: "var(--text-secondary)",
                }}
              >
                {ev.event_type === "tool_call" && (
                  <div>
                    <span className="font-bold" style={{ color: "var(--accent)" }}>$ {ev.payload.tool_name}</span>{" "}
                    <span style={{ color: "var(--text-muted)" }}>{JSON.stringify(ev.payload.arguments)}</span>
                  </div>
                )}
                {ev.event_type === "observation" && (
                  <div>
                    <span style={{ color: "var(--text-muted)" }}>// Output (exit_code: {ev.payload.exit_code}):</span>
                    <pre className="mt-1 whitespace-pre-wrap" style={{ color: "var(--safe)" }}>
                      {ev.payload.stdout || ev.payload.stderr || "(no output)"}
                    </pre>
                  </div>
                )}
                {ev.event_type === "safety_check" && (
                  <div className="font-semibold" style={{ color: ev.payload.passed ? "var(--safe)" : "var(--drift)" }}>
                    [RULE: {ev.payload.rule_name}] Passed: {String(ev.payload.passed)} — {ev.payload.violation_details || "Allowed"}
                  </div>
                )}
                {ev.event_type === "task_end" && (
                  <div className="flex gap-4">
                    <span className="font-bold" style={{ color: ev.payload.success ? "var(--safe)" : "var(--drift)" }}>
                      Status: {ev.payload.status}
                    </span>
                    <span>GT Score: {ev.payload.ground_truth_score}</span>
                    <span style={{ color: "var(--warn)" }}>Proxy Gap: +{ev.payload.proxy_gap}</span>
                  </div>
                )}
                {!["tool_call", "observation", "safety_check", "task_end"].includes(ev.event_type) && (
                  <pre className="whitespace-pre-wrap">{JSON.stringify(ev.payload, null, 2)}</pre>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
