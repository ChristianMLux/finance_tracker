# AI-Powered Personal Finance Tracker (Universal Financial Advisor)

A state-of-the-art, full-stack application that transforms from a simple expense tracker into a **Universal Financial Advisor**. It features a self-extending AI architecture that dynamicially generates, audits, and executes financial tools in secure sandboxes.

## 🚀 Overview: The Finance Foundry

This project implements a unique **Dynamic Tool Retrieval** architecture inspired by the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). While traditional agents use a fixed set of tools, this system can learn and build new capabilities on demand.

### Key Capabilities
- **Expense Intelligence**: Natural language tracking and categorization.
- **Dynamic Math**: On-the-fly generation of calculators for mortgages, taxes, and compound interest.
- **Real-Time Data**: Integration with `yfinance` and DuckDuckGo for live stock prices and news sentiment.
- **Evidence-Based Answers**: All agent claims are grounded in specific data points and assumption-logging.

## 🛠️ Tech Stack

- **Frontend**: Next.js 15+ (App Router), Tailwind CSS, Shadcn UI
- **Backend**: FastAPI, SQLAlchemy (Async), SQLite
- **AI Runtimes**: 
  - **OpenRouter API**: Powering `Gemini 3 Flash` & `Preview` models.
  - **E2B Code Interpreter**: Secure, isolated Firecracker VMs for executing generated tools.
- **Libraries**: `yfinance`, `duckduckgo-search`, `pandas`, `mcp-python-sdk` (blueprint integration).

## ⚙️ Setup Instructions

### 1. Prerequisites
- Node.js (v18+) & Python (3.10+)
- [OpenRouter API Key](https://openrouter.ai/)
- [E2B API Key](https://e2b.dev/) (Required for dynamic tool execution)

### 2. Environment Configuration
Create a `.env` file in the root based on `env.example`:
```bash
OPENROUTER_API_KEY=your_openrouter_key
E2B_API_KEY=your_e2b_key
NEXT_PUBLIC_API_URL=http://localhost:8000
LLM_MODEL=google/gemini-3-flash-preview
```

### 3. Backend & Tooling
```bash
# Setup environment
python -m venv .venv
source .venv/Scripts/activate  # Windows

# Install & Seed
pip install -r backend/requirements.txt
python backend/seed_data.py

# Run
uvicorn backend.main:app --reload
```

### 4. Frontend
```bash
npm install && npm run dev
```

## 🤖 The Agent Ecosystem

The system uses a multi-agent hierarchy to ensure safety and accuracy:

1. **Manager Agent**: The central orchestrator. Classifies intent and routes to specialized agents.
2. **Architect Agent**: Writes high-quality, typed Python code to solve specific financial questions.
3. **Auditor Agent**: Performs a "Double Audit":
   - **Semantic Review**: LLM-based check for financial soundess (diversification, tax awareness).
   - **Runtime Validation**: Executes code in an E2B Sandbox to ensure it runs correctly before registration.
4. **Finance & Currency Agents**: Handles core CRUD and real-time exchange rate logic.

## 🛡️ Security & Sandboxing

All dynamically generated code is executed in **E2B Firecracker MicroVMs**. This provides:
- **Total Isolation**: Generated tools cannot access your local system or environment variables.
- **Safe External Access**: Allows tools to fetch stock data or news safely.
- **Ephemeral Runtimes**: Every calculation happens in a fresh, clean environment.

## 📁 Project Structure

- `backend/agents/`: Logic for Architect, Auditor, and specialized agents.
- `tests/`: Automated verification workflows for agent logic and sandbox safety.
- `infra/`: (Coming Soon) MCP Server deployment templates.


