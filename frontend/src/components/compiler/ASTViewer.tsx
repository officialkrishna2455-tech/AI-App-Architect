"use client";

import { RequirementAST } from "@/types/compiler";
import { CircleStackIcon, KeyIcon, UserGroupIcon, SparklesIcon } from "@heroicons/react/24/outline";

export default function ASTViewer({ ast }: { ast: RequirementAST }) {
  if (!ast || !ast.entities) return <div>No AST Data</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Entities */}
        <div className="glass p-4 rounded-xl border-t-4 border-t-accent-red">
          <div className="flex items-center gap-2 mb-4 text-slate-900">
            <CircleStackIcon className="w-5 h-5 text-accent-red" />
            <h3 className="font-bold text-lg">Entities ({ast.entities.length})</h3>
          </div>
          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2">
            {ast.entities.map(e => (
              <div key={e.name} className="p-2 bg-slate-50 rounded-lg text-sm border border-slate-200">
                <span className="font-semibold text-slate-900">{e.name}</span>
                <div className="text-xs text-slate-500 mt-1">
                  {e.fields.length} fields • {e.relations.length} relations
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Features */}
        <div className="glass p-4 rounded-xl border-t-4 border-t-emerald-500">
          <div className="flex items-center gap-2 mb-4 text-slate-900">
            <SparklesIcon className="w-5 h-5 text-emerald-500" />
            <h3 className="font-bold text-lg">Features ({ast.features.length})</h3>
          </div>
          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2">
            {ast.features.map(f => (
              <div key={f.name} className="p-2 bg-slate-50 rounded-lg text-sm border border-slate-200">
                <span className="font-semibold text-emerald-600">{f.name}</span>
                <div className="text-xs text-slate-500 mt-1">
                  Type: {f.feature_type}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Roles */}
        <div className="glass p-4 rounded-xl border-t-4 border-t-purple-500">
          <div className="flex items-center gap-2 mb-4 text-slate-900">
            <UserGroupIcon className="w-5 h-5 text-purple-500" />
            <h3 className="font-bold text-lg">Roles ({ast.roles?.length || 0})</h3>
          </div>
          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2">
            {ast.roles?.map(r => (
              <div key={r.name} className="p-2 bg-slate-50 rounded-lg text-sm border border-slate-200">
                <span className="font-semibold text-purple-600">{r.name}</span>
                <div className="text-xs text-slate-500 mt-1">
                  {r.permissions.length} permissions
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* JSON Raw */}
        <div className="glass p-4 rounded-xl border-t-4 border-t-slate-500 flex flex-col">
          <div className="flex items-center gap-2 mb-4 text-slate-900">
            <KeyIcon className="w-5 h-5 text-slate-500" />
            <h3 className="font-bold text-lg">Raw AST</h3>
          </div>
          <div className="flex-1 bg-slate-100 rounded-lg p-2 overflow-auto text-xs text-slate-700 font-mono border border-slate-200">
            <pre>{JSON.stringify({ metadata: ast.metadata }, null, 2)}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
