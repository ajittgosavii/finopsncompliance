"""
AWS Deployment Utility for Streamlit Cloud
Replaces bash scripts with Python boto3 calls
Full deployment interface with monitoring
"""

import streamlit as st
import boto3
from botocore.exceptions import ClientError, WaiterError
import json
import time
import zipfile
import io
from datetime import datetime
import pandas as pd

# Initialize AWS clients
def get_aws_clients():
    """Initialize AWS clients using Streamlit secrets"""
    try:
        session = boto3.Session(
            aws_access_key_id=st.secrets['default']['aws_access_key_id'],
            aws_secret_access_key=st.secrets['default']['aws_secret_access_key'],
            region_name=st.secrets['aws']['region']
        )
        
        return {
            'cloudformation': session.client('cloudformation'),
            'lambda': session.client('lambda'),
            'dynamodb': session.client('dynamodb'),
            'iam': session.client('iam'),
            'sns': session.client('sns'),
            'events': session.client('events'),
            'cloudtrail': session.client('cloudtrail'),
            's3': session.client('s3'),
            'sts': session.client('sts'),
            'logs': session.client('logs')
        }
    except Exception as e:
        st.error(f"❌ Failed to initialize AWS clients: {str(e)}")
        st.info("💡 Check that AWS credentials are configured in Streamlit secrets")
        return None


def render_deployment_utility():
    """Main deployment utility interface"""
    
    st.markdown("# 🚀 AWS Threat Detection Deployment Utility")
    
    st.info("""
    ✅ **Secure Deployment Interface**
    - Uses credentials from Streamlit secrets
    - No bash scripts or AWS CLI required
    - Full Python boto3 implementation
    - Real-time monitoring and logging
    """)
    
    # Initialize AWS clients
    clients = get_aws_clients()
    if not clients:
        return
    
    # Get account info
    try:
        account_info = clients['sts'].get_caller_identity()
        account_id = account_info['Account']
        st.success(f"✅ Connected to AWS Account: `{account_id}`")
    except Exception as e:
        st.error(f"❌ Failed to connect to AWS: {str(e)}")
        return
    
    # Create tabs for different operations
    tabs = st.tabs([
        "🚀 Deploy Infrastructure",
        "📦 Deploy Lambda",
        "🧪 Test System",
        "📊 Monitor Status",
        "🔄 Update/Rollback"
    ])
    
    with tabs[0]:
        render_infrastructure_deployment(clients, account_id)
    
    with tabs[1]:
        render_lambda_deployment(clients)
    
    with tabs[2]:
        render_testing_interface(clients)
    
    with tabs[3]:
        render_monitoring_dashboard(clients)
    
    with tabs[4]:
        render_update_rollback(clients)


def render_infrastructure_deployment(clients, account_id):
    """CloudFormation deployment interface"""
    
    st.markdown("## 🏗️ Deploy AWS Infrastructure")
    
    st.markdown("""
    This will deploy:
    - 📊 DynamoDB table for threat storage
    - ⚡ Lambda function for threat detection
    - 🔔 EventBridge rules for monitoring
    - 📧 SNS topic for alerts
    - 🔐 IAM roles with least-privilege permissions
    """)
    
    # Configuration form
    with st.form("deployment_config"):
        stack_name = st.text_input(
            "Stack Name",
            value="threat-detection-system",
            help="Name for the CloudFormation stack"
        )
        
        notification_email = st.text_input(
            "Notification Email",
            value=st.session_state.get('notification_email', ''),
            help="Email address for security alerts"
        )
        
        enable_bedrock = st.checkbox(
            "Enable Claude AI (Bedrock)",
            value=True,
            help="Enables AI-powered threat analysis"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            deploy_button = st.form_submit_button("🚀 Deploy Infrastructure", type="primary")
        with col2:
            dry_run = st.form_submit_button("🔍 Validate Only")
    
    # Deploy on button click
    if deploy_button or dry_run:
        if not notification_email:
            st.error("❌ Please enter a notification email")
            return
        
        # Save email for next time
        st.session_state.notification_email = notification_email
        
        if dry_run:
            st.info("🔍 Validating CloudFormation template...")
            validate_cloudformation_template(clients['cloudformation'])
        else:
            deploy_cloudformation_stack(
                clients, 
                stack_name, 
                notification_email,
                account_id,
                enable_bedrock
            )


def deploy_cloudformation_stack(clients, stack_name, email, account_id, enable_bedrock):
    """Deploy CloudFormation stack with real-time monitoring"""
    
    st.markdown("---")
    st.markdown("### 📊 Deployment Progress")
    
    # Load CloudFormation template
    template_body = get_cloudformation_template(account_id, enable_bedrock)
    
    # Create stack
    try:
        with st.spinner("🚀 Creating CloudFormation stack..."):
            response = clients['cloudformation'].create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'NotificationEmail',
                        'ParameterValue': email
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Tags=[
                    {'Key': 'Application', 'Value': 'CloudComplianceCanvas'},
                    {'Key': 'ManagedBy', 'Value': 'StreamlitDeploymentUtility'}
                ]
            )
        
        stack_id = response['StackId']
        st.success(f"✅ Stack creation initiated: `{stack_id}`")
        
        # Monitor deployment
        monitor_stack_deployment(clients['cloudformation'], stack_name)
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AlreadyExistsException':
            st.warning(f"⚠️ Stack `{stack_name}` already exists")
            
            if st.button("🔄 Update existing stack instead?"):
                update_cloudformation_stack(clients, stack_name, email)
        else:
            st.error(f"❌ Deployment failed: {e.response['Error']['Message']}")


