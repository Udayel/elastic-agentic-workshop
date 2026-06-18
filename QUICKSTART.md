# Quick Start Guide

Get the Travel Intelligence Agent workshop running in 30 minutes.

---

## Prerequisites

- ✅ AWS Account with Bedrock access (Claude 3.5 Sonnet)
- ✅ Elastic Cloud deployment on AWS (8.15+)
- ✅ ELSER v2 model deployed in Elastic
- ✅ Python 3.9-3.11 installed
- ✅ Terraform 1.0+ installed
- ✅ AWS CLI configured

---

## Step 1: Clone and Setup (5 min)

```bash
# Navigate to workshop directory
cd ~/Desktop/Uday-Elastic/elastic-agentic-workshop

# Create Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install elasticsearch==8.15.0 elastic-apm==6.21.0 boto3==1.34.70 \
            python-dotenv==1.0.1 requests==2.31.0 pyyaml==6.0.1
```

---

## Step 2: Configure Credentials (5 min)

Create `.env` file in the project root:

```bash
cat > .env << 'EOF'
# Elastic Cloud
ELASTIC_CLOUD_ID=your_cloud_id_here
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=your_password_here
ELASTIC_ENDPOINT=https://your-deployment.es.us-east-1.aws.found.io:9243

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Strands (optional for testing)
STRANDS_API_KEY=your_strands_key
STRANDS_API_URL=https://api.strands.com/v1

# Twilio (optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
EOF

# Edit with your actual credentials
nano .env
```

---

## Step 3: Verify Setup (3 min)

```bash
# Run verification script
cd modules/module-0-setup
python3 verify_setup.py

# Expected output:
# ✓ Elasticsearch connection successful
# ✓ ELSER model is deployed and running
# ✓ AWS Bedrock access verified
# ✓ All checks passed!
```

