"use client"

import { useState } from "react"
import { Navigation } from "@/components/Navigation"

interface ShellProps {
    children: React.ReactNode
}

export function Shell({ children }: ShellProps) {
    const [isCollapsed, setIsCollapsed] = useState(false)

    return (
        <div className="min-h-screen bg-background">
            {/* Navigation handles both Desktop Sidebar and Mobile Bars */}
            <Navigation isCollapsed={isCollapsed} toggleCollapse={() => setIsCollapsed(!isCollapsed)} />
            
            {/* Main Content Area */}
            {/* 
                Desktop: Margin left depends on collapsed state.
                w-64 (256px) -> ml-64
                w-20 (80px) -> ml-20
                Mobile: No margin (Sidebar is hidden), simplified layout expected.
            */}
            <main 
                className={`
                    transition-all duration-300 ease-in-out
                    ${isCollapsed ? 'lg:ml-20' : 'lg:ml-64'}
                    min-h-screen
                    p-4 pb-24 lg:px-8 lg:pt-6.5
                `}
            >
                <div className="w-full">
                    {children}
                </div>
            </main>
        </div>
    )
}
