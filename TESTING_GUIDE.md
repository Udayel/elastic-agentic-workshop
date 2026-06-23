# Testing Guide - Customer Support Agent

Complete guide to test the hybrid agentic application.

---

## Prerequisites Check

Before testing, verify you have:

```bash
# Check Python version (need 3.11+)
python3 --version

# Check if dependencies are installed
pip list | grep elasticsearch
pip list | grep python-dotenv
pip list | grep boto3

# Check if config/.env exists
ls -la config/.env

# Check if Elasticsearch is accessible
curl -H "Authorization: ApiKey $ES_API_KEY" $ES_URL
```

---

## Step 1: Environment Setup

### Create config/.env file

```bash
cd /Users/uday/Desktop/Uday-Elastic/elastic-agentic-workshop

# Copy template
cp config/.env.example config/.env

# Edit with your credentials
nano config/.env
```

Add your credentials:

```bash
# Elasticsearch Configuration
ES_URL=https://your-deployment.es.us-east-1.aws.elastic.cloud:443
ES_API_KEY=your-new-api-key-here

# AWS Configuration
AWS_REGION=us-east-1

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Verify Environment Variables

```bash
# Source the environment
source config/.env

# Test Elasticsearch connection
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/_cluster/health?pretty"
```

Expected output:
```json
{
  "cluster_name" : "your-cluster",
  "status" : "green",
  ...
}
```

---

## Step 2: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Verify installation
python3 -c "from elasticsearch import Elasticsearch; print('✓ Elasticsearch installed')"
python3 -c "from dotenv import load_dotenv; print('✓ python-dotenv installed')"
python3 -c "import boto3; print('✓ boto3 installed')"
```

---

## Step 3: Create Elasticsearch Indices

### Run Setup Script

```bash
python infra/elasticsearch_setup.py
```

**Expected Output:**
```
============================================================
Elasticsearch Index Setup
============================================================
Connected to Elasticsearch: https://your-deployment...
Creating index: customer-kb
✓ Created index: customer-kb
Creating index: customer-orders
✓ Created index: customer-orders
Creating index: customer-products
✓ Created index: customer-products
Creating index: customer-tickets
✓ Created index: customer-tickets
Creating index: customer-interactions
✓ Created index: customer-interactions
Creating index: customer-notifications
✓ Created index: customer-notifications
Creating index: customer-analytics
✓ Created index: customer-analytics
============================================================
All indices created successfully!
============================================================
```

### Verify Indices Created

```bash
# List all customer indices
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/_cat/indices/customer-*?v"

# Expected output:
# health status index                     pri rep docs.count
# green  open   customer-kb               1   1   0
# green  open   customer-orders           1   1   0
# green  open   customer-products         1   1   0
# green  open   customer-tickets          1   1   0
# green  open   customer-interactions     1   1   0
# green  open   customer-notifications    1   1   0
```

---

## Step 4: Load Sample Data

### Run Seed Script

```bash
python infra/seed_data.py
```

**Expected Output:**
```
============================================================
Seeding Sample Data
============================================================
Connected to Elasticsearch: https://your-deployment...
Seeding knowledge base...
✓ Seeded article: KB-001
✓ Seeded article: KB-002
✓ Seeded article: KB-003
✓ Seeded article: KB-004
✓ Seeded article: KB-005
Seeding products...
✓ Seeded product: PROD-001
✓ Seeded product: PROD-002
✓ Seeded product: PROD-003
✓ Seeded product: PROD-004
✓ Seeded product: PROD-005
Seeding orders...
✓ Seeded order: ORD-12345
✓ Seeded order: ORD-12346
✓ Seeded order: ORD-12347
============================================================
Sample data seeded successfully!
============================================================
```

### Verify Data Loaded

```bash
# Check knowledge base
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-kb/_count"
# Expected: {"count":5}

# Check products
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-products/_count"
# Expected: {"count":5}

# Check orders
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-orders/_count"
# Expected: {"count":3}
```

### View Sample Data

```bash
# View knowledge base articles
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-kb/_search?size=1&pretty"

# View products
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-products/_search?size=1&pretty"

# View orders
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-orders/_search?size=1&pretty"
```

---

## Step 5: Run the Agent

### Start the Interactive Agent

```bash
python main.py
```

**Expected Output:**
```
======================================================================
   CUSTOMER SUPPORT AGENT - Hybrid Architecture
   Elastic AgenticBuilder + Strands Agents SDK
======================================================================

Type your question or command:
  - Ask about products, orders, policies
  - Type 'help' for available commands
  - Type 'quit' or 'exit' to end session
  - Type 'analytics' to see agent statistics
======================================================================

Enter session ID (press Enter for new session): 
Created new session: session_1719234567

Enter customer ID (press Enter for 'anonymous'): 
Initializing agent...
✓ Agent initialized successfully

Ready! Ask me anything...

> 
```

---

## Step 6: Test Queries

### Test 1: Knowledge Base Search

```
> What is your return policy?
```

**Expected Response:**
```
Agent: Our return policy allows you to return items within 30 days 
of purchase. Items must be unused and in original packaging. Refunds 
are processed within 5-7 business days after we receive the returned item.
```

