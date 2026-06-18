# Travel Intelligence Agent Workshop
## For AWS + Elastic Customers

**Build production AI agents leveraging your existing AWS and Elastic infrastructure**

> Transform travel planning with intelligent agents powered by Elastic ELSER on AWS

---

## 🆕 NEW! AWS Marketplace & SageMaker Support (v3.2)

### ☁️ Get Elastic Cloud via AWS Marketplace
✅ **Unified AWS billing** - Pay via your AWS account  
✅ **Use AWS credits** - Apply promotional credits to Elastic  
✅ **7-day free trial** - Start exploring immediately  
✅ **Same-day setup** - Running in AWS in 20 minutes  

👉 **[AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md)** - Complete subscription guide

---

### 📓 Run Workshop in Amazon SageMaker
✅ **No local setup** - Everything in AWS cloud  
✅ **Auto AWS credentials** - IAM role integration  
✅ **Low latency** - Same region as Bedrock  
✅ **Cost-effective** - ~$0.05/hour or FREE (Studio Lab)  

👉 **[SAGEMAKER_SETUP.md](./SAGEMAKER_SETUP.md)** - 3 SageMaker options explained

**Compare all setup options**: [SETUP_COMPARISON.md](./SETUP_COMPARISON.md)

---

## 🎯 Workshop Overview

This hands-on workshop is designed for **AWS and Elastic customers** who want to build production-grade AI agents. We assume you're already familiar with:

- ✅ AWS services (Lambda, API Gateway, DynamoDB, Bedrock, SageMaker)
- ✅ Elastic Cloud from AWS Marketplace
- ✅ Terraform infrastructure as code
- ✅ Microservices architecture patterns

### What You'll Build

A complete **Travel Intelligence Agent** system that showcases:

1. **Elastic ELSER** for zero-shot semantic search
2. **AWS Bedrock Claude** for agent reasoning
3. **Microservices on Lambda** - 8 specialized services
4. **Terraform automation** - one-command deployment
5. **MCP tools** for agent capabilities
6. **Production observability** with Elastic APM
7. **Real integrations** - Strands API, Twilio SMS

### Why This Matters for AWS Customers

**Native AWS Integration:**
- ✅ **Pay via AWS** - Elastic Cloud billed through AWS Marketplace
- ✅ **Use AWS credits** - Apply promotional credits to Elastic
- ✅ **Same region** - Deploy Elastic in same AWS region as Lambda/Bedrock
- ✅ **VPC connectivity** - Optional PrivateLink for secure access
- ✅ **IAM roles** - SageMaker notebooks use IAM for credentials
- ✅ **CloudTrail** - Unified audit logging across services
- ✅ **Cost Explorer** - Track all costs in one place

**Familiar AWS Patterns:**
- Terraform for infrastructure as code
- Lambda for serverless microservices
- API Gateway for REST endpoints
- DynamoDB for state management
- Bedrock for AI/ML inference
- SageMaker for Jupyter notebooks

---

## 🏗️ Architecture (AWS + Elastic Native)

```
┌────────────────────────────────────────────────────────────┐
│                    AWS API Gateway                          │
│              (Regional, HTTP API, CORS enabled)            │
└──────────┬──────────────────────┬──────────────────────────┘
           │                      │
┌──────────▼─────────┐   ┌────────▼──────────────────────────┐
│  AWS Lambda         │   │  AWS Lambda Functions             │
│  (Agent Core)       │   │  (Microservices)                  │
│                     │   │                                   │
│  • Bedrock Claude   │   │  • Destination Expert (ELSER)    │
│  • Orchestration    │   │  • Booking Assistant (Strands)   │
│  • State Mgmt       │   │  • Activities (ELSER)            │
│                     │   │  • Deal Comparator                │
│                     │   │  • Itinerary Builder             │
│                     │   │  • Notification (Twilio)         │
│                     │   │  • Preference Manager            │
└──────────┬──────────┘   └────────┬──────────────────────────┘
           │                       │
           │  ┌────────────────────▼────────────────────────┐
           │  │     AWS Services Layer                      │
           │  │  • DynamoDB (state, trips)                 │
           │  │  • Secrets Manager (credentials)           │
           │  │  • S3 (artifacts)                          │
           │  │  • CloudWatch (logs, metrics)             │
           │  └─────────────────────────────────────────────┘
           │
┌──────────▼────────────────────────────────────────────────┐
│             Elastic Cloud on AWS                          │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │   ELSER v2   │  │  Vector DB   │  │   APM/Traces   │ │
│  │              │  │              │  │                │ │
│  │ • Zero-shot  │  │ • Cities     │  │ • Agent perf   │ │
│  │ • Cross-lang │  │ • Hotels     │  │ • Tool traces  │ │
│  │ • Real-time  │  │ • Activities │  │ • Cost track   │ │
│  └──────────────┘  └──────────────┘  └────────────────┘ │
│                                                           │
│  Deployment: Elastic Cloud on AWS Marketplace            │
│  Region: Same as Lambda (us-east-1)                      │
│  VPC: Private Link (optional for production)             │
└───────────────────────────────────────────────────────────┘
```

