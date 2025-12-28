import { useState, useEffect } from 'react';
import { collection, query, orderBy, onSnapshot } from 'firebase/firestore';
import { db } from '@/lib/firebase/firebase';
import { useAuth } from '@/context/AuthContext';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: unknown; // Firestore Timestamp
  timestamp?: unknown;
}

export function useChatHistory(chatId: string = 'default') {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      setMessages([]);
      setLoading(false);
      return;
    }

    if (!db) {
        console.error("Firestore not initialized");
        setError("Firestore not initialized");
        return;
    }

    const messagesRef = collection(db, 'users', user.uid, 'chats', chatId, 'messages');
    console.log(`[ChatHistory] Listening to: users/${user.uid}/chats/${chatId}/messages`);
    const q = query(messagesRef, orderBy('timestamp', 'asc'));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      console.log(`[ChatHistory] Snapshot received. Docs: ${snapshot.docs.length}, Empty: ${snapshot.empty}`);
      const msgs: Message[] = snapshot.docs.map(doc => {
          const data = doc.data();
          // console.log("Doc:", doc.id, data); 
          return {
            id: doc.id,
            ...data
          } as Message
      });
      console.log(`[ChatHistory] State Updating with ${msgs.length} messages`);
      setMessages(msgs);
      setLoading(false);
    }, (err) => {
      console.error("[ChatHistory] Firestore Error:", err);
      setError(err.message);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [user, chatId]);

  return { messages, loading, error };
}
