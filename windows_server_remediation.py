"""
🪟 Windows Server Vulnerability Remediation Module
Standalone module for Windows Server vulnerability management and remediation

Supported Versions:
- Windows Server 2025 (Build 26100)
- Windows Server 2022 (Build 20348)
- Windows Server 2019 (Build 17763)
- Windows Server 2016 (Build 14393)
- Windows Server 2012 R2 (Build 9600)

Features:
- PowerShell remediation script generation
- System restore point creation
- KB article installation
- Automatic rollback on failure
- Reboot scheduling
- JSON report generation
- WSUS integration support
- Chocolatey package management

Version: 1.0 Standalone
Author: Cloud Security Team
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
import json
import re

# ==================== WINDOWS SERVER CONFIGURATIONS ====================

WINDOWS_SERVER_VERSIONS = {
    'Windows Server 2025': {
        'build': '26100',
        'release_date': '2024',
        'support_end': '2034',
        'patch_mechanism': 'Windows Update',
        'package_manager': 'winget',
        'powershell_version': '7.4+',
        'update_commands': [
            'Install-WindowsUpdate -AcceptAll -AutoReboot',
            'winget upgrade --all --silent'
        ],
        'features': [
            'Hotpatch support',
            'Modern authentication',
            'Enhanced security baseline',
            'Container support improved'
        ]
    },
    'Windows Server 2022': {
        'build': '20348',
        'release_date': '2021',
        'support_end': '2031',
        'patch_mechanism': 'Windows Update',
        'package_manager': 'chocolatey',
        'powershell_version': '5.1 / 7.0+',
        'update_commands': [
            'Install-WindowsUpdate -AcceptAll -AutoReboot',
            'choco upgrade all -y'
        ],
        'features': [
            'Secured-core server',
            'Windows Admin Center',
            'Hybrid capabilities',
            'SMB over QUIC'
        ]
    },
    'Windows Server 2019': {
        'build': '17763',
        'release_date': '2018',
        'support_end': '2029',
        'patch_mechanism': 'Windows Update / WSUS',
        'package_manager': 'chocolatey',
        'powershell_version': '5.1',
        'update_commands': [
            'Install-WindowsUpdate -AcceptAll -AutoReboot',
            'choco upgrade all -y'
        ],
        'features': [
            'Hyper-V improvements',
            'Storage Spaces Direct',
            'System Insights',
            'Windows Defender ATP'
        ]
    },
    'Windows Server 2016': {
        'build': '14393',
        'release_date': '2016',
        'support_end': '2027',
        'patch_mechanism': 'Windows Update / WSUS',
        'package_manager': 'chocolatey',
        'powershell_version': '5.0 / 5.1',
        'update_commands': [
            'Install-WindowsUpdate -AcceptAll -AutoReboot'
        ],
        'features': [
            'Nano Server',
            'Containers support',
            'Nested virtualization',
            'Software-defined networking'
        ]
    },
    'Windows Server 2012 R2': {
        'build': '9600',
        'release_date': '2013',
        'support_end': '2023 (Extended until 2026 with ESU)',
        'patch_mechanism': 'Windows Update / WSUS',
        'package_manager': 'chocolatey',
        'powershell_version': '4.0',
        'update_commands': [
            'wuauclt /detectnow /updatenow'
        ],
        'features': [
            'Storage Spaces',
            'Work Folders',
            'Hyper-V Replica',
            'DirectAccess'
        ],
        'notes': 'Extended Security Updates available'
    }
}

# Common Windows vulnerabilities by category
VULNERABILITY_CATEGORIES = {
    'RCE': 'Remote Code Execution',
    'EoP': 'Elevation of Privilege',
    'ID': 'Information Disclosure',
    'DoS': 'Denial of Service',
    'SFB': 'Security Feature Bypass',
    'Tampering': 'Tampering'
}

# Critical Windows components
CRITICAL_COMPONENTS = [
    'Windows Kernel',
    'Remote Desktop Services',
    'SMB Server',
    'DNS Server',
    'Active Directory',
    'IIS',
    '.NET Framework',
    'Windows Defender',
    'PowerShell'
]

# ==================== WINDOWS SERVER REMEDIATOR CLASS ====================

class WindowsServerRemediator:
    """
    Windows Server Vulnerability Remediation Engine
    
    Generates PowerShell scripts for automated vulnerability remediation
    across all supported Windows Server versions.
    """
    
    def __init__(self, claude_client=None):
        """
        Initialize Windows Server Remediator
        
        Args:
            claude_client: Optional Anthropic Claude client for AI-enhanced analysis
        """
        self.client = claude_client
        self.versions = WINDOWS_SERVER_VERSIONS
        self.remediation_history = []
    
    def generate_remediation_script(self, vulnerability: Dict, 
                                   server_version: str,
                                   custom_options: Optional[Dict] = None) -> str:
        """
        Generate PowerShell remediation script for Windows Server
        
        Args:
            vulnerability: Vulnerability details (CVE, KB, package, etc.)
            server_version: Windows Server version
            custom_options: Optional custom configuration
        
        Returns:
            Complete PowerShell remediation script
        """
        version_info = self.versions.get(server_version, self.versions['Windows Server 2022'])
        
        cve_id = vulnerability.get('cve_id', 'N/A')
        kb_number = vulnerability.get('kb_number', 'KB5000000')
        package = vulnerability.get('package', 'Unknown')
        severity = vulnerability.get('severity', 'HIGH')
        
        script = f"""#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Windows Server Vulnerability Remediation Script
    
