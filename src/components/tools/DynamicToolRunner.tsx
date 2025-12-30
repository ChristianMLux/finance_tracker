"use client"

import React, { useState, useEffect } from "react"
import { Play, Save, Loader2, AlertCircle, CheckCircle } from "lucide-react"
import { DynamicChart, ChartData } from "../DynamicChart"
import { Button } from "../ui/Button"
import { Card, CardContent } from "../ui/Card"
import { formatTitle } from "@/lib/utils"
import { useAuth } from "@/context/AuthContext"
import { ToolChatInterface } from "./ToolChatInterface"

interface Tool {
    name: string
    title?: string
    description?: string
    json_schema: string
    status?: string
}

interface DynamicToolRunnerProps {
    tool: Tool
    initialData?: Record<string, unknown>
}

// Simple AutoForm Component
interface SchemaProperty {
    type: string
    title?: string
    description?: string
    enum?: string[]
}

const AutoForm = ({ schema, value, onChange }: { schema: { properties?: Record<string, SchemaProperty>, required?: string[] }, value: Record<string, unknown>, onChange: (val: Record<string, unknown>) => void }) => {
    if (!schema || !schema.properties) return <div className="text-muted-foreground italic">No parameters required.</div>

    return (
        <div className="space-y-4">
            {Object.entries(schema.properties).map(([key, prop]) => {
                const fieldType = prop.type
                const isRequired = schema.required?.includes(key)
                const title = prop.title || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

                return (
                    <div key={key} className="space-y-1.5">
                        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            {title} {isRequired && <span className="text-destructive">*</span>}
                        </label>
                        {prop.description && <p className="text-[0.8rem] text-muted-foreground">{prop.description}</p>}
                        
                        {fieldType === "string" && !prop.enum && (
                            <input
                                type="text"
                                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                                value={(value[key] as string) || ""}
                                onChange={(e) => onChange({ ...value, [key]: e.target.value })}
                                placeholder={`Enter ${title}...`}
                            />
                        )}
                        
                        {(fieldType === "number" || fieldType === "integer") && (
                            <input
                                type="number"
                                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                                value={(value[key] as number) || ""}
                                onChange={(e) => onChange({ ...value, [key]: parseFloat(e.target.value) })}
                                placeholder="0.00"
                            />
                        )}

                        {prop.enum && (
                            <select
                                className="flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1"
                                value={(value[key] as string) || ""}
                                onChange={(e) => onChange({ ...value, [key]: e.target.value })}
                            >
                                <option value="" disabled>Select option...</option>
                                {prop.enum.map((opt: string) => (
                                    <option key={opt} value={opt} className="text-black">{opt}</option>
                                ))}
                            </select>
                        )}
                        
                        {fieldType === "boolean" && (
                            <div className="flex items-center space-x-2">
                                <input 
                                    type="checkbox" 
                                    checked={(value[key] as boolean) || false}
                                    onChange={(e) => onChange({ ...value, [key]: e.target.checked })}
                                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                />
                                <span className="text-sm text-muted-foreground">Yes</span>
                            </div>
                        )}
                    </div>
                )
            })}
        </div>
    )
}

