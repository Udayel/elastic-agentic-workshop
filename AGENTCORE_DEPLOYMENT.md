# Deploying Elastic MCP Server to Amazon Bedrock AgentCore Runtime

Complete guide to deploy the Elastic MCP server and integrate with AgentCore Runtime.

**Reference:** https://www.elastic.co/search-labs/blog/elastic-mcp-server-amazon-bedrock-agentcore-runtime

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       Supervisor Agent                           │
│                    (Your Python Code)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ AWS SigV4 Auth
                             │ JSON-RPC 2.0 / SSE
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Amazon Bedrock AgentCore Runtime                    │
│                                                                   │
│  ┌─────────────────────────────────────────────────┐           │
│  │  Elastic MCP Server (Docker Container)          │           │
│  │                                                  │           │
│  │  - Dynamic tool discovery                       │           │
│  │  - Natural language → Elasticsearch queries     │           │
│  │  - Session management                            │           │
│  │  - IAM authentication                            │           │
│  └─────────────────────────┬───────────────────────┘           │
│                             │                                    │
│  Features:                  │                                    │
│  - Session isolation        │                                    │
│  - Memory management        │                                    │
│  - Observability/metrics    │                                    │
│  - Service-to-service auth  │                                    │
└────────────────────────────┼────────────────────────────────────┘
                              │
                              │ Elasticsearch API
                              │
┌─────────────────────────────▼──────────────────────────────────┐
│                    Elasticsearch Cluster                         │
│                                                                  │
│  - Indices (customer-kb, products, orders, etc.)               │
│  - ELSER semantic search                                        │
│  - KNN vector search                                            │
│  - Full-text search                                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- AWS Account with Bedrock access
- Elasticsearch deployment (Elastic Cloud or self-hosted)
- AWS CLI configured
- Docker installed
- Python 3.11+

---

## Step 1: Build and Push Elastic MCP Server Container

### Automated Script:

```bash
#!/bin/bash
# deploy_elastic_mcp.sh

set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPO_NAME="elastic-mcp-server"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "==================================================="
echo "Deploying Elastic MCP Server to AgentCore Runtime"
echo "==================================================="

# Step 1: Clone Elastic MCP Server repository
echo "Step 1: Downloading Elastic MCP Server..."
if [ ! -d "elastic-mcp-server" ]; then
    git clone https://github.com/elastic/elasticsearch-mcp-server.git elastic-mcp-server
fi
cd elastic-mcp-server

# Step 2: Build Docker container
echo "Step 2: Building Docker container..."
docker build -f Dockerfile-8000 -t ${ECR_REPO_NAME}:latest .

# Step 3: Create ECR repository
echo "Step 3: Creating ECR repository..."
aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} 2>/dev/null || \
aws ecr create-repository \
    --repository-name ${ECR_REPO_NAME} \
    --region ${AWS_REGION} \
    --image-scanning-configuration scanOnPush=true

# Step 4: Authenticate Docker to ECR
echo "Step 4: Authenticating Docker to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_URI}

# Step 5: Tag and push image
echo "Step 5: Pushing image to ECR..."
docker tag ${ECR_REPO_NAME}:latest ${ECR_URI}:latest
docker push ${ECR_URI}:latest

echo ""
echo "==================================================="
echo "✓ Container deployed to ECR"
echo "==================================================="
echo "ECR Image URI: ${ECR_URI}:latest"
echo ""
echo "Next steps:"
echo "1. Go to AWS Console → Bedrock → Agent Runtimes"
echo "2. Create new Agent Runtime with this image"
echo "3. Configure environment variables"
echo ""
```

### Run the script:

```bash
chmod +x deploy_elastic_mcp.sh
./deploy_elastic_mcp.sh
```

---

## Step 2: Configure AgentCore Runtime in AWS Console

### 2.1 Navigate to AWS Console

1. Go to AWS Console
2. Navigate to **Amazon Bedrock**
3. Click **Agent Runtimes** → **Create Agent Runtime**

### 2.2 Configure Runtime

**Basic Settings:**
- **Name:** `elastic-mcp-runtime`
- **Type:** Host Agent
- **Container Image:** `<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/elastic-mcp-server:latest`

**Protocol Settings:**
- **Protocol:** MCP (Model Context Protocol)
- **Inbound Identity:** IAM Username

**Service Role:**
```bash
# Create IAM role with this trust policy:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

# Attach policy:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    }
  ]
}
```

**Environment Variables:**
```bash
ELASTICSEARCH_URL=https://your-deployment.es.us-east-1.aws.elastic.cloud:443
ELASTICSEARCH_API_KEY=your-elasticsearch-api-key
ELASTICSEARCH_INDEX=customer-kb
```

