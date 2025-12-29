"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { ChevronLeft, ChevronRight, LayoutDashboard, CreditCard, PenTool, Settings, LogOut } from "lucide-react"

import { ThemeToggle } from "@/components/ThemeToggle"
import { Button } from "./ui/Button"

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Expenses", href: "/expenses", icon: CreditCard },
  { name: "Tools", href: "/tools", icon: PenTool },
  { name: "Settings", href: "/settings", icon: Settings },
]

interface NavigationProps {
    isCollapsed?: boolean
    toggleCollapse?: () => void
}

export function Navigation({ isCollapsed = false, toggleCollapse }: NavigationProps) {
  const pathname = usePathname()
  const { userData, signOut } = useAuth()

  return (
    <>
      {/* Desktop Sidebar */}
      <nav 
        className={`
            hidden lg:flex flex-col 
            ${isCollapsed ? 'w-20' : 'w-64'} 
            h-screen fixed left-0 top-0 
            border-r border-border bg-background/50 backdrop-blur-md 
            transition-all duration-300 ease-in-out
            p-4 space-y-4 z-40
        `}
      >
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} px-2 py-3 mb-2 transition-all`}>
            {/* Logo area */}
            <div className="flex items-center gap-2 overflow-hidden">
                <div className="w-8 h-8 rounded-full bg-primary flex-shrink-0 flex items-center justify-center text-primary-foreground font-bold">
                    F
                </div>
                {!isCollapsed && (
                    <span className="text-xl font-bold tracking-tight animate-fade-in whitespace-nowrap">
                        Finance
                    </span>
                )}
            </div>
            
            {!isCollapsed && <ThemeToggle />}
        </div>

        {/* Navigation Links */}
        <div className="space-y-1 flex-1">
          {navItems.map((item) => {
             const Icon = item.icon
             const isActive = pathname === item.href
             return (
                <Link
                key={item.href}
                href={item.href}
                className={`
                    flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                    ${isActive 
                        ? "bg-primary/10 text-foreground" 
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }
                    ${isCollapsed ? 'justify-center px-2' : ''}
                `}
                title={isCollapsed ? item.name : undefined}
                >
                <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-primary' : ''}`} />
                {!isCollapsed && (
                    <span className="whitespace-nowrap animate-fade-in">{item.name}</span>
                )}
                </Link>
             )
          })}
        </div>
        
        {/* Footer Actions */}
        <div className="mt-auto pt-4 border-t border-border space-y-4">
            {/* Collapse Toggle */}
            {toggleCollapse && (
                <div className={`flex ${isCollapsed ? 'justify-center' : 'justify-end'}`}>
                    <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={toggleCollapse}
                        className="text-muted-foreground hover:text-foreground"
                    >
                        {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
                    </Button>
                </div>
            )}

            {/* Profile */}
            <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} transition-all`}>
                <div className="w-8 h-8 rounded-full bg-muted flex-shrink-0 flex items-center justify-center text-xs uppercase cursor-default" title={(userData as { email?: string })?.email || "User"}>
                    {(userData?.full_name as string) ? (userData?.full_name as string)?.[0] : ((userData?.email as string)?.[0] || "U")}
                </div>
                {!isCollapsed && (
                    <div className="text-sm overflow-hidden animate-fade-in">
                        <p className="font-medium truncate max-w-[120px]">{(userData?.full_name as string) || (userData?.email as string)?.split('@')[0] || "Guest"}</p>
                        <p className="text-xs text-muted-foreground capitalize">{(userData?.role as string) || "Free"} Plan</p>
                    </div>
                )}
            </div>

            {/* Logout */}
             <button 
                onClick={() => signOut()} 
                className={`
                    w-full text-xs text-left text-muted-foreground hover:text-destructive transition-colors flex items-center gap-2 pl-1
                    ${isCollapsed ? 'justify-center pl-0' : ''}
                `}
                title="Sign Out"
             >
                <LogOut className="w-4 h-4" /> 
                {!isCollapsed && <span>Sign Out</span>}
             </button>
        </div>
      </nav>

      {/* Mobile Topbar */}
      <nav className="lg:hidden fixed top-0 left-0 right-0 h-16 border-b border-border bg-background/50 backdrop-blur-md flex items-center justify-between px-4 z-50">
         <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
              F
            </div>
            <span className="text-lg font-bold">Finance</span>
         </div>
         <ThemeToggle />
      </nav>

        {/* Mobile Bottom Bar */}
        <nav className="lg:hidden fixed bottom-0 left-0 right-0 h-16 border-t border-border bg-background/80 backdrop-blur-md flex items-center justify-around px-2 z-50 pb-safe">
            {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                <Link
                    key={item.href}
                    href={item.href}
                    className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-colors ${
                        isActive
                            ? "text-primary"
                            : "text-muted-foreground hover:text-foreground"
                    }`}
                >
                    <Icon className="w-5 h-5" />
                    <span className="text-[10px] uppercase font-bold tracking-wider">{item.name}</span>
                </Link>
            )})}
        </nav>
    </>
  )
}
