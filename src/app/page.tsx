import Image from "next/image";

import { ChatInterface } from "@/components/ChatInterface";
import { Dashboard } from "@/components/Dashboard";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
            Personal Finance Tracker
          </h1>
          <Dashboard />
        </div>
        <div className="lg:col-span-1">
          <div className="lg:sticky lg:top-8">
            <ChatInterface />
          </div>
        </div>
      </div>
    </div>
  );
}
