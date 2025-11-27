"""
Simplified AWS Deployment Interface
Easy integration into existing Streamlit apps
"""

import streamlit as st
import boto3
from botocore.exceptions import ClientError
import json
import time

def simple_deployment_interface():
    """
    Simplified one-page deployment interface
    Perfect for adding to your existing Streamlit app
    """
    
    st.markdown("## 🚀 AWS Threat Detection - Quick Deploy")
    
    # Initialize AWS
    if not check_aws_credentials():
        return
    
    # Get AWS clients
    session = boto3.Session(
        aws_access_key_id=st.secrets['default']['aws_access_key_id'],
        aws_secret_access_key=st.secrets['default']['aws_secret_access_key'],
        region_name=st.secrets['aws']['region']
    )
    
    cf_client = session.client('cloudformation')
    lambda_client = session.client('lambda')
    dynamodb_client = session.client('dynamodb')
    
    # Check current status
    deployment_status = check_deployment_status(cf_client, lambda_client, dynamodb_client)
    
    # Display status cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if deployment_status['stack_exists']:
            st.success("✅ **Infrastructure**\nDeployed")
        else:
            st.warning("⚠️ **Infrastructure**\nNot deployed")
    
    with col2:
        if deployment_status['lambda_exists']:
            st.success("✅ **Lambda Function**\nActive")
        else:
            st.warning("⚠️ **Lambda Function**\nNot found")
    
    with col3:
        threat_count = deployment_status['threat_count']
        if threat_count > 0:
            st.info(f"📊 **Threats Detected**\n{threat_count} total")
        else:
            st.info("📊 **Threats Detected**\n0 (monitoring)")
    
    st.markdown("---")
    
    # Action buttons
    if not deployment_status['stack_exists']:
        # Not deployed - show deploy button
        st.markdown("### 🎯 Deploy AWS Infrastructure")
        
        email = st.text_input("Notification Email", value="")
        
        if st.button("🚀 Deploy Now", type="primary", disabled=not email):
            quick_deploy(cf_client, email)
    
    else:
        # Already deployed - show management options
        st.markdown("### 🔧 Manage Deployment")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🧪 Run Test"):
                quick_test(session)
        
        with col_b:
            if st.button("📊 View Logs"):
                show_quick_logs(session.client('logs'))
        
        with col_c:
            if st.button("🔄 Update Lambda"):
                st.info("Lambda update interface (upload ZIP)")


def check_aws_credentials():
    """Verify AWS credentials are configured"""
    try:
        if 'default' not in st.secrets or 'aws' not in st.secrets:
            st.error("❌ AWS credentials not configured in Streamlit secrets")
            with st.expander("ℹ️ How to configure"):
                st.code("""
# Add to Streamlit Cloud → Settings → Secrets

[aws]
region = "us-east-1"
threats_table = "security-threats"

[default]
aws_access_key_id = "YOUR_KEY"
aws_secret_access_key = "YOUR_SECRET"
                """)
            return False
        return True
    except:
        return False


def check_deployment_status(cf_client, lambda_client, dynamodb_client):
    """Check if infrastructure is deployed"""
    status = {
        'stack_exists': False,
        'lambda_exists': False,
        'threat_count': 0
    }
    
    # Check CloudFormation
    try:
        cf_client.describe_stacks(StackName='threat-detection-system')
        status['stack_exists'] = True
    except:
        pass
    
    # Check Lambda
    try:
        lambda_client.get_function(FunctionName='threat-detection-handler')
        status['lambda_exists'] = True
    except:
        pass
    
    # Check DynamoDB
    try:
        response = dynamodb_client.scan(
            TableName='security-threats',
            Select='COUNT'
        )
        status['threat_count'] = response.get('Count', 0)
    except:
        pass
    
    return status


