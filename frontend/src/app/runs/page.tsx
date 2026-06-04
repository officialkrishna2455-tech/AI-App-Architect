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
      <h1 className="text-3xl font-bold mb-6">Compilation Runs</h1>
      
      {loading && <div className="text-accent-blue animate-pulse">Loading runs...</div>}
      
      {!loading && data && (
        <div className="glass rounded-xl border border-white/10 overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-navy-900/80 border-b border-white/10 text-slate-400">
              <tr>
                <th className="p-4">Time</th>
                <th className="p-4">Requirements</th>
                <th className="p-4">Status</th>
                <th className="p-4">Latency</th>
                <th className="p-4">Validation</th>
                <th className="p-4">Entities</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {data.runs.map(run => (
                <tr key={run.run_id} className="hover:bg-white/5 transition-colors">
                  <td className="p-4 whitespace-nowrap">{formatDate(run.created_at)}</td>
                  <td className="p-4 max-w-xs truncate">{run.requirements_preview}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 bg-success/20 text-success rounded text-xs font-medium">
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
