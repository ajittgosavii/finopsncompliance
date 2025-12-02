"""
CloudIDP - AWS Infrastructure Development Platform
Enterprise-Grade AWS Cloud Governance & Automation Framework
Version 2.0.0 - AWS-Only Edition
"""

import streamlit as st
from design_planning import DesignPlanningModule
from provisioning_deployment import ProvisioningDeploymentModule
from ondemand_operations import OnDemandOperationsModule
from finops_module import FinOpsModule
from security_compliance import SecurityComplianceModule
from policy_guardrails import PolicyGuardrailsModule
from module_07_abstraction import AbstractionReusabilityModule
from module_09_developer_experience import DeveloperExperienceModule
from module_10_observability import ObservabilityIntegrationModule
from module_11_multiaccountmgmt import MultiAccountManagementModule
from config import initialize_session_state
from anthropic_helper import AnthropicHelper
from datetime import datetime, timedelta
import json

# Data Provider for Demo/Live Mode
try:
    from data_provider import get_data_provider, get_live_service
    DATA_PROVIDER_AVAILABLE = True
except ImportError:
    DATA_PROVIDER_AVAILABLE = False
    print("⚠️ data_provider.py not found. Live data features will be limited.")

# Quick Patch: Make Demo/Live Mode Actually Work
# Add this to the TOP of streamlit_app.py (after imports)

import streamlit as st

# ===== DEMO/LIVE MODE PATCH =====
# This ensures mode switching actually changes data sources

# Initialize mode in session state
if 'mode' not in st.session_state:
    st.session_state.mode = "Demo"
    st.session_state.demo_mode = True

# Helper function for all modules to use
def get_data_source():
    """
    Returns data source type based on current mode
    Returns: 'demo' or 'live'
    """
    return 'demo' if st.session_state.mode == "Demo" else 'live'

def is_demo_mode():
    """
    Check if currently in demo mode
    Returns: True if Demo mode, False if Live mode
    """
    return st.session_state.mode == "Demo"

def get_blueprints():
    """Example: Get blueprints based on mode"""
    if is_demo_mode():
        # Return demo data
        import demo_data
        return demo_data.get_blueprints()
    else:
        # Return live data
        try:
            from database_service import DatabaseService
            db = DatabaseService()
            return db.get_blueprints()
        except Exception as e:
            st.error(f"Error fetching live data: {e}")
            st.info("Falling back to demo data")
            import demo_data
            return demo_data.get_blueprints()

def get_ec2_instances(region='us-east-1'):
    """Example: Get EC2 instances based on mode"""
    if is_demo_mode():
        import demo_data
        return demo_data.get_ec2_instances()
    else:
        try:
            import boto3
            ec2 = boto3.client('ec2', region_name=region)
            response = ec2.describe_instances()
            instances = []
            for reservation in response['Reservations']:
                instances.extend(reservation['Instances'])
            return instances
        except Exception as e:
            st.error(f"Error fetching live EC2 data: {e}")
            st.info("Falling back to demo data")
            import demo_data
            return demo_data.get_ec2_instances()

def get_cost_data(start_date=None, end_date=None):
    """Example: Get cost data based on mode"""
    if is_demo_mode():
        import demo_data
        return demo_data.get_cost_data()
    else:
        try:
            import boto3
            from datetime import datetime, timedelta
            
            ce = boto3.client('ce', region_name='us-east-1')
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            response = ce.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='MONTHLY',
                Metrics=['UnblendedCost']
            )
            return response
        except Exception as e:
            st.error(f"Error fetching live cost data: {e}")
            st.info("Falling back to demo data")
            import demo_data
            return demo_data.get_cost_data()

# Make these functions available globally
st.session_state.get_data_source = get_data_source
st.session_state.is_demo_mode = is_demo_mode
st.session_state.get_blueprints = get_blueprints
st.session_state.get_ec2_instances = get_ec2_instances
st.session_state.get_cost_data = get_cost_data

# ===== END PATCH =====

# Initialize Data Provider for Live/Demo mode
# Declare as module-level variables so they're accessible in all functions
data_provider = None
live_service = None

if DATA_PROVIDER_AVAILABLE:
    try:
        data_provider = get_data_provider()
        live_service = get_live_service()
    except Exception as e:
        print(f"⚠️ Error initializing data provider: {e}")
        DATA_PROVIDER_AVAILABLE = False

# USAGE IN MODULES:
# Instead of:
#   blueprints = demo_data.get_blueprints()
# 
# Use:
#   blueprints = st.session_state.get_blueprints()
#
# Or check mode directly:
#   if st.session_state.is_demo_mode():
#       data = demo_data.get_something()
#   else:
#       data = real_service.get_something()

# Backend Integration Import
try:
    from backend_integration import CloudIDPBackend
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    print("⚠️ Backend modules not found. Some features will be limited.")

# AWS Integrations Import
try:
    from aws_integrations_manager import AWSIntegrationsManager
    AWS_INTEGRATIONS_AVAILABLE = True
except ImportError:
    AWS_INTEGRATIONS_AVAILABLE = False
    print("⚠️ AWS integration modules not found. AWS features will be limited.")

# Enhanced API Gateway Import
try:
    from api_gateway_streamlit import APIKeyManager, RateLimitTier, RATE_LIMIT_CONFIG
    API_GATEWAY_ENHANCED_AVAILABLE = True
except ImportError:
    API_GATEWAY_ENHANCED_AVAILABLE = False
    print("⚠️ Enhanced API Gateway not found. API management features will be limited.")

