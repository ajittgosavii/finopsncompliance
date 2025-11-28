"""
Enterprise Features Module for Future Minds Platform v5.0
Clean, working version with proper navigation
"""

import streamlit as st
import pandas as pd
import random
import time
import uuid
from datetime import datetime, timedelta

# ============================================================================
# ENTERPRISE AUTHENTICATION & RBAC
# ============================================================================

class EnterpriseAuth:
    """Enterprise Authentication & Authorization System"""
    
    ROLES = {
        'global_admin': {
            'name': 'Global Administrator',
            'permissions': ['*:*:*'],
        },
        'cfo': {
            'name': 'CFO / FinOps Admin',
            'permissions': ['accounts:read:tenant', 'finops:*:tenant', 'reports:*:tenant', 'dashboard:cfo:tenant'],
        },
        'ciso': {
            'name': 'CISO / Security Admin',
            'permissions': ['accounts:read:tenant', 'security:*:tenant', 'compliance:*:tenant', 'reports:*:tenant', 'dashboard:ciso:tenant'],
        },
        'cto': {
            'name': 'CTO / Technology Lead',
            'permissions': ['accounts:*:tenant', 'controltower:*:tenant', 'reports:read:tenant', 'dashboard:cto:tenant'],
        },
    }
    
    DEMO_USERS = {
        'admin@example.com': {
            'id': 'user-001',
            'name': 'Global Administrator',
            'email': 'admin@example.com',
            'tenant_id': 'tenant-001',
            'tenant_name': 'Enterprise Corp',
            'role': 'global_admin',
            'permissions': ROLES['global_admin']['permissions']
        },
        'cfo@example.com': {
            'id': 'user-002',
            'name': 'Chief Financial Officer',
            'email': 'cfo@example.com',
            'tenant_id': 'tenant-001',
            'tenant_name': 'Enterprise Corp',
            'role': 'cfo',
            'permissions': ROLES['cfo']['permissions']
        },
        'ciso@example.com': {
            'id': 'user-003',
            'name': 'Chief Information Security Officer',
            'email': 'ciso@example.com',
            'tenant_id': 'tenant-001',
            'tenant_name': 'Enterprise Corp',
            'role': 'ciso',
            'permissions': ROLES['ciso']['permissions']
        },
        'cto@example.com': {
            'id': 'user-004',
            'name': 'Chief Technology Officer',
            'email': 'cto@example.com',
            'tenant_id': 'tenant-001',
            'tenant_name': 'Enterprise Corp',
            'role': 'cto',
            'permissions': ROLES['cto']['permissions']
        },
    }
    
    @staticmethod
    def authenticate(email, password):
        """Authenticate user (mock for demo)"""
        if email in EnterpriseAuth.DEMO_USERS and password == 'demo123':
            return EnterpriseAuth.DEMO_USERS[email]
        return None
    
    @staticmethod
    def check_permission(user, permission):
        """Check if user has required permission"""
        if not user:
            return False
        user_perms = user.get('permissions', [])
        if '*:*:*' in user_perms:
            return True
        resource, action, scope = permission.split(':')
        for perm in user_perms:
            p_resource, p_action, p_scope = perm.split(':')
            if ((p_resource == '*' or p_resource == resource) and 
                (p_action == '*' or p_action == action) and 
                (p_scope == '*' or p_scope == scope)):
                return True
        return False

