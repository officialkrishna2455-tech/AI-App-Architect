"use client";

import { CompileResponse } from "@/types/compiler";
import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from "@heroicons/react/24/solid";
import { formatDuration } from "@/lib/utils";

export default function MetricsViewer({ data }: { data: CompileResponse }) {
  if (!data) return null;

  const { metrics, validation_report, repair_report, simulation_report } = data;

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-xl flex flex-col justify-center items-center text-center">
          <div className="text-sm text-slate-500 mb-1">Total Time</div>
          <div className="text-2xl font-bold text-slate-900">{formatDuration(metrics.total_latency_ms)}</div>
        </div>
        <div className="glass p-4 rounded-xl flex flex-col justify-center items-center text-center">
          <div className="text-sm text-slate-500 mb-1">Validation Pass Rate</div>
          <div className="text-2xl font-bold text-accent-red">{(metrics.validation_pass_rate * 100).toFixed(0)}%</div>
        </div>
        <div className="glass p-4 rounded-xl flex flex-col justify-center items-center text-center">
          <div className="text-sm text-slate-500 mb-1">Auto-Repairs</div>
          <div className="text-2xl font-bold text-warning">{metrics.repair_count}</div>
        </div>
        <div className="glass p-4 rounded-xl flex flex-col justify-center items-center text-center">
          <div className="text-sm text-slate-500 mb-1">Simulation Pass Rate</div>
          <div className="text-2xl font-bold text-success">
            {metrics.simulation_pass_rate !== undefined ? `${(metrics.simulation_pass_rate * 100).toFixed(0)}%` : "N/A"}
          </div>
        </div>
      </div>

      {/* Validation Issues */}
      {validation_report?.issues && validation_report.issues.length > 0 && (
        <div className="glass rounded-xl border border-slate-200 p-4">
          <h3 className="font-bold text-lg mb-4 text-slate-900">Validation Issues & Repairs</h3>
          <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
            {validation_report.issues.map((issue, idx) => {
              const wasRepaired = repair_report?.repairs?.some(r => r.issue_rule_id === issue.rule_id);
              return (
                <div key={idx} className="bg-slate-50 rounded p-3 border border-slate-200 flex gap-3">
                  <div className="mt-0.5 shrink-0">
                    {wasRepaired ? (
                      <CheckCircleIcon className="w-5 h-5 text-success" />
                    ) : issue.severity === "error" ? (
                      <XCircleIcon className="w-5 h-5 text-error" />
                    ) : (
                      <ExclamationTriangleIcon className="w-5 h-5 text-warning" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium text-sm flex gap-2 items-center text-slate-800">
                      <span>[{issue.rule_id}]</span>
                      <span className="text-slate-500">{issue.layer} layer</span>
                    </div>
                    <div className="text-slate-600 text-sm mt-1">{issue.message}</div>
                    {wasRepaired && (
                      <div className="text-emerald-700 text-xs mt-2 font-medium bg-emerald-100 border border-emerald-200 inline-block px-2 py-1 rounded">
                        Automatically Repaired
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
