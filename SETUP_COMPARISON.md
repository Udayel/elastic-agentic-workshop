# Setup Options Comparison

## Choose the Best Setup Path for You

This workshop offers multiple ways to run — pick what fits your situation:

---

## 📊 Quick Comparison Table

| Aspect | Local Jupyter | SageMaker Studio Lab | SageMaker Notebook | SageMaker Studio |
|--------|--------------|---------------------|-------------------|------------------|
| **Cost** | Free | FREE | ~$0.05/hour | ~$0.05/hour |
| **AWS Account Required** | Yes (for Bedrock) | No (initially) | Yes | Yes |
| **Setup Time** | 30 min | 10 min | 10 min | 15 min (first time) |
| **AWS Credentials** | Manual config | Manual | ✅ Automatic (IAM) | ✅ Automatic (IAM) |
| **Session Limit** | Unlimited | 4 hours | Unlimited | Unlimited |
| **Storage** | Local disk | 15GB persistent | 20GB+ persistent | Persistent |
| **Compute** | Your laptop | ml.t3.large (free) | ml.t3.medium | ml.t3.medium |
| **Best For** | Local dev | Learning/trial | Workshops/AWS users | Teams/enterprise |
| **Network** | Your network | Public internet | VPC (configurable) | VPC (configurable) |
| **Auto-save** | Manual | ✅ Automatic | ✅ Automatic | ✅ Automatic |
| **IDE Integration** | VS Code, etc. | Web only | Web/SSH | Web |
| **Team Sharing** | Via Git | Via Git | Via Git/S3 | ✅ Native sharing |

---

## 🎯 Decision Tree

### Start Here: Do you have an AWS account?

```
Do you have an AWS account?
│
├─ NO → 🌟 SageMaker Studio Lab (FREE!)
│         - No AWS account needed
│         - 100% free compute
│         - Best for learning
│         - Go to: SAGEMAKER_SETUP.md → Option 1
│
└─ YES → Do you want to run in AWS?
          │
          ├─ YES → Are you part of a team?
          │        │
          │        ├─ YES → SageMaker Studio
          │        │         - Team collaboration
          │        │         - MLOps features
          │        │         - Go to: SAGEMAKER_SETUP.md → Option 3
          │        │
          │        └─ NO → 🌟 SageMaker Notebook Instance (RECOMMENDED)
          │                  - IAM role = auto credentials
          │                  - Persistent environment
          │                  - ~$0.05/hour
          │                  - Go to: SAGEMAKER_SETUP.md → Option 2
          │
          └─ NO → Local Jupyter
                   - Full control
                   - Use your laptop
                   - Go to: notebooks/README.md
```

---

## 🌟 Recommended Paths by Use Case

### Learning / First Time

**Best choice**: **SageMaker Studio Lab** (FREE)

✅ Why:
- No AWS account needed (request free account)
- Zero cost
- No credit card required
- Perfect for experimentation
- 4-hour sessions (restart anytime)

⚠️ Limitations:
- Manual AWS credential configuration
- 4-hour session limit
- Public internet only

**Setup time**: 10 minutes (after account approval)

---

### AWS Customer / Workshop Participant

**Best choice**: **SageMaker Notebook Instance**

✅ Why:
- Automatic AWS credentials (IAM role!)
- Same VPC as your Elastic deployment (optional)
- Low latency to Bedrock & Elastic
- Cost-effective (~$0.20 for full workshop)
- Stop when not using = $0

⚠️ Considerations:
- Requires AWS account
- Basic AWS knowledge helpful

**Setup time**: 10 minutes

---

### Enterprise / Team Environment

**Best choice**: **SageMaker Studio**

✅ Why:
- Team collaboration features
- Shared environments
- Git integration
- MLOps workflow support
- Governed access

⚠️ Considerations:
- Requires Studio domain setup (one-time)
- More AWS permissions needed
- Slightly higher complexity