### Key Integration Points

1. **Lambda → Elastic**: Direct HTTPS with retry logic
2. **Lambda → Bedrock**: AWS SDK, same region
3. **API Gateway → Lambda**: Async invocation for long-running tasks
4. **CloudWatch → Elastic APM**: Unified observability
5. **Terraform**: Complete infrastructure deployment

---

## 💼 Workshop Modules (Fast Track for AWS/Elastic Users)

| Module | Duration | Focus | Prerequisites |
|--------|----------|-------|---------------|
| 0 | 15 min | Quick Setup | AWS account, Elastic Cloud |
| 1 | 25 min | ELSER + MCP | ELSER deployed |
| 2 | 20 min | Lambda Functions | Terraform basics |
| 3 | 30 min | Agent Orchestration | Bedrock access |
| 4 | 20 min | Terraform Deploy | AWS CLI configured |
| 5 | 20 min | Production Ops | APM enabled |
| **Total** | **130 min** | | **Production system** |

---

## 🚀 Quick Start (For AWS Customers)

### Step 0: Get Elastic Cloud via AWS Marketplace ⭐ START HERE

**All AWS customers should start here:**

👉 **[AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md)** (20 minutes)

**What you'll do:**
1. Subscribe to Elastic Cloud on AWS Marketplace
2. Deploy Elastic in your AWS region (same as Lambda/Bedrock)
3. Enable ELSER v2 model for semantic search
4. Request AWS Bedrock model access (Claude 3.5)

**Why AWS Marketplace:**
- ✅ **Pay via AWS** - Everything on one AWS bill
- ✅ **Use AWS credits** - Apply promotional credits
- ✅ **7-day free trial** - Start exploring immediately
- ✅ **Faster procurement** - Already approved via AWS
- ✅ **Native integration** - Stays in AWS ecosystem

---

### Prerequisites Checklist

**Required:**
- [ ] **AWS Account** (active account with billing enabled)
- [ ] **AWS Bedrock access** - Request Claude 3.5 Sonnet model access
  - Go to AWS Console → Bedrock → Model access → Request
- [ ] **Elastic Cloud** via AWS Marketplace (8.15+) with ELSER v2
  - 📖 Complete guide: [AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md)
  - 7-day free trial available
  - Everything billed via AWS

**Choose Your Environment:**
- [ ] **Option A**: SageMaker Jupyter (⭐ Recommended for AWS customers)
  - No local setup needed
  - IAM roles for automatic credentials
  - 📖 See [SAGEMAKER_SETUP.md](./SAGEMAKER_SETUP.md)
- [ ] **Option B**: Local Jupyter
  - Requires Python 3.9-3.11, Jupyter installed locally
  - Manual credential configuration

**Optional:**
- [ ] Terraform 1.0+ (for Lambda deployment)
- [ ] AWS CLI configured
- [ ] Strands API key (for real flight/hotel data)

### One-Command Deployment

```bash
# Clone repository
git clone https://github.com/elastic/travel-agent-workshop.git
cd travel-agent-workshop

# Configure (update with your values)
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# Deploy entire infrastructure
cd terraform
terraform init
terraform apply -auto-approve

# Expected output:
# ✅ 8 Lambda functions deployed
# ✅ API Gateway configured
# ✅ DynamoDB tables created
# ✅ Secrets stored
# ✅ API endpoint: https://xxxxx.execute-api.us-east-1.amazonaws.com
```

### Verify Deployment

```bash
# Test API
curl -X POST https://YOUR-API-ENDPOINT/plan \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Plan a 5-day Tokyo trip for a family who loves technology and food",
    "budget": 5000
  }'

# Check Elastic APM traces in Kibana
# Navigate to: Kibana → APM → Services → travel-agent-core
```

---

## 🎯 Key Features (AWS + Elastic Advantages)

### 1. Elastic ELSER on AWS

**Zero-Shot Semantic Search** (No training required!)

