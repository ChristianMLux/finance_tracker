"use client"

import { useEffect, useState } from "react"
import { api, Expense } from "@/lib/api"
import { ExpenseList } from "@/components/ExpenseList"
import { ExpenseForm } from "@/components/ExpenseForm"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"

export default function ExpensesPage() {
    const [expenses, setExpenses] = useState<Expense[]>([])
    const [isFormOpen, setIsFormOpen] = useState(false)

    const fetchExpenses = async () => {
        try {
            const data = await api.getExpenses()
            setExpenses(data)
        } catch (error) {
            console.error("Failed to fetch expenses", error)
        }
    }

    useEffect(() => {
        fetchExpenses()
    }, [])

    return (
        <div className="space-y-8 animate-fade-in max-w-5xl mx-auto">
             <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                 <div>
                    <h1 className="text-3xl font-bold tracking-tight">Expenses</h1>
                    <p className="text-muted-foreground">Manage and view all your transactions.</p>
                 </div>
                 <Button onClick={() => setIsFormOpen(!isFormOpen)}>
                    {isFormOpen ? "Close Form" : "Add Expense"}
                 </Button>
             </div>

             {isFormOpen && (
                 <div className="animate-slide-up">
                    <Card>
                        <CardHeader>
                            <CardTitle>Add New Expense</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ExpenseForm onExpenseAdded={() => {
                                fetchExpenses()
                                setIsFormOpen(false)
                            }} />
                        </CardContent>
                    </Card>
                 </div>
             )}

             <ExpenseList expenses={expenses} />
        </div>
    )
}
