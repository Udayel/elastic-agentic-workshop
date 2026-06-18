# Security Best Practices

This workshop implements enterprise-grade security controls suitable for production deployment.

---

## 🔐 Security Features Implemented

### 1. Secrets Management

**AWS Secrets Manager Integration**
```hcl
# All credentials stored in AWS Secrets Manager
resource "aws_secretsmanager_secret" "elastic_credentials"
resource "aws_secretsmanager_secret" "strands_api"
resource "aws_secretsmanager_secret" "twilio_credentials"

# Automatic rotation support
# Encryption at rest with AWS KMS
# Fine-grained IAM access control
```

**No Hardcoded Credentials:**
- ✅ All secrets in Secrets Manager or environment variables
- ✅ `.env` file in `.gitignore`
- ✅ Terraform state encrypted
- ❌ No passwords in code or config files

### 2. Network Security

**VPC Isolation:**
```
┌─────────────────────────────────────────┐
│            Internet Gateway             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Public Subnets                  │
│         (NAT Gateways only)             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Private Subnets                 │
│         (Lambda Functions)              │
│         • No direct internet access     │
│         • Egress via NAT Gateway        │
└─────────────────────────────────────────┘
```

**Security Groups:**
```hcl
# Lambda security group - restrictive egress
resource "aws_security_group" "lambda" {
  egress {
    # Only HTTPS outbound
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Elastic Cloud Connection:**
- ✅ HTTPS only (TLS 1.2+)
- ✅ Option for AWS PrivateLink (production)
- ✅ IP allowlisting supported

### 3. IAM Least Privilege

**Lambda Execution Role:**
```hcl
# Minimal permissions - only what's needed
- logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents
- secretsmanager:GetSecretValue (specific ARNs only)
- dynamodb:GetItem, PutItem, Query (specific tables only)
- bedrock:InvokeModel (foundation models only)
- s3:GetObject, PutObject (specific bucket only)
```

**No Wildcards:**
```hcl
❌ "Resource": "*"
✅ "Resource": "arn:aws:secretsmanager:us-east-1:123456789:secret:travel-agent-*"
```

### 4. Data Encryption

**At Rest:**
- ✅ S3 buckets: AES-256 encryption
- ✅ DynamoDB: AWS managed keys
- ✅ Secrets Manager: KMS encryption
- ✅ Elastic Cloud: Encryption at rest enabled
- ✅ EBS volumes: Encrypted (Lambda)

**In Transit:**
- ✅ API Gateway: TLS 1.2+
- ✅ Elastic Cloud: HTTPS only
- ✅ Bedrock API: TLS 1.3
- ✅ Strands API: HTTPS
- ✅ Internal AWS: TLS by default

### 5. API Security

**API Gateway Protection:**
```hcl
# Rate limiting via usage plans
- Throttle: 100 requests/second
- Burst: 200 requests
- Quota: 10,000 requests/day

# CORS configuration (restrictive in production)
cors_configuration {
  allow_origins = ["https://your-domain.com"]  # Not "*" in prod
  allow_methods = ["POST", "GET"]
  allow_headers = ["Content-Type", "Authorization"]
}
```

**Request Validation:**
```python
# Input sanitization
- Max query length: 2000 characters
- Validate JSON schemas
- Reject suspicious patterns
- SQL injection prevention
- XSS protection
```

### 6. Authentication & Authorization

**API Key Authentication:**
```bash
# Create API key
aws apigateway create-api-key --name "client-app-key" --enabled

# Associate with usage plan
aws apigateway create-usage-plan-key \
  --usage-plan-id $PLAN_ID \
  --key-id $KEY_ID \
  --key-type API_KEY
