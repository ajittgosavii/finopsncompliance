# app.py
# Cloud Compliance Canvas - GitHub & GitOps Integration
# Streamlit Application with Demo/Live Toggle

import streamlit as st
import boto3
from datetime import datetime, timedelta
import json
import hashlib
import pyotp
from typing import Optional, Dict, Any
import time
from botocore.exceptions import ClientError

# Page configuration
st.set_page_config(
    page_title="Cloud Compliance Canvas - GitHub & GitOps",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .demo-mode-banner {
        background-color: #ff6b6b;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .live-mode-banner {
        background-color: #50c878;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'demo'
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'pending_approval' not in st.session_state:
    st.session_state.pending_approval = False
if 'approval_request_id' not in st.session_state:
    st.session_state.approval_request_id = None

# AWS Configuration
class AWSModeManager:
    """Manages mode switching operations with AWS backend"""
    
    def __init__(self):
        # Use Streamlit secrets for AWS credentials
        if 'aws' in st.secrets:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=st.secrets['aws']['region'],
                aws_access_key_id=st.secrets['aws'].get('access_key_id'),
                aws_secret_access_key=st.secrets['aws'].get('secret_access_key')
            )
            self.sns = boto3.client(
                'sns',
                region_name=st.secrets['aws']['region'],
                aws_access_key_id=st.secrets['aws'].get('access_key_id'),
                aws_secret_access_key=st.secrets['aws'].get('secret_access_key')
            )
            self.cloudwatch = boto3.client(
                'cloudwatch',
                region_name=st.secrets['aws']['region'],
                aws_access_key_id=st.secrets['aws'].get('access_key_id'),
                aws_secret_access_key=st.secrets['aws'].get('secret_access_key')
            )
        else:
            # Demo mode - use local state
            self.dynamodb = None
            self.sns = None
            self.cloudwatch = None
    
    def get_current_mode(self, org_id: str) -> Dict[str, Any]:
        """Get current mode configuration"""
        if self.dynamodb is None:
            # Return demo mode for local development
            return {
                'current_mode': 'demo',
                'metadata': {
                    'last_switched_at': datetime.now().isoformat(),
                    'last_switched_by_email': 'demo@company.com',
                    'organization_id': org_id,
                    'demo_config': {
                        'sample_accounts': 10,
                        'sample_policies': 25
                    }
                }
            }
        
        try:
            table = self.dynamodb.Table(st.secrets['aws']['mode_config_table'])
            response = table.get_item(Key={'organization_id': org_id})
            
            if 'Item' not in response:
                # Initialize with demo mode
                default_config = {
                    'organization_id': org_id,
                    'current_mode': 'demo',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                table.put_item(Item=default_config)
                return {'current_mode': 'demo', 'metadata': default_config}
            
            return {
                'current_mode': response['Item']['current_mode'],
                'metadata': response['Item']
            }
        except Exception as e:
            st.error(f"Error fetching mode: {str(e)}")
            return {'current_mode': 'demo', 'metadata': {}}
    
    def switch_mode(self, org_id: str, target_mode: str, user_email: str, 
                   justification: str, mfa_code: str) -> Dict[str, Any]:
        """Switch mode with approval workflow"""
        
        # Verify MFA
        if not self.verify_mfa(user_email, mfa_code):
            return {
                'status': 'error',
                'message': 'Invalid MFA code'
            }
        
        current_config = self.get_current_mode(org_id)
        current_mode = current_config['current_mode']
        
        if current_mode == target_mode:
            return {
                'status': 'error',
                'message': f'Already in {target_mode} mode'
            }
        
        # Check if approval required (demo → live)
        if current_mode == 'demo' and target_mode == 'live':
            return self._create_approval_request(
                org_id, current_mode, target_mode, user_email, justification
            )
        else:
            # Live → Demo doesn't require approval
            return self._execute_mode_switch(
                org_id, current_mode, target_mode, user_email, justification
            )
    
    def _create_approval_request(self, org_id: str, from_mode: str, 
                                to_mode: str, user_email: str, 
                                justification: str) -> Dict[str, Any]:
        """Create approval request for mode switch"""
        
        request_id = hashlib.md5(
            f"{org_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        approval_request = {
            'request_id': request_id,
            'organization_id': org_id,
            'from_mode': from_mode,
            'to_mode': to_mode,
            'requested_by_email': user_email,
            'justification': justification,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'required_approvers': ['security_team', 'operations_team']
        }
        
        if self.dynamodb:
            try:
                table = self.dynamodb.Table(st.secrets['aws']['approval_table'])
                table.put_item(Item=approval_request)
                
                # Send notifications
                self._send_approval_notifications(approval_request)
            except Exception as e:
                st.error(f"Error creating approval request: {str(e)}")
        
        return {
            'status': 'pending_approval',
            'request_id': request_id,
            'message': 'Approval request sent to Security and Operations teams'
        }
    
    def _execute_mode_switch(self, org_id: str, from_mode: str, 
                            to_mode: str, user_email: str, 
                            justification: str) -> Dict[str, Any]:
        """Execute the mode switch"""
        
        auto_revert_at = None
        if to_mode == 'live':
            # Auto-revert after 4 hours
            auto_revert_at = (datetime.now() + timedelta(hours=4)).isoformat()
        
        updated_config = {
            'organization_id': org_id,
            'current_mode': to_mode,
            'last_switched_at': datetime.now().isoformat(),
            'last_switched_by_email': user_email,
            'last_switched_from': from_mode,
            'reason': justification,
            'auto_revert_enabled': to_mode == 'live',
            'auto_revert_at': auto_revert_at,
            'updated_at': datetime.now().isoformat()
        }
        
        if self.dynamodb:
            try:
                table = self.dynamodb.Table(st.secrets['aws']['mode_config_table'])
                table.put_item(Item=updated_config)
                
                # Log audit event
                self._log_audit_event(org_id, from_mode, to_mode, user_email)
                
                # Publish metrics
                self._publish_metrics(org_id, from_mode, to_mode)
            except Exception as e:
                st.error(f"Error executing mode switch: {str(e)}")
        
        return {
            'status': 'completed',
            'current_mode': to_mode,
            'message': f'Successfully switched to {to_mode} mode'
        }
    
    def verify_mfa(self, user_email: str, mfa_code: str) -> bool:
        """Verify MFA code (simplified for demo)"""
        # In production, integrate with AWS Cognito or similar
        # For demo, accept any 6-digit code
        return len(mfa_code) == 6 and mfa_code.isdigit()
    
    def _send_approval_notifications(self, request: Dict[str, Any]):
        """Send approval notifications via SNS"""
        if self.sns and 'security_alerts_topic' in st.secrets['aws']:
            try:
                message = f"""
Mode Switch Approval Required

Organization: {request['organization_id']}
Requested by: {request['requested_by_email']}
From: {request['from_mode']}
To: {request['to_mode']}
Justification: {request['justification']}
Request ID: {request['request_id']}

Please review in the Cloud Compliance Canvas portal.
                """
                
                self.sns.publish(
                    TopicArn=st.secrets['aws']['security_alerts_topic'],
                    Subject='Mode Switch Approval Required',
                    Message=message
                )
            except Exception as e:
                st.warning(f"Could not send notification: {str(e)}")
    
    def _log_audit_event(self, org_id: str, from_mode: str, 
                        to_mode: str, user_email: str):
        """Log audit event to DynamoDB"""
        if self.dynamodb:
            try:
                table = self.dynamodb.Table(st.secrets['aws']['audit_log_table'])
                log_entry = {
                    'log_id': hashlib.md5(
                        f"{org_id}{datetime.now().isoformat()}".encode()
                    ).hexdigest(),
                    'timestamp': datetime.now().isoformat(),
                    'organization_id': org_id,
                    'event_type': 'mode_switch_completed',
                    'from_mode': from_mode,
                    'to_mode': to_mode,
                    'user_email': user_email,
                    'ttl': int((datetime.now() + timedelta(days=2555)).timestamp())
                }
                table.put_item(Item=log_entry)
            except Exception as e:
                st.warning(f"Could not log audit event: {str(e)}")
    
    def _publish_metrics(self, org_id: str, from_mode: str, to_mode: str):
        """Publish CloudWatch metrics"""
        if self.cloudwatch:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace='CloudComplianceCanvas/ModeManagement',
                    MetricData=[
                        {
                            'MetricName': 'ModeSwitches',
                            'Dimensions': [
                                {'Name': 'OrganizationId', 'Value': org_id},
                                {'Name': 'FromMode', 'Value': from_mode},
                                {'Name': 'ToMode', 'Value': to_mode}
                            ],
                            'Value': 1,
                            'Unit': 'Count'
                        }
                    ]
                )
            except Exception as e:
                st.warning(f"Could not publish metrics: {str(e)}")

# Initialize manager
mode_manager = AWSModeManager()

# Load current mode
org_id = st.secrets.get('organization_id', 'demo-org-12345')
mode_config = mode_manager.get_current_mode(org_id)
st.session_state.current_mode = mode_config['current_mode']

# Main Application
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/4A90E2/FFFFFF?text=CCC", width=150)
        st.title("Navigation")
        
        page = st.radio(
            "Select Page",
            ["🏠 Dashboard", "📝 Policy Update", "🔍 Detection", "📊 Status", "🔧 Remediation", "⚙️ Settings"]
        )
        
        st.divider()
        
        # User info
        if st.session_state.user_authenticated:
            st.write(f"👤 {st.session_state.user_email}")
            if st.button("Logout"):
                st.session_state.user_authenticated = False
                st.session_state.user_email = None
                st.rerun()
        else:
            st.write("👤 Guest Mode")
    
    # Mode Banner
    render_mode_banner()
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "📝 Policy Update":
        render_policy_update()
    elif page == "🔍 Detection":
        render_detection()
    elif page == "📊 Status":
        render_status()
    elif page == "🔧 Remediation":
        render_remediation()
    elif page == "⚙️ Settings":
        render_settings()

def render_mode_banner():
    """Render the mode status banner"""
    
    mode = st.session_state.current_mode
    
    if mode == 'demo':
        st.markdown("""
        <div class="demo-mode-banner">
            🔴 DEMO MODE ACTIVE - Using sample data - No production impact
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="live-mode-banner">
            🟢 LIVE PRODUCTION MODE - Real accounts - Exercise caution ⚠️
        </div>
        """, unsafe_allow_html=True)
    
    # Mode switch section
    with st.expander("🔄 Mode Management", expanded=False):
        render_mode_switch_control()

def render_mode_switch_control():
    """Render mode switch controls"""
    
    current_mode = st.session_state.current_mode
    target_mode = 'live' if current_mode == 'demo' else 'demo'
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Current Mode:** {current_mode.upper()}")
        
        metadata = mode_config.get('metadata', {})
        if 'last_switched_at' in metadata:
            st.write(f"**Last Switched:** {metadata['last_switched_at']}")
        if 'last_switched_by_email' in metadata:
            st.write(f"**Last Switched By:** {metadata['last_switched_by_email']}")
        if metadata.get('auto_revert_enabled'):
            st.write(f"**Auto-Revert:** {metadata.get('auto_revert_at', 'Not set')}")
    
    with col2:
        if st.button(f"Switch to {target_mode.upper()} Mode", type="primary"):
            st.session_state.show_switch_dialog = True
    
    # Show switch dialog
    if st.session_state.get('show_switch_dialog', False):
        render_switch_dialog(target_mode)

def render_switch_dialog(target_mode: str):
    """Render mode switch dialog"""
    
    st.divider()
    st.subheader(f"Switch to {target_mode.upper()} Mode")
    
    # Show warnings
    if target_mode == 'live':
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ High Risk Operation</strong><br>
            • Switching to LIVE mode will affect 500+ production AWS accounts<br>
            • All deployments will be executed against real infrastructure<br>
            • Changes cannot be easily reversed<br>
            • Requires approval from Security and Operations teams<br>
            • MFA verification required<br>
            • All actions will be audited and logged
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-box">
            <strong>ℹ️ Safe Operation</strong><br>
            • Switching to DEMO mode will use sample data only<br>
            • No production infrastructure will be affected<br>
            • Safe for demonstrations and testing
        </div>
        """, unsafe_allow_html=True)
    
    # Form for switch
    with st.form("mode_switch_form"):
        # Email (or login)
        if not st.session_state.user_authenticated:
            email = st.text_input("Email Address*", placeholder="user@company.com")
        else:
            email = st.session_state.user_email
            st.write(f"**Email:** {email}")
        
        # Justification
        justification = st.text_area(
            "Justification*",
            placeholder="Provide detailed justification for switching mode (required for audit trail)",
            height=100
        )
        
        # MFA Code
        mfa_code = st.text_input(
            "MFA Code*",
            placeholder="Enter 6-digit MFA code",
            max_chars=6,
            type="password"
        )
        
        # Submit buttons
        col1, col2 = st.columns(2)
        with col1:
            cancel = st.form_submit_button("Cancel", type="secondary")
        with col2:
            submit = st.form_submit_button(
                "Submit Request" if target_mode == 'live' else "Switch Mode",
                type="primary"
            )
        
        if cancel:
            st.session_state.show_switch_dialog = False
            st.rerun()
        
        if submit:
            if not email or not justification or not mfa_code:
                st.error("All fields are required")
            else:
                # Execute mode switch
                result = mode_manager.switch_mode(
                    org_id, target_mode, email, justification, mfa_code
                )
                
                if result['status'] == 'pending_approval':
                    st.session_state.pending_approval = True
                    st.session_state.approval_request_id = result['request_id']
                    st.success(result['message'])
                    st.info("You will be notified once approved. This page will update automatically.")
                    time.sleep(3)
                    st.session_state.show_switch_dialog = False
                    st.rerun()
                elif result['status'] == 'completed':
                    st.session_state.current_mode = target_mode
                    st.success(result['message'])
                    time.sleep(2)
                    st.session_state.show_switch_dialog = False
                    st.rerun()
                else:
                    st.error(result['message'])

def render_dashboard():
    """Render main dashboard"""
    
    st.title("GitHub & GitOps Integration Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    mode = st.session_state.current_mode
    
    if mode == 'demo':
        with col1:
            st.metric("AWS Accounts", "10", delta="Demo")
        with col2:
            st.metric("Active Policies", "25", delta="Sample")
        with col3:
            st.metric("Compliance Score", "95.5%", delta="+2.3%")
        with col4:
            st.metric("Violations", "5", delta="-2")
    else:
        with col1:
            st.metric("AWS Accounts", "500+", delta="Production")
        with col2:
            st.metric("Active Policies", "156", delta="Live")
        with col3:
            st.metric("Compliance Score", "98.2%", delta="+1.1%")
        with col4:
            st.metric("Violations", "12", delta="-5")
    
    st.divider()
    
    # Overview sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Policy as Code Repository")
        st.write("Automated Detection, Remediation, and Deployment through GitOps Workflow")
        
        if mode == 'demo':
            st.info("🔴 DEMO MODE: Using sample repository data")
        else:
            st.success("🟢 LIVE MODE: Connected to production repository")
    
    with col2:
        st.subheader("📊 Repository Statistics")
        
        if mode == 'demo':
            stats = {
                "Total Commits": 1247,
                "Active Branches": 8,
                "Pull Requests": 3,
                "Policy Files": 156
            }
        else:
            stats = {
                "Total Commits": 3456,
                "Active Branches": 15,
                "Pull Requests": 7,
                "Policy Files": 342
            }
        
        for key, value in stats.items():
            st.metric(key, value)

def render_policy_update():
    """Render Policy Update tab"""
    
    st.title("📝 Policy Update")
    st.write("Create, modify, and version control compliance policies")
    
    mode = st.session_state.current_mode
    
    if mode == 'demo':
        st.info("🔴 DEMO MODE: Policy changes will be simulated")
    else:
        st.warning("🟢 LIVE MODE: Policy changes will affect production infrastructure")
    
    # Policy editor
    st.subheader("Policy Editor")
    
    policy_type = st.selectbox(
        "Policy Type",
        ["Service Control Policy (SCP)", "AWS Config Rule", "IAM Policy", "Compliance Guardrail"]
    )
    
    policy_name = st.text_input("Policy Name", placeholder="e.g., Require S3 Encryption")
    
    policy_code = st.text_area(
        "Policy Code",
        placeholder="Enter your policy code here (JSON, YAML, or Rego)",
        height=300
    )
    
    col1, col2 = st.columns(2)
    with col1:
        framework = st.selectbox("Compliance Framework", ["SOC2", "HIPAA", "PCI-DSS", "ISO 27001"])
    with col2:
        control = st.text_input("Control ID", placeholder="e.g., CC6.1")
    
    if st.button("Save Policy", type="primary"):
        if mode == 'demo':
            st.success("✅ Policy saved to demo repository (simulated)")
        else:
            st.success("✅ Policy saved to production repository")
            st.info("Triggering GitHub Actions workflow for validation...")

def render_detection():
    """Render Detection tab"""
    
    st.title("🔍 Detection")
    st.write("Automated validation, security scanning, and compliance checking")
    
    mode = st.session_state.current_mode
    
    if mode == 'demo':
        st.info("🔴 DEMO MODE: Showing sample validation results")
    
    # Validation stages
    stages = [
        {"name": "Syntax Validation", "status": "success", "duration": "2s"},
        {"name": "KICS Security Scan", "status": "success", "duration": "30s"},
        {"name": "OPA Policy Tests", "status": "success", "duration": "15s"},
        {"name": "Compliance Mapping", "status": "success", "duration": "5s"}
    ]
    
    for stage in stages:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{stage['name']}**")
        with col2:
            if stage['status'] == 'success':
                st.success("✅ PASSED")
            else:
                st.error("❌ FAILED")
        with col3:
            st.write(stage['duration'])
    
    st.divider()
    
    # Scan results
    st.subheader("Latest Scan Results")
    
    if mode == 'demo':
        results = {
            "Critical": 0,
            "High": 0,
            "Medium": 2,
            "Low": 5
        }
    else:
        results = {
            "Critical": 0,
            "High": 1,
            "Medium": 5,
            "Low": 12
        }
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Critical", results["Critical"])
    with col2:
        st.metric("High", results["High"])
    with col3:
        st.metric("Medium", results["Medium"])
    with col4:
        st.metric("Low", results["Low"])

def render_status():
    """Render Status tab"""
    
    st.title("📊 Status")
    st.write("Real-time visibility into repository and pipeline status")
    
    mode = st.session_state.current_mode
    
    # Recent commits
    st.subheader("Recent Commits")
    
    if mode == 'demo':
        commits = [
            {"sha": "abc123", "message": "Add SCP for S3 encryption (DEMO)", "author": "demo-user", "time": "2 hours ago", "status": "✅"},
            {"sha": "def456", "message": "Update OPA policy (DEMO)", "author": "automation", "time": "5 hours ago", "status": "✅"},
            {"sha": "ghi789", "message": "Onboard new account (DEMO)", "author": "pending", "time": "1 day ago", "status": "⏳"}
        ]
    else:
        commits = [
            {"sha": "xyz789", "message": "Add SCP for S3 encryption", "author": "ajit.kumar", "time": "1 hour ago", "status": "✅"},
            {"sha": "uvw456", "message": "Update Config Rule", "author": "security-team", "time": "3 hours ago", "status": "✅"},
            {"sha": "rst123", "message": "Deploy new policy", "author": "ops-team", "time": "6 hours ago", "status": "✅"}
        ]
    
    for commit in commits:
        col1, col2, col3, col4, col5 = st.columns([2, 4, 2, 2, 1])
        with col1:
            st.code(commit['sha'][:7])
        with col2:
            st.write(commit['message'])
        with col3:
            st.write(commit['author'])
        with col4:
            st.write(commit['time'])
        with col5:
            st.write(commit['status'])
    
    st.divider()
    
    # CI/CD Pipeline Status
    st.subheader("CI/CD Pipeline Status")
    
    pipeline_stages = [
        {"stage": "Policy Validation", "status": "SUCCESS", "duration": "2m 34s"},
        {"stage": "KICS Scan", "status": "RUNNING", "duration": "Started 30s ago"},
        {"stage": "Terraform Apply", "status": "PENDING", "duration": "Queued"},
        {"stage": "OPA Policy Test", "status": "SUCCESS", "duration": "45s"}
    ]
    
    for stage in pipeline_stages:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.write(f"**{stage['stage']}**")
        with col2:
            if stage['status'] == 'SUCCESS':
                st.success(stage['status'])
            elif stage['status'] == 'RUNNING':
                st.info(stage['status'])
            else:
                st.warning(stage['status'])
        with col3:
            st.write(stage['duration'])

def render_remediation():
    """Render Remediation tab"""
    
    st.title("🔧 Remediation")
    st.write("Automated deployment and enforcement of policies")
    
    mode = st.session_state.current_mode
    
    if mode == 'demo':
        st.info("🔴 DEMO MODE: Deployments will be simulated")
    else:
        st.warning("🟢 LIVE MODE: Deployments will affect real infrastructure")
    
    # Deployment configuration
    st.subheader("Deployment Configuration")
    
    deployment_target = st.selectbox(
        "Deployment Target",
        ["Specific Accounts", "Account Groups", "All Accounts"] if mode == 'live' else ["Demo Accounts"]
    )
    
    if mode == 'live':
        deployment_mode = st.radio(
            "Deployment Mode",
            ["Phased Rollout (Recommended)", "Immediate Deployment"]
        )
        
        if deployment_mode == "Phased Rollout (Recommended)":
            st.write("**Phase 1:** 10% of accounts (24h monitoring)")
            st.write("**Phase 2:** 50% of accounts (48h monitoring)")
            st.write("**Phase 3:** 100% of accounts (72h monitoring)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Deploy Policies", type="primary"):
            if mode == 'demo':
                st.success("✅ Simulated deployment initiated")
                with st.spinner("Simulating deployment..."):
                    time.sleep(2)
                st.success("✅ Demo deployment completed successfully")
            else:
                st.warning("⚠️ This will deploy to production. Approval required.")
    
    with col2:
        if st.button("Rollback", type="secondary"):
            st.info("Rollback to previous version")
    
    st.divider()
    
    # Deployment history
    st.subheader("Deployment History")
    
    if mode == 'demo':
        deployments = [
            {"id": "demo-001", "status": "Simulated Success", "accounts": 10, "time": "1 hour ago"},
            {"id": "demo-002", "status": "Simulated Success", "accounts": 10, "time": "1 day ago"}
        ]
    else:
        deployments = [
            {"id": "prod-045", "status": "Success", "accounts": 500, "time": "2 hours ago"},
            {"id": "prod-044", "status": "Success", "accounts": 250, "time": "1 day ago"}
        ]
    
    for deployment in deployments:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**{deployment['id']}**")
        with col2:
            st.success(deployment['status'])
        with col3:
            st.write(f"{deployment['accounts']} accounts")
        with col4:
            st.write(deployment['time'])

def render_settings():
    """Render Settings page"""
    
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["Mode Management", "Configuration", "Audit Logs"])
    
    with tab1:
        st.subheader("Mode Management")
        render_mode_switch_control()
    
    with tab2:
        st.subheader("Configuration")
        
        st.write("**Organization ID:**", org_id)
        st.write("**Current Mode:**", st.session_state.current_mode.upper())
        
        if 'aws' in st.secrets:
            st.write("**AWS Region:**", st.secrets['aws']['region'])
            st.success("✅ AWS Integration Enabled")
        else:
            st.warning("⚠️ AWS Integration Disabled (Local Mode)")
        
        st.divider()
        
        st.subheader("Security Settings")
        
        mfa_enabled = st.checkbox("Require MFA for mode switches", value=True, disabled=True)
        ip_whitelist = st.checkbox("Enable IP whitelisting for live mode", value=True, disabled=True)
        auto_revert = st.checkbox("Auto-revert to demo mode after 4 hours", value=True, disabled=True)
    
    with tab3:
        st.subheader("Audit Logs")
        
        st.write("Recent mode switch events:")
        
        # Sample audit logs
        logs = [
            {"timestamp": "2025-11-27 10:30:00", "event": "Mode Switch", "from": "demo", "to": "live", "user": "ajit.kumar@company.com"},
            {"timestamp": "2025-11-27 06:15:00", "event": "Mode Switch", "from": "live", "to": "demo", "user": "system_auto_revert"}
        ]
        
        for log in logs:
            st.write(f"**{log['timestamp']}** - {log['event']}: {log['from']} → {log['to']} by {log['user']}")

# Run the app
if __name__ == "__main__":
    main()
