"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ChatInterface } from "@/components/ChatInterface";

function ChatContent() {
  const searchParams = useSearchParams();
  const message = searchParams.get("message");
  const initialInput = message ? decodeURIComponent(message) : undefined;

  return (
    <div className="flex h-[calc(100vh-65px)] flex-col">
      <div className="flex-1 p-4 md:p-6 lg:p-8">
         <ChatInterface initialInput={initialInput} />
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center">Loading chat...</div>}>
      <ChatContent />
    </Suspense>
  );
}