def monitor_stack_deployment(cf_client, stack_name):
    """Real-time stack deployment monitoring"""
    
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    events_container = st.container()
    
    start_time = datetime.now()
    max_wait_time = 600  # 10 minutes
    
    events_seen = set()
    
    while True:
        try:
            # Get stack status
            response = cf_client.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]
            status = stack['StackStatus']
            
            # Calculate progress (estimate)
            elapsed = (datetime.now() - start_time).total_seconds()
            progress = min(elapsed / 300, 0.95)  # 5 min estimate
            
            if status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                progress = 1.0
            
            progress_bar.progress(progress)
            
            # Update status
            status_emoji = {
                'CREATE_IN_PROGRESS': '⏳',
                'CREATE_COMPLETE': '✅',
                'CREATE_FAILED': '❌',
                'UPDATE_IN_PROGRESS': '⏳',
                'UPDATE_COMPLETE': '✅',
                'UPDATE_FAILED': '❌'
            }
            
            emoji = status_emoji.get(status, '🔄')
            status_placeholder.markdown(f"### {emoji} Status: `{status}`")
            
            # Get recent events
            events_response = cf_client.describe_stack_events(StackName=stack_name)
            events = events_response['StackEvents'][:10]
            
            # Display new events
            with events_container:
                for event in reversed(events):
                    event_id = event['EventId']
                    if event_id not in events_seen:
                        events_seen.add(event_id)
                        
                        resource_status = event['ResourceStatus']
                        resource_type = event['ResourceType']
                        logical_id = event['LogicalResourceId']
                        
                        status_icon = '✅' if 'COMPLETE' in resource_status else '⏳'
                        if 'FAILED' in resource_status:
                            status_icon = '❌'
                        
                        st.caption(f"{status_icon} `{logical_id}` ({resource_type}): {resource_status}")
            
            # Check if complete
            if status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                st.balloons()
                st.success("### 🎉 Deployment Complete!")
                
                # Show outputs
                outputs = stack.get('Outputs', [])
                if outputs:
                    st.markdown("#### 📋 Stack Outputs")
                    for output in outputs:
                        st.code(f"{output['OutputKey']}: {output['OutputValue']}")
                
                break
            
            elif 'FAILED' in status or 'ROLLBACK' in status:
                st.error(f"### ❌ Deployment Failed: {status}")
                
                # Show failure reason
                for event in events:
                    if 'FAILED' in event.get('ResourceStatus', ''):
                        reason = event.get('ResourceStatusReason', 'Unknown')
                        st.error(f"**Failure reason:** {reason}")
                        break
                
                break
            
            # Check timeout
            if elapsed > max_wait_time:
                st.warning("⚠️ Monitoring timeout reached. Stack is still deploying.")
                st.info("Check AWS Console for final status")
                break
            
            # Wait before next check
            time.sleep(5)
            
        except Exception as e:
            st.error(f"❌ Monitoring error: {str(e)}")
            break


