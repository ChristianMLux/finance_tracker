"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api, Tool } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { formatTitle } from "@/lib/utils";

export default function ToolsPage() {
  const { token } = useAuth();
  const [tools, setTools] = useState<Tool[]>([]);
  const router = useRouter();

  useEffect(() => {
    if (token) {
      api.getTools(token).then(setTools).catch(console.error);
    }
  }, [token]);

  const handleToolSelect = (toolName: string, toolTitle: string) => {
    // Navigate to home with tool context
    // We pass tool content via query param or just simple message starter
    // The requirement says: start a new chat based on an existing tool
    // We can pass ?tool=name to auto-start or pre-fill
    const query = new URLSearchParams({ tool: toolName, title: toolTitle }).toString();
    router.push(`/?${query}`);
  };

  return (
    <div className="max-w-7xl space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-display font-bold tracking-tight text-foreground">
          Tools & Agents
        </h1>
        <p className="text-muted-foreground mt-1">
          Select a specialized tool to start a focused task.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tools.map((tool) => (
          <div 
            key={tool.id} 
            onClick={() => handleToolSelect(tool.name, tool.title || formatTitle(tool.name))}
            className="group relative rounded-xl border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all cursor-pointer p-6"
          >
            <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity">
               <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </div>
            <h3 className="text-xl font-semibold tracking-tight mb-2">
              {tool.title || formatTitle(tool.name)}
            </h3>
            <p className="text-muted-foreground text-sm">
              {tool.description}
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground font-mono bg-secondary/50 p-2 rounded w-fit">
              <span>{tool.name}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
