"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";

import { ChatInterface } from "@/components/ChatInterface";
import { Dashboard } from "@/components/Dashboard";
import { ExpenseForm } from "@/components/ExpenseForm";
import { ExpenseList } from "@/components/ExpenseList";
import { api, Expense } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Header } from "@/components/Header";

import { useAuth } from "@/context/AuthContext";

function HomeContent() {
  const { token } = useAuth();
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const searchParams = useSearchParams();
  
  const toolName = searchParams.get('tool');
  const toolTitle = searchParams.get('title');
  const initialInput = toolName ? `I want to use the ${toolTitle || toolName} tool.` : "";

  useEffect(() => {
    if (token) {
        api.getExpenses(token).then(setExpenses).catch(console.error);
    }
  }, [token, refreshTrigger]);

  const handleDownloadReport = async () => {
    if (!token) return;
    try {
      const expenses = await api.getExpenses(token);
      const csvHeader = "Date,Category,Amount,Description\n";
      const csvRows = expenses.map(e => 
        `${e.date},${e.category},${e.amount},"${e.description || ''}"`
      ).join("\n");
      
      const blob = new Blob([csvHeader + csvRows], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `expenses_report_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download report:", error);
      alert("Failed to generate report. Please try again.");
    }
  };

  return (
    <div className="max-w-7xl space-y-8">
      <Header />
      
      <div className="flex justify-end">
           <button 
             onClick={handleDownloadReport}
             className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md text-sm font-medium hover:bg-secondary/80 transition-colors"
           >
             Download Report
           </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 space-y-8">
          <Dashboard refreshTrigger={refreshTrigger} />
          
          <div className="grid gap-8 md:grid-cols-2">
            <div className="space-y-4">
              <h2 className="text-xl font-semibold tracking-tight">Quick Add</h2>
              <Card>
                <div className="p-6">
                  <ExpenseForm onSuccess={() => setRefreshTrigger(prev => prev + 1)} />
                </div>
              </Card>
            </div>

            <div className="space-y-4">
              <h2 className="text-xl font-semibold tracking-tight">Budget Overview</h2>
              <Card>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium">Monthly Budget</span>
                    <span className="text-sm text-muted-foreground">$2,450.00 left</span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div className="h-full bg-primary w-[65%]" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    You have spent 65% of your total budget.
                  </p>
                </div>
              </Card>
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold tracking-tight">Recent Expenses</h2>
            {/* Wrapper removed, letting ExpenseList's Card take over */}
            <ExpenseList expenses={expenses} key={refreshTrigger} />
          </div>
        </div>
        
        <div className="xl:col-span-1">
          <div className="sticky top-8 space-y-6">

            <div className="relative">
                 <div className="absolute -inset-0.5 bg-gradient-to-r from-pink-600 to-purple-600 rounded-2xl blur animate-pulse-slow"></div>
                 <ChatInterface 
                    initialInput={initialInput}
                    onAction={(action) => {
                     if (action === 'expense_added') {
                         setRefreshTrigger(prev => prev + 1);
                     }
                 }} />
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <HomeContent />
        </Suspense>
    );
}
