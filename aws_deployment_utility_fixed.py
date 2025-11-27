"""
AWS Deployment Utility for Streamlit Cloud - Fixed Version
Only renders when explicitly called, no automatic errors
"""

import streamlit as st
import boto3
from botocore.exceptions import ClientError
import json
import time

def render_deployment_utility():
    """
    Main deployment utility interface
    Call this only when user wants to see deployment options
    """
    
    st.markdown("## 🚀 AWS Threat Detection Deployment")
    
    # Check if secrets are configured
    if not check_secrets_configured():
        show_secrets_setup_guide()
        return
    
    # Try to initialize AWS clients
    clients = try_get_aws_clients()
    if not clients:
        return
    
    # Show deployment interface
    show_deployment_interface(clients)


def check_secrets_configured():
    """Quietly check if secrets exist without showing errors"""
    try:
        has_aws = 'aws' in st.secrets
        has_default = 'default' in st.secrets
        return has_aws and has_default
    except:
        return False


def show_secrets_setup_guide():
    """Show setup guide only when user is on deployment page"""
    
    st.warning("⚠️ AWS credentials not configured yet")
    
    with st.expander("📖 How to Configure AWS Credentials", expanded=True):
        st.markdown("""
        ### Step 1: Create AWS IAM User (if not done)
```bash
        # On your local machine with AWS CLI
        aws iam create-user --user-name streamlit-deployer
        
        aws iam attach-user-policy \
            --user-name streamlit-deployer \
            --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
        
        aws iam create-access-key --user-name streamlit-deployer
        # Save the Access Key ID and Secret Access Key
```
        
        ### Step 2: Add to Streamlit Cloud
        
        1. Go to your app dashboard
        2. Click **Settings** → **Secrets**
        3. Add this configuration:
```toml
        [aws]
        region = "us-east-1"
        threats_table = "security-threats"
        
        [default]
        aws_access_key_id = "AKIA..."
        aws_secret_access_key = "..."
```
        
        4. Click **Save**
        5. Refresh this page
        """)
        
        st.info("💡 **Note:** The app will work normally without these credentials. This utility is only needed for AWS deployment.")


def try_get_aws_clients():
    """Try to initialize AWS clients with proper error handling"""
    try:
        session = boto3.Session(
            aws_access_key_id=st.secrets['default']['aws_access_key_id'],
            aws_secret_access_key=st.secrets['default']['aws_secret_access_key'],
            region_name=st.secrets['aws'].get('region', 'us-east-1')
        )
        
        # Test connection
        sts = session.client('sts')
        account = sts.get_caller_identity()
        
        st.success(f"✅ Connected to AWS Account: `{account['Account']}`")
        
        return {
            'cloudformation': session.client('cloudformation'),
            'lambda': session.client('lambda'),
            'dynamodb': session.client('dynamodb'),
            'iam': session.client('iam'),
            'sns': session.client('sns'),
            'events': session.client('events'),
            'logs': session.client('logs'),
            'sts': sts
        }
        
    except KeyError as e:
        st.error(f"❌ Missing secret key: {str(e)}")
        st.info("Check Streamlit secrets configuration above")
        return None
    except ClientError as e:
        st.error(f"❌ AWS connection failed: {e.response['Error']['Message']}")
        st.info("Verify your AWS credentials are correct")
        return None
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        return None
def show_deployment_interface(clients):
    """Show the deployment interface tabs"""
    
    st.markdown("---")
    
    # Create tabs
    tabs = st.tabs([
        "🚀 Deploy",
        "📊 Status",
        "🧪 Test",
        "📋 Logs"
    ])
    
    with tabs[0]:
        show_deploy_tab(clients)
    
    with tabs[1]:
        show_status_tab(clients)
    
    with tabs[2]:
        show_test_tab(clients)
    
    with tabs[3]:
        show_logs_tab(clients)


def show_deploy_tab(clients):
    """Deployment tab"""
    
    st.markdown("### 🏗️ Deploy AWS Infrastructure")
    
    # Check if already deployed
    stack_exists = check_stack_exists(clients['cloudformation'])
    
    if stack_exists:
        st.success("✅ Infrastructure already deployed")
        st.info("Use the Status tab to monitor, or Test tab to verify")
        
        if st.button("🔄 Update Stack"):
            st.info("Update functionality - coming soon")
        
    else:
        st.info("No infrastructure found. Deploy now to start threat detection.")
        
        with st.form("deploy_form"):
            email = st.text_input(
                "Notification Email",
                help="Email for security alerts"
            )
            
            deploy = st.form_submit_button("🚀 Deploy Infrastructure", type="primary")
            
        if deploy:
            if email:
                deploy_infrastructure(clients, email)
            else:
                st.error("Please enter notification email")


