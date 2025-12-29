"use client"

import { useAuth } from "@/context/AuthContext"
import { useEffect, useState } from "react"
import { TrendingUp, Bell } from "lucide-react"

export function Header() {
    const { userData } = useAuth()
    const [greeting, setGreeting] = useState("Good Day")
    
    // Logic for greeting based on time of day
    useEffect(() => {
        const hour = new Date().getHours()
        if (hour < 12) setGreeting("Good Morning")
        else if (hour < 18) setGreeting("Good Afternoon")
        else setGreeting("Good Evening")
    }, [])

    const userName = (userData?.full_name as string) || (userData?.email as string)?.split('@')[0] || "Guest"

    return (
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 animate-fade-in">
            <div>
                <h1 className="text-3xl font-display font-bold tracking-tight text-foreground">
                    {greeting}, {userName}
                </h1>
                <div className="flex items-center gap-2 mt-1 text-muted-foreground text-sm">
                   <span>Here's your financial overview today.</span>
                </div>
            </div>
        </div>
    )
}
