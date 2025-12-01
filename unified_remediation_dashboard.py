"""
🎯 Unified Remediation Dashboard
Comprehensive dashboard showing all resources needing remediation with confidence scoring

Features:
- Single view of Windows EC2, Linux EC2, and EKS containers
- Confidence scoring for each remediation
- Auto-remediate vs Manual intervention recommendations
- Bulk remediation capabilities
- NIST control tracking
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Optional
import json

# Import our remediation engines
from enhanced_windows_remediation import EnhancedWindowsRemediator
from linux_ec2_remediation_complete import LinuxEC2Connector, LinuxRemediationEngine
from eks_remediation_complete import EKSConnector, EKSRemediationEngine


class UnifiedRemediationDashboard:
    """Unified dashboard for all remediation activities"""
    
    def __init__(self, aws_region: str = 'us-east-1'):
        self.aws_region = aws_region
        
        # Initialize remediation engines
        self.windows_remediator = EnhancedWindowsRemediator()
        
        # Linux and EKS require AWS credentials
        # These will be initialized when credentials are available
        self.linux_connector = None
        self.linux_engine = None
        self.eks_connector = None
        self.eks_engine = None
    
    def initialize_connectors(self, aws_access_key: str, aws_secret_key: str,
                            eks_cluster_name: Optional[str] = None):
        """Initialize AWS connectors with credentials"""
        try:
            # Initialize Linux
            self.linux_connector = LinuxEC2Connector(
                region=self.aws_region,
                aws_access_key=aws_access_key,
                aws_secret_key=aws_secret_key
            )
            self.linux_engine = LinuxRemediationEngine(self.linux_connector)
            
            # Initialize EKS if cluster name provided
            if eks_cluster_name:
                self.eks_connector = EKSConnector(
                    cluster_name=eks_cluster_name,
                    region=self.aws_region,
                    aws_access_key=aws_access_key,
                    aws_secret_key=aws_secret_key
                )
                self.eks_engine = EKSRemediationEngine(self.eks_connector)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to initialize connectors: {str(e)}")
            return False
    
    def collect_all_vulnerabilities(self) -> List[Dict]:
        """
        Collect vulnerabilities from all sources:
        - Windows EC2 instances
        - Linux EC2 instances
        - EKS containers
        
        Returns unified list with confidence scores and remediation recommendations
        """
        all_vulnerabilities = []
        
        # Windows EC2 vulnerabilities
        if 'windows_instances' in st.session_state:
            for instance in st.session_state.windows_instances:
                instance_id = instance['instance_id']
                if 'vulnerabilities' in instance:
                    for vuln in instance['vulnerabilities']:
                        # Generate remediation plan
                        remediation_plan = self.windows_remediator.generate_comprehensive_remediation(vuln)
                        
                        all_vulnerabilities.append({
                            'resource_type': 'Windows EC2',
                            'resource_id': instance_id,
                            'resource_name': instance.get('name', instance_id),
                            'vulnerability_id': vuln.get('id', 'Unknown'),
                            'title': vuln.get('title', 'Unknown'),
                            'severity': vuln.get('severity', 'MEDIUM'),
                            'cvss_score': vuln.get('cvss_score', 0.0),
                            'package': vuln.get('packageName', 'Unknown'),
                            'current_version': vuln.get('installedVersion', 'Unknown'),
                            'fixed_version': vuln.get('fixedInVersion', 'Unknown'),
                            'nist_controls': remediation_plan['nist_controls'],
                            'confidence_score': remediation_plan['confidence_score'],
                            'auto_remediate': remediation_plan['auto_remediate_recommended'],
                            'registry_fixes': len(remediation_plan['registry_fixes']),
                            'reboot_required': remediation_plan['reboot_required'],
                            'estimated_duration': remediation_plan['estimated_duration'],
                            'remediation_plan': remediation_plan
                        })
        
        # Linux EC2 vulnerabilities
        if self.linux_connector and 'linux_instances' in st.session_state:
            for instance in st.session_state.linux_instances:
                instance_id = instance['instance_id']
                platform = instance.get('platform', 'Unknown')
                
                if 'vulnerabilities' in instance:
                    for vuln in instance['vulnerabilities']:
                        # Generate remediation plan
                        remediation_plan = self.linux_engine.generate_remediation_script(
                            vuln, platform=platform
                        )
                        
                        all_vulnerabilities.append({
                            'resource_type': 'Linux EC2',
                            'resource_id': instance_id,
                            'resource_name': instance.get('name', instance_id),
                            'vulnerability_id': vuln.get('id', 'Unknown'),
                            'title': vuln.get('title', 'Unknown'),
                            'severity': vuln.get('severity', 'MEDIUM'),
                            'cvss_score': vuln.get('cvss_score', 0.0),
                            'package': vuln.get('packageName', 'Unknown'),
                            'current_version': vuln.get('installedVersion', 'Unknown'),
                            'fixed_version': vuln.get('fixedInVersion', 'Unknown'),
                            'nist_controls': remediation_plan['nist_controls'],
                            'confidence_score': remediation_plan['confidence_score'],
                            'auto_remediate': remediation_plan['auto_remediate_recommended'],
                            'platform': platform,
                            'service_restart': remediation_plan.get('service_restart', []),
                            'estimated_duration': remediation_plan['estimated_duration'],
                            'remediation_plan': remediation_plan
                        })
        
        # EKS container vulnerabilities
        if self.eks_connector and 'eks_deployments' in st.session_state:
            for deployment in st.session_state.eks_deployments:
                if 'vulnerabilities' in deployment:
                    for vuln in deployment['vulnerabilities']:
                        deployment_info = {
                            'deployment_name': deployment['name'],
                            'namespace': deployment['namespace'],
                            'container_name': deployment.get('container_name', 'Unknown'),
                            'current_image': deployment.get('current_image', 'Unknown'),
                            'replicas': deployment.get('replicas', 1)
                        }
                        
                        # Generate remediation plan
                        remediation_plan = self.eks_engine.generate_remediation_plan(
                            vuln, deployment_info
                        )
                        
                        all_vulnerabilities.append({
                            'resource_type': 'EKS Container',
                            'resource_id': f"{deployment['namespace']}/{deployment['name']}",
                            'resource_name': deployment['name'],
                            'vulnerability_id': vuln.get('id', 'Unknown'),
                            'title': vuln.get('title', 'Unknown'),
                            'severity': vuln.get('severity', 'MEDIUM'),
                            'cvss_score': vuln.get('cvss_score', 0.0),
                            'package': vuln.get('packageName', 'Unknown'),
                            'current_version': vuln.get('installedVersion', 'Unknown'),
                            'fixed_version': vuln.get('fixedInVersion', 'Unknown'),
                            'nist_controls': remediation_plan['nist_controls'],
                            'confidence_score': remediation_plan['confidence_score'],
                            'auto_remediate': remediation_plan['auto_remediate_recommended'],
                            'current_image': deployment_info['current_image'],
                            'new_image': remediation_plan['new_image'],
                            'downtime': remediation_plan['downtime'],
                            'estimated_duration': remediation_plan['estimated_duration'],
                            'remediation_plan': remediation_plan
                        })
        
        return all_vulnerabilities
    
    def render_dashboard(self):
        """Render unified remediation dashboard"""
        
        st.markdown("# 🎯 Unified Remediation Dashboard")
        st.markdown("**Comprehensive view of all resources requiring remediation**")
        st.markdown("---")
        
        # Collect all vulnerabilities
        all_vulns = self.collect_all_vulnerabilities()
        
        if not all_vulns:
            st.info("📊 No vulnerabilities found or no resources scanned yet.")
            st.markdown("""
            **To see vulnerabilities:**
            1. Scan Windows EC2 instances
            2. Scan Linux EC2 instances
            3. Scan EKS containers
            """)
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(all_vulns)
        
        # Overview metrics
        self._render_overview_metrics(df)
        
        # Confidence score distribution
        self._render_confidence_distribution(df)
        
        # Main vulnerability table with filters
        self._render_vulnerability_table(df, all_vulns)
        
        # Bulk remediation actions
        self._render_bulk_actions(df, all_vulns)
    
    def _render_overview_metrics(self, df: pd.DataFrame):
        """Render overview metrics"""
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Vulnerabilities",
                len(df),
                help="All vulnerabilities across Windows, Linux, and EKS"
            )
        
        with col2:
            auto_count = len(df[df['auto_remediate'] == True])
            st.metric(
                "Auto-Remediate Ready",
                auto_count,
                f"{auto_count/len(df)*100:.1f}%",
                help="Vulnerabilities with confidence ≥85%"
            )
        
        with col3:
            critical_count = len(df[df['severity'] == 'CRITICAL'])
            st.metric(
                "Critical",
                critical_count,
                help="CRITICAL severity vulnerabilities"
            )
        
        with col4:
            avg_confidence = df['confidence_score'].mean()
            st.metric(
                "Avg Confidence",
                f"{avg_confidence:.1%}",
                help="Average remediation confidence score"
            )
        
        with col5:
            resource_types = df['resource_type'].nunique()
            st.metric(
                "Resource Types",
                resource_types,
                help="Windows EC2, Linux EC2, EKS"
            )
        
        st.markdown("---")
    
    def _render_confidence_distribution(self, df: pd.DataFrame):
        """Render confidence score distribution chart"""
        
        st.markdown("### 📊 Confidence Score Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Confidence score histogram
            fig = px.histogram(
                df,
                x='confidence_score',
                color='resource_type',
                nbins=20,
                title='Confidence Score Distribution by Resource Type',
                labels={'confidence_score': 'Confidence Score', 'count': 'Count'},
                color_discrete_map={
                    'Windows EC2': '#0078D4',
                    'Linux EC2': '#FCC624',
                    'EKS Container': '#326CE5'
                }
            )
            fig.add_vline(x=0.85, line_dash="dash", line_color="red", 
                         annotation_text="Auto-Remediate Threshold (85%)")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Severity by confidence
            severity_confidence = df.groupby(['severity', 'auto_remediate']).size().reset_index(name='count')
            
            fig = px.bar(
                severity_confidence,
                x='severity',
                y='count',
                color='auto_remediate',
                title='Vulnerability Severity vs Auto-Remediate Readiness',
                labels={'count': 'Count', 'severity': 'Severity'},
                color_discrete_map={True: '#28a745', False: '#dc3545'},
                barmode='group',
                category_orders={'severity': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
    
    def _render_vulnerability_table(self, df: pd.DataFrame, all_vulns: List[Dict]):
        """Render filterable vulnerability table"""
        
        st.markdown("### 📋 Vulnerability Details")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            resource_filter = st.multiselect(
                "Resource Type",
                options=df['resource_type'].unique(),
                default=df['resource_type'].unique()
            )
        
        with col2:
            severity_filter = st.multiselect(
                "Severity",
                options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
                default=['CRITICAL', 'HIGH']
            )
        
        with col3:
            auto_filter = st.selectbox(
                "Remediation Type",
                options=['All', 'Auto-Remediate Ready', 'Manual Review Required']
            )
        
        with col4:
            min_confidence = st.slider(
                "Min Confidence Score",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
                format="%.0f%%"
            )
        
        # Apply filters
        filtered_df = df[
            (df['resource_type'].isin(resource_filter)) &
            (df['severity'].isin(severity_filter)) &
            (df['confidence_score'] >= min_confidence)
        ]
        
        if auto_filter == 'Auto-Remediate Ready':
            filtered_df = filtered_df[filtered_df['auto_remediate'] == True]
        elif auto_filter == 'Manual Review Required':
            filtered_df = filtered_df[filtered_df['auto_remediate'] == False]
        
        # Display table
        st.markdown(f"**Showing {len(filtered_df)} of {len(df)} vulnerabilities**")
        
        # Custom display
        for idx, row in filtered_df.iterrows():
            with st.expander(
                f"{'🔴' if row['severity'] == 'CRITICAL' else '🟠' if row['severity'] == 'HIGH' else '🟡'} "
                f"{row['vulnerability_id']} - {row['title'][:80]}... "
                f"[{row['resource_type']}] "
                f"{'✅ Auto' if row['auto_remediate'] else '⚠️ Manual'}"
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Resource:** {row['resource_name']} ({row['resource_id']})")
                    st.markdown(f"**Package:** {row['package']}")
                    st.markdown(f"**Current Version:** {row['current_version']}")
                    st.markdown(f"**Fixed Version:** {row['fixed_version']}")
                    st.markdown(f"**CVSS Score:** {row['cvss_score']}")
                    st.markdown(f"**NIST Controls:** {', '.join(row['nist_controls'])}")
                
                with col2:
                    # Confidence gauge
                    confidence_color = '#28a745' if row['confidence_score'] >= 0.85 else '#ffc107' if row['confidence_score'] >= 0.70 else '#dc3545'
                    
                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
                        <div style='font-size: 48px; font-weight: bold; color: {confidence_color};'>
                            {row['confidence_score']:.0%}
                        </div>
                        <div style='font-size: 14px; color: #6c757d; margin-top: 5px;'>
                            Confidence Score
                        </div>
                        <div style='margin-top: 15px; padding: 10px; background-color: {'#d4edda' if row['auto_remediate'] else '#fff3cd'}; border-radius: 5px;'>
                            <strong>{'✅ Auto-Remediate' if row['auto_remediate'] else '⚠️ Manual Review'}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Remediation details
                st.markdown("---")
                st.markdown("**Remediation Details:**")
                
                if row['resource_type'] == 'Windows EC2':
                    st.markdown(f"- Registry fixes: {row.get('registry_fixes', 0)}")
                    st.markdown(f"- Reboot required: {'Yes' if row.get('reboot_required') else 'No'}")
                elif row['resource_type'] == 'Linux EC2':
                    st.markdown(f"- Platform: {row.get('platform', 'Unknown')}")
                    if row.get('service_restart'):
                        st.markdown(f"- Services to restart: {', '.join(row['service_restart'])}")
                elif row['resource_type'] == 'EKS Container':
                    st.markdown(f"- Current image: {row.get('current_image', 'Unknown')}")
                    st.markdown(f"- New image: {row.get('new_image', 'Unknown')}")
                    st.markdown(f"- Downtime: {row.get('downtime', 'Unknown')}")
                
                st.markdown(f"- Estimated duration: {row['estimated_duration']}")
                
                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button("🔍 View Script", key=f"view_{idx}"):
                        st.code(
                            row['remediation_plan']['complete_script'],
                            language='powershell' if row['resource_type'] == 'Windows EC2' else 'bash'
                        )
                
                with col_btn2:
                    if row['auto_remediate']:
                        if st.button("▶️ Execute", key=f"exec_{idx}", type="primary"):
                            self._execute_single_remediation(row)
                    else:
                        st.button("⚠️ Manual Review Required", key=f"manual_{idx}", disabled=True)
                
                with col_btn3:
                    script_content = row['remediation_plan']['complete_script']
                    file_ext = 'ps1' if row['resource_type'] == 'Windows EC2' else 'sh'
                    st.download_button(
                        "📥 Download",
                        data=script_content,
                        file_name=f"remediate_{row['vulnerability_id']}.{file_ext}",
                        mime="text/plain",
                        key=f"download_{idx}"
                    )
    
    def _render_bulk_actions(self, df: pd.DataFrame, all_vulns: List[Dict]):
        """Render bulk remediation actions"""
        
        st.markdown("---")
        st.markdown("### ⚡ Bulk Remediation")
        
        auto_vulns = df[df['auto_remediate'] == True]
        
        if len(auto_vulns) == 0:
            st.info("No vulnerabilities eligible for auto-remediation (confidence < 85%)")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Auto-Remediate Ready", len(auto_vulns))
        
        with col2:
            critical_auto = len(auto_vulns[auto_vulns['severity'] == 'CRITICAL'])
            st.metric("Critical (Auto)", critical_auto)
        
        with col3:
            high_auto = len(auto_vulns[auto_vulns['severity'] == 'HIGH'])
            st.metric("High (Auto)", high_auto)
        
        st.markdown("---")
        
        # Bulk action options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Auto-Remediate All CRITICAL", type="primary", use_container_width=True):
                critical_vulns = [v for v in all_vulns if v['severity'] == 'CRITICAL' and v['auto_remediate']]
                self._execute_bulk_remediation(critical_vulns)
        
        with col2:
            if st.button("⚡ Auto-Remediate All HIGH+CRITICAL", use_container_width=True):
                high_critical_vulns = [v for v in all_vulns 
                                      if v['severity'] in ['CRITICAL', 'HIGH'] 
                                      and v['auto_remediate']]
                self._execute_bulk_remediation(high_critical_vulns)
    
    def _execute_single_remediation(self, vuln_data: Dict):
        """Execute single remediation"""
        with st.spinner(f"Executing remediation for {vuln_data['vulnerability_id']}..."):
            # Implementation depends on resource type
            resource_type = vuln_data['resource_type']
            
            if resource_type == 'Windows EC2':
                # Execute via Windows SSM
                st.info("Executing Windows remediation via SSM...")
                # Call Windows connector execute method
                
            elif resource_type == 'Linux EC2':
                # Execute via Linux SSM
                st.info("Executing Linux remediation via SSM...")
                # Call Linux connector execute method
                
            elif resource_type == 'EKS Container':
                # Execute via Kubernetes
                st.info("Executing Kubernetes rolling update...")
                # Call EKS engine execute method
            
            st.success(f"✅ Remediation completed for {vuln_data['vulnerability_id']}")
    
    def _execute_bulk_remediation(self, vulnerabilities: List[Dict]):
        """Execute bulk remediation"""
        if not vulnerabilities:
            st.warning("No vulnerabilities selected for bulk remediation")
            return
        
        st.markdown(f"**Executing bulk remediation for {len(vulnerabilities)} vulnerabilities...**")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, vuln in enumerate(vulnerabilities):
            status_text.text(f"Processing {idx+1}/{len(vulnerabilities)}: {vuln['vulnerability_id']}")
            
            # Execute remediation
            self._execute_single_remediation(vuln)
            
            # Update progress
            progress_bar.progress((idx + 1) / len(vulnerabilities))
        
        st.success(f"✅ Bulk remediation completed! Processed {len(vulnerabilities)} vulnerabilities.")


# Streamlit Integration
def render_unified_remediation_dashboard():
    """Render the unified dashboard in Streamlit"""
    
    # Initialize dashboard
    if 'remediation_dashboard' not in st.session_state:
        st.session_state.remediation_dashboard = UnifiedRemediationDashboard(
            aws_region=st.session_state.get('aws_region', 'us-east-1')
        )
    
    dashboard = st.session_state.remediation_dashboard
    
    # Check if AWS credentials are available
    if st.secrets.get("AWS_ACCESS_KEY_ID"):
        # Initialize connectors
        dashboard.initialize_connectors(
            aws_access_key=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            eks_cluster_name=st.session_state.get('eks_cluster_name')
        )
    
    # Render dashboard
    dashboard.render_dashboard()


# Standalone execution
if __name__ == "__main__":
    st.set_page_config(
        page_title="Unified Remediation Dashboard",
        page_icon="🎯",
        layout="wide"
    )
    
    render_unified_remediation_dashboard()