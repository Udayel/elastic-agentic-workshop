# Deployment Guide - Run Anywhere

Deploy the Travel Intelligence Agent in any AWS region with any configuration.

---

## 🌍 Supported Deployment Scenarios

### ✅ Fully Supported

- **AWS Regions**: All regions with Bedrock + Elastic Cloud
- **Elastic Cloud**: Any Elastic Cloud on AWS deployment
- **Network**: VPC, public subnets, private subnets, PrivateLink
- **Authentication**: IAM, API Keys, Cognito
- **Scale**: Development (minimal cost) to Production (high availability)

---

## 🚀 Quick Deploy (Any Region)

### Step 1: Prerequisites Check

```bash
# Check AWS CLI is configured
aws sts get-caller-identity

# Check Terraform is installed
terraform version

# Check Python is installed
python3 --version

# Check you have required permissions
aws iam get-user
```

### Step 2: Configure Variables

Create `terraform/terraform.tfvars`:

```hcl
# === Required Variables ===

# AWS Configuration
aws_region = "us-east-1"  # Change to your region
environment = "workshop"   # or "dev", "staging", "prod"

# Elastic Cloud (from your existing deployment)
elastic_cloud_id = "deployment:dXMtZWFzdC0x..."
elastic_username = "elastic"
elastic_password = "your-secure-password"

# Strands API (get from https://strands.com)
strands_api_key = "your-strands-api-key"

# Twilio SMS (optional - leave blank to skip SMS)
twilio_account_sid  = "AC..."
twilio_auth_token   = "your-token"
twilio_phone_number = "+1234567890"

# === Optional Variables (good defaults) ===

project_name = "travel-agent"  # Customize if needed
```

### Step 3: Deploy

```bash
cd terraform

# Initialize Terraform
terraform init

# Review what will be created
terraform plan

# Deploy (takes 5-7 minutes)
terraform apply -auto-approve

# Save outputs
terraform output > ../deployment-info.txt
```

### Step 4: Verify

```bash
# Test API endpoint (from terraform output)
API_ENDPOINT=$(terraform output -raw api_endpoint)

curl -X POST ${API_ENDPOINT}/health

# Expected: {"status": "healthy"}
```

---

## 🎯 Region-Specific Deployments

### US East (N. Virginia) - us-east-1

**Best for:** East coast US customers, lowest latency to US users

```hcl
aws_region = "us-east-1"

# Elastic Cloud should also be in us-east-1
# Bedrock available: ✅ All models
```

### US West (Oregon) - us-west-2

**Best for:** West coast US customers, Pacific region

```hcl
aws_region = "us-west-2"

# Elastic Cloud should also be in us-west-2
# Bedrock available: ✅ All models
```

### Europe (Ireland) - eu-west-1

**Best for:** European customers, GDPR compliance

```hcl
aws_region = "eu-west-1"

# Elastic Cloud should also be in eu-west-1
# Bedrock available: ✅ All models
# GDPR: ✅ Data stays in EU
```

### Asia Pacific (Singapore) - ap-southeast-1

**Best for:** APAC customers

```hcl
aws_region = "ap-southeast-1"

# Elastic Cloud should also be in ap-southeast-1
# Bedrock available: ✅ Claude models
```

### Other Regions

Check Bedrock availability: https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html#bedrock-regions

---

## 💰 Cost-Optimized Deployments

### Minimal (Development) - ~$5/month

```hcl
# terraform/environments/dev.tfvars

environment = "dev"

# Use smallest Lambda sizes
lambda_memory_mb = 256
lambda_timeout_sec = 30

# Single NAT Gateway (not HA)
enable_nat_gateway = true
single_nat_gateway = true

# On-demand DynamoDB
dynamodb_billing_mode = "PAY_PER_REQUEST"

# Minimal CloudWatch retention
log_retention_days = 3
```

```bash
terraform apply -var-file="environments/dev.tfvars"
```

### Production (High Availability) - ~$250/month

```hcl
# terraform/environments/prod.tfvars

environment = "prod"

# Optimized Lambda sizes
lambda_memory_mb = 512
lambda_timeout_sec = 60

# Multi-AZ with redundant NAT
enable_nat_gateway = true
single_nat_gateway = false  # One per AZ

# Provisioned DynamoDB for predictable performance
dynamodb_billing_mode = "PROVISIONED"
dynamodb_read_capacity = 5
dynamodb_write_capacity = 5

# Standard log retention
log_retention_days = 30

# Enable enhanced monitoring
enable_enhanced_monitoring = true
```