**What's being tested:**
- Hybrid search (BM25 + ELSER)
- Knowledge base index
- Context storage

---

### Test 2: Order Status Lookup

```
> Check status of order ORD-12345
```

**Expected Response:**
```
Agent: Order ORD-12345 is currently shipped.
Tracking Number: 1Z999AA10123456784
Estimated Delivery: June 26, 2026
Items: 1x Wireless Bluetooth Headphones
Total: $149.99
```

**What's being tested:**
- Document lookup by ID
- Order index
- Response formatting

---

### Test 3: Product Search

```
> Show me wireless headphones
```

**Expected Response:**
```
Agent: I found wireless headphones:

1. Wireless Bluetooth Headphones - $149.99
   - Premium over-ear with active noise cancellation
   - 30-hour battery life
   - In stock (50 units available)

Would you like more information on this product?
```

**What's being tested:**
- ELSER semantic search
- Product index
- Inventory information

---

### Test 4: Inventory Check

```
> Is product PROD-001 in stock?
```

**Expected Response:**
```
Agent: Yes! Product PROD-001 (Wireless Bluetooth Headphones) is 
in stock. We have 50 units available at warehouse US-EAST-1.
```

**What's being tested:**
- Product lookup
- Inventory checking
- Warehouse information

---

### Test 5: Multiple Turns (Context)

```
> What is your return policy?
Agent: [Returns policy information]

> What if the item is damaged?
Agent: [Should reference return policy from previous context]

> Can I return after 30 days?
Agent: [Should maintain conversation context]
```

**What's being tested:**
- Context persistence
- Multi-turn conversation
- AgenticBuilder session management

---

### Test 6: Product Search with Price Filter

```
> Show me products under $100
```

**Expected Response:**
```
Agent: I found these products under $100:

1. USB-C Charging Cable - $19.99
2. Portable Power Bank 20000mAh - $49.99

Would you like details on any of these products?
```

---

### Test 7: Shipping Information

```
> How long does shipping take?
```

**Expected Response:**
```
Agent: We offer free standard shipping on orders over $50. 
Standard shipping takes 5-7 business days. 
Express shipping (2-3 days) is available for $15.
```

---

### Test 8: Multiple Order Status

```
> Check status of order ORD-12346
```

**Expected Response:**
```
Agent: Order ORD-12346 has been delivered.
Tracking Number: 1Z999AA10123456785
Items: 1x Smart Watch Pro, 2x USB-C Charging Cable
Total: $339.97
```

---

## Step 7: Test Commands

### Test Help Command

```
> help
```

**Expected Output:**
```
----------------------------------------------------------------------
AVAILABLE COMMANDS:
----------------------------------------------------------------------
  help                - Show this help message
  quit / exit         - End the session
  analytics           - Show agent analytics and statistics
  clear               - Clear conversation history
  status              - Show session information

EXAMPLE QUERIES:
  - What is your return policy?
  - Check status of order ORD-12345
  - Show me wireless headphones under $100
  - Is product PROD-001 in stock?
  - I need help with a defective product
----------------------------------------------------------------------
```

---

### Test Status Command

```
> status
```

**Expected Output:**
```
======================================================================
SESSION STATUS
======================================================================
  Session ID:    session_1719234567
  Customer ID:   anonymous
  Agent Name:    CustomerSupport
  Elasticsearch: https://your-deployment.es.us-east-1.aws.elastic.cloud
  MCP Gateway:   Not configured
  Conversation:  5 turns
======================================================================
```

---

### Test Analytics Command

```
> analytics
```

**Expected Output:**
```
======================================================================
AGENT ANALYTICS
======================================================================

Session ID: session_1719234567

Tool Usage Statistics:
----------------------------------------------------------------------
  hybrid_search_kb
    Usage Count:   3
    Success Rate:  100.00%
    Avg Latency:   42.3ms

  get_order_status
    Usage Count:   2
    Success Rate:  100.00%
    Avg Latency:   18.5ms

  search_products
    Usage Count:   2
    Success Rate:  100.00%
    Avg Latency:   67.2ms

  check_inventory
    Usage Count:   1
    Success Rate:  100.00%
    Avg Latency:   15.8ms
======================================================================
```

---

### Test Clear Command

```
> clear
```

**Expected Output:**
```
✓ Conversation history cleared
```

---

### Test Exit

```
> quit
```

**Expected Output:**
```
Thank you for using Customer Support Agent!
Session session_1719234567 saved.
```

---

## Step 8: Verify Data in Elasticsearch

### Check AgenticBuilder Context

```bash
# View session context
curl -H "Authorization: ApiKey $ES_API_KEY" \
  "$ES_URL/agenticbuilder-context/_search?pretty"
```

**Expected:** Conversation history with user and agent messages

---

### Check Tool Execution Logs

```bash
# View tool executions
curl -H "Authorization: ApiKey $ES_API_KEY" \
  "$ES_URL/agenticbuilder-executions/_search?size=10&sort=timestamp:desc&pretty"
```

