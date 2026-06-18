# Running Workshop on Amazon SageMaker

## Complete Guide to Using SageMaker Notebooks for This Workshop

**Why SageMaker?**

✅ **No local setup** - Run everything in AWS  
✅ **Pre-configured** - Python, Jupyter already installed  
✅ **Same VPC** - Direct access to AWS services  
✅ **Cost-effective** - ml.t3.medium is ~$0.05/hour  
✅ **Persistent** - Work saved automatically  

---

## Option 1: SageMaker Studio Lab (FREE!) ⭐ Recommended

**Best for**: Learning, testing, no AWS account needed initially

### Step 1: Get Studio Lab Account (5 minutes)

1. **Go to**: https://studiolab.sagemaker.aws

2. **Click**: "Request free account"

3. **Fill form**:
   ```
   Email: your-email@company.com
   Purpose: Learning AI/ML
   Organization: Your company
   ```

4. **Wait for approval**: 1-3 days (usually same day)

5. **Check email**: Activation link

6. **Set password**: Create your Studio Lab password

### Step 2: Launch Studio Lab (2 minutes)

1. **Login**: https://studiolab.sagemaker.aws

2. **Click**: "Start runtime"
   - Instance: CPU (free, sufficient for workshop)
   - Time: 4 hours per session
   - Storage: 15GB

3. **Wait**: 1-2 minutes for environment to start

4. **Click**: "Open project"

### Step 3: Upload Workshop Files (3 minutes)

**Option A: From GitHub (Easiest)**

In Studio Lab terminal:

```bash
cd ~
git clone https://github.com/elastic/travel-agent-workshop.git
cd travel-agent-workshop/notebooks
```

**Option B: Upload ZIP**

1. Download workshop ZIP
2. Studio Lab: Click upload icon
3. Upload and extract

### Step 4: Install Dependencies (2 minutes)

Open terminal in Studio Lab:

```bash
pip install elasticsearch==8.15.0 boto3==1.34.70 python-dotenv==1.0.1
```

### Step 5: Configure Credentials

**IMPORTANT**: Studio Lab doesn't have AWS credentials by default

In notebook cell:

```python
import os

# AWS Credentials (get from AWS Console → IAM)
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA...'
os.environ['AWS_SECRET_ACCESS_KEY'] = '...'
os.environ['AWS_REGION'] = 'us-east-1'

# Elastic Cloud (from Marketplace setup)
os.environ['ELASTIC_CLOUD_ID'] = '...'
os.environ['ELASTIC_USERNAME'] = 'elastic'
os.environ['ELASTIC_PASSWORD'] = '...'
```

✅ **Ready!** Open `00-Setup-and-Verification.ipynb`

---

## Option 2: SageMaker Notebook Instances (Classic)

**Best for**: Existing AWS customers, production work

### Step 1: Create Notebook Instance (5 minutes)

**In AWS Console:**

1. **Navigate to**: SageMaker → Notebook instances

2. **Click**: "Create notebook instance"

3. **Configure**:
   ```yaml
   Notebook instance name: travel-agent-workshop
   Notebook instance type: ml.t3.medium ($0.05/hour)
   Platform identifier: Amazon Linux 2, Jupyter Lab 3
   
   IAM role: Create new role
     - Allow access to: S3 (specific buckets)
     - Attach policies: 
       • AmazonBedrockFullAccess
       • SecretsManagerReadWrite (optional)
   
   Root access: Enabled (for pip installs)
   
   VPC: Default (or your VPC if Elastic is in PrivateLink)
   Security group: Default (or restrict to your IPs)
   
   Volume size: 20 GB (plenty for workshop)
   ```

4. **Click**: "Create notebook instance"

5. **Wait**: 3-5 minutes for "InService" status

### Step 2: Open JupyterLab (1 minute)

1. **Status**: InService (green)
2. **Click**: "Open JupyterLab"
3. JupyterLab opens in new tab

### Step 3: Clone Workshop Repository (2 minutes)

In JupyterLab terminal (File → New → Terminal):

```bash
cd SageMaker  # Default working directory
git clone https://github.com/elastic/travel-agent-workshop.git
cd travel-agent-workshop
```

### Step 4: Create Conda Environment (5 minutes)

**Option A: Use Conda (Recommended)**

```bash
conda create -n travel-agent python=3.10 -y
conda activate travel-agent

pip install elasticsearch==8.15.0 \
            boto3==1.34.70 \
            elastic-apm==6.21.0 \
            python-dotenv==1.0.1 \
            requests==2.31.0

# Make kernel available in Jupyter
python -m ipykernel install --user --name=travel-agent --display-name="Python (travel-agent)"
```

