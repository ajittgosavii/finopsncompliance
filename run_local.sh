#!/bin/bash
# run_local.sh
# Helper script to run Cloud Compliance Canvas locally

echo "=========================================="
echo "Cloud Compliance Canvas - Local Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "❌ Python 3.11+ required. Current version: $python_version"
    exit 1
fi
echo "✅ Python version OK"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install/update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check for secrets file
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  Secrets file not found"
    echo "Creating .streamlit directory..."
    mkdir -p .streamlit
    
    if [ -f "secrets.toml.example" ]; then
        echo "Copying secrets template..."
        cp secrets.toml.example .streamlit/secrets.toml
        echo "✅ Secrets template copied to .streamlit/secrets.toml"
        echo ""
        echo "📝 Please edit .streamlit/secrets.toml with your configuration"
        echo "   For demo mode, you can use the default values"
        echo ""
    else
        echo "Creating basic secrets file..."
        cat > .streamlit/secrets.toml << 'EOF'
# Basic configuration for demo mode
organization_id = "demo-org-12345"

[features]
enable_aws_integration = false
demo_mode_default = true
EOF
        echo "✅ Basic secrets file created"
        echo ""
    fi
fi

# Check for config file
if [ ! -f ".streamlit/config.toml" ]; then
    echo "Creating Streamlit config..."
    mkdir -p .streamlit
    
    if [ -f ".streamlit_config.toml" ]; then
        cp .streamlit_config.toml .streamlit/config.toml
    else
        cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#4A90E2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8F9FA"
textColor = "#212529"

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
EOF
    fi
    echo "✅ Streamlit config created"
    echo ""
fi

echo "=========================================="
echo "🚀 Starting Streamlit application..."
echo "=========================================="
echo ""
echo "App will be available at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run Streamlit
streamlit run app.py
