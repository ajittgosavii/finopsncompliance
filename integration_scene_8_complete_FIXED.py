"""
Enterprise Integration - Complete Scene 8 Implementation
AWS re:Invent 2025 Video Script

Features for Scene 8:
1. Integration Hub Dashboard
2. Connected Systems Display (Jira, ServiceNow, Slack, Wiz.io, Snyk, GitHub, GitLab)
3. Real-time Integration Examples
4. Automation Workflows
5. Success Metrics Dashboard
6. Team Notifications Demo

Duration: 4:20 - 4:50 (30 seconds)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

def render_enterprise_integration_scene():
    """
    Complete Enterprise Integration scene matching video script Scene 8
    UPDATED: Now supports both Demo and Live modes
    """
    
    # ⚠️ CRITICAL: Check demo_mode - default to False for LIVE mode
    is_demo = st.session_state.get('demo_mode', False)
    
    st.markdown("## 🔗 Enterprise Integration Hub")
    
    # Show mode indicator
    if is_demo:
        st.markdown("*Connected ecosystem for seamless automation* 🟠 **DEMO MODE**")
    else:
        st.markdown("*Connected ecosystem for seamless automation* 🟢 **LIVE MODE**")
    
    st.markdown("---")
    
    # ============================================================================
    # INTEGRATION HUB - CONNECTED SYSTEMS
    # ============================================================================
    
    st.markdown("### 🌐 Connected Enterprise Stack")
    
    st.info("**Integrates with your entire enterprise stack** — Security findings create tickets. Cost anomalies trigger alerts. Teams notified where they work.")
    
    # Integration grid showing all connected systems
    st.markdown("#### 🔌 Active Integrations")
    
    # Define integration data with both demo and live stat keys
    integration_data = {
        "Jira": {"icon": "🎫", "category": "Project Management", "demo_stats": "2,847 tickets created", "color": "#0052CC"},
        "Slack": {"icon": "💬", "category": "Team Communication", "demo_stats": "18,424 notifications sent", "color": "#4A154B"},
        "ServiceNow": {"icon": "🎟️", "category": "ITSM Platform", "demo_stats": "1,234 incidents tracked", "color": "#62D84E"},
        "Wiz.io": {"icon": "🛡️", "category": "Cloud Security", "demo_stats": "5,892 findings synced", "color": "#6B4FBB"},
        "Snyk": {"icon": "🔒", "category": "DevSecOps", "demo_stats": "3,421 vulnerabilities tracked", "color": "#4C4A73"},
        "GitHub": {"icon": "🐙", "category": "Source Control", "demo_stats": "847 repos monitored", "color": "#181717"},
        "GitLab": {"icon": "🦊", "category": "DevOps Platform", "demo_stats": "524 pipelines integrated", "color": "#FC6D26"},
        "PagerDuty": {"icon": "📟", "category": "Incident Response", "demo_stats": "342 alerts routed", "color": "#06AC38"}
    }
    
    col_int1, col_int2, col_int3, col_int4 = st.columns(4)
    
    # Get integration status from session state (for live mode)
    integrations = st.session_state.get('integrations', {})
    
    integration_names = list(integration_data.keys())
    
    with col_int1:
        for name in ["Jira", "Slack"]:
            info = integration_data[name]
            if is_demo:
                status = "Connected"
                metric = info["demo_stats"]
            else:
                # Live mode - get from session state
                config = integrations.get(name, {})
                status = "Connected" if config.get('enabled', False) else "Disconnected"
                metric = config.get('stats', "No data")
            render_integration_card(name, info["icon"], info["category"], status, metric, info["color"])
            st.markdown("")
    
    with col_int2:
        for name in ["ServiceNow", "Wiz.io"]:
            info = integration_data[name]
            if is_demo:
                status = "Connected"
                metric = info["demo_stats"]
            else:
                config = integrations.get(name, {})
                status = "Connected" if config.get('enabled', False) else "Disconnected"
                metric = config.get('stats', "No data")
            render_integration_card(name, info["icon"], info["category"], status, metric, info["color"])
            st.markdown("")
    
    with col_int3:
        for name in ["Snyk", "GitHub"]:
            info = integration_data[name]
            if is_demo:
                status = "Connected"
                metric = info["demo_stats"]
            else:
                config = integrations.get(name, {})
                status = "Connected" if config.get('enabled', False) else "Disconnected"
                metric = config.get('stats', "No data")
            render_integration_card(name, info["icon"], info["category"], status, metric, info["color"])
            st.markdown("")
    
    with col_int4:
        for name in ["GitLab", "PagerDuty"]:
            info = integration_data[name]
            if is_demo:
                status = "Connected"
                metric = info["demo_stats"]
            else:
                config = integrations.get(name, {})
                status = "Connected" if config.get('enabled', False) else "Disconnected"
                metric = config.get('stats', "No data")
            render_integration_card(name, info["icon"], info["category"], status, metric, info["color"])
            st.markdown("")
    
    st.markdown("---")
    
    # ============================================================================
    # REAL-TIME AUTOMATION EXAMPLES
    # ============================================================================
    
    st.markdown("### ⚡ Live Automation Examples")
    
    # Automation workflow visualization
    col_auto1, col_auto2 = st.columns([1, 1])
    
    with col_auto1:
        st.markdown("#### 🎯 Security Findings → Jira Tickets")
        
        st.markdown("""
        <div style='
            background: white;
            border: 2px solid #E1E4E8;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        '>
            <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                <div style='
                    background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%);
                    color: white;
                    padding: 10px 15px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    margin-right: 15px;
                '>
                    CRITICAL
                </div>
                <div>
                    <strong style='color: #232F3E;'>Security Hub Finding</strong><br>
                    <span style='color: #666; font-size: 13px;'>Public S3 bucket detected</span>
                </div>
            </div>
            
            <div style='text-align: center; padding: 10px 0;'>
                <span style='font-size: 24px; color: #00A8E1;'>↓</span><br>
                <span style='color: #666; font-size: 12px;'>Auto-creates in 0.8 seconds</span>
            </div>
            
            <div style='
                background: linear-gradient(135deg, #E8F4F8 0%, #D5E8F0 100%);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #0052CC;
            '>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <span style='font-size: 20px; margin-right: 10px;'>🎫</span>
                    <strong style='color: #232F3E;'>Jira Ticket SEC-8473</strong>
                </div>
                <div style='color: #666; font-size: 13px; line-height: 1.6;'>
                    <strong>Assignee:</strong> security-team@company.com<br>
                    <strong>Priority:</strong> Highest<br>
                    <strong>Labels:</strong> security, s3, compliance<br>
                    <strong>Description:</strong> Auto-generated with full context
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Cost anomaly example
        st.markdown("#### 💰 Cost Anomaly → Slack Alert")
        
        st.markdown("""
        <div style='
            background: white;
            border: 2px solid #E1E4E8;
            border-radius: 10px;
            padding: 20px;
        '>
            <div style='
                background: linear-gradient(135deg, #FF9900 0%, #FF6600 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            '>
                <strong>🚨 Cost Anomaly Detected</strong><br>
                <span style='font-size: 13px; opacity: 0.9;'>Predicted: $94K (+40% vs expected)</span>
            </div>
            
            <div style='text-align: center; padding: 10px 0;'>
                <span style='font-size: 24px; color: #00A8E1;'>↓</span><br>
                <span style='color: #666; font-size: 12px;'>Instant notification</span>
            </div>
            
            <div style='
                background: linear-gradient(135deg, #F9F4F9 0%, #F0E8F0 100%);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #4A154B;
            '>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <span style='font-size: 20px; margin-right: 10px;'>💬</span>
                    <strong style='color: #232F3E;'>Slack #finops-alerts</strong>
                </div>
                <div style='
                    background: white;
                    padding: 10px;
                    border-radius: 5px;
                    color: #666;
                    font-size: 13px;
                    font-family: monospace;
                '>
                    <strong>@finops-team</strong> Cost anomaly detected!<br>
                    Account: prod-api-01<br>
                    Impact: +$27K/month<br>
                    [View Details] [Acknowledge]
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto2:
        st.markdown("#### 🔍 Vulnerability Scan → ServiceNow")
        
        st.markdown("""
        <div style='
            background: white;
            border: 2px solid #E1E4E8;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        '>
            <div style='
                background: linear-gradient(135deg, #6B4FBB 0%, #4A3480 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            '>
                <div style='display: flex; align-items: center;'>
                    <span style='font-size: 24px; margin-right: 10px;'>🛡️</span>
                    <div>
                        <strong>Wiz.io Scan Complete</strong><br>
                        <span style='font-size: 13px; opacity: 0.9;'>47 new critical findings</span>
                    </div>
                </div>
            </div>
            
            <div style='text-align: center; padding: 10px 0;'>
                <span style='font-size: 24px; color: #00A8E1;'>↓</span><br>
                <span style='color: #666; font-size: 12px;'>Auto-sync to ITSM</span>
            </div>
            
            <div style='
                background: linear-gradient(135deg, #E8F8E8 0%, #D5F0D5 100%);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #62D84E;
            '>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <span style='font-size: 20px; margin-right: 10px;'>🎟️</span>
                    <strong style='color: #232F3E;'>ServiceNow INC0047823</strong>
                </div>
                <div style='color: #666; font-size: 13px; line-height: 1.6;'>
                    <strong>Category:</strong> Security<br>
                    <strong>Impact:</strong> High<br>
                    <strong>Assignment Group:</strong> Cloud Security<br>
                    <strong>SLA:</strong> 4 hours response time
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Code vulnerability example
        st.markdown("#### 🔒 Snyk Vulnerability → GitHub Issue")
        
        st.markdown("""
        <div style='
            background: white;
            border: 2px solid #E1E4E8;
            border-radius: 10px;
            padding: 20px;
        '>
            <div style='
                background: linear-gradient(135deg, #4C4A73 0%, #3A3850 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            '>
                <strong>🔒 Snyk: Critical CVE-2024-8472</strong><br>
                <span style='font-size: 13px; opacity: 0.9;'>Vulnerable dependency in api-service</span>
            </div>
            
            <div style='text-align: center; padding: 10px 0;'>
                <span style='font-size: 24px; color: #00A8E1;'>↓</span><br>
                <span style='color: #666; font-size: 12px;'>Creates issue + PR</span>
            </div>
            
            <div style='
                background: #F6F8FA;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #181717;
            '>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <span style='font-size: 20px; margin-right: 10px;'>🐙</span>
                    <strong style='color: #232F3E;'>GitHub Issue #847</strong>
                </div>
                <div style='color: #666; font-size: 13px; line-height: 1.6;'>
                    <strong>Repo:</strong> company/api-service<br>
                    <strong>Labels:</strong> security, critical, dependencies<br>
                    <strong>Auto-PR:</strong> #848 created with fix<br>
                    <strong>Reviewers:</strong> Auto-assigned
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================================================
    # INTEGRATION STATISTICS
    # ============================================================================
    
    st.markdown("### 📊 Integration Performance")
    
    col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
    
    with col_stat1:
        st.metric("Total Integrations", "8", "All active")
    
    with col_stat2:
        st.metric("Automated Actions", "24,847", "This month")
    
    with col_stat3:
        st.metric("Avg Response Time", "0.8 sec", "Near real-time")
    
    with col_stat4:
        st.metric("Success Rate", "99.7%", "+0.2%")
    
    with col_stat5:
        st.metric("Time Saved", "1,840 hrs", "Manual work eliminated")
    
    st.markdown("---")
    
    # ============================================================================
    # SUCCESS METRICS - KEY RESULTS
    # ============================================================================
    
    st.markdown("### 🎯 Enterprise Results")
    
    # Success metrics grid - matches video script
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    '>
        <h2 style='margin: 0 0 30px 0; text-align: center; color: white; font-size: 28px;'>
            ✨ Platform Impact Metrics
        </h2>
        
        <div style='
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 25px;
        '>
            <div style='
                background: rgba(255,255,255,0.1);
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                border: 2px solid rgba(255,255,255,0.2);
            '>
                <div style='font-size: 14px; opacity: 0.8; margin-bottom: 10px;'>Provisioning Speed</div>
                <div style='font-size: 48px; font-weight: bold; color: #00C851; margin: 15px 0;'>95%</div>
                <div style='font-size: 16px; font-weight: bold; color: #FF9900;'>Faster</div>
                <div style='font-size: 12px; opacity: 0.7; margin-top: 10px;'>10 min → 30 sec</div>
            </div>
            
            <div style='
                background: rgba(255,255,255,0.1);
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                border: 2px solid rgba(255,255,255,0.2);
            '>
                <div style='font-size: 14px; opacity: 0.8; margin-bottom: 10px;'>Annual Savings</div>
                <div style='font-size: 48px; font-weight: bold; color: #00C851; margin: 15px 0;'>$2.3M</div>
                <div style='font-size: 16px; font-weight: bold; color: #FF9900;'>Cost Reduction</div>
                <div style='font-size: 12px; opacity: 0.7; margin-top: 10px;'>Across organization</div>
            </div>
            
            <div style='
                background: rgba(255,255,255,0.1);
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                border: 2px solid rgba(255,255,255,0.2);
            '>
                <div style='font-size: 14px; opacity: 0.8; margin-bottom: 10px;'>Audit Speed</div>
                <div style='font-size: 48px; font-weight: bold; color: #00C851; margin: 15px 0;'>40%</div>
                <div style='font-size: 16px; font-weight: bold; color: #FF9900;'>Faster</div>
                <div style='font-size: 12px; opacity: 0.7; margin-top: 10px;'>3 weeks → 10 days</div>
            </div>
            
            <div style='
                background: rgba(255,255,255,0.1);
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                border: 2px solid rgba(255,255,255,0.2);
            '>
                <div style='font-size: 14px; opacity: 0.8; margin-bottom: 10px;'>Policy Compliance</div>
                <div style='font-size: 48px; font-weight: bold; color: #00C851; margin: 15px 0;'>99.2%</div>
                <div style='font-size: 16px; font-weight: bold; color: #FF9900;'>Adherence</div>
                <div style='font-size: 12px; opacity: 0.7; margin-top: 10px;'>640+ accounts</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional metrics breakdown
    st.markdown("---")
    
    col_detail1, col_detail2 = st.columns(2)
    
    with col_detail1:
        st.markdown("#### 📈 Operational Efficiency")
        
        efficiency_metrics = {
            "Metric": [
                "Mean Time to Remediate",
                "Security Finding Response",
                "Account Provisioning",
                "Policy Deployment",
                "Audit Preparation"
            ],
            "Before": [
                "4.2 hours",
                "2.8 hours",
                "10 minutes",
                "45 minutes",
                "3 weeks"
            ],
            "After": [
                "47 seconds",
                "12 seconds",
                "30 seconds",
                "2 minutes",
                "10 days"
            ],
            "Improvement": [
                "99.7%",
                "99.9%",
                "95.0%",
                "95.6%",
                "52.4%"
            ]
        }
        
        df_efficiency = pd.DataFrame(efficiency_metrics)
        st.dataframe(df_efficiency, use_container_width=True, hide_index=True)
    
    with col_detail2:
        st.markdown("#### 💰 Financial Impact")
        
        financial_metrics = {
            "Category": [
                "Infrastructure Optimization",
                "Labor Cost Reduction",
                "Avoided Security Incidents",
                "Compliance Penalties Avoided",
                "Audit Cost Reduction"
            ],
            "Annual Savings": [
                "$840,000",
                "$720,000",
                "$450,000",
                "$180,000",
                "$110,000"
            ],
            "% of Total": [
                "36.5%",
                "31.3%",
                "19.6%",
                "7.8%",
                "4.8%"
            ]
        }
        
        df_financial = pd.DataFrame(financial_metrics)
        st.dataframe(df_financial, use_container_width=True, hide_index=True)
    
    # Visualization of integrations
    st.markdown("---")
    st.markdown("#### 🔄 Integration Activity (Last 30 Days)")
    
    # Create integration activity chart
    integrations = ["Jira", "Slack", "ServiceNow", "Wiz.io", "Snyk", "GitHub", "GitLab", "PagerDuty"]
    activities = [2847, 18424, 1234, 5892, 3421, 847, 524, 342]
    
    fig_integrations = go.Figure(data=[
        go.Bar(
            x=integrations,
            y=activities,
            marker=dict(
                color=['#0052CC', '#4A154B', '#62D84E', '#6B4FBB', '#4C4A73', '#181717', '#FC6D26', '#06AC38'],
                line=dict(color='white', width=2)
            ),
            text=activities,
            textposition='outside',
            texttemplate='%{text:,.0f}',
        )
    ])
    
    fig_integrations.update_layout(
        title="Automated Actions by Integration",
        xaxis_title="Platform",
        yaxis_title="Actions Performed",
        height=400,
        showlegend=False,
        hovermode='x'
    )
    
    st.plotly_chart(fig_integrations, use_container_width=True)


def render_integration_card(name, icon, category, status, metric, color):
    """Render a single integration card"""
    
    status_color = "#00C851" if status == "Connected" else "#999"
    
    st.markdown(f"""
    <div style='
        background: white;
        border: 2px solid {color};
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    '>
        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
            <span style='font-size: 28px; margin-right: 12px;'>{icon}</span>
            <div style='flex: 1;'>
                <h4 style='margin: 0; color: #232F3E; font-size: 16px;'>{name}</h4>
                <span style='color: #666; font-size: 12px;'>{category}</span>
            </div>
            <div style='
                background: {status_color};
                color: white;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
            '>
                {status}
            </div>
        </div>
        <div style='
            background: #F6F8FA;
            padding: 8px;
            border-radius: 5px;
            color: #666;
            font-size: 11px;
            text-align: center;
        '>
            {metric}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_integration_flow_demo():
    """
    Animated integration flow demonstration
    """
    
    st.markdown("### 🔄 Live Integration Flow")
    
    if st.button("▶️ Show Integration Demo", type="primary", use_container_width=True):
        st.session_state.integration_demo_active = True
    
    if st.session_state.get('integration_demo_active', False):
        
        # Step 1: Security finding detected
        st.markdown("""
        <div style='background: #FFE6E6; padding: 15px; border-radius: 8px; border-left: 4px solid #D13212;'>
            <strong>Step 1:</strong> Security Hub detects critical finding
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1)
        
        # Step 2: Cloud Compliance Canvas processes
        st.markdown("""
        <div style='background: #E8F4F8; padding: 15px; border-radius: 8px; border-left: 4px solid #00A8E1;'>
            <strong>Step 2:</strong> Cloud Compliance Canvas AI analyzes finding
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1)
        
        # Step 3: Jira ticket created
        st.markdown("""
        <div style='background: #E8F4F8; padding: 15px; border-radius: 8px; border-left: 4px solid #0052CC;'>
            <strong>Step 3:</strong> Jira ticket SEC-8473 auto-created
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1)
        
        # Step 4: Slack notification
        st.markdown("""
        <div style='background: #F9F4F9; padding: 15px; border-radius: 8px; border-left: 4px solid #4A154B;'>
            <strong>Step 4:</strong> Slack notification sent to #security-team
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1)
        
        # Step 5: PagerDuty alert
        st.markdown("""
        <div style='background: #E8F8E8; padding: 15px; border-radius: 8px; border-left: 4px solid #06AC38;'>
            <strong>Step 5:</strong> PagerDuty alert triggered for on-call engineer
        </div>
        """, unsafe_allow_html=True)
        
        st.success("✅ **Integration flow complete** - All systems notified in 0.8 seconds!")


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

"""
TO ADD TO YOUR STREAMLIT APP:

1. Import this module:
   from integration_scene_8_complete import render_enterprise_integration_scene

2. Add as final scene in your demo or create dedicated tab:
   
   # Option A: Add to main tabs
   with tabs[9]:  # NEW TAB
       render_enterprise_integration_scene()
   
   # Option B: Add to existing tab
   with tabs[8]:  # FinOps tab
       finops_tabs = st.tabs(["Cost Dashboard", "Integrations"])
       with finops_tabs[1]:
           render_enterprise_integration_scene()

3. No additional session state needed (self-contained)

VIDEO RECORDING TIPS:
- Show integration hub grid (0:00-0:10)
- Highlight 8 connected systems (0:10-0:15)
- Show automation examples (0:15-0:20)
- Display success metrics (0:20-0:30)
- Total scene: 30 seconds (matches script 4:20-4:50)

KEY FEATURES:
✅ 8 enterprise integrations displayed
✅ Real-time automation examples:
   - Security findings → Jira tickets
   - Cost anomalies → Slack alerts
   - Vulnerabilities → ServiceNow
   - Code issues → GitHub
✅ Success metrics (exact from script):
   - 95% faster provisioning
   - $2.3M annual savings
   - 40% faster audits
   - 99.2% policy compliance
✅ Integration activity chart
✅ Financial impact breakdown
✅ Operational efficiency metrics

CUSTOMIZATION:
- Add/remove integrations (lines 60-95)
- Change activity counts (line 465)
- Modify success metrics (lines 350-410)
- Adjust color schemes per integration
"""