.DESCRIPTION
    Automated remediation for {cve_id} on {server_version}
    
.NOTES
    CVE ID:       {cve_id}
    KB Number:    {kb_number}
    Package:      {package}
    Severity:     {severity}
    Server:       {server_version}
    Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
.PARAMETER DryRun
    If specified, simulates the remediation without making changes
    
.PARAMETER SkipReboot
    If specified, skips automatic reboot even if required
    
.PARAMETER BackupPath
    Custom path for pre-remediation backup (default: C:\\Temp\\Backup)
    
.EXAMPLE
    .\\Remediate-{cve_id.replace('-', '_')}.ps1
    
.EXAMPLE
    .\\Remediate-{cve_id.replace('-', '_')}.ps1 -DryRun -SkipReboot
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$DryRun,
    
    [Parameter()]
    [switch]$SkipReboot,
    
    [Parameter()]
    [string]$BackupPath = "C:\\Temp\\Backup"
)

# ========== CONFIGURATION ==========
$ErrorActionPreference = 'Stop'
$VerbosePreference = 'Continue'

$Config = @{{
    CVE_ID          = "{cve_id}"
    KB_NUMBER       = "{kb_number}"
    PACKAGE         = "{package}"
    SEVERITY        = "{severity}"
    SERVER_VERSION  = "{server_version}"
    BUILD_NUMBER    = "{version_info['build']}"
    TIMESTAMP       = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
}}

# ========== FUNCTIONS ==========

function Write-Log {{
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter()]
        [ValidateSet('Info', 'Warning', 'Error', 'Success')]
        [string]$Level = 'Info'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {{
        'Info'    {{ 'Cyan' }}
        'Warning' {{ 'Yellow' }}
        'Error'   {{ 'Red' }}
        'Success' {{ 'Green' }}
    }}
    
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage -ForegroundColor $color
    
    # Log to file
    $logFile = "C:\\Temp\\Remediation_$($Config.CVE_ID.Replace('-','_')).log"
    Add-Content -Path $logFile -Value $logMessage
}}

function Test-Prerequisites {{
    Write-Log "Checking prerequisites..." -Level Info
    
    # Check if running as Administrator
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {{
        Write-Log "ERROR: This script must be run as Administrator" -Level Error
        exit 1
    }}
    
    # Check Windows version
    $osVersion = (Get-WmiObject Win32_OperatingSystem).Caption
    Write-Log "Operating System: $osVersion" -Level Info
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    Write-Log "PowerShell Version: $psVersion" -Level Info
    
    # Check disk space (require at least 5GB free)
    $systemDrive = $env:SystemDrive
    $freeSpace = (Get-PSDrive $systemDrive.TrimEnd(':')).Free / 1GB
    
    if ($freeSpace -lt 5) {{
        Write-Log "WARNING: Low disk space. Only $([math]::Round($freeSpace, 2)) GB free" -Level Warning
    }}
    
    Write-Log "Prerequisites check completed" -Level Success
}}

