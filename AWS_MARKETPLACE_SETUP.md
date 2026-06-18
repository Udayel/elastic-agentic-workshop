# AWS Marketplace Setup Guide

## Complete Guide for Starting Elastic Cloud via AWS Marketplace

**Time**: 20 minutes  
**Cost**: Free 14-day trial available

---

## Why Use AWS Marketplace?

✅ **Unified Billing** - Elastic charges appear on your AWS bill  
✅ **AWS Credits** - Use AWS promotional credits to pay for Elastic  
✅ **Simplified Procurement** - No separate vendor approval needed  
✅ **7-Day Free Trial** - Explore Elastic Cloud at no cost  
✅ **Native AWS Integration** - Deploy and manage from AWS Console  
✅ **Easier Compliance** - Pre-approved via AWS Marketplace  

---

## Step 1: Subscribe to Elastic Cloud on AWS Marketplace (5 minutes)

### 1.1 Navigate to AWS Marketplace

```
1. Open AWS Console
2. Search for "Elastic Cloud" in the search bar
3. Click "AWS Marketplace" from the dropdown
```

**OR** Direct link:
```
https://aws.amazon.com/marketplace/pp/prodview-iyc3k5vglqxve
```

### 1.2 Subscribe to Elastic Cloud

1. **Click "Continue to Subscribe"**

2. **Review pricing**:
   - Elastic Cloud Enterprise: Pay-as-you-go via AWS
   - Standard tier: ~$95/month (for production)
   - Workshop configuration: ~$50/month
   - **7-day free trial available**

3. **Click "Subscribe"**
   - You'll see: "Thank you for subscribing!"
   - Status: "Subscription pending"
   - Wait 2-3 minutes for confirmation

4. **Once subscribed**, click **"Set up your account"**
   - This opens Elastic Cloud registration page

---

## Step 2: Create Elastic Cloud Account (5 minutes)

### 2.1 Registration

You'll be redirected to: `https://cloud.elastic.co/registration`

**Fill in:**
```
Email: your-work-email@company.com
Password: [Strong password - save this!]
Company: Your Company Name
```

✅ **Check**: "I agree to Elastic's terms"  
✅ **Click**: "Create account"

### 2.2 Email Verification

1. Check your email inbox
2. Click verification link
3. Log in to Elastic Cloud Console

---

## Step 3: Create Deployment on AWS (5 minutes)

### 3.1 Create New Deployment

Once logged in to https://cloud.elastic.co:

1. **Click "Create deployment"**

2. **Choose deployment type:**
   - Select: **"Elasticsearch"**
   - Template: **"General purpose"**

3. **Configure deployment:**

   ```yaml
   Name: travel-agent-workshop
   Version: 8.15.0 (or latest)
   Cloud Provider: AWS
   Region: us-east-1 (match your Lambda region!)
   
   Hardware profile:
   - Elasticsearch: 8GB RAM, 2 zones (for HA)
   - Machine Learning: 4GB RAM (required for ELSER!)
   - Kibana: 1GB RAM
   
   Storage:
   - Data: 128GB per zone (auto-scales)
   ```

4. **Enable features:**
   - ✅ Machine Learning (CRITICAL - needed for ELSER!)
   - ✅ APM (for observability)
   - ✅ Security (enabled by default)

5. **Click "Create deployment"**

### 3.2 SAVE YOUR CREDENTIALS! ⚠️

**IMPORTANT**: You'll see a popup with credentials:

```
Username: elastic
Password: AbCdEfGhIjKlMnOpQrStUvWxYz123456

☑️ Download credentials (CSV file)
☑️ Copy to password manager
☑️ Save somewhere secure
```

**⚠️ THIS PASSWORD IS SHOWN ONLY ONCE!**

If you lose it, you must reset it in Deployment settings.

### 3.3 Wait for Deployment

- Status: "Creating..."
- Time: ~5-8 minutes
- You'll see progress bars for each component

**When ready:**
- Status: ✅ Healthy
- Copy these values:

```bash
Cloud ID: workshop-abc123:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbyQ...
Elasticsearch endpoint: https://abc123.es.us-east-1.aws.found.io:9243
Kibana endpoint: https://abc123.kb.us-east-1.aws.found.io:9243
```

---

## Step 4: Verify Deployment (3 minutes)

### 4.1 Test Elasticsearch Connection

```bash
# Replace with YOUR values
export ELASTIC_ENDPOINT="https://abc123.es.us-east-1.aws.found.io:9243"
export ELASTIC_PASSWORD="your-password-here"

# Test connection
curl -u elastic:$ELASTIC_PASSWORD $ELASTIC_ENDPOINT

# Expected output:
{
  "name" : "instance-0000000001",
  "cluster_name" : "abc123",
  "cluster_uuid" : "xyz789",
  "version" : {
    "number" : "8.15.0"
  },
  "tagline" : "You Know, for Search"
}
```

