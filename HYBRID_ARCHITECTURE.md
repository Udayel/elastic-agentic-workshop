# Hybrid Customer Support Agent Architecture

**Version:** 2.0  
**Last Updated:** 2026-06-23  
**Maintainer:** uday@elastic.co

---

## Executive Summary

This document describes the **Hybrid Customer Support Agent** that combines:
- **Elastic AgenticBuilder** for context management, persistence, and analytics
- **Strands Agents SDK** for orchestration, tool execution, and agent framework

This architecture provides the best of both worlds: Elastic's powerful search and context capabilities with Strands' flexible agent orchestration.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Query                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              HybridCustomerSupportAgent                          │
│              (Extends Strands Agent)                             │
│                                                                   │
│  ┌─────────────────────┐         ┌─────────────────────┐       │
│  │  Strands Framework  │         │  AgenticBuilder     │       │
│  │  (Orchestration)    │◄────────┤  (Context)          │       │
│  │                     │         │                     │       │
│  │  - Agent base class │         │  - Session storage  │       │
│  │  - Tool execution   │         │  - Conversation log │       │
│  │  - Routing logic    │         │  - Analytics        │       │
│  │  - Memory mgmt      │         │  - Tool statistics  │       │
│  └──────────┬──────────┘         └──────────┬──────────┘       │
│             │                               │                   │
└─────────────┼───────────────────────────────┼───────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────────┐   ┌──────────────────────────────┐
│     Tool Functions          │   │   Elasticsearch Indices      │
│                             │   │                              │
│  - hybrid_search_kb()       │──▶│  - customer-kb               │
│  - get_order_status()       │──▶│  - customer-orders           │
│  - search_products()        │──▶│  - customer-products         │
│  - check_inventory()        │──▶│  - customer-tickets          │
│  - elastic_rerank_results() │──▶│  - customer-interactions     │
│  - create_support_ticket()  │──▶│  - agenticbuilder-context    │
│  - update_preferences()     │──▶│  - agenticbuilder-tools      │
│  - send_notification()      │──▶│  - agenticbuilder-executions │
└─────────────────────────────┘   └──────────────────────────────┘
```

---

## Component Breakdown

### 1. Strands Agents SDK Layer

**Purpose:** Agent orchestration and execution framework

**Responsibilities:**
- Agent lifecycle management
- Tool registration and execution
- Routing and decision making
- ConversationMemory management
- MCPClient integration (optional)

**Key Classes:**
```python
from strands import Agent, Tool, MCPClient, ConversationMemory

class HybridCustomerSupportAgent(Agent):
    def __init__(self, name, session_id, customer_id):
        # Initialize AgenticBuilder for context
        self.context_manager = AgenticBuilderContext(self.es)
        
        # Initialize Strands Agent
        super().__init__(
            name=name,
            tools=self._register_tools(),
            memory=ConversationMemory(...)
        )