**Setup time**: 15 minutes (first time), 5 minutes (subsequent)

---

### Local Development / Full Control

**Best choice**: **Local Jupyter**

✅ Why:
- Full control over environment
- No AWS compute costs
- Works offline (except Bedrock/Elastic calls)
- Use familiar IDE (VS Code, etc.)
- No session limits

⚠️ Considerations:
- Requires local Python setup
- Manual dependency management
- Manual credential configuration
- Potential version conflicts

**Setup time**: 30 minutes

---

## 💰 Cost Breakdown

### Total Workshop Cost by Option

| Option | Compute | Elastic | Bedrock | Total |
|--------|---------|---------|---------|-------|
| **Studio Lab** | $0 (FREE) | ~$0 (trial) | ~$3-5 | **~$3-5** |
| **SageMaker Notebook** | ~$0.20 | ~$0 (trial) | ~$3-5 | **~$3-5** |
| **SageMaker Studio** | ~$0.20 | ~$0 (trial) | ~$3-5 | **~$3-5** |
| **Local Jupyter** | $0 | ~$0 (trial) | ~$3-5 | **~$3-5** |

**Notes:**
- Elastic: **7-day free trial** via AWS Marketplace
- Bedrock: Pay-per-use via AWS (~$3/M tokens, workshop uses ~1M)
- SageMaker: ml.t3.medium = $0.0582/hour via AWS (~3-4 hours = $0.20)
- **All charges consolidated on your AWS bill**
- Delete resources after workshop = $0 ongoing cost

---

## 🔒 Security Comparison

| Feature | Local | Studio Lab | Notebook Instance | Studio |
|---------|-------|-----------|------------------|--------|
| **AWS Credentials** | File-based | File-based | ✅ IAM role | ✅ IAM role |
| **Secrets Manager** | ❌ Manual | ❌ Manual | ✅ Supported | ✅ Supported |
| **VPC Isolation** | N/A | ❌ Public | ✅ Configurable | ✅ Configurable |
| **Network Control** | Your network | Public | VPC Security Groups | VPC + Studio |
| **IAM Policies** | Via credentials | Via credentials | ✅ Role-based | ✅ Role-based |
| **Audit Logging** | ❌ None | ❌ Limited | ✅ CloudTrail | ✅ CloudTrail |
| **Data Encryption** | Local disk | ✅ EBS encrypted | ✅ EBS encrypted | ✅ EBS encrypted |

**Most secure for enterprise**: SageMaker Notebook Instance or Studio with VPC

---

## ⚡ Performance Comparison

### Bedrock Latency (Same Region: us-east-1)

| Setup | Network Path | Typical Latency |
|-------|-------------|-----------------|
| **Local** | Home → Internet → Bedrock | 50-200ms |
| **Studio Lab** | AWS Public → Bedrock | 5-20ms |
| **Notebook Instance** | AWS VPC → Bedrock | 1-5ms ✅ |
| **Studio** | AWS VPC → Bedrock | 1-5ms ✅ |

### Elastic Cloud Latency (us-east-1)

| Setup | Network Path | Typical Latency |
|-------|-------------|-----------------|
| **Local** | Home → Internet → Elastic | 50-200ms |
| **Studio Lab** | AWS Public → Elastic | 5-20ms |
| **Notebook Instance** | AWS VPC → Elastic (public) | 5-20ms |
| **Notebook Instance** | AWS VPC → Elastic (PrivateLink) | 1-5ms ✅ |
| **Studio** | AWS VPC → Elastic (PrivateLink) | 1-5ms ✅ |

**Fastest**: SageMaker in VPC with PrivateLink to Elastic

---

## 📋 Feature Support Matrix

### What Works Where

