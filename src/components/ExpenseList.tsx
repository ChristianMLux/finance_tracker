"use client"

import { Expense } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card"

interface ExpenseListProps {
    expenses: Expense[]
}

export function ExpenseList({ expenses }: ExpenseListProps) {
    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Recent Expenses</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {expenses.length === 0 ? (
                        <p className="text-gray-500">No expenses recorded yet.</p>
                    ) : (
                        expenses.map((expense) => (
                            <div key={expense.id} className="flex justify-between items-center border-b pb-2 last:border-0 last:pb-0">
                                <div>
                                    <p className="font-medium">{expense.category}</p>
                                    <p className="text-sm text-gray-500">{expense.description}</p>
                                </div>
                                <div className="font-bold">
                                    ${expense.amount.toFixed(2)}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </CardContent>
        </Card>
    )
}
