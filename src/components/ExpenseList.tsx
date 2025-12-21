"use client"

import { useState, useMemo } from "react"
import { Expense } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card"
import { Input } from "./ui/Input"
import { Button } from "./ui/Button"

interface ExpenseListProps {
    expenses: Expense[]
}

type SortOption = "date-desc" | "date-asc" | "amount-desc" | "amount-asc"

const categoryIcons: Record<string, string> = {
    "Food": "🍔",
    "Transport": "🚗",
    "Shopping": "🛍️",
    "Entertainment": "🎬",
    "Health": "💊",
    "Education": "📚",
    "Bills": "🧾",
    "Travel": "✈️",
    "Other": "📦"
}

export function ExpenseList({ expenses }: ExpenseListProps) {
    const [searchTerm, setSearchTerm] = useState("")
    const [sortOption, setSortOption] = useState<SortOption>("date-desc")
    const [page, setPage] = useState(1)
    const itemsPerPage = 5

    const filteredExpenses = useMemo(() => {
        return expenses.filter(expense => 
            expense.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            expense.category.toLowerCase().includes(searchTerm.toLowerCase())
        ).sort((a, b) => {
            switch (sortOption) {
                case "date-desc":
                    return new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime()
                case "date-asc":
                    return new Date(a.date || 0).getTime() - new Date(b.date || 0).getTime()
                case "amount-desc":
                    return (b.amount || 0) - (a.amount || 0)
                case "amount-asc":
                    return (a.amount || 0) - (b.amount || 0)
                default:
                    return 0
            }
        })
    }, [expenses, searchTerm, sortOption])

    const totalPages = Math.ceil(filteredExpenses.length / itemsPerPage)
    const paginatedExpenses = filteredExpenses.slice((page - 1) * itemsPerPage, page * itemsPerPage)

    return (
        <Card className="w-full">
            <CardHeader>
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                    <CardTitle>Recent Expenses</CardTitle>
                    <div className="flex items-center gap-2 w-full sm:w-auto">
                        <Input 
                            placeholder="Search expenses..." 
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="max-w-xs"
                        />
                        <select 
                            className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            value={sortOption}
                            onChange={(e) => setSortOption(e.target.value as SortOption)}
                        >
                            <option value="date-desc">Newest</option>
                            <option value="date-asc">Oldest</option>
                            <option value="amount-desc">Highest</option>
                            <option value="amount-asc">Lowest</option>
                        </select>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-1">
                    {paginatedExpenses.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            {searchTerm ? "No matching expenses found." : "No expenses recorded yet."}
                        </div>
                    ) : (
                        paginatedExpenses.map((expense) => (
                            <div 
                                key={expense.id} 
                                className="group flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center text-xl shadow-sm group-hover:scale-105 transition-transform">
                                        {categoryIcons[expense.category] || "📦"}
                                    </div>
                                    <div>
                                        <p className="font-medium">{expense.category}</p>
                                        <p className="text-sm text-muted-foreground">{expense.description || "No description"}</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="font-bold text-foreground">
                                        ${expense.amount.toFixed(2)}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        {expense.date ? new Date(expense.date).toLocaleDateString() : "No date"}
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-2 mt-6">
                        <Button 
                            variant="outline" 
                            size="sm"
                            disabled={page === 1}
                            onClick={() => setPage(p => p - 1)}
                        >
                            Previous
                        </Button>
                        <span className="text-sm text-muted-foreground">
                            Page {page} of {totalPages}
                        </span>
                        <Button 
                            variant="outline" 
                            size="sm"
                            disabled={page === totalPages}
                            onClick={() => setPage(p => p + 1)}
                        >
                            Next
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
