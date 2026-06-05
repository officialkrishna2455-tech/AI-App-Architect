"use client";

import { useEffect, useState } from "react";
import { CompilerAPI } from "@/lib/api";
import { EvalRunResponse } from "@/types/compiler";

export default function EvalPage() {
  const [evalData, setEvalData] = useState<EvalRunResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    CompilerAPI.getEvaluationReport()
      .then(res => setEvalData(res))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl text-slate-400">Loading evaluation report...</div>
      </div>
    );
  }

  if (!evalData || evalData.total_prompts === 0) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <h1 className="text-3xl font-bold mb-6 text-slate-900">Evaluation Dashboard</h1>
        <div className="p-8 text-center text-slate-500 glass rounded-xl">
          No evaluation data found. Run the evaluation suite to generate metrics.
        </div>
      </div>
    );
  }

  const metrics = evalData.aggregate_metrics;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8 border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
          Evaluation Dashboard
        </h1>
        <p className="text-sm text-slate-500 mt-1">Aggregated metrics from the 20-prompt test suite.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <div className="bg-white border border-slate-200 p-6 rounded-md shadow-sm">
          <div className="text-slate-500 text-xs font-bold mb-2 uppercase tracking-wider">Total Runs</div>
          <div className="text-3xl font-bold text-slate-900">{metrics.total_runs}</div>
        </div>
        <div className="bg-white border border-slate-200 p-6 rounded-md shadow-sm">
          <div className="text-slate-500 text-xs font-bold mb-2 uppercase tracking-wider">Success Rate</div>
          <div className="text-3xl font-bold text-emerald-600">
            {(metrics.success_rate * 100).toFixed(1)}%
          </div>
        </div>
        <div className="bg-white border border-slate-200 p-6 rounded-md shadow-sm">
          <div className="text-slate-500 text-xs font-bold mb-2 uppercase tracking-wider">Validation Pass Rate</div>
          <div className="text-3xl font-bold text-red-600">
            {(metrics.average_validation_pass_rate * 100).toFixed(1)}%
          </div>
        </div>
        <div className="bg-white border border-slate-200 p-6 rounded-md shadow-sm">
          <div className="text-slate-500 text-xs font-bold mb-2 uppercase tracking-wider">Simulation Pass Rate</div>
          <div className="text-3xl font-bold text-purple-600">
            {(metrics.average_simulation_pass_rate * 100).toFixed(1)}%
          </div>
        </div>
        <div className="bg-white border border-slate-200 p-6 rounded-md shadow-sm">
          <div className="text-slate-500 text-xs font-bold mb-2 uppercase tracking-wider">Avg Latency (P50)</div>
          <div className="text-3xl font-bold text-orange-600">{metrics.p50_latency_ms} ms</div>
        </div>
        <div className="bg-white border border-slate-200 p-6 rounded-md shadow-sm">
          <div className="text-slate-500 text-xs font-bold mb-2 uppercase tracking-wider">Avg Repair Count</div>
          <div className="text-3xl font-bold text-orange-500">{metrics.average_repair_rate.toFixed(2)}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        <div className="lg:col-span-1 bg-white border border-slate-200 p-6 rounded-md shadow-sm">
          <h2 className="text-sm font-bold text-slate-800 mb-4 uppercase tracking-wider">Failure Categories</h2>
          {Object.keys(metrics.failure_categories || {}).length === 0 ? (
            <div className="text-slate-500 py-4 text-sm">No failures recorded.</div>
          ) : (
            <ul className="space-y-2">
              {Object.entries(metrics.failure_categories || {}).map(([cat, count]) => (
                <li key={cat} className="flex justify-between items-center bg-slate-50 p-2.5 rounded border border-slate-100">
                  <span className="text-slate-700 text-sm font-medium">{cat}</span>
                  <span className="bg-red-100 text-red-600 px-2 py-0.5 rounded text-xs font-bold border border-red-200">{count}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <div className="lg:col-span-2 bg-white border border-slate-200 p-0 rounded-md shadow-sm overflow-hidden">
          <div className="bg-slate-50 border-b border-slate-200 px-6 py-4">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Detailed Results</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-600 text-sm font-semibold bg-slate-50">
                  <th className="py-3 px-4 rounded-tl-lg">Prompt ID</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Validation</th>
                  <th className="py-3 px-4">Simulation</th>
                  <th className="py-3 px-4">Repairs</th>
                  <th className="py-3 px-4 rounded-tr-lg">Latency</th>
                </tr>
              </thead>
              <tbody>
                {evalData.results.map((r, index) => (
                  <tr key={`${r.prompt_id}-${index}`} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-mono text-sm text-slate-800">{r.prompt_id}</td>
                    <td className="py-3 px-4 text-slate-600 text-sm">{r.prompt_type}</td>
                    <td className="py-3 px-4">
                      {r.success ? (
                        <span className="text-success text-sm bg-success/10 px-2 py-1 rounded font-medium">Pass</span>
                      ) : (
                        <span className="text-red-600 text-sm bg-red-100 px-2 py-1 rounded font-medium border border-red-200">Fail</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-sm font-medium text-slate-700">{(r.validation_pass_rate * 100).toFixed(0)}%</td>
                    <td className="py-3 px-4 text-sm font-medium text-slate-700">{(r.simulation_pass_rate * 100).toFixed(0)}%</td>
                    <td className="py-3 px-4 text-sm text-slate-700">{r.repair_count}</td>
                    <td className="py-3 px-4 text-sm text-slate-500">{r.latency_ms}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