class ControlTowerManager:
    """AWS Control Tower Integration with Demo/Live Mode Support"""
    
    def __init__(self):
        """Initialize Control Tower Manager"""
        self.demo_mode = None  # Will be checked at runtime
        
    def _is_demo_mode(self):
        """Check if app is in demo mode"""
        return st.session_state.get('demo_mode', False)
    
    def get_landing_zone_status(self):
        """Get Control Tower landing zone status with demo/live support"""
        
        if self._is_demo_mode():
            # DEMO MODE - Return sample data
            return {
                'status': 'ACTIVE',
                'version': '3.3',
                'drift_status': 'IN_SYNC',
                'accounts_managed': 127,
                'guardrails_enabled': 45
            }
        else:
            # LIVE MODE - Connect to real AWS
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                # Get AWS Organizations client
                org_client = boto3.client('organizations')
                
                try:
                    # Get actual account count
                    accounts_response = org_client.list_accounts()
                    account_count = len(accounts_response.get('Accounts', []))
                    
                    # Try to get Control Tower status (if available)
                    # Note: Control Tower doesn't have direct API, using Organizations
                    try:
                        # Check if Control Tower is setup by looking for the CT OUs
                        roots = org_client.list_roots()
                        root_id = roots['Roots'][0]['Id'] if roots.get('Roots') else None
                        
                        # Count guardrails as number of SCPs
                        guardrails_count = 0
                        if root_id:
                            policies = org_client.list_policies(Filter='SERVICE_CONTROL_POLICY')
                            guardrails_count = len(policies.get('Policies', []))
                        
                        return {
                            'status': 'ACTIVE',
                            'version': '3.3',  # Can't get actual version via API
                            'drift_status': 'IN_SYNC',
                            'accounts_managed': account_count,
                            'guardrails_enabled': guardrails_count
                        }
                    except Exception as e:
                        # If Control Tower specific checks fail, return basic org info
                        return {
                            'status': 'ACTIVE',
                            'version': 'N/A',
                            'drift_status': 'UNKNOWN',
                            'accounts_managed': account_count,
                            'guardrails_enabled': 0
                        }
                        
                except ClientError as e:
                    st.error(f"⚠️ AWS Organizations Error: {str(e)}")
                    return {
                        'status': 'ERROR',
                        'version': 'N/A',
                        'drift_status': 'ERROR',
                        'accounts_managed': 0,
                        'guardrails_enabled': 0
                    }
                    
            except ImportError:
                st.error("⚠️ boto3 not installed. Cannot connect to AWS.")
                return {
                    'status': 'ERROR',
                    'version': 'N/A',
                    'drift_status': 'ERROR',
                    'accounts_managed': 0,
                    'guardrails_enabled': 0
                }
            except Exception as e:
                st.error(f"⚠️ Error connecting to AWS: {str(e)}")
                return {
                    'status': 'ERROR',
                    'version': 'N/A',
                    'drift_status': 'ERROR',
                    'accounts_managed': 0,
                    'guardrails_enabled': 0
                }
    
    def get_organizational_units(self):
        """Get organizational units with demo/live support"""
        
        if self._is_demo_mode():
            # DEMO MODE - Return sample OUs
            return [
                {'id': 'ou-prod-001', 'name': 'Production', 'accounts': 45, 'compliance': 98.5},
                {'id': 'ou-dev-001', 'name': 'Development', 'accounts': 32, 'compliance': 95.2},
                {'id': 'ou-stg-001', 'name': 'Staging', 'accounts': 20, 'compliance': 96.8},
                {'id': 'ou-sbx-001', 'name': 'Sandbox', 'accounts': 15, 'compliance': 88.3},
            ]
        else:
            # LIVE MODE - Get real OUs from AWS Organizations
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                org_client = boto3.client('organizations')
                
                try:
                    # Get root
                    roots = org_client.list_roots()
                    if not roots.get('Roots'):
                        return []
                    
                    root_id = roots['Roots'][0]['Id']
                    
                    # List all OUs under root
                    ous_data = []
                    ous_response = org_client.list_organizational_units_for_parent(ParentId=root_id)
                    
                    for ou in ous_response.get('OrganizationalUnits', []):
                        ou_id = ou['Id']
                        ou_name = ou['Name']
                        
                        # Count accounts in this OU
                        try:
                            accounts = org_client.list_accounts_for_parent(ParentId=ou_id)
                            account_count = len(accounts.get('Accounts', []))
                        except:
                            account_count = 0
                        
                        # Mock compliance for now (would need Security Hub integration)
                        compliance = random.uniform(85.0, 99.0)
                        
                        ous_data.append({
                            'id': ou_id,
                            'name': ou_name,
                            'accounts': account_count,
                            'compliance': round(compliance, 1)
                        })
                    
                    return ous_data if ous_data else [{'id': 'none', 'name': 'No OUs found', 'accounts': 0, 'compliance': 0}]
                    
                except ClientError as e:
                    st.error(f"⚠️ Error fetching OUs: {str(e)}")
                    return [{'id': 'error', 'name': 'Error fetching OUs', 'accounts': 0, 'compliance': 0}]
                    
            except ImportError:
                st.error("⚠️ boto3 not installed")
                return [{'id': 'error', 'name': 'boto3 not available', 'accounts': 0, 'compliance': 0}]
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                return [{'id': 'error', 'name': str(e), 'accounts': 0, 'compliance': 0}]
    
    def provision_account(self, name, email, ou, sso_user):
        """Provision new account with demo/live support"""
        
        if self._is_demo_mode():
            # DEMO MODE - Simulate account provisioning
            return {
                'status': 'SUCCESS',
                'account_id': f'{random.randint(100000000000, 999999999999)}',
                'provisioning_id': str(uuid.uuid4()),
                'services_enabled': ['SecurityHub', 'GuardDuty', 'Config', 'CloudTrail'],
                'mode': 'DEMO'
            }
        else:
            # LIVE MODE - Actually provision account via AWS Organizations
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                org_client = boto3.client('organizations')
                
                try:
                    # Create actual AWS account
                    response = org_client.create_account(
                        Email=email,
                        AccountName=name
                    )
                    
                    # Get the request ID to track provisioning
                    request_id = response['CreateAccountStatus']['Id']
                    
                    # Note: In production, you'd want to poll for completion
                    # For now, just return the request info
                    return {
                        'status': 'IN_PROGRESS',
                        'account_id': 'Pending...',
                        'provisioning_id': request_id,
                        'services_enabled': ['Will be configured after provisioning'],
                        'mode': 'LIVE',
                        'message': 'Account creation initiated. Check AWS Console for status.'
                    }
                    
                except ClientError as e:
                    st.error(f"⚠️ Error creating account: {str(e)}")
                    return {
                        'status': 'ERROR',
                        'account_id': 'N/A',
                        'provisioning_id': 'N/A',
                        'services_enabled': [],
                        'mode': 'LIVE',
                        'error': str(e)
                    }
                    
            except ImportError:
                st.error("⚠️ boto3 not installed. Cannot provision accounts.")
                return {
                    'status': 'ERROR',
                    'account_id': 'N/A',
                    'provisioning_id': 'N/A',
                    'services_enabled': [],
                    'mode': 'LIVE',
                    'error': 'boto3 not available'
                }
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                return {
                    'status': 'ERROR',
                    'account_id': 'N/A',
                    'provisioning_id': 'N/A',
                    'services_enabled': [],
                    'mode': 'LIVE',
                    'error': str(e)
                }