```python
# Traditional search - requires exact matches
GET /travel-cities/_search
{
  "query": { "match": { "description": "romantic restaurant" }}
}
# Result: Only docs with these exact words

# ELSER search - understands meaning
GET /travel-cities/_search
{
  "query": {
    "text_expansion": {
      "description_embedding": {
        "model_id": ".elser_model_2",
        "model_text": "romantic restaurant"
      }
    }
  }
}
# Result: Finds "candlelit dining", "intimate bistro", "sunset terrace"
#         Even in Spanish: "cena romántica" ✨
```

**ELSER Benefits for AWS Customers:**

| Feature | Advantage |
|---------|-----------|
| Data privacy | All data stays in your AWS VPC |
| Latency | Local Elasticsearch queries (no external calls) |
| Cost | Included in Elastic Cloud subscription |
| Training | Zero-shot learning (no training data needed) |
| Multi-lingual | Native cross-language support |
| Compliance | Runs in your AWS region of choice |

### 2. AWS Lambda Microservices

**8 specialized Lambda functions** with automatic scaling:

```
Agent Core (512MB RAM, 30s timeout)
├─> Destination Expert (256MB, 10s) - ELSER search
├─> Booking Assistant (512MB, 20s) - Strands API
├─> Activities Expert (256MB, 10s) - ELSER search
├─> Deal Comparator (256MB, 15s) - Price analysis
├─> Itinerary Builder (512MB, 20s) - AI planning
├─> Notification (128MB, 5s) - Twilio SMS
└─> Preference Manager (256MB, 10s) - DynamoDB

Cost: ~$0.50 per 1000 trips planned
```

### 3. Terraform Infrastructure as Code

Complete AWS + Elastic deployment:

```hcl
module "travel_agent" {
  source = "./terraform"

  # Elastic Cloud (already deployed on AWS)
  elastic_cloud_id = "your-cloud-id"
  elastic_password = var.elastic_password

  # AWS Configuration
  aws_region = "us-east-1"
  
  # Creates automatically:
  # - 8 Lambda functions
  # - API Gateway (HTTP API)
  # - DynamoDB tables (state, trips)
  # - VPC with private subnets
  # - Secrets Manager entries
  # - CloudWatch log groups
  # - IAM roles and policies
}
```

### 4. Production Observability

**Elastic APM** captures everything:

```
Travel Planning Request
├─ API Gateway: 2ms
├─ Lambda (Agent Core): 3247ms
│  ├─ Bedrock Claude: 1823ms
│  ├─ Destination search (ELSER): 145ms
│  ├─ Hotel search (Strands): 876ms
│  ├─ Activities search (ELSER): 132ms
│  ├─ Itinerary generation: 245ms
│  └─ SMS notification: 26ms
└─ Total: 3249ms

All traces visible in Kibana APM with:
• Full distributed tracing
• Cost per request
• Error tracking
• Performance bottlenecks
```

---

## 💰 Cost Analysis (For AWS + Elastic Customers)

### Workshop Costs (4 hours)

| Service | Usage | Cost |
|---------|-------|------|
| Elastic Cloud | Existing deployment | $0 |
| AWS Bedrock | ~50 requests | $0.75 |
| Lambda | 100 invocations | $0.00 (free tier) |
| API Gateway | 100 requests | $0.00 (free tier) |
| DynamoDB | On-demand | $0.00 (free tier) |
| **Total** | | **~$0.75** |

### Production Costs (1000 trips/month)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Elastic Cloud 16GB | 730 hours | $150 |
| ELSER compute | Included | $0 |
| Lambda | 8000 invocations | $3 |
| Bedrock Claude | 1000 requests | $15 |
| API Gateway | 1000 requests | $1 |
| DynamoDB | 10K reads/writes | $2 |
| Strands API | 2000 searches | $30 |
| CloudWatch | Logs/metrics | $5 |
| **Total** | | **$206/month** |

**Cost per trip: $0.21** (vs $2-5 with traditional solutions)

---

## 🛠️ Technology Stack (AWS + Elastic Native)

### AWS Services Used

- **Compute**: Lambda (Python 3.11)
- **AI/ML**: Bedrock (Claude 3.5 Sonnet)
- **API**: API Gateway (HTTP API, v2)
- **Storage**: DynamoDB (on-demand), S3
- **Security**: Secrets Manager, IAM
- **Networking**: VPC, NAT Gateway, Security Groups
- **Monitoring**: CloudWatch Logs, Metrics
- **IaC**: Terraform

### Elastic Platform

- **Search**: Elasticsearch 8.15+ on AWS
- **ML**: ELSER v2 model (zero-shot)
- **Observability**: APM, Logs, Metrics
- **Deployment**: Elastic Cloud on AWS Marketplace
- **Integrations**: AWS PrivateLink (optional)

### External Integrations

- **Strands API**: Real flight/hotel data
- **Twilio**: SMS notifications
- **MCP Protocol**: Tool standardization