function New-PreRemediationSnapshot {{
    Write-Log "Creating pre-remediation snapshot..." -Level Info
    
    if ($DryRun) {{
        Write-Log "DRY RUN: Would create system restore point" -Level Info
        return $true
    }}
    
    try {{
        # Enable System Restore if not already enabled
        Enable-ComputerRestore -Drive "$env:SystemDrive\\" -ErrorAction SilentlyContinue
        
        # Create restore point
        $description = "Pre-Remediation-$($Config.CVE_ID)-$($Config.TIMESTAMP)"
        Checkpoint-Computer -Description $description -RestorePointType "MODIFY_SETTINGS"
        
        Write-Log "System restore point created: $description" -Level Success
        
        # Backup current Windows Update list
        $backupDir = "$BackupPath\\$($Config.TIMESTAMP)"
        New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
        
        Get-HotFix | Export-Csv -Path "$backupDir\\Installed-Updates-Before.csv" -NoTypeInformation
        
        # Export system info
        $sysInfo = @{{
            Timestamp = $Config.TIMESTAMP
            ComputerName = $env:COMPUTERNAME
            OSVersion = (Get-WmiObject Win32_OperatingSystem).Caption
            OSBuild = (Get-WmiObject Win32_OperatingSystem).BuildNumber
            InstalledUpdates = (Get-HotFix).Count
        }}
        
        $sysInfo | ConvertTo-Json | Out-File "$backupDir\\System-Info-Before.json"
        
        Write-Log "Backup created at: $backupDir" -Level Success
        return $true
        
    }} catch {{
        Write-Log "Failed to create snapshot: $_" -Level Error
        return $false
    }}
}}

function Install-PSWindowsUpdate {{
    Write-Log "Checking for PSWindowsUpdate module..." -Level Info
    
    if (-not (Get-Module -ListAvailable -Name PSWindowsUpdate)) {{
        Write-Log "Installing PSWindowsUpdate module..." -Level Info
        
        if ($DryRun) {{
            Write-Log "DRY RUN: Would install PSWindowsUpdate module" -Level Info
            return
        }}
        
        try {{
            Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction Stop
            Install-Module -Name PSWindowsUpdate -Force -AllowClobber -ErrorAction Stop
            Import-Module PSWindowsUpdate -ErrorAction Stop
            
            Write-Log "PSWindowsUpdate module installed successfully" -Level Success
        }} catch {{
            Write-Log "Failed to install PSWindowsUpdate: $_" -Level Warning
        }}
    }} else {{
        Import-Module PSWindowsUpdate -ErrorAction SilentlyContinue
        Write-Log "PSWindowsUpdate module already installed" -Level Info
    }}
}}

