"""
AI Threat Analysis - Complete Scene 6 Implementation
AWS re:Invent 2025 Video Script

Features for Scene 6:
1. Critical Security Finding Display
2. AI Analysis with expanding sections
3. Threat Assessment
4. Compliance Impact
5. Pattern Detection
6. Recommended Actions
7. One-Click Automated Remediation
8. Real-time remediation progress

Duration: 3:30 - 4:20 (50 seconds)
"""

import streamlit as st
import time
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

def render_ai_threat_analysis_scene():
    """
    Complete AI Threat Analysis scene matching video script Scene 6
    """
    
    st.markdown("## 🤖 AI-Powered Threat Analysis")
    st.markdown("*Real-time security intelligence with automated remediation*")
    
    st.markdown("---")
    
    # ============================================================================
    # CRITICAL SECURITY FINDING
    # ============================================================================
    
    st.markdown("### 🚨 Active Security Findings")
    
    # Critical Alert Card
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%);
        color: white;
        padding: 25px;
        border-radius: 10px;
        border: 3px solid #AA0000;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(255,0,0,0.3);
        animation: pulse 2s infinite;
    '>
        <div style='display: flex; align-items: center; margin-bottom: 15px;'>
            <span style='font-size: 36px; margin-right: 15px;'>⚠️</span>
            <div>
                <h2 style='margin: 0; color: white;'>CRITICAL SECURITY ALERT</h2>
                <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;'>Requires immediate attention</p>
            </div>
        </div>
        <div style='
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
        '>
            <h3 style='margin: 0 0 15px 0; color: white;'>Unauthorized IAM Policy Change</h3>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 14px;'>
                <div>
                    <strong>Account:</strong> prod-healthcare-01<br>
                    <strong>Resource:</strong> IAM Policy "DataAccessPolicy"<br>
                    <strong>Action:</strong> iam:PutRolePolicy
                </div>
                <div>
                    <strong>Time:</strong> 2025-11-25 14:23:18 UTC<br>
                    <strong>User:</strong> dev-user-1247<br>
                    <strong>Severity:</strong> CRITICAL
                </div>
            </div>
        </div>
    </div>
    
    <style>
        @keyframes pulse {
            0%, 100% { box-shadow: 0 4px 12px rgba(255,0,0,0.3); }
            50% { box-shadow: 0 4px 20px rgba(255,0,0,0.6); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col_action1, col_action2, col_action3 = st.columns([2, 1, 1])
    
    with col_action1:
        st.markdown("**Watch what happens when AI analyzes this.**")
    
    with col_action2:
        if st.button("🤖 Analyze with AI", type="primary", use_container_width=True, key="analyze_threat"):
            st.session_state.ai_analysis_started = True
    
    with col_action3:
        if st.button("📋 View Details", use_container_width=True, key="view_details"):
            st.info("Opening CloudTrail event details...")
    
    # ============================================================================
    # AI ANALYSIS - EXPANDING RAPIDLY
    # ============================================================================
    
    if st.session_state.get('ai_analysis_started', False):
        
        st.markdown("---")
        st.markdown("### 🧠 Claude AI Analysis")
        
        # AI analyzing animation
        with st.spinner("🤖 Claude AI analyzing security event..."):
            time.sleep(1.5)
        
        # AI Analysis Container
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #E8F4F8 0%, #D5E8F0 100%);
            border-left: 5px solid #00A8E1;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        '>
            <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                <span style='font-size: 32px; margin-right: 15px;'>🤖</span>
                <h3 style='margin: 0; color: #232F3E;'>Claude AI Security Analysis</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create placeholders for expanding analysis sections
        analysis_placeholder = st.empty()
        
        # Section 1: Threat Assessment (appears first)
        time.sleep(0.3)
        analysis_placeholder.markdown("""
        <div style='background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #FF9900; margin: 10px 0; animation: slideIn 0.5s;'>
            <h4 style='margin: 0 0 10px 0; color: #232F3E;'>🎯 Threat Assessment</h4>
            <p style='color: #666; font-size: 16px; line-height: 1.6; margin: 0;'>
                <strong style='color: #D13212;'>HIGH RISK:</strong> Overly permissive S3 access policy added to role with access to Protected Health Information (PHI) data. 
                Policy grants <code>s3:*</code> permissions to all buckets, bypassing existing data governance controls.
            </p>
        </div>
        
        <style>
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Section 2: Compliance Impact (appears second)
        time.sleep(0.4)
        st.markdown("""
        <div style='background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #D13212; margin: 10px 0; animation: slideIn 0.5s;'>
            <h4 style='margin: 0 0 10px 0; color: #232F3E;'>⚠️ Compliance Impact</h4>
            <p style='color: #666; font-size: 16px; line-height: 1.6; margin: 0 0 10px 0;'>
                <strong style='color: #D13212;'>VIOLATION:</strong> HIPAA §164.308(a)(4) - Information Access Management
            </p>
            <ul style='color: #666; font-size: 14px; margin: 0; padding-left: 20px;'>
                <li>Fails minimum necessary access principle</li>
                <li>No role-based access control enforcement</li>
                <li>PHI exposure risk: <strong>HIGH</strong></li>
                <li>Audit finding severity: <strong>CRITICAL</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 3: Pattern Detection (appears third)
        time.sleep(0.4)
        st.markdown("""
        <div style='background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #FF9900; margin: 10px 0; animation: slideIn 0.5s;'>
            <h4 style='margin: 0 0 10px 0; color: #232F3E;'>🔍 Pattern Detection</h4>
            <p style='color: #666; font-size: 16px; line-height: 1.6; margin: 0 0 10px 0;'>
                <strong>ANOMALY DETECTED:</strong> 3 more IAM policy changes in the last 2 hours
            </p>
            <div style='background: #FFF8DC; padding: 15px; border-radius: 5px; margin-top: 10px;'>
                <strong style='color: #232F3E;'>Matches Insider Threat Indicators:</strong>
                <ul style='color: #666; font-size: 14px; margin: 10px 0 0 0; padding-left: 20px;'>
                    <li>Privilege escalation attempt</li>
                    <li>After-hours activity (14:23 UTC = off-hours for user's timezone)</li>
                    <li>Unusual API call pattern (4x normal rate)</li>
                    <li>User account flagged for upcoming termination</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 4: Recommended Actions (appears fourth)
        time.sleep(0.4)
        st.markdown("""
        <div style='background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #00C851; margin: 10px 0; animation: slideIn 0.5s;'>
            <h4 style='margin: 0 0 15px 0; color: #232F3E;'>💡 Recommended Actions</h4>
            <div style='display: flex; flex-direction: column; gap: 12px;'>
                <div style='background: #FFE6E6; padding: 12px; border-radius: 5px; border-left: 3px solid #D13212;'>
                    <strong style='color: #D13212;'>1. IMMEDIATE:</strong> Revert policy change to previous version
                </div>
                <div style='background: #FFF8DC; padding: 12px; border-radius: 5px; border-left: 3px solid #FF9900;'>
                    <strong style='color: #FF9900;'>2. HIGH PRIORITY:</strong> Rotate credentials for affected role
                </div>
                <div style='background: #E8F4F8; padding: 12px; border-radius: 5px; border-left: 3px solid #00A8E1;'>
                    <strong style='color: #00A8E1;'>3. INVESTIGATE:</strong> Review CloudTrail logs for related activity
                </div>
                <div style='background: #E8F8F5; padding: 12px; border-radius: 5px; border-left: 3px solid #00C851;'>
                    <strong style='color: #00C851;'>4. PREVENT:</strong> Deploy preventive SCP to organization
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("✅ **AI Analysis Complete** - 4 actionable recommendations generated")
        
        # ============================================================================
        # ONE-CLICK AUTOMATED REMEDIATION
        # ============================================================================
        
        st.markdown("---")
        st.markdown("### ⚡ Automated Remediation")
        
        st.info("💡 **One-click automated remediation:** Policy reverted, security notified, incident ticket created, preventive controls deployed—automatically.")
        
        col_remediate1, col_remediate2 = st.columns([3, 1])
        
        with col_remediate1:
            st.markdown("**Execute all recommended actions automatically:**")
            
            remediation_options = st.multiselect(
                "Select remediation actions (all recommended)",
                [
                    "✅ Revert IAM policy to previous version",
                    "✅ Rotate credentials and revoke sessions",
                    "✅ Generate CloudTrail analysis report",
                    "✅ Deploy preventive SCP across organization",
                    "✅ Create Jira incident ticket",
                    "✅ Notify Security Operations Center",
                    "✅ Quarantine user account pending review"
                ],
                default=[
                    "✅ Revert IAM policy to previous version",
                    "✅ Rotate credentials and revoke sessions",
                    "✅ Generate CloudTrail analysis report",
                    "✅ Deploy preventive SCP across organization",
                    "✅ Create Jira incident ticket",
                    "✅ Notify Security Operations Center"
                ],
                key="remediation_options"
            )
        
        with col_remediate2:
            st.markdown("&nbsp;")  # Spacing
            if st.button("🚀 Execute Remediation", type="primary", use_container_width=True, key="execute_remediation"):
                st.session_state.remediation_started = True
        
        # ============================================================================
        # REMEDIATION PROGRESS - REAL-TIME
        # ============================================================================
        
        if st.session_state.get('remediation_started', False):
            
            st.markdown("---")
            st.markdown("### 🔄 Remediation In Progress")
            
            # Progress bar
            progress_bar = st.progress(0)
            status_container = st.container()
            
            remediation_steps = [
                ("⏳ Analyzing IAM policy history...", "Retrieving previous policy versions", 10),
                ("✅ Policy reverted", "IAM policy restored to version from 2025-11-24 12:00 UTC", 25),
                ("⏳ Rotating credentials...", "Generating new access keys and revoking old sessions", 35),
                ("✅ Credentials rotated", "User sessions terminated, new keys generated", 50),
                ("⏳ Analyzing CloudTrail logs...", "Scanning 24-hour window for related events", 60),
                ("✅ CloudTrail report generated", "18 related API calls identified, report created", 70),
                ("⏳ Deploying preventive SCP...", "Applying policy to Healthcare OU", 80),
                ("✅ SCP deployed", "Policy active across 47 accounts in Healthcare portfolio", 90),
                ("⏳ Creating incident ticket...", "Generating Jira ticket with full context", 95),
                ("✅ Incident ticket created", "Ticket JIRA-SEC-8472 assigned to Security team", 98),
                ("⏳ Notifying Security Operations...", "Sending alerts via Slack and PagerDuty", 99),
                ("✅ Security team notified", "Alert sent to #security-incidents channel", 100),
            ]
            
            # Execute remediation steps with animation
            completed_steps = []
            
            for step, detail, progress in remediation_steps:
                time.sleep(0.6)  # Realistic timing
                progress_bar.progress(progress)
                
                # Determine status color
                if step.startswith("⏳"):
                    color = "#FFA500"
                    bg_color = "#FFF8DC"
                else:
                    color = "#00C851"
                    bg_color = "#E8F8F5"
                
                # Add to completed steps
                completed_steps.append((step, detail, color, bg_color))
                
                # Render all completed steps
                with status_container:
                    for s, d, c, bc in completed_steps:
                        st.markdown(f"""
                        <div style='
                            background: {bc};
                            border-left: 4px solid {c};
                            padding: 12px 20px;
                            margin: 8px 0;
                            border-radius: 5px;
                        '>
                            <strong style='color: {c}; font-size: 16px;'>{s}</strong><br>
                            <span style='color: #666; font-size: 13px;'>{d}</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Remediation complete
            st.balloons()
            
            st.markdown("---")
            
            st.success("### ✅ Automated Remediation Complete!")
            
            # Success summary card
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #00C851 0%, #007E33 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin: 20px 0;
                box-shadow: 0 4px 12px rgba(0,200,81,0.3);
            '>
                <h2 style='margin: 0 0 20px 0; color: white; text-align: center;'>
                    🎉 Threat Neutralized & Prevented
                </h2>
                <div style='
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(255,255,255,0.3);
                '>
                    <div style='text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9;'>Resolution Time</div>
                        <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>47 sec</div>
                        <div style='font-size: 12px; opacity: 0.8;'>vs 4-6 hours manual</div>
                    </div>
                    <div style='text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9;'>Actions Completed</div>
                        <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>7</div>
                        <div style='font-size: 12px; opacity: 0.8;'>Fully automated</div>
                    </div>
                    <div style='text-align: center;'>
                        <div style='font-size: 14px; opacity: 0.9;'>Accounts Protected</div>
                        <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>47</div>
                        <div style='font-size: 12px; opacity: 0.8;'>SCP deployed</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed remediation summary
            st.markdown("#### 📋 Remediation Summary")
            
            col_sum1, col_sum2 = st.columns(2)
            
            with col_sum1:
                st.markdown("**Actions Completed:**")
                st.markdown("""
                - ✅ IAM policy reverted to safe version
                - ✅ User credentials rotated and sessions terminated
                - ✅ CloudTrail analysis report generated (18 events)
                - ✅ Preventive SCP deployed to Healthcare OU
                - ✅ Incident ticket created (JIRA-SEC-8472)
                - ✅ Security team notified via Slack + PagerDuty
                - ✅ User account flagged for security review
                """)
            
            with col_sum2:
                st.markdown("**Compliance Status:**")
                st.markdown("""
                - ✅ HIPAA violation remediated
                - ✅ Audit trail complete and preserved
                - ✅ Preventive controls in place
                - ✅ Incident response documented
                - ✅ Mean time to remediate: 47 seconds
                
                **Security Posture:** RESTORED ✅
                """)
            
            # Next steps
            st.markdown("---")
            st.markdown("#### 🎯 Recommended Next Steps")
            
            col_next1, col_next2, col_next3 = st.columns(3)
            
            with col_next1:
                if st.button("📊 View Full Report", use_container_width=True, key="view_report"):
                    st.info("Opening comprehensive incident report...")
            
            with col_next2:
                if st.button("📧 Notify Leadership", use_container_width=True, key="notify_leadership"):
                    st.success("Executive summary sent to security leadership")
            
            with col_next3:
                if st.button("🔍 Investigate Further", use_container_width=True, key="investigate"):
                    st.info("Opening detailed forensics analysis...")


def render_quick_threat_demo():
    """
    Quick demo version that auto-plays for video recording
    """
    
    st.markdown("### 🤖 AI Threat Analysis Demo")
    
    if st.button("▶️ Start Threat Analysis Demo", type="primary", use_container_width=True):
        st.session_state.demo_threat_mode = True
    
    if st.session_state.get('demo_threat_mode', False):
        st.session_state.ai_analysis_started = True
        st.session_state.remediation_started = True
        render_ai_threat_analysis_scene()


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

"""
TO ADD TO YOUR STREAMLIT APP:

1. Import this module:
   from ai_threat_scene_6_complete import render_ai_threat_analysis_scene

2. Add to your AI Remediation tab:
   
   with tabs[4]:  # AI Remediation tab
       st.markdown("## 🤖 AI-Powered Remediation")
       
       ai_tabs = st.tabs(["🔍 Threat Analysis", "AI Insights", "Code Generation", "Batch Remediation"])
       
       with ai_tabs[0]:
           render_ai_threat_analysis_scene()

3. Initialize session state:
   if 'ai_analysis_started' not in st.session_state:
       st.session_state.ai_analysis_started = False
   if 'remediation_started' not in st.session_state:
       st.session_state.remediation_started = False

VIDEO RECORDING TIPS:
- Start with security alert visible (0:00-0:05)
- Click "Analyze with AI" (0:05)
- AI analysis expands section by section (0:05-0:20)
- Show all 4 analysis sections (0:20-0:30)
- Click "Execute Remediation" (0:30)
- Watch remediation progress (0:30-0:50)
- Total scene: ~50 seconds (matches script 3:30-4:20)

KEY FEATURES:
✅ Critical security alert with full context
✅ AI analysis expanding in 4 sections:
   - Threat Assessment
   - Compliance Impact (HIPAA violation)
   - Pattern Detection (3 more changes, insider threat)
   - Recommended Actions (4 steps)
✅ One-click automated remediation
✅ Real-time progress with 7 automated actions
✅ 47-second resolution time
✅ Complete success summary

CUSTOMIZATION:
- Change timestamp in alert (line 56)
- Adjust remediation timing (line 250, currently 0.6s per step)
- Modify number of remediation steps (lines 234-245)
- Change compliance framework (currently HIPAA)
"""
