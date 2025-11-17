"""
FinOps Module for AWS Compliance Platform
Comprehensive Cost Management, Optimization, and Analytics

Features:
- Spend Analytics with Portfolio breakdown
- Cost Optimization Recommendations
- AWS Best Practices Advisor
- Anomaly Detection
- Charge Back and Cost Allocations
- Inventory Dashboard with Cost Correlation
- Tag Management and Compliance
"""

import streamlit as st
import boto3
from botocore.exceptions import ClientError
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import json

# ============================================================================
# COST EXPLORER & SPEND ANALYTICS
# ============================================================================

def fetch_cost_data(ce_client, start_date: str, end_date: str, granularity: str = 'DAILY') -> Dict:
    """Fetch cost and usage data from AWS Cost Explorer"""
    if not ce_client or st.session_state.get('demo_mode', False):
        return generate_demo_cost_data()
    
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity,
            Metrics=['UnblendedCost', 'UsageQuantity'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            ]
        )
        return response
    except ClientError as e:
        st.error(f"Error fetching cost data: {str(e)}")
        return generate_demo_cost_data()

def fetch_cost_by_portfolio(ce_client, start_date: str, end_date: str, portfolio_tag: str = 'Portfolio') -> Dict:
    """Fetch costs grouped by portfolio tag"""
    if not ce_client or st.session_state.get('demo_mode', False):
        return generate_demo_portfolio_costs()
    
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'TAG', 'Key': portfolio_tag}
            ]
        )
        return response
    except ClientError as e:
        st.error(f"Error fetching portfolio costs: {str(e)}")
        return generate_demo_portfolio_costs()

def fetch_cost_forecast(ce_client, start_date: str, end_date: str) -> Dict:
    """Fetch cost forecast from AWS Cost Explorer"""
    if not ce_client or st.session_state.get('demo_mode', False):
        return generate_demo_forecast()
    
    try:
        response = ce_client.get_cost_forecast(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Metric='UNBLENDED_COST',
            Granularity='MONTHLY'
        )
        return response
    except ClientError as e:
        st.error(f"Error fetching forecast: {str(e)}")
        return generate_demo_forecast()

# ============================================================================
# COST ANOMALY DETECTION
# ============================================================================

def fetch_cost_anomalies(ce_client, start_date: str, end_date: str) -> List[Dict]:
    """Fetch cost anomalies from AWS Cost Anomaly Detection"""
    if not ce_client or st.session_state.get('demo_mode', False):
        return generate_demo_anomalies()
    
    try:
        response = ce_client.get_anomalies(
            DateInterval={
                'StartDate': start_date,
                'EndDate': end_date
            },
            MaxResults=50
        )
        return response.get('Anomalies', [])
    except ClientError as e:
        st.warning(f"Cost Anomaly Detection not available: {str(e)}")
        return generate_demo_anomalies()

def detect_spending_patterns(cost_data: Dict) -> Dict:
    """Analyze spending patterns and identify unusual trends"""
    # This is a simplified pattern detection
    # In production, you'd use more sophisticated ML models
    
    if not cost_data or 'ResultsByTime' not in cost_data:
        return {
            'trend': 'stable',
            'avg_daily_spend': 0,
            'max_spike': 0,
            'patterns': []
        }
    
    daily_costs = []
    for result in cost_data['ResultsByTime']:
        total = float(result['Total'].get('UnblendedCost', {}).get('Amount', 0))
        daily_costs.append(total)
    
    if not daily_costs:
        return {'trend': 'stable', 'avg_daily_spend': 0, 'max_spike': 0, 'patterns': []}
    
    avg_spend = sum(daily_costs) / len(daily_costs)
    max_spend = max(daily_costs)
    
    # Detect spikes (>50% above average)
    threshold = avg_spend * 1.5
    spikes = [cost for cost in daily_costs if cost > threshold]
    
    return {
        'trend': 'increasing' if daily_costs[-1] > daily_costs[0] else 'decreasing',
        'avg_daily_spend': avg_spend,
        'max_spike': max_spend,
        'spike_count': len(spikes),
        'patterns': ['Unusual spike detected' if spikes else 'Normal spending pattern']
    }

# ============================================================================
# INVENTORY & RESOURCE TRACKING
# ============================================================================

def fetch_resource_inventory(session) -> Dict:
    """Fetch comprehensive resource inventory across services"""
    if not session or st.session_state.get('demo_mode', False):
        return generate_demo_inventory()
    
    inventory = {
        'ec2': fetch_ec2_inventory(session),
        'rds': fetch_rds_inventory(session),
        's3': fetch_s3_inventory(session),
        'lambda': fetch_lambda_inventory(session),
        'ebs': fetch_ebs_inventory(session)
    }
    
    return inventory

def fetch_ec2_inventory(session) -> List[Dict]:
    """Fetch EC2 instances with cost data"""
    try:
        ec2 = session.client('ec2')
        response = ec2.describe_instances()
        
        instances = []
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instances.append({
                    'InstanceId': instance.get('InstanceId'),
                    'InstanceType': instance.get('InstanceType'),
                    'State': instance.get('State', {}).get('Name'),
                    'LaunchTime': instance.get('LaunchTime'),
                    'Tags': instance.get('Tags', []),
                    'Platform': instance.get('Platform', 'Linux'),
                    'VpcId': instance.get('VpcId'),
                    'EstimatedMonthlyCost': calculate_ec2_cost(instance.get('InstanceType'))
                })
        return instances
    except ClientError as e:
        st.warning(f"Could not fetch EC2 inventory: {str(e)}")
        return []

def fetch_rds_inventory(session) -> List[Dict]:
    """Fetch RDS instances"""
    try:
        rds = session.client('rds')
        response = rds.describe_db_instances()
        
        instances = []
        for db in response.get('DBInstances', []):
            instances.append({
                'DBInstanceIdentifier': db.get('DBInstanceIdentifier'),
                'DBInstanceClass': db.get('DBInstanceClass'),
                'Engine': db.get('Engine'),
                'DBInstanceStatus': db.get('DBInstanceStatus'),
                'AllocatedStorage': db.get('AllocatedStorage'),
                'EstimatedMonthlyCost': calculate_rds_cost(db.get('DBInstanceClass'))
            })
        return instances
    except ClientError as e:
        st.warning(f"Could not fetch RDS inventory: {str(e)}")
        return []

