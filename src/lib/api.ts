export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
console.log("API Configured URL:", API_URL);

export interface Expense {
  id: number;
  amount: number;
  category: string;
  description: string | null;
  date: string | null;
}

export interface ExpenseCreate {
  amount: number;
  category: string;
  description?: string;
  date?: string;
}

export interface Tool {
  id: number;
  name: string;
  title: string | null;
  description: string;
  is_active: number;
}

export const api = {
  getExpenses: async (token?: string, skip = 0, limit = 100): Promise<Expense[]> => {
    const headers: HeadersInit = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    const res = await fetch(`${API_URL}/expenses/?skip=${skip}&limit=${limit}`, { headers });
    if (!res.ok) throw new Error('Failed to fetch expenses');
    return res.json();
  },

  getTools: async (token?: string): Promise<Tool[]> => {
    const headers: HeadersInit = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    const res = await fetch(`${API_URL}/tools/`, { headers });
    if (!res.ok) throw new Error('Failed to fetch tools');
    return res.json();
  },

  createExpense: async (expense: ExpenseCreate, token?: string): Promise<Expense> => {
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_URL}/expenses/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(expense),
    });
    if (!res.ok) throw new Error('Failed to create expense');
    return res.json();
  },

  chat: async (message: string, token?: string): Promise<string> => {
     const headers: HeadersInit = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_URL}/chat?message=${encodeURIComponent(message)}`, {
      method: 'POST',
      headers
    });
    if (!res.ok) throw new Error('Failed to send message');
    const data = await res.json();
    return data.response;
  }
};