**Option B: System Python**

```bash
pip install elasticsearch==8.15.0 boto3 elastic-apm python-dotenv requests
```

### Step 5: Configure Credentials (2 minutes)

**Method A: AWS Secrets Manager** (Most Secure)

Store credentials in Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name elastic-workshop-credentials \
  --description "Credentials for Travel Agent Workshop" \
  --secret-string '{
    "ELASTIC_CLOUD_ID": "your-cloud-id",
    "ELASTIC_PASSWORD": "your-password",
    "ELASTIC_ENDPOINT": "https://..."
  }' \
  --region us-east-1
```

Then in notebook:

```python
import boto3
import json
import os

# Get credentials from Secrets Manager
secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
response = secrets_client.get_secret_value(SecretId='elastic-workshop-credentials')
secrets = json.loads(response['SecretString'])

# Set environment variables
os.environ['ELASTIC_CLOUD_ID'] = secrets['ELASTIC_CLOUD_ID']
os.environ['ELASTIC_PASSWORD'] = secrets['ELASTIC_PASSWORD']
os.environ['ELASTIC_ENDPOINT'] = secrets['ELASTIC_ENDPOINT']

# AWS credentials are automatic from IAM role!
os.environ['AWS_REGION'] = 'us-east-1'

print("✅ Credentials loaded from Secrets Manager!")
```

**Method B: Direct in Notebook** (Easier for workshop)

```python
import os

# Elastic Cloud
os.environ['ELASTIC_CLOUD_ID'] = 'your-cloud-id-here'
os.environ['ELASTIC_USERNAME'] = 'elastic'
os.environ['ELASTIC_PASSWORD'] = 'your-password-here'
os.environ['ELASTIC_ENDPOINT'] = 'https://...'

# AWS (automatic from IAM role!)
os.environ['AWS_REGION'] = 'us-east-1'
# No need for AWS_ACCESS_KEY_ID - IAM role provides this!

print("✅ Credentials configured!")
```

### Step 6: Select Kernel (1 minute)

1. **Open**: `notebooks/00-Setup-and-Verification.ipynb`
2. **Top right**: Click kernel name
3. **Select**: "Python (travel-agent)" or "conda_python3"
4. **Run cells!** 🚀

---

## Option 3: SageMaker Studio (Modern UI)

**Best for**: Teams, MLOps workflows

### Step 1: Setup Studio Domain (10 minutes, one-time)

**In AWS Console → SageMaker Studio:**

1. **Click**: "Set up SageMaker Studio"

2. **Choose**: Quick setup (recommended)
   ```yaml
   User name: workshop-user
   Execution role: Create new role
     - S3 access: All S3 buckets
     - Additional: Bedrock, Secrets Manager
   ```

3. **Click**: "Submit"

4. **Wait**: 5-10 minutes for domain creation

### Step 2: Launch Studio (2 minutes)

1. **SageMaker Console** → Studio → User profiles
2. **Click** your user → **Launch** → Studio
3. Studio UI opens (takes 1-2 min first time)

### Step 3: Create Notebook (3 minutes)

1. **File** → **New** → **Notebook**

2. **Select kernel**:
   - Image: Data Science 3.0
   - Kernel: Python 3
   - Instance: ml.t3.medium

3. **Wait**: Instance starts (1-2 min)

### Step 4: Clone Workshop

In Studio terminal:

```bash
git clone https://github.com/elastic/travel-agent-workshop.git
cd travel-agent-workshop/notebooks
```

Open notebooks from file browser on left.

---

## Comparison: Which SageMaker Option?

| Feature | Studio Lab | Notebook Instance | Studio |
|---------|-----------|-------------------|--------|
| **Cost** | FREE | ~$0.05/hour | ~$0.05/hour |
| **Setup time** | 5 min | 5 min | 15 min (first time) |
| **AWS account** | Not required | Required | Required |
| **Best for** | Learning | Workshops, testing | Teams, production |
| **Storage** | 15GB | 20GB+ | Persistent |
| **Session limit** | 4 hours | Unlimited | Unlimited |
| **IAM integration** | Manual | Automatic | Automatic |
| **Recommendation** | 🌟 Start here | ✅ AWS customers | 🏢 Enterprise |

---

## SageMaker-Specific Notebook Configuration

### Notebook 00: Setup for SageMaker

Create new first cell:

```python
# ===== SAGEMAKER SETUP =====
# Run this cell FIRST if using SageMaker

import sys
import subprocess