def fetch_s3_inventory(session) -> List[Dict]:
    """Fetch S3 buckets"""
    try:
        s3 = session.client('s3')
        response = s3.list_buckets()
        
        buckets = []
        for bucket in response.get('Buckets', []):
            bucket_name = bucket['Name']
            
            # Get bucket size (this is approximate)
            try:
                cw = session.client('cloudwatch')
                size_response = cw.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='BucketSizeBytes',
                    Dimensions=[
                        {'Name': 'BucketName', 'Value': bucket_name},
                        {'Name': 'StorageType', 'Value': 'StandardStorage'}
                    ],
                    StartTime=datetime.now() - timedelta(days=2),
                    EndTime=datetime.now(),
                    Period=86400,
                    Statistics=['Average']
                )
                
                size_gb = 0
                if size_response['Datapoints']:
                    size_bytes = size_response['Datapoints'][0]['Average']
                    size_gb = size_bytes / (1024**3)
                
                buckets.append({
                    'BucketName': bucket_name,
                    'CreationDate': bucket['CreationDate'],
                    'SizeGB': round(size_gb, 2),
                    'EstimatedMonthlyCost': round(size_gb * 0.023, 2)  # S3 Standard pricing
                })
            except:
                buckets.append({
                    'BucketName': bucket_name,
                    'CreationDate': bucket['CreationDate'],
                    'SizeGB': 'N/A',
                    'EstimatedMonthlyCost': 'N/A'
                })
        
        return buckets
    except ClientError as e:
        st.warning(f"Could not fetch S3 inventory: {str(e)}")
        return []

def fetch_lambda_inventory(session) -> List[Dict]:
    """Fetch Lambda functions"""
    try:
        lambda_client = session.client('lambda')
        response = lambda_client.list_functions()
        
        functions = []
        for func in response.get('Functions', []):
            functions.append({
                'FunctionName': func.get('FunctionName'),
                'Runtime': func.get('Runtime'),
                'MemorySize': func.get('MemorySize'),
                'LastModified': func.get('LastModified'),
                'EstimatedMonthlyCost': 'Usage-based'
            })
        return functions
    except ClientError as e:
        st.warning(f"Could not fetch Lambda inventory: {str(e)}")
        return []

def fetch_ebs_inventory(session) -> List[Dict]:
    """Fetch EBS volumes"""
    try:
        ec2 = session.client('ec2')
        response = ec2.describe_volumes()
        
        volumes = []
        for vol in response.get('Volumes', []):
            volumes.append({
                'VolumeId': vol.get('VolumeId'),
                'VolumeType': vol.get('VolumeType'),
                'Size': vol.get('Size'),
                'State': vol.get('State'),
                'EstimatedMonthlyCost': calculate_ebs_cost(vol.get('VolumeType'), vol.get('Size'))
            })
        return volumes
    except ClientError as e:
        st.warning(f"Could not fetch EBS inventory: {str(e)}")
        return []

# ============================================================================
# COST CALCULATIONS
# ============================================================================

def calculate_ec2_cost(instance_type: str) -> float:
    """Calculate approximate monthly EC2 cost"""
    # Simplified pricing (actual pricing varies by region)
    pricing = {
        't2.micro': 8.50,
        't2.small': 17.00,
        't2.medium': 34.00,
        't3.micro': 7.50,
        't3.small': 15.00,
        't3.medium': 30.00,
        'm5.large': 70.00,
        'm5.xlarge': 140.00,
        'c5.large': 62.00,
        'r5.large': 92.00
    }
    return pricing.get(instance_type, 50.00)  # Default estimate

def calculate_rds_cost(instance_class: str) -> float:
    """Calculate approximate monthly RDS cost"""
    pricing = {
        'db.t3.micro': 12.00,
        'db.t3.small': 24.00,
        'db.t3.medium': 48.00,
        'db.m5.large': 140.00,
        'db.r5.large': 180.00
    }
    return pricing.get(instance_class, 75.00)

def calculate_ebs_cost(volume_type: str, size: int) -> float:
    """Calculate approximate monthly EBS cost"""
    pricing_per_gb = {
        'gp2': 0.10,
        'gp3': 0.08,
        'io1': 0.125,
        'io2': 0.125,
        'st1': 0.045,
        'sc1': 0.015
    }
    price_per_gb = pricing_per_gb.get(volume_type, 0.10)
    return round(size * price_per_gb, 2)

# ============================================================================
# TAG MANAGEMENT
# ============================================================================

def fetch_tag_compliance(session) -> Dict:
    """Analyze tag compliance across resources"""
    if not session or st.session_state.get('demo_mode', False):
        return generate_demo_tag_compliance()
    
    try:
        tagging = session.client('resourcegroupstaggingapi')
        
        # Required tags for compliance
        required_tags = ['Environment', 'Owner', 'CostCenter', 'Portfolio', 'Application']
        
        # Get all resources
        response = tagging.get_resources(
            ResourcesPerPage=100
        )
        
        resources = response.get('ResourceTagMappingList', [])
        
        compliance_data = {
            'total_resources': len(resources),
            'tagged_resources': 0,
            'untagged_resources': 0,
            'partially_tagged': 0,
            'compliant_resources': 0,
            'tag_coverage': {},
            'resources_by_service': {}
        }
        
        for resource in resources:
            tags = {tag['Key']: tag['Value'] for tag in resource.get('Tags', [])}
            resource_arn = resource.get('ResourceARN', '')
            
            # Determine service from ARN
            service = resource_arn.split(':')[2] if ':' in resource_arn else 'unknown'
            compliance_data['resources_by_service'][service] = \
                compliance_data['resources_by_service'].get(service, 0) + 1
            
            if not tags:
                compliance_data['untagged_resources'] += 1
            else:
                compliance_data['tagged_resources'] += 1
                
                # Check compliance
                missing_tags = [tag for tag in required_tags if tag not in tags]
                
                if not missing_tags:
                    compliance_data['compliant_resources'] += 1
                elif len(missing_tags) < len(required_tags):
                    compliance_data['partially_tagged'] += 1
                
                # Track individual tag coverage
                for tag_key in required_tags:
                    if tag_key in tags:
                        compliance_data['tag_coverage'][tag_key] = \
                            compliance_data['tag_coverage'].get(tag_key, 0) + 1
        
        return compliance_data
        
    except ClientError as e:
        st.warning(f"Could not fetch tag compliance: {str(e)}")
        return generate_demo_tag_compliance()

def apply_tags_to_resources(session, resources: List[str], tags: Dict[str, str]) -> Dict:
    """Apply tags to specified resources"""
    try:
        tagging = session.client('resourcegroupstaggingapi')
        
        tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
        
        response = tagging.tag_resources(
            ResourceARNList=resources,
            Tags=tag_list
        )
        
        return {
            'success': True,
            'failed_resources': response.get('FailedResourcesMap', {})
        }
    except ClientError as e:
        return {
            'success': False,
            'error': str(e)
        }