```

**IAM Authentication (Optional):**
```python
# AWS Signature Version 4 signing
# Only authorized AWS principals can invoke
```

**Cognito Integration (Production):**
```hcl
# User pools for end-user authentication
resource "aws_cognito_user_pool" "users"
resource "aws_apigatewayv2_authorizer" "cognito"
```

### 7. Audit Logging

**CloudWatch Logs:**
```hcl
# All API requests logged
- Request ID
- Source IP
- Request time
- HTTP method
- Status code
- Response size
- User agent
```

**Elastic APM:**
```python
# Every agent action traced
- Tool invocations
- Search queries
- External API calls
- Error details
- Performance metrics
```

**AWS CloudTrail:**
```bash
# All infrastructure changes tracked
- Who made the change
- When it was made
- What was changed
- Source IP address
```

---

## 🛡️ Security Hardening Checklist

### Pre-Production

- [ ] Review all IAM policies - remove unnecessary permissions
- [ ] Enable AWS CloudTrail for audit logging
- [ ] Set up AWS Config rules for compliance
- [ ] Enable AWS GuardDuty for threat detection
- [ ] Configure VPC Flow Logs
- [ ] Enable S3 bucket versioning and logging
- [ ] Set up AWS WAF for API Gateway (if public)
- [ ] Configure AWS Shield Standard (free)
- [ ] Review security group rules - minimize open ports
- [ ] Enable MFA for AWS root account
- [ ] Rotate all API keys and credentials
- [ ] Set up AWS Secrets Manager rotation
- [ ] Configure API Gateway throttling limits
- [ ] Enable API Gateway access logging
- [ ] Set up CloudWatch alarms for security events
- [ ] Review Elastic Cloud security settings
- [ ] Enable Elastic Cloud IP filtering
- [ ] Configure AWS PrivateLink for Elastic (recommended)
- [ ] Set up SSL/TLS certificate for custom domain
- [ ] Enable HTTP Strict Transport Security (HSTS)

### Development

- [ ] Use separate AWS accounts for dev/staging/prod
- [ ] Never commit secrets to git
- [ ] Use `.gitignore` for sensitive files
- [ ] Scan dependencies for vulnerabilities
- [ ] Keep all packages up to date
- [ ] Use virtual environments for isolation
- [ ] Run static code analysis
- [ ] Perform security scanning on container images
- [ ] Test with read-only credentials when possible
- [ ] Use AWS SSM Session Manager instead of SSH

### Operations

- [ ] Monitor CloudWatch for unusual activity
- [ ] Review Elastic APM for anomalies
- [ ] Set up alerting for failed authentication
- [ ] Monitor API Gateway for abuse
- [ ] Track costs for unexpected spikes
- [ ] Regularly rotate credentials (quarterly)
- [ ] Perform security audits (quarterly)
- [ ] Keep incident response plan updated
- [ ] Document security procedures
- [ ] Train team on security best practices

---

## 🔒 Compliance Considerations

### Data Residency

**All data stays in your chosen AWS region:**
```
✓ Elastic Cloud on AWS - same region as Lambda
✓ DynamoDB - regional service
✓ S3 - regional buckets
✓ Secrets Manager - regional
✓ Lambda - regional functions
✓ No cross-region data transfer by default
```

### GDPR Compliance

**Data subject rights:**
- ✓ Right to access: Query DynamoDB for user data
- ✓ Right to deletion: Delete records via API
- ✓ Right to portability: Export to JSON
- ✓ Right to rectification: Update records

**Data minimization:**
- ✓ Collect only necessary information
- ✓ Implement data retention policies
- ✓ Use DynamoDB TTL for auto-expiration

### HIPAA Compliance (If Needed)

**AWS HIPAA eligible services used:**
- ✓ Lambda (with BAA)
- ✓ API Gateway (with BAA)
- ✓ DynamoDB (with BAA)
- ✓ S3 (with BAA)
- ✓ Secrets Manager (with BAA)

**Additional requirements:**
- Encrypt all PHI data
- Implement access controls
- Enable audit logging
- Sign AWS BAA

### PCI DSS (If Processing Payments)

**Scope minimization:**
- ❌ Do not store credit card numbers
- ✓ Use payment gateway (Stripe/Square)
- ✓ Tokenize payment methods
- ✓ Never log payment details

---

## 🚨 Security Incident Response

### Detection

**Monitoring Points:**
1. CloudWatch Alarms - unusual Lambda invocations
2. Elastic APM - anomalous search patterns
3. API Gateway - rate limit exceeded
4. GuardDuty - threat detection
5. Cost anomalies - unexpected charges

### Response Procedure

**1. Immediate Actions:**
```bash
# Disable compromised API keys
aws apigateway update-api-key --api-key-id $KEY_ID --patch-operations op=replace,path=/enabled,value=false