### 2.3 Create Runtime

Click **Create** and wait for deployment (5-10 minutes).

### 2.4 Get Runtime ARN

After creation, click **View Invocation Code** to get:
```
arn:aws:bedrock:us-east-1:123456789012:agent-runtime/elastic-mcp-runtime
```

---

## Step 3: Update Python Client for AgentCore

### Install Dependencies:

```bash
pip install httpx aws-sigv4-auth
```

### Create AgentCore Client:

```python
# agentcore_client.py
import httpx
import json
from typing import Dict, Any, List
from aws_sigv4_auth import AWSSigV4Auth
import boto3

class AgentCoreClient:
    """Client for Amazon Bedrock AgentCore Runtime with Elastic MCP Server"""
    
    def __init__(self, runtime_arn: str, region: str = "us-east-1"):
        self.runtime_arn = runtime_arn
        self.region = region
        self.endpoint = f"https://bedrock-agent-runtime.{region}.amazonaws.com"
        
        # AWS SigV4 authentication
        session = boto3.Session()
        credentials = session.get_credentials()
        self.auth = AWSSigV4Auth(
            credentials,
            service="bedrock",
            region=region
        )
        
        self.client = httpx.AsyncClient()
        self.session_id = None
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        url = f"{self.endpoint}/agent-runtimes/{self.runtime_arn}/tools"
        
        response = await self.client.get(url, auth=self.auth)
        response.raise_for_status()
        
        return response.json()["tools"]
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call an MCP tool via AgentCore Runtime"""
        url = f"{self.endpoint}/agent-runtimes/{self.runtime_arn}/invoke"
        
        # JSON-RPC 2.0 request
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Include session ID if available
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        
        response = await self.client.post(
            url,
            json=payload,
            headers=headers,
            auth=self.auth
        )
        response.raise_for_status()
        
        # Extract session ID from response
        if "Mcp-Session-Id" in response.headers:
            self.session_id = response.headers["Mcp-Session-Id"]
        
        # Parse JSON-RPC response
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Tool call failed: {result['error']}")
        
        return result["result"]
    
    async def search_elasticsearch(
        self,
        query: str,
        index: str = "customer-kb"
    ) -> Dict[str, Any]:
        """Search Elasticsearch via MCP server"""
        return await self.call_tool(
            "elasticsearch_search",
            {
                "query": query,
                "index": index
            }
        )
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
```

---

## Step 4: Update Hybrid Agent to Use AgentCore

```python
# agents/agentcore_hybrid_agent.py
import asyncio
from agentcore_client import AgentCoreClient
from typing import Dict, Any

class AgentCoreHybridAgent:
    """Hybrid agent using AgentCore Runtime and Elastic MCP Server"""
    
    def __init__(
        self,
        runtime_arn: str,
        session_id: str = None,
        customer_id: str = None
    ):
        self.runtime_arn = runtime_arn
        self.session_id = session_id or f"session_{int(time.time())}"
        self.customer_id = customer_id or "anonymous"
        
        # Initialize AgentCore client
        self.agentcore = AgentCoreClient(runtime_arn)
        
        # Initialize local context manager (AgenticBuilder)
        # Context still stored in Elasticsearch locally
        self.es = Elasticsearch(
            os.getenv("ES_URL"),
            api_key=os.getenv("ES_API_KEY")
        )
        self.context_manager = AgenticBuilderContext(self.es)
    
    async def initialize(self):
        """Initialize agent and discover tools"""
        self.tools = await self.agentcore.list_tools()
        print(f"Discovered {len(self.tools)} tools from MCP server")
    
    async def handle_query(self, query: str) -> str:
        """Handle customer query using AgentCore"""
        
        # Load context from AgenticBuilder
        context = self.context_manager.get_context(self.session_id)
        
        # Determine which tool to use (simple logic for now)
        if "return policy" in query.lower() or "refund" in query.lower():
            tool_name = "elasticsearch_search"
            arguments = {
                "query": query,
                "index": "customer-kb"
            }
        elif "order" in query.lower():
            tool_name = "elasticsearch_get_document"
            # Extract order ID from query
            order_id = self._extract_order_id(query)
            arguments = {
                "index": "customer-orders",
                "id": order_id
            }
        else:
            tool_name = "elasticsearch_search"
            arguments = {
                "query": query,
                "index": "customer-kb"
            }
        
        # Call tool via AgentCore Runtime
        result = await self.agentcore.call_tool(tool_name, arguments)
        
        # Log execution in AgenticBuilder
        self.context_manager.log_tool_execution(
            session_id=self.session_id,
            tool_name=tool_name,
            input_params=arguments,
            output_result=result,
            status="success",
            execution_time_ms=0  # AgentCore handles timing
        )
        
        # Update context
        user_message = {
            "role": "user",
            "content": query,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response_text = self._format_response(result)
        
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in AgenticBuilder
        if not context:
            self.context_manager.store_context(
                session_id=self.session_id,
                agent_id="agentcore-hybrid",
                customer_id=self.customer_id,
                context_data={},
                conversation_history=[user_message, assistant_message]
            )
        else:
            context["conversation_history"].extend([user_message, assistant_message])
            self.context_manager.store_context(
                session_id=self.session_id,
                agent_id="agentcore-hybrid",
                customer_id=self.customer_id,
                context_data=context.get("context_data", {}),
                conversation_history=context["conversation_history"]
            )
        
        return response_text
    
    def _extract_order_id(self, query: str) -> str:
        """Extract order ID from query"""
        import re
        match = re.search(r'ORD-\d+', query)
        return match.group(0) if match else "ORD-12345"
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """Format MCP server response for user"""
        if "hits" in result:
            hits = result["hits"]["hits"]
            if hits:
                return hits[0]["_source"].get("content", "No content available")
        return str(result)
    
    async def close(self):
        """Cleanup"""
        await self.agentcore.close()
```