def quick_deploy(cf_client, email):
    """Quick deployment with minimal template"""
    
    st.markdown("### 🚀 Deployment Starting...")
    
    # Minimal CloudFormation template
    template = {
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
                        {
                            "Endpoint": {"Ref": "NotificationEmail"},
                            "Protocol": "email"
                        }
                    ]
                }
            }
        },
        "Outputs": {
            "TableName": {
                "Value": {"Ref": "SecurityThreatsTable"}
            },
            "TopicArn": {
                "Value": {"Ref": "AlertTopic"}
            }
        }
    }
    
    try:
        with st.spinner("Creating AWS resources..."):
            response = cf_client.create_stack(
                StackName='threat-detection-system',
                TemplateBody=json.dumps(template),
                Parameters=[
                    {'ParameterKey': 'NotificationEmail', 'ParameterValue': email}
                ],
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
        
        st.success(f"✅ Deployment started! Stack ID: {response['StackId'][:50]}...")
        
        # Monitor deployment
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(60):  # Max 5 minutes
            try:
                stack_info = cf_client.describe_stacks(StackName='threat-detection-system')
                status = stack_info['Stacks'][0]['StackStatus']
                
                status_text.info(f"Status: {status}")
                progress_bar.progress(min((i + 1) / 60, 0.95))
                
                if 'COMPLETE' in status:
                    progress_bar.progress(1.0)
                    st.balloons()
                    st.success("🎉 Deployment complete!")
                    
                    # Show outputs
                    outputs = stack_info['Stacks'][0].get('Outputs', [])
                    if outputs:
                        st.markdown("**Outputs:**")
                        for output in outputs:
                            st.code(f"{output['OutputKey']}: {output['OutputValue']}")
                    break
                
                if 'FAILED' in status:
                    st.error(f"❌ Deployment failed: {status}")
                    break
                
                time.sleep(5)
            except:
                break
        
    except ClientError as e:
        st.error(f"❌ Deployment failed: {e.response['Error']['Message']}")


def quick_test(session):
    """Quick threat detection test"""
    
    st.markdown("### 🧪 Running Test...")
    
    iam_client = session.client('iam')
    dynamodb_client = session.client('dynamodb')
    
    test_role = f"ThreatTest-{int(time.time())}"
    
    try:
        # Create test role
        with st.spinner("Creating test role..."):
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            iam_client.create_role(
                RoleName=test_role,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            st.info(f"✅ Created: {test_role}")
        
        # Add wildcard policy
        with st.spinner("Adding wildcard policy (triggers alert)..."):
            time.sleep(2)
            
            policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": "*"
                }]
            }
            
            iam_client.put_role_policy(
                RoleName=test_role,
                PolicyName="WildcardTest",
                PolicyDocument=json.dumps(policy)
            )
            
            st.info("✅ Policy added - should trigger detection!")
        
        # Wait for detection
        with st.spinner("Waiting for threat detection (10 sec)..."):
            time.sleep(10)
        
        # Check DynamoDB
        st.info("Checking for detected threat...")
        
        response = dynamodb_client.scan(
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
        
        # Cleanup
        with st.spinner("Cleaning up..."):
            time.sleep(2)
            iam_client.delete_role_policy(RoleName=test_role, PolicyName="WildcardTest")
            iam_client.delete_role(RoleName=test_role)
            st.success("✅ Cleanup complete!")
        
    except Exception as e:
        st.error(f"❌ Test failed: {str(e)}")
        # Attempt cleanup
        try:
            iam_client.delete_role_policy(RoleName=test_role, PolicyName="WildcardTest")
            iam_client.delete_role(RoleName=test_role)
        except:
            pass


def show_quick_logs(logs_client):
    """Show recent Lambda logs"""
    
    st.markdown("### 📋 Recent Lambda Logs")
    
    try:
        # Get latest log stream
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
        
        # Get events
        events_response = logs_client.get_log_events(
            logGroupName='/aws/lambda/threat-detection-handler',
            logStreamName=stream,
            limit=20,
            startFromHead=False
        )
        
        events = events_response.get('events', [])
        
        if events:
            for event in reversed(events):
                st.text(event['message'])
        else:
            st.info("No recent events")
            
    except Exception as e:
        st.error(f"Error fetching logs: {str(e)}")


# Quick integration function
def add_deployment_to_sidebar():
    """
    Add deployment interface to sidebar
    Call this from your main app
    """
    with st.sidebar:
        if st.checkbox("🔧 Show AWS Deployment"):
            simple_deployment_interface()


# Main entry point for standalone use
if __name__ == "__main__":
    st.set_page_config(page_title="Quick Deploy", layout="wide")
    simple_deployment_interface()
