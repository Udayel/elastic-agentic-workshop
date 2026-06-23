# Production Setup with Strands, AgentBuilder & AgentCore

**Goal:** Build production-ready agentic system using Strands, Elastic AgentBuilder, and Amazon Bedrock AgentCore Runtime.

---

## Current Status

### ✅ What Works Right Now:

- Simple Customer Support Agent (`agents/simple_customer_support.py`)
- Direct Elasticsearch integration
- No external dependencies beyond `elasticsearch` package
- Run with: `python main.py`

### ❌ What's Missing for Full Production:

1. **Strands SDK** - Not available as public package
2. **AgentCore Runtime** - Needs AWS deployment
3. **MCP Server** - Needs containerization
4. **Elastic AgentBuilder** - Needs API integration

---

## Production Architecture Roadmap

###  Step 1: Use What Works Now

**Current working implementation:**

```bash
# Install dependencies
pip install -r requirements-minimal.txt

# Configure
cp config/.env.example config/.env
# Edit config/.env with your credentials

# Setup
python infra/elasticsearch_setup.py
python infra/seed_data.py

# Run
python main.py
```

**Agent:** `SimpleCustomerSupportAgent`
- Uses tool functions directly
- No external agent frameworks
- Works immediately

---

### Step 2: Add Elastic AgentBuilder

**Implementation:** `agents/elastic_agentbuilder_agent.py` (already created)

**Features:**
- Tools registered in Elasticsearch
- Query templates for each tool
- Agents defined in Elasticsearch
- Session management

**Run:**
```bash
python -c "
from agents.elastic_agentbuilder_agent import CustomerSupportAgentWithBuilder
agent = CustomerSupportAgentWithBuilder()
print(agent.handle_query('What is your return policy?'))
"
```

**Status:** ✅ Ready to use (no AWS deployment needed)

---

### Step 3: Deploy MCP Server to AgentCore Runtime

**Follow:** `AGENTCORE_DEPLOYMENT.md`

**Steps:**
1. Build Elastic MCP server container
2. Push to AWS ECR
3. Create AgentCore Runtime in AWS Console
4. Configure environment variables
5. Get Runtime ARN

**Time:** 30-60 minutes  
**Cost:** ~$170/month

**Benefits:**
- Session isolation
- AWS IAM security
- Observability/metrics
- Auto-scaling

---

### Step 4: Integrate Strands SDK (Custom)

Since Strands is not a public package, you have two options:

#### Option A: Mock Strands Interface

Create a minimal Strands-like interface:

```python
# agents/strands_mock.py
class Agent:
    """Mock Strands Agent base class"""
    def __init__(self, name, tools, memory):
        self.name = name
        self.tools = tools
        self.memory = memory
    
    def run(self, query):
        # Implement tool selection logic
        pass

class Tool:
    """Mock Strands Tool"""
    def __init__(self, name, description, function, parameters):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters

class MCPClient:
    """Mock MCP Client"""
    def __init__(self, gateway_url, token_provider):
        self.gateway_url = gateway_url
        self.token_provider = token_provider
    
    async def call_tool(self, tool_name, arguments):
        # Implement MCP protocol
        pass

class ConversationMemory:
    """Mock Conversation Memory"""
    def __init__(self, namespace, max_turns):
        self.namespace = namespace
        self.max_turns = max_turns
        self.history = []
```

#### Option B: Use Real Strands

If you have access to Strands:

1. Get Strands SDK from vendor
2. Install: `pip install /path/to/strands-sdk.whl`
3. Use `hybrid_customer_support.py` (already created)

---

##  Recommended Path

### For Testing/Development (Right Now):

```bash
# Use simple agent
python main.py
```

Uses: `SimpleCustomerSupportAgent`
- No external frameworks
- Direct Elasticsearch
- Works immediately

---

### For Production (Phase 1):

```bash
# Use AgentBuilder
python -c "
from agents.elastic_agentbuilder_agent import CustomerSupportAgentWithBuilder
agent = CustomerSupportAgentWithBuilder()

# Test
queries = [
    'What is your return policy?',
    'Check status of order ORD-12345',
    'Show me wireless headphones'
]

for q in queries:
    print(f'Q: {q}')
    print(f'A: {agent.handle_query(q)}')
    print()
"
```

Uses: `CustomerSupportAgentWithBuilder`
- Elastic AgentBuilder for tool registry
- Query templates in Elasticsearch
- No AWS deployment needed

---

### For Production (Phase 2 - Full Stack):

1. **Deploy MCP Server:**
   ```bash
   ./deploy_elastic_mcp.sh
   ```

2. **Create AgentCore Runtime** in AWS Console

3. **Use AgentCore Client:**
   ```python
   from agentcore_client import AgentCoreClient
   
   client = AgentCoreClient(
       runtime_arn="arn:aws:bedrock:us-east-1:123:agent-runtime/elastic-mcp"
   )
   
   await client.search_elasticsearch("return policy")
   ```

---

## What You Can Do Right Now

### Option 1: Test Simple Agent (Fastest)

```bash
# 1. Check you have data
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-kb/_count"

# 2. Run agent
python main.py

# 3. Test queries
> What is your return policy?
> Check status of order ORD-12345
> Show me wireless headphones
```

---

### Option 2: Test AgentBuilder Implementation

```bash
# Run AgentBuilder agent directly
python agents/elastic_agentbuilder_agent.py
```

This will:
- Register tools in Elasticsearch
- Register agent in Elasticsearch  
- Run 4 test queries
- Show results

---

### Option 3: Deploy Full Stack

Follow `AGENTCORE_DEPLOYMENT.md` to:
1. Build MCP server container
2. Deploy to AgentCore Runtime
3. Use AWS authentication
4. Get full observability

---

## Summary

**Current Working Options:**

| Implementation | Complexity | AWS Required | Works Now |
|----------------|------------|--------------|-----------|
| SimpleCustomerSupportAgent | Low | No | ✅ Yes |
| ElasticAgentBuilderAgent | Medium | No | ✅ Yes |
| AgentCore + MCP | High | Yes | ⚠️ Needs deployment |
| Strands + AgentCore | High | Yes | ❌ Needs Strands SDK |

**Recommendation:**

1. **Start with:** `SimpleCustomerSupportAgent` (working now)
2. **Upgrade to:** `ElasticAgentBuilderAgent` (Elastic-native)
3. **Deploy:** AgentCore Runtime when ready for production

---

## Next Steps

### Right Now:

```bash
# Test the simple agent
python main.py
```

### When Ready:

```bash
# Test AgentBuilder
python agents/elastic_agentbuilder_agent.py
```

### For Production:

```bash
# Deploy to AgentCore
./deploy_elastic_mcp.sh
# Then follow AGENTCORE_DEPLOYMENT.md
```

---

**All implementations are ready in the repository!** Choose based on your needs.