# ============================================================================
# COST OPTIMIZATION RECOMMENDATIONS
# ============================================================================

def fetch_cost_optimization_recommendations(session) -> Dict:
    """Fetch recommendations from AWS Compute Optimizer and Cost Explorer"""
    if not session or st.session_state.get('demo_mode', False):
        return generate_demo_optimization_recommendations()
    
    recommendations = {
        'ec2_rightsizing': [],
        'unused_resources': [],
        'reserved_instance_opportunities': [],
        'savings_plans': [],
        'total_potential_savings': 0
    }
    
    try:
        # Get Compute Optimizer recommendations
        co_client = session.client('compute-optimizer')
        
        # EC2 Rightsizing
        ec2_recs = co_client.get_ec2_instance_recommendations()
        for rec in ec2_recs.get('instanceRecommendations', []):
            current_type = rec.get('currentInstanceType')
            recommended_type = rec.get('recommendationOptions', [{}])[0].get('instanceType')
            
            if recommended_type and recommended_type != current_type:
                recommendations['ec2_rightsizing'].append({
                    'instance_id': rec.get('instanceArn', '').split('/')[-1],
                    'current_type': current_type,
                    'recommended_type': recommended_type,
                    'reason': 'Underutilized - Lower performance tier suitable',
                    'estimated_savings': calculate_rightsizing_savings(current_type, recommended_type)
                })
    except ClientError as e:
        st.warning(f"Compute Optimizer not available: {str(e)}")
    
    # Identify unused resources
    try:
        recommendations['unused_resources'] = identify_unused_resources(session)
    except Exception as e:
        st.warning(f"Could not identify unused resources: {str(e)}")
    
    # Calculate total potential savings
    total_savings = 0
    for rec in recommendations['ec2_rightsizing']:
        total_savings += rec['estimated_savings']
    for res in recommendations['unused_resources']:
        total_savings += res.get('monthly_cost', 0)
    
    recommendations['total_potential_savings'] = total_savings
    
    return recommendations

def calculate_rightsizing_savings(current: str, recommended: str) -> float:
    """Calculate potential monthly savings from rightsizing"""
    current_cost = calculate_ec2_cost(current)
    recommended_cost = calculate_ec2_cost(recommended)
    return max(0, current_cost - recommended_cost)

def identify_unused_resources(session) -> List[Dict]:
    """Identify unused AWS resources"""
    unused = []
    
    try:
        # Unused EBS volumes
        ec2 = session.client('ec2')
        volumes = ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        
        for vol in volumes.get('Volumes', []):
            unused.append({
                'resource_type': 'EBS Volume',
                'resource_id': vol['VolumeId'],
                'reason': 'Unattached volume',
                'monthly_cost': calculate_ebs_cost(vol['VolumeType'], vol['Size'])
            })
        
        # Unused Elastic IPs
        eips = ec2.describe_addresses()
        for eip in eips.get('Addresses', []):
            if 'InstanceId' not in eip:
                unused.append({
                    'resource_type': 'Elastic IP',
                    'resource_id': eip.get('PublicIp'),
                    'reason': 'Not associated with instance',
                    'monthly_cost': 3.60  # $0.005/hour
                })
        
        # Old snapshots (>90 days)
        snapshots = ec2.describe_snapshots(OwnerIds=['self'])
        ninety_days_ago = datetime.now() - timedelta(days=90)
        
        for snap in snapshots.get('Snapshots', []):
            if snap['StartTime'].replace(tzinfo=None) < ninety_days_ago:
                unused.append({
                    'resource_type': 'EBS Snapshot',
                    'resource_id': snap['SnapshotId'],
                    'reason': 'Older than 90 days',
                    'monthly_cost': snap['VolumeSize'] * 0.05  # $0.05/GB-month
                })
    
    except ClientError as e:
        st.warning(f"Could not identify some unused resources: {str(e)}")
    
    return unused[:10]  # Return top 10

# ============================================================================
# AWS TRUSTED ADVISOR / BEST PRACTICES
# ============================================================================

def fetch_trusted_advisor_checks(session) -> Dict:
    """Fetch AWS Trusted Advisor recommendations"""
    if not session or st.session_state.get('demo_mode', False):
        return generate_demo_trusted_advisor()
    
    try:
        support = session.client('support', region_name='us-east-1')
        
        # Get all checks
        checks = support.describe_trusted_advisor_checks(language='en')
        
        results = {
            'cost_optimization': [],
            'security': [],
            'performance': [],
            'fault_tolerance': [],
            'service_limits': []
        }
        
        for check in checks.get('checks', []):
            check_id = check['id']
            category = check['category']
            
            # Get check result
            try:
                result = support.describe_trusted_advisor_check_result(
                    checkId=check_id,
                    language='en'
                )
                
                check_result = result.get('result', {})
                status = check_result.get('status', 'unknown')
                
                check_info = {
                    'name': check['name'],
                    'description': check['description'],
                    'status': status,
                    'flagged_resources': check_result.get('flaggedResources', [])
                }
                
                # Categorize
                if category == 'cost_optimizing':
                    results['cost_optimization'].append(check_info)
                elif category == 'security':
                    results['security'].append(check_info)
                elif category == 'performance':
                    results['performance'].append(check_info)
                elif category == 'fault_tolerance':
                    results['fault_tolerance'].append(check_info)
                elif category == 'service_limits':
                    results['service_limits'].append(check_info)
            except:
                continue
        
        return results
        
    except ClientError as e:
        st.warning(f"Trusted Advisor not available (requires Business/Enterprise support): {str(e)}")
        return generate_demo_trusted_advisor()

# ============================================================================
# DEMO DATA GENERATORS
# ============================================================================