✅ If you see cluster info → SUCCESS!

### 4.2 Open Kibana

1. Click **"Open Kibana"** in Elastic Cloud Console
2. Login:
   - Username: `elastic`
   - Password: [your saved password]

3. You should see Kibana home page

---

## Step 5: Deploy ELSER Model (5 minutes)

**CRITICAL for this workshop!**

### 5.1 Download ELSER

In Kibana:

1. **Navigate to**: Menu → **Machine Learning** → **Trained Models**

2. **Find**: `.elser_model_2` or search for "ELSER"

3. **Click**: **Download model**
   - Size: ~438MB
   - Time: 1-2 minutes
   - Status: "Downloading..."

4. **Wait for**: Status → "Downloaded"

### 5.2 Deploy ELSER

1. **Click**: **Deploy model** (next to .elser_model_2)

2. **Configure deployment:**
   ```yaml
   Deployment ID: elser_model_2_deployment
   Priority: normal
   Number of allocations: 1
   Threads per allocation: 2
   ```

3. **Click**: **Start deployment**

4. **Wait for**: Status → **"Started"** (green)
   - Time: 30-60 seconds

### 5.3 Verify ELSER is Running

```bash
# Test ELSER inference
curl -u elastic:$ELASTIC_PASSWORD \
  -X POST "$ELASTIC_ENDPOINT/_ml/trained_models/.elser_model_2/_infer" \
  -H "Content-Type: application/json" \
  -d '{
    "docs": [
      {"text_field": "romantic dinner in Tokyo"}
    ]
  }'

# Expected: Large JSON response with sparse vectors
```

✅ If you see tokens and weights → ELSER is working!

---

## Step 6: Configure for Workshop (2 minutes)

### 6.1 Get Required Values

You need these for the workshop:

```bash
# From Elastic Cloud Console → Deployment → "Copy endpoint"
ELASTIC_CLOUD_ID="workshop-abc:dXMtZWFzdC0xLmF3cy..."
ELASTIC_ENDPOINT="https://abc123.es.us-east-1.aws.found.io:9243"
ELASTIC_PASSWORD="your-password"

# From AWS
AWS_REGION="us-east-1"  # Same as Elastic deployment!
AWS_ACCESS_KEY_ID="AKIA..."
AWS_SECRET_ACCESS_KEY="..."
```

### 6.2 Save to Environment

**Option A: Jupyter Notebook** (Recommended)

Open `notebooks/00-Setup-and-Verification.ipynb` and paste:

```python
import os

os.environ['ELASTIC_CLOUD_ID'] = 'your-cloud-id'
os.environ['ELASTIC_USERNAME'] = 'elastic'
os.environ['ELASTIC_PASSWORD'] = 'your-password'
os.environ['ELASTIC_ENDPOINT'] = 'https://...'
os.environ['AWS_REGION'] = 'us-east-1'
# ... etc
```

**Option B: .env file**

```bash
cd elastic-agentic-workshop
cat > .env << EOF
ELASTIC_CLOUD_ID=your-cloud-id
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=your-password
ELASTIC_ENDPOINT=https://...
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
EOF
```

---

## Step 7: Request AWS Bedrock Access (5 minutes)

### 7.1 Enable Bedrock Models

In AWS Console:

1. **Search for**: "Bedrock"
2. **Click**: Amazon Bedrock
3. **Left menu**: **Model access**
4. **Click**: **Request model access** (orange button)

### 7.2 Select Models

Check these boxes:
- ✅ Anthropic → Claude 3.5 Sonnet
- ✅ Anthropic → Claude 3 Haiku
- ✅ Amazon → Titan Embeddings G1 - Text

Click **"Next"** → **"Submit"**

### 7.3 Wait for Approval

- Status: "Access granted" (usually instant!)
- Green checkmarks appear next to models
- If pending: Wait 2-5 minutes and refresh

### 7.4 Verify Bedrock Access

```bash
aws bedrock list-foundation-models --region us-east-1 | grep claude

# Expected:
# "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0"
# "modelId": "anthropic.claude-3-haiku-20240307-v1:0"
```

---

## ✅ Verification Checklist

Before starting the workshop, confirm:

- [ ] Elastic Cloud deployment is **Healthy** (green)
- [ ] ELSER model is **Started** (green status)
- [ ] Can connect to Elasticsearch (curl test passed)
- [ ] Can open Kibana (login successful)
- [ ] AWS Bedrock models show **"Access granted"**
- [ ] Have all credentials saved securely
- [ ] Workshop files downloaded/cloned

