"use client"

import { useState } from "react"
import { api } from "@/lib/api"
import { Button } from "./ui/Button"
import { Input } from "./ui/Input"
 

import { useAuth } from "@/context/AuthContext"

interface ExpenseFormProps {
    onExpenseAdded?: () => void
    onSuccess?: () => void
}

export function ExpenseForm({ onExpenseAdded, onSuccess }: ExpenseFormProps) {
    const { user } = useAuth()
    const [amount, setAmount] = useState("")
    const [category, setCategory] = useState("")
    const [description, setDescription] = useState("")
    const [loading, setLoading] = useState(false)

    const [error, setError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!user) return
        
        setLoading(true)
        setError(null)
        try {
            const token = await user.getIdToken()
            await api.createExpense({
                amount: parseFloat(amount),
                category,
                description
            }, token)
            setAmount("")
            setCategory("")
            setDescription("")
            if (onExpenseAdded) onExpenseAdded()
            if (onSuccess) onSuccess()
        } catch (error) {
            console.error("Failed to add expense", error)
            setError("Failed to add expense. Please try again.")
        } finally {
            setLoading(false)
        }
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label htmlFor="amount" className="text-xs font-medium text-muted-foreground ml-1">Amount</label>
                    <div className="relative">
                        <span className="absolute left-3 top-2.5 text-muted-foreground">$</span>
                        <Input 
                            id="amount"
                            placeholder="0.00" 
                            type="number" 
                            value={amount} 
                            onChange={(e) => setAmount(e.target.value)} 
                            className="pl-7"
                            required 
                            step="0.01"
                        />
                    </div>
                </div>
                <div className="space-y-2">
                    <label htmlFor="category" className="text-xs font-medium text-muted-foreground ml-1">Category</label>
                    <Input 
                        id="category"
                        placeholder="e.g. Food" 
                        value={category} 
                        onChange={(e) => setCategory(e.target.value)} 
                        required 
                        list="categories"
                    />
                    <datalist id="categories">
                        <option value="Food" />
                        <option value="Transport" />
                        <option value="Shopping" />
                        <option value="Bills" />
                        <option value="Entertainment" />
                    </datalist>
                </div>
            </div>
            <div className="space-y-2">
                <label htmlFor="description" className="text-xs font-medium text-muted-foreground ml-1">Description</label>
                <Input 
                    id="description"
                    placeholder="What did you buy?" 
                    value={description} 
                    onChange={(e) => setDescription(e.target.value)} 
                />
            </div>
            <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Adding..." : "Add Expense"}
            </Button>
            {error && (
                <p className="text-xs text-destructive text-center">{error}</p>
            )}
        </form>
    )
}