# Rotate credentials
aws secretsmanager rotate-secret --secret-id travel-agent-elastic-credentials

# Review access logs
aws logs tail /aws/apigateway/travel-agent --since 1h
```

**2. Investigation:**
- Review CloudTrail logs
- Check Elastic APM traces
- Analyze API Gateway access logs
- Examine Lambda CloudWatch logs
- Query DynamoDB for suspicious activity

**3. Containment:**
- Block malicious IP addresses
- Disable compromised credentials
- Isolate affected resources
- Enable AWS WAF if not already

**4. Recovery:**
- Restore from backups if needed
- Deploy clean infrastructure
- Verify system integrity
- Update security controls

**5. Post-Incident:**
- Document timeline
- Identify root cause
- Implement preventive measures
- Update runbooks
- Train team on lessons learned

---

## 🔐 Credential Rotation

### Automated Rotation (Recommended)

```bash
# Enable automatic rotation for secrets
aws secretsmanager rotate-secret \
  --secret-id travel-agent-elastic-credentials \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123:function:rotate-secret \
  --rotation-rules AutomaticallyAfterDays=90
```

### Manual Rotation (Quarterly)

**Elastic Cloud:**
1. Create new Elastic Cloud password
2. Update Secrets Manager
3. Restart Lambda functions (new env)
4. Verify connectivity
5. Deactivate old password

**AWS Access Keys:**
1. Create new access key
2. Update Secrets Manager
3. Test with new credentials
4. Deactivate old key
5. Delete old key after 24h

**Strands API:**
1. Generate new API key in Strands portal
2. Update Secrets Manager
3. Test API connectivity
4. Revoke old key

**Twilio:**
1. Generate new auth token
2. Update Secrets Manager
3. Test SMS functionality
4. Revoke old token

---

## 🌍 Multi-Region Deployment (DR)

### Active-Passive Setup

**Primary Region (us-east-1):**
```
- Active Lambda functions
- Read/Write DynamoDB
- Elastic Cloud primary
```

**Secondary Region (us-west-2):**
```
- Standby Lambda functions
- DynamoDB Global Tables (replica)
- Elastic Cloud snapshot (daily)
```

**Failover Process:**
```bash
# Update Route53 to point to secondary region
aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch file://failover.json

# Restore Elastic Cloud from snapshot
# Promote DynamoDB replica to primary
```

---

## 📋 Security Testing

### Automated Scans

**Dependency Scanning:**
```bash
# Python dependencies
pip-audit

# Terraform
tfsec terraform/

# Container images (if using)
trivy image your-image:latest
```

**Static Analysis:**
```bash
# Python code
bandit -r services/

# Secrets detection
truffleHog --regex --entropy=True .
```

### Penetration Testing

**Before Production:**
- API fuzzing
- SQL injection testing
- XSS testing
- Authentication bypass attempts
- Rate limiting validation
- CORS policy testing

**Note:** Get written permission before testing production systems.

---

## ✅ Security Validation

Run this checklist before going live:

```bash
# 1. No secrets in code
grep -r "password\|secret\|api_key" --include="*.py" --include="*.tf"

# 2. All secrets in Secrets Manager
aws secretsmanager list-secrets

# 3. IAM policies reviewed
aws iam get-role-policy --role-name travel-agent-lambda-role --policy-name custom

# 4. Encryption enabled
aws s3api get-bucket-encryption --bucket $BUCKET_NAME
aws dynamodb describe-table --table-name travel-agent-state

# 5. Logging enabled
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/travel-agent

# 6. API throttling configured
aws apigateway get-usage-plan --usage-plan-id $PLAN_ID

# 7. Network isolation
aws ec2 describe-security-groups --group-ids $SG_ID

# 8. Backup configured
aws dynamodb describe-continuous-backups --table-name travel-agent-state
```

---

## 📚 Additional Resources

- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [Elastic Cloud Security](https://www.elastic.co/guide/en/cloud/current/ec-security.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Well-Architected Framework - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)

---

**Security is everyone's responsibility. Report any security concerns immediately.**

*Last Updated: June 18, 2026*