# Install workshop dependencies
print("📦 Installing workshop dependencies...")
subprocess.check_call([
    sys.executable, '-m', 'pip', 'install', '-q',
    'elasticsearch==8.15.0',
    'boto3==1.34.70',
    'elastic-apm==6.21.0',
    'python-dotenv==1.0.1',
    'requests==2.31.0'
])

print("✅ Dependencies installed!")
print("\nConfigure credentials in next cell →")
```

### Enhanced Credentials Cell

```python
import os
import boto3

print("🔧 Configuration Options:")
print("1. Using IAM Role (automatic AWS credentials)")
print("2. Using Secrets Manager (recommended for Elastic)")
print("3. Using direct configuration (easiest for workshop)")
print()

# Option 1: AWS credentials from IAM role (automatic in SageMaker!)
os.environ['AWS_REGION'] = 'us-east-1'
print("✅ AWS credentials: Using IAM role")

# Option 2: Get Elastic credentials from Secrets Manager
try:
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
    response = secrets_client.get_secret_value(SecretId='elastic-workshop-credentials')
    
    import json
    secrets = json.loads(response['SecretString'])
    
    os.environ['ELASTIC_CLOUD_ID'] = secrets['ELASTIC_CLOUD_ID']
    os.environ['ELASTIC_USERNAME'] = secrets.get('ELASTIC_USERNAME', 'elastic')
    os.environ['ELASTIC_PASSWORD'] = secrets['ELASTIC_PASSWORD']
    os.environ['ELASTIC_ENDPOINT'] = secrets['ELASTIC_ENDPOINT']
    
    print("✅ Elastic credentials: Loaded from Secrets Manager")
    
except Exception as e:
    print(f"ℹ️  Secrets Manager not found, using direct configuration")
    print(f"   (This is fine for workshop! Configure below)")
    
    # Option 3: Direct configuration
    os.environ['ELASTIC_CLOUD_ID'] = 'your-cloud-id-here'  # ← EDIT THIS
    os.environ['ELASTIC_USERNAME'] = 'elastic'
    os.environ['ELASTIC_PASSWORD'] = 'your-password-here'   # ← EDIT THIS
    os.environ['ELASTIC_ENDPOINT'] = 'https://your-url...'  # ← EDIT THIS
    
    print("✅ Elastic credentials: Direct configuration")

print("\n🎯 Ready to continue!")
```

---

## Cost Optimization for SageMaker

### During Workshop (Recommended)

```yaml
Instance: ml.t3.medium
Cost: $0.0582/hour
Workshop duration: 2-3 hours
Total cost: ~$0.20
```

### Stop Instance When Not Using

**Notebook Instances:**
```bash
# Stop (via Console or CLI)
aws sagemaker stop-notebook-instance \
  --notebook-instance-name travel-agent-workshop

# Restart later (no data loss!)
aws sagemaker start-notebook-instance \
  --notebook-instance-name travel-agent-workshop
```

**Studio Lab:**
- Automatically stops after 4 hours
- Free, no cost concerns!

**Studio:**
- Apps auto-stop after 30 min idle (configurable)

### Delete When Completely Done

```bash
aws sagemaker delete-notebook-instance \
  --notebook-instance-name travel-agent-workshop
```

---

## Benefits of SageMaker for This Workshop

### 1. No Local Setup

❌ **Without SageMaker:**
```bash
# Install Python
# Install Jupyter
# Install packages
# Configure environment
# Troubleshoot conflicts
# 30+ minutes
```

✅ **With SageMaker:**
```bash
# Just open notebook
# Install 5 packages
# 5 minutes
```

### 2. Native AWS Integration

```python
# Bedrock access - automatic from IAM role!
import boto3
bedrock = boto3.client('bedrock-runtime')  # Just works!

# No access keys needed
# No credential files
# No security risks
```

### 3. Same Region = Low Latency

```
SageMaker (us-east-1)
    ↓ 1-2ms
Bedrock (us-east-1)
    ↓ 1-2ms
Elastic Cloud (us-east-1)

