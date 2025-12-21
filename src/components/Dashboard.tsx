"use client"

import { useEffect, useState } from "react"
import { api, Expense } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card"
import { ExpenseForm } from "./ExpenseForm"
import { ExpenseList } from "./ExpenseList"

export function Dashboard() {
    const [expenses, setExpenses] = useState<Expense[]>([])

    const fetchExpenses = async () => {
        try {
            const data = await api.getExpenses()
            setExpenses(data)
        } catch (error) {
            console.error(error)
        }
    }

    useEffect(() => {
        fetchExpenses()
    }, [])

    const totalStats = expenses.reduce((acc, curr) => acc + curr.amount, 0)

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Spending</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">${totalStats.toFixed(2)}</div>
                    <p className="text-xs text-gray-500">All time expenses</p>
                </CardContent>
            </Card>
            
            <div className="col-span-1 md:col-span-2 lg:col-span-3 grid gap-4 md:grid-cols-2">
                <div className="space-y-4">
                    <ExpenseForm onExpenseAdded={fetchExpenses} />
                    <ExpenseList expenses={expenses} />
                </div>
                <div>
                     {/* Chat Interface will be placed here in the main layout or passed as prop if needed, 
                         but for now let's keep Dashboard focused on Expenses */}
                </div>
            </div>
        </div>
    )
}
