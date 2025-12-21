"use client"

import { useState } from "react"
import { api } from "@/lib/api"
import { Button } from "./ui/Button"
import { Input } from "./ui/Input"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card"

interface ExpenseFormProps {
    onExpenseAdded: () => void
}

export function ExpenseForm({ onExpenseAdded }: ExpenseFormProps) {
    const [amount, setAmount] = useState("")
    const [category, setCategory] = useState("")
    const [description, setDescription] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            await api.createExpense({
                amount: parseFloat(amount),
                category,
                description
            })
            setAmount("")
            setCategory("")
            setDescription("")
            onExpenseAdded()
        } catch (error) {
            console.error("Failed to add expense", error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Add Expense</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                    <Input 
                        placeholder="Amount" 
                        type="number" 
                        value={amount} 
                        onChange={(e) => setAmount(e.target.value)} 
                        required 
                    />
                    <Input 
                        placeholder="Category (e.g., Food)" 
                        value={category} 
                        onChange={(e) => setCategory(e.target.value)} 
                        required 
                    />
                    <Input 
                        placeholder="Description" 
                        value={description} 
                        onChange={(e) => setDescription(e.target.value)} 
                    />
                    <Button type="submit" disabled={loading}>
                        {loading ? "Adding..." : "Add Expense"}
                    </Button>
                </form>
            </CardContent>
        </Card>
    )
}
