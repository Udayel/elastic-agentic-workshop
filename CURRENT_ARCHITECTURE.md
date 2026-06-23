# Current Architecture - What's Actually Implemented

**Status:** Working without AgentCore Runtime  
**Last Updated:** 2026-06-23

---

## What's Actually Running

The current implementation works **WITHOUT** AgentCore Runtime or MCP server deployment. The agent calls Elasticsearch directly.

### Actual Architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                         User (You)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Terminal / REPL
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    main.py (REPL Interface)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              HybridCustomerSupportAgent                          │
│              (agents/hybrid_customer_support.py)                 │
│                                                                   │
│  Components:                                                     │
│  ✓ Strands Agent base class                                     │
│  ✓ AgenticBuilder context management (Elasticsearch)            │
│  ✓ 8 customer support tools                                     │
│  ✓ Conversation memory                                          │
│  ✓ Tool execution tracking                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Direct API calls
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Tool Functions                               │
│              (agents/customer_support_tools.py)                  │
│                                                                   │
│  ✓ hybrid_search_kb()                                           │
│  ✓ get_order_status()                                           │
│  ✓ search_products()                                            │
│  ✓ check_inventory()                                            │
│  ✓ elastic_rerank_results()                                     │
│  ✓ create_support_ticket()                                      │
│  ✓ update_preferences()                                         │
│  ✓ send_notification()                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Elasticsearch Python Client
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  Elasticsearch Cluster                           │
│                                                                   │
│  URL: your-deployment.es.us-east-1.aws.elastic.cloud           │
│  Auth: API Key from config/.env                                 │
│                                                                   │
│  Indices:                                                        │
│  ✓ customer-kb (knowledge base)                                 │
│  ✓ customer-orders (order tracking)                             │
│  ✓ customer-products (product catalog)                          │
│  ✓ customer-tickets (support tickets)                           │
│  ✓ customer-interactions (conversation logs)                    │
│  ✓ customer-notifications (notifications)                       │
│  ✓ agenticbuilder-context (session context)                     │
│  ✓ agenticbuilder-tools (tool statistics)                       │
│  ✓ agenticbuilder-executions (execution logs)                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## What's Working Right Now

### ✅ Fully Functional:

1. **Hybrid Agent** (`agents/hybrid_customer_support.py`)
   - Extends Strands Agent base class
   - Direct Elasticsearch integration
   - 8 working tools
   - Context management via AgenticBuilder

2. **Tool Functions** (`agents/customer_support_tools.py`)
   - All 8 tools implemented
   - Direct Elasticsearch API calls
   - No MCP server needed

3. **AgenticBuilder Context** (Elasticsearch indices)
   - Session context storage
   - Conversation history tracking
   - Tool execution logging
   - Analytics and metrics

4. **Data Indices** (Elasticsearch)
   - Knowledge base with sample data
   - Products catalog
   - Orders tracking
   - All properly indexed

5. **REPL Interface** (`main.py`)
   - Interactive terminal interface
   - Session management
   - Analytics display
   - Command handling

---

## What's NOT Currently Deployed

### ❌ Optional Components (Not Required):

1. **AgentCore Runtime**
   - Not deployed
   - Not required for current functionality
   - MCP server can run standalone if needed

2. **MCP Server Container**
   - Code exists (`mcp/elastic_mcp_server.py`)
   - Not deployed to AgentCore
   - Not needed for direct Elasticsearch calls

3. **AgentCore Gateway**
   - Not configured
   - OAuth2 not required for local testing
   - Can be added later for production

4. **Cognito Authentication**
   - Setup script exists (`infra/cognito_setup.py`)
   - Not required for local development
   - Can be configured for production

5. **AWS Bedrock Integration**
   - Code references exist
   - Not required for basic agent functionality
   - Can be added for enhanced LLM capabilities

---

## How It Actually Works

### Current Flow:

```
1. User starts agent
   → python main.py

2. Agent initializes
   → Loads config from config/.env
   → Connects to Elasticsearch directly
   → Creates AgenticBuilder context manager
   → Registers 8 tools

3. User asks question
   → "What is your return policy?"

4. Agent processes
   → Strands Agent selects appropriate tool
   → Calls hybrid_search_kb() function directly
   → Function calls Elasticsearch API
   → Returns results

5. AgenticBuilder logs
   → Stores conversation in agenticbuilder-context
   → Logs execution in agenticbuilder-executions
   → Updates tool stats in agenticbuilder-tools

6. User gets response
   → "Our return policy allows returns within 30 days..."
```

---

## Configuration Required

### Minimal Setup (What You Need):

1. **Elasticsearch credentials** in `config/.env`:
   ```bash
   ES_URL=https://your-deployment.es.us-east-1.aws.elastic.cloud:443
   ES_API_KEY=your-api-key
   AWS_REGION=us-east-1
   ```

2. **Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Elasticsearch indices**:
   ```bash
   python infra/elasticsearch_setup.py
   python infra/seed_data.py
   ```

That's it! No AWS deployment, no containers, no MCP server needed.

