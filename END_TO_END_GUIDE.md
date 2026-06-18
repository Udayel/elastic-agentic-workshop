# End-to-End Workshop Guide

## Complete Journey: Zero to Working Travel Agent

**Total Time**: 90-120 minutes  
**Result**: Fully functional AI travel agent running on AWS + Elastic

---

## 📋 Overview

This guide walks you through the **complete workshop** from scratch:

1. **AWS Setup** (20 min) - Elastic Cloud via Marketplace + Bedrock
2. **SageMaker Environment** (15 min) - Jupyter notebook setup
3. **ELSER Configuration** (15 min) - Semantic search setup
4. **MCP Tools** (20 min) - Build agent capabilities
5. **Lambda Deployment** (20 min) - Deploy microservices
6. **End-to-End Test** (10 min) - Verify everything works

---

## Phase 1: AWS Infrastructure Setup (20 minutes)

### Step 1.1: Subscribe to Elastic Cloud (5 min)

```bash
# 1. Open AWS Console
# 2. Search for "Elastic Cloud" in AWS Marketplace
# 3. Click "Continue to Subscribe"
# 4. Click "Set up your account"

# Direct link:
https://aws.amazon.com/marketplace/pp/prodview-iyc3k5vglqxve
```

**Save these values:**
```bash
ELASTIC_CLOUD_ID="your-deployment:dXMtZW..."
ELASTIC_ENDPOINT="https://abc123.es.us-east-1.aws.found.io:9243"
ELASTIC_PASSWORD="AbCdEfGh..."  # Shown only once!
```

### Step 1.2: Deploy ELSER Model (5 min)

```bash
# In Kibana:
# 1. Menu → Machine Learning → Trained Models
# 2. Find ".elser_model_2"
# 3. Click "Download model" (wait 1-2 min)
# 4. Click "Deploy model"
# 5. Verify status = "Started" (green)
```

### Step 1.3: Request Bedrock Access (5 min)

```bash
# In AWS Console:
# 1. Search "Bedrock"
# 2. Left menu → Model access
# 3. Click "Request model access"
# 4. Select: Claude 3.5 Sonnet, Claude 3 Haiku
# 5. Submit (usually instant approval)
```

### Step 1.4: Create IAM Role for SageMaker (5 min)

```bash
# AWS Console → IAM → Roles → Create role

# Trust relationship:
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "sagemaker.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}

# Attach policies:
- AmazonSageMakerFullAccess
- AmazonBedrockFullAccess
- SecretsManagerReadWrite

# Role name: travel-agent-workshop-role
```

### ✅ Phase 1 Checkpoint

```bash
# Verify:
- [ ] Elastic Cloud deployment is "Healthy"
- [ ] ELSER model status is "Started"
- [ ] Bedrock shows "Access granted" for Claude
- [ ] IAM role created with correct permissions
```

---

## Phase 2: SageMaker Notebook Setup (15 minutes)

### Step 2.1: Create Notebook Instance (5 min)

```bash
# AWS Console → SageMaker → Notebook instances → Create

Name: travel-agent-workshop
Instance type: ml.t3.medium
Platform: Amazon Linux 2, Jupyter Lab 3
IAM role: travel-agent-workshop-role (from Phase 1)
Root access: Enabled
VPC: Default (or your VPC if using PrivateLink)
Volume size: 20 GB

# Click "Create notebook instance"
# Wait 3-5 minutes for "InService" status
```

### Step 2.2: Clone Workshop Repository (2 min)

```bash
# Click "Open JupyterLab"
# In JupyterLab terminal:

cd SageMaker
git clone https://github.com/elastic/travel-agent-workshop.git
cd travel-agent-workshop
```

### Step 2.3: Store Credentials in Secrets Manager (5 min)

```bash
# In JupyterLab terminal:

aws secretsmanager create-secret \
  --name elastic-workshop-credentials \
  --description "Credentials for Travel Agent Workshop" \
  --secret-string '{
    "ELASTIC_CLOUD_ID": "your-cloud-id-here",
    "ELASTIC_USERNAME": "elastic",
    "ELASTIC_PASSWORD": "your-password-here",
    "ELASTIC_ENDPOINT": "https://your-endpoint.aws.found.io:9243"
  }' \
  --region us-east-1
```

### Step 2.4: Install Dependencies (3 min)

```bash
# In JupyterLab terminal:

cd travel-agent-workshop
pip install -r requirements.txt

# Verify:
pip list | grep elasticsearch  # Should show 8.15.0
pip list | grep boto3           # Should show 1.34.70
```