function Install-VulnerabilityFix {{
    Write-Log "Starting vulnerability remediation..." -Level Info
    
    if ($DryRun) {{
        Write-Log "DRY RUN: Would install updates for $($Config.CVE_ID)" -Level Info
        return @{{
            Status = "Simulated"
            UpdatesInstalled = 0
        }}
    }}
    
    try {{
        # Enable TLS 1.2 for secure downloads
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        
        # Method 1: Try specific KB installation if available
        if ($Config.KB_NUMBER -ne "KB5000000") {{
            Write-Log "Attempting to install specific KB: $($Config.KB_NUMBER)" -Level Info
            
            try {{
"""

        # Add version-specific update commands
        for cmd in version_info['update_commands']:
            script += f"                {cmd}\n"
        
        script += f"""                
                # Try direct KB installation
                if (Get-Module -Name PSWindowsUpdate -ListAvailable) {{
                    $kbResult = Get-WindowsUpdate -KBArticleID $Config.KB_NUMBER -Install -AcceptAll -IgnoreReboot
                    
                    if ($kbResult) {{
                        Write-Log "KB $($Config.KB_NUMBER) installation initiated" -Level Success
                    }}
                }}
                
            }} catch {{
                Write-Log "Direct KB installation failed: $_" -Level Warning
                Write-Log "Falling back to general Windows Update..." -Level Info
            }}
        }}
        
        # Method 2: General Windows Update
        Write-Log "Running Windows Update scan..." -Level Info
        
        if (Get-Module -Name PSWindowsUpdate -ListAvailable) {{
            # Get available updates
            $updates = Get-WindowsUpdate -MicrosoftUpdate -Verbose
            
            if ($updates) {{
                Write-Log "Found $($updates.Count) available update(s)" -Level Info
                
                # Install updates
                $installResult = Install-WindowsUpdate -MicrosoftUpdate -AcceptAll -IgnoreReboot -Verbose
                
                Write-Log "Windows updates installed successfully" -Level Success
                
                return @{{
                    Status = "Success"
                    UpdatesInstalled = $installResult.Count
                    Updates = $installResult
                }}
            }} else {{
                Write-Log "No updates found. System may already be patched." -Level Info
                
                return @{{
                    Status = "No_Updates_Available"
                    UpdatesInstalled = 0
                }}
            }}
        }} else {{
            Write-Log "PSWindowsUpdate not available, using native methods..." -Level Warning
            
            # Fallback to COM object method
            $updateSession = New-Object -ComObject Microsoft.Update.Session
            $updateSearcher = $updateSession.CreateUpdateSearcher()
            
            Write-Log "Searching for updates..." -Level Info
            $searchResult = $updateSearcher.Search("IsInstalled=0")
            
            if ($searchResult.Updates.Count -gt 0) {{
                Write-Log "Found $($searchResult.Updates.Count) update(s)" -Level Info
                
                $updatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl
                
                foreach ($update in $searchResult.Updates) {{
                    if ($update.IsDownloaded) {{
                        $updatesToInstall.Add($update) | Out-Null
                    }}
                }}
                
                if ($updatesToInstall.Count -gt 0) {{
                    $installer = $updateSession.CreateUpdateInstaller()
                    $installer.Updates = $updatesToInstall
                    $installationResult = $installer.Install()
                    
                    Write-Log "Updates installed. Result code: $($installationResult.ResultCode)" -Level Success
                    
                    return @{{
                        Status = "Success"
                        UpdatesInstalled = $updatesToInstall.Count
                        ResultCode = $installationResult.ResultCode
                    }}
                }} else {{
                    Write-Log "Updates need to be downloaded first" -Level Warning
                    
                    return @{{
                        Status = "Download_Required"
                        UpdatesInstalled = 0
                    }}
                }}
            }} else {{
                Write-Log "No updates available" -Level Info
                
                return @{{
                    Status = "Up_To_Date"
                    UpdatesInstalled = 0
                }}
            }}
        }}
        
    }} catch {{
        Write-Log "Remediation failed: $_" -Level Error
        throw
    }}
}}

function Test-RemediationSuccess {{
    Write-Log "Verifying remediation success..." -Level Info
    
    try {{
        # Check if KB is installed
        if ($Config.KB_NUMBER -ne "KB5000000") {{
            $kbInstalled = Get-HotFix | Where-Object {{ $_.HotFixID -eq $Config.KB_NUMBER }}
            
            if ($kbInstalled) {{
                Write-Log "KB $($Config.KB_NUMBER) is installed" -Level Success
                return $true
            }} else {{
                Write-Log "KB $($Config.KB_NUMBER) is NOT installed" -Level Warning
                
                # Check if update is pending reboot
                $pendingReboot = Test-PendingReboot
                if ($pendingReboot) {{
                    Write-Log "System has pending reboot. KB may be installed after reboot." -Level Info
                    return $true
                }}
                
                return $false
            }}
        }} else {{
            Write-Log "Specific KB not provided. Verifying general update status..." -Level Info
            
            # Verify system is up to date
            if (Get-Module -Name PSWindowsUpdate -ListAvailable) {{
                $updates = Get-WindowsUpdate -MicrosoftUpdate
                
                if ($updates.Count -eq 0) {{
                    Write-Log "System is up to date" -Level Success
                    return $true
                }} else {{
                    Write-Log "System has $($updates.Count) pending update(s)" -Level Warning
                    return $false
                }}
            }} else {{
                Write-Log "Unable to verify update status without PSWindowsUpdate module" -Level Warning
                return $null
            }}
        }}
        
    }} catch {{
        Write-Log "Verification failed: $_" -Level Error
        return $false
    }}
}}

