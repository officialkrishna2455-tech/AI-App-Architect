"use client";

import { SchemaOutput } from "@/types/compiler";
import { useState } from "react";
import { cn } from "@/lib/utils";

export default function SchemaViewer({ schemas }: { schemas: SchemaOutput }) {
  const [activeTab, setActiveTab] = useState<keyof SchemaOutput>("ui_schema");
  
  if (!schemas) return <div>No schemas generated</div>;
  
  const tabs: { key: keyof SchemaOutput; label: string }[] = [
    { key: "ui_schema", label: "UI Schema" },
    { key: "api_schema", label: "API Schema" },
    { key: "db_schema", label: "Database Schema" },
    { key: "auth_schema", label: "Auth Schema" },
    { key: "business_logic_schema", label: "Business Logic" },
  ];

  return (
    <div className="glass rounded-xl overflow-hidden border border-slate-200 flex flex-col h-[500px]">
      <div className="flex border-b border-slate-200 bg-slate-100 overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              "px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors",
              activeTab === tab.key
                ? "text-accent-red border-b-2 border-accent-red bg-white"
                : "text-slate-500 hover:text-slate-900 hover:bg-white/50"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="flex-1 p-4 overflow-auto bg-slate-50">
        <pre className="text-xs text-slate-700 font-mono">
          {JSON.stringify(schemas[activeTab], null, 2)}
        </pre>
      </div>
    </div>
  );
}
