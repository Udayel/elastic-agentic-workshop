# Travel Intelligence Agent Workshop
## For AWS + Elastic Customers

**Build production AI agents leveraging your existing AWS and Elastic infrastructure**

Transform travel planning with intelligent agents powered by Elastic ELSER on AWS

---

## NEW: AWS Marketplace & SageMaker Support (v3.2)

### Get Elastic Cloud via AWS Marketplace

- **Unified AWS billing** - Pay via your AWS account
- **Use AWS credits** - Apply promotional credits to Elastic
- **7-day free trial** - Start exploring immediately
- **Same-day setup** - Running in AWS in 20 minutes

**[AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md)** - Complete subscription guide

---

### Run Workshop in Amazon SageMaker

- **No local setup** - Everything in AWS cloud
- **Auto AWS credentials** - IAM role integration
- **Low latency** - Same region as Bedrock
- **Cost-effective** - ~$0.05/hour or FREE (Studio Lab)

**[SAGEMAKER_SETUP.md](./SAGEMAKER_SETUP.md)** - 3 SageMaker options explained

**Compare all setup options**: [SETUP_COMPARISON.md](./SETUP_COMPARISON.md)

---

## Workshop Overview

This hands-on workshop is designed for **AWS and Elastic customers** who want to build production-grade AI agents. We assume you're already familiar with:

- AWS services (Lambda, API Gateway, DynamoDB, Bedrock, SageMaker)
- Elastic Cloud from AWS Marketplace
- Terraform infrastructure as code
- Microservices architecture patterns

### What You'll Build

A complete **Travel Intelligence Agent** system that showcases:

1. **Elastic ELSER** for zero-shot semantic search
2. **AWS Bedrock Claude** for agent reasoning
3. **Microservices on Lambda** - 8 specialized services
4. **Terraform automation** - one-command deployment
5. **MCP tools** for agent capabilities
6. **Production observability** with Elastic APM
7. **Real integrations** - Strands API connector

### Why This Matters for AWS Customers

**Native AWS Integration:**
- **Pay via AWS** - Elastic Cloud billed through AWS Marketplace
- **Use AWS credits** - Apply promotional credits to Elastic
- **Same region** - Deploy Elastic in same AWS region as Lambda/Bedrock
- **VPC connectivity** - Optional PrivateLink for secure access
- **IAM roles** - SageMaker notebooks use IAM for credentials
- **CloudTrail** - Unified audit logging across services
- **Cost Explorer** - Track all costs in one place

**Familiar AWS Patterns:**
- Terraform for infrastructure as code
- Lambda for serverless microservices
- API Gateway for REST endpoints
- DynamoDB for state management
- Bedrock for AI/ML inference
- SageMaker for Jupyter notebooks

---

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed AWS Solutions Architecture diagram with VPC, subnets, and security groups.

### High-Level Architecture

```
Internet Gateway
       |
   API Gateway
       |
   +---------+
   |   VPC   |
   |         |
   | +---------------------+
   | | Public Subnet       |
   | | - NAT Gateway       |
   | +---------------------+
   |         |
   | +---------------------+
   | | Private Subnet 1    |
   | | - Lambda Functions  |
   | | - Bedrock Access    |
   | +---------------------+
   |         |
   | +---------------------+
   | | Private Subnet 2    |
   | | - DynamoDB         |
   | | - Secrets Manager  |
   | +---------------------+
   +---------+
       |
   Elastic Cloud
   (AWS Marketplace)
```

### Components

**AWS Services:**
- API Gateway (Regional HTTP API)
- Lambda Functions (8 microservices)
- Bedrock (Claude 3.5 Sonnet)
- DynamoDB (state management)
- Secrets Manager (credentials)
- CloudWatch (logs & metrics)
- S3 (artifacts)
- VPC with public/private subnets
- NAT Gateway
- Security Groups

**Elastic Cloud (via AWS Marketplace):**
- Elasticsearch 8.15+
- ELSER v2 model
- Vector database
- APM (Application Performance Monitoring)
- AgenticBuilder (notifications)

