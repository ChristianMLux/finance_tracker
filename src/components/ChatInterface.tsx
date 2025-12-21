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
        <Card className="h-[600px] flex flex-col">
            <CardHeader>
                <CardTitle>Finance Assistant</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-2">
                    {messages.length === 0 && (
                        <p className="text-gray-500 text-center mt-20">Ask me anything about your finances!</p>
                    )}
                    {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] rounded-lg p-3 ${
                                msg.role === 'user' 
                                ? 'bg-black text-white dark:bg-white dark:text-black' 
                                : 'bg-gray-100 dark:bg-gray-800'
                            }`}>
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3 animate-pulse">
                                Thinking...
                            </div>
                        </div>
                    )}
                </div>
                <form onSubmit={handleSend} className="flex gap-2 mt-auto">
                    <Input 
                        value={input} 
                        onChange={(e) => setInput(e.target.value)} 
                        placeholder="Type a message..." 
                        disabled={loading}
                    />
                    <Button type="submit" disabled={loading}>Send</Button>
                </form>
            </CardContent>
        </Card>
    )
}
