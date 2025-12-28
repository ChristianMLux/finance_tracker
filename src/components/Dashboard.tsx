"use client"

import { useEffect, useState } from "react"
import { api, Expense } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card"
import { ExpenseForm } from "./ExpenseForm"
import { ExpenseList } from "./ExpenseList"
import { useAuth } from "@/context/AuthContext"

interface DashboardProps {
    refreshTrigger?: number;
}

export function Dashboard({ refreshTrigger = 0 }: DashboardProps) {
    const { user } = useAuth()
    const [expenses, setExpenses] = useState<Expense[]>([])
    const [error, setError] = useState<string | null>(null)

    const fetchExpenses = async () => {
        if (!user) return;
        try {
            setError(null)
            const token = await user.getIdToken()
            const data = await api.getExpenses(token)
            setExpenses(data)
        } catch (error) {
            console.error(error)
            setError("Failed to load expenses. Is backend running?")
        }
    }

    useEffect(() => {
        fetchExpenses()
    }, [user, refreshTrigger])

    const totalStats = expenses.reduce((acc, curr) => acc + curr.amount, 0)
    

    const categoryStats = expenses.reduce((acc, curr) => {
        acc[curr.category] = (acc[curr.category] || 0) + curr.amount
        return acc
    }, {} as Record<string, number>)
    

    const topCategory = Object.entries(categoryStats).sort(([,a], [,b]) => b - a)[0]

    return (
        <div className="space-y-8 animate-fade-in">
            {error && (
                <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md border border-destructive/20 text-sm">
                    ⚠️ {error}
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Total Spending</CardTitle>
                        <span className="text-2xl">💰</span>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-foreground">${totalStats.toFixed(2)}</div>
                        <p className="text-xs text-muted-foreground mt-1">+12% from last month</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Top Category</CardTitle>
                        <span className="text-2xl">📊</span>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-foreground">{topCategory ? topCategory[0] : "N/A"}</div>
                        <p className="text-xs text-muted-foreground mt-1">
                             {topCategory ? `$${topCategory[1].toFixed(2)} spent` : "No data yet"}
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Budget Status</CardTitle>
                        <span className="text-2xl">🎯</span>
                    </CardHeader>
                    <CardContent>
                         <div className="text-3xl font-bold text-foreground">On Track</div>
                         <div className="w-full bg-secondary h-2 mt-2 rounded-full overflow-hidden">
                            <div className="bg-primary h-full w-[65%]" />
                         </div>
                         <p className="text-xs text-muted-foreground mt-1">65% of budget used</p>
                    </CardContent>
                </Card>
            </div>
            

            <div className="grid gap-6 lg:grid-cols-3">
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex items-center justify-between">
                         <h2 className="text-xl font-semibold tracking-tight">Recent Transactions</h2>

                    </div>
                    <ExpenseList expenses={expenses} />
                </div>
                
                <div className="lg:col-span-1 space-y-6">
                    <Card className="bg-primary/5 border-primary/20">
                        <CardHeader>
                             <CardTitle className="text-primary">Quick Add</CardTitle>
                        </CardHeader>
                        <CardContent>
                             <ExpenseForm onExpenseAdded={fetchExpenses} />
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
