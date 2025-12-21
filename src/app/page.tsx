"use client";

import { ChatInterface } from "@/components/ChatInterface";
import { Dashboard } from "@/components/Dashboard";
import { api } from "@/lib/api";

export default function Home() {
  const handleDownloadReport = async () => {
    try {
      const expenses = await api.getExpenses();
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
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-4xl font-display font-bold tracking-tight text-foreground">
            Overview
          </h1>
          <p className="text-muted-foreground mt-1">
            Welcome back, here&apos;s what&apos;s happening with your finances.
          </p>
        </div>
        <div className="flex items-center gap-2">
           <button 
             onClick={handleDownloadReport}
             className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md text-sm font-medium hover:bg-secondary/80 transition-colors"
           >
             Download Report
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 space-y-8">
          <Dashboard />
        </div>
        
        <div className="xl:col-span-1">
          <div className="sticky top-8 space-y-6">

            <div className="relative">
                 <div className="absolute -inset-0.5 bg-gradient-to-r from-pink-600 to-purple-600 rounded-2xl blur opacity-30 animate-pulse"></div>
                 <ChatInterface />
            </div>
            

          </div>
        </div>
      </div>
    </div>
  );
}