function Test-PendingReboot {{
    # Check various registry keys for pending reboot
    $rebootPending = $false
    
    # Check Component Based Servicing
    $cbs = Get-ChildItem "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing\\RebootPending" -ErrorAction SilentlyContinue
    if ($cbs) {{ $rebootPending = $true }}
    
    # Check Windows Update
    $wu = Get-Item "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\RebootRequired" -ErrorAction SilentlyContinue
    if ($wu) {{ $rebootPending = $true }}
    
    # Check PendingFileRenameOperations
    $pfr = Get-ItemProperty "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" -Name PendingFileRenameOperations -ErrorAction SilentlyContinue
    if ($pfr) {{ $rebootPending = $true }}
    
    return $rebootPending
}}

function Invoke-SystemReboot {{
    param(
        [int]$DelayMinutes = 5
    )
    
    if ($SkipReboot) {{
        Write-Log "Reboot skipped as per -SkipReboot parameter" -Level Warning
        Write-Log "IMPORTANT: Manual reboot required to complete remediation" -Level Warning
        return
    }}
    
    if ($DryRun) {{
        Write-Log "DRY RUN: Would schedule reboot in $DelayMinutes minutes" -Level Info
        return
    }}
    
    $delaySeconds = $DelayMinutes * 60
    $message = "System will reboot in $DelayMinutes minutes to complete security updates for $($Config.CVE_ID)"
    
    Write-Log "Scheduling system reboot in $DelayMinutes minutes..." -Level Warning
    
    shutdown /r /t $delaySeconds /c $message
    
    Write-Log "Reboot scheduled. Users will be notified." -Level Info
}}

function New-RemediationReport {{
    param(
        [Parameter(Mandatory=$true)]
        $RemediationResult,
        
        [Parameter(Mandatory=$true)]
        $VerificationResult
    )
    
    Write-Log "Generating remediation report..." -Level Info
    
    $report = @{{
        Metadata = @{{
            CVE_ID = $Config.CVE_ID
            KB_NUMBER = $Config.KB_NUMBER
            PACKAGE = $Config.PACKAGE
            SEVERITY = $Config.SEVERITY
            SERVER_VERSION = $Config.SERVER_VERSION
            BUILD_NUMBER = $Config.BUILD_NUMBER
        }}
        Execution = @{{
            Timestamp = $Config.TIMESTAMP
            DryRun = $DryRun.IsPresent
            ComputerName = $env:COMPUTERNAME
            ExecutedBy = $env:USERNAME
            Duration = $null  # Will be calculated
        }}
        Results = @{{
            RemediationStatus = $RemediationResult.Status
            UpdatesInstalled = $RemediationResult.UpdatesInstalled
            VerificationStatus = $VerificationResult
            RebootRequired = Test-PendingReboot
        }}
        SystemInfo = @{{
            OSVersion = (Get-WmiObject Win32_OperatingSystem).Caption
            OSBuild = (Get-WmiObject Win32_OperatingSystem).BuildNumber
            LastBootTime = (Get-WmiObject Win32_OperatingSystem).LastBootUpTime
            InstalledUpdates = (Get-HotFix).Count
        }}
    }}
    
    $reportPath = "C:\\Temp\\Remediation_Report_$($Config.CVE_ID.Replace('-','_'))_$($Config.TIMESTAMP).json"
    $report | ConvertTo-Json -Depth 5 | Out-File $reportPath
    
    Write-Log "Report saved to: $reportPath" -Level Success
    
    return $reportPath
}}

function Invoke-Rollback {{
    Write-Log "Initiating rollback procedure..." -Level Warning
    
    if ($DryRun) {{
        Write-Log "DRY RUN: Would restore to latest restore point" -Level Info
        return
    }}
    
    try {{
        # Get most recent restore point
        $restorePoint = Get-ComputerRestorePoint | 
                       Sort-Object CreationTime -Descending | 
                       Select-Object -First 1
        
        if ($restorePoint) {{
            Write-Log "Rolling back to restore point: $($restorePoint.Description)" -Level Info
            
            Restore-Computer -RestorePoint $restorePoint.SequenceNumber -Confirm:$false
            
            Write-Log "Rollback initiated. System will restart." -Level Success
        }} else {{
            Write-Log "No restore points available for rollback" -Level Error
        }}
        
    }} catch {{
        Write-Log "Rollback failed: $_" -Level Error
    }}
}}