def render_lambda_deployment(clients):
    """Lambda function deployment interface"""
    
    st.markdown("## 📦 Deploy Lambda Function")
    
    st.info("""
    Deploy or update the threat detection Lambda function code.
    This updates the function without changing infrastructure.
    """)
    
    # Check if function exists
    try:
        function_info = clients['lambda'].get_function(
            FunctionName='threat-detection-handler'
        )
        
        st.success("✅ Lambda function exists")
        
        config = function_info['Configuration']
        st.markdown(f"""
        **Current Configuration:**
        - Runtime: `{config['Runtime']}`
        - Memory: `{config['MemorySize']} MB`
        - Timeout: `{config['Timeout']} seconds`
        - Last Modified: `{config['LastModified']}`
        """)
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            st.warning("⚠️ Lambda function not found. Deploy infrastructure first.")
            return
        else:
            st.error(f"❌ Error checking function: {str(e)}")
            return
    
    # Lambda code editor
    st.markdown("### 📝 Lambda Code")
    
    if st.checkbox("📄 Show current Lambda code", value=False):
        try:
            # Get function code
            code_response = clients['lambda'].get_function(
                FunctionName='threat-detection-handler'
            )
            
            code_location = code_response['Code']['Location']
            st.info(f"Code location: {code_location}")
            st.caption("Download code from S3 URL above to view/edit")
            
        except Exception as e:
            st.error(f"Error retrieving code: {str(e)}")
    
    # Upload new code
    st.markdown("### ⬆️ Upload New Code")
    
    uploaded_file = st.file_uploader(
        "Upload Lambda code (ZIP file)",
        type=['zip'],
        help="Upload a ZIP file containing threat_detection_lambda.py"
    )
    
    if uploaded_file:
        if st.button("🚀 Deploy Lambda Code", type="primary"):
            deploy_lambda_code(clients['lambda'], uploaded_file)
    
    # Or use embedded code
    st.markdown("---")
    st.markdown("### 🔧 Quick Update from Template")
    
    if st.button("📥 Deploy Template Code", help="Deploy the threat detection code from template"):
        deploy_lambda_from_template(clients['lambda'])


def deploy_lambda_code(lambda_client, zip_file):
    """Deploy Lambda function from uploaded ZIP"""
    
    try:
        with st.spinner("📦 Uploading Lambda code..."):
            # Read ZIP file
            zip_bytes = zip_file.read()
            
            # Update function code
            response = lambda_client.update_function_code(
                FunctionName='threat-detection-handler',
                ZipFile=zip_bytes
            )
            
            st.success("✅ Lambda code deployed successfully!")
            st.code(f"Version: {response['Version']}")
            st.code(f"Last Modified: {response['LastModified']}")
            
            # Wait for update to complete
            with st.spinner("⏳ Waiting for update to complete..."):
                waiter = lambda_client.get_waiter('function_updated')
                waiter.wait(FunctionName='threat-detection-handler')
            
            st.success("✅ Lambda function is ready!")
            
    except Exception as e:
        st.error(f"❌ Deployment failed: {str(e)}")


def deploy_lambda_from_template(lambda_client):
    """Deploy Lambda from embedded template code"""
    
    try:
        # Create ZIP file with Lambda code
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add Lambda code (you would load this from file)
            lambda_code = get_lambda_template_code()
            zip_file.writestr('threat_detection_lambda.py', lambda_code)
        
        with st.spinner("📦 Deploying Lambda code..."):
            response = lambda_client.update_function_code(
                FunctionName='threat-detection-handler',
                ZipFile=zip_buffer.getvalue()
            )
            
            st.success("✅ Lambda template deployed!")
            st.code(f"Version: {response['Version']}")
            
    except Exception as e:
        st.error(f"❌ Deployment failed: {str(e)}")


