"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

const navItems = [
  { name: "Dashboard", href: "/", icon: "📊" },
  { name: "Expenses", href: "/expenses", icon: "💳" },
  { name: "Settings", href: "/settings", icon: "⚙️" },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <>
      {/* Desktop Sidebar */}
      <nav className="hidden lg:flex flex-col w-64 h-screen fixed left-0 top-0 border-r border-border bg-background/50 backdrop-blur-md p-4 space-y-4">
        <div className="flex items-center gap-2 px-4 py-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
            F
          </div>
          <span className="text-xl font-bold tracking-tight">Finance</span>
        </div>
        
        <div className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === item.href
                  ? "bg-primary/10 text-primary border-r-2 border-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </div>
        
        <div className="mt-auto px-4 py-4 border-t border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs">
              U
            </div>
            <div className="text-sm">
              <p className="font-medium">User</p>
              <p className="text-xs text-muted-foreground">Pro Plan</p>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Topbar */}
      <nav className="lg:hidden fixed top-0 left-0 right-0 h-16 border-b border-border bg-background/50 backdrop-blur-md flex items-center px-4 z-50">
         <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
              F
            </div>
            <span className="text-lg font-bold">Finance</span>
         </div>
      </nav>

        {/* Mobile Bottom Bar */}
        <nav className="lg:hidden fixed bottom-0 left-0 right-0 h-16 border-t border-border bg-background/80 backdrop-blur-md flex items-center justify-around px-2 z-50 pb-safe">
            {navItems.map((item) => (
                <Link
                    key={item.href}
                    href={item.href}
                    className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-colors ${
                        pathname === item.href
                            ? "text-primary"
                            : "text-muted-foreground hover:text-foreground"
                    }`}
                >
                    <span className="text-xl">{item.icon}</span>
                    <span className="text-[10px] uppercase font-bold tracking-wider">{item.name}</span>
                </Link>
            ))}
        </nav>
    </>
  )
}
