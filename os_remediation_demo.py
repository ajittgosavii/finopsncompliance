"""
🎯 DEMO APP - OS Remediation by Flavour
Quick demo showing Windows and Linux remediation organized by OS version

Run this file to see the OS flavour selection interface:
    streamlit run os_remediation_demo.py
"""

import streamlit as st

# Try to import the remediation modules
try:
    from windows_server_remediation import (
        WindowsServerRemediator,
        WINDOWS_SERVER_VERSIONS,
        render_windows_remediation_ui
    )
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

try:
    from linux_distribution_remediation import (
        LinuxRemediator,
        LINUX_DISTRIBUTIONS,
        render_linux_remediation_ui
    )
    LINUX_AVAILABLE = True
except ImportError:
    LINUX_AVAILABLE = False

# Configure page
st.set_page_config(
    page_title="OS Remediation by Flavour - Demo",
    page_icon="🖥️",
    layout="wide"
)

# Main title
st.markdown("# 🖥️ OS Vulnerability Remediation")
st.markdown("### Organized by Operating System Flavour")

st.markdown("---")

# Check if modules are available
if not WINDOWS_AVAILABLE and not LINUX_AVAILABLE:
    st.error("""
    ⚠️ Remediation modules not found!
    
    Please ensure these files are in the same directory:
    - windows_server_remediation.py
    - linux_distribution_remediation.py
    
    Or run the standalone modules directly:
    - streamlit run windows_server_remediation.py
    - streamlit run linux_distribution_remediation.py
    """)
    st.stop()

# Create tabs for Windows and Linux
os_tabs = st.tabs(["🪟 Windows Server", "🐧 Linux Distributions"])

# ==================== WINDOWS TAB ====================
with os_tabs[0]:
    if WINDOWS_AVAILABLE:
        render_windows_remediation_ui()
    else:
        st.error("Windows remediation module not available. Please add windows_server_remediation.py")

# ==================== LINUX TAB ====================
with os_tabs[1]:
    if LINUX_AVAILABLE:
        render_linux_remediation_ui()
    else:
        st.error("Linux remediation module not available. Please add linux_distribution_remediation.py")

# ==================== FOOTER ====================
st.markdown("---")

# Show available OS flavours
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🪟 Windows Versions Available")
    if WINDOWS_AVAILABLE:
        for version in WINDOWS_SERVER_VERSIONS.keys():
            st.write(f"✅ {version}")
    else:
        st.info("Module not loaded")

with col2:
    st.markdown("### 🐧 Linux Distributions Available")
    if LINUX_AVAILABLE:
        for distro in LINUX_DISTRIBUTIONS.keys():
            st.write(f"✅ {distro}")
    else:
        st.info("Module not loaded")

# Quick help
with st.expander("📖 Quick Help - How to Use", expanded=False):
    st.markdown("""
    ### How to Generate a Remediation Script:
    
    1. **Select your OS flavour** from the dropdown
       - Windows: Choose your Windows Server version
       - Linux: Choose your Linux distribution
    
    2. **Enter vulnerability details:**
       - CVE ID (e.g., CVE-2024-6387)
       - KB Number (Windows) or Package Name (Linux)
       - Severity level
    
    3. **Click "Generate Script"**
       - PowerShell script generated for Windows
       - Bash script generated for Linux
    
    4. **Download and execute**
       - Download the generated script
       - Review before running
       - Execute on your target system
    
    ### Supported OS Flavours:
    
    **Windows (5 versions):**
    - Windows Server 2025
    - Windows Server 2022
    - Windows Server 2019
    - Windows Server 2016
    - Windows Server 2012 R2
    
    **Linux (11 distributions):**
    - Amazon Linux 2 / 2023
    - RHEL 7 / 8 / 9
    - Ubuntu 18.04 / 20.04 / 22.04 / 24.04 LTS
    - CentOS 8 / Rocky Linux 8
    - AlmaLinux 9
    """)

# Module status
st.markdown("---")
st.markdown("#### 📊 Module Status")
col_status1, col_status2 = st.columns(2)

with col_status1:
    if WINDOWS_AVAILABLE:
        st.success("✅ Windows remediation module loaded")
    else:
        st.error("❌ Windows remediation module not found")

with col_status2:
    if LINUX_AVAILABLE:
        st.success("✅ Linux remediation module loaded")
    else:
        st.error("❌ Linux remediation module not found")