---

## Quick Start (For AWS Customers)

### Step 0: Get Elastic Cloud via AWS Marketplace - START HERE

**All AWS customers should start here:**

**[AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md)** (20 minutes)

**What you'll do:**
1. Subscribe to Elastic Cloud on AWS Marketplace
2. Deploy Elastic in your AWS region (same as Lambda/Bedrock)
3. Enable ELSER v2 model for semantic search
4. Request AWS Bedrock model access (Claude 3.5)

**Why AWS Marketplace:**
- **Pay via AWS** - Everything on one AWS bill
- **Use AWS credits** - Apply promotional credits
- **7-day free trial** - Start exploring immediately
- **Faster procurement** - Already approved via AWS
- **Native integration** - Stays in AWS ecosystem

---

### Prerequisites Checklist

**Required:**
- AWS Account (active account with billing enabled)
- AWS Bedrock access - Request Claude 3.5 Sonnet model access
  - Go to AWS Console → Bedrock → Model access → Request
- Elastic Cloud via AWS Marketplace (8.15+) with ELSER v2
  - Complete guide: [AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md)
  - 7-day free trial available
  - Everything billed via AWS

**Choose Your Environment:**
- **Option A**: SageMaker Jupyter (Recommended for AWS customers)
  - No local setup needed
  - IAM roles for automatic credentials
  - See [SAGEMAKER_SETUP.md](./SAGEMAKER_SETUP.md)
- **Option B**: Local Jupyter
  - Requires Python 3.9-3.11, Jupyter installed locally
  - Manual credential configuration

**Optional:**
- Terraform 1.0+ (for Lambda deployment)
- AWS CLI configured
- Strands API key (for real flight/hotel data)

---

### One-Command Deployment

```bash
# Clone repository
git clone https://github.com/Udayel/elastic-agentic-workshop.git
cd elastic-agentic-workshop

# Configure (update with your values)
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
nano terraform/terraform.tfvars

# Deploy entire infrastructure
cd terraform
terraform init
terraform apply -auto-approve

# Expected output:
# - 8 Lambda functions deployed
# - API Gateway configured
# - DynamoDB tables created
# - Secrets stored
# - VPC with subnets created
# - API endpoint: https://xxxxx.execute-api.us-east-1.amazonaws.com
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

## Workshop Modules (Fast Track for AWS/Elastic Users)

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

## Key Features (AWS + Elastic Advantages)

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
#         Even in Spanish: "cena romántica"
```

**ELSER Benefits for AWS Customers:**

| Feature | Benefit | AWS Integration |
|---------|---------|-----------------|
| **Zero-shot learning** | No training data needed | Deploy immediately in AWS region |
| **Cross-lingual** | 100+ languages supported | Same latency for all languages |
| **Fast inference** | Sub-100ms queries | Elastic in same AWS AZ |
| **No external API** | Runs in Elasticsearch | No API Gateway overhead |
| **Cost effective** | Included in Elastic | Billed via AWS Marketplace |
| **Secure** | Data stays in your VPC | Optional PrivateLink |

### 2. AWS Bedrock Integration

**Claude 3.5 Sonnet** for agent reasoning

```python
import boto3

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": "Plan a Tokyo trip"}],
        "tools": mcp_tools  # MCP-compliant tool definitions
    })
)
```

**Bedrock Advantages:**
- Pay-per-use pricing ($3 per 1M input tokens)
- No infrastructure management
- Streaming responses supported
- Native IAM authentication
- CloudWatch metrics included

### 3. Strands Native Integration

**Real-time flight and hotel data via Strands API**

```python
from strands_connector import StrandsElasticConnector

strands = StrandsElasticConnector(
    es_client=es,
    strands_api_key=os.getenv('STRANDS_API_KEY')
)

# Search flights with Strands + ELSER
flights = strands.search_flights_with_strands(
    origin="SFO",
    destination="NRT",
    departure_date="2026-07-15",
    budget_level="medium"
)

# Results indexed in Elasticsearch with ELSER embeddings
# Searchable semantically: "cheap direct flights to Tokyo"
```

