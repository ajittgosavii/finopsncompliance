"""
Enhanced Account Lifecycle Management Module
Cloud Compliance Canvas - AWS re:Invent 2025

Features:
- Template Marketplace with 15+ pre-built templates
- Real-time Cost Forecasting
- Pre-provisioning Readiness Validation
- Visual Workflow Orchestration
- Compliance Scorecard Preview
- Batch Account Provisioning
- Account Modification/Evolution
- Approval Workflow Integration
- Account Cloning
- Offboarding/Decommissioning
- AI Configuration Assistant
- Network Topology Designer
- Dependency Mapping
- Portfolio Dashboard Overview

Version: 2.0 Enterprise
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time
from typing import Dict, List, Any, Tuple
import json

# ============================================================================
# ACCOUNT TEMPLATES LIBRARY
# ============================================================================

ACCOUNT_TEMPLATES = {
    "financial_services_prod": {
        "name": "Financial Services - Production",
        "description": "PCI-DSS and SOC 2 compliant production environment for financial workloads",
        "icon": "🏦",
        "category": "Production",
        "compliance_frameworks": ["SOC 2 Type II", "PCI-DSS v4.0", "ISO 27001"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 38000, "max": 48000, "average": 42000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": True,
        },
        "guardrails": ["SCPs", "OPA", "Tag Policies"],
        "budget_alert": 80,
        "compliance_scores": {"SOC 2": 96, "PCI-DSS": 89, "ISO 27001": 92},
        "features": ["Multi-AZ", "Encrypted EBS", "CloudWatch Detailed", "WAF", "Shield Advanced"],
        "network": {
            "vpc_cidr": "10.100.0.0/16",
            "availability_zones": 3,
            "nat_gateways": 3,
            "transit_gateway": True
        }
    },
    "healthcare_hipaa": {
        "name": "Healthcare - HIPAA Compliant",
        "description": "HIPAA-ready environment for healthcare applications and PHI data",
        "icon": "🏥",
        "category": "Production",
        "compliance_frameworks": ["HIPAA", "SOC 2 Type II", "HITRUST"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 32000, "max": 42000, "average": 36000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": True,
        },
        "guardrails": ["SCPs", "OPA", "HIPAA Guardrails"],
        "budget_alert": 85,
        "compliance_scores": {"HIPAA": 94, "SOC 2": 92, "HITRUST": 88},
        "features": ["Data Classification", "Encryption at Rest", "Audit Logging", "Access Controls"],
        "network": {
            "vpc_cidr": "10.110.0.0/16",
            "availability_zones": 3,
            "nat_gateways": 2,
            "transit_gateway": True
        }
    },
    "dev_sandbox": {
        "name": "Development Sandbox",
        "description": "Cost-optimized development environment with baseline security",
        "icon": "🧪",
        "category": "Development",
        "compliance_frameworks": ["Baseline Security"],
        "environment": "Development",
        "region": "us-east-1",
        "estimated_cost": {"min": 2500, "max": 5000, "average": 3500},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": False,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": False,
            "macie": False,
        },
        "guardrails": ["SCPs", "Cost Controls"],
        "budget_alert": 70,
        "compliance_scores": {"Baseline": 85},
        "features": ["Auto-shutdown", "Spot Instances", "Basic Monitoring"],
        "network": {
            "vpc_cidr": "10.200.0.0/16",
            "availability_zones": 2,
            "nat_gateways": 1,
            "transit_gateway": False
        }
    },
    "data_analytics": {
        "name": "Data Analytics Platform",
        "description": "Optimized for big data processing with Redshift, EMR, and Athena",
        "icon": "📊",
        "category": "Analytics",
        "compliance_frameworks": ["SOC 2 Type II", "ISO 27001"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 45000, "max": 65000, "average": 52000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": True,
        },
        "guardrails": ["SCPs", "OPA", "Data Governance"],
        "budget_alert": 80,
        "compliance_scores": {"SOC 2": 94, "ISO 27001": 91},
        "features": ["S3 Data Lake", "Redshift Cluster", "EMR", "Glue", "Athena"],
        "network": {
            "vpc_cidr": "10.120.0.0/16",
            "availability_zones": 3,
            "nat_gateways": 2,
            "transit_gateway": True
        }
    },
    "ml_training": {
        "name": "ML/AI Training Environment",
        "description": "GPU-enabled environment for machine learning model training",
        "icon": "🤖",
        "category": "AI/ML",
        "compliance_frameworks": ["SOC 2 Type II"],
        "environment": "Production",
        "region": "us-west-2",
        "estimated_cost": {"min": 55000, "max": 85000, "average": 68000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": False,
        },
        "guardrails": ["SCPs", "Cost Controls", "GPU Limits"],
        "budget_alert": 85,
        "compliance_scores": {"SOC 2": 89},
        "features": ["SageMaker", "EC2 GPU Instances", "S3 Model Store", "MLflow"],
        "network": {
            "vpc_cidr": "10.130.0.0/16",
            "availability_zones": 2,
            "nat_gateways": 2,
            "transit_gateway": True
        }
    },
    "saas_multitenant": {
        "name": "Multi-Tenant SaaS Platform",
        "description": "Isolated tenant environments with shared infrastructure",
        "icon": "🏢",
        "category": "Production",
        "compliance_frameworks": ["SOC 2 Type II", "ISO 27001", "GDPR"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 42000, "max": 58000, "average": 48000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": True,
        },
        "guardrails": ["SCPs", "OPA", "Tenant Isolation"],
        "budget_alert": 80,
        "compliance_scores": {"SOC 2": 95, "ISO 27001": 93, "GDPR": 91},
        "features": ["Multi-tenant DB", "Tenant Isolation", "API Gateway", "Cognito"],
        "network": {
            "vpc_cidr": "10.140.0.0/16",
            "availability_zones": 3,
            "nat_gateways": 3,
            "transit_gateway": True
        }
    },
    "disaster_recovery": {
        "name": "Disaster Recovery",
        "description": "DR environment with automated failover capabilities",
        "icon": "🔄",
        "category": "DR/Backup",
        "compliance_frameworks": ["SOC 2 Type II", "ISO 27001"],
        "environment": "Production",
        "region": "us-west-2",
        "estimated_cost": {"min": 18000, "max": 28000, "average": 22000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": False,
        },
        "guardrails": ["SCPs", "DR Policies"],
        "budget_alert": 75,
        "compliance_scores": {"SOC 2": 92, "ISO 27001": 90},
        "features": ["Cross-region Replication", "RDS Read Replicas", "Automated Snapshots"],
        "network": {
            "vpc_cidr": "10.150.0.0/16",
            "availability_zones": 3,
            "nat_gateways": 2,
            "transit_gateway": True
        }
    },
    "compliance_audit": {
        "name": "Compliance Testing & Audit",
        "description": "Isolated environment for compliance testing and audit activities",
        "icon": "🔍",
        "category": "Testing",
        "compliance_frameworks": ["SOC 2 Type II", "PCI-DSS v4.0", "HIPAA", "ISO 27001"],
        "environment": "Staging",
        "region": "us-east-1",
        "estimated_cost": {"min": 8000, "max": 12000, "average": 9500},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": True,
        },
        "guardrails": ["SCPs", "OPA", "Audit Controls"],
        "budget_alert": 90,
        "compliance_scores": {"SOC 2": 98, "PCI-DSS": 96, "HIPAA": 95, "ISO 27001": 97},
        "features": ["Evidence Collection", "Audit Logging", "Compliance Scanning"],
        "network": {
            "vpc_cidr": "10.160.0.0/16",
            "availability_zones": 2,
            "nat_gateways": 1,
            "transit_gateway": False
        }
    },
    "shared_services": {
        "name": "Shared Services Hub",
        "description": "Centralized services: SSO, DNS, monitoring, logging",
        "icon": "🔗",
        "category": "Infrastructure",
        "compliance_frameworks": ["SOC 2 Type II", "ISO 27001"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 15000, "max": 22000, "average": 18000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": False,
        },
        "guardrails": ["SCPs", "OPA", "Cross-Account Policies"],
        "budget_alert": 80,
        "compliance_scores": {"SOC 2": 93, "ISO 27001": 91},
        "features": ["AWS SSO", "Route 53", "CloudWatch", "S3 Logging", "Transit Gateway Hub"],
        "network": {
            "vpc_cidr": "10.0.0.0/16",
            "availability_zones": 3,
            "nat_gateways": 2,
            "transit_gateway": True
        }
    },
    "edge_cdn": {
        "name": "Edge & CDN Services",
        "description": "CloudFront and global edge computing infrastructure",
        "icon": "🌍",
        "category": "Infrastructure",
        "compliance_frameworks": ["SOC 2 Type II"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 25000, "max": 45000, "average": 32000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": False,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": False,
            "macie": False,
        },
        "guardrails": ["SCPs", "CDN Policies"],
        "budget_alert": 80,
        "compliance_scores": {"SOC 2": 88},
        "features": ["CloudFront", "Lambda@Edge", "WAF", "Shield Standard"],
        "network": {
            "vpc_cidr": "10.170.0.0/16",
            "availability_zones": 2,
            "nat_gateways": 1,
            "transit_gateway": False
        }
    },
    "iot_platform": {
        "name": "IoT Platform",
        "description": "IoT Core, device management, and real-time data processing",
        "icon": "📡",
        "category": "IoT",
        "compliance_frameworks": ["SOC 2 Type II", "ISO 27001"],
        "environment": "Production",
        "region": "us-west-2",
        "estimated_cost": {"min": 28000, "max": 42000, "average": 34000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": False,
        },
        "guardrails": ["SCPs", "IoT Policies", "Device Management"],
        "budget_alert": 80,
        "compliance_scores": {"SOC 2": 90, "ISO 27001": 88},
        "features": ["IoT Core", "Greengrass", "Kinesis", "Lambda", "DynamoDB"],
        "network": {
            "vpc_cidr": "10.180.0.0/16",
            "availability_zones": 2,
            "nat_gateways": 2,
            "transit_gateway": True
        }
    },
    "container_platform": {
        "name": "Container Orchestration Platform",
        "description": "EKS-based microservices platform with service mesh",
        "icon": "🐳",
        "category": "Platform",
        "compliance_frameworks": ["SOC 2 Type II", "ISO 27001"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 38000, "max": 52000, "average": 44000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": False,
        },
        "guardrails": ["SCPs", "OPA", "Pod Security Policies"],
        "budget_alert": 80,
        "compliance_scores": {"SOC 2": 91, "ISO 27001": 89},
        "features": ["EKS Cluster", "Fargate", "ECR", "Service Mesh", "ArgoCD"],
        "network": {
            "vpc_cidr": "10.190.0.0/16",
            "availability_zones": 3,
            "nat_gateways": 3,
            "transit_gateway": True
        }
    },
    "security_operations": {
        "name": "Security Operations Center",
        "description": "Centralized security monitoring and incident response",
        "icon": "🛡️",
        "category": "Security",
        "compliance_frameworks": ["SOC 2 Type II", "ISO 27001", "NIST CSF"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 22000, "max": 32000, "average": 26000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": True,
        },
        "guardrails": ["SCPs", "OPA", "Security Baseline"],
        "budget_alert": 85,
        "compliance_scores": {"SOC 2": 97, "ISO 27001": 95, "NIST CSF": 93},
        "features": ["Security Hub Aggregation", "SIEM", "Threat Intelligence", "Incident Response"],
        "network": {
            "vpc_cidr": "10.210.0.0/16",
            "availability_zones": 2,
            "nat_gateways": 2,
            "transit_gateway": True
        }
    },
    "serverless_app": {
        "name": "Serverless Application",
        "description": "Event-driven serverless architecture with Lambda and API Gateway",
        "icon": "⚡",
        "category": "Application",
        "compliance_frameworks": ["SOC 2 Type II"],
        "environment": "Production",
        "region": "us-east-1",
        "estimated_cost": {"min": 12000, "max": 22000, "average": 16000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": False,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": False,
            "macie": False,
        },
        "guardrails": ["SCPs", "Lambda Concurrency Limits"],
        "budget_alert": 75,
        "compliance_scores": {"SOC 2": 87},
        "features": ["Lambda", "API Gateway", "DynamoDB", "EventBridge", "Step Functions"],
        "network": {
            "vpc_cidr": "10.220.0.0/16",
            "availability_zones": 2,
            "nat_gateways": 0,
            "transit_gateway": False
        }
    },
    "gaming_platform": {
        "name": "Gaming Platform",
        "description": "Low-latency gaming infrastructure with GameLift",
        "icon": "🎮",
        "category": "Gaming",
        "compliance_frameworks": ["SOC 2 Type II"],
        "environment": "Production",
        "region": "us-west-2",
        "estimated_cost": {"min": 48000, "max": 72000, "average": 58000},
        "security_controls": {
            "security_hub": True,
            "guardduty": True,
            "config_rules": True,
            "inspector": True,
            "cloudtrail": True,
            "s3_encryption": True,
            "vpc_flow_logs": True,
            "macie": False,
        },
        "guardrails": ["SCPs", "GameLift Policies"],
        "budget_alert": 80,
        "compliance_scores": {"SOC 2": 86},
        "features": ["GameLift", "ElastiCache", "DynamoDB", "CloudFront", "Low-latency Networking"],
        "network": {
            "vpc_cidr": "10.230.0.0/16",
            "availability_zones": 3,
            "nat_gateways": 3,
            "transit_gateway": False
        }
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_cost_forecast(template_key: str, modifications: Dict = None) -> Dict:
    """Calculate detailed cost forecast based on template and modifications"""
    template = ACCOUNT_TEMPLATES[template_key]
    base_cost = template["estimated_cost"]["average"]
    
    breakdown = {
        "Compute": base_cost * 0.35,
        "Storage": base_cost * 0.20,
        "Security Services": base_cost * 0.15,
        "Networking": base_cost * 0.12,
        "Monitoring & Logging": base_cost * 0.08,
        "Database": base_cost * 0.10,
    }
    
    # Add optimizations
    optimizations = []
    potential_savings = 0
    
    if template["environment"] == "Production":
        optimizations.append({
            "name": "Reserved Instances (1-year)",
            "savings": base_cost * 0.18,
            "description": "Commit to 1-year RIs for predictable workloads"
        })
        potential_savings += base_cost * 0.18
        
        optimizations.append({
            "name": "Savings Plans",
            "savings": base_cost * 0.12,
            "description": "Flexible compute savings across EC2, Lambda, Fargate"
        })
        potential_savings += base_cost * 0.12
    
    return {
        "base_monthly": base_cost,
        "min_monthly": template["estimated_cost"]["min"],
        "max_monthly": template["estimated_cost"]["max"],
        "breakdown": breakdown,
        "optimizations": optimizations,
        "potential_savings": potential_savings,
        "optimized_monthly": base_cost - (potential_savings * 0.7)  # 70% adoption
    }

def run_readiness_validation(config: Dict) -> Dict:
    """Run pre-provisioning validation checks"""
    checks = []
    
    # Simulate various checks
    check_definitions = [
        ("Organizations parent account accessible", "critical", True, ""),
        ("Control Tower deployed and healthy", "critical", True, ""),
        ("Sufficient service limits available", "critical", True, ""),
        ("Required IAM permissions present", "critical", True, ""),
        ("Account name unique", "high", random.choice([True, True, False]), "Name 'Production-FinServices-001' already exists"),
        ("Budget within portfolio allocation", "high", True, ""),
        ("Region approved for compliance framework", "medium", random.choice([True, True, True, False]), "us-west-1 not approved for HIPAA workloads"),
        ("Network CIDR no conflicts", "high", random.choice([True, True, False]), "CIDR 10.100.0.0/16 overlaps with existing VPC"),
        ("Security Hub capacity available", "low", True, ""),
        ("Cost Explorer API accessible", "low", True, ""),
    ]
    
    passed = 0
    warnings = 0
    errors = 0
    
    for name, severity, status, message in check_definitions:
        check = {
            "name": name,
            "severity": severity,
            "status": "pass" if status else "fail",
            "message": message
        }
        checks.append(check)
        
        if status:
            passed += 1
        else:
            if severity == "critical":
                errors += 1
            else:
                warnings += 1
    
    total = len(checks)
    score = (passed / total) * 100
    
    return {
        "checks": checks,
        "total": total,
        "passed": passed,
        "warnings": warnings,
        "errors": errors,
        "score": score,
        "ready": errors == 0
    }

def generate_compliance_preview(template_key: str) -> Dict:
    """Generate compliance scorecard preview"""
    template = ACCOUNT_TEMPLATES[template_key]
    frameworks = template["compliance_frameworks"]
    scores = template["compliance_scores"]
    
    details = []
    for framework in frameworks:
        if framework in scores:
            score = scores[framework]
            
            # Generate category breakdowns
            categories = []
            if framework == "SOC 2 Type II":
                categories = [
                    {"name": "Security", "score": score + random.randint(-3, 3)},
                    {"name": "Availability", "score": score + random.randint(-5, 2)},
                    {"name": "Confidentiality", "score": score + random.randint(-4, 1)},
                    {"name": "Processing Integrity", "score": score + random.randint(-2, 3)},
                ]
            elif framework == "PCI-DSS v4.0":
                categories = [
                    {"name": "Network Security", "score": score + random.randint(-2, 8)},
                    {"name": "Cardholder Data Protection", "score": score + random.randint(-10, 5)},
                    {"name": "Access Control", "score": score + random.randint(-5, 3)},
                    {"name": "Monitoring & Testing", "score": score + random.randint(-4, 2)},
                ]
            elif framework == "HIPAA":
                categories = [
                    {"name": "Administrative Safeguards", "score": score + random.randint(-3, 4)},
                    {"name": "Physical Safeguards", "score": score + random.randint(-6, 2)},
                    {"name": "Technical Safeguards", "score": score + random.randint(-2, 5)},
                ]
            else:
                categories = [{"name": "Overall", "score": score}]
            
            # Identify gaps
            gaps = []
            improvements = []
            
            for cat in categories:
                if cat["score"] < 90:
                    gaps.append(f"{cat['name']}: {100 - cat['score']}% gap")
                    if cat["score"] < 85:
                        improvements.append(f"Critical: Improve {cat['name']} controls")
                    elif cat["score"] < 90:
                        improvements.append(f"Recommended: Enhance {cat['name']} coverage")
            
            details.append({
                "framework": framework,
                "score": score,
                "categories": categories,
                "gaps": gaps,
                "improvements": improvements,
                "audit_ready": score >= 85,
                "evidence_items": random.randint(800, 1500)
            })
    
    overall_score = sum([d["score"] for d in details]) / len(details) if details else 0
    
    return {
        "overall_score": round(overall_score, 1),
        "frameworks": details,
        "audit_ready": all([d["audit_ready"] for d in details]),
        "total_evidence": sum([d["evidence_items"] for d in details])
    }

def generate_workflow_steps() -> List[Dict]:
    """Generate workflow orchestration steps"""
    return [
        {"name": "Account Request Validation", "duration": 2, "status": "complete", "substeps": ["Validate inputs", "Check permissions"]},
        {"name": "AWS Account Creation", "duration": 5, "status": "complete", "substeps": ["Call Organizations API", "Wait for account"]},
        {"name": "Security Baseline Deployment", "duration": 4, "status": "in_progress", "substeps": [
            {"name": "Enable Security Hub", "duration": 2, "status": "complete"},
            {"name": "Configure GuardDuty", "duration": 2, "status": "in_progress"},
            {"name": "Deploy Config Rules", "duration": 3, "status": "pending"},
            {"name": "Setup CloudTrail", "duration": 1, "status": "pending"},
        ]},
        {"name": "Compliance Controls", "duration": 3, "status": "pending", "substeps": ["Apply framework controls", "Validate compliance"]},
        {"name": "Network Configuration", "duration": 2, "status": "pending", "substeps": ["Create VPC", "Configure subnets", "Deploy NAT gateways"]},
        {"name": "Budget & Cost Tracking", "duration": 1, "status": "pending", "substeps": ["Create budget", "Configure alerts"]},
        {"name": "Integration Hub Sync", "duration": 1, "status": "pending", "substeps": ["Jira ticket", "Slack notification", "ServiceNow CMDB"]},
        {"name": "Validation & Activation", "duration": 2, "status": "pending", "substeps": ["Final compliance check", "Activate account"]},
    ]

# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_enhanced_account_lifecycle():
    """Render the enhanced Account Lifecycle Management interface"""
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #232F3E 0%, #37475A 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0;'>⚙️ Account Lifecycle Management</h2>
        <p style='color: #E8F4F8; margin: 0.5rem 0 0 0;'>Automated provisioning, modification, and decommissioning of AWS accounts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tabs = st.tabs([
        "📊 Portfolio Dashboard",
        "➕ Create Account", 
        "📚 Template Marketplace",
        "📦 Batch Provisioning",
        "🔄 Account Modification",
        "👯 Clone Account",
        "🔴 Offboarding",
        "✅ Approvals",
        "🤖 AI Assistant",
        "🌐 Network Designer",
        "🔗 Dependencies"
    ])
    
    # Tab 0: Portfolio Dashboard
    with tabs[0]:
        render_portfolio_dashboard()
    
    # Tab 1: Create Account
    with tabs[1]:
        render_create_account()
    
    # Tab 2: Template Marketplace
    with tabs[2]:
        render_template_marketplace()
    
    # Tab 3: Batch Provisioning
    with tabs[3]:
        render_batch_provisioning()
    
    # Tab 4: Account Modification
    with tabs[4]:
        render_account_modification()
    
    # Tab 5: Clone Account
    with tabs[5]:
        render_account_cloning()
    
    # Tab 6: Offboarding
    with tabs[6]:
        render_offboarding()
    
    # Tab 7: Approvals
    with tabs[7]:
        render_approval_workflow()
    
    # Tab 8: AI Assistant
    with tabs[8]:
        render_ai_assistant()
    
    # Tab 9: Network Designer
    with tabs[9]:
        render_network_designer()
    
    # Tab 10: Dependencies
    with tabs[10]:
        render_dependency_mapping()

# ============================================================================
# TAB RENDER FUNCTIONS
# ============================================================================

def render_portfolio_dashboard():
    """Render portfolio overview dashboard"""
    st.markdown("### 📊 Account Portfolio Overview")
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Accounts", "127", "+3 this month")
    with col2:
        st.metric("Production", "67", "52.8%")
    with col3:
        st.metric("Development", "45", "35.4%")
    with col4:
        st.metric("Staging", "15", "11.8%")
    with col5:
        st.metric("Monthly Spend", "$2.4M", "+5.2%")
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Accounts by Environment")
        env_data = pd.DataFrame({
            "Environment": ["Production", "Development", "Staging", "Testing", "DR"],
            "Count": [67, 45, 15, 8, 12]
        })
        fig = px.pie(env_data, values="Count", names="Environment", hole=0.4)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Compliance Distribution")
        compliance_data = pd.DataFrame({
            "Framework": ["SOC 2", "PCI-DSS", "HIPAA", "ISO 27001", "NIST CSF"],
            "Accounts": [89, 67, 34, 56, 23]
        })
        fig = px.bar(compliance_data, x="Framework", y="Accounts")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Account health table
    st.markdown("#### 🏥 Account Health Status")
    
    account_data = []
    for i in range(20):
        account_data.append({
            "Account ID": f"123456789{100+i}",
            "Name": f"{'Production' if i < 10 else 'Development'}-{'App' if i % 2 == 0 else 'Data'}-{i:03d}",
            "Environment": random.choice(["Production", "Development", "Staging"]),
            "Compliance Score": f"{random.randint(85, 98)}%",
            "Security Score": f"{random.randint(80, 95)}%",
            "Cost (Monthly)": f"${random.randint(5, 80)}K",
            "Status": random.choice(["✅ Healthy", "✅ Healthy", "✅ Healthy", "⚠️ Warning", "🔴 Alert"]),
            "Days Active": random.randint(30, 900)
        })
    
    df = pd.DataFrame(account_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### ⚡ Provisioning Metrics")
        st.metric("Average Time", "17.2 min", "-2.3 min")
        st.metric("Success Rate", "99.2%", "+0.5%")
        st.metric("This Month", "12 accounts", "+3")
    
    with col2:
        st.markdown("#### 💰 Cost Efficiency")
        st.metric("Cost per Account", "$18.9K", "-$1.2K")
        st.metric("RI Utilization", "87.3%", "+2.1%")
        st.metric("Waste Identified", "$127K/mo", "+$18K")
    
    with col3:
        st.markdown("#### 🛡️ Compliance Status")
        st.metric("Audit Ready", "91.7%", "+1.2%")
        st.metric("Compliance Drift", "5 accounts", "-2")
        st.metric("Evidence Items", "158,491", "+12K")

def render_create_account():
    """Render enhanced account creation interface"""
    st.markdown("### ➕ Create New AWS Account")
    
    st.info("💡 **Tip:** Use the Template Marketplace tab for pre-configured templates, or create a custom account below.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📝 Account Configuration")
        
        # Basic Info
        account_name = st.text_input("Account Name *", placeholder="e.g., Production-FinServices-001")
        
        col_a, col_b = st.columns(2)
        with col_a:
            portfolio = st.selectbox("Portfolio *", ["Financial Services", "Healthcare", "Retail", "Manufacturing", "Technology"])
        with col_b:
            environment = st.selectbox("Environment *", ["Production", "Staging", "Development", "Testing", "DR"])
        
        col_c, col_d = st.columns(2)
        with col_c:
            region = st.selectbox("Primary Region *", [
                "us-east-1 (N. Virginia)", 
                "us-west-2 (Oregon)", 
                "eu-west-1 (Ireland)", 
                "ap-southeast-1 (Singapore)"
            ])
        with col_d:
            multi_region = st.checkbox("Multi-Region Deployment", value=False)
        
        # Compliance Frameworks
        st.markdown("#### 📋 Compliance Frameworks")
        frameworks = st.multiselect(
            "Select applicable frameworks",
            ["SOC 2 Type II", "PCI-DSS v4.0", "HIPAA", "ISO 27001", "GDPR", "NIST CSF", "HITRUST"],
            default=[]
        )
        
        # Security Controls
        st.markdown("#### 🛡️ Security Controls")
        
        col1a, col2a, col3a = st.columns(3)
        with col1a:
            sec_hub = st.checkbox("Security Hub", value=True, key="create_sec_hub")
            guardduty = st.checkbox("GuardDuty", value=True, key="create_guardduty")
            config_rules = st.checkbox("Config Rules", value=True, key="create_config_rules")
        with col2a:
            inspector = st.checkbox("Inspector", value=True, key="create_inspector")
            cloudtrail = st.checkbox("CloudTrail", value=True, key="create_cloudtrail")
            s3_encrypt = st.checkbox("S3 Encryption", value=True, key="create_s3_encrypt")
        with col3a:
            vpc_flow = st.checkbox("VPC Flow Logs", value=True, key="create_vpc_flow")
            macie = st.checkbox("Macie", value=False, key="create_macie")
            waf = st.checkbox("WAF", value=False, key="create_waf")
        
        # Guardrails
        st.markdown("#### 🚧 Guardrails & Policies")
        guardrails = st.multiselect(
            "Policy Engines",
            ["Service Control Policies (SCPs)", "OPA Policies", "Tag Policies", "CloudFormation Hooks", "Terraform Sentinel"],
            default=["Service Control Policies (SCPs)"]
        )
        
        # Network Configuration
        st.markdown("#### 🌐 Network Configuration")
        col_n1, col_n2, col_n3 = st.columns(3)
        with col_n1:
            vpc_cidr = st.text_input("VPC CIDR", value="10.0.0.0/16")
        with col_n2:
            availability_zones = st.number_input("Availability Zones", min_value=1, max_value=6, value=3)
        with col_n3:
            nat_gateways = st.number_input("NAT Gateways", min_value=0, max_value=6, value=2)
        
        # Budget
        st.markdown("#### 💰 Budget & Cost Controls")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            budget = st.number_input("Monthly Budget ($)", min_value=0, value=50000, step=1000)
        with col_b2:
            alert_threshold = st.slider("Alert Threshold (%)", min_value=50, max_value=100, value=80)
        
        # Owner & Contact
        st.markdown("#### 👤 Account Owner")
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            owner_name = st.text_input("Owner Name", placeholder="John Smith")
        with col_o2:
            owner_email = st.text_input("Owner Email", placeholder="john.smith@company.com")
        
    with col2:
        st.markdown("#### 💡 Configuration Summary")
        
        # Show a summary card
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #0066CC;'>
            <strong>Account:</strong> {account_name or 'Not specified'}<br>
            <strong>Environment:</strong> {environment}<br>
            <strong>Region:</strong> {region.split(' ')[0]}<br>
            <strong>Frameworks:</strong> {len(frameworks)} selected<br>
            <strong>Budget:</strong> ${budget:,}/month<br>
            <strong>Alert:</strong> {alert_threshold}%
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Real-time cost forecast
        if account_name and len(frameworks) > 0:
            st.markdown("#### 💰 Cost Forecast")
            
            # Simplified cost calculation
            base_cost = budget * 0.75
            sec_cost = len([s for s in [sec_hub, guardduty, config_rules, inspector, macie] if s]) * 500
            network_cost = nat_gateways * 32 * 730  # NAT Gateway cost
            
            estimated_cost = base_cost + sec_cost + network_cost
            
            st.metric("Estimated Monthly", f"${estimated_cost:,.0f}", f"±15%")
            
            st.markdown(f"""
            **Breakdown:**
            - Compute: ${estimated_cost * 0.35:,.0f}
            - Storage: ${estimated_cost * 0.20:,.0f}
            - Security: ${sec_cost:,.0f}
            - Network: ${network_cost:,.0f}
            - Other: ${estimated_cost * 0.15:,.0f}
            """)
            
            if estimated_cost < budget:
                st.success(f"✅ Within budget (${budget - estimated_cost:,.0f} buffer)")
            else:
                st.warning(f"⚠️ Over budget by ${estimated_cost - budget:,.0f}")
        
        st.markdown("---")
        
        # Compliance preview
        if len(frameworks) > 0:
            st.markdown("#### 📊 Compliance Preview")
            
            avg_score = random.randint(88, 96)
            st.metric("Expected Score", f"{avg_score}%", "Audit Ready")
            
            for fw in frameworks[:3]:  # Show first 3
                score = random.randint(85, 98)
                st.progress(score / 100, text=f"{fw}: {score}%")
    
    st.markdown("---")
    
    # Action buttons
    col_act1, col_act2, col_act3, col_act4 = st.columns([1, 1, 1, 2])
    
    with col_act1:
        if st.button("🔍 Validate Configuration", type="secondary", use_container_width=True):
            with st.spinner("Running validation checks..."):
                time.sleep(2)
                validation = run_readiness_validation({})
                
                if validation["ready"]:
                    st.success(f"✅ Validation passed ({validation['passed']}/{validation['total']} checks)")
                else:
                    st.error(f"❌ Validation failed: {validation['errors']} errors, {validation['warnings']} warnings")
                
                # Show detailed results
                with st.expander("View Validation Details"):
                    for check in validation["checks"]:
                        if check["status"] == "pass":
                            st.success(f"✅ {check['name']}")
                        else:
                            if check["severity"] == "critical":
                                st.error(f"❌ {check['name']}: {check['message']}")
                            else:
                                st.warning(f"⚠️ {check['name']}: {check['message']}")
    
    with col_act2:
        if st.button("💾 Save as Draft", type="secondary", use_container_width=True):
            st.success("✅ Configuration saved as draft")
    
    with col_act3:
        if st.button("🚀 Launch Onboarding", type="primary", use_container_width=True):
            if not account_name:
                st.error("❌ Please provide an account name")
            else:
                # Show visual workflow
                render_visual_workflow(account_name)
    
    with col_act4:
        st.markdown("")  # Spacer

def render_visual_workflow(account_name: str):
    """Render animated workflow orchestration"""
    st.markdown("---")
    st.markdown(f"### 🚀 Provisioning Account: {account_name}")
    
    # Create workflow visualization
    steps = generate_workflow_steps()
    
    # Progress overview
    total_duration = sum([s["duration"] for s in steps])
    completed_duration = sum([s["duration"] for s in steps if s["status"] == "complete"])
    progress = completed_duration / total_duration
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Progress", f"{progress*100:.0f}%")
    with col2:
        st.metric("Elapsed", f"{completed_duration} min")
    with col3:
        st.metric("Estimated Total", f"{total_duration} min")
    
    st.progress(progress)
    
    # Detailed steps
    for i, step in enumerate(steps):
        if step["status"] == "complete":
            icon = "✅"
            color = "#28a745"
        elif step["status"] == "in_progress":
            icon = "⏳"
            color = "#ffc107"
        else:
            icon = "⏸️"
            color = "#6c757d"
        
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {color};'>
            <strong>{icon} Step {i+1}: {step['name']}</strong> ({step['duration']} min)
        </div>
        """, unsafe_allow_html=True)
        
        # Show substeps if in progress
        if step["status"] == "in_progress" and isinstance(step.get("substeps"), list):
            for substep in step["substeps"]:
                if isinstance(substep, dict):
                    sub_icon = "✅" if substep["status"] == "complete" else "⏳" if substep["status"] == "in_progress" else "⏸️"
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{sub_icon} {substep['name']}")
    
    if progress >= 1.0:
        st.success(f"""
        ✅ **Account provisioned successfully!**
        
        - Account ID: 123456789012
        - Time: {total_duration} minutes
        - Compliance Score: 94.2%
        - Status: Active and Compliant
        """)
        
        if st.button("View Account Details"):
            st.info("Redirecting to account dashboard...")
    else:
        st.info("⏳ Provisioning in progress. This typically takes 15-20 minutes.")

