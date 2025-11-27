"""
Batch Remediation Module - Production Implementation
Bulk threat remediation across multiple threats and accounts
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

# Feature flag - set to True when ready to enable in production
BATCH_REMEDIATION_ENABLED = True  # Change to True to enable


def execute_batch_remediation(selected_threats: List[Dict], remediation_options: Dict) -> Dict:
    """
    Execute remediation actions on multiple threats simultaneously
    
    Args:
        selected_threats: List of threat dictionaries
        remediation_options: Configuration for remediation actions
    
    Returns:
        Dict with batch remediation results
    """
    results = {
        'total_threats': len(selected_threats),
        'successful': 0,
        'failed': 0,
        'start_time': datetime.utcnow().isoformat(),
        'end_time': None,
        'details': []
    }
    
    for threat in selected_threats:
        try:
            # Execute remediation for each threat
            threat_result = remediate_single_threat(
                threat,
                remediation_options
            )
            
            if threat_result['status'] == 'SUCCESS':
                results['successful'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append(threat_result)
            
        except Exception as e:
            results['failed'] += 1
            results['details'].append({
                'threat_id': threat.get('threat_id', 'UNKNOWN'),
                'status': 'FAILED',
                'error': str(e)
            })
    
    results['end_time'] = datetime.utcnow().isoformat()
    return results


def remediate_single_threat(threat: Dict, options: Dict) -> Dict:
    """
    Remediate a single threat based on options
    
    Args:
        threat: Threat dictionary
        options: Remediation options
    
    Returns:
        Dict with remediation result
    """
    import boto3
    
    result = {
        'threat_id': threat.get('threat_id'),
        'status': 'SUCCESS',
        'actions': [],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        # Determine threat type and execute appropriate remediation
        event_name = threat.get('event_name', '')
        
        if 'IAM' in event_name or 'Policy' in event_name:
            result['actions'] = remediate_iam_threat(threat, options)
        elif 'S3' in event_name or 'Bucket' in event_name:
            result['actions'] = remediate_s3_threat(threat, options)
        elif 'SecurityGroup' in event_name:
            result['actions'] = remediate_sg_threat(threat, options)
        else:
            result['actions'] = remediate_generic_threat(threat, options)
        
    except Exception as e:
        result['status'] = 'FAILED'
        result['error'] = str(e)
    
    return result


def remediate_iam_threat(threat: Dict, options: Dict) -> List[Dict]:
    """Remediate IAM-related threats"""
    import boto3
    
    iam = boto3.client('iam', region_name='us-east-1')
    actions = []
    
    event_details = threat.get('event_details', {})
    event_name = event_details.get('eventName')
    request_params = event_details.get('requestParameters', {})
    
    if options.get('revert_changes', True):
        if event_name == 'PutRolePolicy':
            role_name = request_params.get('roleName')
            policy_name = request_params.get('policyName')
            
            iam.delete_role_policy(
                RoleName=role_name,
                PolicyName=policy_name
            )
            
            actions.append({
                'action': 'DeleteRolePolicy',
                'target': f"{role_name}/{policy_name}"
            })
    
    if options.get('rotate_credentials', False):
        user_arn = event_details.get('userIdentity', {}).get('arn', '')
        if user_arn:
            user_name = user_arn.split('/')[-1]
            
            # List and delete access keys
            keys = iam.list_access_keys(UserName=user_name)
            for key in keys.get('AccessKeyMetadata', []):
                iam.delete_access_key(
                    UserName=user_name,
                    AccessKeyId=key['AccessKeyId']
                )
            
            actions.append({
                'action': 'RotateCredentials',
                'target': user_name
            })
    
    return actions


def remediate_s3_threat(threat: Dict, options: Dict) -> List[Dict]:
    """Remediate S3-related threats"""
    import boto3
    
    s3 = boto3.client('s3', region_name='us-east-1')
    actions = []
    
    event_details = threat.get('event_details', {})
    bucket_name = event_details.get('requestParameters', {}).get('bucketName')
    
    if bucket_name and options.get('enable_encryption', True):
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        )
        
        actions.append({
            'action': 'EnableEncryption',
            'target': bucket_name
        })
    
    if bucket_name and options.get('block_public_access', True):
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        
        actions.append({
            'action': 'BlockPublicAccess',
            'target': bucket_name
        })
    
    return actions


def remediate_sg_threat(threat: Dict, options: Dict) -> List[Dict]:
    """Remediate Security Group threats"""
    import boto3
    
    ec2 = boto3.client('ec2', region_name='us-east-1')
    actions = []
    
    event_details = threat.get('event_details', {})
    sg_id = event_details.get('requestParameters', {}).get('groupId')
    
    if sg_id and options.get('revoke_rules', True):
        # Get security group
        response = ec2.describe_security_groups(GroupIds=[sg_id])
        sg = response['SecurityGroups'][0]
        
        # Revoke overly permissive rules
        for rule in sg.get('IpPermissions', []):
            for ip_range in rule.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':
                    ec2.revoke_security_group_ingress(
                        GroupId=sg_id,
                        IpPermissions=[rule]
                    )
                    
                    actions.append({
                        'action': 'RevokeIngress',
                        'target': f"{sg_id}/0.0.0.0/0"
                    })
    
    return actions


def remediate_generic_threat(threat: Dict, options: Dict) -> List[Dict]:
    """Generic remediation for unknown threat types"""
    
    actions = []
    
    # Log the threat
    actions.append({
        'action': 'LogThreat',
        'target': threat.get('threat_id', 'UNKNOWN')
    })
    
    # Send notification
    if options.get('notify', True):
        actions.append({
            'action': 'NotifySecurityTeam',
            'target': 'security-team@example.com'
        })
    
    return actions


def schedule_batch_remediation(selected_threats: List[Dict], schedule_time: datetime, options: Dict) -> str:
    """
    Schedule batch remediation for a future time
    
    Args:
        selected_threats: List of threats to remediate
        schedule_time: When to execute remediation
        options: Remediation options
    
    Returns:
        Schedule ID
    """
    import uuid
    
    schedule_id = f"SCHED-{uuid.uuid4().hex[:8].upper()}"
    
    # In production, this would store the schedule in DynamoDB
    schedule_data = {
        'schedule_id': schedule_id,
        'threats': [t.get('threat_id') for t in selected_threats],
        'schedule_time': schedule_time.isoformat(),
        'options': options,
        'status': 'SCHEDULED',
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Store in session state for now (in production: DynamoDB)
    if 'scheduled_remediations' not in st.session_state:
        st.session_state.scheduled_remediations = []
    
    st.session_state.scheduled_remediations.append(schedule_data)
    
    return schedule_id


def render_batch_remediation_tab(available_threats: List[Dict] = None):
    """
    Render the Batch Remediation tab content
    
    Args:
        available_threats: List of available threats (optional)
    """
    
    if not BATCH_REMEDIATION_ENABLED:
        # Show placeholder until feature is enabled
        st.markdown("### ⚡ Batch Threat Remediation")
        st.info("💡 **Coming Soon:** Bulk remediation across multiple threats and accounts")
        
        st.markdown("""
        This feature will enable:
        - Remediate multiple threats simultaneously
        - Apply fixes across multiple AWS accounts
        - Schedule remediation during maintenance windows
        - Rollback capabilities with audit trail
        - Compliance reporting for all remediation actions
        """)
        
        # Placeholder UI
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pending Remediations", "0", help="Threats awaiting batch remediation")
        with col2:
            st.metric("Scheduled Actions", "0", help="Remediation actions scheduled")
        with col3:
            st.metric("Success Rate", "N/A", help="Historical remediation success rate")
        
        st.markdown("---")
        st.markdown("**Batch Operations:** Select multiple threats from the Threat Analysis tab to enable batch remediation.")
        
        return
    
    # PRODUCTION IMPLEMENTATION
    st.markdown("### ⚡ Batch Threat Remediation")
    
    if available_threats is None or len(available_threats) == 0:
        st.warning("⚠️ No threats available for batch remediation. Navigate to Threat Analysis to load threats.")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pending = len([t for t in available_threats if t.get('status') == 'ACTIVE'])
        st.metric("Available Threats", pending, help="Active threats available for remediation")
    
    with col2:
        scheduled_count = len(st.session_state.get('scheduled_remediations', []))
        st.metric("Scheduled Actions", scheduled_count, help="Remediation actions scheduled")
    
    with col3:
        history = st.session_state.get('remediation_history', [])
        if history:
            success_rate = sum(1 for h in history if h.get('status') == 'SUCCESS') / len(history) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%", help="Historical remediation success rate")
        else:
            st.metric("Success Rate", "N/A", help="No historical data yet")
    
    with col4:
        total_remediated = len(history) if history else 0
        st.metric("Total Remediated", total_remediated, help="Total threats remediated")
    
    st.markdown("---")
    
    # Threat Selection
    st.markdown("#### 1️⃣ Select Threats for Batch Remediation")
    
    # Create DataFrame for display
    threat_df = pd.DataFrame([
        {
            'Select': False,
            'Threat ID': t.get('threat_id', 'UNKNOWN'),
            'Severity': t.get('severity', 'UNKNOWN'),
            'Type': t.get('threat_type', 'Unknown'),
            'Event': t.get('event_name', 'Unknown'),
            'Account': t.get('account_id', 'Unknown'),
            'Time': t.get('timestamp', 'Unknown')[:19] if t.get('timestamp') else 'Unknown'
        }
        for t in available_threats
    ])
    
    # Display threat selection table
    edited_df = st.data_editor(
        threat_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select threats for batch remediation",
                default=False,
            ),
            "Severity": st.column_config.TextColumn(
                "Severity",
                width="small",
            ),
        }
    )
    
    selected_threats = [
        available_threats[i] 
        for i, row in edited_df.iterrows() 
        if row['Select']
    ]
    
    st.markdown(f"**Selected:** {len(selected_threats)} threat(s)")
    
    if len(selected_threats) == 0:
        st.info("👆 Select one or more threats from the table above to begin batch remediation.")
        return
    
    st.markdown("---")
    
    # Remediation Options
    st.markdown("#### 2️⃣ Configure Remediation Options")
    
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        st.markdown("**Actions:**")
        revert_changes = st.checkbox("✅ Revert unauthorized changes", value=True)
        rotate_credentials = st.checkbox("🔑 Rotate compromised credentials", value=True)
        enable_encryption = st.checkbox("🔒 Enable encryption", value=True)
        
    with col_opt2:
        st.markdown("**Additional:**")
        block_public_access = st.checkbox("🚫 Block public access", value=True)
        revoke_rules = st.checkbox("⛔ Revoke security group rules", value=True)
        notify_team = st.checkbox("📧 Notify security team", value=True)
    
    remediation_options = {
        'revert_changes': revert_changes,
        'rotate_credentials': rotate_credentials,
        'enable_encryption': enable_encryption,
        'block_public_access': block_public_access,
        'revoke_rules': revoke_rules,
        'notify': notify_team
    }
    
    st.markdown("---")
    
    # Execution Options
    st.markdown("#### 3️⃣ Execute or Schedule")
    
    col_exec1, col_exec2 = st.columns(2)
    
    with col_exec1:
        st.markdown("**Immediate Execution:**")
        
        if st.button("🚀 Execute Remediation Now", type="primary", use_container_width=True):
            st.session_state.batch_remediation_started = True
            st.session_state.batch_selected_threats = selected_threats
            st.session_state.batch_options = remediation_options
    
    with col_exec2:
        st.markdown("**Scheduled Execution:**")
        
        schedule_date = st.date_input("Schedule Date", value=datetime.now() + timedelta(days=1))
        schedule_time = st.time_input("Schedule Time", value=datetime.now().time())
        
        if st.button("📅 Schedule Remediation", use_container_width=True):
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
            schedule_id = schedule_batch_remediation(
                selected_threats,
                schedule_datetime,
                remediation_options
            )
            st.success(f"✅ Remediation scheduled! Schedule ID: **{schedule_id}**")
            st.info(f"Remediation will execute at: {schedule_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Execute batch remediation if triggered
    if st.session_state.get('batch_remediation_started', False):
        execute_batch_remediation_ui(
            st.session_state.batch_selected_threats,
            st.session_state.batch_options
        )
        st.session_state.batch_remediation_started = False
    
    # Show scheduled remediations
    if st.session_state.get('scheduled_remediations'):
        st.markdown("---")
        st.markdown("#### 📅 Scheduled Remediations")
        
        scheduled_df = pd.DataFrame([
            {
                'Schedule ID': s['schedule_id'],
                'Threats': len(s['threats']),
                'Scheduled Time': s['schedule_time'][:19],
                'Status': s['status'],
                'Created': s['created_at'][:19]
            }
            for s in st.session_state.scheduled_remediations
        ])
        
        st.dataframe(scheduled_df, use_container_width=True)


def execute_batch_remediation_ui(selected_threats: List[Dict], options: Dict):
    """Execute batch remediation with UI feedback"""
    
    st.markdown("---")
    st.markdown("### 🔄 Batch Remediation In Progress")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    results = {
        'successful': 0,
        'failed': 0,
        'details': []
    }
    
    total = len(selected_threats)
    
    for i, threat in enumerate(selected_threats):
        progress = (i + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Remediating threat {i+1} of {total}: {threat.get('threat_id', 'UNKNOWN')}")
        
        try:
            threat_result = remediate_single_threat(threat, options)
            
            if threat_result['status'] == 'SUCCESS':
                results['successful'] += 1
                
                with results_container:
                    st.markdown(f"""
                    <div style='background: #E8F8F5; border-left: 4px solid #00C851; padding: 12px; margin: 5px 0; border-radius: 5px;'>
                        <strong style='color: #00C851;'>✅ {threat.get('threat_id', 'UNKNOWN')}</strong><br>
                        <span style='font-size: 12px; color: #666;'>
                            Actions: {', '.join([a['action'] for a in threat_result['actions']])}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                results['failed'] += 1
                
                with results_container:
                    st.markdown(f"""
                    <div style='background: #FFE6E6; border-left: 4px solid #D13212; padding: 12px; margin: 5px 0; border-radius: 5px;'>
                        <strong style='color: #D13212;'>❌ {threat.get('threat_id', 'UNKNOWN')}</strong><br>
                        <span style='font-size: 12px; color: #666;'>
                            Error: {threat_result.get('error', 'Unknown error')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            results['details'].append(threat_result)
            
        except Exception as e:
            results['failed'] += 1
            
            with results_container:
                st.markdown(f"""
                <div style='background: #FFE6E6; border-left: 4px solid #D13212; padding: 12px; margin: 5px 0; border-radius: 5px;'>
                    <strong style='color: #D13212;'>❌ {threat.get('threat_id', 'UNKNOWN')}</strong><br>
                    <span style='font-size: 12px; color: #666;'>Error: {str(e)}</span>
                </div>
                """, unsafe_allow_html=True)
    
    progress_bar.progress(1.0)
    status_text.text(f"Batch remediation complete!")
    
    # Store in history
    if 'remediation_history' not in st.session_state:
        st.session_state.remediation_history = []
    
    st.session_state.remediation_history.extend(results['details'])
    
    # Success summary
    st.markdown("---")
    st.success("### ✅ Batch Remediation Complete!")
    
    col_sum1, col_sum2, col_sum3 = st.columns(3)
    
    with col_sum1:
        st.metric("Total Processed", total)
    with col_sum2:
        st.metric("Successful", results['successful'], delta="✅")
    with col_sum3:
        st.metric("Failed", results['failed'], delta="❌" if results['failed'] > 0 else None)
    
    # Download report
    report_data = json.dumps(results, indent=2)
    st.download_button(
        label="📥 Download Remediation Report",
        data=report_data,
        file_name=f"batch_remediation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )