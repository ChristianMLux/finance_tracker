# Use an official lightweight Python image.
FROM python:3.10-slim

# Set working directory to /app
WORKDIR /app

# Install system dependencies if needed (e.g., git, gcc for some python libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
# We assume the build context is the project root, so we access backend/requirements.txt
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backend ./backend

# Copy the .env file if it exists, or expect environment variables to be passed
# For production, strictly pass ENV vars via docker-compose
# COPY .env . 

# Set Python path so 'backend' module is resolvable
ENV PYTHONPATH=/app

# Expose port if using SSE (8000 is default for FastMCP SSE)
EXPOSE 8000

# Default command: Run the MCP Server
# Note: By default this runs in stdio mode. 
# To run in SSE mode, you likely need a different entrypoint or flag if supported by the script.
CMD ["python", "backend/mcp_server.py"]