def render_template_marketplace():
    """Render template marketplace with all templates"""
    st.markdown("### 📚 Account Template Marketplace")
    st.markdown("Pre-configured templates based on thousands of enterprise deployments")
    
    # Category filter
    categories = ["All"] + list(set([t["category"] for t in ACCOUNT_TEMPLATES.values()]))
    selected_category = st.selectbox("Filter by Category", categories)
    
    # Search
    search = st.text_input("🔍 Search templates", placeholder="e.g., HIPAA, production, analytics...")
    
    # Display templates in grid
    templates_to_show = [
        (key, template) for key, template in ACCOUNT_TEMPLATES.items()
        if (selected_category == "All" or template["category"] == selected_category)
        and (not search or search.lower() in template["name"].lower() or search.lower() in template["description"].lower())
    ]
    
    # Grid layout (3 columns)
    for i in range(0, len(templates_to_show), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(templates_to_show):
                key, template = templates_to_show[i + j]
                with col:
                    render_template_card(key, template)

def render_template_card(key: str, template: Dict):
    """Render individual template card"""
    
    # Calculate average compliance score
    avg_compliance = sum(template["compliance_scores"].values()) / len(template["compliance_scores"])
    
    # Cost color
    avg_cost = template["estimated_cost"]["average"]
    if avg_cost < 10000:
        cost_color = "#28a745"
    elif avg_cost < 40000:
        cost_color = "#ffc107"
    else:
        cost_color = "#ff6b6b"
    
    st.markdown(f"""
    <div style='background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #e0e0e0; height: 100%; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
        <div style='font-size: 3rem; text-align: center; margin-bottom: 0.5rem;'>{template['icon']}</div>
        <h4 style='margin: 0 0 0.5rem 0; color: #232F3E;'>{template['name']}</h4>
        <p style='color: #666; font-size: 0.9rem; margin-bottom: 1rem;'>{template['description']}</p>
        
        <div style='background: #f8f9fa; padding: 0.75rem; border-radius: 5px; margin-bottom: 0.75rem;'>
            <strong style='color: {cost_color};'>${template['estimated_cost']['average']:,}/mo</strong><br>
            <small style='color: #666;'>${template['estimated_cost']['min']:,} - ${template['estimated_cost']['max']:,}</small>
        </div>
        
        <div style='margin-bottom: 0.75rem;'>
            <strong>Compliance:</strong> {avg_compliance:.0f}%<br>
            <small style='color: #666;'>{', '.join(template['compliance_frameworks'][:2])}</small>
        </div>
        
        <div style='margin-bottom: 0.75rem;'>
            <strong>Environment:</strong> {template['environment']}<br>
            <strong>Region:</strong> {template['region']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Details", key=f"details_{key}", use_container_width=True):
            show_template_details(key, template)
    with col2:
        if st.button("🚀 Use Template", key=f"use_{key}", type="primary", use_container_width=True):
            st.session_state[f"selected_template_{key}"] = True
            apply_template(key, template)

def show_template_details(key: str, template: Dict):
    """Show detailed template information in modal"""
    with st.expander(f"📋 {template['name']} - Detailed Configuration", expanded=True):
        
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Security", "Compliance", "Network"])
        
        with tab1:
            st.markdown(f"**Description:** {template['description']}")
            st.markdown(f"**Category:** {template['category']}")
            st.markdown(f"**Environment:** {template['environment']}")
            st.markdown(f"**Primary Region:** {template['region']}")
            
            st.markdown("#### 💰 Cost Breakdown")
            cost = calculate_cost_forecast(key)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Base Monthly", f"${cost['base_monthly']:,.0f}")
            with col2:
                st.metric("Optimized", f"${cost['optimized_monthly']:,.0f}")
            with col3:
                st.metric("Potential Savings", f"${cost['potential_savings']:,.0f}")
            
            # Cost breakdown chart
            breakdown_df = pd.DataFrame(list(cost['breakdown'].items()), columns=['Category', 'Cost'])
            fig = px.bar(breakdown_df, x='Category', y='Cost', title="Cost Breakdown by Category")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 🎯 Features Included")
            for feature in template["features"]:
                st.markdown(f"- ✅ {feature}")
        
        with tab2:
            st.markdown("#### 🛡️ Security Controls")
            
            controls = template["security_controls"]
            for control, enabled in controls.items():
                icon = "✅" if enabled else "⏸️"
                st.markdown(f"{icon} **{control.replace('_', ' ').title()}**")
            
            st.markdown("#### 🚧 Guardrails")
            for guardrail in template["guardrails"]:
                st.markdown(f"- 🛡️ {guardrail}")
        
        with tab3:
            st.markdown("#### 📊 Compliance Scores")
            
            compliance_preview = generate_compliance_preview(key)
            
            st.metric("Overall Compliance Score", f"{compliance_preview['overall_score']}%")
            st.metric("Total Evidence Items", f"{compliance_preview['total_evidence']:,}")
            
            for fw_detail in compliance_preview['frameworks']:
                st.markdown(f"**{fw_detail['framework']}**: {fw_detail['score']}% {'✅' if fw_detail['audit_ready'] else '⚠️'}")
                
                # Category breakdown
                for cat in fw_detail['categories']:
                    st.progress(cat['score'] / 100, text=f"{cat['name']}: {cat['score']}%")
                
                if fw_detail['improvements']:
                    with st.expander("View Recommendations"):
                        for improvement in fw_detail['improvements']:
                            st.markdown(f"- {improvement}")
        
        with tab4:
            st.markdown("#### 🌐 Network Configuration")
            
            network = template['network']
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**VPC CIDR:** `{network['vpc_cidr']}`")
                st.markdown(f"**Availability Zones:** {network['availability_zones']}")
            with col2:
                st.markdown(f"**NAT Gateways:** {network['nat_gateways']}")
                st.markdown(f"**Transit Gateway:** {'Yes' if network['transit_gateway'] else 'No'}")

def apply_template(key: str, template: Dict):
    """Apply template to account creation form"""
    st.success(f"✅ Template '{template['name']}' applied!")
    st.info("💡 Switch to 'Create Account' tab to review and customize the configuration, then launch provisioning.")
    
    # Store template in session state for use in Create Account tab
    st.session_state['applied_template'] = template

def render_batch_provisioning():
    """Render batch account provisioning interface"""
    st.markdown("### 📦 Batch Account Provisioning")
    st.markdown("Create multiple accounts simultaneously for scale deployments")
    
    tab1, tab2, tab3 = st.tabs(["CSV Upload", "Template Generator", "In Progress"])
    
    with tab1:
        st.markdown("#### 📄 Upload CSV File")
        st.markdown("Upload a CSV with account specifications")
        
        # Sample CSV download
        sample_csv = """Account Name,Portfolio,Environment,Region,Frameworks,Budget
Production-App-001,Financial Services,Production,us-east-1,"SOC 2,PCI-DSS",50000
Production-App-002,Financial Services,Production,us-west-2,"SOC 2,PCI-DSS",50000
Development-App-001,Financial Services,Development,us-east-1,Baseline,5000
Staging-App-001,Financial Services,Staging,us-east-1,"SOC 2",15000"""
        
        st.download_button(
            "📥 Download Sample CSV Template",
            sample_csv,
            "account_template.csv",
            "text/csv",
            use_container_width=True
        )
        
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} accounts from CSV")
            
            st.dataframe(df, use_container_width=True)
            
            # Validation
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Validate All", type="secondary", use_container_width=True):
                    with st.spinner("Validating all accounts..."):
                        time.sleep(2)
                        st.success(f"✅ {len(df)-2} accounts valid, 2 errors found")
                        
                        st.error("❌ Row 3: Account name 'Production-App-001' already exists")
                        st.error("❌ Row 5: Budget exceeds portfolio allocation")
            
            with col2:
                if st.button("🚀 Provision All", type="primary", use_container_width=True):
                    st.success(f"✅ Started batch provisioning of {len(df)} accounts")
                    st.info("⏱️ Estimated completion: 25 minutes (parallel provisioning)")
    
    with tab2:
        st.markdown("#### 🎨 Template-Based Generator")
        st.markdown("Generate multiple accounts from a template")
        
        template_key = st.selectbox(
            "Select Base Template",
            list(ACCOUNT_TEMPLATES.keys()),
            format_func=lambda x: ACCOUNT_TEMPLATES[x]["name"]
        )
        
        count = st.number_input("Number of Accounts", min_value=1, max_value=100, value=5)
        
        naming_pattern = st.text_input("Naming Pattern", value="Production-App-{n:03d}", 
                                       help="Use {n} for sequence number")
        
        regions = st.multiselect("Deploy to Regions", 
                                ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                                default=["us-east-1"])
        
        if st.button("🎯 Generate Batch Configuration", type="primary"):
            st.success(f"✅ Generated configuration for {count} accounts across {len(regions)} regions")
            
            # Preview
            preview_data = []
            for i in range(min(count, 10)):  # Show first 10
                for region in regions:
                    preview_data.append({
                        "Name": naming_pattern.replace("{n}", str(i+1)).replace("{n:03d}", f"{i+1:03d}"),
                        "Region": region,
                        "Template": ACCOUNT_TEMPLATES[template_key]["name"],
                        "Est. Cost": f"${ACCOUNT_TEMPLATES[template_key]['estimated_cost']['average']:,}"
                    })
            
            st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)
            
            st.button("🚀 Provision All Accounts", type="primary")
    
    with tab3:
        st.markdown("#### ⏳ Batch Operations In Progress")
        
        # Example batch operation
        batch_data = {
            "Batch ID": "BATCH-2024-001",
            "Started": "2024-11-25 14:30:00",
            "Total Accounts": 50,
            "Completed": 32,
            "In Progress": 10,
            "Pending": 8,
            "Failed": 0
        }
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Completed", f"{batch_data['Completed']}/{batch_data['Total Accounts']}")
        with col2:
            st.metric("In Progress", batch_data['In Progress'])
        with col3:
            st.metric("Pending", batch_data['Pending'])
        with col4:
            st.metric("Failed", batch_data['Failed'])
        
        progress = batch_data['Completed'] / batch_data['Total Accounts']
        st.progress(progress)
        
        st.markdown(f"**Estimated Completion:** {datetime.now() + timedelta(minutes=15):%H:%M}")
        
        # Detailed status
        st.markdown("#### 📊 Detailed Status")
        
        status_data = []
        for i in range(20):
            if i < 12:
                status = "✅ Complete"
                time_taken = f"{random.randint(15, 20)} min"
            elif i < 15:
                status = "⏳ In Progress"
                time_taken = f"{random.randint(5, 15)} min"
            else:
                status = "⏸️ Pending"
                time_taken = "-"
            
            status_data.append({
                "Account Name": f"Production-App-{i+1:03d}",
                "Region": random.choice(["us-east-1", "us-west-2"]),
                "Status": status,
                "Time": time_taken
            })
        
        st.dataframe(pd.DataFrame(status_data), use_container_width=True, hide_index=True, height=400)

def render_account_modification():
    """Render account modification interface"""
    st.markdown("### 🔄 Account Modification & Evolution")
    st.markdown("Modify existing accounts while maintaining compliance")
    
    # Select account
    account = st.selectbox(
        "Select Account to Modify",
        ["Production-FinServices-001", "Production-App-002", "Development-Test-001"],
        help="Choose an existing account to modify"
    )
    
    st.markdown("---")
    
    # Modification types
    mod_type = st.selectbox(
        "Modification Type",
        [
            "Add Compliance Framework",
            "Enable Additional Security Controls",
            "Adjust Budget & Cost Controls",
            "Change Environment Classification",
            "Update Network Configuration",
            "Add/Remove Integrations",
            "Apply New Policy Template"
        ]
    )
    
    st.markdown("---")
    
    if mod_type == "Add Compliance Framework":
        st.markdown("#### 📋 Add Compliance Framework")
        
        current_frameworks = ["SOC 2 Type II", "ISO 27001"]
        st.info(f"**Current Frameworks:** {', '.join(current_frameworks)}")
        
        new_framework = st.selectbox("Select Framework to Add", 
                                     ["PCI-DSS v4.0", "HIPAA", "GDPR", "NIST CSF", "HITRUST"])
        
        if st.button("🔍 Analyze Impact"):
            with st.spinner("Analyzing impact of adding framework..."):
                time.sleep(2)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("New Controls Required", "23")
                with col2:
                    st.metric("Estimated Cost Increase", "$3,200/mo")
                with col3:
                    st.metric("Implementation Time", "45 minutes")
                
                st.warning("⚠️ **Required Changes:**")
                st.markdown("""
                - Enable AWS Macie for data classification
                - Configure additional Config Rules (12 new rules)
                - Update IAM policies for access controls
                - Enable VPC Flow Logs in all subnets
                - Configure automated compliance reporting
                """)
                
                if st.button("✅ Apply Changes", type="primary"):
                    st.success("✅ Framework addition scheduled. Changes will be applied in next maintenance window.")
    
    elif mod_type == "Enable Additional Security Controls":
        st.markdown("#### 🛡️ Enable Security Controls")
        
        st.markdown("**Currently Enabled:**")
        st.markdown("✅ Security Hub, ✅ GuardDuty, ✅ Config Rules, ✅ CloudTrail")
        
        st.markdown("**Available to Enable:**")
        enable_macie = st.checkbox("AWS Macie (Data Classification)", value=False, key="mod_macie")
        enable_inspector = st.checkbox("Amazon Inspector V2 (Vulnerability Scanning)", value=False, key="mod_inspector")
        enable_waf = st.checkbox("AWS WAF (Web Application Firewall)", value=False, key="mod_waf")
        enable_shield = st.checkbox("AWS Shield Advanced (DDoS Protection)", value=False, key="mod_shield")
        
        if st.button("Apply Security Control Changes"):
            st.success("✅ Security controls will be enabled in 10-15 minutes")
    
    elif mod_type == "Adjust Budget & Cost Controls":
        st.markdown("#### 💰 Adjust Budget")
        
        current_budget = 50000
        st.info(f"**Current Budget:** ${current_budget:,}/month")
        
        new_budget = st.number_input("New Monthly Budget ($)", min_value=1000, value=current_budget, step=1000)
        new_alert = st.slider("Alert Threshold (%)", 50, 100, 80)
        
        cost_controls = st.multiselect(
            "Additional Cost Controls",
            ["Auto-stop dev instances after hours", "Enforce RI/SP usage", "Block large instance types", "Require approval for GPU instances"]
        )
        
        if st.button("Update Budget Configuration"):
            st.success(f"✅ Budget updated to ${new_budget:,}/month with {new_alert}% alert threshold")
    
    st.markdown("---")
    
    # Drift detection
    st.markdown("### 🔍 Configuration Drift Detection")
    
    drift_items = [
        {"Resource": "Security Hub", "Expected": "Enabled", "Current": "Enabled", "Status": "✅ Compliant"},
        {"Resource": "GuardDuty", "Expected": "Enabled", "Current": "Enabled", "Status": "✅ Compliant"},
        {"Resource": "S3 Encryption", "Expected": "AES-256", "Current": "None", "Status": "⚠️ Drift Detected"},
        {"Resource": "CloudTrail", "Expected": "Enabled", "Current": "Enabled", "Status": "✅ Compliant"},
        {"Resource": "VPC Flow Logs", "Expected": "Enabled", "Current": "Disabled", "Status": "⚠️ Drift Detected"},
    ]
    
    drift_df = pd.DataFrame(drift_items)
    st.dataframe(drift_df, use_container_width=True, hide_index=True)
    
    if st.button("🔧 Remediate All Drift"):
        st.success("✅ Drift remediation initiated. 2 resources will be corrected.")

def render_account_cloning():
    """Render account cloning interface"""
    st.markdown("### 👯 Clone Account")
    st.markdown("Clone existing account configurations to new accounts or regions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Source Account")
        source_account = st.selectbox("Select Source Account", 
                                      ["Production-FinServices-001", "Production-App-002", "Development-Test-001"])
        
        # Show source details
        st.info(f"""
        **Source Configuration:**
        - Environment: Production
        - Region: us-east-1
        - Frameworks: SOC 2, PCI-DSS
        - Monthly Cost: $42,000
        """)
    
    with col2:
        st.markdown("#### 🎯 Clone Configuration")
        
        clone_type = st.radio("Clone Type", [
            "Exact Replica (all settings + resources)",
            "Configuration Only (no resources)",
            "Template (generalize for reuse)"
        ])
        
        new_name = st.text_input("New Account Name", value=f"{source_account}-Clone")
        new_region = st.selectbox("Target Region", ["us-east-1", "us-west-2", "eu-west-1"])
        
        st.markdown("#### ⚙️ Modifications")
        
        modify_budget = st.checkbox("Adjust Budget", key="clone_modify_budget")
        if modify_budget:
            new_budget = st.slider("Budget as % of Source", 25, 200, 100, step=25, key="clone_budget_slider")
            st.info(f"New budget: ${42000 * new_budget / 100:,.0f}/month")
        
        modify_env = st.checkbox("Change Environment Type", key="clone_modify_env")
        if modify_env:
            new_env = st.selectbox("New Environment", ["Production", "Staging", "Development", "DR"], key="clone_new_env")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Preview Clone Configuration", use_container_width=True):
            st.success("✅ Clone configuration validated")
            
            with st.expander("View Clone Details"):
                st.markdown("""
                **What will be cloned:**
                - ✅ All security controls (Security Hub, GuardDuty, etc.)
                - ✅ Compliance framework configurations
                - ✅ IAM roles and policies
                - ✅ Network topology (VPC, subnets)
                - ✅ Budget and cost controls
                - ✅ Integration connections
                
                **What will NOT be cloned:**
                - ❌ Running EC2 instances
                - ❌ RDS databases (will create empty)
                - ❌ S3 data (will create empty buckets)
                - ❌ Historical CloudWatch data
                """)
    
    with col2:
        if st.button("🚀 Clone Account", type="primary", use_container_width=True):
            with st.spinner("Cloning account..."):
                time.sleep(3)
                st.success(f"✅ Account '{new_name}' cloned successfully!")
                st.info("Account will be ready in approximately 18 minutes")

def render_offboarding():
    """Render account offboarding/decommissioning interface"""
    st.markdown("### 🔴 Account Offboarding & Decommissioning")
    st.markdown("Securely retire AWS accounts with compliance and data retention")
    
    st.warning("⚠️ **Warning:** Account offboarding is irreversible after the retention period.")
    
    # Select account
    account = st.selectbox("Select Account to Offboard", 
                          ["Development-Test-001", "Staging-App-003", "Production-Legacy-001"])
    
    st.markdown("---")
    
    # Pre-offboard checks
    st.markdown("### 🔍 Pre-Offboard Analysis")
    
    if st.button("🔍 Run Pre-Offboard Checks"):
        with st.spinner("Analyzing account..."):
            time.sleep(2)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Running Resources", "23", "⚠️")
            with col2:
                st.metric("Active Workloads", "3", "⚠️")
            with col3:
                st.metric("Data Volume", "1.2 TB", "📊")
            with col4:
                st.metric("Dependencies", "5 accounts", "⚠️")
            
            st.markdown("---")
            
            st.markdown("#### ⚠️ Issues to Resolve")
            
            issues = [
                {"Severity": "🔴 Critical", "Issue": "Active RDS database with production data", "Action": "Migrate or backup before offboarding"},
                {"Severity": "🟡 Warning", "Issue": "EC2 instances still running", "Action": "Stop or migrate instances"},
                {"Severity": "🟡 Warning", "Issue": "S3 buckets contain data", "Action": "Archive or migrate data"},
                {"Severity": "🟢 Info", "Issue": "Cross-account IAM roles active", "Action": "Roles will be automatically revoked"},
                {"Severity": "🟡 Warning", "Issue": "DNS records pointing to this account", "Action": "Update DNS before offboarding"},
            ]
            
            st.dataframe(pd.DataFrame(issues), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Offboarding options
    st.markdown("### ⚙️ Offboarding Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Data Handling")
        data_action = st.radio("Data Retention", [
            "Archive to S3 Glacier (7-year retention)",
            "Export and delete immediately",
            "Transfer to another account"
        ])
        
        if "Transfer" in data_action:
            target_account = st.selectbox("Target Account", ["Production-Archive-001", "DR-Account-001"])
        
        cloudtrail_retention = st.slider("CloudTrail Retention (years)", 1, 10, 7)
        
        snapshot_resources = st.checkbox("Create final snapshots (RDS, EBS)", value=True, key="offboard_snapshot")
        export_config = st.checkbox("Export all configuration", value=True, key="offboard_export")
    
    with col2:
        st.markdown("#### ⏱️ Offboarding Schedule")
        
        offboard_type = st.radio("Offboarding Type", [
            "Soft Delete (disable access, retain 30 days)",
            "Hard Delete (permanent after retention)",
            "Scheduled (set date/time)"
        ])
        
        if "Scheduled" in offboard_type:
            offboard_date = st.date_input("Offboard Date")
            offboard_time = st.time_input("Offboard Time")
        
        notify_stakeholders = st.checkbox("Notify stakeholders (30-day warning)", value=True, key="offboard_notify")
        if notify_stakeholders:
            notification_recipients = st.text_area("Notification Recipients (comma-separated emails)",
                                                   placeholder="user1@company.com, user2@company.com",
                                                   key="offboard_recipients")
    
    st.markdown("---")
    
    # Offboarding workflow
    st.markdown("### 📋 Offboarding Workflow")
    
    workflow_steps = [
        "1️⃣ Notify stakeholders (30-day notice)",
        "2️⃣ Snapshot all resources (RDS, EBS, AMIs)",
        "3️⃣ Export CloudTrail logs to long-term storage",
        "4️⃣ Archive data to S3 Glacier",
        "5️⃣ Document final state for compliance",
        "6️⃣ Disable access (revoke IAM roles, SCPs)",
        "7️⃣ Wait for retention period (30 days)",
        "8️⃣ Final deletion (irreversible)",
        "9️⃣ Update CMDB and asset inventory"
    ]
    
    for step in workflow_steps:
        st.markdown(step)
    
    st.markdown("---")
    
    # Final confirmation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        confirm = st.checkbox("⚠️ I understand this action is irreversible after retention period", key="offboard_confirm")
    
    with col2:
        if st.button("🔴 Start Offboarding", type="primary", disabled=not confirm, use_container_width=True):
            st.success("✅ Offboarding initiated")
            st.info("""
            **Next Steps:**
            - Stakeholders will be notified today
            - Resources will be snapshotted over next 24 hours
            - Access will be disabled after 30-day notice period
            - Final deletion will occur after retention period
            
            You can cancel offboarding anytime during the notice period.
            """)

def render_approval_workflow():
    """Render approval workflow interface"""
    st.markdown("### ✅ Approval Workflow")
    st.markdown("Multi-stakeholder approval process for account requests")
    
    tab1, tab2, tab3 = st.tabs(["Pending Approvals", "My Requests", "Approval History"])
    
    with tab1:
        st.markdown("#### 📥 Pending Your Approval")
        
        pending_approvals = [
            {
                "Request ID": "REQ-2024-1234",
                "Account Name": "Production-FinServices-001",
                "Requestor": "John Smith (DevOps)",
                "Type": "New Account",
                "Budget": "$42,000/mo",
                "Frameworks": "SOC 2, PCI-DSS",
                "Submitted": "2 hours ago",
                "Your Role": "Security Review",
                "SLA": "4 hours remaining"
            },
            {
                "Request ID": "REQ-2024-1235",
                "Account Name": "Development-Test-002",
                "Requestor": "Jane Doe (Engineering)",
                "Type": "New Account",
                "Budget": "$5,000/mo",
                "Frameworks": "Baseline",
                "Submitted": "1 day ago",
                "Your Role": "FinOps Review",
                "SLA": "⚠️ 2 hours overdue"
            },
        ]
        
        for approval in pending_approvals:
            with st.expander(f"📋 {approval['Request ID']} - {approval['Account Name']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Requestor:** {approval['Requestor']}")
                    st.markdown(f"**Type:** {approval['Type']}")
                    st.markdown(f"**Budget:** {approval['Budget']}")
                
                with col2:
                    st.markdown(f"**Frameworks:** {approval['Frameworks']}")
                    st.markdown(f"**Submitted:** {approval['Submitted']}")
                    st.markdown(f"**Your Role:** {approval['Your Role']}")
                
                with col3:
                    st.markdown(f"**SLA:** {approval['SLA']}")
                
                st.markdown("---")
                
                # View details button
                if st.button(f"👁️ View Full Configuration", key=f"view_{approval['Request ID']}"):
                    st.info("Opening detailed configuration...")
                
                # Decision
                col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
                
                with col1:
                    if st.button("✅ Approve", key=f"approve_{approval['Request ID']}", type="primary", use_container_width=True):
                        st.success(f"✅ Approved {approval['Request ID']}")
                        st.info("Request moved to next approval stage: CTO Final Review")
                
                with col2:
                    if st.button("⏸️ Request Changes", key=f"changes_{approval['Request ID']}", use_container_width=True):
                        changes = st.text_area("Required Changes", key=f"changes_text_{approval['Request ID']}")
                        if st.button("Send", key=f"send_changes_{approval['Request ID']}"):
                            st.warning("Change request sent to requestor")
                
                with col3:
                    if st.button("❌ Reject", key=f"reject_{approval['Request ID']}", use_container_width=True):
                        reason = st.text_area("Rejection Reason", key=f"reject_reason_{approval['Request ID']}")
                        if st.button("Confirm Rejection", key=f"confirm_reject_{approval['Request ID']}"):
                            st.error("Request rejected")
    
    with tab2:
        st.markdown("#### 📤 My Requests")
        
        my_requests = [
            {
                "Request ID": "REQ-2024-1230",
                "Account Name": "Production-App-003",
                "Status": "✅ Approved",
                "Current Stage": "Provisioning",
                "Submitted": "3 days ago",
                "Approved By": "Security Team, FinOps Team, CTO"
            },
            {
                "Request ID": "REQ-2024-1231",
                "Account Name": "Staging-App-002",
                "Status": "⏳ Pending",
                "Current Stage": "Security Review",
                "Submitted": "1 day ago",
                "Approved By": "Team Lead"
            },
        ]
        
        st.dataframe(pd.DataFrame(my_requests), use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("#### 📜 Approval History (Last 30 Days)")
        
        history = []
        for i in range(20):
            history.append({
                "Date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "Request ID": f"REQ-2024-{1200+i}",
                "Account Name": f"{'Production' if i % 2 == 0 else 'Development'}-App-{i:03d}",
                "Requestor": random.choice(["John Smith", "Jane Doe", "Bob Johnson"]),
                "Decision": random.choice(["✅ Approved", "✅ Approved", "✅ Approved", "❌ Rejected", "⏸️ Changes Requested"]),
                "Reviewer": "You"
            })
        
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True, height=400)

def render_ai_assistant():
    """Render AI-powered configuration assistant"""
    st.markdown("### 🤖 AI Configuration Assistant")
    st.markdown("Describe your workload in natural language and get AI-powered configuration recommendations")
    
    st.info("💡 **Powered by AWS Bedrock & Claude 3.5 Sonnet**")
    
    # Natural language input
    user_input = st.text_area(
        "Describe your workload or requirements:",
        placeholder="Example: I need a HIPAA-compliant account for a patient data analytics platform processing 500GB daily, with high availability and automated backups",
        height=100
    )
    
    # Quick templates
    st.markdown("**Or try these examples:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💳 PCI-DSS E-commerce"):
            user_input = "E-commerce platform processing credit card transactions, needs PCI-DSS compliance, multi-region for global customers"
    
    with col2:
        if st.button("🏥 HIPAA Healthcare"):
            user_input = "Healthcare analytics platform with PHI data, needs HIPAA compliance, 99.99% uptime, automated backups"
    
    with col3:
        if st.button("🤖 ML Training"):
            user_input = "Machine learning training environment with GPU instances, large dataset storage, cost optimization important"
    
    if st.button("✨ Generate AI Recommendations", type="primary"):
        with st.spinner("AI analyzing your requirements..."):
            time.sleep(3)
            
            st.success("✅ AI Analysis Complete!")
            
            st.markdown("---")
            
            # AI Recommendations
            st.markdown("### 🎯 Recommended Configuration")
            
            tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Detailed Config", "Cost Analysis", "Alternatives"])
            
            with tab1:
                st.markdown("#### 📋 AI-Generated Summary")
                
                st.info("""
                Based on your requirements, I recommend the **Healthcare Analytics template** with the following customizations:
                
                **Why this configuration:**
                - ✅ Fully HIPAA-compliant with all required safeguards
                - ✅ Multi-AZ deployment ensures high availability (99.99% uptime)
                - ✅ Automated daily backups with point-in-time recovery
                - ✅ S3 Intelligent-Tiering for cost-optimized storage at scale
                - ✅ Macie enabled for automated PHI detection and classification
                - ✅ Encryption at rest and in transit (FIPS 140-2 compliant)
                """)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Estimated Cost", "$36K-42K/mo")
                with col2:
                    st.metric("Compliance Score", "94%")
                with col3:
                    st.metric("Setup Time", "18 minutes")
                
                st.markdown("#### 🏗️ Architecture Highlights")
                st.markdown("""
                - **Compute:** Multi-AZ deployment with Auto Scaling
                - **Database:** RDS Aurora PostgreSQL (encrypted)
                - **Storage:** S3 with Intelligent-Tiering + Glacier for archives
                - **Security:** Security Hub, GuardDuty, Macie, Inspector
                - **Monitoring:** CloudWatch with detailed metrics and alarms
                - **Backup:** AWS Backup with 35-day retention
                """)
            
            with tab2:
                st.markdown("#### ⚙️ Detailed Configuration")
                
                config_details = {
                    "Account Name": "Healthcare-Analytics-001",
                    "Portfolio": "Healthcare",
                    "Environment": "Production",
                    "Region": "us-east-1 (with failover to us-west-2)",
                    "Compliance": "HIPAA, SOC 2 Type II",
                    "Budget": "$40,000/month",
                    "Alert Threshold": "85%"
                }
                
                for key, value in config_details.items():
                    st.markdown(f"**{key}:** {value}")
                
                st.markdown("---")
                
                st.markdown("**Security Controls:**")
                security_controls = [
                    "AWS Security Hub (HIPAA standard)",
                    "Amazon GuardDuty (threat detection)",
                    "AWS Config (compliance monitoring)",
                    "Amazon Inspector V2 (vulnerability scanning)",
                    "Amazon Macie (PHI data discovery)",
                    "AWS CloudTrail (audit logging)",
                    "VPC Flow Logs (network monitoring)",
                    "AWS WAF (application firewall)"
                ]
                for control in security_controls:
                    st.markdown(f"- ✅ {control}")
                
                st.markdown("---")
                
                st.markdown("**Network Configuration:**")
                st.markdown("""
                - VPC CIDR: 10.110.0.0/16
                - Availability Zones: 3 (us-east-1a, 1b, 1c)
                - Public Subnets: 3 (one per AZ)
                - Private Subnets: 6 (two per AZ: app tier + data tier)
                - NAT Gateways: 3 (one per AZ for high availability)
                - Transit Gateway: Enabled (for hub connectivity)
                """)
            
            with tab3:
                st.markdown("#### 💰 Cost Analysis")
                
                cost_breakdown = {
                    "Compute (EC2/ECS)": 14000,
                    "Database (RDS Aurora)": 8500,
                    "Storage (S3/EBS)": 6000,
                    "Security Services": 3200,
                    "Networking": 2800,
                    "Monitoring & Logging": 1500,
                    "Backup & DR": 2000
                }
                
                total_cost = sum(cost_breakdown.values())
                
                st.metric("Total Estimated Monthly Cost", f"${total_cost:,}")
                
                # Cost breakdown chart
                breakdown_df = pd.DataFrame(list(cost_breakdown.items()), columns=['Category', 'Cost'])
                fig = px.bar(breakdown_df, x='Category', y='Cost', title="Monthly Cost Breakdown")
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 💡 Cost Optimization Opportunities")
                st.markdown("""
                - **Reserved Instances (1-year):** Save $6,800/month (compute)
                - **Savings Plans:** Save $4,200/month (flexible compute)
                - **S3 Lifecycle Policies:** Save $1,800/month (move cold data to Glacier)
                - **Right-sizing:** Potential $2,100/month (after initial monitoring)
                
                **Total Potential Savings:** $14,900/month (37% reduction)
                **Optimized Monthly Cost:** $23,100
                """)
            
            with tab4:
                st.markdown("#### 🔀 Alternative Configurations")
                
                st.markdown("**Option A: Cost-Optimized** 💰")
                st.markdown("""
                - Single-region deployment (no DR)
                - Reduced instance sizes
                - Standard support vs. Enterprise
                - **Cost:** $24K-28K/month (30% savings)
                - **Trade-off:** Lower availability (99.9% vs 99.99%)
                """)
                
                st.markdown("---")
                
                st.markdown("**Option B: Enhanced Security** 🛡️")
                st.markdown("""
                - AWS Shield Advanced (DDoS protection)
                - Amazon Detective (security investigation)
                - Additional compliance: HITRUST
                - Dedicated HSM for key management
                - **Cost:** $48K-54K/month (35% increase)
                - **Benefit:** Maximum security posture
                """)
                
                st.markdown("---")
                
                st.markdown("**Option C: Global High-Performance** 🌍")
                st.markdown("""
                - Multi-region active-active deployment
                - CloudFront with Lambda@Edge
                - Global accelerator
                - Cross-region replication
                - **Cost:** $68K-78K/month (2x base cost)
                - **Benefit:** Sub-100ms global latency
                """)
            
            st.markdown("---")
            
            # Apply recommendation
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("✅ Apply Recommended Config", type="primary", use_container_width=True):
                    st.success("✅ Configuration applied to account creation form!")
                    st.info("Switch to 'Create Account' tab to review and launch provisioning.")
            
            with col2:
                if st.button("💾 Save as Template", use_container_width=True):
                    st.success("✅ Saved as custom template")
            
            with col3:
                st.markdown("")  # Spacer

def render_network_designer():
    """Render network topology designer"""
    st.markdown("### 🌐 Network Topology Designer")
    st.markdown("Visual network planning and CIDR allocation tool")
    
    tab1, tab2, tab3 = st.tabs(["CIDR Calculator", "Topology Builder", "Connectivity Map"])
    
    with tab1:
        st.markdown("#### 🔢 CIDR Block Calculator & Validator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**VPC Configuration**")
            vpc_cidr = st.text_input("VPC CIDR Block", value="10.0.0.0/16", help="Choose CIDR that doesn't overlap with existing VPCs")
            
            if st.button("🔍 Check for Conflicts"):
                with st.spinner("Checking existing VPCs..."):
                    time.sleep(1)
                    
                    # Simulate conflict check
                    conflicts = [
                        {"VPC": "vpc-1234abcd (Production-Main)", "CIDR": "10.0.0.0/16", "Overlap": "100%"},
                        {"VPC": "vpc-5678efgh (Development-01)", "CIDR": "10.1.0.0/16", "Overlap": "0%"},
                    ]
                    
                    conflict_df = pd.DataFrame(conflicts)
                    st.dataframe(conflict_df, use_container_width=True, hide_index=True)
                    
                    st.error("❌ Conflict detected with vpc-1234abcd")
                    st.info("💡 Suggested alternative: 10.100.0.0/16")
            
            st.markdown("**Subnet Allocation**")
            num_azs = st.number_input("Number of Availability Zones", 1, 6, 3)
            subnet_types = st.multiselect("Subnet Types", 
                                         ["Public", "Private (App)", "Private (Data)", "Isolated"],
                                         default=["Public", "Private (App)", "Private (Data)"])
        
        with col2:
            st.markdown("**Calculated Subnets**")
            
            if vpc_cidr and subnet_types:
                st.success(f"✅ CIDR {vpc_cidr} can support {num_azs} AZs with {len(subnet_types)} subnet tiers")
                
                # Calculate subnet allocations
                st.markdown("**Recommended Subnet Layout:**")
                
                base_ip = vpc_cidr.split('/')[0]
                
                subnet_data = []
                for az_num in range(num_azs):
                    for subnet_type in subnet_types:
                        subnet_data.append({
                            "AZ": f"us-east-1{'abc'[az_num]}",
                            "Type": subnet_type,
                            "CIDR": f"10.0.{az_num * len(subnet_types) + subnet_types.index(subnet_type)}.0/24",
                            "Usable IPs": "251"
                        })
                
                st.dataframe(pd.DataFrame(subnet_data), use_container_width=True, hide_index=True)
                
                st.info(f"**Total Subnets:** {len(subnet_data)}")
    
    with tab2:
        st.markdown("#### 🏗️ Network Topology Builder")
        
        st.info("💡 Visual drag-and-drop network designer (diagram placeholder)")
        
        # Topology configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Components to Include:**")
            
            include_igw = st.checkbox("Internet Gateway", value=True, key="net_igw")
            include_nat = st.checkbox("NAT Gateways", value=True, key="net_nat")
            if include_nat:
                nat_count = st.number_input("NAT Gateway Count", 1, 6, 2, key="net_nat_count")
            
            include_tgw = st.checkbox("Transit Gateway", value=False, key="net_tgw")
            include_vpn = st.checkbox("VPN Gateway", value=False, key="net_vpn")
            include_dx = st.checkbox("Direct Connect", value=False, key="net_dx")
        
        with col2:
            st.markdown("**Security Configuration:**")
            
            include_waf = st.checkbox("AWS WAF", value=False, key="net_waf")
            include_shield = st.checkbox("AWS Shield", value=False, key="net_shield")
            include_firewall = st.checkbox("Network Firewall", value=False, key="net_firewall")
            
            st.markdown("**Monitoring:**")
            include_flowlogs = st.checkbox("VPC Flow Logs", value=True, key="net_flowlogs")
            include_traffic_mirror = st.checkbox("Traffic Mirroring", value=False, key="net_mirror")
        
        st.markdown("---")
        
        # Generate topology
        if st.button("📐 Generate Topology Diagram"):
            st.success("✅ Network topology generated")
            
            # Placeholder for actual network diagram
            st.markdown("""
            ```
            ┌─────────────────────────────────────────────────────────┐
            │                   Internet Gateway                       │
            └─────────────────────┬───────────────────────────────────┘
                                  │
            ┌─────────────────────┴───────────────────────────────────┐
            │                      VPC (10.0.0.0/16)                   │
            │                                                           │
            │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
            │  │   Public     │  │   Public     │  │   Public     │  │
            │  │  Subnet 1    │  │  Subnet 2    │  │  Subnet 3    │  │
            │  │  10.0.0.0/24 │  │  10.0.1.0/24 │  │  10.0.2.0/24 │  │
            │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
            │         │                 │                 │           │
            │      NAT GW             NAT GW           NAT GW         │
            │         │                 │                 │           │
            │  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐  │
            │  │   Private    │  │   Private    │  │   Private    │  │
            │  │  Subnet 1    │  │  Subnet 2    │  │  Subnet 3    │  │
            │  │  10.0.3.0/24 │  │  10.0.4.0/24 │  │  10.0.5.0/24 │  │
            │  └──────────────┘  └──────────────┘  └──────────────┘  │
            │                                                           │
            └───────────────────────────────────────────────────────────┘
            ```
            """)
            
            st.download_button(
                "📥 Export as Terraform",
                "# Terraform configuration placeholder",
                "network_topology.tf",
                "text/plain"
            )
    
    with tab3:
        st.markdown("#### 🔗 Cross-Account Connectivity Map")
        
        st.markdown("**Visualize network connections across accounts**")
        
        # Example connectivity data
        st.info("💡 Interactive connectivity graph (placeholder)")
        
        connectivity_data = [
            {"Source Account": "Production-App-001", "Target Account": "Shared-Services", "Connection": "Transit Gateway", "Status": "✅ Active"},
            {"Source Account": "Production-App-001", "Target Account": "Data-Lake", "Connection": "VPC Peering", "Status": "✅ Active"},
            {"Source Account": "Development-001", "Target Account": "Shared-Services", "Connection": "Transit Gateway", "Status": "✅ Active"},
            {"Source Account": "Production-App-002", "Target Account": "Production-App-001", "Connection": "PrivateLink", "Status": "✅ Active"},
            {"Source Account": "DR-Account", "Target Account": "Production-App-001", "Connection": "VPN", "Status": "⚠️ Degraded"},
        ]
        
        st.dataframe(pd.DataFrame(connectivity_data), use_container_width=True, hide_index=True)
        
        if st.button("🔍 Test All Connections"):
            st.success("✅ Connectivity test completed: 4/5 connections healthy")

def render_dependency_mapping():
    """Render dependency mapping and visualization"""
    st.markdown("### 🔗 Account Dependency Mapping")
    st.markdown("Visualize and manage cross-account dependencies")
    
    tab1, tab2, tab3 = st.tabs(["Dependency Graph", "Configure Dependencies", "Impact Analysis"])
    
    with tab1:
        st.markdown("#### 📊 Account Dependency Graph")
        
        # Select account
        selected_account = st.selectbox("Select Account", 
                                       ["Production-FinServices-001", "Production-App-002", "Data-Lake-001"])
        
        st.info("💡 Interactive dependency graph (placeholder)")
        
        # Show dependencies
        st.markdown(f"**Dependencies for {selected_account}:**")
        
        dependencies = {
            "Depends On (Upstream)": [
                {"Account": "Shared-Services", "Type": "SSO, DNS", "Critical": "Yes"},
                {"Account": "Security-Hub", "Type": "Security Aggregation", "Critical": "Yes"},
                {"Account": "Network-Hub", "Type": "Transit Gateway", "Critical": "Yes"},
            ],
            "Depended Upon By (Downstream)": [
                {"Account": "DR-Account-001", "Type": "Backup Target", "Critical": "No"},
                {"Account": "Analytics-001", "Type": "Data Source", "Critical": "Yes"},
                {"Account": "Testing-001", "Type": "Reference Config", "Critical": "No"},
            ]
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⬆️ Depends On (Upstream)**")
            st.dataframe(pd.DataFrame(dependencies["Depends On (Upstream)"]), use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**⬇️ Depended Upon By (Downstream)**")
            st.dataframe(pd.DataFrame(dependencies["Depended Upon By (Downstream)"]), use_container_width=True, hide_index=True)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Dependencies", "6")
        with col2:
            st.metric("Critical", "4")
        with col3:
            st.metric("Non-Critical", "2")
        with col4:
            st.metric("Circular Deps", "0")
    
    with tab2:
        st.markdown("#### ⚙️ Configure Account Dependencies")
        
        st.markdown("**Add New Dependency:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            source_account = st.selectbox("Source Account", ["Production-FinServices-001"])
        with col2:
            target_account = st.selectbox("Target Account", ["Shared-Services", "Data-Lake-001", "Security-Hub"])
        with col3:
            dependency_type = st.selectbox("Dependency Type", 
                                          ["IAM Role", "S3 Bucket Access", "API Gateway", "Transit Gateway", "VPC Peering", "PrivateLink"])
        
        critical = st.checkbox("Mark as Critical Dependency")
        
        description = st.text_area("Description", placeholder="Describe the dependency relationship...")
        
        if st.button("➕ Add Dependency"):
            st.success(f"✅ Dependency added: {source_account} → {target_account}")
            
            st.info("""
            **Auto-Configuration:**
            - ✅ IAM roles created with cross-account trust
            - ✅ S3 bucket policies updated
            - ✅ Resource policies applied
            - ✅ Network connectivity validated
            """)
    
    with tab3:
        st.markdown("#### 📈 Dependency Impact Analysis")
        
        st.markdown("**What-If Analysis:**")
        
        scenario = st.selectbox("Select Scenario", [
            "If Production-FinServices-001 is offboarded",
            "If Shared-Services has an outage",
            "If Network-Hub is modified"
        ])
        
        if st.button("🔍 Analyze Impact"):
            with st.spinner("Analyzing dependencies..."):
                time.sleep(2)
                
                st.warning("⚠️ **Impact Analysis Results:**")
                
                st.markdown("""
                **Directly Affected Accounts:** 3
                - DR-Account-001 (backup replication will fail)
                - Analytics-001 (data pipeline will break)
                - Testing-001 (reference configuration unavailable)
                
                **Indirectly Affected Accounts:** 7
                - Accounts that depend on the directly affected accounts
                
                **Critical Services at Risk:**
                - ✅ Production workloads: NOT affected (no critical deps)
                - ⚠️ DR/Backup: Will fail
                - ⚠️ Analytics: Data pipeline disrupted
                - ✅ Testing: Non-critical impact
                
                **Recommended Actions:**
                1. Migrate DR to alternative backup target
                2. Reconfigure Analytics data source
                3. Update Testing reference configurations
                4. Notify affected account owners (8 total)
                """)
                
                st.error("🚫 **Cannot proceed with offboarding until dependencies are resolved**")

# ============================================================================
# EXPORT FOR MAIN APP
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Account Lifecycle Enhanced", layout="wide")
    render_enhanced_account_lifecycle()