def check_stack_exists(cf_client):
    """Check if CloudFormation stack exists"""
    try:
        cf_client.describe_stacks(StackName='threat-detection-system')
        return True
    except:
        return False


def deploy_infrastructure(clients, email):
    """Deploy infrastructure"""
    
    st.markdown("### 🚀 Deploying...")
    
    # Simple template
    template = create_minimal_template()
    
    try:
        with st.spinner("Creating CloudFormation stack..."):
            response = clients['cloudformation'].create_stack(
                StackName='threat-detection-system',
                TemplateBody=json.dumps(template),
                Parameters=[
                    {'ParameterKey': 'NotificationEmail', 'ParameterValue': email}
                ],
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
        
        st.success(f"✅ Deployment started!")
        
        # Monitor progress
        monitor_deployment(clients['cloudformation'])
        
    except ClientError as e:
        st.error(f"❌ Deployment failed: {e.response['Error']['Message']}")


def monitor_deployment(cf_client):
    """Monitor deployment progress"""
    
    progress = st.progress(0)
    status_text = st.empty()
    
    for i in range(60):
        try:
            response = cf_client.describe_stacks(StackName='threat-detection-system')
            status = response['Stacks'][0]['StackStatus']
            
            status_text.info(f"Status: {status}")
            progress.progress(min((i + 1) / 60, 0.95))
            
            if 'COMPLETE' in status:
                progress.progress(1.0)
                st.balloons()
                st.success("🎉 Deployment complete!")
                
                outputs = response['Stacks'][0].get('Outputs', [])
                if outputs:
                    st.markdown("**Outputs:**")
                    for output in outputs:
                        st.code(f"{output['OutputKey']}: {output['OutputValue']}")
                break
            
            if 'FAILED' in status:
                st.error(f"❌ Deployment failed")
                break
            
            time.sleep(5)
        except:
            break
def show_status_tab(clients):
    """Status monitoring tab"""
    
    st.markdown("### 📊 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        check_cf_status(clients['cloudformation'])
    
    with col2:
        check_lambda_status(clients['lambda'])
    
    with col3:
        check_dynamodb_status(clients['dynamodb'])


def check_cf_status(cf_client):
    """Check CloudFormation status"""
    try:
        response = cf_client.describe_stacks(StackName='threat-detection-system')
        status = response['Stacks'][0]['StackStatus']
        
        if 'COMPLETE' in status:
            st.metric("CloudFormation", "✅ Active", status)
        else:
            st.metric("CloudFormation", "⏳ Deploying", status)
    except:
        st.metric("CloudFormation", "❌ Not Found", "Not deployed")


def check_lambda_status(lambda_client):
    """Check Lambda status"""
    try:
        response = lambda_client.get_function(FunctionName='threat-detection-handler')
        state = response['Configuration']['State']
        
        if state == 'Active':
            st.metric("Lambda", "✅ Active", state)
        else:
            st.metric("Lambda", "⏳ Updating", state)
    except:
        st.metric("Lambda", "❌ Not Found", "Not deployed")


def check_dynamodb_status(dynamodb_client):
    """Check DynamoDB status"""
    try:
        response = dynamodb_client.describe_table(TableName='security-threats')
        count = response['Table']['ItemCount']
        st.metric("DynamoDB", "✅ Active", f"{count} threats")
    except:
        st.metric("DynamoDB", "❌ Not Found", "Not deployed")


def show_test_tab(clients):
    """Testing tab"""
    
    st.markdown("### 🧪 Test Threat Detection")
    
    st.info("Create a test threat to verify the system is working")
    
    if st.button("🧪 Run Quick Test", type="primary"):
        run_quick_test(clients)


def run_quick_test(clients):
    """Run quick test"""
    
    test_role = f"ThreatTest-{int(time.time())}"
    
    try:
        with st.spinner("Creating test role..."):
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            clients['iam'].create_role(
                RoleName=test_role,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            st.success(f"✅ Created: {test_role}")
        
        with st.spinner("Adding test policy..."):
            time.sleep(2)
            
            policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": "*"
                }]
            }
            
            clients['iam'].put_role_policy(
                RoleName=test_role,
                PolicyName="WildcardTest",
                PolicyDocument=json.dumps(policy)
            )
            st.success("✅ Policy added - should trigger detection!")
        
        with st.spinner("Waiting for detection (10 sec)..."):
            time.sleep(10)
        
        # Check for threat
        try:
            response = clients['dynamodb'].scan(
                TableName='security-threats',
                FilterExpression='contains(resource_affected, :role)',
                ExpressionAttributeValues={':role': {'S': test_role}},
                Limit=5
            )
            
            if response.get('Items'):
                st.success("✅ TEST PASSED! Threat detected!")
                st.balloons()
            else:
                st.warning("⚠️ Threat not detected yet. Check again in 30 seconds.")
        except:
            st.warning("⚠️ Could not check DynamoDB. Table may not exist yet.")
        
        # Cleanup
        with st.spinner("Cleaning up..."):
            time.sleep(2)
            clients['iam'].delete_role_policy(RoleName=test_role, PolicyName="WildcardTest")
            clients['iam'].delete_role(RoleName=test_role)
            st.success("✅ Cleanup complete!")
        
    except Exception as e:
        st.error(f"❌ Test failed: {str(e)}")