**Strands Benefits:**
- Native Elasticsearch connector
- Real-time flight/hotel data
- Financial context (PFM integration)
- Auto-indexed with ELSER
- No external API latency

### 4. Lambda Microservices Architecture

**8 specialized Lambda functions:**

1. **Agent Core** - Bedrock Claude orchestration, conversation state
2. **Destination Expert** - ELSER semantic search for cities
3. **Booking Assistant** - Strands integration for flights/hotels
4. **Activities Expert** - ELSER search for activities and restaurants
5. **Deal Comparator** - Price analysis and recommendations
6. **Itinerary Builder** - Multi-day trip planning
7. **Notification Service** - AgenticBuilder SMS/email
8. **Preference Manager** - User profile and preferences

**Architecture Benefits:**
- Independent scaling per function
- Pay-per-invocation pricing
- Sub-second cold starts
- Native AWS service integration
- VPC isolation for security

---

## Complete End-to-End Guide

For step-by-step instructions from zero to production:

**[END_TO_END_GUIDE.md](./END_TO_END_GUIDE.md)** - Complete 90-120 minute walkthrough

**Phases:**
1. AWS Infrastructure Setup (20 min)
2. SageMaker Notebook Setup (15 min)
3. ELSER Configuration (15 min)
4. MCP Tools Testing (20 min)
5. Lambda Deployment (20 min)
6. End-to-End Verification (10 min)

---

## Documentation

### Getting Started
- [INDEX.md](./INDEX.md) - Central navigation hub
- [AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md) - Elastic Cloud setup
- [SAGEMAKER_SETUP.md](./SAGEMAKER_SETUP.md) - SageMaker notebook options
- [SETUP_COMPARISON.md](./SETUP_COMPARISON.md) - Compare all setup paths
- [QUICKSTART.md](./QUICKSTART.md) - 30-minute quick start

### Architecture & Deployment
- [ARCHITECTURE.md](./ARCHITECTURE.md) - AWS Solutions Architecture diagram
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment guide
- [SECURITY.md](./SECURITY.md) - Security best practices
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Technical deep dive

### Workshop Materials
- [notebooks/](./notebooks/) - Jupyter notebooks for hands-on learning
- [modules/](./modules/) - Step-by-step workshop modules
- [terraform/](./terraform/) - Infrastructure as Code
- [services/](./services/) - Service implementations

### Reference
- [LATEST_UPDATES.md](./LATEST_UPDATES.md) - Recent improvements
- [WHATS_NEW_V3.2.md](./WHATS_NEW_V3.2.md) - Version 3.2 changelog
- [PROJECT_STATUS.md](./PROJECT_STATUS.md) - Current status
- [SECURITY_AUDIT.md](./SECURITY_AUDIT.md) - Security verification

---

## Cost Breakdown

### Workshop Cost (7-day trial)

| Service | Usage | Cost |
|---------|-------|------|
| **Elastic Cloud** | 7-day trial | **$0** |
| After trial (optional) | ~3 hours testing | ~$0.50 |
| **SageMaker** | ml.t3.medium, 2 hours | $0.12 |
| **Bedrock (Claude)** | ~2M tokens | $6-8 |
| **Lambda** | ~1000 invocations | $0.02 |
| **API Gateway** | ~1000 requests | $0.01 |
| **DynamoDB** | On-demand, minimal | $0.01 |
| **VPC** | NAT Gateway, 2 hours | $0.09 |
| **CloudWatch** | Logs | $0.01 |
| **Total** | **Full workshop** | **~$6-8** |

**After cleanup**: $0 ongoing cost (delete all resources)

### Production Cost Estimate (per month)