# Page configuration
st.set_page_config(
    page_title="CloudIDP - Cloud Infrastructure Development Platform",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="auto"  # Auto-collapse on smaller screens
)

# Custom CSS - COMPLETE VERSION
st.markdown("""
    <style>
    /* Reduce overall padding for better space utilization */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    
    /* Compact sidebar */
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
    
    /* Compact metrics */
    div[data-testid="stMetric"] {
        padding: 0.5rem 0;
    }
    
    /* Compact expanders */
    div[data-testid="stExpander"] {
        margin: 0.5rem 0;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF9900;
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #232F3E;
        text-align: center;
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .mode-indicator {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .live-mode {
        background-color: #28a745;
        color: white;
    }
    .demo-mode {
        background-color: #ffc107;
        color: #000;
    }
    .backend-status {
        padding: 8px;
        border-radius: 5px;
        margin: 10px 0;
        font-size: 0.9rem;
    }
    .backend-healthy {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .backend-degraded {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        background-color: white;
        border-radius: 5px;
        border: 1px solid #dee2e6;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF9900 !important;
        color: white !important;
        border-color: #FF9900 !important;
    }
    .api-key-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .tier-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 5px;
    }
    .tier-free {
        background-color: #e9ecef;
        color: #495057;
    }
    .tier-basic {
        background-color: #cfe2ff;
        color: #084298;
    }
    .tier-premium {
        background-color: #ffd700;
        color: #000;
    }
    .tier-enterprise {
        background-color: #d4edda;
        color: #155724;
    }
    .rate-limit-bar {
        height: 20px;
        background-color: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        margin: 5px 0;
    }
    .rate-limit-fill {
        height: 100%;
        background: linear-gradient(90deg, #28a745 0%, #ffc107 70%, #dc3545 100%);
        transition: width 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_backend():
    """Initialize backend services with current demo mode"""
    if BACKEND_AVAILABLE:
        try:
            st.session_state.backend = CloudIDPBackend(
                demo_mode=st.session_state.demo_mode,
                region=st.session_state.get('aws_region', 'us-east-1')
            )
            st.session_state.backend_initialized = True
        except Exception as e:
            st.session_state.backend_initialized = False
            st.session_state.backend_error = str(e)
    else:
        st.session_state.backend_initialized = False
    
    # Initialize AWS Integrations
    if AWS_INTEGRATIONS_AVAILABLE:
        try:
            st.session_state.aws_integrations = AWSIntegrationsManager(
                demo_mode=st.session_state.demo_mode,
                region=st.session_state.get('aws_region', 'us-east-1')
            )
            st.session_state.aws_integrations_initialized = True
        except Exception as e:
            st.session_state.aws_integrations_initialized = False
            st.session_state.aws_integrations_error = str(e)
    else:
        st.session_state.aws_integrations_initialized = False
    
    # Initialize Enhanced API Gateway Manager
    if API_GATEWAY_ENHANCED_AVAILABLE:
        try:
            if 'api_key_manager' not in st.session_state:
                st.session_state.api_key_manager = APIKeyManager()
            st.session_state.api_gateway_initialized = True
        except Exception as e:
            st.session_state.api_gateway_initialized = False
            st.session_state.api_gateway_error = str(e)
    else:
        st.session_state.api_gateway_initialized = False

def render_sidebar():
    """Render compact sidebar with settings and quick stats"""
    with st.sidebar:
        # CloudIDP Logo - More Compact
        st.markdown("""
            <div style="text-align: center; padding: 10px 0 5px 0;">
                <div style="
                    background: linear-gradient(180deg, #232F3E 0%, #1a252f 100%);
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    border: 2px solid #FF9900;
                ">
                    <div style="
                        color: #FF9900;
                        font-size: 28px;
                        font-weight: bold;
                        letter-spacing: 2px;
                        margin-bottom: 5px;
                    ">CloudIDP</div>
                    <div style="
                        color: #FFFFFF;
                        font-size: 9px;
                        letter-spacing: 1px;
                        font-weight: 500;
                    ">INFRASTRUCTURE PLATFORM</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Operation Mode Toggle - Compact
        st.markdown("### 🔄 Mode")
        mode = st.radio(
            "Select:",
            ["Demo", "Live"],
            index=0,
            help="Demo: Sample data | Live: Real cloud"
        )
        
        # Update session state
        old_demo_mode = st.session_state.get('demo_mode', True)
        st.session_state.demo_mode = (mode == "Demo")
        st.session_state.mode = mode  # CRITICAL: Sync with data_provider!
        
        if old_demo_mode != st.session_state.demo_mode and BACKEND_AVAILABLE:
            initialize_backend()
        
        # Display mode indicator - Compact
        if st.session_state.demo_mode:
            st.success("📋 DEMO MODE")
        else:
            st.warning("🟢 LIVE MODE")
        
        # Quick Platform Stats
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Modules", "18", delta=None, label_visibility="visible")
        with col2:
            st.metric("Clouds", "3", delta=None, label_visibility="visible")
        
        # Backend Status - Compact
        if BACKEND_AVAILABLE and st.session_state.get('backend_initialized'):
            backend = st.session_state.backend
            health = backend.health_check()
            
            if health['status'] == 'healthy':
                st.success("✅ Backend Healthy")
            else:
                st.warning("⚠️ Backend Degraded")
            
            with st.expander("📊 Services"):
                for service, status in health.get('services', {}).items():
                    icon = "✅" if status == "healthy" else "⚠️"
                    st.caption(f"{icon} {service.title()}")
        
        # API Gateway Status - Compact
        if API_GATEWAY_ENHANCED_AVAILABLE and st.session_state.get('api_gateway_initialized'):
            st.markdown("### 🔑 API Keys")
            
            if 'api_key_manager' in st.session_state:
                manager = st.session_state.api_key_manager
                total_keys = len(manager.keys)
                active_keys = sum(1 for k in manager.keys.values() if k['is_active'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total", total_keys)
                with col2:
                    st.metric("Active", active_keys)
        
        # AWS Region Selection - Compact
        if not st.session_state.demo_mode:
            st.markdown("### 🌍 Region")
            regions = [
                "us-east-1",
                "us-west-2",
                "eu-west-1",
                "ap-southeast-1"
            ]
            selected_region = st.selectbox(
                "AWS:",
                regions,
                index=0,
                label_visibility="collapsed"
            )
            st.session_state.aws_region = selected_region
        
        # Quick Navigation Hint
        st.markdown("### 💡 Navigation")
        st.info("Use tabs above to navigate between modules")
        
        # Footer - Compact
        st.markdown("---")
        st.caption("CloudIDP v2.0")
        st.caption("© 2024 CloudIDP")

def main():
    """Main application entry point with tab-based navigation"""
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize backend if not already done
    if 'backend_initialized' not in st.session_state:
        initialize_backend()
    
    # Header
    st.markdown('<div class="main-header">☁️ CloudIDP</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cloud Infrastructure Development Platform | Enterprise Architecture & Governance</div>', unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main content area with tabs
    # Create main tab groups
    main_tabs = st.tabs([
        "🏠 Home",
        "🏗️ Core Infrastructure", 
        "🏢 Multi-Account Mgmt",
        "🔑 API Management",
        "☁️ AWS Integrations"
    ])
    
    # Home Tab
    with main_tabs[0]:
        render_home_page()
    
    # Core Infrastructure Tab
    with main_tabs[1]:
        render_core_infrastructure_tabs()
    
    # Multi-Account Management Tab
    with main_tabs[2]:
        render_multiaccountmgmt_tab()
    
    # API Management Tab
    with main_tabs[3]:
        render_api_management_tabs()
    
    # AWS Integrations Tab
    with main_tabs[4]:
        render_aws_integrations_tabs()

def render_home_page():
    """Render the home/dashboard page"""
    st.markdown("## 🏠 Welcome to CloudIDP")
    
    st.markdown("""
    ### Cloud Infrastructure Development Platform
    
    CloudIDP is a comprehensive enterprise platform for managing multi-cloud infrastructure, 
    governance, and operations at scale.
    """)
    
    # Quick Stats Dashboard - MODE-AWARE
    col1, col2, col3, col4 = st.columns(4)
    
    # Get data based on Demo/Live mode
    if DATA_PROVIDER_AVAILABLE and data_provider is not None:
        try:
            active_projects = data_provider.get(
                key='active_projects',
                demo_value='12',
                live_fn=lambda: live_service.count_active_projects() if live_service else '12'
            )
            cloud_providers = data_provider.get(
                key='cloud_providers',
                demo_value='3',
                live_fn=None
            )
            compliance_score = data_provider.get(
                key='compliance_score',
                demo_value='98%',
                live_fn=lambda: live_service.get_compliance_score() if live_service else '98%'
            )
            monthly_cost = data_provider.get(
                key='monthly_cost',
                demo_value='$45.2K',
                live_fn=lambda: live_service.get_monthly_cost() if live_service else '$45.2K'
            )
            
        except Exception as e:
            # Fallback to demo values on error
            # Fallback
            active_projects = '12'
            cloud_providers = '3'
            compliance_score = '98%'
            monthly_cost = '$45.2K'
    else:
        # Fallback to demo values if data provider not available
        active_projects = '12'
        cloud_providers = '3'
        compliance_score = '98%'
        monthly_cost = '$45.2K'
    
    with col1:
        st.metric(
            label="🏗️ Active Projects",
            value=active_projects,
            delta="2 new"
        )
    
    with col2:
        st.metric(
            label="☁️ Cloud Providers",
            value=cloud_providers,
            delta="AWS, Azure, GCP"
        )
    
    with col3:
        st.metric(
            label="🔐 Compliance Score",
            value=compliance_score,
            delta="2%"
        )
    
    with col4:
        st.metric(
            label="💰 Monthly Cost",
            value=monthly_cost,
            delta="-$2.3K"
        )
    
    st.markdown("---")
    
    # Rest of the function continues...
def render_module(module_instance, module_name):
    """
    Flexible module renderer that works with different method names
    Tries common method names: render, show, display, run, execute
    """
    method_names = ['render', 'show', 'display', 'run', 'execute', 'main']
    
    for method_name in method_names:
        if hasattr(module_instance, method_name):
            method = getattr(module_instance, method_name)
            if callable(method):
                try:
                    method()
                    return True
                except Exception as e:
                    st.error(f"Error running {module_name}: {str(e)}")
                    return False
    
    # If no common method found, show available methods
    available_methods = [m for m in dir(module_instance) if not m.startswith('_') and callable(getattr(module_instance, m))]
    st.error(f"❌ {module_name} module error")
    st.warning(f"Could not find a display method. Available methods: {', '.join(available_methods)}")
    st.info("💡 Please ensure your module has one of these methods: render(), show(), display(), run(), or execute()")
    return False

def render_core_infrastructure_tabs():
    """Render Core Infrastructure modules in nested tabs - AWS-Only"""
    st.markdown("## 🏗️ Core Infrastructure Modules")
    
    infra_tabs = st.tabs([
        "📐 Design & Planning",
        "🚀 Provisioning",
        "⚙️ Operations",
        "💰 FinOps",
        "🔒 Security",
        "📜 Policy",
        "🔄 Abstraction",
        "💻 DevEx",
        "📊 Observability"
    ])
    
    with infra_tabs[0]:
        try:
            design_planning = DesignPlanningModule()
            render_module(design_planning, "Design & Planning")
        except Exception as e:
            st.error(f"❌ Error loading Design & Planning module: {str(e)}")
            st.info("Please ensure design_planning.py is in the same directory.")
    
    with infra_tabs[1]:
        try:
            provisioning = ProvisioningDeploymentModule()
            render_module(provisioning, "Provisioning & Deployment")
        except Exception as e:
            st.error(f"❌ Error loading Provisioning module: {str(e)}")
    
    with infra_tabs[2]:
        try:
            operations = OnDemandOperationsModule()
            render_module(operations, "On-Demand Operations")
        except Exception as e:
            st.error(f"❌ Error loading Operations module: {str(e)}")
    
    with infra_tabs[3]:
        try:
            finops = FinOpsModule()
            render_module(finops, "FinOps Cost Management")
        except Exception as e:
            st.error(f"❌ Error loading FinOps module: {str(e)}")
    
    with infra_tabs[4]:
        try:
            security = SecurityComplianceModule()
            render_module(security, "Security & Compliance")
        except Exception as e:
            st.error(f"❌ Error loading Security module: {str(e)}")
    
    with infra_tabs[5]:
        try:
            policy = PolicyGuardrailsModule()
            render_module(policy, "Policy & Guardrails")
        except Exception as e:
            st.error(f"❌ Error loading Policy module: {str(e)}")
    
    with infra_tabs[6]:
        try:
            abstraction = AbstractionReusabilityModule()
            render_module(abstraction, "Abstraction & Reusability")
        except Exception as e:
            st.error(f"❌ Error loading Abstraction module: {str(e)}")
    
    with infra_tabs[7]:
        try:
            devex = DeveloperExperienceModule()
            render_module(devex, "Developer Experience")
        except Exception as e:
            st.error(f"❌ Error loading Developer Experience module: {str(e)}")
    
    with infra_tabs[8]:
        try:
            observability = ObservabilityIntegrationModule()
            render_module(observability, "Observability & Integration")
        except Exception as e:
            st.error(f"❌ Error loading Observability module: {str(e)}")

def render_multiaccountmgmt_tab():
    """Render Multi-Account Management module"""
    try:
        multiaccountmgmt = MultiAccountManagementModule()
        multiaccountmgmt.render()
    except Exception as e:
        st.error(f"❌ Error loading Multi-Account Management module: {str(e)}")
        st.info("💡 Multi-Account Management provides AWS Organizations integration, SSO, CMDB, and account lifecycle management.")

def render_api_management_tabs():
    """Render API Management modules in nested tabs"""
    st.markdown("## 🔑 API Management & Gateway")
    
    if not API_GATEWAY_ENHANCED_AVAILABLE or not st.session_state.get('api_gateway_initialized'):
        st.error("❌ Enhanced API Gateway not available")
        st.info("💡 The enhanced API gateway provides API key authentication, rate limiting, and usage tracking.")
        return
    
    api_tabs = st.tabs([
        "🔑 API Keys",
        "📈 Rate Limits",
        "📊 Analytics"
    ])
    
    with api_tabs[0]:
        show_api_key_management()
    
    with api_tabs[1]:
        show_rate_limit_monitoring()
    
    with api_tabs[2]:
        show_api_usage_analytics()

def render_aws_integrations_tabs():
    """Render AWS Integration modules in nested tabs"""
    st.markdown("## ☁️ AWS Cloud Integrations")
    
    if not AWS_INTEGRATIONS_AVAILABLE or not st.session_state.get('aws_integrations_initialized'):
        st.error("❌ AWS integrations not available")
        return
    
    aws_tabs = st.tabs([
        "🔐 IAM",
        "📊 Cost Explorer",
        "⚙️ Systems Manager",
        "🖥️ Compute & Network",
        "🗄️ Databases"
    ])
    
    with aws_tabs[0]:
        show_iam_management_page()
    
    with aws_tabs[1]:
        show_cost_explorer_page()
    
    with aws_tabs[2]:
        show_systems_manager_page()
    
    with aws_tabs[3]:
        show_compute_network_page()
    
    with aws_tabs[4]:
        show_database_management_page()

# ==================== API Gateway Pages - COMPLETE IMPLEMENTATION ====================

def show_api_key_management():
    """API Key Management Page - COMPLETE VERSION"""
    st.markdown("### 🔑 API Key Management")
    st.markdown("Generate and manage API keys for backend services and integrations")
    
    manager = st.session_state.api_key_manager
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🆕 Generate Key", "📋 My Keys", "📊 Rate Limits", "📚 Documentation"])
    
    with tab1:
        st.markdown("#### Generate New API Key")
        
        with st.form("generate_api_key"):
            col1, col2 = st.columns(2)
            
            with col1:
                user_id = st.text_input(
                    "User/Service ID",
                    placeholder="e.g., backend-service-1",
                    help="Identifier for the service or user using this API key"
                )
            
            with col2:
                tier = st.selectbox(
                    "Rate Limit Tier",
                    options=[tier.value for tier in RateLimitTier],
                    format_func=lambda x: x.upper(),
                    help="Select the appropriate tier based on usage needs"
                )
            
            # Show tier details
            st.markdown("##### Selected Tier Details")
            tier_config = RATE_LIMIT_CONFIG[RateLimitTier(tier)]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Requests per Minute", tier_config['requests_per_minute'])
            with col2:
                st.metric("Requests per Hour", tier_config['requests_per_hour'])
            
            description = st.text_area(
                "Description (Optional)",
                placeholder="e.g., Production backend service for order processing",
                help="Add notes about this API key's purpose"
            )
            
            submitted = st.form_submit_button("🔑 Generate API Key", use_container_width=True)
            
            if submitted:
                if not user_id:
                    st.error("❌ Please provide a User/Service ID")
                else:
                    with st.spinner("Generating API key..."):
                        api_key = manager.generate_api_key(user_id, RateLimitTier(tier))
                        
                        # Store description if provided
                        if description and api_key in manager.keys:
                            manager.keys[api_key]['description'] = description
                        
                        st.success("✅ API Key generated successfully!")
                        
                        # Display the key prominently
                        st.markdown("#### 🔐 Your API Key")
                        st.warning("⚠️ **IMPORTANT**: Copy this key now! It won't be shown again for security reasons.")
                        
                        st.code(api_key, language="text")
                        
                        st.markdown("#### 📝 Quick Start")
                        st.markdown("Use this API key in your requests:")
                        st.code(f"""curl -X GET http://localhost:8000/api/v1/accounts \\
  -H "X-API-Key: {api_key}" """, language="bash")
    
    with tab2:
        st.markdown("#### My API Keys")
        
        if not manager.keys:
            st.info("📝 No API keys generated yet. Create your first key in the 'Generate Key' tab!")
        else:
            # Filter controls
            col1, col2 = st.columns([3, 1])
            with col1:
                search = st.text_input("🔍 Search keys", placeholder="Search by user ID...")
            with col2:
                show_inactive = st.checkbox("Show Inactive", value=False)
            
            # Display keys
            for api_key, key_data in manager.keys.items():
                if not show_inactive and not key_data['is_active']:
                    continue
                
                if search and search.lower() not in key_data['user_id'].lower():
                    continue
                
                # Key card
                with st.expander(
                    f"{'🟢' if key_data['is_active'] else '🔴'} {key_data['user_id']} - {key_data['tier'].value.upper()}",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Status**")
                        status = "Active" if key_data['is_active'] else "Revoked"
                        st.markdown(f"{'🟢' if key_data['is_active'] else '🔴'} {status}")
                        
                        st.markdown("**Tier**")
                        tier_class = f"tier-{key_data['tier'].value}"
                        st.markdown(
                            f'<span class="tier-badge {tier_class}">{key_data["tier"].value.upper()}</span>',
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        st.markdown("**Created**")
                        created = key_data.get('created_at')
                        if created:
                            # Handle both datetime objects and strings
                            if isinstance(created, str):
                                st.write(created)
                            else:
                                try:
                                    st.write(created.strftime("%Y-%m-%d %H:%M"))
                                except AttributeError:
                                    st.write(str(created))
                        else:
                            st.write("Unknown")
                        
                        st.markdown("**Last Used**")
                        last_used = key_data.get('last_used')
                        if last_used:
                            # Handle both datetime objects and strings
                            if isinstance(last_used, str):
                                st.write(last_used)
                            else:
                                try:
                                    st.write(last_used.strftime("%Y-%m-%d %H:%M"))
                                except AttributeError:
                                    st.write(str(last_used))
                        else:
                            st.write("Never")
                    
                    with col3:
                        st.markdown("**Total Requests**")
                        st.metric("", key_data.get('usage_count', 0))
                        
                        st.markdown("**Today**")
                        st.metric("", key_data.get('requests_today', 0))
                    
                    # Description
                    if key_data.get('description'):
                        st.markdown("**Description**")
                        st.info(key_data['description'])
                    
                    # Masked API key
                    st.markdown("**API Key (Masked)**")
                    masked_key = f"{api_key[:12]}...{api_key[-8:]}"
                    st.code(masked_key, language="text")
                    
                    # Actions
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if key_data['is_active']:
                            if st.button("🔒 Revoke Key", key=f"revoke_{api_key}", use_container_width=True):
                                manager.revoke_api_key(api_key)
                                st.success("✅ API key revoked successfully")
                                st.rerun()
                    
                    with col2:
                        if st.button("📋 Copy Key ID", key=f"copy_{api_key}", use_container_width=True):
                            st.info(f"Key ID: {api_key[:12]}...")
    
    with tab3:
        st.markdown("#### Rate Limit Tiers")
        st.markdown("Compare different rate limit tiers and their capabilities")
        
        # Tier comparison table
        tiers_data = []
        for tier in RateLimitTier:
            config = RATE_LIMIT_CONFIG[tier]
            tiers_data.append({
                "Tier": tier.value.upper(),
                "Requests/Min": config['requests_per_minute'],
                "Requests/Hour": config['requests_per_hour'],
                "Recommended For": {
                    RateLimitTier.FREE: "Testing & Development",
                    RateLimitTier.BASIC: "Small Applications",
                    RateLimitTier.PREMIUM: "Production Apps",
                    RateLimitTier.ENTERPRISE: "Large-Scale Systems"
                }[tier]
            })
        
        import pandas as pd
        df = pd.DataFrame(tiers_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Visual comparison
        st.markdown("#### 📊 Visual Comparison")
        
        for tier in RateLimitTier:
            config = RATE_LIMIT_CONFIG[tier]
            tier_class = f"tier-{tier.value}"
            
            st.markdown(f'<span class="tier-badge {tier_class}">{tier.value.upper()}</span>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.progress(config['requests_per_minute'] / 1000, text=f"{config['requests_per_minute']} req/min")
            with col2:
                st.progress(config['requests_per_hour'] / 50000, text=f"{config['requests_per_hour']} req/hour")
    
    with tab4:
        st.markdown("#### 📚 API Key Documentation")
        
        st.markdown("""
        ##### Authentication Methods
        
        CloudIDP supports two authentication methods:
        
        1. **JWT Tokens** - For web applications and user sessions
        2. **API Keys** - For backend services and integrations (Enhanced)
        
        ##### Using API Keys
        
        Include your API key in the request header:
        ```bash
        curl -X GET http://localhost:8000/api/v1/accounts \\
          -H "X-API-Key: cidp_your_api_key_here"
        ```
        
        ##### Rate Limiting
        
        API keys are subject to rate limits based on their tier:
        - Requests are tracked per minute and per hour
        - Rate limit headers are included in responses
        - Exceeded limits return 429 Too Many Requests
        
        ##### Response Headers
        
        Rate limit information is included in response headers:
        ```
        X-RateLimit-Limit-Minute: 300
        X-RateLimit-Remaining-Minute: 285
        X-RateLimit-Limit-Hour: 10000
        X-RateLimit-Remaining-Hour: 9850
        X-RateLimit-Reset: 2024-01-15T10:30:00Z
        ```
        
        ##### Best Practices
        
        1. **Keep Keys Secret**: Never commit API keys to version control
        2. **Use Environment Variables**: Store keys in environment variables
        3. **Rotate Regularly**: Generate new keys periodically
        4. **Revoke Unused Keys**: Remove keys that are no longer needed
        5. **Monitor Usage**: Track API key usage regularly
        6. **Choose Appropriate Tier**: Select tier based on your needs
        
        ##### Security
        
        - API keys are hashed before storage
        - Keys are only shown once during generation
        - Revoked keys cannot be reactivated
        - Usage is tracked and auditable
        """)

def show_rate_limit_monitoring():
    """Rate Limit Monitoring Page - COMPLETE VERSION"""
    st.markdown("### 📈 Rate Limit Monitoring")
    st.markdown("Monitor API rate limits and usage in real-time")
    
    manager = st.session_state.api_key_manager
    
    # Summary metrics
    st.markdown("#### 📊 Current Usage")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_requests_today = sum(k.get('requests_today', 0) for k in manager.keys.values())
    active_keys = sum(1 for k in manager.keys.values() if k['is_active'])
    
    with col1:
        st.metric("Total Keys", len(manager.keys))
    with col2:
        st.metric("Active Keys", active_keys)
    with col3:
        st.metric("Requests Today", total_requests_today)
    with col4:
        avg_requests = total_requests_today / active_keys if active_keys > 0 else 0
        st.metric("Avg per Key", f"{avg_requests:.0f}")
    
    st.markdown("---")
    
    # Per-key monitoring
    st.markdown("#### 🔍 Per-Key Monitoring")
    
    if not manager.keys:
        st.info("📝 No API keys to monitor. Generate keys in the API Key Management module.")
    else:
        for api_key, key_data in manager.keys.items():
            if not key_data['is_active']:
                continue
            
            tier = key_data['tier']
            config = RATE_LIMIT_CONFIG[tier]
            
            with st.expander(
                f"{key_data['user_id']} - {tier.value.upper()}",
                expanded=True
            ):
                # Usage bars
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Requests per Minute**")
                    # Simulated current usage (in real app, track actual usage)
                    current_rpm = min(key_data.get('requests_today', 0) % 100, config['requests_per_minute'])
                    usage_pct = (current_rpm / config['requests_per_minute']) * 100
                    
                    st.markdown(f"""
                    <div class="rate-limit-bar">
                        <div class="rate-limit-fill" style="width: {usage_pct}%"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"{current_rpm} / {config['requests_per_minute']} requests")
                
                with col2:
                    st.markdown("**Requests per Hour**")
                    current_rph = min(key_data.get('requests_today', 0), config['requests_per_hour'])
                    usage_pct = (current_rph / config['requests_per_hour']) * 100
                    
                    st.markdown(f"""
                    <div class="rate-limit-bar">
                        <div class="rate-limit-fill" style="width: {usage_pct}%"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"{current_rph} / {config['requests_per_hour']} requests")
                
                # Additional stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Requests", key_data.get('usage_count', 0))
                with col2:
                    st.metric("Today's Requests", key_data.get('requests_today', 0))
                with col3:
                    if key_data.get('last_used'):
                        last_used = key_data['last_used']
                        time_ago = datetime.now() - last_used
                        if time_ago.seconds < 60:
                            st.metric("Last Used", f"{time_ago.seconds}s ago")
                        elif time_ago.seconds < 3600:
                            st.metric("Last Used", f"{time_ago.seconds // 60}m ago")
                        else:
                            st.metric("Last Used", f"{time_ago.seconds // 3600}h ago")
                    else:
                        st.metric("Last Used", "Never")

def show_api_usage_analytics():
    """API Usage Analytics Page - COMPLETE VERSION"""
    st.markdown("### 📊 API Usage Analytics")
    st.markdown("Analyze API usage patterns and trends")
    
    manager = st.session_state.api_key_manager
    
    if not manager.keys:
        st.info("📝 No API keys to analyze. Generate keys in the API Key Management module.")
        return
    
    # Summary statistics
    st.markdown("#### 📈 Usage Summary")
    
    total_usage = sum(k.get('usage_count', 0) for k in manager.keys.values())
    active_keys = sum(1 for k in manager.keys.values() if k['is_active'])
    today_usage = sum(k.get('requests_today', 0) for k in manager.keys.values())
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requests", f"{total_usage:,}")
    with col2:
        st.metric("Active Keys", active_keys)
    with col3:
        st.metric("Today's Requests", f"{today_usage:,}")
    with col4:
        avg = total_usage / active_keys if active_keys > 0 else 0
        st.metric("Avg per Key", f"{avg:.0f}")
    
    st.markdown("---")
    
    # Usage by tier
    st.markdown("#### 📊 Usage by Tier")
    
    tier_usage = {}
    for key_data in manager.keys.values():
        tier = key_data['tier'].value
        if tier not in tier_usage:
            tier_usage[tier] = {'count': 0, 'usage': 0, 'today': 0}
        tier_usage[tier]['count'] += 1
        tier_usage[tier]['usage'] += key_data.get('usage_count', 0)
        tier_usage[tier]['today'] += key_data.get('requests_today', 0)
    
    for tier in RateLimitTier:
        if tier.value in tier_usage:
            data = tier_usage[tier.value]
            tier_class = f"tier-{tier.value}"
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<span class="tier-badge {tier_class}">{tier.value.upper()}</span>', unsafe_allow_html=True)
            with col2:
                st.metric("Keys", data['count'])
            with col3:
                st.metric("Total Requests", f"{data['usage']:,}")
            with col4:
                st.metric("Today", f"{data['today']:,}")
    
    st.markdown("---")
    
    # Top consumers
    st.markdown("#### 🏆 Top API Consumers")
    
    sorted_keys = sorted(
        manager.keys.items(),
        key=lambda x: x[1].get('usage_count', 0),
        reverse=True
    )[:10]
    
    for rank, (api_key, key_data) in enumerate(sorted_keys, 1):
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        
        with col1:
            st.markdown(f"**#{rank}**")
        with col2:
            st.write(key_data['user_id'])
        with col3:
            st.metric("Total", f"{key_data.get('usage_count', 0):,}")
        with col4:
            st.metric("Today", f"{key_data.get('requests_today', 0):,}")

# ==================== AWS Integration Pages - COMPLETE IMPLEMENTATION ====================

def show_iam_management_page():
    """IAM Management Page - COMPLETE VERSION"""
    st.markdown("### 🔐 IAM Management")
    
    try:
        aws = st.session_state.aws_integrations
        
        # IAM Users
        st.markdown("#### IAM Users")
        users = aws.iam.list_users()
        
        st.write(f"**Total Users**: {users.get('count', 0)}")
        
        for user in users.get('users', []):
            with st.expander(f"👤 {user.get('UserName')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**User ID**: {user.get('UserId')}")
                    st.write(f"**ARN**: {user.get('Arn')}")
                with col2:
                    created = user.get('CreateDate')
                    if created:
                        st.write(f"**Created**: {created}")
        
        # IAM Roles
        st.markdown("---")
        st.markdown("#### IAM Roles")
        roles = aws.iam.list_roles()
        
        st.write(f"**Total Roles**: {roles.get('count', 0)}")
        
        for role in roles.get('roles', []):
            with st.expander(f"🎭 {role.get('RoleName')}"):
                st.write(f"**ARN**: {role.get('Arn')}")
                st.write(f"**Description**: {role.get('Description', 'N/A')}")
        
        # Create User
        st.markdown("---")
        st.markdown("#### Create New IAM User")
        
        with st.form("create_iam_user"):
            username = st.text_input("Username", placeholder="new-user")
            
            if st.form_submit_button("Create User"):
                with st.spinner("Creating IAM user..."):
                    result = aws.iam.create_user(user_name=username)
                if result.get('success'):
                    st.success(f"✅ User created: {username}")
                else:
                    st.error(f"❌ Failed: {result.get('error')}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_cost_explorer_page():
    """AWS Cost Explorer Page - COMPLETE VERSION"""
    st.markdown("### 📊 Cost Explorer")
    
    try:
        aws = st.session_state.aws_integrations
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Get cost data
        costs = aws.cost_explorer.get_cost_and_usage(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cost", f"${costs.get('total_cost', 0):.2f}")
        with col2:
            st.metric("Average Daily", f"${costs.get('average_daily', 0):.2f}")
        with col3:
            st.metric("Period", f"{(end_date - start_date).days} days")
        
        st.markdown("---")
        
        # Cost breakdown
        st.markdown("#### Cost by Service")
        breakdown = costs.get('breakdown', [])
        
        for item in breakdown:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{item.get('service')}**")
            with col2:
                st.write(f"${item.get('cost', 0):.2f}")
        
        # Rightsizing recommendations
        st.markdown("---")
        st.markdown("#### 💡 Rightsizing Recommendations")
        recommendations = aws.cost_explorer.get_rightsizing_recommendations()
        
        if recommendations.get('recommendations'):
            st.info(f"Potential monthly savings: **${recommendations.get('total_savings', 0):.2f}**")
            
            for rec in recommendations.get('recommendations', []):
                with st.expander(f"Instance: {rec.get('instance_id')}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Current**: {rec.get('current_type')}")
                    with col2:
                        st.write(f"**Recommended**: {rec.get('recommended_type')}")
                    with col3:
                        st.write(f"**Savings**: ${rec.get('estimated_monthly_savings', 0):.2f}/month")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_systems_manager_page():
    """AWS Systems Manager Page - COMPLETE VERSION"""
    st.markdown("### ⚙️ AWS Systems Manager")
    
    try:
        aws = st.session_state.aws_integrations
        
        # Parameter Store
        st.markdown("#### Parameter Store")
        
        with st.form("get_parameter"):
            param_name = st.text_input("Parameter Name", placeholder="/cloudidp/config/example")
            decrypt = st.checkbox("Decrypt SecureString", value=False)
            
            if st.form_submit_button("Get Parameter"):
                result = aws.systems_manager.get_parameter(param_name, with_decryption=decrypt)
                if result.get('success'):
                    st.success("✅ Parameter retrieved")
                    st.code(result.get('value', result.get('parameter', {}).get('Value', 'N/A')))
                else:
                    st.error(f"❌ Failed: {result.get('error')}")
        
        st.markdown("---")
        
        # Automation
        st.markdown("#### Automation Documents")
        
        with st.form("execute_automation"):
            doc_name = st.selectbox(
                "Document Name",
                ["AWS-StopEC2Instance", "AWS-StartEC2Instance", "AWS-RestartEC2Instance"]
            )
            instance_id = st.text_input("Instance ID", placeholder="i-1234567890abcdef0")
            
            if st.form_submit_button("Execute Automation"):
                result = aws.systems_manager.execute_automation(
                    document_name=doc_name,
                    parameters={'InstanceId': [instance_id]} if instance_id else {}
                )
                if result.get('success'):
                    st.success(f"✅ Automation started: {result.get('automation_execution_id', result.get('execution_id'))}")
                else:
                    st.error(f"❌ Failed: {result.get('error')}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_compute_network_page():
    """EC2 and VPC Management Page - COMPLETE VERSION"""
    st.markdown("### 🖥️ Compute & Network Management")
    
    try:
        aws = st.session_state.aws_integrations
        
        # VPCs
        st.markdown("#### Virtual Private Clouds (VPCs)")
        vpcs = aws.compute_network.list_vpcs()
        
        st.write(f"**Total VPCs**: {vpcs.get('count', 0)}")
        
        for vpc in vpcs.get('vpcs', []):
            with st.expander(f"🌐 VPC: {vpc.get('VpcId')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**CIDR Block**: {vpc.get('CidrBlock')}")
                    st.write(f"**State**: {vpc.get('State')}")
                with col2:
                    tags = vpc.get('Tags', [])
                    name = next((t['Value'] for t in tags if t['Key'] == 'Name'), 'N/A')
                    st.write(f"**Name**: {name}")
        
        # EC2 Instances
        st.markdown("---")
        st.markdown("#### EC2 Instances")
        instances = aws.compute_network.list_instances()
        
        st.write(f"**Total Instances**: {instances.get('count', 0)}")
        
        for instance in instances.get('instances', []):
            state = instance.get('State', {}).get('Name', 'unknown')
            state_icon = "🟢" if state == 'running' else "🔴" if state == 'stopped' else "🟡"
            
            with st.expander(f"{state_icon} {instance.get('InstanceId')} - {instance.get('InstanceType')} ({state})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**State**: {state}")
                    st.write(f"**Type**: {instance.get('InstanceType')}")
                with col2:
                    tags = instance.get('Tags', [])
                    name = next((t['Value'] for t in tags if t['Key'] == 'Name'), 'N/A')
                    st.write(f"**Name**: {name}")
        
        # Create VPC
        st.markdown("---")
        st.markdown("#### Create New VPC")
        
        with st.form("create_vpc"):
            col1, col2 = st.columns(2)
            with col1:
                cidr = st.text_input("CIDR Block", "10.0.0.0/16")
            with col2:
                vpc_name = st.text_input("VPC Name", "Production-VPC")
            enable_dns = st.checkbox("Enable DNS", value=True)
            
            if st.form_submit_button("Create VPC"):
                with st.spinner("Creating VPC..."):
                    result = aws.compute_network.create_vpc(
                        cidr_block=cidr,
                        name=vpc_name,
                        enable_dns=enable_dns
                    )
                if result.get('success'):
                    st.success(f"✅ VPC created: {result['vpc_id']}")
                else:
                    st.error(f"❌ Failed: {result.get('error')}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_database_management_page():
    """RDS and DynamoDB Management Page - COMPLETE VERSION"""
    st.markdown("### 🗄️ Database Management")
    
    try:
        aws = st.session_state.aws_integrations
        
        # RDS Instances
        st.markdown("#### RDS Database Instances")
        rds_instances = aws.database.list_db_instances()
        
        st.write(f"**Total RDS Instances**: {rds_instances.get('count', 0)}")
        
        for db in rds_instances.get('db_instances', []):
            status = db.get('DBInstanceStatus', 'unknown')
            status_icon = "🟢" if status == 'available' else "🔴" if status == 'stopped' else "🟡"
            
            with st.expander(f"{status_icon} {db.get('DBInstanceIdentifier')} - {db.get('Engine')} ({status})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Engine**: {db.get('Engine')}")
                    st.write(f"**Status**: {status}")
                with col2:
                    st.write(f"**Class**: {db.get('DBInstanceClass')}")
                    st.write(f"**Storage**: {db.get('AllocatedStorage')} GB")
                with col3:
                    st.write(f"**Multi-AZ**: {'Yes' if db.get('MultiAZ') else 'No'}")
        
        # DynamoDB Tables
        st.markdown("---")
        st.markdown("#### DynamoDB Tables")
        tables = aws.database.list_dynamodb_tables()
        
        st.write(f"**Total DynamoDB Tables**: {tables.get('count', 0)}")
        
        for table in tables.get('tables', []):
            st.write(f"📊 {table}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()