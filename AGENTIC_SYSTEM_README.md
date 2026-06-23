# Real Agentic AI System - Production Architecture

**Maintainer:** uday@elastic.co  
**Architecture:** Strands Agents SDK + Amazon Bedrock AgentCore + Elastic MCP  
**Status:** Production-Ready Multi-Agent System

---

## System Overview

This is a **real agentic AI application** built with:

1. **Strands Agents SDK** - Agent framework with MCPClient
2. **Amazon Bedrock AgentCore Runtime** - Hosts Elastic MCP server
3. **Elastic MCP Server** - Context engine (ELSER, KNN, APM)
4. **AgentCore Gateway** - Exposes MCP tools to agents
5. **AgentCore Memory** - Persistent cross-session context
6. **AgentCore Identity** - Cognito OAuth2 + service-linked roles

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User / Client                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ OAuth2 (Cognito)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      Supervisor Agent                            │
│                   (Strands Agent SDK)                            │
│                                                                   │
│  - Routes requests to specialist agents                          │
│  - Maintains conversation context                                │
│  - Uses MCPClient for all tools                                  │
└──────┬──────────┬──────────┬──────────┬───────────┬─────────────┘
       │          │          │          │           │
       │          │          │          │           │
┌──────▼────┐ ┌──▼────┐ ┌───▼────┐ ┌──▼──────┐ ┌──▼──────────┐
│  Elastic  │ │  AWS  │ │ Memory │ │Security │ │ Integration │
│  Agent    │ │ Agent │ │ Agent  │ │ Agent   │ │ Agent       │
└──────┬────┘ └──┬────┘ └───┬────┘ └──┬──────┘ └──┬──────────┘
       │         │          │          │           │
       │         │          │          │           │
       └─────────┴──────────┴──────────┴───────────┘
                             │
                             │ HTTPS + Bearer Token
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Amazon Bedrock AgentCore Gateway                    │
│                                                                   │
│  - OAuth2 token validation (Cognito)                            │
│  - Request routing to AgentCore Runtime                         │
│  - Rate limiting & monitoring                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
┌───────────────▼──────────┐  ┌──────────▼──────────────────────┐
│  AgentCore Runtime       │  │  AgentCore Memory                │
│  (Container)             │  │                                  │
│                          │  │  - Persistent storage            │
│  ┌────────────────────┐ │  │  - Session management            │
│  │ Elastic MCP Server │ │  │  - Context retrieval             │
│  │                    │ │  │  - Namespace scoping             │
│  │ Port: 8000/mcp     │ │  │                                  │
│  │                    │ │  └──────────────────────────────────┘
│  │ Tools:             │ │
│  │ - ELSER search     │ │
│  │ - KNN vector       │ │
│  │ - Full-text search │ │
│  │ - Aggregations     │ │
│  │ - APM tracing      │ │
│  └────────┬───────────┘ │
│           │             │
└───────────┼─────────────┘
            │
            │ Elasticsearch API
            │
┌───────────▼─────────────────────────────────────────────────────┐
│             Elastic Cloud (Your Deployment)                      │
│                                                                   │
│  URL: https://udaytest-fe14f3.es.us-east-1.aws.elastic.cloud   │
│  Auth: API Key (secured in AWS Secrets Manager)                 │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │ Elasticsearch   │  │ ELSER v2 Model  │  │ APM Server      ││
│  │                 │  │                 │  │                 ││
│  │ Indices:        │  │ - Semantic      │  │ - Distributed   ││
│  │ - travel-*      │  │ - Cross-lingual │  │   tracing       ││
│  │ - agent-state   │  │ - Zero-shot     │  │ - Performance   ││
│  │ - conversations │  │                 │  │   monitoring    ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Architecture

### Supervisor Agent (supervisor.py)
```python
Responsibilities:
- Receives user requests
- Determines which specialist agent to route to
- Maintains conversation context
- Aggregates results from multiple agents
- Uses AgentCore Memory for session persistence

Routing Logic:
- Elastic queries → ElasticAgent
- AWS operations → AWSAgent
- Memory operations → MemoryAgent
- Security/auth → SecurityAgent
```