| Feature | Local | Studio Lab | Notebook | Studio |
|---------|-------|-----------|----------|--------|
| **All Notebooks** | ✅ | ✅ | ✅ | ✅ |
| **ELSER Search** | ✅ | ✅ | ✅ | ✅ |
| **Bedrock/Claude** | ✅ | ✅ | ✅ | ✅ |
| **MCP Tools** | ✅ | ✅ | ✅ | ✅ |
| **Strands API** | ✅ | ✅ | ✅ | ✅ |
| **IAM Role Auth** | ❌ | ❌ | ✅ | ✅ |
| **Secrets Manager** | Manual | Manual | ✅ Auto | ✅ Auto |
| **VPC Deployment** | N/A | ❌ | ✅ | ✅ |
| **Team Sharing** | Git | Git | Git/S3 | ✅ Native |
| **GPU Support** | Depends | ❌ | ✅ | ✅ |

---

## 🚀 Quick Start Commands

### Option 1: SageMaker Studio Lab

```bash
# 1. Request account at: https://studiolab.sagemaker.aws
# 2. Wait for approval (1-3 days)
# 3. Login → Start runtime → Open project
# 4. Clone repo:
git clone https://github.com/elastic/travel-agent-workshop.git
cd travel-agent-workshop/notebooks
# 5. Open: 00-Setup-SageMaker.ipynb
```

---

### Option 2: SageMaker Notebook Instance

```bash
# In AWS Console → SageMaker → Create notebook instance
# Name: travel-agent-workshop
# Type: ml.t3.medium
# IAM role: Create new (with Bedrock access)
# Wait 5 min → Open JupyterLab → Terminal:

cd SageMaker
git clone https://github.com/elastic/travel-agent-workshop.git
cd travel-agent-workshop/notebooks
# Open: 00-Setup-SageMaker.ipynb
```

---

### Option 3: Local Jupyter

```bash
# Install Jupyter
pip install jupyter notebook ipykernel

# Clone repo
git clone https://github.com/elastic/travel-agent-workshop.git
cd travel-agent-workshop/notebooks

# Launch
jupyter notebook

# Open: 00-Setup-and-Verification.ipynb
```

---

## 🎯 Final Recommendations

### By Priority

**Priority: Learning & Experimentation**
→ SageMaker Studio Lab (FREE)

**Priority: Professional Workshop / Production-like**
→ SageMaker Notebook Instance (IAM role, ~$0.20)

**Priority: Team Collaboration**
→ SageMaker Studio (team features)

**Priority: Full Control / Offline Work**
→ Local Jupyter (your laptop)

---

### By AWS Experience Level

**Beginner** (new to AWS)
→ SageMaker Studio Lab (simpler, no AWS config)

**Intermediate** (familiar with AWS)
→ SageMaker Notebook Instance (best balance)

**Advanced** (AWS power user)
→ SageMaker Studio or Local (your choice)

---

### By Time Available

**< 15 minutes setup time**
→ SageMaker Studio Lab or Notebook Instance

**< 30 minutes setup time**
→ Any option works

**> 30 minutes available**
→ Local Jupyter (more setup, more control)

---

## 📞 Getting Help

### Setup Issues

**SageMaker**: See [SAGEMAKER_SETUP.md](./SAGEMAKER_SETUP.md) troubleshooting section

**Local Jupyter**: See [notebooks/README.md](./notebooks/README.md) troubleshooting

**Elastic Cloud**: See [AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md) troubleshooting

**General**: Check [INDEX.md](./INDEX.md) for navigation

---

## ✅ Ready to Start?

1. **Choose your option** from the table above
2. **Follow the setup guide**:
   - SageMaker: [SAGEMAKER_SETUP.md](./SAGEMAKER_SETUP.md)
   - Local: [notebooks/README.md](./notebooks/README.md)
   - Elastic Cloud: [AWS_MARKETPLACE_SETUP.md](./AWS_MARKETPLACE_SETUP.md)
3. **Open the first notebook**: `00-Setup-*.ipynb`
4. **Start learning!** 🚀

---

*Last Updated: June 18, 2026*  
*For: Travel Intelligence Agent Workshop*  
*Optimized for AWS + Elastic customers*