---

## Step 5: Update main.py for AsyncIO

```python
# main_agentcore.py
import asyncio
import os
from dotenv import load_dotenv
from agents.agentcore_hybrid_agent import AgentCoreHybridAgent

load_dotenv()

async def main():
    print("="*70)
    print("   CUSTOMER SUPPORT AGENT - AgentCore Runtime")
    print("   Elastic MCP Server + Amazon Bedrock")
    print("="*70)
    
    # Get runtime ARN from environment
    runtime_arn = os.getenv("AGENTCORE_RUNTIME_ARN")
    if not runtime_arn:
        print("Error: AGENTCORE_RUNTIME_ARN not set in config/.env")
        return
    
    # Initialize agent
    agent = AgentCoreHybridAgent(runtime_arn=runtime_arn)
    await agent.initialize()
    
    print("\nReady! Ask me anything...\n")
    
    while True:
        try:
            query = input("> ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit']:
                break
            
            response = await agent.handle_query(query)
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
    
    await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 6: Update config/.env

```bash
# Elasticsearch Configuration
ES_URL=https://your-deployment.es.us-east-1.aws.elastic.cloud:443
ES_API_KEY=your-api-key

# AWS Configuration
AWS_REGION=us-east-1

# AgentCore Runtime
AGENTCORE_RUNTIME_ARN=arn:aws:bedrock:us-east-1:123456789012:agent-runtime/elastic-mcp-runtime

# Application
LOG_LEVEL=INFO
ENVIRONMENT=production
```

---

## Running with AgentCore

```bash
# Run with AgentCore Runtime
python main_agentcore.py
```

**Output:**
```
======================================================================
   CUSTOMER SUPPORT AGENT - AgentCore Runtime
   Elastic MCP Server + Amazon Bedrock
======================================================================
Discovered 5 tools from MCP server
Ready! Ask me anything...

> What is your return policy?

Agent: Our return policy allows you to return items within 30 days...
```

---

## Benefits of AgentCore Runtime

1. **Session Isolation** - Each customer gets isolated environment
2. **Memory Management** - Persistent and session-state storage
3. **Observability** - Built-in logging and metrics
4. **Security** - IAM-based authentication and authorization
5. **Scalability** - Serverless, auto-scaling runtime
6. **Protocol Support** - MCP-compliant gateway

---

## Cost Comparison

### Without AgentCore (Current):
- Direct Elasticsearch calls: Free
- Total: ~$0/month (Elasticsearch cost only)

### With AgentCore Runtime:
- AgentCore Runtime: ~$100/month
- Container hosting: ~$50/month
- Data transfer: ~$20/month
- Total: ~$170/month + Elasticsearch

**Use AgentCore when you need:**
- Production-grade security
- Multi-tenant isolation
- Enterprise observability
- Managed scaling

---

## Next Steps

1. Deploy MCP server to AgentCore (Step 1-2)
2. Update agent code to use AgentCore client (Step 3-4)
3. Test with sample queries
4. Monitor via AWS CloudWatch
5. Scale as needed

---

**See:** https://www.elastic.co/search-labs/blog/elastic-mcp-server-amazon-bedrock-agentcore-runtime