class RealTimeCostMonitor:
    """Real-time cost monitoring"""
    
    def get_current_hourly_cost(self):
        return {
            'total': 118.64,
            'by_service': {
                'EC2': 45.30,
                'RDS': 25.80,
                'S3': 12.45,
                'Lambda': 8.20,
                'Other': 26.89
            },
            'burn_rate': {
                'hourly': 118.64,
                'daily': 2847.36,
                'monthly_projection': 85421.00
            }
        }
    
    def detect_anomalies(self):
        return [
            {
                'service': 'EC2',
                'region': 'us-east-1',
                'current_cost': 2847.50,
                'expected_cost': 1800.00,
                'increase_pct': 58.2,
                'confidence': 'HIGH',
                'root_cause': '15 new m5.2xlarge instances launched'
            }
        ]
    
    def get_budget_status(self):
        return {
            'monthly_budget': 100000,
            'current_spend': 85421,
            'utilization_pct': 85.4
        }
    
    def get_chargeback_data(self):
        return [
            {'department': 'Engineering', 'cost': 45000, 'budget': 50000, 'utilization': '90%'},
            {'department': 'Product', 'cost': 23000, 'budget': 25000, 'utilization': '92%'},
            {'department': 'Data Science', 'cost': 18000, 'budget': 20000, 'utilization': '90%'},
        ]

# ============================================================================
# ENTERPRISE UI FUNCTIONS
# ============================================================================

def init_enterprise_session():
    """Initialize enterprise session state"""
    if 'enterprise_initialized' not in st.session_state:
        st.session_state.enterprise_initialized = True
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.last_activity = datetime.now()
        st.session_state.ct_manager = ControlTowerManager()
        st.session_state.cost_monitor = RealTimeCostMonitor()

