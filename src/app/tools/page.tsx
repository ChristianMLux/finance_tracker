"use client";

"use client";

import { useRouter } from "next/navigation";
import { Tool } from "@/lib/api";
import { formatTitle } from "@/lib/utils";
import { useTools } from "@/hooks/useTools";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";

export default function ToolsPage() {
  const { tools } = useTools();
  const router = useRouter();

  // Helper to split tools
  const [agents, interactiveTools] = tools.reduce(
    (acc, tool) => {
      let isInteractive = false;
      try {
        if (tool.json_schema && typeof tool.json_schema === 'string' && tool.json_schema.trim() !== "") {
            const schema = JSON.parse(tool.json_schema);
            if (schema.properties && Object.keys(schema.properties).length > 0) {
                isInteractive = true;
            }
        } else if (typeof tool.json_schema === 'object' && tool.json_schema !== null) {
             const schema = tool.json_schema as { properties?: unknown };
             if (schema.properties && Object.keys(schema.properties as object).length > 0) {
                isInteractive = true;
            }
        }
      } catch (e) {
          console.warn(`Failed to parse schema for ${tool.name}`, e);
      }
      
      if (isInteractive) acc[1].push(tool);
      else acc[0].push(tool);
      
      return acc;
    },
    [[], []] as [Tool[], Tool[]]
  );


  const handleToolSelect = (tool: Tool) => {
    // Check if tool is 'interactive' (has schema properties) or 'agent' (no inputs)
    let isAgent = true;
    try {
        if (tool.json_schema && tool.json_schema.trim() !== "") {
            const schema = JSON.parse(tool.json_schema);
            if (schema.properties && Object.keys(schema.properties).length > 0) {
                isAgent = false;
            }
        }
    } catch {
        console.warn("Failed to parse schema for tool check", tool.name);
    }

    if (isAgent) {
        // Redirect to chat with a triggering message
        router.push(`/chat?message=${encodeURIComponent("Run " + (tool.title || tool.name))}`);
    } else {
        router.push(`/tools/${tool.name}`);
    }
  };


  return (
    <div className="max-w-7xl space-y-8 animate-fade-in pb-20">
      <div>
        <h1 className="text-3xl font-display font-bold tracking-tight text-foreground">
          Tools & Agents
        </h1>
        <p className="text-muted-foreground mt-1">
          Select a specialized tool to run directly or start a focused task.
        </p>
      </div>

      {/* Specialized Agents Section */}
      {agents.length > 0 && (
        <section>
          <div className="mb-6 border-b border-border/40 pb-4">
             <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
                Specialized Agents
             </h2>
             <p className="text-sm text-muted-foreground mt-1">
                AI agents that run automated tasks or retrieve information directly in the chat.
             </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((tool) => (
              <ToolCard key={tool.id} tool={tool} onClick={() => handleToolSelect(tool)} type="agent" />
            ))}
          </div>
        </section>
      )}

      {/* Interactive Tools Section */}
      {interactiveTools.length > 0 && (
        <section>
          <div className="mb-6 border-b border-border/40 pb-4 mt-8">
             <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
                Interactive Tools
             </h2>
             <p className="text-sm text-muted-foreground mt-1">
                Apps and calculators with dedicated interfaces for complex inputs.
             </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {interactiveTools.map((tool) => (
              <ToolCard key={tool.id} tool={tool} onClick={() => handleToolSelect(tool)} type="tool"/>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function ToolCard({ tool, onClick, type }: { tool: Tool, onClick: () => void, type: 'agent'|'tool' }) {
    return (
        <Card 
            onClick={onClick}
            className={`
                group relative hover:shadow-md transition-all cursor-pointer flex flex-col h-full
                ${tool.status === 'saved' ? 'border-primary/50 bg-primary/5' : 'hover:border-primary/50'}
            `}
          >
            <CardHeader className="pb-3 space-y-0">
                <div className="flex justify-between items-start gap-4">
                     <CardTitle className="text-lg font-semibold tracking-tight leading-tight">
                      {tool.title || formatTitle(tool.name)}
                    </CardTitle>
                    {tool.status === 'saved' && (
                        <span className="inline-flex items-center rounded-full border border-transparent bg-primary px-2 py-0.5 text-[10px] font-semibold text-primary-foreground shadow transition-colors shrink-0">
                            Saved
                        </span>
                    )}
                </div>
            </CardHeader>
           
            <CardContent className="flex-1 flex flex-col">
                <p className="text-muted-foreground text-sm flex-1 mb-4 line-clamp-3">
                  {tool.description}
                </p>
                
                <div className="flex items-center justify-between mt-auto pt-4 border-t border-border/50">
                     <div className="text-xs text-muted-foreground font-mono bg-secondary/50 p-1.5 rounded truncate max-w-[150px]">
                        {tool.name}
                     </div>
                     <div className="text-primary opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-xs font-semibold uppercase tracking-wider">
                         {type === 'agent' ? 'Chat' : 'Open'} 
                         {type === 'agent' 
                            ? <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4c0-1.1.9-2 2-2h8a2 2 0 0 1 2 2v5Z"/><path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1"/></svg>
                            : <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                         }
                     </div>
                </div>
            </CardContent>
          </Card>
    )
}