### Specialist Agents

**ElasticAgent (elastic_agent.py)**
```python
Tools via MCP:
- elasticsearch_search (full-text)
- elasticsearch_elser_search (semantic)
- elasticsearch_knn_search (vector)
- elasticsearch_aggregation
- apm_capture_transaction

Example:
User: "Find hotels in Tokyo with modern technology"
ElasticAgent: Uses ELSER semantic search
Result: Finds "high-tech accommodations", "smart hotels"
```

**AWSAgent (aws_agent.py)**
```python
Tools:
- invoke_bedrock_model
- cloudwatch_put_metric
- s3_get_object
- s3_put_object
- get_secret_value

Example:
User: "Analyze costs for last month"
AWSAgent: Queries CloudWatch metrics
Result: Returns cost breakdown
```

**MemoryAgent (memory_agent.py)**
```python
Tools:
- agentcore_memory_store
- agentcore_memory_recall
- agentcore_memory_delete

Example:
User: "Remember I prefer window seats"
MemoryAgent: Stores in AgentCore Memory
Result: Retrieved in future conversations
```

**SecurityAgent (security_agent.py)**
```python
Tools:
- cognito_get_token
- cognito_refresh_token
- validate_session

Example:
System: Needs to call MCP server
SecurityAgent: Gets OAuth2 token from Cognito
Result: Valid bearer token for API calls
```

---

## File Structure

```
elastic-agentic-workshop/
├── agents/
│   ├── supervisor.py              # Main routing agent
│   ├── elastic_agent.py           # Elastic search specialist
│   ├── aws_agent.py               # AWS services specialist
│   ├── memory_agent.py            # AgentCore Memory specialist
│   ├── security_agent.py          # Cognito/OAuth specialist
│   └── integration_agent.py       # Strands/external APIs
│
├── mcp/
│   ├── elastic_mcp_server.py      # FastMCP server
│   ├── Dockerfile                 # AgentCore Runtime container
│   └── requirements.txt           # MCP dependencies
│
├── infra/
│   ├── agentcore_deploy.py        # Deploy AgentCore components
│   ├── cognito_setup.py           # Setup Cognito for OAuth
│   └── elastic_seed.py            # Seed Elasticsearch data
│
├── config/
│   ├── .env                       # Environment variables (SECURED)
│   ├── .env.example               # Template
│   └── agentcore.json             # AgentCore CLI config
│
├── main.py                        # Entry point (REPL)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Security Architecture

### 1. No Hardcoded Credentials

**Elastic:**
```bash
# Stored in .env (gitignored)
ES_URL=https://...
ES_API_KEY=...

# Loaded via:
from dotenv import load_dotenv
es_url = os.getenv("ES_URL")
```

**AWS:**
```bash
# Uses aws configure (IAM credentials)
AWS_REGION=us-east-1

# Or IAM service-linked role:
SERVICE_ROLE_ARN=arn:aws:iam::...
```

### 2. OAuth2 Flow (Cognito)

```
1. User authenticates with Cognito
2. Receives JWT access token
3. Token included in all MCP requests:
   Authorization: Bearer <token>
4. MCP server validates JWT
5. Requests processed if valid
```

### 3. Service-Linked Roles

```python
# AgentCore Runtime uses service role
agentcore.create_agent_runtime(
    runtime_id="travel-agent-runtime",
    execution_role_arn=service_role_arn
)

# Permissions:
# - Read from Secrets Manager
# - Write to CloudWatch Logs
# - No admin access
```

---

## Deployment Steps

### Prerequisites

```bash
# 1. AWS credentials configured
aws configure
# Access Key: (from IAM)
# Secret Key: (from IAM)
# Region: us-east-1

# 2. Elastic deployment ready
# URL: <Enter your URL>
# API Key: <Enter your apikey>
# 3. Python 3.11+
python3 --version
```

### Step 1: Setup Cognito

```bash
cd infra
python3 cognito_setup.py

# This creates:
# - User Pool
# - App Client
# - Domain
# - Test user
# Updates config/.env automatically
```

### Step 2: Deploy AgentCore Components

```bash
python3 agentcore_deploy.py

