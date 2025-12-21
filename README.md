# AI-Powered Personal Finance Tracker

A modern, full-stack application for tracking expenses with integrated AI agents for financial assistance and currency conversion. Built as a hiring task for the Fullstack Developer role.

## 🚀 Overview

This project combines a robust **Next.js** frontend with a high-performance **FastAPI** backend to provide a seamless expense management experience. The core feature is a pair of AI agents capable of performing real actions through tool calling:
- **Finance Assistant**: Manages your local expense database (queries, additions, summaries).
- **Currency Converter**: Integrates with an external API for real-time exchange rates.

## 🛠️ Tech Stack

- **Frontend**: Next.js 15+ (App Router), Tailwind CSS, Shadcn UI
- **Backend**: FastAPI (Python 3.10+), SQLAlchemy (Async), SQLite
- **AI**: OpenRouter API (`google/gemini-3-flash-preview`)
- **Tools**: `httpx`, `aiosqlite`, `pydantic`

## ⚙️ Setup Instructions

### 1. Prerequisites
- Node.js (v18+)
- Python (3.10+)
- OpenRouter API Key

### 2. Environment Configuration
Create a `.env` file in the root directory based on `env.example`:
```bash
OPENROUTER_API_KEY=your_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Backend Setup
```bash
# Navigate to the project root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Seed the database with sample data
python backend/seed_data.py

# Start the FastAPI server
uvicorn backend.main:app --reload
```
The API will be available at [http://localhost:8000](http://localhost:8000). You can explore the interactive docs at `/docs`.

### 4. Frontend Setup
```bash
# In a new terminal, from the project root
npm install
npm run dev
```
The application will be running at [http://localhost:3000](http://localhost:3000).

## 🤖 AI Agents

### Finance Assistant
Ask questions about your spending or add new expenses naturally:
- *"How much did I spend on food this month?"*
- *"Add $50 for groceries today"*
- *"Summarize my spending in October"*

### Currency Converter
Get real-time conversions using the integrated tool:
- *"How much is 100 USD in EUR?"*
- *"What is a flight for 500 GBP in USD?"*

## 📁 Project Structure

- `backend/`: FastAPI application, agents logic, and database models.
- `src/`: Next.js frontend source (components, hooks, styles).
- `public/`: Static assets and project specification documents.
- `tests/`: Verification scripts and output logs.

---
*Created by Christian Lux as part of a Fullstack Developer Hiring Task.*
