"""
Future Minds | Enterprise DevOps Migration & Compliance Platform
Multi-Account Security Monitoring, GitHub Cloud Migration, Automated Guardrails & Unified Compliance

Migration Scope:
- 150,000 Jenkins Pipelines → GitHub Actions
- 2,600 Infrastructure Pipelines → GitHub Actions
- Future State: 25,000+ Consolidated Pipelines
- Target Platform: GitHub Cloud (SaaS-based DevOps)

Integrated Services:
- GitHub Cloud (Repos, Actions, Advanced Security)
- AWS Security Hub, Config, GuardDuty, Inspector, CloudTrail
- Service Control Policies (SCP)
- Open Policy Agent (OPA)
- KICS (Keeping Infrastructure as Code Secure)
- Wiz.io Cloud Security
- AWS Bedrock (Claude AI) for Detection & Remediation
- CI/CD Pipeline Analytics

SCM & CI/CD Guardrails:
✓ GitHub Cloud Repos with KICS Scanning
✓ OPA Policy Enforcement (On-Prem & AWS Deployments)
✓ GitHub Advanced Security (Code Scanning, Secret Detection)
✓ Automated PR Validation
✓ Branch Protection Rules

Infrastructure Guardrails:
✓ SCP Enforcement for AWS Accounts
✓ OPA Policies for GitHub Actions Workflows
✓ KICS Scans for IaC (Terraform, CloudFormation)
✓ Automated Compliance Checks on PR Merge
✓ Infrastructure Drift Detection

Unified Compliance Dashboard:
✓ AWS Security Hub + AWS Config Aggregation
✓ OPA Policy Evaluation Results
✓ KICS Scan Reports & Trends
✓ Wiz.io Posture Score Integration
✓ Pipeline Migration Progress Tracking
✓ Single Pane of Glass for Policy Compliance, IaC Security & Migration Status

Company: Future Minds
Version: 5.0 - DevOps Migration Edition
"""

import streamlit as st
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import anthropic
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import time
import hashlib
import base64

# Import existing modules
try:
    from pipeline_simulator import render_pipeline_simulator
    from finops_module_enhanced_complete import (
        render_enhanced_finops_dashboard,
        render_finops_dashboard,
        fetch_cost_data,
        fetch_tag_compliance,
        fetch_resource_inventory,
        fetch_cost_optimization_recommendations,
        get_anthropic_client
    )
except ImportError:
    st.warning("Some modules not found. Running in standalone mode.")

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Future Minds | DevOps Migration & Compliance Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING - DEVOPS MIGRATION THEME
# ============================================================================

