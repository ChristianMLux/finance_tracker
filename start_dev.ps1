# start_dev.ps1

# 1. Start Proxy (optional, auskommentieren wenn lokal SQLite genutzt wird)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "./start_db_proxy.ps1"

# 2. Start Backend (Uvicorn)
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\.venv\Scripts\activate; uvicorn backend.main:app --reload --port 8000"

# 3. Start Frontend (Next.js)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

# 4. Start MCP Server (Optional)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "./infra/start_mcp_local.ps1"