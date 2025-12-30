import { formatTitle } from "@/lib/utils"
import { notFound } from "next/navigation"
import { DynamicToolRunner } from "@/components/tools/DynamicToolRunner"
import { ChevronLeft } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/Button"

async function getTool(name: string) {
  try {
      const res = await fetch(`http://127.0.0.1:8000/tools/${name}`, { cache: 'no-store' })
      if (!res.ok) return undefined
      return res.json()
  } catch (error) {
      console.error("Failed to fetch tool:", error)
      return undefined
  }
}

export default async function ToolPage({ params, searchParams }: { params: { name: string }, searchParams: { initial_data?: string } }) {
  const toolName = decodeURIComponent(params.name)
  const tool = await getTool(toolName)
  
  if (!tool) return notFound()

  let initialData = {}
  if (searchParams.initial_data) {
     try {
         initialData = JSON.parse(searchParams.initial_data)
     } catch (e) {
         console.error("Failed to parse initial_data", e)
     }
  }

  return (
    <div className="min-h-screen bg-background pb-20 lg:pb-0 font-sans">
      {/* Header */}
      <div className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur-md px-6 py-4 flex items-center gap-4">
        <Link href="/tools">
           <Button variant="ghost" size="icon">
             <ChevronLeft className="w-5 h-5" />
           </Button>
        </Link>
        <h1 className="text-xl font-bold truncate">Run Tool: {tool.title || formatTitle(tool.name)}</h1>
      </div>

      <div className="p-6">
         <DynamicToolRunner tool={tool} initialData={initialData} />
      </div>
    </div>
  )
}
