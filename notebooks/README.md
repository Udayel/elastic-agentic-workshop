# Interactive Jupyter Notebooks

**The easiest way to learn!** Step-by-step interactive notebooks with runnable code.

---

## 🎯 Why Jupyter Notebooks?

✅ **Interactive** - Run code cell-by-cell, see results immediately  
✅ **Easy to follow** - Clear explanations with executable examples  
✅ **No setup hassles** - Just configure credentials and go  
✅ **Visual feedback** - See search results, traces, and outputs  
✅ **Learn by doing** - Modify code and experiment  

---

## 📚 Available Notebooks

### 00-Setup-and-Verification.ipynb
**Time**: 15 minutes  
**What you'll do**:
- Install required packages
- Configure credentials
- Test Elastic Cloud connection
- Verify ELSER model
- Test AWS Bedrock access
- Run "Hello World" agent

**Start here if**: This is your first time

---

### 01-ELSER-Semantic-Search.ipynb
**Time**: 30 minutes  
**What you'll do**:
- Create ELSER-optimized indexes
- Load sample travel data
- Run semantic search queries
- Test cross-lingual search (Spanish, French, Japanese!)
- Compare ELSER vs traditional search
- Try your own queries

**Start here if**: You want to understand ELSER

---

### 02-MCP-Tools-and-Agents.ipynb (Coming Soon)
**Time**: 30 minutes  
**What you'll do**:
- Build MCP-compliant tools
- Create search tools for destinations, hotels, activities
- Test tool execution
- Integrate with Claude agents

---

### 03-Strands-Integration.ipynb (Coming Soon)
**Time**: 20 minutes  
**What you'll do**:
- Set up Strands-Elastic connector
- Search flights with real data
- Search hotels
- Get financial insights (PFM)

---

### 04-Build-Travel-Agent.ipynb (Coming Soon)
**Time**: 45 minutes  
**What you'll do**:
- Build complete travel agent
- Multi-tool orchestration
- Conversation memory
- End-to-end trip planning

---

## 🚀 Quick Start

### Step 1: Install Jupyter

```bash
pip install jupyter notebook ipykernel
```

### Step 2: Launch Jupyter

```bash
cd elastic-agentic-workshop/notebooks
jupyter notebook
```

Your browser will open automatically!

### Step 3: Start with Notebook 00

Click on `00-Setup-and-Verification.ipynb` and follow along!

---

## 📋 What You Need

### Required:
- ✅ Elastic Cloud deployment on AWS (8.15+)
- ✅ ELSER v2 model deployed
- ✅ AWS account with Bedrock access (Claude 3.5 Sonnet)
- ✅ Python 3.9-3.11

### Optional:
- ✅ Strands API key (for notebooks 03+)
- ✅ AgenticBuilder configured (for notebook 04)

---

## 💡 Tips for Success

### Running Cells
- **Shift + Enter**: Run cell and move to next
- **Ctrl + Enter**: Run cell and stay on it
- **Alt + Enter**: Run cell and insert new below

### If Something Goes Wrong
- **Restart kernel**: Kernel → Restart
- **Clear outputs**: Cell → All Output → Clear
- **Run from beginning**: Kernel → Restart & Run All

### Best Practices
1. **Run cells in order** - Don't skip ahead
2. **Read the markdown** - It explains what's happening
3. **Experiment!** - Modify code and see what happens
4. **Check outputs** - Make sure each cell succeeds before continuing

---

## 🎓 Learning Paths

### Path 1: Fast Track (1 hour)
```
00-Setup → 01-ELSER (skim examples) → Done
```
**Result**: Understanding of semantic search

### Path 2: Complete Workshop (3 hours)
```
00-Setup → 01-ELSER (all examples) → 
02-MCP-Tools → 03-Strands → 04-Build-Agent
```
**Result**: Working travel agent

### Path 3: ELSER Deep Dive (45 min)
```
00-Setup → 01-ELSER (try many queries, add your own data)
```
**Result**: ELSER expert

---

## 🔧 Troubleshooting

### "ModuleNotFoundError"
```bash
# In notebook cell:
!pip install package-name
```

### "Connection timeout" to Elastic
- Check credentials in notebook 00
- Verify deployment is running
- Test from terminal: `curl -u user:pass https://endpoint`

### "ELSER model not found"
- Go to Kibana → ML → Trained Models
- Download and deploy `.elser_model_2`

### "Kernel died"
- Too much memory used
- Restart: Kernel → Restart
- Or restart Jupyter server

### Cells take long time
- Bedrock API calls: 1-3 seconds normal
- ELSER search: < 1 second normal
- First ELSER call: May be slower (model loading)

---

## 📊 What Makes These Notebooks Special

### 1. Production-Ready Code
Not toy examples - actual code you can use in production

### 2. Elastic-First
Everything showcases Elastic's strengths (ELSER, connectors, APM)

### 3. Interactive Learning
See results immediately, experiment freely

### 4. Well-Documented
Every cell explained, every concept clear

### 5. No External Dependencies
Just Elastic + AWS Bedrock (+ optional Strands)

---

## 🎯 After the Notebooks

### Next Steps:
1. **Deploy to AWS** - Use Terraform (see `/terraform` directory)
2. **Build Custom Agent** - Adapt code for your use case
3. **Add More Data** - Index your own travel data
4. **Create UI** - Build Streamlit dashboard (see `/ui` directory)

### Advanced Topics:
- Multi-agent orchestration
- Production deployment
- Monitoring with APM
- Security hardening

---

## 📞 Getting Help

### In the Notebooks:
- Read markdown cells carefully
- Check cell outputs for errors
- Run verification cells

### Outside:
- **Elastic Docs**: https://www.elastic.co/guide
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/
- **Workshop Issues**: GitHub Issues
- **Community**: Elastic forums

---

## ✅ Notebook Completion Checklist

After finishing all notebooks, you should be able to:

- [ ] Explain what ELSER is and how it works
- [ ] Create ELSER-optimized Elasticsearch indexes
- [ ] Perform semantic searches that understand meaning
- [ ] Use cross-lingual search capabilities
- [ ] Build MCP-compliant tools
- [ ] Integrate Strands data with Elastic
- [ ] Build a complete AI travel agent
- [ ] Send notifications via AgenticBuilder
- [ ] Deploy everything to AWS

---

**Ready to start?** 

Open `00-Setup-and-Verification.ipynb` and let's go! 🚀

---

*Tips: Save notebooks frequently, experiment with code, have fun!*