Total: Sub-5ms overhead
```

### 4. Persistent Storage

```
Work saved automatically
Stop instance → No data loss
Resume later → Continue where you left off
```

### 5. Scalable

```
Start: ml.t3.medium ($0.05/hour)
Scale: ml.m5.large if needed ($0.115/hour)
GPU: ml.g4dn.xlarge for heavy ML ($0.736/hour)
```

---

## Troubleshooting SageMaker

### "No module named 'elasticsearch'"

**Solution**: Install in notebook cell

```python
!pip install elasticsearch==8.15.0 boto3
```

---

### "Unable to locate credentials"

**Problem**: Using Studio Lab without AWS keys

**Solution**: Add credentials to notebook

```python
import os
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA...'
os.environ['AWS_SECRET_ACCESS_KEY'] = '...'
```

Or use SageMaker Notebook Instance (has IAM role).

---

### "Kernel died" or "Out of memory"

**Problem**: ml.t3.medium has 4GB RAM

**Solution**: 
- Reduce batch sizes in code
- Or upgrade to ml.m5.large (8GB RAM)

```python
# In search functions, reduce top_k
search_with_elser(query, top_k=3)  # Instead of 10
```

---

### "Connection timeout" to Elastic

**Problem**: Security group blocking SageMaker

**Solution**: Add SageMaker IP range to Elastic traffic filter

1. Get SageMaker IP:
   ```python
   import requests
   my_ip = requests.get('https://api.ipify.org').text
   print(f"Add this IP to Elastic: {my_ip}")
   ```

2. Elastic Cloud Console → Deployment → Security
3. Add IP to traffic filter

---

### "Rate limit exceeded" on Bedrock

**Problem**: Too many requests too fast

**Solution**: Add throttling

```python
import time

def invoke_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = bedrock_runtime.invoke_model(...)
            return response
        except Exception as e:
            if 'ThrottlingException' in str(e):
                wait_time = (2 ** attempt)  # Exponential backoff
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

---

## Security Best Practices for SageMaker

### 1. Use IAM Roles (Not Access Keys)

✅ **Good** (Notebook Instance):
```python
import boto3
# Credentials from IAM role - automatic!
bedrock = boto3.client('bedrock-runtime')
```

❌ **Avoid** (hardcoded keys):
```python
bedrock = boto3.client(
    'bedrock-runtime',
    aws_access_key_id='AKIA...',  # Don't do this!
    aws_secret_access_key='...'
)
```

### 2. Use Secrets Manager for Elastic Credentials

```python
# Store once
aws secretsmanager create-secret \
  --name elastic-workshop \
  --secret-string '{"password":"..."}'

# Retrieve in notebook
import boto3
secrets = boto3.client('secretsmanager')
secret = secrets.get_secret_value(SecretId='elastic-workshop')
```

### 3. Don't Commit Notebooks with Credentials

```bash
# Before committing
jupyter nbconvert --clear-output --inplace *.ipynb

# Or add to .gitignore
echo "*.ipynb" >> .gitignore
```

### 4. Enable VPC for Production

For production (not workshop):

```yaml
Notebook in VPC: Yes
Subnet: Private subnet
Security group: Restrict to Elastic IPs only
Internet: Via NAT Gateway
```

---

## 🎯 Quick Start Summary

**Choose your path:**

### Path 1: Studio Lab (Free, No AWS Account)
```bash
1. Request account: studiolab.sagemaker.aws
2. Wait for approval (1-3 days)
3. Login → Start runtime → Open project
4. Clone workshop repo
5. Run notebooks!

Time: 10 minutes active work
Cost: $0 (FREE!)
```

### Path 2: Notebook Instance (AWS Account)
```bash
1. AWS Console → SageMaker → Create notebook instance
2. Name: travel-agent-workshop
3. Type: ml.t3.medium
4. Create IAM role with Bedrock access
5. Wait 5 min → Open JupyterLab
6. Clone repo → Run notebooks

Time: 10 minutes
Cost: ~$0.20 for full workshop
```

### Path 3: SageMaker Studio (Teams/Enterprise)
```bash
1. Setup Studio domain (one-time, 10 min)
2. Launch Studio
3. New notebook → ml.t3.medium
4. Clone repo → Run notebooks

Time: 15 minutes (first time)
Cost: ~$0.20 per session
```

---

## 📚 Additional Resources

### SageMaker Documentation
- Studio Lab: https://studiolab.sagemaker.aws
- Notebook Instances: https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html
- SageMaker Studio: https://docs.aws.amazon.com/sagemaker/latest/dg/studio.html

### Workshop Resources
- Main README: `README.md`
- AWS Marketplace Setup: `AWS_MARKETPLACE_SETUP.md`
- Jupyter Notebooks: `notebooks/README.md`

---

## ✅ You're Ready for SageMaker!

**Next steps:**

1. Choose your SageMaker option (Studio Lab recommended for learning)
2. Follow setup steps above
3. Open `notebooks/00-Setup-and-Verification.ipynb`
4. Configure credentials
5. Start learning! 🚀

**Total time to first running notebook:** ~15 minutes

---

*Last Updated: June 18, 2026*  
*For: Travel Intelligence Agent Workshop*  
*SageMaker-optimized for AWS customers*