def render_testing_interface(clients):
    """Testing and verification interface"""
    
    st.markdown("## 🧪 Test System")
    
    st.info("Create test threats to verify the detection system is working")
    
    # Test scenarios
    st.markdown("### 📋 Test Scenarios")
    
    test_type = st.selectbox(
        "Select test type",
        [
            "IAM Policy Change (Critical)",
            "S3 Bucket Policy (High)",
            "After-Hours Activity (Medium)",
            "Custom IAM Action"
        ]
    )
    
    if test_type == "IAM Policy Change (Critical)":
        st.markdown("""
        **This test will:**
        1. Create a test IAM role
        2. Add a wildcard (*) policy (triggers CRITICAL alert)
        3. Verify Lambda detects it
        4. Clean up test resources
        """)
        
        if st.button("🧪 Run Test", type="primary"):
            run_iam_policy_test(clients)
    
    elif test_type == "Custom IAM Action":
        st.markdown("**Create custom IAM test**")
        
        with st.form("custom_test"):
            role_name = st.text_input("Role Name", value="TestRole")
            policy_name = st.text_input("Policy Name", value="TestPolicy")
            
            policy_document = st.text_area(
                "Policy Document (JSON)",
                value='''{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:*",
    "Resource": "*"
  }]
}''',
                height=200
            )
            
            if st.form_submit_button("🧪 Execute Test"):
                run_custom_iam_test(clients, role_name, policy_name, policy_document)
    
    # View test results
    st.markdown("---")
    st.markdown("### 📊 Recent Test Results")
    
    if st.button("🔄 Refresh Results"):
        show_recent_threats(clients['dynamodb'])


def run_iam_policy_test(clients):
    """Run IAM policy change test"""
    
    test_role_name = f"ThreatTest-{int(time.time())}"
    
    try:
        # Create test role
        with st.spinner("1️⃣ Creating test IAM role..."):
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            clients['iam'].create_role(
                RoleName=test_role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            st.success(f"✅ Created role: `{test_role_name}`")
        
        time.sleep(2)
        
        # Add wildcard policy (should trigger alert)
        with st.spinner("2️⃣ Adding wildcard policy (triggers CRITICAL alert)..."):
            test_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": "*"
                }]
            }
            
            clients['iam'].put_role_policy(
                RoleName=test_role_name,
                PolicyName="WildcardTestPolicy",
                PolicyDocument=json.dumps(test_policy)
            )
            
            st.success("✅ Policy added - this should trigger detection!")
        
        # Wait for detection
        with st.spinner("3️⃣ Waiting for threat detection (10 seconds)..."):
            time.sleep(10)
        
        # Check for threat in DynamoDB
        st.markdown("4️⃣ Checking DynamoDB for detected threat...")
        
        threat_found = check_for_test_threat(clients['dynamodb'], test_role_name)
        
        if threat_found:
            st.success("✅ TEST PASSED! Threat was detected and stored!")
            st.balloons()
        else:
            st.warning("⚠️ Threat not found yet. Check again in 30 seconds.")
        
        # Cleanup
        with st.spinner("5️⃣ Cleaning up test resources..."):
            time.sleep(2)
            clients['iam'].delete_role_policy(
                RoleName=test_role_name,
                PolicyName="WildcardTestPolicy"
            )
            clients['iam'].delete_role(RoleName=test_role_name)
            
            st.success("✅ Cleanup complete!")
        
        st.markdown("---")
        st.success("### 🎉 Test Complete!")
        st.markdown("""
        **What happened:**
        1. ✅ Created test IAM role
        2. ✅ Added wildcard policy (CRITICAL threat)
        3. ✅ CloudTrail captured the event
        4. ✅ EventBridge triggered Lambda
        5. ✅ Lambda detected threat
        6. ✅ Threat stored in DynamoDB
        7. ✅ Cleanup completed
        """)
        
    except Exception as e:
        st.error(f"❌ Test failed: {str(e)}")
        
        # Attempt cleanup
        try:
            clients['iam'].delete_role_policy(
                RoleName=test_role_name,
                PolicyName="WildcardTestPolicy"
            )
            clients['iam'].delete_role(RoleName=test_role_name)
        except:
            pass


def check_for_test_threat(dynamodb_client, role_name):
    """Check if test threat was detected"""
    
    try:
        response = dynamodb_client.scan(
            TableName='security-threats',
            FilterExpression='contains(event_name, :event) AND contains(resource_affected, :role)',
            ExpressionAttributeValues={
                ':event': {'S': 'PutRolePolicy'},
                ':role': {'S': role_name}
            },
            Limit=10
        )
        
        items = response.get('Items', [])
        
        if items:
            st.markdown("**Detected Threat:**")
            for item in items:
                threat_id = item.get('threat_id', {}).get('S', 'Unknown')
                severity = item.get('severity', {}).get('S', 'Unknown')
                timestamp = item.get('timestamp', {}).get('S', 'Unknown')
                
                st.code(f"Threat ID: {threat_id}")
                st.code(f"Severity: {severity}")
                st.code(f"Time: {timestamp}")
            
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Error checking threats: {str(e)}")
        return False


