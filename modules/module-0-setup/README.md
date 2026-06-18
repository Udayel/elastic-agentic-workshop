# Module 0: Getting Started with Elastic AgenticBuilder

## Overview

In this module, you'll set up your complete development environment for building AI travel agents. You'll deploy Elastic Cloud with AgenticBuilder, enable the ELSER model, and configure all necessary integrations.

**Time to Complete**: 25 minutes

---

## What You'll Accomplish

By the end of this module, you will have:

- ✅ An Elastic Cloud deployment with AgenticBuilder enabled
- ✅ ELSER v2 model deployed and running
- ✅ AWS Bedrock access configured
- ✅ Development environment set up
- ✅ API credentials configured
- ✅ Your first "Hello World" agent running

---

## Prerequisites

Before starting, ensure you have:

- [ ] AWS Account with admin access
- [ ] Credit card for Elastic Cloud trial (14 days free)
- [ ] Modern web browser (Chrome, Firefox, Safari)
- [ ] Terminal/command line access
- [ ] Text editor (VS Code recommended)

---

## Step 1: Create Elastic Cloud Account

### 1.1 Sign Up for Elastic Cloud

1. Navigate to [Elastic Cloud](https://cloud.elastic.co/registration)

2. Click **"Start free trial"**

   ![Sign up button](../../docs/images/elastic-signup.png)

3. Fill in your details:
   ```
   Email: your-email@example.com
   Password: [create strong password]
   Full Name: Your Name
   Company: Your Company (optional)
   ```

4. Click **"Create account"**

5. Check your email and **verify your email address**

   ![Email verification](../../docs/images/email-verify.png)

### 1.2 Start Your Free Trial

1. After email verification, you'll be redirected to the Elastic Cloud console

2. Click **"Start your free trial"**

3. Select trial options:
   ```
   Trial Duration: 14 days
   Credits: $400 (should be pre-filled)
   ```

4. Enter payment information (card won't be charged during trial)

5. Click **"Start trial"**

✅ **Checkpoint**: You should now see the Elastic Cloud console dashboard

---

## Step 2: Deploy Elastic Cloud with AgenticBuilder

### 2.1 Create New Deployment

1. From the Elastic Cloud console, click **"Create deployment"**

   ![Create deployment button](../../docs/images/create-deployment.png)

2. Configure deployment settings:

   **Deployment name:**
   ```
   travel-agent-workshop
   ```

   **Version:**
   ```
   8.15.0 (or latest)
   ```

   **Cloud platform:**
   ```
   AWS
   ```

   **Region:** (Select closest to you)
   ```
   us-east-1 (N. Virginia)
   or
   eu-west-1 (Ireland)
   or
   ap-southeast-1 (Singapore)
   ```

3. Select deployment template:

   Click **"Customize deployment"** instead of using a template

### 2.2 Configure Elasticsearch

1. **Hardware profile**: Select **"General purpose"**

2. **Size**: 
   ```
   8 GB RAM per zone (recommended for workshop)
   4 GB RAM per zone (minimum)
   ```

3. **Availability zones**: 
   ```
   1 zone (for workshop)
   ```

4. **Storage**:
   ```
   240 GB (default)
   ```

### 2.3 Enable Machine Learning Features

This is critical for ELSER!

1. Scroll to **"Machine Learning instances"**

2. Toggle **Enable** machine learning instances

   ![Enable ML](../../docs/images/enable-ml.png)

3. Configure ML settings:
   ```
   Size: 4 GB RAM
   Availability zones: 1
   ```

### 2.4 Enable Kibana

1. Scroll to **"Kibana"**

2. Ensure it's **Enabled** (should be by default)

3. Size:
   ```
   1 GB RAM (default)
   ```

### 2.5 Review and Create

1. Review your configuration:
   ```
   Elasticsearch: 8 GB RAM, 1 zone
   Machine Learning: 4 GB RAM, 1 zone
   Kibana: 1 GB RAM
   
   Estimated monthly cost: ~$200 (covered by trial credits)
   ```

2. Click **"Create deployment"**

3. **IMPORTANT**: Save your credentials!

   A popup will show:
   ```
   Username: elastic
   Password: [random password - COPY THIS!]
   
   Cloud ID: travel-agent-workshop:dXMtZW...
   ```

   ![Save credentials](../../docs/images/save-credentials.png)

4. Click **"Download credentials"** or copy to a safe place

   **⚠️ WARNING**: You cannot retrieve this password later!

5. Click **"Continue"**

### 2.6 Wait for Deployment

Your deployment will take 5-10 minutes to provision.

You'll see:
```
Creating deployment...
├─ Elasticsearch: Creating... ⏳
├─ Machine Learning: Creating... ⏳
└─ Kibana: Creating... ⏳
```

When complete:
```
Deployment ready! ✅
├─ Elasticsearch: Ready ✅
├─ Machine Learning: Ready ✅
└─ Kibana: Ready ✅
```

✅ **Checkpoint**: Your Elastic Cloud deployment is now running!

---

## Step 3: Access Kibana and Verify Setup

### 3.1 Open Kibana

1. From the deployment page, click **"Open Kibana"**

   ![Open Kibana button](../../docs/images/open-kibana.png)

2. You'll be redirected to Kibana login page

3. Enter credentials:
   ```
   Username: elastic
   Password: [password you saved earlier]
   ```

4. Click **"Log in"**

### 3.2 Welcome to Kibana!

You should see the Kibana home page with:
- Navigation menu on the left
- "Welcome to Elastic" banner
- Quick start guides

![Kibana home](../../docs/images/kibana-home.png)

✅ **Checkpoint**: You're now logged into Kibana!

---

## Step 4: Deploy ELSER Model

ELSER (Elastic Learned Sparse EncodeR) is Elastic's semantic search model. This is the secret sauce for our travel agent!

### 4.1 Navigate to Machine Learning

1. Click the **hamburger menu** (☰) in the top-left

2. Scroll down to **"Machine Learning"**

3. Click **"Trained Models"**

   ![ML menu](../../docs/images/ml-menu.png)

### 4.2 Download ELSER Model

1. On the Trained Models page, you'll see available models

2. Find **".elser_model_2"** (ELSER v2)

   ![ELSER model](../../docs/images/elser-model.png)

3. Click **"Download model"** button

4. A modal will appear - click **"Download"** to confirm

5. Model download will start:
   ```
   Downloading .elser_model_2...
   Progress: [=========>    ] 67%
   ```

   This takes 2-3 minutes.

6. When complete, you'll see:
   ```
   Status: Downloaded ✅
   ```

### 4.3 Start ELSER Deployment

1. Next to the ELSER model, click **"Deploy"** button

   ![Deploy ELSER](../../docs/images/deploy-elser.png)

2. Configure deployment:

   **Deployment name:**
   ```
   elser-travel-agent
   ```

   **Number of allocations:**
   ```
   1 (for workshop)
   ```

   **Number of threads:**
   ```
   1 (for workshop)
   ```

   **Priority:**
   ```
   normal
   ```

3. Click **"Start deployment"**

4. Deployment will begin:
   ```
   Starting deployment...
   Allocating resources...
   Loading model...
   ```

   This takes 1-2 minutes.

5. When complete, you'll see:
   ```
   Status: Started ✅
   ```

### 4.4 Verify ELSER is Working

1. Click on the **"Test model"** button

2. Enter test text:
   ```
   romantic dinner spot with sunset views
   ```

3. Click **"Test"**

4. You should see output tokens (sparse vector representation):
   ```json
   {
     "romantic": 2.34,
     "dinner": 1.87,
     "sunset": 2.91,
     "views": 2.15,
     "intimate": 1.42,
     "restaurant": 1.98,
     ...
   }
   ```

   ![ELSER test](../../docs/images/elser-test.png)

✅ **Checkpoint**: ELSER is deployed and working!

---

## Step 5: Set Up Development Environment

### 5.1 Create Workshop Directory

Open your terminal and run:

```bash
# Create workshop directory
mkdir -p ~/travel-agent-workshop
cd ~/travel-agent-workshop

# Create subdirectories
mkdir -p {agents,data,scripts,terraform}
```

### 5.2 Install Required Tools

#### For macOS:

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install python@3.11
brew install jq
brew install terraform
brew install git

# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

#### For Linux:

```bash
# Update package manager
sudo apt-get update

# Install Python
sudo apt-get install -y python3.11 python3-pip

# Install tools
sudo apt-get install -y jq git curl unzip

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### For Windows:

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install tools
choco install python311
choco install jq
choco install terraform
choco install git
choco install awscli
```

### 5.3 Verify Installations

Run these commands to verify everything is installed:

```bash
# Check Python
python3 --version
# Should output: Python 3.11.x

# Check pip
pip3 --version
# Should output: pip 23.x.x

# Check Terraform
terraform --version
# Should output: Terraform v1.6.0

# Check AWS CLI
aws --version
# Should output: aws-cli/2.x.x

# Check jq
jq --version
# Should output: jq-1.6 or higher
```

✅ **Checkpoint**: All tools installed successfully!

### 5.4 Create Python Virtual Environment

```bash
# Navigate to workshop directory
cd ~/travel-agent-workshop

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
.\venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip

# Install Python packages
pip install elasticsearch==8.15.0
pip install elastic-apm==6.21.0
pip install boto3==1.34.70
pip install python-dotenv==1.0.1
pip install requests==2.31.0
pip install pyyaml==6.0.1
```

### 5.5 Create Configuration File

Create a `.env` file to store your credentials:

```bash
# Create .env file
cat > .env << 'EOF'
# Elastic Cloud Configuration
ELASTIC_CLOUD_ID=your_cloud_id_here
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=your_password_here
ELASTIC_ENDPOINT=https://your-deployment.es.us-east-1.aws.found.io:9243

# ELSER Configuration
ELSER_MODEL_ID=.elser_model_2
ELSER_DEPLOYMENT_NAME=elser-travel-agent

# AWS Configuration (will configure in next step)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# External APIs (will configure later)
STRANDS_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
```

### 5.6 Update Configuration with Your Values

1. Get your Elastic Cloud ID:
   - Go to Elastic Cloud console
   - Click on your deployment name
   - Copy the **Cloud ID**

2. Get your Elasticsearch endpoint:
   - Same page, copy **Elasticsearch endpoint**

3. Edit `.env` file:
   ```bash
   nano .env  # or use your preferred editor
   ```

4. Replace these values:
   ```
   ELASTIC_CLOUD_ID=travel-agent-workshop:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbyRhYmMxMjM=
   ELASTIC_PASSWORD=your_saved_password_here
   ELASTIC_ENDPOINT=https://travel-agent-abc123.es.us-east-1.aws.found.io:9243
   ```

5. Save and close the file

✅ **Checkpoint**: Configuration file created with Elastic credentials!

---

## Step 6: Configure AWS Access

### 6.1 Enable Amazon Bedrock

1. Open [AWS Console](https://console.aws.amazon.com/)

2. Navigate to **Amazon Bedrock**
   - Search for "Bedrock" in the top search bar
   - Click on "Amazon Bedrock"

3. Click **"Get started"** if first time

4. In the left sidebar, click **"Model access"**

   ![Bedrock menu](../../docs/images/bedrock-menu.png)

5. Click **"Request model access"** button

6. Select these models:
   - ✅ **Anthropic - Claude 3.5 Sonnet**
   - ✅ **Anthropic - Claude 3 Haiku**
   - ✅ **Amazon - Titan Text Embeddings V2**

   ![Model selection](../../docs/images/bedrock-models.png)

7. Click **"Request model access"**

8. Wait for approval (usually instant, max 2 minutes)

9. Refresh the page - you should see:
   ```
   Access granted ✅
   ```

### 6.2 Create IAM User for Workshop

1. Navigate to **IAM** service in AWS Console

2. Click **"Users"** in left sidebar

3. Click **"Create user"** button

4. Enter user details:
   ```
   User name: travel-agent-workshop
   ```

5. Click **"Next"**

6. Select **"Attach policies directly"**

7. Search and select these policies:
   - ✅ **AmazonBedrockFullAccess**
   - ✅ **AWSLambda_FullAccess**
   - ✅ **AmazonAPIGatewayAdministrator**
   - ✅ **AmazonDynamoDBFullAccess**
   - ✅ **IAMFullAccess** (for Terraform)

   ![IAM policies](../../docs/images/iam-policies.png)

8. Click **"Next"**, then **"Create user"**

### 6.3 Create Access Keys

1. Click on the newly created user **"travel-agent-workshop"**

2. Click **"Security credentials"** tab

3. Scroll to **"Access keys"** section

4. Click **"Create access key"**

5. Select use case:
   ```
   ☑ CLI access
   ```

6. Check the confirmation box, click **"Next"**

7. Add description:
   ```
   Travel agent workshop development
   ```

8. Click **"Create access key"**

9. **IMPORTANT**: Copy your credentials:
   ```
   Access key ID: AKIAIOSFODNN7EXAMPLE
   Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

   ![Access keys](../../docs/images/access-keys.png)

10. Click **"Download .csv file"** for backup

11. Click **"Done"**

### 6.4 Configure AWS CLI

```bash
# Configure AWS CLI
aws configure

# Enter when prompted:
AWS Access Key ID: [paste your access key]
AWS Secret Access Key: [paste your secret key]
Default region name: us-east-1
Default output format: json
```

### 6.5 Update .env File

```bash
# Edit .env file
nano .env

# Update AWS section:
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### 6.6 Test AWS Access

```bash
# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1

# You should see a list of models including Claude
```

✅ **Checkpoint**: AWS access configured and verified!

---

## Step 7: Verify Complete Setup

### 7.1 Create Verification Script

Create a file called `verify_setup.py`:

```python
#!/usr/bin/env python3
"""
Verify that all components are correctly configured
"""

import os
import sys
from dotenv import load_dotenv

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✓{RESET} {message}")

def print_error(message):
    print(f"{RED}✗{RESET} {message}")

def print_warning(message):
    print(f"{YELLOW}⚠{RESET} {message}")

def verify_elasticsearch():
    """Verify Elasticsearch connection"""
    try:
        from elasticsearch import Elasticsearch
        
        es = Elasticsearch(
            cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
            basic_auth=(os.getenv('ELASTIC_USERNAME'), os.getenv('ELASTIC_PASSWORD'))
        )
        
        info = es.info()
        print_success(f"Elasticsearch connection successful")
        print(f"  Cluster: {info['cluster_name']}")
        print(f"  Version: {info['version']['number']}")
        return True
        
    except Exception as e:
        print_error(f"Elasticsearch connection failed: {e}")
        return False

def verify_elser():
    """Verify ELSER model deployment"""
    try:
        from elasticsearch import Elasticsearch
        
        es = Elasticsearch(
            cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
            basic_auth=(os.getenv('ELASTIC_USERNAME'), os.getenv('ELASTIC_PASSWORD'))
        )
        
        # Check if ELSER model is deployed
        response = es.ml.get_trained_models(
            model_id=".elser_model_2"
        )
        
        if response['trained_model_configs']:
            print_success("ELSER model found")
            
            # Check deployment
            deployments = es.ml.get_trained_models_stats(
                model_id=".elser_model_2"
            )
            
            if deployments['trained_model_stats']:
                status = deployments['trained_model_stats'][0]['deployment_stats']
                if status and status['state'] == 'started':
                    print_success("ELSER model is deployed and running")
                    return True
                else:
                    print_warning("ELSER model exists but is not started")
                    return False
        else:
            print_error("ELSER model not found")
            return False
            
    except Exception as e:
        print_error(f"ELSER verification failed: {e}")
        return False

def verify_aws_bedrock():
    """Verify AWS Bedrock access"""
    try:
        import boto3
        
        bedrock = boto3.client('bedrock', region_name=os.getenv('AWS_REGION'))
        
        models = bedrock.list_foundation_models()
        claude_models = [m for m in models['modelSummaries'] 
                        if 'claude' in m['modelId'].lower()]
        
        if claude_models:
            print_success("AWS Bedrock access verified")
            print(f"  Claude models available: {len(claude_models)}")
            return True
        else:
            print_error("No Claude models accessible")
            return False
            
    except Exception as e:
        print_error(f"AWS Bedrock verification failed: {e}")
        return False

def verify_python_packages():
    """Verify required Python packages"""
    required_packages = [
        'elasticsearch',
        'elastic_apm',
        'boto3',
        'dotenv',
        'requests',
        'yaml'
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"Package '{package}' installed")
        except ImportError:
            print_error(f"Package '{package}' not installed")
            all_installed = False
    
    return all_installed

def main():
    # Load environment variables
    load_dotenv()
    
    print("=" * 60)
    print("Travel Agent Workshop - Setup Verification")
    print("=" * 60)
    print()
    
    # Track results
    results = []
    
    # Check Python packages
    print("1. Checking Python packages...")
    results.append(verify_python_packages())
    print()
    
    # Check Elasticsearch
    print("2. Checking Elasticsearch connection...")
    results.append(verify_elasticsearch())
    print()
    
    # Check ELSER
    print("3. Checking ELSER model deployment...")
    results.append(verify_elser())
    print()
    
    # Check AWS Bedrock
    print("4. Checking AWS Bedrock access...")
    results.append(verify_aws_bedrock())
    print()
    
    # Summary
    print("=" * 60)
    if all(results):
        print_success("All checks passed! You're ready to proceed.")
        print()
        print("Next step: Module 1 - ELSER Semantic Search")
        print("  cd modules/module-1-elser")
        sys.exit(0)
    else:
        print_error("Some checks failed. Please review the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### 7.2 Run Verification

```bash
# Make script executable
chmod +x verify_setup.py

# Run verification
python3 verify_setup.py
```

Expected output:

```
============================================================
Travel Agent Workshop - Setup Verification
============================================================

1. Checking Python packages...
✓ Package 'elasticsearch' installed
✓ Package 'elastic_apm' installed
✓ Package 'boto3' installed
✓ Package 'dotenv' installed
✓ Package 'requests' installed
✓ Package 'yaml' installed

2. Checking Elasticsearch connection...
✓ Elasticsearch connection successful
  Cluster: travel-agent-workshop
  Version: 8.15.0

3. Checking ELSER model deployment...
✓ ELSER model found
✓ ELSER model is deployed and running

4. Checking AWS Bedrock access...
✓ AWS Bedrock access verified
  Claude models available: 3

============================================================
✓ All checks passed! You're ready to proceed.

Next step: Module 1 - ELSER Semantic Search
  cd modules/module-1-elser
============================================================
```

✅ **Checkpoint**: Complete setup verified!

---

## Step 8: Create Your First Agent (Hello World)

Let's create a simple "Hello World" agent to verify everything works end-to-end.

### 8.1 Create Hello World Agent Script

Create `hello_agent.py`:

```python
#!/usr/bin/env python3
"""
Simple Hello World agent to verify setup
"""

import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import boto3
import json

load_dotenv()

def test_bedrock_agent():
    """Test simple Bedrock interaction"""
    
    print("🤖 Testing Bedrock Agent...")
    
    bedrock_runtime = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION')
    )
    
    # Simple prompt
    prompt = "You are a travel agent. Say hello and introduce yourself in 2 sentences."
    
    # Call Claude
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    agent_response = response_body['content'][0]['text']
    
    print(f"\n{agent_response}\n")
    return True

def test_elser_search():
    """Test ELSER semantic search"""
    
    print("🔍 Testing ELSER Semantic Search...")
    
    es = Elasticsearch(
        cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
        basic_auth=(os.getenv('ELASTIC_USERNAME'), os.getenv('ELASTIC_PASSWORD'))
    )
    
    # Create a test index with ELSER
    index_name = "hello-world-test"
    
    # Delete if exists
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    
    # Create index with ELSER inference
    es.indices.create(
        index=index_name,
        mappings={
            "properties": {
                "content": {"type": "text"},
                "content_embedding": {
                    "type": "sparse_vector"
                }
            }
        }
    )
    
    # Add a test document
    test_doc = {
        "content": "Paris is a beautiful city known for the Eiffel Tower, amazing food, and romantic atmosphere."
    }
    
    # Generate ELSER embedding using inference API
    inference_result = es.ml.infer_trained_model(
        model_id=".elser_model_2",
        docs=[{"text_field": test_doc["content"]}]
    )
    
    # Get the sparse vector
    sparse_vector = inference_result['inference_results'][0]['predicted_value']
    
    # Index document with embedding
    es.index(
        index=index_name,
        document={
            **test_doc,
            "content_embedding": sparse_vector
        }
    )
    
    # Refresh index
    es.indices.refresh(index=index_name)
    
    # Search using ELSER
    search_query = {
        "query": {
            "text_expansion": {
                "content_embedding": {
                    "model_id": ".elser_model_2",
                    "model_text": "romantic dinner destination"
                }
            }
        }
    }
    
    results = es.search(index=index_name, body=search_query)
    
    if results['hits']['total']['value'] > 0:
        print(f"✓ Found {results['hits']['total']['value']} result(s)")
        print(f"  Top match: {results['hits']['hits'][0]['_source']['content'][:100]}...")
        print(f"  Score: {results['hits']['hits'][0]['_score']:.2f}")
    
    # Cleanup
    es.indices.delete(index=index_name)
    
    return True

def main():
    print("=" * 60)
    print("Hello World Agent Test")
    print("=" * 60)
    print()
    
    try:
        # Test Bedrock agent
        test_bedrock_agent()
        print()
        
        # Test ELSER search
        test_elser_search()
        print()
        
        print("=" * 60)
        print("✅ All tests passed! Your agent is working!")
        print()
        print("You're ready to build the travel agent!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check your configuration and try again.")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
```

### 8.2 Run Hello World Agent

```bash
# Make executable
chmod +x hello_agent.py

# Run the agent
python3 hello_agent.py
```

Expected output:

```
============================================================
Hello World Agent Test
============================================================

🤖 Testing Bedrock Agent...

Hello! I'm your AI travel assistant, ready to help you plan 
amazing trips around the world. I can search destinations, 
find flights and hotels, create personalized itineraries, 
and help you discover unforgettable experiences.

🔍 Testing ELSER Semantic Search...
✓ Found 1 result(s)
  Top match: Paris is a beautiful city known for the Eiffel 
  Tower, amazing food, and romantic atmosphere...
  Score: 15.42

============================================================
✅ All tests passed! Your agent is working!

You're ready to build the travel agent!
============================================================
```

✅ **Congratulations!** Your first agent is working!

---

## Troubleshooting

### Issue: Cannot connect to Elasticsearch

**Symptoms:**
```
Connection timeout
or
Authentication failed
```

**Solutions:**

1. Check your Cloud ID is correct:
   ```bash
   echo $ELASTIC_CLOUD_ID
   ```

2. Verify password has no typos:
   ```bash
   # Don't echo password, but check it's set
   echo ${ELASTIC_PASSWORD:0:3}***
   ```

3. Ensure deployment is running:
   - Go to Elastic Cloud console
   - Check deployment status is "Healthy"

4. Test connection directly:
   ```bash
   curl -u elastic:YOUR_PASSWORD https://your-deployment.es.us-east-1.aws.found.io:9243
   ```

### Issue: ELSER model not found

**Symptoms:**
```
Model .elser_model_2 not found
```

**Solutions:**

1. Verify model is downloaded:
   - Go to Kibana → ML → Trained Models
   - Check ".elser_model_2" shows "Downloaded"

2. Verify model is deployed:
   - Status should be "Started"
   - If "Stopped", click "Start"

3. Wait for deployment:
   - Can take 1-2 minutes after starting

### Issue: Bedrock access denied

**Symptoms:**
```
AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel
```

**Solutions:**

1. Verify model access granted:
   - Go to AWS Bedrock console
   - Check Model access page shows "Access granted"

2. Check IAM permissions:
   - Verify user has AmazonBedrockFullAccess policy

3. Wait for propagation:
   - After requesting access, wait 2-5 minutes

4. Check region:
   - Bedrock must be accessed in supported regions
   - Use us-east-1, us-west-2, or eu-west-1

### Issue: Python package import errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'elasticsearch'
```

**Solutions:**

1. Verify virtual environment is activated:
   ```bash
   which python3
   # Should show: /path/to/travel-agent-workshop/venv/bin/python3
   ```

2. If not activated:
   ```bash
   source venv/bin/activate
   ```

3. Reinstall packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Summary

Congratulations! You've completed Module 0. You now have:

✅ Elastic Cloud deployment with AgenticBuilder  
✅ ELSER model deployed and tested  
✅ AWS Bedrock access configured  
✅ Development environment ready  
✅ First "Hello World" agent working  

**Total time**: ~25 minutes

---

## Next Steps

Now you're ready to dive deep into ELSER semantic search!

**Continue to:** [Module 1: ELSER Semantic Search](../module-1-elser/)

In the next module, you'll learn how to:
- Index travel data with ELSER
- Perform cross-lingual semantic searches
- Compare ELSER vs traditional search
- Optimize search relevance

---

## Additional Resources

- [Elastic Cloud Documentation](https://www.elastic.co/guide/en/cloud/current/index.html)
- [ELSER Documentation](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)

---

**Questions or issues?** Check the [Troubleshooting Guide](../../docs/troubleshooting.md) or ask in the workshop chat.
