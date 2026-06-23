#!/bin/bash
# Quick Setup Script for Customer Support Agent

set -e

echo "======================================================================="
echo "  Customer Support Agent - Setup"
echo "======================================================================="
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python..."
python3 --version || { echo "Error: Python 3 not found"; exit 1; }
echo "✓ Python installed"
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing Python packages..."
pip install -r requirements-minimal.txt > /dev/null 2>&1 || {
    echo "Error: Failed to install packages"
    exit 1
}
echo "✓ Packages installed"
echo ""

# Step 3: Check config
echo "Step 3: Checking configuration..."
if [ ! -f "config/.env" ]; then
    echo "✗ config/.env not found"
    echo ""
    echo "Creating config/.env from template..."
    cp config/.env.example config/.env
    echo ""
    echo "⚠️  IMPORTANT: Edit config/.env with your credentials:"
    echo ""
    echo "nano config/.env"
    echo ""
    echo "You need to add:"
    echo "  - ES_URL (your Elasticsearch URL)"
    echo "  - ES_API_KEY (your NEW Elasticsearch API key)"
    echo ""
    echo "⚠️  DO NOT use the old exposed API key!"
    echo "   Create a new one in Kibana → Stack Management → API Keys"
    echo ""
    exit 1
fi

# Load environment
source config/.env

if [ -z "$ES_URL" ] || [ -z "$ES_API_KEY" ]; then
    echo "✗ ES_URL or ES_API_KEY not configured"
    echo ""
    echo "Edit config/.env and add your credentials:"
    echo "  ES_URL=https://your-deployment.es.us-east-1.aws.elastic.cloud:443"
    echo "  ES_API_KEY=your-new-api-key"
    echo ""
    exit 1
fi

echo "✓ Configuration file exists"
echo ""

# Step 4: Test Elasticsearch connection
echo "Step 4: Testing Elasticsearch connection..."
response=$(curl -s -w "\n%{http_code}" -H "Authorization: ApiKey $ES_API_KEY" "$ES_URL/_cluster/health" 2>/dev/null)
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" == "200" ]; then
    echo "✓ Elasticsearch connection successful"
else
    echo "✗ Elasticsearch connection failed (HTTP $http_code)"
    echo ""
    echo "Please check:"
    echo "  1. ES_URL is correct"
    echo "  2. ES_API_KEY is valid (create new one in Kibana)"
    echo "  3. Your deployment is accessible"
    echo ""
    exit 1
fi
echo ""

# Step 5: Create indices
echo "Step 5: Creating Elasticsearch indices..."
python3 infra/elasticsearch_setup.py || {
    echo "Error: Failed to create indices"
    exit 1
}
echo ""

# Step 6: Load sample data
echo "Step 6: Loading sample data..."
python3 infra/seed_data.py || {
    echo "Error: Failed to load data"
    exit 1
}
echo ""

echo "======================================================================="
echo "✓ Setup Complete!"
echo "======================================================================="
echo ""
echo "Next steps:"
echo "  1. Run the agent: python main.py"
echo "  2. Try queries:"
echo "     - What is your return policy?"
echo "     - Check status of order ORD-12345"
echo "     - Show me wireless headphones"
echo ""
echo "See TESTING_GUIDE.md for more test scenarios."
echo ""