### ✅ Phase 2 Checkpoint

```bash
# Verify:
- [ ] SageMaker notebook is "InService"
- [ ] Repository cloned successfully
- [ ] Secrets Manager has credentials
- [ ] Dependencies installed

# Quick test:
python3 -c "from elasticsearch import Elasticsearch; print('✅ Elasticsearch imported')"
python3 -c "import boto3; print('✅ Boto3 imported')"
```

---

## Phase 3: ELSER & Semantic Search (15 minutes)

### Step 3.1: Run Setup Notebook (5 min)

```bash
# In JupyterLab:
# Navigate to: notebooks/00-Setup-SageMaker.ipynb
# Run all cells (Cell → Run All)

# Expected output:
✅ AWS Credentials: Using IAM role
✅ Elastic credentials: Loaded from Secrets Manager
✅ Successfully connected to Elastic Cloud!
✅ ELSER is deployed and running!
✅ AWS Bedrock access verified!
✅ Claude is responding!
```

### Step 3.2: Test ELSER Semantic Search (10 min)

```bash
# Open: notebooks/01-ELSER-Semantic-Search.ipynb
# Run all cells

# Test queries:
"romantic destination with great food"
"tech-savvy city with modern vibe"
"tropical paradise for relaxation"

# Cross-lingual:
"ciudad romántica con buena comida" (Spanish)
"ville moderne avec technologie" (French)
"ビーチリゾート" (Japanese)

# Expected: Relevant results in all cases!
```

### ✅ Phase 3 Checkpoint

```bash
# Verify:
- [ ] Setup notebook completed without errors
- [ ] ELSER inference working
- [ ] Semantic search returning relevant results
- [ ] Cross-lingual search working

# Manual test:
curl -u elastic:$ELASTIC_PASSWORD \
  "$ELASTIC_ENDPOINT/travel-cities/_search?size=1" | jq .hits.total.value
# Should return: 5 (number of indexed cities)
```

---

## Phase 4: MCP Tools & Agent Capabilities (20 minutes)

### Step 4.1: Test MCP Tools (10 min)

```bash
# In JupyterLab terminal:

cd services/mcp-server
python3 travel_tools.py

# Expected output:
✅ Connected to Elastic Cloud
✅ Testing MCP Tools
  ✅ search_destinations
  ✅ search_activities
  ✅ search_hotels
  ✅ search_flights
  ✅ compare_deals
  ✅ create_itinerary
  ✅ send_notification
✅ All MCP tools functional!
```

### Step 4.2: Test Strands Connector (5 min)

```bash
cd ../strands-integration
python3 strands_connector.py

# Expected output:
✅ Strands API connected
✅ Elasticsearch connected
✅ Testing flight search
✅ Testing hotel search
✅ Strands integration working!
```

### Step 4.3: Test AgenticBuilder Notifications (5 min)

```bash
cd ../notification
python3 agenticbuilder_sms.py

# Expected output:
📱 Sending SMS via AgenticBuilder to +1234567890
✅ SMS sent successfully!
✅ Trip summary test passed
✅ Email test passed
✅ All notification tests complete!
```

### ✅ Phase 4 Checkpoint

```bash
# Verify:
- [ ] All 7 MCP tools working
- [ ] Strands connector functional
- [ ] AgenticBuilder notifications working
- [ ] Test data indexed in Elasticsearch

# Check indexes:
curl -u elastic:$ELASTIC_PASSWORD "$ELASTIC_ENDPOINT/_cat/indices?v" | grep travel
# Should see: travel-cities, travel-hotels, travel-flights, etc.
```

---

## Phase 5: Lambda Deployment (20 minutes)

### Step 5.1: Configure Terraform (5 min)

```bash
# In JupyterLab terminal:

cd ~/SageMaker/travel-agent-workshop/terraform
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars:
nano terraform.tfvars
```

```hcl
# terraform.tfvars
aws_region = "us-east-1"
environment = "workshop"
project_name = "travel-agent"

# Elastic Cloud
elastic_cloud_id = "your-cloud-id"
elastic_endpoint = "https://your-endpoint.aws.found.io:9243"
elastic_username = "elastic"
elastic_password = "your-password"

# AWS Bedrock
bedrock_model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Strands API (optional)
strands_api_key = "your-key-or-leave-empty"

# Tags
tags = {
  Workshop = "TravelAgent"
  Environment = "Demo"
  ManagedBy = "Terraform"
}
```