---

## 🎯 You're Ready!

**Total setup time**: ~20 minutes  
**Cost so far**: $0 (using free trial)

### Next Steps:

1. **Launch Jupyter notebooks**:
   ```bash
   cd elastic-agentic-workshop/notebooks
   jupyter notebook
   ```

2. **Open**: `00-Setup-and-Verification.ipynb`

3. **Follow along!** 🚀

---

## 💰 Cost Management

### Free Trial (7 Days)

Your Elastic Cloud deployment includes:
- **7-day free trial** via AWS Marketplace
- Full features enabled during trial
- Charges to AWS account after trial ends

After trial:
- **Standard deployment**: ~$95/month (billed via AWS)
- **Optimized for workshop**: ~$50/month (reduce resources)
- **Delete when done**: $0 ongoing cost

### Optimize Costs

**During workshop** (keep full resources):
```yaml
ML nodes: 4GB RAM (needed for ELSER)
ES nodes: 8GB RAM x 2 zones
```

**After workshop** (for experimentation):
```yaml
ML nodes: 2GB RAM (still works, slower)
ES nodes: 4GB RAM x 1 zone
Monthly: ~$35
```

**Delete deployment** (no longer needed):
1. Elastic Cloud Console → Deployments
2. Click deployment → Delete
3. Type deployment name to confirm
4. **Cost**: $0

### AWS Bedrock Costs

Pay-per-use:
- Claude 3.5 Sonnet: $3 per 1M input tokens
- Workshop usage: ~1M tokens = $3-5 total
- Delete Lambda functions when done

---

## 🔒 Security Best Practices

### 1. Secure Your Credentials

```bash
# Never commit credentials!
echo ".env" >> .gitignore
echo "*.ipynb" >> .gitignore  # If it has credentials

# Use AWS Secrets Manager for production
aws secretsmanager create-secret \
  --name elastic-workshop-creds \
  --secret-string '{"password":"your-password"}'
```

### 2. Restrict Access

In Elastic Cloud Console:

1. **Deployment** → **Security**
2. **Traffic filters**: Add your IP address
3. **Delete** the "0.0.0.0/0" rule (allows all IPs)

### 3. IAM Least Privilege

For workshop IAM user:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🐛 Troubleshooting

### "Subscription is pending"

**Solution**: Wait 2-3 minutes, refresh the page

---

### "No ML nodes available"

**Problem**: ML not enabled in deployment

**Solution**:
1. Elastic Cloud Console → Your deployment → **Edit**
2. **Machine Learning**: Enable (4GB minimum)
3. **Save changes**
4. Wait 5 minutes for nodes to start

---

### "ELSER model not found"

**Problem**: Model not downloaded

**Solution**:
1. Kibana → ML → Trained Models
2. Search: ".elser" or scroll to find it
3. Click **"Download model"**
4. Wait for download (1-2 min)
5. Click **"Deploy"**

---

### "Access denied" to Bedrock

**Problem**: Models not enabled

**Solution**:
1. AWS Console → Bedrock → Model access
2. Click **"Request model access"**
3. Select Claude models
4. Submit request
5. Wait 2-5 minutes

---

### "Connection timeout" from notebook

**Problem**: Traffic filter blocking you

**Solution**:
1. Get your IP: `curl ifconfig.me`
2. Elastic Console → Deployment → Security → Traffic filters
3. Add your IP: `123.45.67.89/32`
4. Save
5. Retry connection

---

### Deployment costs more than expected

**Problem**: Using production-sized resources

**Solution**:
1. Edit deployment
2. Reduce to smaller instance sizes
3. Use 1 availability zone (not 2)
4. Or delete and recreate with "Development" template

---

## 📞 Getting Help

### Elastic Support
- Community: https://discuss.elastic.co
- Documentation: https://www.elastic.co/guide
- AWS Marketplace support: Through AWS Support

### AWS Support
- Bedrock docs: https://docs.aws.amazon.com/bedrock/
- AWS Support Center (if you have support plan)

---

## 🎉 Summary

You now have:

✅ **Elastic Cloud** running on AWS (via Marketplace)  
✅ **ELSER v2** deployed and ready  
✅ **AWS Bedrock** access approved  
✅ **Unified billing** through AWS  
✅ **All credentials** saved securely  

**Time to start building!** 🚀

Open the workshop notebooks and begin with `00-Setup-and-Verification.ipynb`.

---

*Last Updated: June 18, 2026*  
*For: Travel Intelligence Agent Workshop*  
*Elastic Cloud Version: 8.15+*