```

### 2. Elastic AgenticBuilder Layer

**Purpose:** Context management, persistence, and analytics

**Responsibilities:**
- Store conversation history
- Manage session state
- Track tool usage
- Log execution metrics
- Provide analytics dashboard

**Key Indices:**

**agenticbuilder-context**
```json
{
  "session_id": "session_123",
  "agent_id": "customer-support",
  "customer_id": "CUST-001",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is your return policy?",
      "timestamp": "2026-06-23T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Our return policy...",
      "timestamp": "2026-06-23T10:30:02Z"
    }
  ],
  "preferences": {
    "language": "en",
    "notification_channel": "email"
  }
}
```

**agenticbuilder-tools**
```json
{
  "tool_id": "hybrid_search_kb",
  "name": "hybrid_search_kb",
  "usage_count": 127,
  "success_rate": 0.98,
  "avg_latency_ms": 45.3,
  "last_used": "2026-06-23T10:30:00Z"
}
```

**agenticbuilder-executions**
```json
{
  "execution_id": "exec_1719143000123",
  "session_id": "session_123",
  "tool_name": "hybrid_search_kb",
  "input": {"query": "return policy"},
  "output": {"results_count": 3},
  "status": "success",
  "execution_time_ms": 42.5,
  "timestamp": "2026-06-23T10:30:00Z"
}
```

### 3. Tool Functions Layer

**Purpose:** Reusable tool implementations

**Location:** `agents/customer_support_tools.py`

**Tools:**

1. **hybrid_search_kb** - BM25 + ELSER semantic search
2. **get_order_status** - Order lookup
3. **search_products** - Product search with ELSER
4. **check_inventory** - Inventory checking
5. **elastic_rerank_results** - LTR reranking
6. **create_support_ticket** - Ticket creation
7. **update_preferences** - Context updates
8. **send_notification** - Notifications

### 4. Elasticsearch Storage Layer

**Purpose:** Data storage and search engine

**Indices:**

**Customer Support Data:**
- `customer-kb` - Knowledge base with ELSER embeddings
- `customer-orders` - Order tracking
- `customer-products` - Product catalog with ELSER
- `customer-tickets` - Support tickets
- `customer-interactions` - Interaction logs
- `customer-notifications` - Notification history

**AgenticBuilder Data:**
- `agenticbuilder-context` - Session context
- `agenticbuilder-tools` - Tool metadata
- `agenticbuilder-executions` - Execution logs

---

## Data Flow

### Query Processing Flow

```
1. User Input
   └─> main.py REPL

2. Agent Initialization
   └─> HybridCustomerSupportAgent.__init__()
       ├─> Load context from AgenticBuilder
       ├─> Initialize Strands Agent
       └─> Register tools

3. Query Processing
   └─> agent.handle_customer_query(query)
       ├─> Add message to context
       ├─> Call Strands Agent.run()
       │   ├─> Select appropriate tool(s)
       │   ├─> Execute tool function
       │   └─> Generate response
       ├─> Log execution in AgenticBuilder
       └─> Update context in Elasticsearch

4. Response
   └─> Return to user
```

### Context Management Flow

```
Session Start:
  └─> AgenticBuilder.get_context(session_id)
      ├─> If exists: Load from Elasticsearch
      └─> If new: Create empty context

During Conversation:
  └─> Each turn:
      ├─> Append user message to context
      ├─> Process with Strands Agent
      ├─> Append assistant message to context
      └─> Store in AgenticBuilder

Tool Execution:
  └─> Before execution: Start timer
  └─> Execute tool function
  └─> After execution:
      ├─> Log in agenticbuilder-executions
      └─> Update tool statistics

Session End:
  └─> Context persisted in Elasticsearch
  └─> Available for next session
```

---

## Key Features

### 1. Hybrid Search

Combines BM25 keyword search with ELSER semantic search:

```python
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "content": {
              "query": "return policy",
              "boost": 1.0
            }
          }
        },
        {
          "text_expansion": {
            "content_embedding": {
              "model_id": ".elser_model_2",
              "model_text": "return policy",
              "boost": 2.0
            }
          }
        }
      ]
    }
  }
}
```

**Benefits:**
- BM25 finds exact keyword matches
- ELSER finds semantic matches
- Boost controls relative importance

### 2. Learning to Rank Reranking

Uses Elastic LTR to rerank results:

```python
{
  "rescore": {
    "window_size": 50,
    "query": {
      "rescore_query": {
        "sltr": {
          "params": {"query": "return policy"},
          "model": "customer_support_reranker"
        }
      }
    }
  }
}
```

**Features:**
- Custom featureset (BM25, ELSER, recency, helpfulness)
- Trained model on judgment data
- Improves relevance by 20-30%

### 3. Context Persistence

Session context stored in Elasticsearch:

```python
context = {
  "conversation_history": [...],
  "preferences": {...},
  "context_data": {
    "current_order_id": "ORD-12345",
    "recent_searches": ["headphones", "cables"],
    "last_interaction": "2026-06-23T10:00:00Z"
  }
}
```

**Benefits:**
- Cross-session continuity
- Personalized responses
- Conversation history preserved

### 4. Tool Analytics

Track tool performance:

```python
{
  "tool_name": "hybrid_search_kb",
  "usage_count": 127,
  "success_rate": 0.98,
  "avg_latency_ms": 45.3
}
```

**Insights:**
- Most used tools
- Performance bottlenecks
- Error patterns
- Optimization opportunities

---

## Deployment

### Prerequisites

```bash
# 1. Elasticsearch deployment
ES_URL=https://your-deployment.es.us-east-1.aws.elastic.cloud:443
ES_API_KEY=your-api-key