### Step 5.2: Deploy Infrastructure (10 min)

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Review plan:
# - 8 Lambda functions
# - API Gateway
# - DynamoDB tables
# - IAM roles
# - CloudWatch logs
# - Secrets Manager secrets

# Deploy (takes 5-7 minutes)
terraform apply tfplan

# Save outputs:
API_ENDPOINT=$(terraform output -raw api_endpoint)
echo "API Endpoint: $API_ENDPOINT"
```

### Step 5.3: Verify Deployment (5 min)

```bash
# Test API endpoint
curl -X POST $API_ENDPOINT/plan \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Plan a 5-day Tokyo trip for tech enthusiasts",
    "budget": 5000,
    "travelers": 2
  }'

# Expected response:
{
  "trip_id": "trip-abc123",
  "destination": "Tokyo",
  "status": "planned",
  "summary": "5-day tech-focused Tokyo itinerary...",
  "total_cost": 4850
}
```

### ✅ Phase 5 Checkpoint

```bash
# Verify:
- [ ] Terraform deployment successful
- [ ] 8 Lambda functions deployed
- [ ] API Gateway responding
- [ ] DynamoDB tables created
- [ ] Test API call succeeds

# Check Lambda functions:
aws lambda list-functions --region us-east-1 | grep travel-agent
# Should see 8 functions

# Check API Gateway:
aws apigatewayv2 get-apis --region us-east-1 | grep travel-agent
# Should see API
```

---

## Phase 6: End-to-End Integration Test (10 minutes)

### Step 6.1: Run Complete Trip Planning Flow (5 min)

```bash
# In JupyterLab, create new notebook:
# notebooks/99-End-to-End-Test.ipynb
```

```python
import requests
import json

API_ENDPOINT = "https://your-api-id.execute-api.us-east-1.amazonaws.com"

# Test 1: Search destinations
print("🧪 Test 1: Search destinations")
response = requests.post(
    f"{API_ENDPOINT}/search/destinations",
    json={"query": "romantic city with great food", "budget_level": "medium"}
)
print(f"✅ Found {len(response.json()['results'])} destinations")

# Test 2: Get recommendations
print("\n🧪 Test 2: Get AI recommendations")
response = requests.post(
    f"{API_ENDPOINT}/plan",
    json={
        "query": "Plan a romantic 3-day Paris trip for anniversary",
        "budget": 3000,
        "travelers": 2
    }
)
trip = response.json()
print(f"✅ Trip planned: {trip['trip_id']}")
print(f"   Destination: {trip['destination']}")
print(f"   Cost: ${trip['total_cost']}")

# Test 3: Search hotels
print("\n🧪 Test 3: Search hotels")
response = requests.post(
    f"{API_ENDPOINT}/search/hotels",
    json={
        "city": trip['destination'],
        "check_in": "2026-07-15",
        "check_out": "2026-07-18",
        "budget_level": "medium"
    }
)
print(f"✅ Found {len(response.json()['hotels'])} hotels")

# Test 4: Create itinerary
print("\n🧪 Test 4: Create itinerary")
response = requests.post(
    f"{API_ENDPOINT}/itinerary/create",
    json={
        "trip_id": trip['trip_id'],
        "days": 3
    }
)
itinerary = response.json()
print(f"✅ Itinerary created with {len(itinerary['days'])} days")

# Test 5: Send notification
print("\n🧪 Test 5: Send notification")
response = requests.post(
    f"{API_ENDPOINT}/notify",
    json={
        "trip_id": trip['trip_id'],
        "phone": "+1234567890",
        "message": "Your trip is ready!"
    }
)
print(f"✅ Notification sent: {response.json()['message_id']}")

print("\n" + "="*60)
print("🎉 ALL TESTS PASSED!")
print("="*60)
```

### Step 6.2: Verify in Kibana (3 min)

```bash
# Open Kibana
# 1. Check indexes:
GET _cat/indices?v

# Should see:
travel-cities
travel-hotels
travel-flights
travel-activities
agenticbuilder-notifications
trip-data

# 2. Check APM traces:
# Navigate to: APM → Services → travel-agent-core
# Should see traces for API calls

# 3. Check notifications:
GET agenticbuilder-notifications/_search
# Should see test notifications
```

### Step 6.3: Monitor CloudWatch (2 min)

```bash
# AWS Console → CloudWatch → Log groups