export function DynamicToolRunner({ tool, initialData = {} }: DynamicToolRunnerProps) {
    // Parse Schema
    const schema = typeof tool.json_schema === "string" ? JSON.parse(tool.json_schema) : tool.json_schema
    const { token } = useAuth()

    const [formData, setFormData] = useState<Record<string, unknown>>(initialData)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<{ output: unknown; visualization?: unknown; logs?: string[] } | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [logs, setLogs] = useState<string[]>([])
    const [isSaved, setIsSaved] = useState(tool.status === "saved")
    const [saving, setSaving] = useState(false)

    // Update formData if initialData changes (e.g. from URL params)
    useEffect(() => {
        if (Object.keys(initialData).length > 0) {
            setFormData(prev => ({ ...prev, ...initialData }))
        }
    }, [initialData])

    const handleExecute = async () => {
        if (!token) {
            setError("You must be logged in to execute tools.")
            return
        }
        setLoading(true)
        setError(null)
        setResult(null)
        setLogs([])

        try {
            const res = await fetch(`http://localhost:8000/tools/${tool.name}/execute`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` 
                },
                body: JSON.stringify({ args: formData })
            })
            
            if (!res.ok) {
                const errData = await res.json().catch(() => ({ detail: "Unknown Error" }))
                throw new Error(errData.detail || "Execution failed")
            }

            const data = await res.json()
            setResult(data)
            if (data.logs) setLogs(data.logs)
        } catch (err) {
            setError((err as Error).message)
        } finally {
            setLoading(false)
        }
    }

    const handleSaveTool = async () => {
        if (!token) return
        setSaving(true)
        try {
             const res = await fetch(`http://localhost:8000/tools/${tool.name}/save`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` 
                } 
             })
             if (!res.ok) throw new Error("Failed to save tool")
             setIsSaved(true)
        } catch (err) {
             console.error(err)
             alert("Failed to save tool")
        } finally {
            setSaving(false)
        }
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 max-w-[1600px] mx-auto p-6">
            {/* Input Column */}
            <div className="space-y-6 lg:col-span-3 lg:col-start-1">
                <div className="space-y-2">
                    <div className="flex items-center justify-between">
                         <h2 className="text-2xl font-bold tracking-tight">{tool.title || formatTitle(tool.name)}</h2>
                         {!isSaved && (
                             <Button size="sm" variant="outline" onClick={handleSaveTool} disabled={saving}>
                                 {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                                 Save Tool
                             </Button>
                         )}
                         {isSaved && <div className="flex items-center text-green-500 text-sm font-medium"><CheckCircle className="w-4 h-4 mr-1"/> Saved</div>}
                    </div>
                    <p className="text-muted-foreground">{tool.description}</p>
                </div>

                <Card>
                    <CardContent className="pt-6">
                        <AutoForm schema={schema} value={formData} onChange={setFormData} />
                        
                        <div className="mt-6 flex justify-end">
                            <Button onClick={handleExecute} disabled={loading} className="w-full sm:w-auto">
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Running...
                                    </>
                                ) : (
                                    <>
                                        <Play className="mr-2 h-4 w-4" />
                                        Execute Tool
                                    </>
                                )}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
                
                {logs.length > 0 && (
                    <div className="bg-muted/30 rounded-lg p-4 font-mono text-xs text-muted-foreground max-h-40 overflow-y-auto">
                        <div className="font-semibold mb-2">Execution Logs:</div>
                        {logs.map((log, i) => <div key={i}>{log}</div>)}
                    </div>
                )}
            </div>

            {/* Output Column */}
            <div className="space-y-6 lg:col-span-8">
                 {error && (
                    <div className="bg-destructive/10 text-destructive p-4 rounded-lg flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="font-medium">Execution Failed</p>
                            <p className="text-sm opacity-90">{error}</p>
                        </div>
                    </div>
                 )}

                 {/* Persistent Loading State */}
                 {loading && !result && (
                     <Card className="h-full min-h-[500px] flex items-center justify-center bg-muted/5 animate-pulse">
                         <div className="text-center space-y-4">
                             <div className="relative w-16 h-16 mx-auto">
                                 <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
                                 <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                             </div>
                             <div>
                                 <h3 className="text-lg font-semibold">Running Tool...</h3>
                                 <p className="text-muted-foreground text-sm">Processing your request</p>
                             </div>
                         </div>
                     </Card>
                 )}

                 {result && (
                     <Card className="h-full flex flex-col">
                        <CardContent className="pt-6 flex-1 flex flex-col">
                            <h3 className="text-lg font-semibold mb-4">Result</h3>
                            
                            <div className="flex-1 space-y-4">
                                {result.visualization ? (
                                    <div className="w-full h-[300px]">
                                        <DynamicChart data={result.visualization as ChartData} />
                                    </div>
                                ) : null}
                                
                                {/* Chat Interface for Explanation & Follow-up */}
                                <div className="flex-1 min-h-[400px]">
                                     <ToolChatInterface 
                                        initialPrompt={`Here is the financial data from the '${formatTitle(tool.name)}' calculation: \n\`\`\`json\n${JSON.stringify({ 
                                            inputs: formData,
                                            output: result.output, 
                                            visualization_summary: result.visualization ? "A chart was generated." : "No chart." 
                                        })}\n\`\`\`\n\nPlease analyze this data. As a Financial Advisor, provide a clear, human-readable explanation of what this means. Do NOT show the raw JSON. Use Markdown for formatting.`}
                                     />
                                </div>
                            </div>
                        </CardContent>
                     </Card>
                 )}
                 
                 {!result && !error && !loading && (
                     <div className="border border-dashed rounded-xl h-full min-h-[400px] flex items-center justify-center text-muted-foreground bg-muted/5">
                        <div className="text-center">
                            <Play className="w-12 h-12 mx-auto mb-4 opacity-20" />
                            <p>Configure parameters and run the tool<br/>to see results here.</p>
                        </div>
                     </div>
                 )}
            </div>
        </div>
    )
}
