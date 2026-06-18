#!/bin/bash

# Travel Agent Workshop - GitHub Setup Script
# This script helps you quickly set up and push the workshop to GitHub

set -e  # Exit on error

echo "=================================================="
echo "  Travel Agent Workshop - GitHub Setup"
echo "  Version 3.2 - AWS Marketplace & SageMaker"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "workshop.html" ]; then
    echo -e "${RED}Error: workshop.html not found!${NC}"
    echo "Please run this script from the workshop root directory"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found workshop files"
echo ""

# Step 1: Initialize Git
echo "Step 1: Initializing Git repository..."
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠${NC}  Git repository already exists"
else
    git init
    echo -e "${GREEN}✓${NC} Git repository initialized"
fi
echo ""

# Step 2: Create .gitignore
echo "Step 2: Creating .gitignore..."
if [ -f ".gitignore" ]; then
    echo -e "${YELLOW}⚠${NC}  .gitignore already exists (keeping existing)"
else
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints
*/.ipynb_checkpoints/*

# Environment variables
.env
.env.local
*.env

# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
terraform.tfvars
*.tfvars
!terraform.tfvars.example

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Credentials
*password*
*secret*
*credentials*
*.pem
*.key

# Logs
*.log
logs/

# AWS
.aws/
EOF
    echo -e "${GREEN}✓${NC} .gitignore created"
fi
echo ""

# Step 3: Add files to git
echo "Step 3: Adding files to git..."
git add .
echo -e "${GREEN}✓${NC} Files added to staging"
echo ""

# Step 4: Create initial commit
echo "Step 4: Creating initial commit..."
if git rev-parse HEAD >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠${NC}  Commits already exist"
else
    git commit -m "Initial commit: Travel Intelligence Agent Workshop v3.2

- AWS Marketplace integration for Elastic Cloud
- SageMaker Jupyter notebook support
- Complete end-to-end guide (90-120 min)
- Interactive HTML workshop interface
- 7-day free trial support
- ELSER v2 semantic search
- Claude 3.5 Sonnet integration
- 8 Lambda microservices
- Full Terraform IaC
- Complete documentation"
    echo -e "${GREEN}✓${NC} Initial commit created"
fi
echo ""

# Step 5: Get GitHub repository URL
echo "Step 5: GitHub Repository Setup"
echo "=================================================="
echo ""
echo "Before continuing, create a new repository on GitHub:"
echo ""
echo "  1. Go to: https://github.com/new"
echo "  2. Repository name: travel-agent-workshop"
echo "  3. Description: Build Production AI Agents on AWS + Elastic Cloud"
echo "  4. Public or Private (your choice)"
echo "  5. DON'T initialize with README (we have one)"
echo "  6. Click 'Create repository'"
echo ""
read -p "Have you created the repository? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠${NC}  Exiting. Run this script again after creating the repository."
    exit 0
fi

echo ""
read -p "Enter your GitHub username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo -e "${RED}Error: GitHub username cannot be empty${NC}"
    exit 1
fi

REPO_URL="https://github.com/$GITHUB_USER/travel-agent-workshop.git"

echo ""
echo "Using repository URL: $REPO_URL"
echo ""

# Step 6: Add remote
echo "Step 6: Adding GitHub remote..."
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}⚠${NC}  Remote 'origin' already exists"
    echo "Current remote:"
    git remote get-url origin
    read -p "Update remote? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "$REPO_URL"
        echo -e "${GREEN}✓${NC} Remote updated"
    fi
else
    git remote add origin "$REPO_URL"
    echo -e "${GREEN}✓${NC} Remote added"
fi
echo ""

# Step 7: Push to GitHub
echo "Step 7: Pushing to GitHub..."
echo ""
read -p "Ready to push? This will upload all files to GitHub. (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠${NC}  Skipping push. You can push manually later with:"
    echo "  git push -u origin main"
    exit 0
fi

# Rename branch to main if it's master
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main
    echo -e "${GREEN}✓${NC} Renamed branch to 'main'"
fi

# Push
if git push -u origin main; then
    echo -e "${GREEN}✓${NC} Successfully pushed to GitHub!"
else
    echo -e "${RED}✗${NC} Push failed. You may need to authenticate."
    echo ""
    echo "If using HTTPS, you'll need a Personal Access Token:"
    echo "  1. Go to: https://github.com/settings/tokens"
    echo "  2. Generate new token (classic)"
    echo "  3. Select 'repo' scope"
    echo "  4. Use token as password when prompted"
    echo ""
    echo "Or use SSH instead:"
    echo "  git remote set-url origin git@github.com:$GITHUB_USER/travel-agent-workshop.git"
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Your repository is now live at:"
echo "  https://github.com/$GITHUB_USER/travel-agent-workshop"
echo ""
echo "Next steps:"
echo ""
echo "1. Enable GitHub Pages:"
echo "   • Go to: https://github.com/$GITHUB_USER/travel-agent-workshop/settings/pages"
echo "   • Source: Deploy from a branch"
echo "   • Branch: main, Folder: / (root)"
echo "   • Your workshop will be at:"
echo "     https://$GITHUB_USER.github.io/travel-agent-workshop/workshop.html"
echo ""
echo "2. Add repository details:"
echo "   • Go to: https://github.com/$GITHUB_USER/travel-agent-workshop"
echo "   • Click ⚙️ (Settings) at top right"
echo "   • Add description and topics"
echo ""
echo "3. Create a release:"
echo "   • Go to: https://github.com/$GITHUB_USER/travel-agent-workshop/releases/new"
echo "   • Tag: v3.2.0"
echo "   • Title: v3.2.0 - AWS Marketplace & SageMaker Edition"
echo ""
echo "4. Share your workshop:"
echo "   • Star the repository ⭐"
echo "   • Share on social media"
echo "   • Add to your README portfolio"
echo ""
echo "For detailed instructions, see: GITHUB_SETUP.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