# Check Lambda logs:
/aws/lambda/travel-agent-core
/aws/lambda/travel-agent-destination-expert
/aws/lambda/travel-agent-booking-assistant

# Recent logs should show successful invocations
```

### ✅ Phase 6 Checkpoint

```bash
# Verify:
- [ ] All API endpoints responding
- [ ] ELSER semantic search working
- [ ] Claude/Bedrock integration working
- [ ] Hotels/flights searchable
- [ ] Itinerary generation working
- [ ] Notifications sending
- [ ] APM traces visible in Kibana
- [ ] CloudWatch logs showing activity

# Final test:
curl $API_ENDPOINT/health
# Should return: {"status": "healthy", "services": "all_operational"}
```

---

## 🎉 Success! What You've Built

### ✅ Complete System Running:

1. **Elastic Cloud on AWS** (via Marketplace)
   - ELSER v2 semantic search
   - Vector database with travel data
   - APM monitoring
   - AgenticBuilder notifications

2. **AWS Bedrock**
   - Claude 3.5 Sonnet for reasoning
   - Tool use / function calling
   - Streaming responses

3. **8 Lambda Microservices**
   - Agent Core (orchestration)
   - Destination Expert (ELSER search)
   - Booking Assistant (Strands integration)
   - Activities Expert
   - Deal Comparator
   - Itinerary Builder
   - Notification Service
   - Preference Manager

4. **API Gateway**
   - REST endpoints
   - Request validation
   - CORS enabled

5. **Supporting Infrastructure**
   - DynamoDB (state, trips)
   - S3 (artifacts)
   - Secrets Manager (credentials)
   - CloudWatch (logs, metrics)
   - VPC (optional security)

---

## 📊 System Architecture

```
User/Application
       ↓
API Gateway (HTTPS)
       ↓
┌──────────────────────────────────────────────┐
│  AWS Lambda Functions                        │
│  ┌────────────┐  ┌──────────────┐           │
│  │ Agent Core │→ │ Bedrock      │           │
│  │            │  │ Claude 3.5   │           │
│  └─────┬──────┘  └──────────────┘           │
│        │                                     │
│   ┌────┴─────────────────────┐              │
│   ↓         ↓         ↓       ↓              │
│ Dest.   Booking   Activities Deal           │
│ Expert  Assist.   Expert    Comp.           │
└──┬────────┬─────────┬────────┬──────────────┘
   │        │         │        │
   ↓        ↓         ↓        ↓
┌─────────────────────────────────────────┐
│  Elastic Cloud on AWS                   │
│  ┌──────────┐  ┌────────┐  ┌─────────┐ │
│  │ ELSER v2 │  │ Vector │  │   APM   │ │
│  │ Semantic │  │   DB   │  │ Traces  │ │
│  └──────────┘  └────────┘  └─────────┘ │
└─────────────────────────────────────────┘
   ↓
DynamoDB (state) | S3 (files) | CloudWatch
```

---

## 🧪 Testing Checklist

### Functional Tests

```bash
# 1. Semantic search
✅ Search in English
✅ Search in Spanish
✅ Search in French
✅ Search in Japanese
✅ Intent-based queries ("romantic", "adventure", "budget")

# 2. Agent reasoning
✅ Multi-turn conversation
✅ Context retention
✅ Tool selection
✅ Error handling
✅ Fallback responses

# 3. Data retrieval
✅ Destination search (ELSER)
✅ Hotel search (Strands)
✅ Flight search (Strands)
✅ Activity search
✅ Deal comparison

# 4. Itinerary generation
✅ Day-by-day planning
✅ Budget allocation
✅ Preference matching
✅ Optimization

# 5. Notifications
✅ SMS via AgenticBuilder
✅ Email notifications
✅ Trip summaries
✅ Status updates

# 6. Infrastructure
✅ API Gateway routing
✅ Lambda invocation
✅ DynamoDB reads/writes
✅ Secrets Manager access
✅ CloudWatch logging
✅ APM tracing
```

### Performance Tests

```bash
# Response times (target)
- Semantic search: < 500ms
- Claude reasoning: 1-3 seconds
- Full trip plan: < 10 seconds
- API Gateway latency: < 100ms

# Concurrent users (ml.t3.medium):
- Expected: 10-20 concurrent
- Lambda can scale to 1000+