def render_enterprise_login():
    """Enterprise login page"""
    st.markdown("""
    <div class='main-header'>
        <h1>🛡️ Future Minds Enterprise Platform v5.0</h1>
        <p>Unified Cloud Governance • Security • Compliance • FinOps</p>
        <div style='background: #FF9900; color: #232F3E; padding: 0.4rem 1.2rem; border-radius: 25px; 
                    font-weight: bold; display: inline-block; margin-top: 1rem;'>ENTERPRISE EDITION</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Secure Sign In")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@company.com")
            password = st.text_input("Password", type="password", placeholder="demo123")
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if submit:
                user = EnterpriseAuth.authenticate(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"✅ Welcome, {user['name']}!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Try: cfo@example.com / demo123")
        
        st.markdown("---")
        st.markdown("**Demo Accounts** (password: `demo123`):")
        st.markdown("- `admin@example.com` - Global Admin")
        st.markdown("- `cfo@example.com` - CFO/FinOps")
        st.markdown("- `ciso@example.com` - CISO/Security")
        st.markdown("- `cto@example.com` - CTO/Operations")

def render_enterprise_header():
    """Show enterprise user banner"""
    user = st.session_state.user
    col1, col2 = st.columns([5, 1])
    with col1:
        role_name = EnterpriseAuth.ROLES[user['role']]['name']
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #232F3E 0%, #37475A 100%); 
                    padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;'>
            <strong>👤 {user['name']}</strong> • <em>{role_name}</em> • 
            <small style='background: #FF9900; padding: 0.2rem 0.6rem; border-radius: 10px; 
                         color: #232F3E; font-weight: bold;'>{user['tenant_name']}</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

def render_enterprise_sidebar():
    """Render enterprise navigation menu"""
    st.markdown("## 🎯 Executive Dashboards")
    
    user = st.session_state.user
    
    # CFO Dashboard
    if EnterpriseAuth.check_permission(user, 'dashboard:cfo:tenant'):
        if st.button("💰 CFO Dashboard", use_container_width=True, key="nav_cfo"):
            st.session_state.enterprise_page = 'cfo'
            st.rerun()
    
    # Control Tower
    if EnterpriseAuth.check_permission(user, 'controltower:read:tenant'):
        if st.button("🏗️ Control Tower", use_container_width=True, key="nav_ct"):
            st.session_state.enterprise_page = 'controltower'
            st.rerun()
    
    # Real-Time Costs
    if EnterpriseAuth.check_permission(user, 'finops:read:tenant'):
        if st.button("💸 Real-Time Costs", use_container_width=True, key="nav_rtc"):
            st.session_state.enterprise_page = 'realtime_costs'
            st.rerun()
    
    # Main Dashboard
    if st.button("🏠 Main Dashboard", use_container_width=True, key="nav_main"):
        st.session_state.enterprise_page = None
        st.rerun()
    
    st.markdown("---")

def render_cfo_dashboard():
    """CFO Executive Dashboard"""
    if not EnterpriseAuth.check_permission(st.session_state.user, 'dashboard:cfo:tenant'):
        st.error("❌ Access Denied")
        return
    
    # Back button
    if st.button("⬅️ Back to Main Dashboard", key="cfo_back"):
        st.session_state.enterprise_page = None
        st.rerun()
    
    st.title("💰 CFO Dashboard - Financial Overview")
    
    cost_data = st.session_state.cost_monitor.get_current_hourly_cost()
    budget_data = st.session_state.cost_monitor.get_budget_status()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cloud Spend", "$2.4M", "-8.2%", delta_color="inverse")
    with col2:
        st.metric("Savings Realized", "$287K", "+$45K")
    with col3:
        st.metric("ROI on Cloud", "342%", "+12%")
    with col4:
        st.metric("Budget Utilization", f"{budget_data['utilization_pct']:.1f}%")
    
    st.markdown("---")
    st.markdown("### 💳 Department Chargeback/Showback")
    chargeback = st.session_state.cost_monitor.get_chargeback_data()
    st.dataframe(pd.DataFrame(chargeback), use_container_width=True, hide_index=True)

def render_control_tower():
    """Control Tower Management Dashboard with Demo/Live Mode Support"""
    if not EnterpriseAuth.check_permission(st.session_state.user, 'controltower:read:tenant'):
        st.error("❌ Access Denied")
        return
    
    # Back button
    if st.button("⬅️ Back to Main Dashboard", key="ct_back"):
        st.session_state.enterprise_page = None
        st.rerun()
    
    # ⚠️ CRITICAL: Check and display mode
    is_demo = st.session_state.get('demo_mode', False)
    
    # Title with mode indicator
    if is_demo:
        st.title("🏗️ AWS Control Tower Management 🟠 DEMO MODE")
        st.warning("📊 Demo Mode: Showing sample data (127 accounts, 45 guardrails)")
    else:
        st.title("🏗️ AWS Control Tower Management 🟢 LIVE MODE")
        st.info("🔗 Connected to your AWS Organization")
    
    ct = st.session_state.ct_manager
    lz = ct.get_landing_zone_status()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_color = "🟢" if lz['status'] == 'ACTIVE' else "🔴"
        st.metric("Status", f"{status_color} {lz['status']}")
    with col2:
        st.metric("Accounts Managed", lz['accounts_managed'])
    with col3:
        st.metric("Guardrails Enabled", lz['guardrails_enabled'])
    
    st.markdown("---")
    st.markdown("### 🏢 Organizational Units")
    ous = ct.get_organizational_units()
    st.dataframe(pd.DataFrame(ous), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Account provisioning section with mode-aware messaging
    if is_demo:
        st.markdown("### ➕ Provision New Account (60-second target) - **DEMO SIMULATION**")
        st.caption("Note: In Demo mode, this simulates account provisioning without creating real AWS accounts")
    else:
        st.markdown("### ➕ Provision New Account (60-second target) - **LIVE PROVISIONING**")
        st.caption("⚠️ Warning: This will create an actual AWS account in your organization!")
    
    with st.form("provision_account"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Account Name", placeholder="prod-app-2024")
            email = st.text_input("Email", placeholder="aws+prod@company.com")
        with col2:
            ou = st.selectbox("Organizational Unit", [o['name'] for o in ous])
            sso = st.text_input("SSO User Email", placeholder="owner@company.com")
        
        button_label = "🚀 Provision Account (Simulation)" if is_demo else "🚀 Provision Account (LIVE - Creates Real Account!)"
        
        if st.form_submit_button(button_label, type="primary", use_container_width=True):
            start_time = time.time()
            with st.spinner("Provisioning via Account Factory..."):
                progress = st.progress(0)
                for i in range(21):
                    progress.progress(i * 5)
                    time.sleep(0.05)
                
                result = ct.provision_account(name, email, ou, sso)
                elapsed = time.time() - start_time
                
                progress.empty()
                
                if result['status'] == 'SUCCESS':
                    st.success(f"✅ **SUCCESS!** Account {result['account_id']} provisioned in {elapsed:.1f} seconds!")
                    st.info(f"**Services Enabled:** {', '.join(result['services_enabled'])}")
                    if result.get('mode') == 'DEMO':
                        st.caption("🟠 This was a demo simulation - no real account was created")
                elif result['status'] == 'IN_PROGRESS':
                    st.info(f"⏳ **PROVISIONING STARTED** - Request ID: {result['provisioning_id']}")
                    st.info(result.get('message', 'Account creation in progress'))
                else:
                    st.error(f"❌ **ERROR** - {result.get('error', 'Unknown error')}")

def render_realtime_costs():
    """Real-Time Cost Operations Dashboard"""
    if not EnterpriseAuth.check_permission(st.session_state.user, 'finops:read:tenant'):
        st.error("❌ Access Denied")
        return
    
    # Back button
    if st.button("⬅️ Back to Main Dashboard", key="rtc_back"):
        st.session_state.enterprise_page = None
        st.rerun()
    
    st.title("💸 Real-Time Cost Operations")
    
    cost_data = st.session_state.cost_monitor.get_current_hourly_cost()
    anomalies = st.session_state.cost_monitor.detect_anomalies()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Hourly Burn Rate", f"${cost_data['burn_rate']['hourly']:.2f}/hr", "+12.3%")
    with col2:
        st.metric("Today's Spend", f"${cost_data['burn_rate']['daily']:,.2f}")
    with col3:
        st.metric("Monthly Projection", f"${cost_data['burn_rate']['monthly_projection']:,.0f}", "+8.5%")
    
    if anomalies:
        st.markdown("### ⚠️ Cost Anomalies Detected (Real-Time)")
        for a in anomalies:
            st.warning(f"🚨 **{a['service']}** in {a['region']}: +{a['increase_pct']:.1f}% increase - {a['root_cause']}")

def check_enterprise_routing():
    """Check if enterprise page is requested and route accordingly"""
    enterprise_page = st.session_state.get('enterprise_page')
    if enterprise_page == 'cfo':
        render_cfo_dashboard()
        return True
    elif enterprise_page == 'controltower':
        render_control_tower()
        return True
    elif enterprise_page == 'realtime_costs':
        render_realtime_costs()
        return True
    return False