# 2. Python 3.11+
python3 --version

# 3. Dependencies
pip install -r requirements.txt
```

### Setup Steps

**Step 1: Create Indices**

```bash
python infra/elasticsearch_setup.py
```

Creates all required indices with proper mappings.

**Step 2: Seed Sample Data**

```bash
python infra/seed_data.py
```

Populates indices with sample products, orders, and knowledge base articles.

**Step 3: Test Search**

```bash
# Test hybrid search
curl -X POST "$ES_URL/customer-kb/_search" \
  -H "Authorization: ApiKey $ES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "should": [
          {"match": {"content": "return policy"}},
          {
            "text_expansion": {
              "content_embedding": {
                "model_id": ".elser_model_2",
                "model_text": "return policy"
              }
            }
          }
        ]
      }
    }
  }'
```

**Step 4: Run Agent**

```bash
python main.py
```

Interactive REPL for testing the agent.

---

## Usage Examples

### Example 1: Knowledge Base Search

```
User: What is your return policy?

Agent Flow:
1. Strands Agent receives query
2. Selects hybrid_search_kb tool
3. Searches customer-kb with BM25 + ELSER
4. Returns relevant article
5. Logs execution in AgenticBuilder

Response: "Our return policy allows you to return items 
within 30 days of purchase..."
```

### Example 2: Order Status

```
User: Check status of order ORD-12345

Agent Flow:
1. Strands Agent receives query
2. Selects get_order_status tool
3. Queries customer-orders index
4. Returns order details
5. Updates context with current_order_id

Response: "Order ORD-12345 is currently shipped. 
Tracking: 1Z999AA10123456784. Estimated delivery: Jun 26."
```

### Example 3: Product Search

```
User: Show me wireless headphones under $100

Agent Flow:
1. Strands Agent receives query
2. Selects search_products tool
3. ELSER semantic search on customer-products
4. Filters by price < $100
5. Returns matching products

Response: "I found 2 wireless headphones under $100:
1. Wireless Bluetooth Headphones - $79.99 (in stock)
2. Budget Sport Earbuds - $49.99 (in stock)"
```

### Example 4: Create Support Ticket

```
User: I received a defective product and need help

Agent Flow:
1. Strands Agent detects issue requiring human
2. Selects create_support_ticket tool
3. Creates ticket in customer-tickets
4. Sentiment analysis (negative detected)
5. Sets priority to "high"

Response: "I've created support ticket TKT-001 with high 
priority. A specialist will contact you within 2 hours."
```

---

## Analytics Dashboard

Access analytics via REPL:

```bash
> analytics

AGENT ANALYTICS
========================================
Session ID: session_1719143000

Tool Usage Statistics:
----------------------------------------
  hybrid_search_kb
    Usage Count:   15
    Success Rate:  100.00%
    Avg Latency:   42.3ms

  get_order_status
    Usage Count:   3
    Success Rate:  100.00%
    Avg Latency:   18.5ms

  search_products
    Usage Count:   8
    Success Rate:  100.00%
    Avg Latency:   67.2ms
