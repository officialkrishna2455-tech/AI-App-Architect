"use client";

import { useEffect, useState } from "react";
import { CompilerAPI } from "@/lib/api";
import { MetricsResponse } from "@/types/compiler";

export default function EvalPage() {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);

  useEffect(() => {
    CompilerAPI.getMetrics().then(res => setMetrics(res)).catch(() => {});
  }, []);

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <h1 className="text-3xl font-bold mb-6">Evaluation Metrics</h1>
      
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass p-6 rounded-xl border border-white/10">
            <div className="text-slate-400 mb-2">Total Prompt Runs</div>
            <div className="text-4xl font-bold text-white">{metrics.total_runs}</div>
          </div>
          <div className="glass p-6 rounded-xl border border-white/10">
            <div className="text-slate-400 mb-2">Success Rate</div>
            <div className="text-4xl font-bold text-success">
              {(metrics.success_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="glass p-6 rounded-xl border border-white/10">
            <div className="text-slate-400 mb-2">Avg Validation Pass Rate</div>
            <div className="text-4xl font-bold text-accent-cyan">
              {(metrics.average_validation_pass_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="glass p-6 rounded-xl border border-white/10">
            <div className="text-slate-400 mb-2">P50 Latency</div>
            <div className="text-4xl font-bold text-white">{metrics.p50_latency_ms}ms</div>
          </div>
          <div className="glass p-6 rounded-xl border border-white/10">
            <div className="text-slate-400 mb-2">P95 Latency</div>
            <div className="text-4xl font-bold text-warning">{metrics.p95_latency_ms}ms</div>
          </div>
          <div className="glass p-6 rounded-xl border border-white/10">
            <div className="text-slate-400 mb-2">Avg Auto-Repairs / Run</div>
            <div className="text-4xl font-bold text-white">{metrics.average_repair_rate.toFixed(1)}</div>
          </div>
        </div>
      )}
    </div>
  );
}