If any checks fail, see [Module 0 Troubleshooting](./modules/module-0-setup/README.md#troubleshooting).

---

## Step 4: Create Indexes (3 min)

```bash
# Create ELSER-optimized indexes
cd ../module-1-elser
python3 create_indexes.py

# Expected output:
# ✓ Created index: travel-cities
# ✓ Created pipeline: travel-cities-elser-pipeline
# ✓ Created index: travel-activities
# ✓ Created index: travel-hotels
# ✅ All indexes created successfully!
```

---

## Step 5: Load Sample Data (2 min)

```bash
# Load travel data with ELSER embeddings
python3 load_sample_data.py

# Expected output:
# Loading 3 documents into travel-cities...
#   ✓ Indexed: 3 documents
# Loading 3 documents into travel-activities...
#   ✓ Indexed: 3 documents
# Loading 3 documents into travel-hotels...
#   ✓ Indexed: 3 documents
# ✅ All data loaded successfully!
```

---

## Step 6: Test ELSER Search (5 min)

```bash
# Run ELSER semantic search demo
python3 test_elser_search.py

# You'll see 6 test demonstrations:
# TEST 1: Semantic Understanding
# TEST 2: Cross-Lingual Search
# TEST 3: Intent Understanding
# TEST 4: Context Awareness
# TEST 5: ELSER vs Traditional Search
# TEST 6: Compound Concepts

# This showcases ELSER's zero-shot semantic capabilities
```

---

## Step 7: Test MCP Tools (3 min)

```bash
# Test MCP travel tools
cd ../../services/mcp-server
python3 travel_tools.py

# Expected output:
# ====================================
# Testing MCP Travel Tools
# ====================================
# 
# 1. Testing destination search...
# 🔍 Searching destinations: 'vibrant city with amazing food and technology'
# Found 2 destinations
#   • Tokyo, Japan (score: 15.42)
#   • Paris, France (score: 12.38)
#
# 2. Testing activity search...
# 🎯 Searching activities in Tokyo: 'interactive technology experience for families'
# Found 2 activities
#   • teamLab Borderless Digital Art Museum (score: 18.91)
#
# ✅ MCP Tools Test Complete!
```

---

## Step 8: Test Strands Integration (2 min)

```bash
# Test Strands-Elastic connector
cd ../strands-integration
python3 strands_connector.py

# Expected output:
# ====================================
# Strands-Elastic Connector Test
# ====================================
# 
# Setting up Strands-Elastic connector indexes...
# ✓ Created index: strands-flights
# ✓ Created index: strands-hotels
# ✅ Strands-Elastic indexes configured
#
# 1. Testing flight search via Strands...
# 🔍 Searching flights via Strands-Elastic connector:
#    JFK → NRT on 2026-12-15
# ✓ Found flights
#
# 2. Testing hotel search via Strands...
# 🏨 Searching hotels via Strands-Elastic connector:
#    Tokyo | 2026-12-15 to 2026-12-20
# ✓ Found hotels
#
# ✅ Strands-Elastic Integration Test Complete!
```

---

## Step 9: Test Simple Agent (2 min)

```bash
# Test basic agent with Bedrock
cd ../../modules/module-0-setup
python3 hello_agent.py

# Expected output:
# ====================================
# Hello World Agent Test
# ====================================
# 
# 🤖 Testing Bedrock Agent...
# 
# Hello! I'm your AI travel assistant, ready to help you plan 
# amazing trips around the world...
#
# 🔍 Testing ELSER Semantic Search...
# ✓ Found 1 result(s)
#   Top match: Paris is a beautiful city...
#   Score: 15.42
#
# ✅ All tests passed! Your agent is working!
```

---

## What You've Accomplished ✅

In 30 minutes, you've:

1. ✅ Set up complete Python environment
2. ✅ Verified Elastic + AWS connections
3. ✅ Created ELSER-optimized indexes
4. ✅ Loaded sample travel data
5. ✅ Tested semantic search (6 scenarios)
6. ✅ Verified MCP tools work
7. ✅ Tested Strands connector integration
8. ✅ Ran first AI agent

---

## Next Steps

### Immediate

1. **Explore ELSER searches** - Try different queries in `test_elser_search.py`
2. **Review MCP tools** - See how tools integrate with Elastic
3. **Check Strands data** - View indexes in Kibana

### Continue Workshop

- **[Module 1: ELSER Deep Dive](./modules/module-1-elser/)** - Learn semantic search
- **[Module 2: Build Agents](./modules/module-2-lambda/)** - Create Lambda functions
- **[Module 3: Deploy with Terraform](./terraform/)** - Infrastructure automation

---

## Troubleshooting

### Can't connect to Elastic?

```bash
# Test connection manually
curl -u elastic:YOUR_PASSWORD https://your-endpoint.es.us-east-1.aws.found.io:9243

# Check .env file
cat .env | grep ELASTIC
```

### ELSER not found?

```bash
# Check ELSER deployment in Kibana
# Navigate to: ML → Trained Models → .elser_model_2
# Status should be "Started"
```

### Python import errors?

```bash
# Verify virtual environment is active
which python3
# Should show: /path/to/venv/bin/python3

# Reinstall packages
pip install --force-reinstall elasticsearch boto3 python-dotenv
```

### AWS Bedrock access denied?

```bash
# Verify model access
aws bedrock list-foundation-models --region us-east-1 | grep claude

# Check IAM permissions
aws iam list-attached-user-policies --user-name YOUR_USER
```

---

## Viewing Results

### Kibana

1. Open Kibana: `https://your-deployment.kb.us-east-1.aws.found.io`
2. Go to **Dev Tools** → **Console**
3. View indexes:
   ```
   GET travel-cities/_search
   {
     "query": {
       "text_expansion": {
         "description_embedding": {
           "model_id": ".elser_model_2",
           "model_text": "romantic destination"
         }
       }
     }
   }
   ```

### Elasticsearch Indices

```bash
# List all travel indexes
curl -u elastic:PASSWORD https://your-endpoint/travel-*/_search?size=0

# Count documents
curl -u elastic:PASSWORD https://your-endpoint/travel-cities/_count
```

---

## Clean Up (When Done)

```bash
# Delete sample indexes (optional)
curl -X DELETE -u elastic:PASSWORD https://your-endpoint/travel-cities
curl -X DELETE -u elastic:PASSWORD https://your-endpoint/travel-activities
curl -X DELETE -u elastic:PASSWORD https://your-endpoint/travel-hotels
curl -X DELETE -u elastic:PASSWORD https://your-endpoint/strands-*

# Deactivate Python environment
deactivate
```

---

## What's Working Now

✅ **Fully Functional:**
- ELSER semantic search with travel data
- MCP tools for destination/activity/hotel search
- Strands connector framework
- Basic Bedrock agent
- All verification scripts

🚧 **Partially Working:**
- Lambda functions (stubs created)
- Agent orchestration (needs completion)
- Terraform deployment (structure ready)

📝 **Pending:**
- Full agent orchestration logic
- Streamlit demo UI
- Production deployment scripts
- End-to-end workflow

---

## Cost Summary (What You Just Ran)

| Service | Usage | Cost |
|---------|-------|------|
| Elastic Cloud | Existing deployment | $0 |
| AWS Bedrock | 5-10 test requests | ~$0.05 |
| Data transfer | Minimal | $0 |
| **Total** | | **~$0.05** |

Very cheap to test! 💰

---

## Getting Help

- **Workshop Issues**: Check `IMPLEMENTATION_SUMMARY.md`
- **Elastic Docs**: https://www.elastic.co/guide
- **AWS Docs**: https://docs.aws.amazon.com/bedrock/
- **Strands**: https://strands.com/

---

**You're all set!** 🎉

Continue to [Module 1](./modules/module-1-elser/) or start building your own agents!
