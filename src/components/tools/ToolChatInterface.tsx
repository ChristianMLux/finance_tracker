"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { API_URL } from "@/lib/api"
import { Card, CardContent } from "../ui/Card"

import { Button } from "../ui/Button"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { DynamicChart, ChartData } from "../DynamicChart"
import { useAuth } from "@/context/AuthContext"
import { useChatHistory } from "@/hooks/useChatHistory"
import { v4 as uuidv4 } from 'uuid'
import { MessageSquarePlus } from "lucide-react"


type Message = {
    role: 'user' | 'agent'
    content: string
    component?: {
        type: string
        data: unknown
    }
}

interface ToolChatInterfaceProps {
    initialPrompt?: string;
}

export function ToolChatInterface({ initialPrompt }: ToolChatInterfaceProps) {
    const [chatId, setChatId] = useState(() => uuidv4()) // Unique chat tool execution
    const { messages: historyMessages } = useChatHistory(chatId)
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [statusLog, setStatusLog] = useState<string>("")
    const { token } = useAuth()
    const hasInitialTriggered = useRef(false)




    // Map Firestore 'assistant' role to UI 'agent' role
    const messages = historyMessages.map(msg => ({
        ...msg,
        role: msg.role === 'assistant' ? 'agent' : msg.role
    })) as Message[]

    const [pendingMessages, setPendingMessages] = useState<Message[]>([])
    
    // Merge history with pending messages and filter out hidden technical prompts
    const mergedMessages = [
        ...messages, 
        ...pendingMessages.filter(pm => !messages.some(m => m.content === pm.content && m.role === pm.role))
    ].filter(msg => 
        !msg.content.includes("I just ran the tool") && 
        !msg.content.includes("Here is the financial data")
    )

    const handleNewChat = () => {
        const newId = uuidv4()
        setChatId(newId)
        setPendingMessages([]) 
        setStatusLog("")
    }

    const handleSend = useCallback(async (e?: React.FormEvent, overrideInput?: string, options: { hidden?: boolean } = {}) => {
        if (e) e.preventDefault()
        const messageToSend = overrideInput || input
        if (!messageToSend.trim()) return

        if (!options.hidden) {
             setPendingMessages(prev => [...prev, { role: 'user', content: messageToSend }])
        }
        
        setInput("")
        setLoading(true)
        setStatusLog(options.hidden ? "Analyzing results..." : "Thinking...")

        try {
            const headers: HeadersInit = {}
            if (token) headers['Authorization'] = `Bearer ${token}`

            const res = await fetch(`${API_URL}/chat?message=${encodeURIComponent(messageToSend)}&chat_id=${chatId}`, {
                method: 'POST',
                headers,
            })
            
            if (!res.ok) throw new Error('Failed to send message')
            
            const reader = res.body?.getReader()
            if (!reader) throw new Error('No reader available')

            const decoder = new TextDecoder()
            let buffer = ""

            while (true) {
                const { done, value } = await reader.read()
                if (done) break
                
                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n')
                buffer = lines.pop() || ""

                for (const line of lines) {
                    if (!line.trim()) continue
                    try {
                        const data = JSON.parse(line)
                        if (data.type === 'log') {
                            setStatusLog(data.content)
                        } 
                    } catch (e) {
                        console.error("Error parsing NDJSON:", e)
                    }
                }
            }

        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
            setStatusLog("") 
        }
    }, [input, token, chatId])

    // Auto-send initial prompt if provided and not yet triggered
    useEffect(() => {
        if (initialPrompt && !hasInitialTriggered.current && token) {
             hasInitialTriggered.current = true
             handleSend(undefined, initialPrompt, { hidden: true })
        }
    }, [initialPrompt, token, handleSend])

    return (
        <Card className="h-full flex flex-col glass-card border-none shadow-none bg-transparent">
             {/* Simplified Header for Tool Chat */}
             <div className="px-4 py-2 border-b border-border/40 flex justify-between items-center bg-muted/20">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-widest">AI Analysis & Chat</span>
                <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={handleNewChat}
                    className="h-6 text-xs text-muted-foreground hover:text-primary"
                >
                    <MessageSquarePlus className="w-3 h-3 mr-1" />
                    Reset
                </Button>
            </div>

            <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
                <div className="flex-1 overflow-y-auto space-y-4 p-4 pb-20 scroll-smooth">
                    {/* Welcome/Empty State - Only show if absolutely no messages and not loading */}
                    {/* Welcome/Empty State - Show when no messages OR when analyzing initial result */}
                    {mergedMessages.length === 0 && (
                         <div className="flex flex-col items-center justify-center h-full text-muted-foreground space-y-4">
                            {loading ? (
                                <>
                                    <div className="relative w-12 h-12">
                                        <div className="absolute inset-0 border-2 border-primary/20 rounded-full"></div>
                                        <div className="absolute inset-0 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                                    </div>
                                    <div className="text-center">
                                        <p className="font-medium text-foreground">Analyzing Results</p>
                                        <p className="text-xs opacity-70 mt-1">{statusLog || "Interpreting financial data..."}</p>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <span className="text-2xl opacity-50">🤖</span>
                                    <p className="text-sm opacity-50">Analysis complete. Ask a follow-up!</p>
                                </>
                            )}
                        </div>
                    )}

                    {mergedMessages.map((msg, i) => {
                        // Normalize component data if present
                        let serializedComponent = msg.component
                        if (serializedComponent) {
                             const legacyComponent = serializedComponent as unknown as { component?: string; type?: string; data?: unknown };
                             if (legacyComponent.component && !legacyComponent.type) {
                                 serializedComponent = {
                                     ...serializedComponent,
                                     type: legacyComponent.component
                                 }
                             }
                             if (serializedComponent.type === 'chart' && serializedComponent.data) {
                                  type ChartDataPayload = {
                                      title?: string; type?: string; xAxisKey?: string;
                                      series?: Array<{ title?: string; type?: string; xAxisKey?: string; }>;
                                  };
                                  const chartData = serializedComponent.data as ChartDataPayload;
                                  if (!chartData.title && chartData.series?.[0]?.title) chartData.title = chartData.series[0].title
                                  if (!chartData.type && chartData.series?.[0]?.type) chartData.type = chartData.series[0].type
                                  if (!chartData.xAxisKey && chartData.series?.[0]?.xAxisKey) chartData.xAxisKey = chartData.series[0].xAxisKey
                             }
                        }

                        if (!msg.content && !serializedComponent) return null;
                        
                        return (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}>
                            <div className={`max-w-[90%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                                msg.role === 'user' 
                                ? 'bg-primary text-primary-foreground rounded-br-none' 
                                : 'bg-muted/80 text-foreground rounded-bl-none'
                            }`}>
                                {msg.role === 'agent' ? (
                                    <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                                        <ReactMarkdown 
                                            remarkPlugins={[remarkGfm]}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                ) : (
                                    msg.content
                                )}

                                {serializedComponent && (
                                    <div className="mt-4 pt-4 border-t border-border/50">
                                        {serializedComponent.type === 'chart' ? (
                                            <DynamicChart data={serializedComponent.data as ChartData} />
                                        ) : (
                                            <div className="text-sm text-muted-foreground">Unsupported Component</div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    )})}
                    {loading && (
                        <div className="flex justify-start animate-pulse">
                            <div className="bg-muted rounded-2xl px-4 py-3 text-sm rounded-bl-none">
                                {statusLog || "Analyzing..."}
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-background via-background to-transparent z-10">
                    <form onSubmit={handleSend} className="relative flex items-center gap-2 bg-background border border-input p-1 rounded-full shadow-sm focus-within:ring-1 focus-within:ring-primary">
                        <input 
                            value={input} 
                            onChange={(e) => setInput(e.target.value)} 
                            placeholder="Ask a follow-up question..." 
                            disabled={loading}
                            className="flex-1 bg-transparent border-none outline-none shadow-none px-4 h-9 text-sm"
                        />
                        <Button 
                            type="submit" 
                            disabled={loading || !input.trim()} 
                            size="icon" 
                            className="rounded-full w-8 h-8 shrink-0"
                        >
                            {loading ? <span className="animate-spin text-[10px]">⏳</span> : "↑"}
                        </Button>
                    </form>
                </div>
            </CardContent>
        </Card>
    )
}
