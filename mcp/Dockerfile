# Elastic MCP Server - AgentCore Runtime Container
FROM python:3.11-slim

LABEL maintainer="elastic-agents@example.com"
LABEL description="Elastic MCP Server for Amazon Bedrock AgentCore Runtime"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY elastic_mcp_server.py .

# Create non-root user
RUN useradd -m -u 1000 mcpserver && \
    chown -R mcpserver:mcpserver /app

USER mcpserver

# Expose MCP server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run MCP server
CMD ["python", "elastic_mcp_server.py"]