---

## 📖 Module Overview

### [Module 0: Setup](./modules/module-0-setup/) (15 min)

**For AWS/Elastic customers - streamlined setup**

- Verify Elastic Cloud deployment on AWS
- Enable ELSER v2 (if not already)
- Configure AWS Bedrock access
- Set up Terraform backend
- Store credentials in Secrets Manager

**Expected state**: Ready to deploy

---

### [Module 1: ELSER + MCP Tools](./modules/module-1-elser/) (25 min)

**Deep dive into Elastic's competitive advantage**

- ELSER with external APIs embeddings comparison
- Index travel data with ELSER
- Cross-lingual search demonstration
- Build MCP tools for agents
- Performance benchmarking

**Deliverable**: Working semantic search with MCP tools

---

### [Module 2: Lambda Microservices](./modules/module-2-lambda/) (20 min)

**AWS serverless best practices**

- Deploy 8 Lambda functions via Terraform
- Configure VPC networking
- Set up async invocation patterns
- Implement retry logic
- Cost optimization techniques

**Deliverable**: Deployed microservices architecture

---

### [Module 3: Agent Orchestration](./modules/module-3-orchestration/) (30 min)

**Bedrock Claude + Elastic integration**

- Build agent core with tool calling
- Multi-tool orchestration
- State management with DynamoDB
- Error handling and retries
- Elastic APM instrumentation

**Deliverable**: Intelligent orchestrator

---

### [Module 4: Terraform Deployment](./modules/module-4-terraform/) (20 min)

**Infrastructure as code for production**

- Complete Terraform configuration
- Secrets management
- Network architecture
- Monitoring setup
- Disaster recovery

**Deliverable**: Production infrastructure

---

### [Module 5: Production Operations](./modules/module-5-operations/) (20 min)

**Running at scale**

- Elastic APM dashboards
- CloudWatch alarms
- Cost optimization
- A/B testing strategies
- Scaling Lambda concurrency

**Deliverable**: Operational playbook

---

## 🎓 Learning Outcomes

By the end of this workshop, you will have:

### Technical Skills

1. ✅ Deployed ELSER for semantic search
2. ✅ Built MCP-compliant tools
3. ✅ Created Lambda microservices
4. ✅ Integrated Bedrock with Elastic
5. ✅ Automated deployment with Terraform
6. ✅ Implemented production observability

### Business Value

1. ✅ Understand ROI of Elastic ELSER vs external APIs
2. ✅ Calculate total cost of ownership
3. ✅ Demonstrate value to stakeholders
4. ✅ Production-ready architecture patterns
5. ✅ Compliance and data privacy approach

---

## 🏢 For Your Organization

### AWS Customers

**Why add Elastic:**
- Keep sensitive data in your VPC
- Reduce API costs (ELSER with external APIs)
- Better performance (local vs external)
- Unified observability (APM + logs)
- Compliance simplified (data residency)

### Elastic Customers

**Why leverage AWS native services:**
- Serverless scaling (Lambda auto-scales)
- Managed infrastructure (no EC2 management)
- Native integrations (Bedrock, Secrets Manager)
- Cost-effective (pay-per-use Lambda)
- Familiar tools (Terraform, CloudWatch)

---

## 📊 Success Metrics

Track these after deployment:

### Performance
- P50 latency: < 2s
- P99 latency: < 5s
- ELSER query time: < 200ms
- End-to-end trip planning: < 4s

### Cost
- Per-trip cost: $0.15-0.25
- Lambda cost: < 10% of total
- Elastic cost: Largest component (justified by value)
- External APIs: Controllable via caching

### Quality
- Search relevance: > 90%
- Agent success rate: > 95%
- Error rate: < 1%
- User satisfaction: Measure with feedback

---

## 🔗 Resources

### Documentation
- [Elastic Cloud on AWS](https://www.elastic.co/guide/en/cloud/current/ec-aws-marketplace.html)
- [ELSER Documentation](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)
- [AWS Bedrock](https://docs.aws.amazon.com/bedrock/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

### Support
- Elastic Support Portal
- AWS Support (if Enterprise)
- GitHub Issues for workshop
- Community Slack

---

## ⚡ Next Steps

1. **Complete the workshop** (2 hours)
2. **Customize for your use case** (adapt travel → your domain)
3. **Deploy to your AWS account**
4. **Measure and optimize**
5. **Share results with stakeholders**

---

**Ready to build?** Start with [Module 0: Setup](./modules/module-0-setup/)

---

*Workshop Version 3.0 - Optimized for AWS + Elastic Customers*
*Deployment time: 2 hours | Production-ready: Yes*
