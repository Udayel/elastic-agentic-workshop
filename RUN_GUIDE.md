# How to Run the Hybrid Customer Support Agent

Quick guide to get the agentic app running in 5 minutes.

---

## Prerequisites

- Python 3.11+
- Elasticsearch deployment (Elastic Cloud)
- Git

---

## Step-by-Step Instructions

### 1. Install Dependencies

```bash
# Navigate to project directory
cd /Users/uday/Desktop/Uday-Elastic/elastic-agentic-workshop

# Install Python packages
pip install -r requirements.txt
```

Expected packages:
- elasticsearch==8.15.0
- boto3==1.34.70
- python-dotenv==1.0.1
- strands-agents-sdk==1.2.0
- fastapi==0.109.0

---

### 2. Configure Elasticsearch Credentials

Create your `.env` file:

```bash
# Copy the template
cp config/.env.example config/.env

# Edit with your credentials
nano config/.env
```

Add your Elasticsearch credentials:

```bash
# Elasticsearch Configuration
ES_URL=https://your-deployment.es.us-east-1.aws.elastic.cloud:443
ES_API_KEY=your-new-elasticsearch-api-key

# AWS Configuration (optional for now)
AWS_REGION=us-east-1

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

**To get your Elasticsearch credentials:**

1. Go to https://cloud.elastic.co
2. Select your deployment
3. Click "Management" → "Security" → "API Keys"
4. Click "Create API key"
5. Name: `customer-support-agent`
6. Copy the API key

---

### 3. Create Elasticsearch Indices

```bash
# Run the setup script
python infra/elasticsearch_setup.py
```

**Expected output:**
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

---

### 4. Load Sample Data

```bash
# Seed the indices with sample data
python infra/seed_data.py
```

**Expected output:**
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

---

### 5. Run the Agent

```bash
# Start the interactive agent
python main.py
```

**Expected output:**
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

## Test Queries

Try these example queries:

### 1. Knowledge Base Search
```
> What is your return policy?

Agent: Our return policy allows you to return items within 30 days 
of purchase. Items must be unused and in original packaging. Refunds 
are processed within 5-7 business days after we receive the returned item.
```

### 2. Order Status
```
> Check status of order ORD-12345

Agent: Order ORD-12345 is currently shipped.
Tracking Number: 1Z999AA10123456784
Estimated Delivery: June 26, 2026
Items: Wireless Bluetooth Headphones
Total: $149.99
```

### 3. Product Search
```
> Show me wireless headphones

Agent: I found wireless headphones:

1. Wireless Bluetooth Headphones - $149.99
   - Premium over-ear with active noise cancellation
   - 30-hour battery life
   - In stock (50 units available)

Would you like more information on this product?
```

### 4. Inventory Check
```
> Is product PROD-001 in stock?

Agent: Yes! Product PROD-001 (Wireless Bluetooth Headphones) is 
in stock. We have 50 units available at warehouse US-EAST-1.
```

### 5. Create Support Ticket
```
> I received a defective product and need help

Agent: I understand you've received a defective product. I've created 
support ticket TKT-001 with high priority. A specialist will contact 
you within 2 hours to resolve this issue.
```

---

## Available Commands

### In the REPL:

- **help** - Show available commands and examples
- **status** - Show session information
- **analytics** - Show tool usage statistics
- **clear** - Clear conversation history
- **quit** or **exit** - End the session

### Examples:

```bash
> help
# Shows full help menu

> status
# Shows session ID, customer ID, conversation turns

> analytics
# Shows tool performance metrics

> clear
# Clears conversation history, starts fresh

> quit
# Exits the application
```

---

## View Analytics

Type `analytics` to see agent performance:

```
> analytics

======================================================================
AGENT ANALYTICS
======================================================================

Session ID: session_1719234567

Tool Usage Statistics:
----------------------------------------------------------------------
  hybrid_search_kb
    Usage Count:   5
    Success Rate:  100.00%
    Avg Latency:   42.3ms

  get_order_status
    Usage Count:   2
    Success Rate:  100.00%
    Avg Latency:   18.5ms

  search_products
    Usage Count:   3
    Success Rate:  100.00%
    Avg Latency:   67.2ms

  check_inventory
    Usage Count:   2
    Success Rate:  100.00%
    Avg Latency:   15.8ms
