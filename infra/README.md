# Infrastructure & Deployment

This directory contains deployment templates and scripts for the **Finance Foundry** system, specifically the **Dynamic MCP Server**.

## 🚀 MCP Server Deployment

The MCP Server (`backend/mcp_server.py`) allows AI agents to dynamically retrieve and execute financial tools.

### 1. Local Execution (No Docker)

Use the provided PowerShell script to run the MCP server with your existing Python environment.

```powershell
./infra/start_mcp_local.ps1
```

This will start the server using Standard Input/Output (stdio), which is compatible with local MCP clients like **Claude Desktop**.

### 2. Docker Deployment

To run the MCP server in a container (e.g., for a continuously running backend service):

```bash
cd infra/mcp
docker-compose up --build
```

This setup:
- Builds a lightweight Python image.
- Installs dependencies from `../../backend/requirements.txt`.
- Runs the server (defaulting to stdio, but configurable via CMD).

## 📂 Structure

- **mcp/**: Docker configuration for the MCP Server.
- **start_mcp_local.ps1**: Quick-start script for local development.