```

---

## Advantages of Hybrid Architecture

### Elastic AgenticBuilder Strengths

✓ **Context Management**
- Persistent session storage
- Cross-session continuity
- Elasticsearch-native

✓ **Analytics**
- Built-in tool tracking
- Execution logging
- Performance metrics

✓ **Search Capabilities**
- ELSER semantic search
- Hybrid BM25 + vector
- Learning to Rank

### Strands SDK Strengths

✓ **Agent Framework**
- Clean agent abstraction
- Tool registration
- Conversation memory

✓ **Orchestration**
- Multi-agent coordination
- Tool selection logic
- Routing capabilities

✓ **MCP Integration**
- AgentCore Gateway
- OAuth2 authentication
- Remote tool execution

### Combined Benefits

✓ Strands handles agent logic
✓ AgenticBuilder handles persistence
✓ Tools are reusable functions
✓ Analytics via Elasticsearch
✓ Scales horizontally
✓ Production-ready

---

## Performance Characteristics

### Latency Breakdown

**Typical Query:**
- Context retrieval: 5-10ms
- Tool execution: 30-100ms
- Context update: 5-10ms
- **Total: 40-120ms**

**ELSER Search:**
- Hybrid search: 40-80ms
- Reranking: +20-30ms
- **Total: 60-110ms**

### Scalability

**Horizontal:**
- Multiple agent instances
- Shared Elasticsearch cluster
- Session affinity not required

**Vertical:**
- Elasticsearch scales independently
- Agent instances scale independently
- No coupling between layers

---

## Monitoring

### Elasticsearch Metrics

```bash
GET agenticbuilder-executions/_search
{
  "aggs": {
    "avg_latency": {
      "avg": {"field": "execution_time_ms"}
    },
    "success_rate": {
      "terms": {"field": "status"}
    }
  }
}
```

### Tool Performance

```bash
GET agenticbuilder-tools/_search
{
  "sort": [{"usage_count": {"order": "desc"}}]
}
```

### Session Analytics

```bash
GET agenticbuilder-context/_search
{
  "aggs": {
    "avg_conversation_length": {
      "avg": {
        "script": "doc['conversation_history'].size()"
      }
    }
  }
}
```

---

## Future Enhancements

### Phase 1: Enhanced Intelligence
- Multi-turn conversation understanding
- Intent classification
- Entity extraction
- Sentiment-aware routing

### Phase 2: Advanced Search
- Vector embeddings (dense + sparse)
- Cross-lingual search
- Image search for products
- Voice query support

### Phase 3: Multi-Agent
- Supervisor agent routing
- Specialist agents (returns, technical, billing)
- Agent collaboration
- Escalation logic

### Phase 4: Production Features
- A/B testing framework
- Reinforcement learning
- Automated training data collection
- Real-time model updates

---

## Troubleshooting

### Issue: Context not persisting

**Symptoms:** Each query seems like first interaction

**Solution:**
```bash
# Check context index
GET agenticbuilder-context/_search
{
  "query": {"term": {"session_id": "YOUR_SESSION_ID"}}
}

# Verify context_manager initialization
# Ensure session_id is consistent
```

### Issue: Slow tool execution

**Symptoms:** Queries taking >1 second

**Solution:**
```bash
# Check tool statistics
GET agenticbuilder-tools/_search
{
  "sort": [{"avg_latency_ms": {"order": "desc"}}]
}

# Identify slow tools
# Check Elasticsearch query performance
# Add caching layer if needed
```

### Issue: Tools not found

**Symptoms:** "Tool X not registered" error

**Solution:**
```python
# Verify tool registration
agent = HybridCustomerSupportAgent(...)
print([tool.name for tool in agent.tools])

# Check tool_functions import
from agents.customer_support_tools import hybrid_search_kb
```

---

## Conclusion

The Hybrid Customer Support Agent combines:
- **Strands SDK** for agent orchestration
- **Elastic AgenticBuilder** for context and analytics
- **Elasticsearch** for search and storage

This architecture provides a production-ready, scalable, and observable customer support AI system.

**Repository:** https://github.com/Udayel/elastic-agentic-workshop  
**Maintainer:** uday@elastic.co  
**License:** Apache 2.0
