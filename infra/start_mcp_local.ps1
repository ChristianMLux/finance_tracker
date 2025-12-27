# Script to start the MCP Server locally
$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ROOT_DIR = (Resolve-Path "$SCRIPT_DIR/..").Path

# Path to the virtual environment python
$PYTHON_EXEC = "$ROOT_DIR/.venv/Scripts/python.exe"

if (-not (Test-Path $PYTHON_EXEC)) {
    Write-Error "Virtual environment not found at $PYTHON_EXEC. Please run 'python -m venv .venv' and install requirements first."
}

# Add root to PYTHONPATH
$env:PYTHONPATH = $ROOT_DIR

Write-Host "Starting Finance Foundry MCP Server (Stdio Mode)..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray

# Run the server
& $PYTHON_EXEC -m backend.mcp_server
