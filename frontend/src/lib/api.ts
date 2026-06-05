import { 
  CompileMetrics, 
  CompileResponse, 
  EvalRunResponse, 
  MetricsResponse, 
  RunListResponse 
} from "@/types/compiler";

const API_BASE = "http://localhost:8000/api/v1";

export class CompilerAPI {
  
  static async compile(requirements: string, sync: boolean = true): Promise<CompileResponse> {
    const res = await fetch(`${API_BASE}/compile?sync=${sync}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        requirements,
        options: {
          target_stack: "nextjs-fastapi",
          include_simulation: true,
          include_knowledge_graph: true,
          max_repair_iterations: 3
        }
      })
    });
    
    if (!res.ok) {
      throw new Error(`Compile failed: ${res.statusText}`);
    }
    
    return res.json();
  }
  
  static async getRuns(page = 1, pageSize = 20): Promise<RunListResponse> {
    const res = await fetch(`${API_BASE}/runs?page=${page}&page_size=${pageSize}`);
    if (!res.ok) throw new Error("Failed to fetch runs");
    return res.json();
  }
  
  static async getRun(id: string): Promise<CompileResponse> {
    const res = await fetch(`${API_BASE}/runs/${id}`);
    if (!res.ok) throw new Error("Failed to fetch run details");
    return res.json();
  }
  
  static async getMetrics(): Promise<MetricsResponse> {
    const res = await fetch(`${API_BASE}/metrics`);
    if (!res.ok) throw new Error("Failed to fetch metrics");
    return res.json();
  }

  static async getEvaluationReport(): Promise<EvalRunResponse> {
    const res = await fetch(`${API_BASE}/evaluation/report`);
    if (!res.ok) throw new Error("Failed to fetch evaluation report");
    return res.json();
  }
}