---

## 🔐 Security Configurations

### Public API (Default)

```hcl
# terraform/terraform.tfvars

# API Gateway is public with API key authentication
api_gateway_type = "REGIONAL"
enable_api_keys = true
```

**Use for:**
- Public-facing travel apps
- Mobile applications
- External partners

### Private API (VPC Only)

```hcl
# terraform/terraform.tfvars

# API Gateway private with VPC endpoint
api_gateway_type = "PRIVATE"
vpc_endpoint_enabled = true

# Only accessible from your VPC
```

**Use for:**
- Internal applications
- Corporate environments
- Maximum security

### Cognito Authentication

```hcl
# terraform/terraform.tfvars

enable_cognito = true
cognito_user_pool_name = "travel-agent-users"

# Require authenticated users
require_authentication = true
```

**Use for:**
- Consumer applications
- User account management
- OAuth/OIDC integration

---

## 🌐 Network Configurations

### Standard VPC (Default)

```
Public Subnets (NAT Gateways)
    ↓
Private Subnets (Lambda Functions)
    ↓
Internet via NAT → Elastic Cloud
```

**Best for:** Most deployments

### Elastic Cloud PrivateLink

```hcl
# terraform/terraform.tfvars

elastic_private_link_enabled = true
elastic_vpc_endpoint_service = "com.amazonaws.vpce..."
```

```
Private Subnets (Lambda)
    ↓
VPC Endpoint (PrivateLink)
    ↓
Elastic Cloud (no internet)
```

**Best for:**
- Maximum security
- Compliance requirements
- No internet egress

### Shared VPC

```hcl
# terraform/terraform.tfvars

# Use existing VPC
use_existing_vpc = true
vpc_id = "vpc-12345678"
private_subnet_ids = ["subnet-aaa", "subnet-bbb"]
```

**Best for:**
- Existing AWS infrastructure
- Centralized networking
- Multi-account setups

---

## 📦 Lambda Deployment Packages

### Create Deployment Packages

```bash
# Run from project root
./scripts/build-lambda-packages.sh

# Creates:
# - build/agent-core.zip
# - build/destination-expert.zip
# - build/booking-assistant.zip
# - build/activities-expert.zip
# - build/deal-comparator.zip
# - build/itinerary-builder.zip
# - build/notification.zip
# - build/preference-mgr.zip
# - build/lambda-layer.zip (shared dependencies)
```

### Manual Package Creation

```bash
# For any Lambda function
mkdir -p build/temp
cd build/temp

# Copy function code
cp ../../services/lambda/agent-core/*.py .

# Install dependencies
pip install -r requirements.txt -t .

# Create zip
zip -r ../agent-core.zip .

# Clean up
cd ../..
rm -rf build/temp
```

### Automated CI/CD

```yaml
# .github/workflows/deploy.yml

name: Deploy Lambda Functions

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build packages
        run: ./scripts/build-lambda-packages.sh
      
      - name: Deploy with Terraform
        run: |
          cd terraform
          terraform init
          terraform apply -auto-approve
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## 🔄 Update Deployments

### Update Lambda Code Only

```bash
# Build new packages
./scripts/build-lambda-packages.sh

# Update functions
cd terraform
terraform apply -target=module.lambda_functions

# Or update specific function
aws lambda update-function-code \
  --function-name travel-agent-core \
  --zip-file fileb://../build/agent-core.zip
```

### Update Infrastructure

```bash
cd terraform

# Pull latest changes
git pull

# Plan changes
terraform plan -out=tfplan

# Review and apply
terraform apply tfplan
```

### Zero-Downtime Updates

```bash
# Use Lambda aliases and versions

# Publish new version
VERSION=$(aws lambda publish-version \
  --function-name travel-agent-core \
  --query 'Version' --output text)

# Update alias gradually
aws lambda update-alias \
  --function-name travel-agent-core \
  --name prod \
  --function-version $VERSION \
  --routing-config AdditionalVersionWeights={$OLD_VERSION=0.1}

# Monitor, then route 100% to new version
aws lambda update-alias \
  --function-name travel-agent-core \
  --name prod \
  --function-version $VERSION