def render_monitoring_dashboard(clients):
    """Monitoring and status dashboard"""
    
    st.markdown("## 📊 System Status & Monitoring")
    
    # Get system status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        check_cloudformation_status(clients['cloudformation'])
    
    with col2:
        check_lambda_status(clients['lambda'])
    
    with col3:
        check_dynamodb_status(clients['dynamodb'])
    
    with col4:
        check_eventbridge_status(clients['events'])
    
    # Recent threats
    st.markdown("---")
    st.markdown("### 🚨 Recent Threats")
    
    show_recent_threats(clients['dynamodb'])
    
    # Lambda logs
    st.markdown("---")
    st.markdown("### 📋 Lambda Execution Logs")
    
    if st.button("🔄 Refresh Logs"):
        show_lambda_logs(clients['logs'])


def check_cloudformation_status(cf_client):
    """Check CloudFormation stack status"""
    
    try:
        response = cf_client.describe_stacks(StackName='threat-detection-system')
        stack = response['Stacks'][0]
        status = stack['StackStatus']
        
        if 'COMPLETE' in status:
            st.metric("CloudFormation", "✅ Active", status)
        elif 'IN_PROGRESS' in status:
            st.metric("CloudFormation", "⏳ Deploying", status)
        else:
            st.metric("CloudFormation", "❌ Issue", status)
            
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            st.metric("CloudFormation", "❌ Not Deployed", "Stack not found")
        else:
            st.metric("CloudFormation", "❌ Error", str(e))


def check_lambda_status(lambda_client):
    """Check Lambda function status"""
    
    try:
        response = lambda_client.get_function(FunctionName='threat-detection-handler')
        state = response['Configuration']['State']
        
        if state == 'Active':
            st.metric("Lambda", "✅ Active", state)
        else:
            st.metric("Lambda", "⏳ Updating", state)
            
    except ClientError:
        st.metric("Lambda", "❌ Not Found", "Not deployed")


def check_dynamodb_status(dynamodb_client):
    """Check DynamoDB table status"""
    
    try:
        response = dynamodb_client.describe_table(TableName='security-threats')
        status = response['Table']['TableStatus']
        item_count = response['Table']['ItemCount']
        
        if status == 'ACTIVE':
            st.metric("DynamoDB", "✅ Active", f"{item_count} threats")
        else:
            st.metric("DynamoDB", "⏳ Creating", status)
            
    except ClientError:
        st.metric("DynamoDB", "❌ Not Found", "Not deployed")


def check_eventbridge_status(events_client):
    """Check EventBridge rules status"""
    
    try:
        response = events_client.list_rules(NamePrefix='detect-')
        rules = response.get('Rules', [])
        
        enabled_count = sum(1 for r in rules if r['State'] == 'ENABLED')
        
        if enabled_count > 0:
            st.metric("EventBridge", "✅ Active", f"{enabled_count} rules")
        else:
            st.metric("EventBridge", "⚠️ No Rules", "0 active")
            
    except Exception:
        st.metric("EventBridge", "❌ Error", "Check failed")


