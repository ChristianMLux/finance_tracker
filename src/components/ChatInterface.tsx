"use client"

import { useState, useEffect } from "react"
import { API_URL } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card"
import { Input } from "./ui/Input"
import { Button } from "./ui/Button"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { DynamicChart, ChartData } from "./DynamicChart"
import { useAuth } from "@/context/AuthContext"
import { useChatHistory } from "@/hooks/useChatHistory"
import { v4 as uuidv4 } from 'uuid'
import { PlusCircle, MessageSquarePlus } from "lucide-react"
import { formatTitle } from "@/lib/utils"

type Message = {
    role: 'user' | 'agent'
    content: string
    component?: {
        type: string
        data: any
    }
}

interface ChatInterfaceProps {
    onAction?: (action: string) => void;
    initialInput?: string;
}

export function ChatInterface({ onAction, initialInput }: ChatInterfaceProps) {
    const [chatId, setChatId] = useState("default")
    const { messages: historyMessages, loading: historyLoading } = useChatHistory(chatId)
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [statusLog, setStatusLog] = useState<string>("")
    const { token } = useAuth()

    // effects
    useEffect(() => {
        if (initialInput) {
            setInput(initialInput)
        }
    }, [initialInput])
    
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)
    const [tools, setTools] = useState<{name: string, title?: string}[]>([])

    // Fetch tools on mount and when dropdown opens
    const fetchTools = async () => {
        if (!token) return
        try {
            const res = await fetch(`${API_URL}/tools/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setTools(data)
            }
        } catch (e) {
            console.error("Failed to fetch tools", e)
        }
    }

    useEffect(() => {
        fetchTools()
    }, [token])

    useEffect(() => {
        if (isDropdownOpen) {
            fetchTools()
        }
    }, [isDropdownOpen])

    const handleNewChat = () => {
        const newId = uuidv4()
        setChatId(newId)
        setPendingMessages([]) 
        setStatusLog("")
    }

    // Map Firestore 'assistant' role to UI 'agent' role
    const messages = historyMessages.map(msg => ({
        ...msg,
        role: msg.role === 'assistant' ? 'agent' : msg.role
    })) as Message[]

    const [pendingMessages, setPendingMessages] = useState<Message[]>([])
    
    // Merge history with pending messages
    const mergedMessages = [
        ...messages, 
        ...pendingMessages.filter(pm => !messages.some(m => m.content === pm.content && m.role === pm.role))
    ]

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim()) return

        const userMessage = input
        // Optimistic Update
        setPendingMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setInput("")
        setLoading(true)
        setStatusLog("Starting...")

        try {
            const headers: HeadersInit = {}
            if (token) headers['Authorization'] = `Bearer ${token}`

            const res = await fetch(`${API_URL}/chat?message=${encodeURIComponent(userMessage)}&chat_id=${chatId}`, {
                method: 'POST',
                headers,
            })
            
            if (!res.ok) throw new Error('Failed to send message')
            
            const reader = res.body?.getReader()
            if (!reader) throw new Error('No reader available')

            const decoder = new TextDecoder()
            let buffer = ""

            // Keep loading TRUE until stream ends to prevent input from re-enabling too early.
            // The status log will be cleared when we finish or when a new message arrives.
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
    }

    return (
        <Card className="h-[600px] flex flex-col glass-card border-none shadow-2xl">
            <CardHeader className="border-b border-white/5 bg-white/5 backdrop-blur-md flex flex-row items-center justify-between sticky top-0 z-10">
                <CardTitle className="flex items-center gap-2">
                    <span className="text-xl">🤖</span>
                    Finance Assistant
                </CardTitle>

                <div className="flex-1 flex justify-center px-4">
                    <div className="relative group">
                        {/* Custom Dropdown Trigger */}
                        <button 
                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                            className="bg-white/5 border border-white/10 rounded-full px-4 py-1.5 text-sm text-foreground hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer flex items-center gap-2 font-medium focus:ring-1 focus:ring-primary/50 focus:outline-none min-w-[100px] justify-center"
                        >
                            <span>Tools</span>
                            <span className="text-xs text-muted-foreground">▼</span>
                        </button>

                        {/* Custom Dropdown Menu */}
                        {isDropdownOpen && (
                            <>
                                <div 
                                    className="fixed inset-0 z-40" 
                                    onClick={() => setIsDropdownOpen(false)}
                                />
                                <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-48 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100 max-h-60 overflow-y-auto custom-scrollbar">
                                    <div className="py-1">
                                        {tools.map(tool => (
                                            <button
                                                key={tool.name}
                                                onClick={() => {
                                                    setInput(`I want to use the ${tool.title || formatTitle(tool.name)} tool.`);
                                                    setIsDropdownOpen(false);
                                                }}
                                                className="w-full text-left px-4 py-2.5 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors flex items-center gap-2 group/item"
                                            >
                                                <span className="opacity-0 group-hover/item:opacity-100 text-primary transition-opacity">➜</span>
                                                <span className="truncate">{tool.title || formatTitle(tool.name)}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </div>

                <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={handleNewChat}
                    className="text-muted-foreground hover:text-primary gap-2"
                    title="Start a new conversation"
                >
                    <MessageSquarePlus className="w-4 h-4" />
                    <span className="hidden sm:inline">New Chat</span>
                </Button>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
                <div className="flex-1 overflow-y-auto space-y-4 p-4 scroll-smooth">
                    {mergedMessages.length === 0 && (
                         <div className="flex flex-col items-center justify-center h-full text-muted-foreground opacity-50 space-y-2">
                            <span className="text-4xl">💬</span>
                            <p>Ask me anything about your finances!</p>
                            {chatId !== 'default' && <p className="text-xs">Chat ID: {chatId.slice(0,8)}...</p>}
                        </div>
                    )}
                    {mergedMessages.map((msg, i) => {
                        // Skip rendering if message is empty and has no component (avoids empty bubbles)
                        if (!msg.content && !msg.component) return null;
                        
                        return (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}>
                            <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-md ${
                                msg.role === 'user' 
                                ? 'bg-primary text-primary-foreground rounded-br-none' 
                                : msg.content.startsWith("Error:") 
                                    ? 'bg-destructive/10 text-destructive border border-destructive/20 rounded-bl-none' 
                                    : 'bg-muted text-foreground rounded-bl-none'
                            }`}>
                                {msg.component ? (
                                    msg.component.type === 'chart' ? (
                                        <DynamicChart data={msg.component.data as ChartData} />
                                    ) : (
                                        <div className="text-sm text-muted-foreground italic">[Unsupported Component: {msg.component.type}]</div>
                                    )
                                ) : msg.role === 'agent' ? (
                                    <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                                        <ReactMarkdown 
                                            remarkPlugins={[remarkGfm]}
                                            components={{
                                                p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                                                ul: ({node, ...props}) => <ul className="list-disc pl-4 mb-2" {...props} />,
                                                ol: ({node, ...props}) => <ol className="list-decimal pl-4 mb-2" {...props} />,
                                                li: ({node, ...props}) => <li className="mb-1" {...props} />,
                                                a: ({node, ...props}) => <a className="text-primary underline underline-offset-4" {...props} />,
                                                code: ({node, className, children, ...props}) => {
                                                    const match = /language-(\w+)/.exec(className || '')
                                                    return !className ? (
                                                        <code className="bg-black/10 dark:bg-white/10 px-1 py-0.5 rounded font-mono text-xs" {...props}>
                                                            {children}
                                                        </code>
                                                    ) : (
                                                        <code className={className} {...props}>
                                                            {children}
                                                        </code>
                                                    )
                                                },
                                                table: ({node, ...props}) => <div className="overflow-x-auto my-2"><table className="min-w-full divide-y divide-border" {...props} /></div>,
                                                th: ({node, ...props}) => <th className="bg-muted px-3 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider" {...props} />,
                                                td: ({node, ...props}) => <td className="px-3 py-2 whitespace-nowrap text-sm border-t border-border" {...props} />,
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                ) : (
                                    msg.content
                                )}
                            </div>
                        </div>
                    )})}
                    {loading && (
                        <div className="flex justify-start animate-pulse">
                            <div className="bg-muted rounded-2xl px-4 py-3 text-sm rounded-bl-none">
                                {statusLog || "Thinking..."}
                            </div>
                        </div>
                    )}
                </div>
                <div className="p-4 bg-background/50 backdrop-blur-sm border-t border-white/5">
                    <form onSubmit={handleSend} className="flex gap-2">
                        <Input 
                            value={input} 
                            onChange={(e) => setInput(e.target.value)} 
                            placeholder="Type a message..." 
                            disabled={loading}
                            className="bg-background/80 border-white/10"
                        />
                        <Button type="submit" disabled={loading} size="icon" className="w-12 shrink-0" aria-label="Send message">
                            ➤
                        </Button>
                    </form>
                </div>
            </CardContent>
        </Card>
    )
}