def show_logs_tab(clients):
    """Logs tab"""
    
    st.markdown("### 📋 Lambda Logs")
    
    if st.button("🔄 Refresh Logs"):
        show_lambda_logs(clients['logs'])


def show_lambda_logs(logs_client):
    """Show Lambda logs"""
    try:
        response = logs_client.describe_log_streams(
            logGroupName='/aws/lambda/threat-detection-handler',
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if not response.get('logStreams'):
            st.info("No logs available yet")
            return
        
        stream = response['logStreams'][0]['logStreamName']
        
        events_response = logs_client.get_log_events(
            logGroupName='/aws/lambda/threat-detection-handler',
            logStreamName=stream,
            limit=20,
            startFromHead=False
        )
        
        events = events_response.get('events', [])
        
        if events:
            for event in reversed(events[-10:]):
                st.text(event['message'])
        else:
            st.info("No recent events")
            
    except Exception as e:
        st.error(f"Error fetching logs: {str(e)}")


def create_minimal_template():
    """Create minimal CloudFormation template"""
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Threat Detection System - Quick Deploy",
        "Parameters": {
            "NotificationEmail": {
                "Type": "String",
                "Description": "Email for security alerts"
            }
        },
        "Resources": {
            "SecurityThreatsTable": {
                "Type": "AWS::DynamoDB::Table",
                "Properties": {
                    "TableName": "security-threats",
                    "BillingMode": "PAY_PER_REQUEST",
                    "AttributeDefinitions": [
                        {"AttributeName": "threat_id", "AttributeType": "S"},
                        {"AttributeName": "timestamp", "AttributeType": "S"},
                        {"AttributeName": "status", "AttributeType": "S"}
                    ],
                    "KeySchema": [
                        {"AttributeName": "threat_id", "KeyType": "HASH"}
                    ],
                    "GlobalSecondaryIndexes": [
                        {
                            "IndexName": "status-timestamp-index",
                            "KeySchema": [
                                {"AttributeName": "status", "KeyType": "HASH"},
                                {"AttributeName": "timestamp", "KeyType": "RANGE"}
                            ],
                            "Projection": {"ProjectionType": "ALL"}
                        }
                    ]
                }
            },
            "AlertTopic": {
                "Type": "AWS::SNS::Topic",
                "Properties": {
                    "TopicName": "security-threat-alerts",
                    "Subscription": [
                        {"Endpoint": {"Ref": "NotificationEmail"}, "Protocol": "email"}
                    ]
                }
            }
        },
        "Outputs": {
            "TableName": {"Value": {"Ref": "SecurityThreatsTable"}},
            "TopicArn": {"Value": {"Ref": "AlertTopic"}}
        }
    }


# Main function - only for standalone testing
if __name__ == "__main__":
    st.set_page_config(page_title="AWS Deployment", layout="wide")
    render_deployment_utility()