# This creates:
# - AgentCore Runtime
# - AgentCore Gateway
# - AgentCore Memory
# - Service-linked IAM role
```

### Step 3: Build & Deploy MCP Server

```bash
cd ../mcp

# Build Docker image
docker build -t elastic-mcp-server:latest .

# Push to ECR (or run locally)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag elastic-mcp-server:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/elastic-mcp-server:latest

docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/elastic-mcp-server:latest

# Deploy to AgentCore Runtime
aws agentcore deploy-runtime \
  --runtime-id travel-agent-runtime \
  --image <account-id>.dkr.ecr.us-east-1.amazonaws.com/elastic-mcp-server:latest \
  --port 8000
```

### Step 4: Seed Elasticsearch Data

```bash
cd ../infra
python3 elastic_seed.py

# Seeds:
# - travel-cities index
# - travel-hotels index
# - Sample ELSER data
```

### Step 5: Install Agent Dependencies

```bash
cd ..
pip3 install -r requirements.txt
```

### Step 6: Run Supervisor Agent (REPL)

```bash
python3 main.py

# Interactive REPL:
> Plan a 5-day Tokyo trip for tech enthusiasts

# Agent flow:
# 1. Supervisor receives request
# 2. Routes to ElasticAgent
# 3. ElasticAgent calls MCP server
# 4. MCP server uses ELSER search
# 5. Results returned to Supervisor
# 6. Supervisor formats response
# 7. User receives itinerary
```

---

## MCP Protocol Implementation

### Tools List Endpoint

```bash
GET /mcp/tools/list
Authorization: Bearer <cognito-token>

Response:
{
  "tools": [
    {
      "name": "elasticsearch_elser_search",
      "description": "Semantic search using ELSER v2",
      "inputSchema": {
        "type": "object",
        "properties": {
          "index": {"type": "string"},
          "query_text": {"type": "string"}
        },
        "required": ["index", "query_text"]
      }
    },
    ...
  ]
}
```

### Tool Call Endpoint

```bash
POST /mcp/tools/call
Authorization: Bearer <cognito-token>
Content-Type: application/json

{
  "name": "elasticsearch_elser_search",
  "arguments": {
    "index": "travel-cities",
    "query_text": "romantic destination with great food"
  }
}

Response:
{
  "content": [{
    "type": "text",
    "text": "{\"total\": 3, \"hits\": [{\"id\": \"paris\", ...}]}"
  }],
  "isError": false
}
```

---

## Agent Communication Flow

### Example: "Plan a Tokyo trip"

```
1. User Input
   └─> Supervisor Agent

2. Supervisor Analysis
   - Understands: trip planning request
   - Decides: Need Elastic search + Memory recall
   - Routes to: ElasticAgent, MemoryAgent

3. Parallel Execution
   ┌─> ElasticAgent
   │   └─> MCPClient.call("elasticsearch_elser_search", {
   │         index: "travel-cities",
   │         query_text: "Tokyo attractions technology"
   │       })
   │   └─> AgentCore Gateway
   │       └─> MCP Server (port 8000)
   │           └─> Elasticsearch ELSER
   │               └─> Returns: Akihabara, Odaiba, etc.
   │
   └─> MemoryAgent
       └─> AgentCore Memory.recall(session_id)
           └─> Returns: User prefers tech, budget: $5000

4. Result Aggregation
   - Supervisor combines:
     • Elastic search results
     • User preferences from memory
   - Generates coherent plan

5. Memory Storage
   - Supervisor calls MemoryAgent
   - Stores conversation in AgentCore Memory
   - Session ID: preserved for next turn

6. Response to User
   - Formatted itinerary
   - Budget breakdown
   - Hotel recommendations
```

---

## Production Monitoring

### APM Traces

```python
# Automatic tracing via Elastic APM
from elastic_apm import instrument
instrument()