**Expected:** Logs of each tool execution with timing

---

### Check Tool Statistics

```bash
# View tool stats
curl -H "Authorization: ApiKey $ES_API_KEY" \
  "$ES_URL/agenticbuilder-tools/_search?pretty"
```

**Expected:** Usage counts, success rates, latencies

---

## Step 9: Test in Kibana

### View Data in Kibana Console

1. Open Kibana: `https://your-deployment.kb.us-east-1.aws.found.io`
2. Go to **Dev Tools** → **Console**
3. Run queries:

```json
# View knowledge base
GET customer-kb/_search
{
  "size": 5,
  "_source": ["title", "content", "category"]
}

# View recent orders
GET customer-orders/_search
{
  "size": 5,
  "sort": [{"created_at": {"order": "desc"}}]
}

# View products
GET customer-products/_search
{
  "size": 5,
  "_source": ["product_id", "name", "price", "in_stock"]
}

# View agent sessions
GET agenticbuilder-context/_search
{
  "size": 5,
  "sort": [{"updated_at": {"order": "desc"}}]
}

# View tool executions
GET agenticbuilder-executions/_search
{
  "size": 10,
  "sort": [{"timestamp": {"order": "desc"}}]
}

# Tool statistics
GET agenticbuilder-tools/_search

# Test hybrid search manually
GET customer-kb/_search
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
        }
      ]
    }
  }
}
```

---

## Step 10: Load Testing (Optional)

### Create Test Script

```python
# test_load.py
import asyncio
from agents.hybrid_customer_support import HybridCustomerSupportAgent

async def test_concurrent_sessions():
    """Test multiple concurrent sessions"""
    
    agents = [
        HybridCustomerSupportAgent(
            session_id=f"test_session_{i}",
            customer_id=f"customer_{i}"
        )
        for i in range(10)
    ]
    
    queries = [
        "What is your return policy?",
        "Check status of order ORD-12345",
        "Show me wireless headphones",
        "Is product PROD-001 in stock?"
    ]
    
    for agent in agents:
        for query in queries:
            response = agent.handle_customer_query(query)
            print(f"Session {agent.session_id}: {len(response)} chars")

if __name__ == "__main__":
    asyncio.run(test_concurrent_sessions())
```

Run:
```bash
python test_load.py
```

---

## Troubleshooting

### Issue: "Connection error"

**Solution:**
```bash
# Test Elasticsearch connection
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/_cluster/health"

# Check if API key is valid
# Regenerate if needed in Kibana
```

---

### Issue: "No results found"

**Solution:**
```bash
# Verify data exists
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-kb/_count"

# Reload data
python infra/seed_data.py
```

---

### Issue: "Tool execution failed"

**Solution:**
```bash
# Check tool logs
curl -H "Authorization: ApiKey $ES_API_KEY" \
  "$ES_URL/agenticbuilder-executions/_search?q=status:error&pretty"

# Check Elasticsearch logs
```

---

### Issue: "Agent not responding"

**Solution:**
```bash
# Check Python errors
python main.py 2>&1 | tee agent.log

# Verify all indices exist
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/_cat/indices?v"
```

---

## Test Checklist

Use this checklist to verify everything works:

- [ ] Environment variables configured
- [ ] Elasticsearch connection successful
- [ ] All 7 indices created
- [ ] Sample data loaded (5 KB articles, 5 products, 3 orders)
- [ ] Agent starts without errors
- [ ] Knowledge base search works
- [ ] Order lookup works
- [ ] Product search works
- [ ] Inventory check works
- [ ] Context persists across turns
- [ ] Analytics displays correctly
- [ ] Commands (help, status, clear) work
- [ ] Data visible in Kibana
- [ ] Tool execution logs created
- [ ] Session context saved

---

## Performance Benchmarks

Expected performance:

| Operation | Expected Time |
|-----------|---------------|
| Agent initialization | < 1 second |
| Knowledge base search | 40-80ms |
| Order lookup | 15-30ms |
| Product search | 50-100ms |
| Inventory check | 15-30ms |
| Context update | 10-20ms |
| Total query time | 100-200ms |

---

## Next Steps

After successful testing:

1. **Customize data** - Add your own products, KB articles
2. **Deploy to production** - See `AGENTCORE_DEPLOYMENT.md`
3. **Add monitoring** - CloudWatch, Elastic APM
4. **Scale up** - Multiple agent instances
5. **Integrate UI** - Build web interface

---

## Quick Test Script

```bash
#!/bin/bash
# quick_test.sh

echo "Testing Customer Support Agent..."

# Test 1: Setup
python infra/elasticsearch_setup.py && echo "✓ Indices created" || exit 1

# Test 2: Data
python infra/seed_data.py && echo "✓ Data loaded" || exit 1

# Test 3: Agent
echo "What is your return policy?" | timeout 30 python main.py && echo "✓ Agent works" || exit 1

echo ""
echo "All tests passed! ✓"
```

Run:
```bash
chmod +x quick_test.sh
./quick_test.sh
```

---

**Ready to test!** Run `python main.py` and start asking questions.
