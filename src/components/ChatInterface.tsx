"use client"

import { useState } from "react"
import { api } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card"
import { Input } from "./ui/Input"
import { Button } from "./ui/Button"

export function ChatInterface() {
    const [messages, setMessages] = useState<{role: 'user' | 'agent', content: string}[]>([])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim()) return

        const userMessage = input
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setInput("")
        setLoading(true)

        try {
            const response = await api.chat(userMessage)
            setMessages(prev => [...prev, { role: 'agent', content: response }])
        } catch (error) {
            setMessages(prev => [...prev, { role: 'agent', content: "Error: Failed to get response." }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <Card className="h-[600px] flex flex-col glass-card border-none shadow-2xl">
            <CardHeader className="border-b border-white/5 bg-white/5 backdrop-blur-md">
                <CardTitle className="flex items-center gap-2">
                    <span className="text-xl">🤖</span>
                    Finance Assistant
                </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
                <div className="flex-1 overflow-y-auto space-y-4 p-4 scroll-smooth">
                    {messages.length === 0 && (
                         <div className="flex flex-col items-center justify-center h-full text-muted-foreground opacity-50 space-y-2">
                            <span className="text-4xl">💬</span>
                            <p>Ask me anything about your finances!</p>
                        </div>
                    )}
                    {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}>
                            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-md ${
                                msg.role === 'user' 
                                ? 'bg-primary text-primary-foreground rounded-br-none' 
                                : msg.content.startsWith("Error:") 
                                    ? 'bg-destructive/10 text-destructive border border-destructive/20 rounded-bl-none' 
                                    : 'bg-muted text-foreground rounded-bl-none'
                            }`}>
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex justify-start animate-pulse">
                            <div className="bg-muted rounded-2xl px-4 py-3 text-sm rounded-bl-none">
                                Thinking...
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
                        <Button type="submit" disabled={loading} size="icon" className="w-12 shrink-0">
                            ➤
                        </Button>
                    </form>
                </div>
            </CardContent>
        </Card>
    )
}