# ========== MAIN EXECUTION ==========

try {{
    Write-Log "========================================" -Level Info
    Write-Log "Windows Server Remediation Script" -Level Info
    Write-Log "========================================" -Level Info
    Write-Log "CVE:     $($Config.CVE_ID)" -Level Info
    Write-Log "KB:      $($Config.KB_NUMBER)" -Level Info
    Write-Log "Server:  $($Config.SERVER_VERSION)" -Level Info
    Write-Log "Mode:    $(if ($DryRun) {{'DRY RUN'}} else {{'LIVE'}})" -Level Info
    Write-Log "========================================" -Level Info
    Write-Log "" -Level Info
    
    # Step 1: Prerequisites
    Test-Prerequisites
    
    # Step 2: Create snapshot
    $snapshotResult = New-PreRemediationSnapshot
    if (-not $snapshotResult -and -not $DryRun) {{
        Write-Log "Failed to create snapshot. Aborting for safety." -Level Error
        exit 1
    }}
    
    # Step 3: Install PSWindowsUpdate module
    Install-PSWindowsUpdate
    
    # Step 4: Install vulnerability fix
    $remediationResult = Install-VulnerabilityFix
    
    Write-Log "" -Level Info
    Write-Log "Remediation Status: $($remediationResult.Status)" -Level Info
    Write-Log "Updates Installed: $($remediationResult.UpdatesInstalled)" -Level Info
    
    # Step 5: Verify remediation
    $verificationResult = Test-RemediationSuccess
    
    if ($verificationResult) {{
        Write-Log "" -Level Info
        Write-Log "========================================" -Level Success
        Write-Log "REMEDIATION SUCCESSFUL" -Level Success
        Write-Log "========================================" -Level Success
    }} elseif ($verificationResult -eq $false) {{
        Write-Log "" -Level Info
        Write-Log "========================================" -Level Warning
        Write-Log "REMEDIATION INCOMPLETE" -Level Warning
        Write-Log "========================================" -Level Warning
        Write-Log "The vulnerability fix may require additional steps or a system reboot" -Level Warning
    }} else {{
        Write-Log "" -Level Info
        Write-Log "Verification status: Unknown" -Level Info
    }}
    
    # Step 6: Generate report
    $reportPath = New-RemediationReport -RemediationResult $remediationResult -VerificationResult $verificationResult
    
    # Step 7: Check if reboot is required
    $rebootRequired = Test-PendingReboot
    
    if ($rebootRequired) {{
        Write-Log "" -Level Info
        Write-Log "========================================" -Level Warning
        Write-Log "SYSTEM REBOOT REQUIRED" -Level Warning
        Write-Log "========================================" -Level Warning
        
        if (-not $DryRun) {{
            Invoke-SystemReboot -DelayMinutes 5
        }}
    }} else {{
        Write-Log "" -Level Info
        Write-Log "No reboot required at this time" -Level Success
    }}
    
    Write-Log "" -Level Info
    Write-Log "Remediation process completed" -Level Success
    Write-Log "Report: $reportPath" -Level Info
    
    exit 0
    
}} catch {{
    Write-Log "" -Level Error
    Write-Log "========================================" -Level Error
    Write-Log "REMEDIATION FAILED" -Level Error
    Write-Log "========================================" -Level Error
    Write-Log "Error: $_" -Level Error
    
    # Attempt rollback
    Write-Log "Attempting automatic rollback..." -Level Warning
    Invoke-Rollback
    
    exit 1
}}

