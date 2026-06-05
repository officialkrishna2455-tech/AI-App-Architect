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
    <div className="container mx-auto px-4 py-12 max-w-5xl">
      {/* Header */}
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 flex items-center justify-center gap-3 mb-4">
          <CodeBracketIcon className="w-10 h-10 text-red-600" />
          AI Application Architect
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          A compiler-like system for transforming software requirements into validated application blueprints.
        </p>
      </div>

      {/* Input Section - Centralized */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-sm p-6 mb-12">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-600" />
          Software Requirements
        </label>
        <textarea
          className="w-full bg-slate-50 border border-slate-200 rounded p-4 text-slate-800 text-base font-mono placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-600 focus:border-red-600 resize-y min-h-[160px]"
          placeholder="Describe your architecture... e.g., Build a CRM with login, contacts, dashboard, role-based access, premium plans, payments, and analytics."
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
        />
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleCompile}
            disabled={isCompiling || !requirements.trim()}
            className="bg-slate-900 hover:bg-slate-800 disabled:bg-slate-100 disabled:text-slate-400 disabled:border-slate-200 text-white font-semibold py-3 px-8 rounded flex items-center gap-2 transition-colors shadow-sm text-sm"
          >
            {isCompiling ? (
              <>
                <ArrowPathIcon className="w-5 h-5 animate-spin" />
                Compiling Pipeline...
              </>
            ) : (
              <>
                <PlayIcon className="w-5 h-5" />
                Generate Blueprint
              </>
            )}
          </button>
        </div>
      </div>

      {/* Compiler Pipeline Indicator (Visible during and after compilation) */}
      {(isCompiling || result) && (
        <div className="mb-12">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 text-center">Compiler Pipeline Status</h3>
          <div className="flex flex-wrap items-center justify-center gap-2 md:gap-4 text-xs md:text-sm font-medium text-slate-500 bg-white border border-slate-200 p-4 rounded-lg shadow-sm">
            <div className={`flex items-center gap-2 ${result ? 'text-emerald-600' : isCompiling ? 'text-red-600 animate-pulse' : ''}`}>
              <span className="flex items-center justify-center w-6 h-6 rounded-full border border-current bg-white">1</span>
              <span>AST Generated</span>
            </div>
            <div className="w-4 md:w-8 h-px bg-slate-300" />
            <div className={`flex items-center gap-2 ${result ? 'text-emerald-600' : (isCompiling && result === null) ? 'text-red-600 opacity-50' : ''}`}>
              <span className="flex items-center justify-center w-6 h-6 rounded-full border border-current bg-white">2</span>
              <span>Schemas Generated</span>
            </div>
            <div className="w-4 md:w-8 h-px bg-slate-300" />
            <div className={`flex items-center gap-2 ${result ? 'text-emerald-600' : ''}`}>
              <span className="flex items-center justify-center w-6 h-6 rounded-full border border-current bg-white">3</span>
              <span>Validation Executed</span>
            </div>
            <div className="w-4 md:w-8 h-px bg-slate-300" />
            <div className={`flex items-center gap-2 ${result ? 'text-emerald-600' : ''}`}>
              <span className="flex items-center justify-center w-6 h-6 rounded-full border border-current bg-white">4</span>
              <span>Repairs Applied</span>
            </div>
            <div className="w-4 md:w-8 h-px bg-slate-300" />
            <div className={`flex items-center gap-2 ${result ? 'text-emerald-600' : ''}`}>
              <span className="flex items-center justify-center w-6 h-6 rounded-full border border-current bg-white">5</span>
              <span>Simulations Run</span>
            </div>
          </div>
        </div>
      )}

      {/* Results Section - Sequential downward expansion */}
      {result && !isCompiling && (
        <div className="space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
          <section className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
            <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex items-center gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded bg-slate-800 text-white font-mono text-xs font-bold shadow-inner">1</span>
              <h2 className="text-base font-bold text-slate-800 uppercase tracking-wider">Requirement AST & Knowledge Graph</h2>
            </div>
            <div className="p-0">
              <ASTViewer ast={result.ast} />
            </div>
          </section>

          <section className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
            <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex items-center gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded bg-slate-800 text-white font-mono text-xs font-bold shadow-inner">2</span>
              <h2 className="text-base font-bold text-slate-800 uppercase tracking-wider">Generated Application Schemas</h2>
            </div>
            <div className="p-0">
              <SchemaViewer schemas={result.schemas} />
            </div>
          </section>

          <section className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
            <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex items-center gap-3">
              <span className="flex items-center justify-center px-2 py-1 rounded bg-slate-800 text-white font-mono text-xs font-bold shadow-inner tracking-widest">3-5</span>
              <h2 className="text-base font-bold text-slate-800 uppercase tracking-wider">Validation, Repairs & Simulation Metrics</h2>
            </div>
            <div className="p-0">
              <MetricsViewer data={result} />
            </div>
          </section>
        </div>
      )}
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