======================================================================
```

---

## Troubleshooting

### Error: "ES_URL and ES_API_KEY must be set"

**Solution:**
```bash
# Make sure config/.env exists
ls -la config/.env

# If not, create it
cp config/.env.example config/.env

# Edit with your credentials
nano config/.env
```

---

### Error: "Connection error" or "Authentication failed"

**Solution:**
```bash
# Test Elasticsearch connection manually
curl -H "Authorization: ApiKey $ES_API_KEY" $ES_URL

# Verify credentials are correct in config/.env
cat config/.env | grep ES_
```

---

### Error: "Index not found"

**Solution:**
```bash
# Create the indices
python infra/elasticsearch_setup.py

# Verify indices were created
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/_cat/indices/customer-*?v"
```

---

### Error: "No results found" for queries

**Solution:**
```bash
# Load sample data
python infra/seed_data.py

# Verify data was loaded
curl -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/customer-kb/_count"
```

---

### Error: "Module not found" or import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific packages
pip install elasticsearch==8.15.0 python-dotenv==1.0.1 boto3==1.34.70
```

---

## Architecture Overview

The application uses:

1. **Strands Agents SDK** - Agent orchestration and tool execution
2. **Elastic AgenticBuilder** - Context management and persistence
3. **Elasticsearch** - Search engine and data storage
4. **Hybrid Search** - BM25 keyword + ELSER semantic search

### Data Flow:

```
User Query → HybridCustomerSupportAgent → Tool Selection
    ↓
Tool Execution → Elasticsearch Search → Results
    ↓
Context Update → AgenticBuilder → Response to User
```

---

## What's Stored in Elasticsearch

### Customer Support Data:
- **customer-kb** - Knowledge base articles (FAQs, policies)
- **customer-orders** - Order tracking information
- **customer-products** - Product catalog
- **customer-tickets** - Support tickets
- **customer-interactions** - Conversation history

### AgenticBuilder Data:
- **agenticbuilder-context** - Session context and conversation history
- **agenticbuilder-tools** - Tool usage statistics
- **agenticbuilder-executions** - Tool execution logs

---

## View Data in Kibana

1. Go to your Kibana instance
2. Open **Dev Tools** → **Console**
3. Run queries:

```json
# View knowledge base
GET customer-kb/_search
{
  "size": 5
}

# View products
GET customer-products/_search
{
  "size": 5
}

# View orders
GET customer-orders/_search
{
  "size": 5
}

# View session context
GET agenticbuilder-context/_search
{
  "size": 5
}

# View tool statistics
GET agenticbuilder-tools/_search
{
  "size": 10
}
```

---

## Next Steps

### Customize the Agent:

1. **Add your own tools** - Edit `agents/customer_support_tools.py`
2. **Modify agent behavior** - Edit `agents/hybrid_customer_support.py`
3. **Add more data** - Create custom seed scripts
4. **Deploy to production** - See `CUSTOMER_SUPPORT_ARCHITECTURE.md`

### Advanced Features:

- Deploy ELSER model for semantic search
- Setup Cognito for OAuth2 authentication
- Deploy MCP server for remote tool execution
- Configure AWS Bedrock for enhanced LLM capabilities

---

## Architecture Documentation

For detailed architecture information:

- **HYBRID_ARCHITECTURE.md** - Complete hybrid architecture guide
- **CUSTOMER_SUPPORT_ARCHITECTURE.md** - Customer support specifics
- **AGENTIC_SYSTEM_README.md** - Multi-agent system overview

---

## Support

**Issues:** https://github.com/Udayel/elastic-agentic-workshop/issues  
**Maintainer:** uday@elastic.co  
**Repository:** https://github.com/Udayel/elastic-agentic-workshop

---

## Quick Commands Summary

```bash
# Setup
pip install -r requirements.txt
cp config/.env.example config/.env
# Edit config/.env with your credentials

# Initialize
python infra/elasticsearch_setup.py
python infra/seed_data.py

# Run
python main.py

# Test queries
> What is your return policy?
> Check status of order ORD-12345
> Show me wireless headphones
> Is product PROD-001 in stock?

# Commands
> help
> status
> analytics
> clear
> quit
```

---

**You're ready to go!** 🚀

Start the agent with `python main.py` and begin asking questions.
