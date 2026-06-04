"use client";

import { useState } from "react";
import { CompilerAPI } from "@/lib/api";
import { CompileResponse } from "@/types/compiler";
import ASTViewer from "@/components/compiler/ASTViewer";
import SchemaViewer from "@/components/compiler/SchemaViewer";
import MetricsViewer from "@/components/compiler/MetricsViewer";
import { PlayIcon, ArrowPathIcon } from "@heroicons/react/24/solid";

export default function Home() {
  const [requirements, setRequirements] = useState(
    "Build a CRM with login, contacts, dashboard, role-based access, premium plans, payments, and analytics."
  );
  const [isCompiling, setIsCompiling] = useState(false);
  const [result, setResult] = useState<CompileResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCompile = async () => {
    if (!requirements.trim()) return;
    
    setIsCompiling(true);
    setError(null);
    setResult(null);
    
    try {
      const res = await CompilerAPI.compile(requirements);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "An error occurred during compilation");
    } finally {
      setIsCompiling(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight mb-4 text-white">
          <span className="text-gradient">Requirement</span> Compiler
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          Convert natural language software requirements into executable, production-ready application blueprints in seconds.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Section */}
        <div className="lg:col-span-1 space-y-4">
          <div className="glass rounded-xl p-4 border border-white/10 flex flex-col h-full min-h-[400px]">
            <label className="text-sm font-semibold text-slate-300 mb-2 block">
              Natural Language Requirements
            </label>
            <textarea
              className="flex-1 w-full bg-navy-900/50 border border-white/10 rounded-lg p-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-accent-blue resize-none"
              placeholder="Describe your app..."
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
            />
            <button
              onClick={handleCompile}
              disabled={isCompiling || !requirements.trim()}
              className="mt-4 w-full bg-accent-blue hover:bg-accent-blue/90 disabled:bg-slate-700 disabled:text-slate-500 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all transform active:scale-[0.98]"
            >
              {isCompiling ? (
                <>
                  <ArrowPathIcon className="w-5 h-5 animate-spin" />
                  Compiling Pipeline...
                </>
              ) : (
                <>
                  <PlayIcon className="w-5 h-5" />
                  Compile Requirements
                </>
              )}
            </button>
            {error && (
              <div className="mt-4 p-3 bg-error/20 border border-error/50 rounded text-error text-sm">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2">
          {!result && !isCompiling && (
            <div className="glass rounded-xl h-full min-h-[400px] flex items-center justify-center border border-white/5 border-dashed">
              <div className="text-center text-slate-500">
                <CodeBracketIcon className="w-12 h-12 mx-auto mb-3 opacity-20" />
                <p>Compile requirements to view generated architecture</p>
              </div>
            </div>
          )}

          {isCompiling && (
            <div className="glass rounded-xl h-full min-h-[400px] flex flex-col items-center justify-center border border-white/10">
              <div className="w-16 h-16 border-4 border-accent-blue/30 border-t-accent-blue rounded-full animate-spin mb-4" />
              <p className="text-accent-cyan font-medium animate-pulse">Running Compiler Pipeline...</p>
              <div className="flex gap-2 mt-4 text-xs text-slate-500">
                <span>Lexing</span> → <span>Parsing</span> → <span>Validating</span> → <span>Simulating</span>
              </div>
            </div>
          )}

          {result && !isCompiling && (
            <div className="space-y-8">
              <section>
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-full bg-accent-blue/20 text-accent-blue flex items-center justify-center text-sm">1</span>
                  Requirement AST
                </h2>
                <ASTViewer ast={result.ast} />
              </section>

              <section>
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-full bg-accent-emerald/20 text-accent-emerald flex items-center justify-center text-sm">2</span>
                  Generated Schemas
                </h2>
                <SchemaViewer schemas={result.schemas} />
              </section>

              <section>
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-sm">3</span>
                  Validation & Simulation
                </h2>
                <MetricsViewer data={result} />
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function CodeBracketIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
    </svg>
  );
}