# End of script
"""
        
        # Record in history
        self.remediation_history.append({
            'cve_id': cve_id,
            'server_version': server_version,
            'timestamp': datetime.now().isoformat(),
            'script_generated': True
        })
        
        return script
    
    def get_version_info(self, server_version: str) -> Dict:
        """Get detailed information about a Windows Server version"""
        return self.versions.get(server_version, {})
    
    def list_supported_versions(self) -> List[str]:
        """Get list of supported Windows Server versions"""
        return list(self.versions.keys())
    
    def get_remediation_history(self) -> List[Dict]:
        """Get remediation script generation history"""
        return self.remediation_history


# ==================== STREAMLIT UI FUNCTIONS ====================

def render_windows_remediation_ui():
    """Render Streamlit UI for Windows Server remediation"""
    
    st.markdown("## 🪟 Windows Server Vulnerability Remediation")
    
    # Initialize remediator with safe error handling
    remediator = st.session_state.get('windows_remediator')
    
    # Check if remediator exists and is the right type
    if not remediator or not isinstance(remediator, WindowsServerRemediator):
        claude_client = st.session_state.get('claude_client')
        remediator = WindowsServerRemediator(claude_client)
        st.session_state.windows_remediator = remediator
    
    # Double-check that we have a valid remediator
    if not hasattr(remediator, 'list_supported_versions'):
        st.error("⚠️ Windows remediator initialization failed. Please refresh the page.")
        return
    
    # Version selector
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Supported Windows Server Versions")
        for version in remediator.list_supported_versions():
            info = remediator.get_version_info(version)
            with st.expander(f"📦 {version}", expanded=False):
                st.write(f"**Build:** {info.get('build', 'N/A')}")
                st.write(f"**Released:** {info.get('release_date', 'N/A')}")
                st.write(f"**Support Until:** {info.get('support_end', 'N/A')}")
                st.write(f"**Update Mechanism:** {info.get('patch_mechanism', 'N/A')}")
                st.write(f"**Package Manager:** {info.get('package_manager', 'N/A')}")
                st.write(f"**PowerShell:** {info.get('powershell_version', 'N/A')}")
                
                if 'features' in info:
                    st.write("**Key Features:**")
                    for feature in info['features']:
                        st.write(f"  • {feature}")
    
    with col2:
        st.markdown("### Generate Remediation Script")
        
        # Input form
        selected_version = st.selectbox(
            "Select Windows Server Version",
            options=remediator.list_supported_versions(),
            key="win_version_select"
        )
        
        cve_id = st.text_input(
            "CVE ID",
            placeholder="CVE-2024-12345",
            key="win_cve_id"
        )
        
        kb_number = st.text_input(
            "KB Article Number (optional)",
            placeholder="KB5043936",
            key="win_kb_number"
        )
        
        package = st.text_input(
            "Affected Package/Component",
            placeholder="e.g., Windows Kernel, SMB Server",
            key="win_package"
        )
        
        severity = st.selectbox(
            "Severity",
            options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            key="win_severity"
        )
        
        if st.button("🔨 Generate PowerShell Script", type="primary", use_container_width=True):
            if cve_id:
                vulnerability = {
                    'cve_id': cve_id,
                    'kb_number': kb_number if kb_number else 'KB5000000',
                    'package': package if package else 'Unknown',
                    'severity': severity
                }
                
                with st.spinner("Generating PowerShell script..."):
                    script = remediator.generate_remediation_script(
                        vulnerability,
                        selected_version
                    )
                
                st.success("✅ PowerShell script generated successfully!")
                
                # Display script
                st.markdown("### Generated PowerShell Script")
                st.code(script, language='powershell')
                
                # Download button
                st.download_button(
                    label="📥 Download PowerShell Script",
                    data=script,
                    file_name=f"Remediate-{cve_id.replace('-', '_')}.ps1",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("Please enter a CVE ID")
    
    # Remediation history
    st.markdown("---")
    st.markdown("### 📜 Remediation History")
    
    history = remediator.get_remediation_history()
    if history:
        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No remediation scripts generated yet")


# ==================== MODULE EXPORTS ====================

__all__ = [
    'WindowsServerRemediator',
    'WINDOWS_SERVER_VERSIONS',
    'render_windows_remediation_ui'
]

if __name__ == "__main__":
    st.set_page_config(
        page_title="Windows Server Remediation",
        page_icon="🪟",
        layout="wide"
    )
    render_windows_remediation_ui()