def generate_demo_cost_data() -> Dict:
    """Generate demo cost data for testing"""
    start_date = datetime.now() - timedelta(days=30)
    
    results = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        results.append({
            'TimePeriod': {
                'Start': date.strftime('%Y-%m-%d'),
                'End': (date + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            'Total': {
                'UnblendedCost': {
                    'Amount': str(150 + (i * 5) + (i % 7) * 20),
                    'Unit': 'USD'
                }
            },
            'Groups': [
                {'Keys': ['EC2'], 'Metrics': {'UnblendedCost': {'Amount': '50', 'Unit': 'USD'}}},
                {'Keys': ['RDS'], 'Metrics': {'UnblendedCost': {'Amount': '30', 'Unit': 'USD'}}},
                {'Keys': ['S3'], 'Metrics': {'UnblendedCost': {'Amount': '20', 'Unit': 'USD'}}},
                {'Keys': ['Lambda'], 'Metrics': {'UnblendedCost': {'Amount': '15', 'Unit': 'USD'}}},
            ]
        })
    
    return {'ResultsByTime': results}

def generate_demo_portfolio_costs() -> Dict:
    """Generate demo portfolio cost breakdown"""
    return {
        'ResultsByTime': [
            {
                'TimePeriod': {'Start': '2024-11-01', 'End': '2024-11-30'},
                'Groups': [
                    {'Keys': ['Retail'], 'Metrics': {'UnblendedCost': {'Amount': '4500', 'Unit': 'USD'}}},
                    {'Keys': ['Healthcare'], 'Metrics': {'UnblendedCost': {'Amount': '6800', 'Unit': 'USD'}}},
                    {'Keys': ['Financial'], 'Metrics': {'UnblendedCost': {'Amount': '8200', 'Unit': 'USD'}}},
                ]
            }
        ]
    }

def generate_demo_forecast() -> Dict:
    """Generate demo forecast data"""
    return {
        'Total': {
            'Amount': '6500',
            'Unit': 'USD'
        },
        'ForecastResultsByTime': [
            {'TimePeriod': {'Start': '2024-12-01', 'End': '2024-12-31'},
             'MeanValue': '6500'}
        ]
    }

def generate_demo_anomalies() -> List[Dict]:
    """Generate demo anomaly data"""
    return [
        {
            'AnomalyId': 'ANOM-001',
            'AnomalyScore': {'MaxScore': 0.85, 'CurrentScore': 0.85},
            'Impact': {'MaxImpact': 450, 'TotalImpact': 450},
            'MonitorArn': 'arn:aws:ce::123456789012:anomalymonitor/monitor-1',
            'AnomalyStartDate': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'AnomalyEndDate': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'DimensionValue': 'EC2',
            'RootCauses': [
                {'Service': 'EC2', 'Region': 'us-east-1', 'UsageType': 'm5.xlarge'}
            ]
        },
        {
            'AnomalyId': 'ANOM-002',
            'AnomalyScore': {'MaxScore': 0.72, 'CurrentScore': 0.72},
            'Impact': {'MaxImpact': 320, 'TotalImpact': 320},
            'MonitorArn': 'arn:aws:ce::123456789012:anomalymonitor/monitor-1',
            'AnomalyStartDate': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'AnomalyEndDate': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'DimensionValue': 'RDS',
            'RootCauses': [
                {'Service': 'RDS', 'Region': 'us-west-2', 'UsageType': 'db.m5.large'}
            ]
        }
    ]

def generate_demo_inventory() -> Dict:
    """Generate demo inventory data"""
    return {
        'ec2': [
            {'InstanceId': 'i-0123456789abcdef0', 'InstanceType': 't3.medium', 'State': 'running',
             'LaunchTime': datetime.now() - timedelta(days=45), 'EstimatedMonthlyCost': 30.00},
            {'InstanceId': 'i-0123456789abcdef1', 'InstanceType': 'm5.large', 'State': 'running',
             'LaunchTime': datetime.now() - timedelta(days=120), 'EstimatedMonthlyCost': 70.00},
            {'InstanceId': 'i-0123456789abcdef2', 'InstanceType': 't3.small', 'State': 'stopped',
             'LaunchTime': datetime.now() - timedelta(days=200), 'EstimatedMonthlyCost': 0.00},
        ],
        'rds': [
            {'DBInstanceIdentifier': 'prod-database', 'DBInstanceClass': 'db.m5.large',
             'Engine': 'postgres', 'DBInstanceStatus': 'available', 'EstimatedMonthlyCost': 140.00},
            {'DBInstanceIdentifier': 'dev-database', 'DBInstanceClass': 'db.t3.small',
             'Engine': 'mysql', 'DBInstanceStatus': 'available', 'EstimatedMonthlyCost': 24.00},
        ],
        's3': [
            {'BucketName': 'prod-data-bucket', 'SizeGB': 450.0, 'EstimatedMonthlyCost': 10.35},
            {'BucketName': 'backup-bucket', 'SizeGB': 1200.0, 'EstimatedMonthlyCost': 27.60},
            {'BucketName': 'logs-bucket', 'SizeGB': 85.0, 'EstimatedMonthlyCost': 1.96},
        ],
        'lambda': [
            {'FunctionName': 'api-handler', 'Runtime': 'python3.11', 'MemorySize': 512,
             'EstimatedMonthlyCost': 'Usage-based'},
            {'FunctionName': 'data-processor', 'Runtime': 'nodejs18.x', 'MemorySize': 1024,
             'EstimatedMonthlyCost': 'Usage-based'},
        ],
        'ebs': [
            {'VolumeId': 'vol-0123456789abcdef0', 'VolumeType': 'gp3', 'Size': 100,
             'State': 'in-use', 'EstimatedMonthlyCost': 8.00},
            {'VolumeId': 'vol-0123456789abcdef1', 'VolumeType': 'gp2', 'Size': 50,
             'State': 'available', 'EstimatedMonthlyCost': 5.00},
        ]
    }

def generate_demo_tag_compliance() -> Dict:
    """Generate demo tag compliance data"""
    return {
        'total_resources': 156,
        'tagged_resources': 134,
        'untagged_resources': 22,
        'partially_tagged': 45,
        'compliant_resources': 89,
        'tag_coverage': {
            'Environment': 142,
            'Owner': 128,
            'CostCenter': 115,
            'Portfolio': 134,
            'Application': 98
        },
        'resources_by_service': {
            'ec2': 42,
            's3': 35,
            'rds': 18,
            'lambda': 28,
            'dynamodb': 12,
            'efs': 8,
            'elasticloadbalancing': 13
        }
    }

def generate_demo_optimization_recommendations() -> Dict:
    """Generate demo optimization recommendations"""
    return {
        'ec2_rightsizing': [
            {
                'instance_id': 'i-0123456789abcdef0',
                'current_type': 'm5.xlarge',
                'recommended_type': 'm5.large',
                'reason': 'CPU utilization consistently below 20%',
                'estimated_savings': 70.00
            },
            {
                'instance_id': 'i-0123456789abcdef1',
                'current_type': 'c5.2xlarge',
                'recommended_type': 'c5.xlarge',
                'reason': 'Memory utilization below 30%',
                'estimated_savings': 125.00
            },
        ],
        'unused_resources': [
            {
                'resource_type': 'EBS Volume',
                'resource_id': 'vol-0123456789abcdef2',
                'reason': 'Unattached for 45+ days',
                'monthly_cost': 5.00
            },
            {
                'resource_type': 'Elastic IP',
                'resource_id': '54.123.45.67',
                'reason': 'Not associated with instance',
                'monthly_cost': 3.60
            },
            {
                'resource_type': 'EBS Snapshot',
                'resource_id': 'snap-0123456789abcdef',
                'reason': 'Older than 180 days',
                'monthly_cost': 12.50
            },
        ],
        'reserved_instance_opportunities': [],
        'savings_plans': [],
        'total_potential_savings': 216.10
    }

def generate_demo_trusted_advisor() -> Dict:
    """Generate demo Trusted Advisor recommendations"""
    return {
        'cost_optimization': [
            {
                'name': 'Low Utilization Amazon EC2 Instances',
                'description': 'Identifies EC2 instances with low utilization',
                'status': 'warning',
                'flagged_resources': 3
            },
            {
                'name': 'Idle Load Balancers',
                'description': 'Identifies load balancers with no traffic',
                'status': 'error',
                'flagged_resources': 1
            },
            {
                'name': 'Unassociated Elastic IP Addresses',
                'description': 'Identifies elastic IPs not associated with instances',
                'status': 'warning',
                'flagged_resources': 2
            },
        ],
        'security': [
            {
                'name': 'Security Groups - Unrestricted Access',
                'description': 'Checks for security groups that allow unrestricted access',
                'status': 'error',
                'flagged_resources': 5
            },
        ],
        'performance': [
            {
                'name': 'High Utilization Amazon EC2 Instances',
                'description': 'Identifies instances with high utilization',
                'status': 'ok',
                'flagged_resources': 0
            },
        ],
        'fault_tolerance': [
            {
                'name': 'Amazon RDS Backups',
                'description': 'Checks for RDS instances without automatic backups',
                'status': 'ok',
                'flagged_resources': 0
            },
        ],
        'service_limits': [
            {
                'name': 'EC2 Service Limits',
                'description': 'Monitors EC2 service limits',
                'status': 'ok',
                'flagged_resources': 0
            },
        ]
    }

# ============================================================================
# RENDER FUNCTIONS - UI COMPONENTS
# ============================================================================

def render_finops_dashboard():
    """Main FinOps dashboard with all features"""
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #232F3E 0%, #37475A 100%); 
                padding: 1.5rem; 
                border-radius: 10px; 
                margin-bottom: 1rem;
                border-top: 4px solid #FF9900;'>
        <h2 style='color: white; margin: 0;'>💰 FinOps Cost Management</h2>
        <p style='color: #E8F4F8; margin: 0.5rem 0 0 0;'>
            Comprehensive cost optimization, analytics, and resource management
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different FinOps features
    finops_tabs = st.tabs([
        "📊 Spend Analytics",
        "💡 Cost Optimization",
        "✅ Best Practices",
        "🚨 Anomaly Detection",
        "💳 Chargeback & Allocation",
        "📦 Inventory Dashboard",
        "🏷️ Tag Management"
    ])
    
    # Spend Analytics Tab
    with finops_tabs[0]:
        render_spend_analytics()
    
    # Cost Optimization Tab
    with finops_tabs[1]:
        render_cost_optimization()
    
    # Best Practices Tab
    with finops_tabs[2]:
        render_best_practices()
    
    # Anomaly Detection Tab
    with finops_tabs[3]:
        render_anomaly_detection()
    
    # Chargeback & Allocation Tab
    with finops_tabs[4]:
        render_chargeback_allocation()
    
    # Inventory Dashboard Tab
    with finops_tabs[5]:
        render_inventory_dashboard()
    
    # Tag Management Tab
    with finops_tabs[6]:
        render_tag_management()

def render_spend_analytics():
    """Render spend analytics dashboard"""
    st.markdown("### 📊 AWS Spend Analytics")
    
    # Date range selector
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        days_back = st.selectbox("Time Period", [7, 30, 60, 90], index=1)
    with col2:
        granularity = st.selectbox("Granularity", ["DAILY", "MONTHLY"])
    with col3:
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP"])
    
    # Fetch cost data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    ce_client = st.session_state.get('aws_clients', {}).get('ce')
    cost_data = fetch_cost_data(ce_client, start_date, end_date, granularity)
    
    # Summary metrics
    total_cost = 0
    if cost_data and 'ResultsByTime' in cost_data:
        for result in cost_data['ResultsByTime']:
            total_cost += float(result['Total'].get('UnblendedCost', {}).get('Amount', 0))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Spend", f"${total_cost:,.2f}")
    with col2:
        avg_daily = total_cost / max(days_back, 1)
        st.metric("Avg Daily", f"${avg_daily:,.2f}")
    with col3:
        forecast_monthly = avg_daily * 30
        st.metric("Monthly Forecast", f"${forecast_monthly:,.2f}")
    with col4:
        # Calculate trend
        if cost_data and 'ResultsByTime' in cost_data and len(cost_data['ResultsByTime']) > 1:
            first_day = float(cost_data['ResultsByTime'][0]['Total'].get('UnblendedCost', {}).get('Amount', 0))
            last_day = float(cost_data['ResultsByTime'][-1]['Total'].get('UnblendedCost', {}).get('Amount', 0))
            trend = ((last_day - first_day) / max(first_day, 1)) * 100
            st.metric("Trend", f"{trend:+.1f}%", delta=f"{trend:+.1f}%")
        else:
            st.metric("Trend", "N/A")
    
    st.markdown("---")
    
    # Cost trend chart
    if cost_data and 'ResultsByTime' in cost_data:
        dates = []
        costs = []
        
        for result in cost_data['ResultsByTime']:
            dates.append(result['TimePeriod']['Start'])
            costs.append(float(result['Total'].get('UnblendedCost', {}).get('Amount', 0)))
        
        df_trend = pd.DataFrame({'Date': dates, 'Cost': costs})
        
        fig_trend = px.line(
            df_trend,
            x='Date',
            y='Cost',
            title='Cost Trend Over Time',
            labels={'Cost': 'Cost (USD)', 'Date': 'Date'}
        )
        fig_trend.update_traces(line_color='#FF9900', line_width=3)
        fig_trend.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("---")
    
    # Service breakdown
    # Service breakdown
    st.markdown("#### 🔧 Cost by Service")
    
    if cost_data and 'ResultsByTime' in cost_data:
        # Aggregate costs by service
        service_costs = {}
        for result in cost_data['ResultsByTime']:
            for group in result.get('Groups', []):
                service = group['Keys'][0] if group.get('Keys') else 'Other'
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                service_costs[service] = service_costs.get(service, 0) + cost
        
        # Create pie chart
        if service_costs:
            df_services = pd.DataFrame([
                {'Service': k, 'Cost': v}
                for k, v in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
            ])
            
            fig_pie = px.pie(
                df_services,
                values='Cost',
                names='Service',
                title='Cost Distribution by Service',
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Service table - Calculate percentage BEFORE formatting
            df_services['Percentage'] = df_services['Cost'].apply(
                lambda x: f"{(x / total_cost * 100):.1f}%" if total_cost > 0 else "0.0%"
            )
            df_services['Cost'] = df_services['Cost'].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(df_services, use_container_width=True, hide_index=True)

def render_cost_optimization():
    """Render cost optimization recommendations"""
    st.markdown("### 💡 Cost Optimization Recommendations")
    
    session = st.session_state.get('boto3_session')
    recommendations = fetch_cost_optimization_recommendations(session)
    
    # Summary card
    st.markdown(f"""
    <div class='score-card excellent'>
        <h3>💰 Total Potential Monthly Savings</h3>
        <h1 style='color: #4CAF50; margin: 1rem 0;'>
            ${recommendations['total_potential_savings']:,.2f}
        </h1>
        <p>Based on identified optimization opportunities</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # EC2 Rightsizing
    st.markdown("#### 🖥️ EC2 Rightsizing Opportunities")
    
    if recommendations['ec2_rightsizing']:
        for rec in recommendations['ec2_rightsizing']:
            st.markdown(f"""
            <div class='metric-card'>
                <strong>Instance:</strong> {rec['instance_id']}<br>
                <strong>Current:</strong> {rec['current_type']} → <strong>Recommended:</strong> {rec['recommended_type']}<br>
                <strong>Reason:</strong> {rec['reason']}<br>
                <strong>Monthly Savings:</strong> <span style='color: #4CAF50; font-weight: bold;'>
                    ${rec['estimated_savings']:.2f}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ All EC2 instances are optimally sized!")
    
    st.markdown("---")
    
    # Unused Resources
    st.markdown("#### 🗑️ Unused Resources")
    
    if recommendations['unused_resources']:
        df_unused = pd.DataFrame(recommendations['unused_resources'])
        df_unused['monthly_cost'] = df_unused['monthly_cost'].apply(lambda x: f"${x:.2f}")
        st.dataframe(df_unused, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Generate Cleanup Script", type="primary"):
            cleanup_script = generate_cleanup_script(recommendations['unused_resources'])
            st.code(cleanup_script, language='bash')
    else:
        st.success("✅ No unused resources detected!")

def render_best_practices():
    """Render AWS best practices and Trusted Advisor checks"""
    st.markdown("### ✅ AWS Best Practices Advisor")
    
    session = st.session_state.get('boto3_session')
    advisor_data = fetch_trusted_advisor_checks(session)
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cost_issues = len([c for c in advisor_data['cost_optimization'] if c['status'] in ['error', 'warning']])
        st.metric("Cost Issues", cost_issues)
    
    with col2:
        security_issues = len([c for c in advisor_data['security'] if c['status'] in ['error', 'warning']])
        st.metric("Security Issues", security_issues)
    
    with col3:
        perf_issues = len([c for c in advisor_data['performance'] if c['status'] in ['error', 'warning']])
        st.metric("Performance", perf_issues)
    
    with col4:
        ft_issues = len([c for c in advisor_data['fault_tolerance'] if c['status'] in ['error', 'warning']])
        st.metric("Fault Tolerance", ft_issues)
    
    with col5:
        limit_issues = len([c for c in advisor_data['service_limits'] if c['status'] in ['error', 'warning']])
        st.metric("Service Limits", limit_issues)
    
    st.markdown("---")
    
    # Detailed checks by category
    categories = [
        ("💰 Cost Optimization", advisor_data['cost_optimization']),
        ("🔒 Security", advisor_data['security']),
        ("⚡ Performance", advisor_data['performance']),
        ("🔧 Fault Tolerance", advisor_data['fault_tolerance']),
        ("📊 Service Limits", advisor_data['service_limits'])
    ]
    
    for category_name, checks in categories:
        if checks:
            st.markdown(f"#### {category_name}")
            
            for check in checks:
                status_color = {
                    'ok': '#4CAF50',
                    'warning': '#FF9900',
                    'error': '#F44336',
                    'unknown': '#9E9E9E'
                }.get(check['status'], '#9E9E9E')
                
                status_icon = {
                    'ok': '✅',
                    'warning': '⚠️',
                    'error': '❌',
                    'unknown': '❓'
                }.get(check['status'], '❓')
                
                flagged = check.get('flagged_resources', 0)
                if isinstance(flagged, list):
                    flagged = len(flagged)
                
                st.markdown(f"""
                <div style='background: white; 
                            padding: 1rem; 
                            border-radius: 5px; 
                            margin: 0.5rem 0;
                            border-left: 5px solid {status_color};'>
                    <strong>{status_icon} {check['name']}</strong><br>
                    {check['description']}<br>
                    <span style='color: {status_color}; font-weight: bold;'>
                        Flagged Resources: {flagged}
                    </span>
                </div>
                """, unsafe_allow_html=True)

def render_anomaly_detection():
    """Render cost anomaly detection"""
    st.markdown("### 🚨 Cost Anomaly Detection")
    
    # Fetch anomalies
    ce_client = st.session_state.get('aws_clients', {}).get('ce')
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    anomalies = fetch_cost_anomalies(ce_client, start_date, end_date)
    
    # Summary metrics
    total_impact = sum(a.get('Impact', {}).get('TotalImpact', 0) for a in anomalies)
    high_severity = len([a for a in anomalies if a.get('AnomalyScore', {}).get('CurrentScore', 0) > 0.75])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Anomalies", len(anomalies))
    with col2:
        st.metric("High Severity", high_severity)
    with col3:
        st.metric("Total Impact", f"${total_impact:,.2f}")
    
    st.markdown("---")
    
    if anomalies:
        st.markdown("#### 🔍 Detected Anomalies")
        
        for anomaly in anomalies:
            score = anomaly.get('AnomalyScore', {}).get('CurrentScore', 0)
            impact = anomaly.get('Impact', {}).get('TotalImpact', 0)
            dimension = anomaly.get('DimensionValue', 'Unknown')
            
            severity_color = '#F44336' if score > 0.75 else '#FF9900' if score > 0.5 else '#FFC107'
            severity_text = 'HIGH' if score > 0.75 else 'MEDIUM' if score > 0.5 else 'LOW'
            
            st.markdown(f"""
            <div style='background: white; 
                        padding: 1.5rem; 
                        border-radius: 8px; 
                        margin: 1rem 0;
                        border-left: 5px solid {severity_color};
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h4 style='margin: 0; color: #232F3E;'>{dimension} Anomaly</h4>
                        <p style='margin: 0.5rem 0; color: #666;'>
                            {anomaly.get('AnomalyStartDate', 'N/A')} to {anomaly.get('AnomalyEndDate', 'N/A')}
                        </p>
                    </div>
                    <div style='text-align: right;'>
                        <span style='background: {severity_color}; 
                                     color: white; 
                                     padding: 0.3rem 0.8rem; 
                                     border-radius: 15px; 
                                     font-weight: bold;'>
                            {severity_text}
                        </span>
                    </div>
                </div>
                <div style='margin-top: 1rem;'>
                    <strong>Anomaly Score:</strong> {score:.2f}<br>
                    <strong>Financial Impact:</strong> <span style='color: #F44336; font-weight: bold;'>
                        ${impact:,.2f}
                    </span><br>
                    <strong>Root Cause:</strong> {anomaly.get('RootCauses', [{}])[0].get('Service', 'Unknown')} 
                    in {anomaly.get('RootCauses', [{}])[0].get('Region', 'Unknown')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No cost anomalies detected in the last 30 days!")
    
    # Pattern analysis
    st.markdown("---")
    st.markdown("#### 📈 Spending Pattern Analysis")
    
    ce_client = st.session_state.get('aws_clients', {}).get('ce')
    cost_data = fetch_cost_data(ce_client, start_date, end_date, 'DAILY')
    patterns = detect_spending_patterns(cost_data)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Trend", patterns['trend'].upper())
        st.metric("Avg Daily Spend", f"${patterns['avg_daily_spend']:.2f}")
    with col2:
        st.metric("Max Spike", f"${patterns['max_spike']:.2f}")
        st.metric("Spike Events", patterns.get('spike_count', 0))

def render_chargeback_allocation():
    """Render chargeback and cost allocation by portfolio"""
    st.markdown("### 💳 Chargeback & Cost Allocation")
    
    # Fetch portfolio costs
    ce_client = st.session_state.get('aws_clients', {}).get('ce')
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    portfolio_costs = fetch_cost_by_portfolio(ce_client, start_date, end_date)
    
    # Extract portfolio data
    if portfolio_costs and 'ResultsByTime' in portfolio_costs:
        portfolios = {}
        for result in portfolio_costs['ResultsByTime']:
            for group in result.get('Groups', []):
                portfolio = group['Keys'][0] if group.get('Keys') else 'Untagged'
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                portfolios[portfolio] = portfolios.get(portfolio, 0) + cost
        
        total = sum(portfolios.values())
        
        # Summary cards
        st.markdown("#### 📊 Monthly Cost Allocation by Portfolio")
        
        cols = st.columns(len(portfolios) if portfolios else 3)
        for idx, (portfolio, cost) in enumerate(sorted(portfolios.items(), key=lambda x: x[1], reverse=True)):
            with cols[idx % len(cols)]:
                percentage = (cost / total * 100) if total > 0 else 0
                st.markdown(f"""
                <div class='metric-card'>
                    <h3 style='color: #FF9900; margin: 0;'>{portfolio}</h3>
                    <h2 style='color: white; margin: 0.5rem 0;'>${cost:,.2f}</h2>
                    <p style='color: #E8F4F8; margin: 0;'>{percentage:.1f}% of total</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Visualization
        df_portfolios = pd.DataFrame([
            {'Portfolio': k, 'Cost': v, 'Percentage': f"{(v/total*100):.1f}%"}
            for k, v in sorted(portfolios.items(), key=lambda x: x[1], reverse=True)
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_bar = px.bar(
                df_portfolios,
                x='Portfolio',
                y='Cost',
                title='Cost by Portfolio',
                color='Cost',
                color_continuous_scale='Oranges'
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            fig_pie = px.pie(
                df_portfolios,
                values='Cost',
                names='Portfolio',
                title='Cost Distribution',
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Detailed allocation table
        st.markdown("---")
        st.markdown("#### 📋 Detailed Cost Allocation")
        
        df_portfolios['Cost'] = df_portfolios['Cost'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_portfolios, use_container_width=True, hide_index=True)
        
        # Export options
        if st.button("📥 Export Chargeback Report"):
            csv = df_portfolios.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"chargeback_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def render_inventory_dashboard():
    """Render inventory dashboard with cost correlation"""
    st.markdown("### 📦 Resource Inventory with Cost Correlation")
    
    session = st.session_state.get('boto3_session')
    inventory = fetch_resource_inventory(session)
    
    # Calculate totals
    total_monthly_cost = 0
    resource_counts = {}
    
    for service, resources in inventory.items():
        resource_counts[service] = len(resources)
        for resource in resources:
            cost = resource.get('EstimatedMonthlyCost', 0)
            if isinstance(cost, (int, float)):
                total_monthly_cost += cost
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("EC2 Instances", resource_counts.get('ec2', 0))
    with col2:
        st.metric("RDS Databases", resource_counts.get('rds', 0))
    with col3:
        st.metric("S3 Buckets", resource_counts.get('s3', 0))
    with col4:
        st.metric("Lambda Functions", resource_counts.get('lambda', 0))
    with col5:
        st.metric("EBS Volumes", resource_counts.get('ebs', 0))
    
    st.markdown("---")
    
    # Total cost
    st.markdown(f"""
    <div class='score-card excellent'>
        <h3>💰 Total Estimated Monthly Cost</h3>
        <h1 style='color: #FF9900; margin: 1rem 0;'>${total_monthly_cost:,.2f}</h1>
        <p>Based on current resource inventory and usage patterns</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Resource details tabs
    resource_tabs = st.tabs(["🖥️ EC2", "🗄️ RDS", "📦 S3", "⚡ Lambda", "💾 EBS"])
    
    # EC2 Tab
    with resource_tabs[0]:
        st.markdown("#### EC2 Instances")
        if inventory['ec2']:
            df_ec2 = pd.DataFrame(inventory['ec2'])
            # Format cost column
            if 'EstimatedMonthlyCost' in df_ec2.columns:
                df_ec2['EstimatedMonthlyCost'] = df_ec2['EstimatedMonthlyCost'].apply(
                    lambda x: f"${x:.2f}" if isinstance(x, (int, float)) else x
                )
            st.dataframe(df_ec2, use_container_width=True, hide_index=True)
        else:
            st.info("No EC2 instances found")
    
    # RDS Tab
    with resource_tabs[1]:
        st.markdown("#### RDS Database Instances")
        if inventory['rds']:
            df_rds = pd.DataFrame(inventory['rds'])
            if 'EstimatedMonthlyCost' in df_rds.columns:
                df_rds['EstimatedMonthlyCost'] = df_rds['EstimatedMonthlyCost'].apply(
                    lambda x: f"${x:.2f}" if isinstance(x, (int, float)) else x
                )
            st.dataframe(df_rds, use_container_width=True, hide_index=True)
        else:
            st.info("No RDS instances found")
    
    # S3 Tab
    with resource_tabs[2]:
        st.markdown("#### S3 Buckets")
        if inventory['s3']:
            df_s3 = pd.DataFrame(inventory['s3'])
            if 'EstimatedMonthlyCost' in df_s3.columns:
                df_s3['EstimatedMonthlyCost'] = df_s3['EstimatedMonthlyCost'].apply(
                    lambda x: f"${x:.2f}" if isinstance(x, (int, float)) else x
                )
            st.dataframe(df_s3, use_container_width=True, hide_index=True)
        else:
            st.info("No S3 buckets found")
    
    # Lambda Tab
    with resource_tabs[3]:
        st.markdown("#### Lambda Functions")
        if inventory['lambda']:
            df_lambda = pd.DataFrame(inventory['lambda'])
            st.dataframe(df_lambda, use_container_width=True, hide_index=True)
        else:
            st.info("No Lambda functions found")
    
    # EBS Tab
    with resource_tabs[4]:
        st.markdown("#### EBS Volumes")
        if inventory['ebs']:
            df_ebs = pd.DataFrame(inventory['ebs'])
            if 'EstimatedMonthlyCost' in df_ebs.columns:
                df_ebs['EstimatedMonthlyCost'] = df_ebs['EstimatedMonthlyCost'].apply(
                    lambda x: f"${x:.2f}" if isinstance(x, (int, float)) else x
                )
            st.dataframe(df_ebs, use_container_width=True, hide_index=True)
        else:
            st.info("No EBS volumes found")

def render_tag_management():
    """Render tag management and compliance"""
    st.markdown("### 🏷️ Tag Management & Compliance")
    
    session = st.session_state.get('boto3_session')
    tag_compliance = fetch_tag_compliance(session)
    
    # Compliance overview
    total = tag_compliance['total_resources']
    compliant = tag_compliance['compliant_resources']
    compliance_rate = (compliant / total * 100) if total > 0 else 0
    
    # Status color
    status_color = '#4CAF50' if compliance_rate >= 80 else '#FF9900' if compliance_rate >= 60 else '#F44336'
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {status_color} 0%, {status_color}CC 100%); 
                padding: 2rem; 
                border-radius: 10px; 
                text-align: center; 
                margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0;'>Tag Compliance Score</h2>
        <h1 style='color: white; font-size: 4rem; margin: 1rem 0;'>{compliance_rate:.1f}%</h1>
        <p style='color: white; margin: 0;'>{compliant} out of {total} resources are fully compliant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Resources", tag_compliance['total_resources'])
    with col2:
        st.metric("Fully Compliant", tag_compliance['compliant_resources'])
    with col3:
        st.metric("Partially Tagged", tag_compliance['partially_tagged'])
    with col4:
        st.metric("Untagged", tag_compliance['untagged_resources'])
    
    st.markdown("---")
    
    # Tag coverage
    st.markdown("#### 📊 Tag Coverage Analysis")
    
    if tag_compliance['tag_coverage']:
        df_coverage = pd.DataFrame([
            {
                'Tag': tag,
                'Resources': count,
                'Coverage': f"{(count / total * 100):.1f}%"
            }
            for tag, count in tag_compliance['tag_coverage'].items()
        ])
        
        fig_coverage = px.bar(
            df_coverage,
            x='Tag',
            y='Resources',
            title='Tag Coverage by Key',
            color='Resources',
            color_continuous_scale='Oranges',
            text='Coverage'
        )
        fig_coverage.update_traces(textposition='outside')
        st.plotly_chart(fig_coverage, use_container_width=True)
    
    st.markdown("---")
    
    # Resources by service
    st.markdown("#### 🔧 Resources by Service")
    
    if tag_compliance['resources_by_service']:
        df_services = pd.DataFrame([
            {'Service': service.upper(), 'Count': count}
            for service, count in sorted(
                tag_compliance['resources_by_service'].items(),
                key=lambda x: x[1],
                reverse=True
            )
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                df_services,
                values='Count',
                names='Service',
                title='Resource Distribution',
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.dataframe(df_services, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Tag management actions
    st.markdown("#### ⚙️ Tag Management Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Bulk Tag Application")
        
        tag_key = st.text_input("Tag Key", placeholder="Environment")
        tag_value = st.text_input("Tag Value", placeholder="Production")
        resource_filter = st.selectbox(
            "Resource Type",
            ["All", "ec2", "rds", "s3", "lambda"]
        )
        
        if st.button("🏷️ Apply Tags", type="primary"):
            st.info("Tag application would be executed here")
            st.code(f"""
# Applying tags:
Tag: {tag_key}={tag_value}
Filter: {resource_filter}
Status: Simulated (Demo Mode)
            """)
    
    with col2:
        st.markdown("##### Tag Compliance Report")
        
        if st.button("📊 Generate Report"):
            report_data = {
                'Total Resources': tag_compliance['total_resources'],
                'Compliant': tag_compliance['compliant_resources'],
                'Non-Compliant': tag_compliance['total_resources'] - tag_compliance['compliant_resources'],
                'Compliance Rate': f"{compliance_rate:.1f}%",
            }
            
            st.json(report_data)
            
            if st.button("📥 Download Report"):
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(report_data, indent=2),
                    file_name=f"tag_compliance_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )

def generate_cleanup_script(unused_resources: List[Dict]) -> str:
    """Generate AWS CLI cleanup script for unused resources"""
    script = "#!/bin/bash\n"
    script += "# AWS Resource Cleanup Script\n"
    script += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    script += "# WARNING: Review before executing!\n\n"
    
    for resource in unused_resources:
        resource_type = resource['resource_type']
        resource_id = resource['resource_id']
        
        if resource_type == 'EBS Volume':
            script += f"# Delete EBS Volume: {resource_id}\n"
            script += f"aws ec2 delete-volume --volume-id {resource_id}\n\n"
        
        elif resource_type == 'Elastic IP':
            script += f"# Release Elastic IP: {resource_id}\n"
            script += f"aws ec2 release-address --allocation-id <ALLOCATION_ID>\n\n"
        
        elif resource_type == 'EBS Snapshot':
            script += f"# Delete EBS Snapshot: {resource_id}\n"
            script += f"aws ec2 delete-snapshot --snapshot-id {resource_id}\n\n"
    
    script += "\necho 'Cleanup completed!'\n"
    return script