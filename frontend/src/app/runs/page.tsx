"use client";

import { useEffect, useState } from "react";
import { CompilerAPI } from "@/lib/api";
import { RunListResponse } from "@/types/compiler";
import { formatDuration, formatDate } from "@/lib/utils";

export default function RunsPage() {
  const [data, setData] = useState<RunListResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    CompilerAPI.getRuns().then(res => {
      setData(res);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-6 border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
          Compilation Runs
        </h1>
      </div>
      
      {loading && <div className="text-slate-500 animate-pulse text-sm font-medium">Loading runs...</div>}
      
      {!loading && data && (
        <div className="bg-white rounded-md border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold text-xs uppercase tracking-wider">
              <tr>
                <th className="p-4 font-semibold">Time</th>
                <th className="p-4 font-semibold">Requirements</th>
                <th className="p-4 font-semibold">Status</th>
                <th className="p-4 font-semibold">Latency</th>
                <th className="p-4 font-semibold">Validation</th>
                <th className="p-4 font-semibold">Entities</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {data.runs.map(run => (
                <tr key={run.run_id} className="hover:bg-slate-50 transition-colors">
                  <td className="p-4 whitespace-nowrap text-slate-500 text-xs font-mono">{formatDate(run.created_at)}</td>
                  <td className="p-4 max-w-xs truncate font-medium text-slate-800">{run.requirements_preview}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold border ${run.status === 'COMPLETED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-100 text-slate-700 border-slate-200'}`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="p-4">{formatDuration(run.total_latency_ms)}</td>
                  <td className="p-4">{(run.validation_pass_rate * 100).toFixed(0)}%</td>
                  <td className="p-4">{run.entity_count}</td>
                </tr>
              ))}
              {data.runs.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-500">No runs found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