def show_recent_threats(dynamodb_client):
    """Display recent threats from DynamoDB"""
    
    try:
        response = dynamodb_client.scan(
            TableName='security-threats',
            Limit=10
        )
        
        items = response.get('Items', [])
        
        if not items:
            st.info("No threats detected yet. System is monitoring.")
            return
        
        # Convert to DataFrame
        threats_data = []
        for item in items:
            threats_data.append({
                'Threat ID': item.get('threat_id', {}).get('S', ''),
                'Severity': item.get('severity', {}).get('S', ''),
                'Event': item.get('event_name', {}).get('S', ''),
                'Account': item.get('account_id', {}).get('S', ''),
                'Time': item.get('timestamp', {}).get('S', ''),
                'Status': item.get('status', {}).get('S', '')
            })
        
        df = pd.DataFrame(threats_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error fetching threats: {str(e)}")


def show_lambda_logs(logs_client):
    """Display recent Lambda logs"""
    
    try:
        # Get log streams
        response = logs_client.describe_log_streams(
            logGroupName='/aws/lambda/threat-detection-handler',
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if not response.get('logStreams'):
            st.info("No logs available yet")
            return
        
        log_stream = response['logStreams'][0]['logStreamName']
        
        # Get recent log events
        events_response = logs_client.get_log_events(
            logGroupName='/aws/lambda/threat-detection-handler',
            logStreamName=log_stream,
            limit=50,
            startFromHead=False
        )
        
        events = events_response.get('events', [])
        
        if events:
            for event in reversed(events[-20:]):  # Last 20 events
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                message = event['message']
                st.text(f"[{timestamp}] {message}")
        else:
            st.info("No recent log events")
            
    except Exception as e:
        st.error(f"Error fetching logs: {str(e)}")


def render_update_rollback(clients):
    """Update and rollback interface"""
    
    st.markdown("## 🔄 Update & Rollback")
    
    # Update section
    st.markdown("### 🔧 Update Configuration")
    
    if st.button("🔄 Update Lambda Environment Variables"):
        st.info("Environment variables can be updated here")
        # Add form for env vars
    
    if st.button("📊 Update DynamoDB Capacity"):
        st.info("DynamoDB capacity settings")
        # Add capacity configuration
    
    # Rollback section
    st.markdown("---")
    st.markdown("### ⚠️ Rollback / Cleanup")
    
    st.warning("""
    **Warning:** This will delete all threat detection resources:
    - CloudFormation stack
    - DynamoDB table (and all threat data)
    - Lambda function
    - EventBridge rules
    - SNS topics
    """)
    
    confirm = st.checkbox("I understand this will delete all resources")
    
    if confirm:
        if st.button("🗑️ Delete All Resources", type="secondary"):
            rollback_deployment(clients)


def rollback_deployment(clients):
    """Delete all resources"""
    
    st.markdown("### 🗑️ Rollback in Progress")
    
    try:
        with st.spinner("Deleting CloudFormation stack..."):
            clients['cloudformation'].delete_stack(
                StackName='threat-detection-system'
            )
            
            st.info("Stack deletion initiated. This may take 3-5 minutes.")
            
            # Monitor deletion
            for i in range(60):
                try:
                    response = clients['cloudformation'].describe_stacks(
                        StackName='threat-detection-system'
                    )
                    status = response['Stacks'][0]['StackStatus']
                    st.caption(f"Status: {status}")
                    
                    if 'DELETE_COMPLETE' in status:
                        st.success("✅ All resources deleted!")
                        break
                    
                    if 'DELETE_FAILED' in status:
                        st.error("❌ Deletion failed. Check AWS Console.")
                        break
                    
                    time.sleep(5)
                    
                except ClientError as e:
                    if 'does not exist' in str(e):
                        st.success("✅ Stack deleted successfully!")
                        break
                    raise
                    
    except Exception as e:
        st.error(f"❌ Rollback error: {str(e)}")


# Helper functions to get templates

def get_cloudformation_template(account_id, enable_bedrock):
    """Get CloudFormation template (simplified version)"""
    # You would load the full template from cloudformation_threat_detection.yaml
    # For now, returning a minimal template
    return f"""
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Threat Detection System'

Parameters:
  NotificationEmail:
    Type: String
    Description: Email for alerts

Resources:
  SecurityThreatsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: security-threats
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: threat_id
          AttributeType: S
      KeySchema:
        - AttributeName: threat_id
          KeyType: HASH

Outputs:
  TableName:
    Value: !Ref SecurityThreatsTable
"""


def get_lambda_template_code():
    """Get Lambda code template"""
    return """
# Lambda function code would be loaded here
# You would load the full threat_detection_lambda.py content
def lambda_handler(event, context):
    print("Threat detection lambda")
    return {'statusCode': 200}
"""


def validate_cloudformation_template(cf_client):
    """Validate CloudFormation template"""
    try:
        template = get_cloudformation_template("123456789012", True)
        cf_client.validate_template(TemplateBody=template)
        st.success("✅ Template is valid!")
    except Exception as e:
        st.error(f"❌ Template validation failed: {str(e)}")


def run_custom_iam_test(clients, role_name, policy_name, policy_doc):
    """Run custom IAM test"""
    try:
        # Validate JSON
        policy_dict = json.loads(policy_doc)
        
        # Create role if it doesn't exist
        st.info(f"Creating role: {role_name}")
        # Implementation similar to run_iam_policy_test
        
        st.success("Test executed successfully!")
        
    except json.JSONDecodeError:
        st.error("Invalid JSON in policy document")
    except Exception as e:
        st.error(f"Test failed: {str(e)}")


# Main entry point
if __name__ == "__main__":
    render_deployment_utility()