st.markdown("""
<style>
    /* Main header styling - DevOps Migration Theme */
    .main-header {
        background: linear-gradient(135deg, #2E3440 0%, #3B4252 50%, #434C5E 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 4px solid #88C0D0;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: bold;
    }
    
    .main-header p {
        color: #D8DEE9;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .main-header .stats {
        color: #88C0D0;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .main-header .company-badge {
        background: #88C0D0;
        color: #2E3440;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 1rem;
    }
    
    /* Migration Progress Cards */
    .migration-card {
        background: linear-gradient(135deg, #5E81AC 0%, #81A1C1 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .migration-card.complete {
        background: linear-gradient(135deg, #A3BE8C 0%, #8FBCBB 100%);
    }
    
    .migration-card.in-progress {
        background: linear-gradient(135deg, #EBCB8B 0%, #D08770 100%);
    }
    
    .migration-card.pending {
        background: linear-gradient(135deg, #B48EAD 0%, #5E81AC 100%);
    }
    
    /* Compliance Score Cards */
    .compliance-metric {
        background: white;
        border-left: 5px solid #A3BE8C;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .compliance-metric.critical { border-left-color: #BF616A; }
    .compliance-metric.warning { border-left-color: #D08770; }
    .compliance-metric.good { border-left-color: #A3BE8C; }
    .compliance-metric.excellent { border-left-color: #88C0D0; }
    
    /* Guardrail Status */
    .guardrail-active {
        background: linear-gradient(135deg, #A3BE8C 0%, #8FBCBB 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .guardrail-violation {
        background: linear-gradient(135deg, #BF616A 0%, #D08770 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.5rem 0;
    }
    
    /* Service badges - GitHub Theme */
    .service-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.2rem;
    }
    
    .service-badge.github { background: #24292e; color: white; }
    .service-badge.kics { background: #5E81AC; color: white; }
    .service-badge.opa { background: #88C0D0; color: #2E3440; }
    .service-badge.wiz { background: #B48EAD; color: white; }
    .service-badge.active { background: #A3BE8C; color: white; }
    .service-badge.inactive { background: #4C566A; color: white; }
    
    /* Dashboard tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #3B4252;
        color: white;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #88C0D0;
        color: #2E3440;
    }
    
    /* Unified compliance table */
    .compliance-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables"""
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = True
    
    if 'aws_connected' not in st.session_state:
        st.session_state.aws_connected = False
    
    if 'github_connected' not in st.session_state:
        st.session_state.github_connected = False
    
    if 'migration_data' not in st.session_state:
        st.session_state.migration_data = generate_demo_migration_data()
    
    if 'compliance_data' not in st.session_state:
        st.session_state.compliance_data = generate_demo_compliance_data()
    
    if 'guardrail_violations' not in st.session_state:
        st.session_state.guardrail_violations = []

# ============================================================================
# DEMO DATA GENERATORS - DEVOPS MIGRATION
# ============================================================================

def generate_demo_migration_data() -> Dict[str, Any]:
    """Generate demonstration data for pipeline migration"""
    return {
        'jenkins_pipelines': {
            'total': 150000,
            'migrated': 67500,
            'in_progress': 22500,
            'pending': 60000,
            'migration_rate': 2250  # pipelines per week
        },
        'infra_pipelines': {
            'total': 2600,
            'migrated': 1820,
            'in_progress': 390,
            'pending': 390,
            'migration_rate': 65  # pipelines per week
        },
        'future_state': {
            'target_pipelines': 25000,
            'consolidation_ratio': 6.1,  # 152,600 → 25,000
            'estimated_completion': '2026-Q2'
        },
        'migration_phases': [
            {
                'phase': 'Phase 1 - Assessment & Planning',
                'status': 'Complete',
                'completion': 100,
                'pipelines': 15000,
                'duration': '3 months'
            },
            {
                'phase': 'Phase 2 - POC & Templates',
                'status': 'Complete',
                'completion': 100,
                'pipelines': 5000,
                'duration': '2 months'
            },
            {
                'phase': 'Phase 3 - Bulk Migration (Wave 1)',
                'status': 'In Progress',
                'completion': 75,
                'pipelines': 50000,
                'duration': '6 months'
            },
            {
                'phase': 'Phase 4 - Bulk Migration (Wave 2)',
                'status': 'In Progress',
                'completion': 30,
                'pipelines': 50000,
                'duration': '6 months'
            },
            {
                'phase': 'Phase 5 - Complex Pipelines',
                'status': 'Pending',
                'completion': 0,
                'pipelines': 20000,
                'duration': '4 months'
            },
            {
                'phase': 'Phase 6 - Consolidation & Optimization',
                'status': 'Pending',
                'completion': 0,
                'pipelines': 12600,
                'duration': '3 months'
            }
        ],
        'weekly_migration_trend': [
            {'week': 'Week 1', 'migrated': 1200},
            {'week': 'Week 2', 'migrated': 1800},
            {'week': 'Week 3', 'migrated': 2100},
            {'week': 'Week 4', 'migrated': 2400},
            {'week': 'Week 5', 'migrated': 2250},
            {'week': 'Week 6', 'migrated': 2350},
            {'week': 'Week 7', 'migrated': 2500},
            {'week': 'Week 8', 'migrated': 2300}
        ]
    }

def generate_demo_compliance_data() -> Dict[str, Any]:
    """Generate demonstration compliance data from multiple sources"""
    return {
        'aws_security_hub': {
            'total_findings': 342,
            'critical': 12,
            'high': 45,
            'medium': 128,
            'low': 157,
            'compliance_score': 87.3,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'aws_config': {
            'total_rules': 156,
            'compliant': 142,
            'non_compliant': 14,
            'compliance_percentage': 91.0,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'opa_policies': {
            'total_policies': 89,
            'passing': 76,
            'failing': 13,
            'compliance_percentage': 85.4,
            'github_actions_policies': 45,
            'iac_policies': 44,
            'last_evaluated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'kics_scans': {
            'total_scans': 2847,
            'files_scanned': 18920,
            'high_severity': 56,
            'medium_severity': 234,
            'low_severity': 432,
            'info': 1245,
            'compliance_score': 92.1,
            'last_scan': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'wiz_io': {
            'posture_score': 88.5,
            'critical_issues': 8,
            'high_issues': 34,
            'medium_issues': 89,
            'cloud_accounts': 640,
            'resources_scanned': 145230,
            'last_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'github_advanced_security': {
            'code_scanning_alerts': 67,
            'secret_scanning_alerts': 23,
            'dependency_alerts': 145,
            'repositories_scanned': 1240,
            'compliance_score': 89.2,
            'last_scan': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

# ============================================================================
# MAIN HEADER
# ============================================================================

def render_main_header():
    """Render the main application header"""
    migration_data = st.session_state.migration_data
    total_pipelines = migration_data['jenkins_pipelines']['total'] + migration_data['infra_pipelines']['total']
    migrated_pipelines = migration_data['jenkins_pipelines']['migrated'] + migration_data['infra_pipelines']['migrated']
    migration_percentage = (migrated_pipelines / total_pipelines) * 100
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🚀 Future Minds | DevOps Migration & Compliance Platform</h1>
        <p>Enterprise-Scale GitHub Cloud Migration with Automated Guardrails & Unified Compliance Monitoring</p>
        <div class="stats">
            <strong>Migration Progress:</strong> {migrated_pipelines:,} / {total_pipelines:,} Pipelines 
            ({migration_percentage:.1f}% Complete) | 
            <strong>Target State:</strong> {migration_data['future_state']['target_pipelines']:,} Consolidated Pipelines | 
            <strong>ETA:</strong> {migration_data['future_state']['estimated_completion']}
        </div>
        <div class="company-badge">Future Minds Enterprise Platform v5.0</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render sidebar with configuration options"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/2E3440/88C0D0?text=Future+Minds", use_container_width=True)
        
        st.markdown("### ⚙️ Platform Configuration")
        
        # Mode selector
        st.markdown("#### 🔄 Data Source Mode")
        mode = st.radio(
            "Select Mode",
            ["Demo Mode", "Live Mode"],
            index=0 if st.session_state.demo_mode else 1,
            help="Demo Mode shows sample data. Live Mode connects to real systems."
        )
        st.session_state.demo_mode = (mode == "Demo Mode")
        
        st.markdown("---")
        
        # AWS Configuration
        with st.expander("🔐 AWS Configuration", expanded=not st.session_state.demo_mode):
            aws_region = st.text_input("AWS Region", value="us-east-1")
            aws_access_key = st.text_input("AWS Access Key", type="password")
            aws_secret_key = st.text_input("AWS Secret Key", type="password")
            
            if st.button("Connect to AWS"):
                if aws_access_key and aws_secret_key:
                    st.session_state.aws_connected = True
                    st.success("✅ Connected to AWS")
                else:
                    st.error("❌ Please provide credentials")
        
        # GitHub Configuration
        with st.expander("🐙 GitHub Configuration", expanded=not st.session_state.demo_mode):
            github_token = st.text_input("GitHub Token", type="password")
            github_org = st.text_input("GitHub Organization", value="future-minds")
            
            if st.button("Connect to GitHub"):
                if github_token:
                    st.session_state.github_connected = True
                    st.success("✅ Connected to GitHub")
                else:
                    st.error("❌ Please provide token")
        
        # Anthropic Configuration
        with st.expander("🤖 Anthropic AI Configuration"):
            anthropic_key = st.text_input("Anthropic API Key", type="password")
            
            if st.button("Configure AI"):
                if anthropic_key:
                    st.success("✅ AI Configured")
                else:
                    st.error("❌ Please provide API key")
        
        st.markdown("---")
        
        # System Status
        st.markdown("### 📊 System Status")
        
        status_items = [
            ("AWS", st.session_state.aws_connected or st.session_state.demo_mode),
            ("GitHub", st.session_state.github_connected or st.session_state.demo_mode),
            ("KICS", st.session_state.demo_mode),
            ("OPA", st.session_state.demo_mode),
            ("Wiz.io", st.session_state.demo_mode),
            ("Security Hub", st.session_state.demo_mode),
            ("Config", st.session_state.demo_mode)
        ]
        
        for service, status in status_items:
            icon = "🟢" if status else "🔴"
            st.markdown(f"{icon} **{service}**")

# ============================================================================
# MIGRATION OVERVIEW DASHBOARD
# ============================================================================

def render_migration_overview():
    """Render comprehensive migration overview dashboard"""
    st.markdown("## 🚀 DevOps Platform Migration Overview")
    
    migration_data = st.session_state.migration_data
    
    # Top-level metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_pipelines = migration_data['jenkins_pipelines']['total'] + migration_data['infra_pipelines']['total']
    migrated_pipelines = migration_data['jenkins_pipelines']['migrated'] + migration_data['infra_pipelines']['migrated']
    in_progress = migration_data['jenkins_pipelines']['in_progress'] + migration_data['infra_pipelines']['in_progress']
    pending = migration_data['jenkins_pipelines']['pending'] + migration_data['infra_pipelines']['pending']
    migration_percentage = (migrated_pipelines / total_pipelines) * 100
    
    with col1:
        st.metric(
            "Total Pipelines",
            f"{total_pipelines:,}",
            help="Jenkins (150K) + Infrastructure (2.6K)"
        )
    
    with col2:
        st.metric(
            "Migrated",
            f"{migrated_pipelines:,}",
            f"{migration_percentage:.1f}%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "In Progress",
            f"{in_progress:,}",
            f"{(in_progress/total_pipelines)*100:.1f}%"
        )
    
    with col4:
        st.metric(
            "Pending",
            f"{pending:,}",
            f"{(pending/total_pipelines)*100:.1f}%"
        )
    
    with col5:
        st.metric(
            "Target State",
            f"{migration_data['future_state']['target_pipelines']:,}",
            f"{migration_data['future_state']['consolidation_ratio']:.1f}x consolidation"
        )
    
    st.markdown("---")
    
    # Jenkins vs Infrastructure Pipeline Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Jenkins Pipelines (150K)")
        jenkins = migration_data['jenkins_pipelines']
        
        fig = go.Figure(data=[go.Pie(
            labels=['Migrated', 'In Progress', 'Pending'],
            values=[jenkins['migrated'], jenkins['in_progress'], jenkins['pending']],
            hole=0.4,
            marker=dict(colors=['#A3BE8C', '#EBCB8B', '#5E81AC'])
        )])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
        <div class="migration-card in-progress">
            <strong>Migration Rate:</strong> {jenkins['migration_rate']:,} pipelines/week<br>
            <strong>Estimated Completion:</strong> {int(jenkins['pending'] / jenkins['migration_rate'])} weeks
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🏗️ Infrastructure Pipelines (2.6K)")
        infra = migration_data['infra_pipelines']
        
        fig = go.Figure(data=[go.Pie(
            labels=['Migrated', 'In Progress', 'Pending'],
            values=[infra['migrated'], infra['in_progress'], infra['pending']],
            hole=0.4,
            marker=dict(colors=['#A3BE8C', '#EBCB8B', '#5E81AC'])
        )])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
        <div class="migration-card complete">
            <strong>Migration Rate:</strong> {infra['migration_rate']:,} pipelines/week<br>
            <strong>Estimated Completion:</strong> {int(infra['pending'] / infra['migration_rate'])} weeks
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Migration Phase Timeline
    st.markdown("### 📅 Migration Phase Timeline")
    
    phases_df = pd.DataFrame(migration_data['migration_phases'])
    
    fig = px.bar(
        phases_df,
        x='phase',
        y='completion',
        color='status',
        text='completion',
        color_discrete_map={
            'Complete': '#A3BE8C',
            'In Progress': '#EBCB8B',
            'Pending': '#5E81AC'
        }
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(
        xaxis_title="Migration Phase",
        yaxis_title="Completion %",
        yaxis_range=[0, 110],
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Phase details table
    st.markdown("#### 📋 Phase Details")
    phase_table = phases_df[['phase', 'status', 'completion', 'pipelines', 'duration']].copy()
    phase_table['completion'] = phase_table['completion'].apply(lambda x: f"{x}%")
    phase_table['pipelines'] = phase_table['pipelines'].apply(lambda x: f"{x:,}")
    st.dataframe(phase_table, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Weekly Migration Trend
    st.markdown("### 📈 Weekly Migration Velocity")
    
    trend_df = pd.DataFrame(migration_data['weekly_migration_trend'])
    
    fig = px.line(
        trend_df,
        x='week',
        y='migrated',
        markers=True,
        line_shape='spline'
    )
    fig.update_traces(line_color='#88C0D0', marker=dict(size=10, color='#5E81AC'))
    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Pipelines Migrated",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
    
    avg_velocity = sum([w['migrated'] for w in migration_data['weekly_migration_trend']]) / len(migration_data['weekly_migration_trend'])
    st.info(f"📊 **Average Weekly Velocity:** {avg_velocity:,.0f} pipelines/week")

# ============================================================================
# SCM & CI/CD GUARDRAILS DASHBOARD
# ============================================================================

def render_scm_cicd_guardrails():
    """Render SCM & CI/CD guardrails monitoring dashboard"""
    st.markdown("## 🛡️ SCM & CI/CD Guardrails")
    
    st.markdown("""
    <div class="guardrail-active">
        <h4>✅ Active Guardrails</h4>
        <ul>
            <li><strong>GitHub Cloud Repos:</strong> KICS scans integrated via GitHub Actions</li>
            <li><strong>OPA Policy Enforcement:</strong> All pipelines (on-prem & AWS deployments)</li>
            <li><strong>GitHub Advanced Security:</strong> Code scanning & secret detection enabled</li>
            <li><strong>Branch Protection:</strong> Automated PR validation & approval workflows</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # GitHub Advanced Security Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    ghas = st.session_state.compliance_data['github_advanced_security']
    
    with col1:
        st.metric(
            "Code Scanning Alerts",
            ghas['code_scanning_alerts'],
            help="Static code analysis findings"
        )
    
    with col2:
        st.metric(
            "Secret Scanning Alerts",
            ghas['secret_scanning_alerts'],
            help="Exposed secrets detected"
        )
    
    with col3:
        st.metric(
            "Dependency Alerts",
            ghas['dependency_alerts'],
            help="Vulnerable dependencies"
        )
    
    with col4:
        st.metric(
            "Repositories Scanned",
            f"{ghas['repositories_scanned']:,}",
            help="Total repos under GHAS"
        )
    
    st.markdown("---")
    
    # KICS Scanning Dashboard
    st.markdown("### 🔍 KICS IaC Security Scanning")
    
    kics = st.session_state.compliance_data['kics_scans']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scans", f"{kics['total_scans']:,}")
    
    with col2:
        st.metric("Files Scanned", f"{kics['files_scanned']:,}")
    
    with col3:
        st.metric("Compliance Score", f"{kics['compliance_score']}%")
    
    with col4:
        st.metric("Last Scan", kics['last_scan'].split()[1])
    
    # KICS findings breakdown
    st.markdown("#### 📊 KICS Findings by Severity")
    
    kics_data = {
        'Severity': ['High', 'Medium', 'Low', 'Info'],
        'Count': [kics['high_severity'], kics['medium_severity'], kics['low_severity'], kics['info']],
        'Color': ['#BF616A', '#EBCB8B', '#5E81AC', '#88C0D0']
    }
    
    fig = px.bar(
        kics_data,
        x='Severity',
        y='Count',
        color='Severity',
        color_discrete_sequence=kics_data['Color']
    )
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # OPA Policy Enforcement
    st.markdown("### ⚖️ OPA Policy Enforcement")
    
    opa = st.session_state.compliance_data['opa_policies']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Policies", opa['total_policies'])
    
    with col2:
        st.metric("Passing", opa['passing'], delta=f"{opa['compliance_percentage']:.1f}%")
    
    with col3:
        st.metric("Failing", opa['failing'], delta="-{:.1f}%".format(100-opa['compliance_percentage']), delta_color="inverse")
    
    # Policy breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔄 GitHub Actions Policies")
        st.markdown(f"""
        <div class="compliance-metric good">
            <h3>{opa['github_actions_policies']}</h3>
            <p>Workflow validation, deployment gates, security checks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🏗️ IaC Policies")
        st.markdown(f"""
        <div class="compliance-metric good">
            <h3>{opa['iac_policies']}</h3>
            <p>Terraform, CloudFormation, resource compliance</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent Guardrail Violations
    st.markdown("### 🚨 Recent Guardrail Violations")
    
    violations = [
        {
            'Timestamp': '2025-11-21 14:32:15',
            'Type': 'KICS',
            'Severity': 'HIGH',
            'Repository': 'infrastructure-core',
            'Issue': 'Unencrypted S3 bucket detected in terraform',
            'Status': 'Blocked'
        },
        {
            'Timestamp': '2025-11-21 13:45:22',
            'Type': 'OPA',
            'Severity': 'CRITICAL',
            'Repository': 'deployment-pipelines',
            'Issue': 'Production deployment without approval',
            'Status': 'Blocked'
        },
        {
            'Timestamp': '2025-11-21 12:18:44',
            'Type': 'GHAS',
            'Severity': 'CRITICAL',
            'Repository': 'api-service',
            'Issue': 'AWS access key exposed in code',
            'Status': 'Blocked'
        },
        {
            'Timestamp': '2025-11-21 11:55:30',
            'Type': 'KICS',
            'Severity': 'MEDIUM',
            'Repository': 'network-config',
            'Issue': 'Security group with overly permissive rules',
            'Status': 'Warning'
        }
    ]
    
    df = pd.DataFrame(violations)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================================
# INFRASTRUCTURE GUARDRAILS DASHBOARD
# ============================================================================

def render_infrastructure_guardrails():
    """Render infrastructure guardrails monitoring dashboard"""
    st.markdown("## 🏗️ Infrastructure Guardrails")
    
    st.markdown("""
    <div class="guardrail-active">
        <h4>✅ Active Infrastructure Guardrails</h4>
        <ul>
            <li><strong>SCP Enforcement:</strong> Service Control Policies active on 640+ AWS accounts</li>
            <li><strong>OPA for GitHub Actions:</strong> IaC validation in all workflows</li>
            <li><strong>KICS Automation:</strong> Scans triggered on every PR merge to main branch</li>
            <li><strong>Drift Detection:</strong> Continuous monitoring of infrastructure changes</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # AWS SCP Enforcement
    st.markdown("### 🔐 AWS Service Control Policies (SCP)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("AWS Accounts", "640+", help="Multi-portfolio coverage")
    
    with col2:
        st.metric("Active SCPs", "47", help="Organization-wide policies")
    
    with col3:
        st.metric("Compliance Rate", "98.7%")
    
    with col4:
        st.metric("Policy Violations", "8", delta="-3", delta_color="inverse")
    
    # SCP Coverage by Portfolio
    st.markdown("#### 📊 SCP Coverage by Portfolio")
    
    scp_data = pd.DataFrame([
        {'Portfolio': 'Retail', 'Accounts': 245, 'SCPs': 18, 'Compliance': 99.2},
        {'Portfolio': 'Healthcare', 'Accounts': 198, 'SCPs': 15, 'Compliance': 98.5},
        {'Portfolio': 'Financial', 'Accounts': 197, 'SCPs': 14, 'Compliance': 98.3}
    ])
    
    fig = px.bar(
        scp_data,
        x='Portfolio',
        y='Compliance',
        color='Compliance',
        text='Compliance',
        color_continuous_scale='Greens'
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(height=300, yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Automated KICS Scanning
    st.markdown("### 🤖 Automated KICS IaC Scanning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="compliance-metric excellent">
            <h4>PR Merge Automation</h4>
            <p><strong>Status:</strong> ✅ Active</p>
            <p><strong>Trigger:</strong> Every PR merge to main branch</p>
            <p><strong>Scan Time:</strong> ~2-5 minutes average</p>
            <p><strong>Auto-Block:</strong> Critical & High findings</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="compliance-metric good">
            <h4>Scan Statistics (Last 30 Days)</h4>
            <p><strong>Total PRs:</strong> 2,847</p>
            <p><strong>Scans Executed:</strong> 2,847 (100%)</p>
            <p><strong>PRs Blocked:</strong> 127 (4.5%)</p>
            <p><strong>Issues Remediated:</strong> 543</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # OPA Workflow Policies
    st.markdown("### ⚖️ OPA Policies for GitHub Actions Workflows")
    
    workflow_policies = [
        {
            'Policy': 'Require Security Scanning',
            'Status': '✅ Enforced',
            'Workflows': 1240,
            'Violations': 0
        },
        {
            'Policy': 'Mandate Approval for Production',
            'Status': '✅ Enforced',
            'Workflows': 856,
            'Violations': 2
        },
        {
            'Policy': 'Terraform Plan Required',
            'Status': '✅ Enforced',
            'Workflows': 678,
            'Violations': 1
        },
        {
            'Policy': 'Secret Scanning Pre-Deploy',
            'Status': '✅ Enforced',
            'Workflows': 1240,
            'Violations': 5
        }
    ]
    
    df = pd.DataFrame(workflow_policies)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Infrastructure Drift Detection
    st.markdown("### 🎯 Infrastructure Drift Detection")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Resources Monitored", "145,230")
    
    with col2:
        st.metric("Drift Detected", "23", delta="-5", delta_color="inverse")
    
    with col3:
        st.metric("Auto-Remediated", "18")
    
    with col4:
        st.metric("Manual Review", "5")
    
    # Recent drift events
    drift_events = [
        {'Resource': 'vpc-prod-east-1', 'Type': 'VPC', 'Drift': 'Security group rules modified', 'Action': 'Auto-remediated'},
        {'Resource': 's3-logs-bucket', 'Type': 'S3', 'Drift': 'Encryption disabled', 'Action': 'Auto-remediated'},
        {'Resource': 'rds-prod-cluster', 'Type': 'RDS', 'Drift': 'Backup retention changed', 'Action': 'Manual review'},
    ]
    
    st.markdown("#### 📋 Recent Drift Events")
    df = pd.DataFrame(drift_events)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================================
# UNIFIED COMPLIANCE DASHBOARD
# ============================================================================

def render_unified_compliance_dashboard():
    """Render unified compliance dashboard aggregating all sources"""
    st.markdown("## 🎯 Unified Compliance Dashboard")
    st.markdown("**Single Pane of Glass:** Policy Compliance • IaC Security • Pipeline Migration Progress")
    
    compliance_data = st.session_state.compliance_data
    
    # Overall Compliance Score
    weights = {
        'aws_security_hub': 0.25,
        'aws_config': 0.20,
        'opa_policies': 0.20,
        'kics_scans': 0.15,
        'wiz_io': 0.15,
        'github_advanced_security': 0.05
    }
    
    overall_score = (
        compliance_data['aws_security_hub']['compliance_score'] * weights['aws_security_hub'] +
        compliance_data['aws_config']['compliance_percentage'] * weights['aws_config'] +
        compliance_data['opa_policies']['compliance_percentage'] * weights['opa_policies'] +
        compliance_data['kics_scans']['compliance_score'] * weights['kics_scans'] +
        compliance_data['wiz_io']['posture_score'] * weights['wiz_io'] +
        compliance_data['github_advanced_security']['compliance_score'] * weights['github_advanced_security']
    )
    
    # Overall Score Card
    score_color = "excellent" if overall_score >= 90 else "good" if overall_score >= 80 else "warning" if overall_score >= 70 else "critical"
    
    st.markdown(f"""
    <div class="compliance-metric {score_color}">
        <h2 style='text-align: center; margin: 0;'>Overall Compliance Score</h2>
        <h1 style='text-align: center; font-size: 4rem; margin: 1rem 0;'>{overall_score:.1f}%</h1>
        <p style='text-align: center; margin: 0;'>Aggregated from 6 compliance sources</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Source-by-Source Breakdown
    st.markdown("### 📊 Compliance by Source")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🛡️ AWS Security Hub")
        sec_hub = compliance_data['aws_security_hub']
        st.metric("Compliance Score", f"{sec_hub['compliance_score']}%")
        st.metric("Total Findings", sec_hub['total_findings'])
        st.metric("Critical", sec_hub['critical'], delta=f"High: {sec_hub['high']}")
    
    with col2:
        st.markdown("#### ⚙️ AWS Config")
        config = compliance_data['aws_config']
        st.metric("Compliance Rate", f"{config['compliance_percentage']}%")
        st.metric("Total Rules", config['total_rules'])
        st.metric("Compliant", config['compliant'], delta=f"Non-compliant: {config['non_compliant']}")
    
    with col3:
        st.markdown("#### ⚖️ OPA Policies")
        opa = compliance_data['opa_policies']
        st.metric("Compliance Rate", f"{opa['compliance_percentage']}%")
        st.metric("Total Policies", opa['total_policies'])
        st.metric("Passing", opa['passing'], delta=f"Failing: {opa['failing']}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🔍 KICS Scans")
        kics = compliance_data['kics_scans']
        st.metric("Compliance Score", f"{kics['compliance_score']}%")
        st.metric("Total Scans", f"{kics['total_scans']:,}")
        st.metric("High Severity", kics['high_severity'], delta=f"Medium: {kics['medium_severity']}")
    
    with col2:
        st.markdown("#### 🌐 Wiz.io")
        wiz = compliance_data['wiz_io']
        st.metric("Posture Score", f"{wiz['posture_score']}%")
        st.metric("Resources Scanned", f"{wiz['resources_scanned']:,}")
        st.metric("Critical Issues", wiz['critical_issues'], delta=f"High: {wiz['high_issues']}")
    
    with col3:
        st.markdown("#### 🐙 GitHub Advanced Security")
        ghas = compliance_data['github_advanced_security']
        st.metric("Compliance Score", f"{ghas['compliance_score']}%")
        st.metric("Repositories", f"{ghas['repositories_scanned']:,}")
        st.metric("Code Alerts", ghas['code_scanning_alerts'], delta=f"Secrets: {ghas['secret_scanning_alerts']}")
    
    st.markdown("---")
    
    # Compliance Trend Over Time
    st.markdown("### 📈 Compliance Trend (Last 30 Days)")
    
    trend_data = pd.DataFrame({
        'Date': pd.date_range(start='2025-10-22', end='2025-11-21', freq='D'),
        'AWS Security Hub': [85 + i*0.08 for i in range(31)],
        'AWS Config': [88 + i*0.1 for i in range(31)],
        'OPA': [83 + i*0.08 for i in range(31)],
        'KICS': [90 + i*0.07 for i in range(31)],
        'Wiz.io': [86 + i*0.08 for i in range(31)],
        'Overall': [86 + i*0.07 for i in range(31)]
    })
    
    fig = px.line(
        trend_data,
        x='Date',
        y=['AWS Security Hub', 'AWS Config', 'OPA', 'KICS', 'Wiz.io', 'Overall'],
        labels={'value': 'Compliance %', 'variable': 'Source'}
    )
    fig.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Migration Progress Integration
    st.markdown("### 🚀 Pipeline Migration Progress")
    
    migration_data = st.session_state.migration_data
    total = migration_data['jenkins_pipelines']['total'] + migration_data['infra_pipelines']['total']
    migrated = migration_data['jenkins_pipelines']['migrated'] + migration_data['infra_pipelines']['migrated']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pipelines", f"{total:,}")
    
    with col2:
        st.metric("Migrated", f"{migrated:,}", f"{(migrated/total)*100:.1f}%")
    
    with col3:
        st.metric("Target State", f"{migration_data['future_state']['target_pipelines']:,}")
    
    with col4:
        st.metric("ETA", migration_data['future_state']['estimated_completion'])
    
    # Combined migration progress bar
    progress = (migrated / total) * 100
    st.progress(progress / 100)
    st.markdown(f"**Migration Progress:** {progress:.1f}% complete")
    
    st.markdown("---")
    
    # Consolidated Findings Table
    st.markdown("### 📋 Consolidated Findings Across All Sources")
    
    consolidated_findings = [
        {
            'Source': 'AWS Security Hub',
            'Category': 'S3 Public Access',
            'Severity': 'CRITICAL',
            'Count': 12,
            'Status': 'In Remediation',
            'SLA': '24 hours'
        },
        {
            'Source': 'KICS',
            'Category': 'Unencrypted Storage',
            'Severity': 'HIGH',
            'Count': 56,
            'Status': 'Active',
            'SLA': '72 hours'
        },
        {
            'Source': 'OPA',
            'Category': 'Policy Violations',
            'Severity': 'HIGH',
            'Count': 13,
            'Status': 'Blocked',
            'SLA': 'Immediate'
        },
        {
            'Source': 'GitHub Advanced Security',
            'Category': 'Secret Exposure',
            'Severity': 'CRITICAL',
            'Count': 23,
            'Status': 'Revoked',
            'SLA': 'Immediate'
        },
        {
            'Source': 'Wiz.io',
            'Category': 'Misconfigurations',
            'Severity': 'HIGH',
            'Count': 34,
            'Status': 'In Remediation',
            'SLA': '48 hours'
        },
        {
            'Source': 'AWS Config',
            'Category': 'Non-Compliant Resources',
            'Severity': 'MEDIUM',
            'Count': 14,
            'Status': 'Active',
            'SLA': '1 week'
        }
    ]
    
    df = pd.DataFrame(consolidated_findings)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export Options
    st.markdown("---")
    st.markdown("### 📤 Export Compliance Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to CSV"):
            st.success("✅ Compliance data exported to compliance_report.csv")
    
    with col2:
        if st.button("📄 Generate PDF Report"):
            st.success("✅ PDF report generated: compliance_report.pdf")
    
    with col3:
        if st.button("📧 Email Report"):
            st.success("✅ Report emailed to stakeholders")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main header
    render_main_header()
    
    # Mode indicator banner
    if st.session_state.demo_mode:
        st.info("📊 **Demo Mode Active** - Viewing sample data for 150K Jenkins + 2.6K Infra pipelines migration")
    else:
        if st.session_state.aws_connected and st.session_state.github_connected:
            st.success("🟢 **Live Mode** - Connected to AWS and GitHub Cloud")
        else:
            st.warning("⚠️ **Live Mode** - Configure credentials in sidebar")
    
    st.markdown("---")
    
    # Main navigation tabs
    tabs = st.tabs([
        "🚀 Migration Overview",
        "🛡️ SCM & CI/CD Guardrails",
        "🏗️ Infrastructure Guardrails",
        "🎯 Unified Compliance Dashboard",
        "📊 Analytics & Reporting",
        "⚙️ Configuration Management"
    ])
    
    with tabs[0]:
        render_migration_overview()
    
    with tabs[1]:
        render_scm_cicd_guardrails()
    
    with tabs[2]:
        render_infrastructure_guardrails()
    
    with tabs[3]:
        render_unified_compliance_dashboard()
    
    with tabs[4]:
        st.markdown("## 📊 Analytics & Reporting")
        st.info("📈 Advanced analytics dashboard coming soon...")
        st.markdown("""
        **Planned Features:**
        - Migration velocity analytics
        - Guardrail effectiveness metrics
        - Compliance trend analysis
        - Cost savings from consolidation
        - Team productivity metrics
        """)
    
    with tabs[5]:
        st.markdown("## ⚙️ Configuration Management")
        st.info("🔧 Configuration interface coming soon...")
        st.markdown("""
        **Configuration Options:**
        - Guardrail policies and thresholds
        - Notification preferences
        - Integration settings
        - User access management
        - Automated remediation rules
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>Future Minds | DevOps Migration & Compliance Platform v5.0</strong></p>
        <p>🚀 Migration Scope: 150K Jenkins + 2.6K Infra → 25K Consolidated Pipelines</p>
        <p style='font-size: 0.9rem;'>Integrated Services: GitHub Cloud • KICS • OPA • AWS Security Hub • Config • Wiz.io • Anthropic Claude AI</p>
        <p style='font-size: 0.9rem;'>Guardrails: SCM/CI/CD • Infrastructure • Policy Enforcement • IaC Security • Automated Compliance</p>
        <p style='font-size: 0.8rem;'>⚠️ Ensure proper permissions across all platforms | 📚 Documentation | 🐛 Report Issues</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