| Service | Configuration | Est. Cost |
|---------|--------------|-----------|
| **Elastic Cloud** | Standard (8GB ES + 4GB ML) | $95 |
| **Lambda** | 1M invocations/month | $0.20 |
| **Bedrock** | 10M tokens/month | $30 |
| **DynamoDB** | On-demand, 1M requests | $1.25 |
| **API Gateway** | 1M requests | $3.50 |
| **VPC** | NAT Gateway | $32 |
| **CloudWatch** | Standard logs | $5 |
| **Total** | **Production workload** | **~$167/month** |

**Cost optimization:** Use AWS Savings Plans, Reserved Instances, and Elastic Cloud discounts for 30-40% savings.

---

## Technology Stack

### AWS Services
- **Compute:** Lambda (Python 3.11 runtime)
- **AI/ML:** Bedrock (Claude 3.5 Sonnet)
- **API:** API Gateway (HTTP API)
- **Database:** DynamoDB (on-demand)
- **Storage:** S3 (standard)
- **Security:** Secrets Manager, IAM roles
- **Networking:** VPC, NAT Gateway, Security Groups
- **Monitoring:** CloudWatch Logs, CloudWatch Metrics
- **Development:** SageMaker Notebooks

### Elastic Stack (via AWS Marketplace)
- **Search:** Elasticsearch 8.15+
- **ML:** ELSER v2 (Elastic Learned Sparse Encoder)
- **Monitoring:** APM (Application Performance Monitoring)
- **Notifications:** AgenticBuilder
- **Deployment:** Elastic Cloud on AWS

### Infrastructure & Tools
- **IaC:** Terraform 1.0+
- **Language:** Python 3.9-3.11
- **Notebooks:** Jupyter
- **Integration:** Strands API connector
- **Version Control:** Git

---

## Production Features

### Security
- VPC isolation with private subnets
- IAM roles for service-to-service authentication
- Secrets Manager for credential management
- Encryption at rest (DynamoDB, S3)
- Encryption in transit (TLS 1.2+)
- Security groups restricting traffic
- CloudTrail audit logging
- Optional PrivateLink to Elastic Cloud

### Observability
- Elastic APM for distributed tracing
- CloudWatch Logs for all Lambda functions
- CloudWatch Metrics for performance monitoring
- Custom metrics for business KPIs
- Kibana dashboards for visualization
- Alert configuration via CloudWatch Alarms

### Scalability
- Lambda auto-scales to 1000 concurrent executions
- DynamoDB on-demand scales automatically
- Elastic Cloud auto-scales storage
- API Gateway handles 10,000 RPS+
- Multi-AZ deployment for high availability

### Reliability
- Multi-AZ VPC architecture
- Lambda retry logic with exponential backoff
- DynamoDB point-in-time recovery
- S3 versioning for artifacts
- Elastic Cloud snapshots (daily)
- Circuit breakers for external APIs

---

## Support & Community

### Getting Help
- **GitHub Issues:** [Report bugs or request features](https://github.com/Udayel/elastic-agentic-workshop/issues)
- **AWS Support:** For AWS service issues
- **Elastic Support:** For Elastic Cloud issues
- **Documentation:** Check [INDEX.md](./INDEX.md) for all resources

### Contributing
We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### License
This project is licensed under the Apache License 2.0 - see [LICENSE](./LICENSE) file for details.

---

## Acknowledgments

Built with:
- **AWS Bedrock** for Claude 3.5 Sonnet
- **Elastic ELSER** for semantic search
- **Strands API** for travel data
- **Terraform** for infrastructure automation
- **Model Context Protocol (MCP)** for tool definitions

---

**Version:** 3.2 - AWS Marketplace & SageMaker Edition  
**Last Updated:** June 18, 2026  
**Repository:** https://github.com/Udayel/elastic-agentic-workshop

---

## Quick Links

- [Start Workshop](./END_TO_END_GUIDE.md)
- [AWS Marketplace Setup](./AWS_MARKETPLACE_SETUP.md)
- [Architecture Diagram](./ARCHITECTURE.md)
- [Notebooks](./notebooks/)
- [Terraform Code](./terraform/)