```

---

## 🧪 Testing Deployments

### Smoke Tests

```bash
# Test health endpoint
curl ${API_ENDPOINT}/health

# Test search functionality
curl -X POST ${API_ENDPOINT}/search/destinations \
  -H "Content-Type: application/json" \
  -d '{"query": "beach destination"}'

# Test full agent
curl -X POST ${API_ENDPOINT}/plan \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "query": "Plan a 5-day Tokyo trip",
    "budget": 5000
  }'
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 -p request.json -T application/json \
  ${API_ENDPOINT}/plan

# Results show requests/second and latency
```

### Integration Tests

```python
# tests/test_integration.py

import pytest
import requests
import os

API_ENDPOINT = os.getenv('API_ENDPOINT')
API_KEY = os.getenv('API_KEY')

def test_destination_search():
    response = requests.post(
        f"{API_ENDPOINT}/search/destinations",
        json={"query": "romantic beach"},
        headers={"x-api-key": API_KEY}
    )
    assert response.status_code == 200
    assert len(response.json()['destinations']) > 0

def test_full_trip_planning():
    response = requests.post(
        f"{API_ENDPOINT}/plan",
        json={
            "query": "5-day Tokyo trip for family",
            "budget": 5000
        },
        headers={"x-api-key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'itinerary' in data
    assert data['budget_used'] <= 5000

# Run tests
pytest tests/test_integration.py -v
```

---

## 📊 Monitoring Deployments

### CloudWatch Dashboard

```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name TravelAgentMetrics \
  --dashboard-body file://dashboards/main-dashboard.json
```

### Elastic APM

```python
# Already instrumented in Lambda code
# View in Kibana:
# https://your-elastic.kb.aws.found.io/app/apm
```

### Alarms

```bash
# High error rate
aws cloudwatch put-metric-alarm \
  --alarm-name travel-agent-errors \
  --alarm-description "Lambda error rate > 5%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# High latency
aws cloudwatch put-metric-alarm \
  --alarm-name travel-agent-latency \
  --alarm-description "API latency > 5 seconds" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 60 \
  --threshold 5000 \
  --comparison-operator GreaterThanThreshold
```

---

## 🗑️ Clean Up

### Remove Everything

```bash
cd terraform

# Destroy all infrastructure
terraform destroy -auto-approve

# Verify deletion
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `travel-agent`)]'
aws dynamodb list-tables --query 'TableNames[?starts_with(@, `travel-agent`)]'
```

### Remove Specific Components

```bash
# Remove Lambda functions only
terraform destroy -target=module.lambda_functions

# Remove DynamoDB tables only
terraform destroy -target=aws_dynamodb_table.agent_state
terraform destroy -target=aws_dynamodb_table.trip_data
```

---

## 🆘 Troubleshooting

### Common Issues

**Issue:** Terraform timeout during apply
```bash
# Solution: Increase timeout
export TF_CLI_ARGS="-parallelism=1"
terraform apply
```

**Issue:** Lambda function not connecting to Elastic
```bash
# Check security group allows HTTPS egress
aws ec2 describe-security-groups --group-ids sg-xxx

# Check NAT Gateway is working
aws ec2 describe-nat-gateways

# Check Elastic endpoint is correct
aws secretsmanager get-secret-value --secret-id travel-agent-elastic-credentials
```

**Issue:** API Gateway 403 errors
```bash
# Check API key is provided
curl -H "x-api-key: YOUR_KEY" ${API_ENDPOINT}/health

# Check usage plan is attached
aws apigateway get-usage-plans
```

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] Review and customize `terraform.tfvars`
- [ ] Choose appropriate AWS region
- [ ] Size Lambda functions appropriately
- [ ] Configure network (VPC/PrivateLink)
- [ ] Set up authentication (API keys/Cognito)
- [ ] Enable monitoring and alarms
- [ ] Test in non-production environment first
- [ ] Document custom configurations
- [ ] Set up backup procedures
- [ ] Configure log retention
- [ ] Review security settings (SECURITY.md)
- [ ] Set up CI/CD pipeline (optional)
- [ ] Train team on operations
- [ ] Create runbooks for common tasks

---

## 📚 Additional Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Elastic Cloud on AWS](https://www.elastic.co/guide/en/cloud/current/ec-aws-marketplace.html)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)

---

**Deploy anywhere, run securely, scale infinitely.** 🚀

*Last Updated: June 18, 2026*