# Cost per request:
- Lambda: ~$0.0001
- Bedrock: ~$0.003 (1K tokens)
- Elastic: Included in subscription
- Total: ~$0.0031 per trip plan
```

---

## 🔧 Troubleshooting

### Common Issues

**1. "Connection timeout" to Elastic**

```bash
# Solution: Add SageMaker IP to Elastic traffic filter
curl https://api.ipify.org  # Get your IP
# Add to: Elastic Cloud Console → Security → Traffic filters
```

**2. "Access denied" to Bedrock**

```bash
# Solution: Check IAM role permissions
aws iam get-role-policy \
  --role-name travel-agent-workshop-role \
  --policy-name BedrockAccess
```

**3. Lambda function errors**

```bash
# Check logs:
aws logs tail /aws/lambda/travel-agent-core --follow

# Common fixes:
- Increase Lambda timeout (default: 30s → 60s)
- Increase Lambda memory (default: 512MB → 1024MB)
- Check environment variables
```

**4. ELSER not returning results**

```bash
# Verify ELSER is running:
curl -u elastic:$PASSWORD "$ELASTIC_ENDPOINT/_ml/trained_models/.elser_model_2/_stats"

# Restart if needed (in Kibana):
# ML → Trained Models → .elser_model_2 → Stop → Start
```

---

## 🧹 Cleanup (When Done)

### Step 1: Delete Lambda Infrastructure

```bash
cd ~/SageMaker/travel-agent-workshop/terraform
terraform destroy -auto-approve

# Removes:
- Lambda functions
- API Gateway
- DynamoDB tables
- IAM roles
- CloudWatch logs
```

### Step 2: Stop SageMaker Notebook

```bash
aws sagemaker stop-notebook-instance \
  --notebook-instance-name travel-agent-workshop

# Or delete completely:
aws sagemaker delete-notebook-instance \
  --notebook-instance-name travel-agent-workshop
```

### Step 3: Delete Elastic Deployment (Optional)

```bash
# Go to: cloud.elastic.co
# Deployments → Your deployment → Delete
# Type deployment name to confirm

# Cost after delete: $0
```

### Step 4: Delete Secrets

```bash
aws secretsmanager delete-secret \
  --secret-id elastic-workshop-credentials \
  --force-delete-without-recovery
```

### Total Cleanup Time: 10 minutes

---

## 💰 Total Workshop Cost

| Service | Usage | Cost |
|---------|-------|------|
| **Elastic Cloud** | 7-day trial | $0 |
| **After trial** | ~3 hours | ~$0.50 |
| **SageMaker** | ml.t3.medium, 2 hours | $0.12 |
| **Bedrock** | ~2M tokens | $6-8 |
| **Lambda** | ~1000 invocations | $0.02 |
| **API Gateway** | ~1000 requests | $0.01 |
| **DynamoDB** | On-demand | $0.01 |
| **CloudWatch** | Logs | $0.01 |
| **Total** | **Full workshop** | **~$6-8** |

**After cleanup**: $0 ongoing cost

---

## 📚 Next Steps

### Learning

1. **Modify semantic search** - Add more cities, try different queries
2. **Customize agent** - Change prompts, add tools
3. **Experiment with models** - Try Claude 3 Opus, Haiku
4. **Add data sources** - Index hotels, activities, restaurants

### Production

1. **Scale infrastructure** - Increase Lambda memory, add caching
2. **Add authentication** - API keys, Cognito, OAuth
3. **Enable PrivateLink** - VPC connectivity to Elastic
4. **Setup monitoring** - Alarms, dashboards, SLAs
5. **Add CI/CD** - GitHub Actions, CodePipeline

### Documentation

- [AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md) - Elastic setup
- [SAGEMAKER_SETUP.md](./SAGEMAKER_SETUP.md) - Notebook setup
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment
- [SECURITY.md](./SECURITY.md) - Security best practices

---

## 🎓 What You Learned

✅ Subscribe to Elastic Cloud via AWS Marketplace  
✅ Deploy and configure ELSER for semantic search  
✅ Setup SageMaker notebooks with IAM roles  
✅ Build MCP-compliant tools for AI agents  
✅ Integrate AWS Bedrock (Claude) for reasoning  
✅ Deploy Lambda microservices with Terraform  
✅ Create API Gateway REST endpoints  
✅ Monitor with Elastic APM and CloudWatch  
✅ Manage secrets with Secrets Manager  
✅ Build production-ready AI agents on AWS  

---

**🎉 Congratulations! You've built a production-grade AI travel agent on AWS!**

*End-to-End Guide v3.2*  
*For AWS + Elastic Customers*  
*Total time: 90-120 minutes*  
*Total cost: ~$6-8*