---

## Code Architecture

### What's Actually Used:

```python
# agents/hybrid_customer_support.py
class HybridCustomerSupportAgent(Agent):
    def __init__(self):
        # Direct Elasticsearch connection
        self.es = Elasticsearch(
            self.es_url,
            api_key=self.es_api_key
        )
        
        # AgenticBuilder for context (uses Elasticsearch)
        self.context_manager = AgenticBuilderContext(self.es)
        
        # Strands Agent initialization
        super().__init__(
            name=name,
            tools=self._register_tools(),
            memory=ConversationMemory(...)
        )
    
    def _tool_hybrid_search_kb(self, query: str):
        # Direct Elasticsearch call
        response = self.es.search(
            index="customer-kb",
            body={...}
        )
        return results
```

**No MCP server, no AgentCore Gateway, just direct API calls.**

---

## Optional: Future Enhancements

### If You Want to Add AgentCore Later:

1. **Deploy MCP Server**:
   ```bash
   cd mcp
   docker build -t elastic-mcp-server .
   # Deploy to AgentCore Runtime (requires AWS setup)
   ```

2. **Configure Cognito**:
   ```bash
   python infra/cognito_setup.py
   ```

3. **Update Agent to Use MCP**:
   ```python
   # Enable MCP client
   self.mcp_client = MCPClient(
       gateway_url=self.mcp_gateway_url,
       token_provider=self._get_auth_token
   )
   ```

But **none of this is required** for the agent to work!

---

## Running the Agent (Actual Steps)

### Step 1: Configure
```bash
cp config/.env.example config/.env
# Edit config/.env with your Elasticsearch credentials
```

### Step 2: Setup Indices
```bash
python infra/elasticsearch_setup.py
python infra/seed_data.py
```

### Step 3: Run
```bash
python main.py
```

### Step 4: Test
```
> What is your return policy?
> Check status of order ORD-12345
> Show me wireless headphones
```

---

## What Each File Does

### Actually Used Files:

| File | Purpose | Required? |
|------|---------|-----------|
| `main.py` | REPL interface | ✅ Yes |
| `agents/hybrid_customer_support.py` | Main agent | ✅ Yes |
| `agents/customer_support_tools.py` | Tool functions | ✅ Yes |
| `infra/elasticsearch_setup.py` | Create indices | ✅ Yes |
| `infra/seed_data.py` | Load sample data | ✅ Yes |
| `config/.env` | Credentials | ✅ Yes |
| `requirements.txt` | Dependencies | ✅ Yes |

### Optional Files (Not Used in Current Flow):

| File | Purpose | Required? |
|------|---------|-----------|
| `mcp/elastic_mcp_server.py` | MCP server | ❌ No |
| `mcp/Dockerfile` | Container | ❌ No |
| `infra/cognito_setup.py` | OAuth2 | ❌ No |
| `agents/agentic_customer_support.py` | Alternate implementation | ❌ No |
| `agents/customer_support_agent.py` | Strands-only version | ❌ No |

---

## Dependencies Breakdown

### What's Actually Required:

```txt
# Core (Required)
elasticsearch==8.15.0          # ✅ Direct Elasticsearch calls
python-dotenv==1.0.1           # ✅ Load config/.env
boto3==1.34.70                 # ✅ Used by code (can remove if not using AWS)

# Agent Framework (Used)
strands-agents-sdk==1.2.0      # ✅ Agent base class
                               # Note: Not using MCPClient from Strands

# Optional (Can Remove)
mcp-client==0.4.0              # ❌ Not used (no MCP server)
fastmcp==0.3.0                 # ❌ Not used (no MCP server)
fastapi==0.109.0               # ❌ Not used (no web server)
uvicorn==0.27.0                # ❌ Not used (no web server)
```

---

## Simplified Architecture Diagram

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     ▼
┌────────────────┐
│   main.py      │
│   (Terminal)   │
└────┬───────────┘
     │
     ▼
┌─────────────────────────┐
│ HybridAgent             │
│ - Strands Agent         │
│ - Tool Functions        │
│ - AgenticBuilder        │
└────┬────────────────────┘
     │
     ▼
┌────────────────────────┐
│  Elasticsearch         │
│  - Direct API calls    │
│  - No middleware       │
└────────────────────────┘
```

**Simple and working!**

---

## Summary

### What You Actually Have:

✅ Working customer support agent  
✅ Direct Elasticsearch integration  
✅ 8 functional tools  
✅ Context persistence  
✅ Analytics and logging  
✅ Interactive REPL  

### What You DON'T Need:

❌ AgentCore Runtime  
❌ MCP server deployment  
❌ Cognito authentication  
❌ AWS container orchestration  
❌ OAuth2 gateway  

### To Run:

1. Configure Elasticsearch in `config/.env`
2. Create indices: `python infra/elasticsearch_setup.py`
3. Load data: `python infra/seed_data.py`
4. Run agent: `python main.py`

**That's it!** No complex AWS setup needed.

---

**See RUN_GUIDE.md for step-by-step instructions.**
