# AI-Powered Personal Finance Tracker (Universal Financial Advisor)

A state-of-the-art, full-stack application that transforms from a simple expense tracker into a **Universal Financial Advisor**. It features a self-extending AI architecture that dynamically generates, audits, and executes financial tools in secure sandboxes.

## 🚀 Overview: The Finance Foundry

This project implements a unique **Dynamic Tool Retrieval** architecture inspired by the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). While traditional agents use a fixed set of tools, this system can learn and build new capabilities on demand.

### Key Capabilities
- **Expense Intelligence**: Natural language tracking and categorization.
- **Advanced Analytics**: Interactive dashboards for asset allocation (Donut) and monthly cashflow (Stacked Bar) using Recharts.
- **Generative UI**: AI Agents can now emit dynamic visual components (Charts, Tables) directly in the chat stream.
- **Dynamic Math**: On-the-fly generation of calculators for mortgages, taxes, and compound interest.
- **Real-Time Data**: Integration with `yfinance` and DuckDuckGo for live stock prices and news sentiment.
- **Evidence-Based Answers**: All agent claims are grounded in specific data points and assumption-logging.

## 🛠️ Tech Stack

- **Frontend**: Next.js 15+ (App Router), Tailwind CSS, Shadcn UI, Recharts (v3.x)
- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL (Google Cloud SQL) / SQLite
- **Authentication**: Firebase Auth (Google Sign-In)
- **Memory/State**: Firebase Firestore (Persistent Chat History & Agent Context)
- **AI Runtimes**: 
  - **OpenRouter API**: Powering `Gemini 3 Flash` & `Preview` models.
  - **E2B Code Interpreter**: Secure, isolated Firecracker VMs for executing generated tools.
- **Infrastructure**: 
  - **MCP**: Model Context Protocol for tool discovery.
  - **Docker**: Containerized deployment for the MCP server.
  - **Hybrid Database**: 
    - **PostgreSQL**: ACID-compliant storage for transactions/budgets.
    - **Firestore**: Real-time NoSQL storage for chat logs and agent memory.

## ⚙️ Setup Instructions

### 1. Prerequisites
- Node.js (v18+) & Python (3.10+)
- [OpenRouter API Key](https://openrouter.ai/)
- [E2B API Key](https://e2b.dev/) (Required for dynamic tool execution)
- [Firebase Project](https://console.firebase.google.com/) (For authentication)

### 2. Environment Configuration
Create a `.env` file in the root based on `env.example`:
```bash
# Core API Keys
OPENROUTER_API_KEY=your_openrouter_key
E2B_API_KEY=your_e2b_key
LLM_MODEL=google/gemini-3-flash-preview

# Backend config
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./finance.db

# Firebase configuration (Found in Project Settings)
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=...
```

### 3. Backend & Tooling
```bash
# Setup environment
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Install & Seed
pip install -r backend/requirements.txt
python backend/seed_data.py # only seed data if user exists

# Run Backend
uvicorn backend.main:app --reload --port 8000
```

### 4. Frontend
```bash
npm install && npm run dev
```

## 🔌 Infrastructure & Deployment

### Model Context Protocol (MCP) Server
The system includes an MCP server that exposes dynamically generated tools to other MCP-compatible clients (like Claude Desktop).

**Local Execution:**
```powershell
./infra/start_mcp_local.ps1
```

**Docker Deployment:**
The MCP server can be run in a container (especially useful for cloud deployments):
```bash
cd infra/mcp
docker-compose up --build
```

### Start Development Environment (Windows)
```powershell
./start_dev.ps1
```
after the first user is created, run the seed data script again

### Database Proxy (Cloud SQL)
If using Google Cloud SQL, you can use the proxy for local development access:
```powershell
./start_db_proxy.ps1
```
> [!NOTE]
> Ensure you have the `cloud_sql_proxy.exe` in your root directory and appropriate service account permissions.

## 🤖 The Agent Ecosystem

The system uses a multi-agent hierarchy to ensure safety and accuracy:

1. **Manager Agent**: The central orchestrator. Classifies intent, manages **Persistent Context** via Firestore, and processes **Generative UI** events (`ui_evt`).
2. **Architect Agent**: Writes high-quality, typed Python code to solve specific financial questions and generates structured data for visualizations.
3. **Auditor Agent**: Performs a "Double Audit":
   - **Semantic Review**: LLM-based check for financial soundness (diversification, tax awareness).
   - **Runtime Validation**: Executes code in an E2B Sandbox to ensure it runs correctly before registration.
4. **Finance & Analytics Agents**: Handles core CRUD and SQL-based data aggregation for reporting.

## 🛡️ Security & Sandboxing

All dynamically generated code is executed in **E2B Firecracker MicroVMs**. This provides:
- **Total Isolation**: Generated tools cannot access your local system or environment variables.
- **Safe External Access**: Allows tools to fetch stock data or news safely.
- **Ephemeral Runtimes**: Every calculation happens in a fresh, clean environment.

## 📁 Project Structure

- `backend/agents/`: Logic for Architect, Auditor, and specialized agents.
- `src/`: Next.js frontend application.
- `infra/mcp/`: Docker and configuration files for the MCP server.
- `tests/`: Automated verification workflows for agent logic and sandbox safety.


