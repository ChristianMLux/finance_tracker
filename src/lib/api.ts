const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

export const api = {
  getExpenses: async (skip = 0, limit = 100): Promise<Expense[]> => {
    const res = await fetch(`${API_URL}/expenses/?skip=${skip}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch expenses');
    return res.json();
  },

  createExpense: async (expense: ExpenseCreate): Promise<Expense> => {
    const res = await fetch(`${API_URL}/expenses/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(expense),
    });
    if (!res.ok) throw new Error('Failed to create expense');
    return res.json();
  },

  chat: async (message: string): Promise<string> => {
    const res = await fetch(`${API_URL}/chat?message=${encodeURIComponent(message)}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to send message');
    const data = await res.json();
    return data.response;
  }
};