# Every agent call traced:
# - Supervisor → ElasticAgent
# - ElasticAgent → MCP Server
# - MCP Server → Elasticsearch
# - End-to-end latency
# - Error tracking
```

### CloudWatch Metrics

```python
# Custom metrics
cloudwatch.put_metric_data(
    Namespace='TravelAgent',
    MetricData=[{
        'MetricName': 'AgentInvocations',
        'Value': 1,
        'Unit': 'Count',
        'Dimensions': [{
            'Name': 'AgentType',
            'Value': 'ElasticAgent'
        }]
    }]
)
```

### AgentCore Monitoring

```bash
# Built-in dashboards
aws agentcore get-runtime-metrics \
  --runtime-id travel-agent-runtime

# Metrics:
# - Request count
# - Latency p50/p95/p99
# - Error rate
# - Token usage
```

---

## Cost Breakdown

### AgentCore Runtime
- Container: $0.10/hour
- Gateway: $0.05/hour
- Memory: $0.01/GB-hour
**Total**: ~$3.60/day

### Elastic Cloud
- Your deployment: Existing cost
- API calls: Included

### AWS Services
- Cognito: $0.0055/MAU (first 50K free)
- Secrets Manager: $0.40/secret/month
- CloudWatch: $0.30/GB logs
**Total**: ~$5/month

### Total Cost
- Development: ~$110/month
- Production: ~$300/month (with HA)

---

## Testing

### Unit Tests

```bash
pytest tests/test_elastic_agent.py -v
pytest tests/test_mcp_server.py -v
pytest tests/test_supervisor.py -v
```

### Integration Tests

```bash
# Test MCP server
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/mcp/tools/list

# Test agent flow
python3 tests/test_end_to_end.py
```

### Load Tests

```bash
# Simulate 100 concurrent users
locust -f tests/load_test.py --users 100
```

---

## Maintenance

### Update MCP Server

```bash
cd mcp
docker build -t elastic-mcp-server:v1.1.0 .
docker push <ecr-url>/elastic-mcp-server:v1.1.0

aws agentcore update-runtime \
  --runtime-id travel-agent-runtime \
  --image <ecr-url>/elastic-mcp-server:v1.1.0
```

### Rotate Credentials

```bash
# Rotate Elastic API key
# 1. Generate new key in Kibana
# 2. Update Secrets Manager
aws secretsmanager update-secret \
  --secret-id elastic-api-key \
  --secret-string "new-key-here"

# 3. Restart MCP server (auto-reads new value)
```

### Scale AgentCore Runtime

```bash
aws agentcore update-runtime \
  --runtime-id travel-agent-runtime \
  --instance-count 3 \
  --instance-type c6i.xlarge
```

---

## Troubleshooting

### MCP Server Not Responding

```bash
# Check logs
aws logs tail /aws/agentcore/travel-agent-runtime --follow

# Check container status
aws agentcore describe-runtime --runtime-id travel-agent-runtime

# Test connectivity
curl http://localhost:8000/health
```

### OAuth Token Invalid

```bash
# Refresh token
python3 -c "from agents.security_agent import SecurityAgent; \
  agent = SecurityAgent(); \
  token = agent.get_fresh_token(); \
  print(token)"
```

### Elasticsearch Connection Failed

```bash
# Test directly
curl -H "Authorization: ApiKey $ES_API_KEY" $ES_URL

# Check API key
# Regenerate in Kibana if expired
```

---

## Next Steps

1. **Deploy to production**
   - Multi-region AgentCore Runtime
   - High availability configuration
   - Auto-scaling policies

2. **Add more agents**
   - BookingAgent (Strands integration)
   - AnalyticsAgent (data insights)
   - NotificationAgent (AgenticBuilder)

3. **Build UI**
   - Web interface for REPL
   - Mobile app integration
   - Voice interface (Alexa/Google)

4. **Advanced features**
   - Multi-agent collaboration
   - Reinforcement learning
   - Custom tool creation

---

## Support

**Maintainer:** uday@elastic.co  
**Repository:** https://github.com/Udayel/elastic-agentic-workshop  
**Documentation:** See individual files for detailed implementation

---

**This is a real agentic system** - not a UI wrapper. Agents autonomously:
- Route requests intelligently
- Select appropriate tools
- Combine information from multiple sources
- Maintain context across sessions
- Adapt to user preferences
- Learn from interactions

All secured with OAuth2, service-linked roles, and no hardcoded credentials.
