# AWS Solutions Architecture

## Travel Intelligence Agent - Production Architecture

**Version:** 3.2  
**Last Updated:** June 18, 2026  
**Architecture Style:** AWS Well-Architected Framework

---

## Architecture Diagram

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Internet / Users                                │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     │ HTTPS
                                     │
┌────────────────────────────────────▼────────────────────────────────────────┐
│                           AWS Cloud (us-east-1)                              │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Amazon API Gateway                             │   │
│  │                    (Regional HTTP API)                               │   │
│  │                                                                       │   │
│  │  - REST API endpoints                                                │   │
│  │  - CORS enabled                                                      │   │
│  │  - Request validation                                                │   │
│  │  - Rate limiting: 10,000 RPS                                        │   │
│  └────────────────────────────────┬─────────────────────────────────────┘   │
│                                   │                                          │
│  ┌────────────────────────────────▼──────────────────────────────────────┐  │
│  │                                VPC                                     │  │
│  │                         (10.0.0.0/16)                                 │  │
│  │                                                                        │  │
│  │  ┌──────────────────────────────────────────────────────────────┐   │  │
│  │  │            Availability Zone us-east-1a                       │   │  │
│  │  │                                                                │   │  │
│  │  │  ┌────────────────────────────────────────────────────┐     │   │  │
│  │  │  │  Public Subnet (10.0.1.0/24)                       │     │   │  │
│  │  │  │                                                     │     │   │  │
│  │  │  │  ┌──────────────┐         ┌──────────────┐        │     │   │  │
│  │  │  │  │ NAT Gateway  │         │ Internet     │        │     │   │  │
│  │  │  │  │ (Managed)    │◄────────│ Gateway      │        │     │   │  │
│  │  │  │  └──────┬───────┘         └──────────────┘        │     │   │  │
│  │  │  └─────────┼─────────────────────────────────────────┘     │   │  │
│  │  │            │                                                 │   │  │
│  │  │            │ Route                                           │   │  │
│  │  │            │                                                 │   │  │
│  │  │  ┌─────────▼────────────────────────────────────────┐     │   │  │
│  │  │  │  Private Subnet 1 (10.0.10.0/24)                │     │   │  │
│  │  │  │  (Application Layer)                             │     │   │  │
│  │  │  │                                                   │     │   │  │
│  │  │  │  ┌─────────────────────────────────────────┐   │     │   │  │
│  │  │  │  │    AWS Lambda Functions                  │   │     │   │  │
│  │  │  │  │    (VPC-enabled)                         │   │     │   │  │
│  │  │  │  │                                           │   │     │   │  │
│  │  │  │  │  - Agent Core                            │   │     │   │  │
│  │  │  │  │  - Destination Expert                    │   │     │   │  │
│  │  │  │  │  - Booking Assistant                     │   │     │   │  │
│  │  │  │  │  - Activities Expert                     │   │     │   │  │
│  │  │  │  │  - Deal Comparator                       │   │     │   │  │
│  │  │  │  │  - Itinerary Builder                     │   │     │   │  │
│  │  │  │  │  - Notification Service                  │   │     │   │  │
│  │  │  │  │  - Preference Manager                    │   │     │   │  │
│  │  │  │  │                                           │   │     │   │  │
│  │  │  │  │  Runtime: Python 3.11                    │   │     │   │  │
│  │  │  │  │  Memory: 512MB - 1024MB                  │   │     │   │  │
│  │  │  │  │  Timeout: 60 seconds                     │   │     │   │  │
│  │  │  │  │  Concurrency: 100 per function           │   │     │   │  │
│  │  │  │  └─────────────────────────────────────────┘   │     │   │  │
│  │  │  │                      │                           │     │   │  │
│  │  │  │                      │ IAM Role                  │     │   │  │
│  │  │  │                      ▼                           │     │   │  │
│  │  │  │  ┌─────────────────────────────────────────┐   │     │   │  │
│  │  │  │  │    Security Group (Lambda-SG)            │   │     │   │  │
│  │  │  │  │    - Inbound: None                       │   │     │   │  │
│  │  │  │  │    - Outbound: HTTPS (443)               │   │     │   │  │
│  │  │  │  │    - Outbound: Elastic (9243)            │   │     │   │  │
│  │  │  │  └─────────────────────────────────────────┘   │     │   │  │
│  │  │  └───────────────────────────────────────────────┘     │   │  │
│  │  │                                                          │   │  │
│  │  │  ┌────────────────────────────────────────────────┐   │   │  │
│  │  │  │  Private Subnet 2 (10.0.20.0/24)              │   │   │  │
│  │  │  │  (Data Layer)                                  │   │   │  │
│  │  │  │                                                 │   │   │  │
│  │  │  │  ┌──────────────────────────────────────┐    │   │   │  │
│  │  │  │  │  VPC Endpoint - DynamoDB              │    │   │   │  │
│  │  │  │  └──────────────────────────────────────┘    │   │   │  │
│  │  │  │                                                 │   │   │  │
│  │  │  │  ┌──────────────────────────────────────┐    │   │   │  │
│  │  │  │  │  VPC Endpoint - Secrets Manager       │    │   │   │  │
│  │  │  │  └──────────────────────────────────────┘    │   │   │  │
│  │  │  │                                                 │   │   │  │
│  │  │  │  ┌──────────────────────────────────────┐    │   │   │  │
│  │  │  │  │  VPC Endpoint - S3                    │    │   │   │  │
│  │  │  │  └──────────────────────────────────────┘    │   │   │  │
│  │  │  └─────────────────────────────────────────────┘   │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────────┐   │  │
│  │  │            Availability Zone us-east-1b                   │   │  │
│  │  │                                                            │   │  │
│  │  │  (Same subnet configuration for high availability)        │   │  │
│  │  └──────────────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    AWS Managed Services                         │  │
│  │                                                                  │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐             │  │
│  │  │  Amazon DynamoDB    │  │  Amazon Bedrock     │             │  │
│  │  │                     │  │                     │             │  │
│  │  │  Tables:            │  │  Model: Claude 3.5  │             │  │
│  │  │  - agent-state      │  │  Sonnet             │             │  │
│  │  │  - trip-data        │  │                     │             │  │
│  │  │  - user-preferences │  │  Pricing:           │             │  │
│  │  │                     │  │  $3/1M input tokens │             │  │
│  │  │  Billing: On-demand │  │  $15/1M out tokens  │             │  │
│  │  │  Capacity: Auto     │  │                     │             │  │
│  │  └─────────────────────┘  └─────────────────────┘             │  │
│  │                                                                  │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐             │  │
│  │  │  AWS Secrets        │  │  Amazon S3          │             │  │
│  │  │  Manager            │  │                     │             │  │
│  │  │                     │  │  Bucket:            │             │  │
│  │  │  Secrets:           │  │  - artifacts        │             │  │
│  │  │  - elastic-creds    │  │  - logs backup      │             │  │
│  │  │  - strands-api-key  │  │                     │             │  │
│  │  │                     │  │  Encryption: AES256 │             │  │
│  │  │  Encryption: KMS    │  │  Versioning: On     │             │  │
│  │  │  Rotation: 90 days  │  │                     │             │  │
│  │  └─────────────────────┘  └─────────────────────┘             │  │
│  │                                                                  │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐             │  │
│  │  │  CloudWatch Logs    │  │  CloudWatch         │             │  │
│  │  │                     │  │  Metrics            │             │  │
│  │  │  Log Groups:        │  │                     │             │  │
│  │  │  - /aws/lambda/*    │  │  Custom Metrics:    │             │  │
│  │  │  - /aws/apigateway  │  │  - API latency      │             │  │
│  │  │                     │  │  - Token usage      │             │  │
│  │  │  Retention: 7 days  │  │  - Error rates      │             │  │
│  │  └─────────────────────┘  └─────────────────────┘             │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    Elastic Cloud on AWS (via Marketplace)                    │
│                                                                               │
│  Region: us-east-1 (same as Lambda)                                         │
│  Connection: Internet Gateway (or PrivateLink for production)               │
│                                                                               │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐   │
│  │  Elasticsearch      │  │  Machine Learning   │  │  Kibana          │   │
│  │                     │  │                     │  │                  │   │
│  │  Version: 8.15+     │  │  ELSER v2 Model     │  │  Version: 8.15+  │   │
│  │  Nodes: 2 x 8GB     │  │  Nodes: 1 x 4GB     │  │  1GB RAM         │   │
│  │  Storage: 256GB     │  │                     │  │                  │   │
│  │                     │  │  Inference:         │  │  Features:       │   │
│  │  Indices:           │  │  - Semantic search  │  │  - APM UI        │   │
│  │  - travel-cities    │  │  - Cross-lingual    │  │  - Dashboards    │   │
│  │  - travel-hotels    │  │  - Sub-100ms        │  │  - Dev Tools     │   │
│  │  - travel-flights   │  │                     │  │                  │   │
│  │  - agent-traces     │  │                     │  │                  │   │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘   │
│                                                                               │
│  ┌─────────────────────┐  ┌─────────────────────┐                          │
│  │  APM Server         │  │  AgenticBuilder     │                          │
│  │                     │  │                     │                          │
│  │  Distributed traces │  │  SMS Notifications  │                          │
│  │  Performance        │  │  Email Alerts       │                          │
│  │  monitoring         │  │  Native to Elastic  │                          │
│  └─────────────────────┘  └─────────────────────┘                          │
│                                                                               │
│  Billing: Via AWS Marketplace                                               │
│  Cost: ~$95/month (standard configuration)                                  │
│  Trial: 7 days free                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         External Services (Optional)                         │
│                                                                               │
│  ┌─────────────────────┐                                                    │
│  │  Strands API        │                                                    │
│  │                     │                                                    │
│  │  - Flight data      │                                                    │
│  │  - Hotel data       │                                                    │
│  │  - PFM integration  │                                                    │
│  │                     │                                                    │
│  │  Auth: API Key      │                                                    │
│  │  (Stored in Secrets │                                                    │
│  │   Manager)          │                                                    │
│  └─────────────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Network Flow

### Request Flow (User → Response)

```
1. User Request
   │
   ├─→ API Gateway (HTTPS)
   │   - TLS termination
   │   - Request validation
   │   - Rate limiting
   │
2. API Gateway → Lambda (Async)
   │
   ├─→ Lambda (Private Subnet 1)
   │   - IAM role authentication
   │   - Security group enforcement
   │
3. Lambda → AWS Services
   │
   ├─→ Bedrock (Claude 3.5)
   │   - AI reasoning
   │   - Tool use
   │
   ├─→ DynamoDB (VPC Endpoint)
   │   - State management
   │   - Trip data storage
   │
   ├─→ Secrets Manager (VPC Endpoint)
   │   - Credential retrieval
   │
   └─→ S3 (VPC Endpoint)
       - Artifact storage
   │
4. Lambda → Elastic Cloud
   │
   ├─→ NAT Gateway (Public Subnet)
   │   - Outbound internet access
   │
   └─→ Elastic Cloud (Internet Gateway)
       - ELSER search
       - Vector database
       - APM traces
   │
5. Response Path
   │
   └─→ Lambda → API Gateway → User
       - JSON response
       - CloudWatch logs
```

### Internal Communication

```
Lambda Function A
    │
    ├─→ Step Function (Optional)
    │   - Workflow orchestration
    │
    └─→ Lambda Function B
        - Async invocation
        - Event-driven
```

---

## Security Architecture

### Network Security

```
┌─────────────────────────────────────┐
│  Security Layer 1: Network ACL       │
│  - Subnet-level firewall             │
│  - Stateless rules                   │
└─────────────────────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Security Layer 2: Security Groups   │
│                                      │
│  Lambda-SG:                          │
│  - Inbound: None (event-driven)     │
│  - Outbound: 443 (HTTPS)            │
│  - Outbound: 9243 (Elastic)         │
│                                      │
│  VPC-Endpoint-SG:                    │
│  - Inbound: 443 from Lambda-SG      │
│  - Outbound: None                    │
└──────────────────────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Security Layer 3: IAM Roles         │
│                                      │
│  Lambda Execution Role:              │
│  - Bedrock: InvokeModel              │
│  - DynamoDB: GetItem, PutItem        │
│  - Secrets Manager: GetSecretValue   │
│  - S3: GetObject, PutObject          │
│  - CloudWatch: PutLogEvents          │
│  - VPC: CreateNetworkInterface       │
│                                      │
│  Principle of Least Privilege        │
└──────────────────────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Security Layer 4: Encryption        │
│                                      │
│  Data at Rest:                       │
│  - DynamoDB: KMS encryption          │
│  - S3: AES-256 encryption            │
│  - Secrets Manager: KMS              │
│  - EBS: Encrypted volumes            │
│                                      │
│  Data in Transit:                    │
│  - API Gateway: TLS 1.2+             │
│  - Lambda → AWS: TLS 1.2+            │
│  - Lambda → Elastic: TLS 1.2+        │
└──────────────────────────────────────┘
```

### Access Control

```
┌──────────────────────────────────────┐
│  Identity & Access Management        │
│                                      │
│  Service Accounts:                   │
│  - Lambda Execution Role             │
│  - API Gateway Execution Role        │
│                                      │
│  User Access:                        │
│  - AWS Console (MFA required)        │
│  - Terraform (Service Account)       │
│  - SageMaker Notebooks (IAM Role)    │
│                                      │
│  API Authentication:                 │
│  - API Gateway: API Keys (optional)  │
│  - Custom Authorizer (Lambda)        │
│  - AWS IAM Authorization             │
└──────────────────────────────────────┘
```

---

## High Availability & Disaster Recovery

### Multi-AZ Deployment

```
Availability Zone 1           Availability Zone 2
─────────────────            ─────────────────
Public Subnet                Public Subnet
- NAT Gateway 1              - NAT Gateway 2

Private Subnet 1             Private Subnet 3
- Lambda ENIs                - Lambda ENIs

Private Subnet 2             Private Subnet 4
- VPC Endpoints              - VPC Endpoints

┌─────────────────────────────────────┐
│  Elastic Load Balancer (Optional)   │
│  - Cross-AZ load balancing          │
│  - Health checks                    │
└─────────────────────────────────────┘
```

### Disaster Recovery Strategy

**RTO (Recovery Time Objective):** 1 hour  
**RPO (Recovery Point Objective):** 5 minutes

**Backup Strategy:**
- DynamoDB: Point-in-time recovery (continuous backups)
- S3: Versioning enabled, cross-region replication
- Elastic Cloud: Daily snapshots
- Terraform state: S3 backend with versioning

**Failover Procedures:**
1. Lambda: Automatic retry with exponential backoff
2. DynamoDB: Multi-region replication (optional)
3. Elastic Cloud: Cross-region snapshots
4. API Gateway: Multi-region deployment (optional)

---

## Monitoring & Observability

### CloudWatch Dashboards

```
┌─────────────────────────────────────────┐
│  API Gateway Metrics                     │
│  - Request count                         │
│  - 4XX/5XX errors                        │
│  - Latency (p50, p95, p99)              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Lambda Metrics                          │
│  - Invocations                           │
│  - Errors                                │
│  - Duration                              │
│  - Concurrent executions                 │
│  - Throttles                             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  DynamoDB Metrics                        │
│  - Read/Write capacity                   │
│  - Throttled requests                    │
│  - Latency                               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Bedrock Metrics                         │
│  - Model invocations                     │
│  - Token usage                           │
│  - Latency                               │
│  - Errors                                │
└─────────────────────────────────────────┘
```

### Elastic APM

```
┌─────────────────────────────────────────┐
│  Distributed Tracing                     │
│                                          │
│  API Request → Lambda → Bedrock          │
│      └─→ Elastic Search                  │
│      └─→ DynamoDB                        │
│                                          │
│  Trace Visualization:                    │
│  - Transaction timeline                  │
│  - Span durations                        │
│  - Error correlation                     │
│  - Resource utilization                  │
└─────────────────────────────────────────┘
```

### Alarms

```
Critical Alarms (PagerDuty):
- API Gateway 5XX > 5% for 5 minutes
- Lambda error rate > 10% for 5 minutes
- DynamoDB throttling > 100 for 5 minutes

Warning Alarms (Email):
- API Gateway latency p95 > 2s
- Lambda duration > 50s
- Bedrock throttling detected
```

---

## Scalability

### Auto-Scaling Configuration

```
Component         | Min | Max  | Target Metric
──────────────────|─────|──────|───────────────
Lambda            | 0   | 1000 | Concurrent executions
API Gateway       | -   | -    | 10,000 RPS
DynamoDB          | 0   | ∞    | On-demand (auto)
Elastic Cloud     | 2   | 10   | Storage usage
NAT Gateway       | 1   | 2    | Manual (Multi-AZ)
```

### Performance Targets

```
Metric                    | Target  | Current
──────────────────────────|─────────|─────────
API Response Time (p95)   | < 2s    | ~1.5s
Lambda Cold Start         | < 3s    | ~2s
Lambda Warm Start         | < 500ms | ~300ms
ELSER Search              | < 100ms | ~50ms
Bedrock Inference         | < 3s    | ~2s
End-to-End Transaction    | < 10s   | ~7s
```

---

## Cost Optimization

### Resource Right-Sizing

```
Current:
- Lambda: 512MB memory → Optimized for balance
- Lambda: 60s timeout → Sufficient for Bedrock
- DynamoDB: On-demand → Cost-effective for variable load
- NAT Gateway: 1-2 AZs → Required for HA

Optimization Opportunities:
- Lambda memory: Monitor and adjust based on usage
- Reserved capacity: DynamoDB if predictable load
- Savings Plans: Lambda and Bedrock for steady-state
- S3 Lifecycle: Move old logs to Glacier
```

### Cost Allocation Tags

```
Tags applied to all resources:
- Environment: workshop | production
- Project: travel-agent
- CostCenter: engineering
- ManagedBy: terraform
- Owner: team-name
```

---

## Compliance & Governance

### AWS Well-Architected Framework

**Operational Excellence:**
- Infrastructure as Code (Terraform)
- Automated deployments
- Runbook documentation
- Incident response procedures

**Security:**
- Least privilege IAM roles
- Encryption at rest and in transit
- Network isolation (VPC)
- Security groups and NACLs
- CloudTrail audit logging
- Secrets management

**Reliability:**
- Multi-AZ deployment
- Auto-scaling
- Automated backups
- Disaster recovery plan
- Retry logic with exponential backoff

**Performance Efficiency:**
- Serverless architecture
- Caching strategies
- Performance monitoring
- Right-sized resources

**Cost Optimization:**
- Pay-per-use pricing
- Resource tagging
- Cost allocation
- Reserved capacity (when appropriate)

---

## Deployment Architecture

### Infrastructure as Code

```
terraform/
├── main.tf              # Main configuration
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── backend.tf           # S3 backend for state
├── modules/
│   ├── vpc/             # VPC module
│   ├── lambda/          # Lambda module
│   ├── api-gateway/     # API Gateway module
│   ├── dynamodb/        # DynamoDB module
│   └── security/        # IAM & Security Groups
└── environments/
    ├── dev/
    ├── staging/
    └── production/
```

### CI/CD Pipeline (Recommended)

```
GitHub Actions / AWS CodePipeline

Source → Build → Test → Deploy
  │       │       │       │
  │       │       │       ├─→ Dev
  │       │       │       ├─→ Staging
  │       │       │       └─→ Production
  │       │       │
  │       │       └─→ Integration Tests
  │       │           - API tests
  │       │           - Lambda tests
  │       │           - E2E tests
  │       │
  │       └─→ Build Artifacts
  │           - Lambda packages
  │           - Terraform plan
  │
  └─→ Git commit
      - Terraform validate
      - Python linting
      - Security scan
```

---

## Migration Path

### From Workshop to Production

**Phase 1: Enhanced Security**
- Enable VPC PrivateLink to Elastic Cloud
- Implement API Gateway custom authorizer
- Add WAF rules
- Enable GuardDuty
- Configure AWS Config rules

**Phase 2: High Availability**
- Multi-region deployment
- Route 53 failover routing
- Cross-region DynamoDB replication
- Elastic Cloud cross-region snapshots

**Phase 3: Performance Optimization**
- CloudFront CDN
- ElastiCache for caching
- Lambda provisioned concurrency
- DynamoDB DAX

**Phase 4: Advanced Features**
- Step Functions for complex workflows
- EventBridge for event-driven architecture
- SQS for async processing
- SNS for notifications

---

## Support & Operations

### Runbook

**Standard Operations:**
1. Deployment: Terraform apply
2. Rollback: Terraform state rollback + reapply
3. Scaling: Update Terraform variables
4. Monitoring: CloudWatch + Elastic APM dashboards

**Incident Response:**
1. Alert received (CloudWatch Alarm)
2. Check CloudWatch Logs
3. Check Elastic APM traces
4. Investigate root cause
5. Apply fix (code or configuration)
6. Post-incident review

**Maintenance Windows:**
- Elastic Cloud: Sunday 2-4 AM UTC
- Lambda: Rolling deployments (no downtime)
- DynamoDB: No maintenance required

---

## Architecture Decision Records (ADR)

### ADR-001: Lambda in VPC
**Decision:** Deploy Lambda functions in VPC  
**Rationale:** Enhanced security, VPC endpoint cost savings, consistent network policy  
**Trade-offs:** Increased cold start time (~1-2s), ENI management overhead

### ADR-002: DynamoDB On-Demand
**Decision:** Use DynamoDB on-demand capacity  
**Rationale:** Variable workshop load, cost-effective for low usage, auto-scaling  
**Trade-offs:** Higher per-request cost than provisioned capacity

### ADR-003: Elastic Cloud via AWS Marketplace
**Decision:** Deploy Elastic Cloud via AWS Marketplace  
**Rationale:** Unified billing, AWS credits usage, simplified procurement  
**Trade-offs:** Limited to Marketplace pricing (vs direct Elastic)

### ADR-004: Multi-AZ NAT Gateway
**Decision:** Deploy NAT Gateway in both AZs  
**Rationale:** High availability, eliminate single point of failure  
**Trade-offs:** 2x NAT Gateway cost (~$64/month)

---

## Appendix

### Service Endpoints

```
API Gateway: https://{api-id}.execute-api.us-east-1.amazonaws.com
Elastic Cloud: https://{deployment-id}.es.us-east-1.aws.found.io:9243
Kibana: https://{deployment-id}.kb.us-east-1.aws.found.io:9243
CloudWatch: https://console.aws.amazon.com/cloudwatch/
```

### Resource Naming Convention

```
Pattern: {project}-{environment}-{service}-{resource}

Examples:
- travel-agent-workshop-agent-core-lambda
- travel-agent-workshop-agent-state-dynamodb
- travel-agent-workshop-elastic-creds-secret
```

### Tags

```
Required tags for all resources:
- Project: travel-agent
- Environment: workshop | dev | staging | production
- ManagedBy: terraform
- CostCenter: engineering
- Owner: {team-name}
- Compliance: {standard}
```

---

**Architecture Version:** 3.2  
**Last Updated:** June 18, 2026  
**Maintained By:** Workshop Team  
**Review Cycle:** Quarterly
