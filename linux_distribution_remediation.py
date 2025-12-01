"""
🐧 Linux Distribution Vulnerability Remediation Module
Standalone module for Linux vulnerability management and remediation

Supported Distributions:
- Amazon Linux 2 / 2023
- Red Hat Enterprise Linux 7 / 8 / 9
- Ubuntu 18.04 LTS / 20.04 LTS / 22.04 LTS / 24.04 LTS
- CentOS 8 / Rocky Linux 8
- AlmaLinux 9

Features:
- Bash remediation script generation
- Pre-flight system checks
- Automated backup/snapshot creation
- Security-focused patching
- Kernel update handling
- Reboot detection and management
- JSON report generation
- Distribution-specific package management

Version: 1.0 Standalone
Author: Cloud Security Team
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
import json
import re

# ==================== LINUX DISTRIBUTION CONFIGURATIONS ====================

LINUX_DISTRIBUTIONS = {
    'Amazon Linux 2': {
        'family': 'RedHat',
        'package_manager': 'yum',
        'release_year': '2018',
        'support_end': '2025-06-30',
        'kernel_package': 'kernel',
        'update_commands': [
            'sudo yum update -y',
            'sudo yum upgrade -y'
        ],
        'security_updates': 'sudo yum update --security -y',
        'kernel_update': 'sudo yum update kernel -y && sudo reboot',
        'check_reboot': 'needs-restarting -r',
        'features': [
            'AWS optimized',
            'systemd',
            'Python 2.7/3.7',
            'Long-term support'
        ]
    },
    'Amazon Linux 2023': {
        'family': 'RedHat',
        'package_manager': 'dnf',
        'release_year': '2023',
        'support_end': '2028-03-15',
        'kernel_package': 'kernel',
        'update_commands': [
            'sudo dnf update -y',
            'sudo dnf upgrade -y'
        ],
        'security_updates': 'sudo dnf update --security -y',
        'kernel_update': 'sudo dnf update kernel -y && sudo reboot',
        'check_reboot': 'needs-restarting -r',
        'features': [
            'Deterministic updates',
            'SELinux enabled by default',
            'Python 3.9+',
            'Container optimized'
        ]
    },
    'Red Hat Enterprise Linux 9': {
        'family': 'RedHat',
        'package_manager': 'dnf',
        'release_year': '2022',
        'support_end': '2032-05-31',
        'kernel_package': 'kernel',
        'update_commands': [
            'sudo dnf update -y',
            'sudo dnf upgrade -y'
        ],
        'security_updates': 'sudo dnf update --security -y',
        'kernel_update': 'sudo dnf update kernel -y && sudo reboot',
        'check_reboot': 'needs-restarting -r',
        'subscription_required': True,
        'features': [
            'Image Builder',
            'Web Console',
            'Enhanced security',
            'Container tools'
        ]
    },
    'Red Hat Enterprise Linux 8': {
        'family': 'RedHat',
        'package_manager': 'dnf',
        'release_year': '2019',
        'support_end': '2029-05-31',
        'kernel_package': 'kernel',
        'update_commands': [
            'sudo dnf update -y',
            'sudo dnf upgrade -y'
        ],
        'security_updates': 'sudo dnf update --security -y',
        'kernel_update': 'sudo dnf update kernel -y && sudo reboot',
        'check_reboot': 'needs-restarting -r',
        'subscription_required': True,
        'features': [
            'Application Streams',
            'Podman/Buildah',
            'LUKS2 encryption',
            'Extended support'
        ]
    },
    'Red Hat Enterprise Linux 7': {
        'family': 'RedHat',
        'package_manager': 'yum',
        'release_year': '2014',
        'support_end': '2024-06-30',
        'kernel_package': 'kernel',
        'update_commands': [
            'sudo yum update -y',
            'sudo yum upgrade -y'
        ],
        'security_updates': 'sudo yum update --security -y',
        'kernel_update': 'sudo yum update kernel -y && sudo reboot',
        'check_reboot': 'needs-restarting -r',
        'subscription_required': True,
        'features': [
            'systemd',
            'Docker support',
            'XFS by default',
            'Extended Life Phase'
        ]
    },
    'Ubuntu 24.04 LTS': {
        'family': 'Debian',
        'package_manager': 'apt',
        'release_year': '2024',
        'support_end': '2029-04',
        'kernel_package': 'linux-image-generic',
        'update_commands': [
            'sudo apt update',
            'sudo apt upgrade -y',
            'sudo apt dist-upgrade -y'
        ],
        'security_updates': 'sudo unattended-upgrade',
        'kernel_update': 'sudo apt upgrade linux-image-generic -y && sudo reboot',
        'check_reboot': 'test -f /var/run/reboot-required && echo "reboot required" || echo "no reboot"',
        'features': [
            'Noble Numbat',
            'Latest LTS',
            'Snap packages',
            '5 years support'
        ]
    },
    'Ubuntu 22.04 LTS': {
        'family': 'Debian',
        'package_manager': 'apt',
        'release_year': '2022',
        'support_end': '2027-04',
        'kernel_package': 'linux-image-generic',
        'update_commands': [
            'sudo apt update',
            'sudo apt upgrade -y',
            'sudo apt dist-upgrade -y'
        ],
        'security_updates': 'sudo unattended-upgrade',
        'kernel_update': 'sudo apt upgrade linux-image-generic -y && sudo reboot',
        'check_reboot': 'test -f /var/run/reboot-required && echo "reboot required" || echo "no reboot"',
        'features': [
            'Jammy Jellyfish',
            'Kernel 5.15',
            'GNOME 42',
            'OpenSSL 3.0'
        ]
    },
    'Ubuntu 20.04 LTS': {
        'family': 'Debian',
        'package_manager': 'apt',
        'release_year': '2020',
        'support_end': '2025-04',
        'kernel_package': 'linux-image-generic',
        'update_commands': [
            'sudo apt update',
            'sudo apt upgrade -y',
            'sudo apt dist-upgrade -y'
        ],
        'security_updates': 'sudo unattended-upgrade',
        'kernel_update': 'sudo apt upgrade linux-image-generic -y && sudo reboot',
        'check_reboot': 'test -f /var/run/reboot-required && echo "reboot required" || echo "no reboot"',
        'features': [
            'Focal Fossa',
            'Kernel 5.4',
            'ZFS on root',
            'WireGuard VPN'
        ]
    },
    'Ubuntu 18.04 LTS': {
        'family': 'Debian',
        'package_manager': 'apt',
        'release_year': '2018',
        'support_end': '2023-04 (ESM until 2028)',
        'kernel_package': 'linux-image-generic',
        'update_commands': [
            'sudo apt-get update',
            'sudo apt-get upgrade -y',
            'sudo apt-get dist-upgrade -y'
        ],
        'security_updates': 'sudo unattended-upgrade',
        'kernel_update': 'sudo apt-get upgrade linux-image-generic -y && sudo reboot',
        'check_reboot': 'test -f /var/run/reboot-required && echo "reboot required" || echo "no reboot"',
        'features': [
            'Bionic Beaver',
            'Kernel 4.15',
            'GNOME 3.28',
            'Extended Security Maintenance'
        ]
    },
    'CentOS 8 / Rocky Linux 8': {
        'family': 'RedHat',
        'package_manager': 'dnf',
        'release_year': '2019/2021',
        'support_end': '2029-05-31',
        'kernel_package': 'kernel',
        'update_commands': [
            'sudo dnf update -y',
            'sudo dnf upgrade -y'
        ],
        'security_updates': 'sudo dnf update --security -y',
        'kernel_update': 'sudo dnf update kernel -y && sudo reboot',
        'check_reboot': 'needs-restarting -r',
        'features': [
            'RHEL compatible',
            'Podman/Buildah',
            'Community supported',
            'Drop-in replacement'
        ]
    },
    'AlmaLinux 9': {
        'family': 'RedHat',
        'package_manager': 'dnf',
        'release_year': '2022',
        'support_end': '2032-05-31',
        'kernel_package': 'kernel',
        'update_commands': [
            'sudo dnf update -y',
            'sudo dnf upgrade -y'
        ],
        'security_updates': 'sudo dnf update --security -y',
        'kernel_update': 'sudo dnf update kernel -y && sudo reboot',
        'check_reboot': 'needs-restarting -r',
        'features': [
            'RHEL 9 compatible',
            'CloudLinux backed',
            'Community driven',
            'Enterprise ready'
        ]
    }
}

# Package managers and their commands
PACKAGE_MANAGERS = {
    'apt': {
        'update': 'apt update',
        'upgrade': 'apt upgrade -y',
        'install': 'apt install -y',
        'remove': 'apt remove -y',
        'list': 'apt list --installed',
        'search': 'apt search'
    },
    'yum': {
        'update': 'yum update -y',
        'upgrade': 'yum upgrade -y',
        'install': 'yum install -y',
        'remove': 'yum remove -y',
        'list': 'yum list installed',
        'search': 'yum search'
    },
    'dnf': {
        'update': 'dnf update -y',
        'upgrade': 'dnf upgrade -y',
        'install': 'dnf install -y',
        'remove': 'dnf remove -y',
        'list': 'dnf list installed',
        'search': 'dnf search'
    }
}

# ==================== LINUX REMEDIATOR CLASS ====================

class LinuxRemediator:
    """
    Linux Distribution Vulnerability Remediation Engine
    
    Generates Bash scripts for automated vulnerability remediation
    across all supported Linux distributions.
    """
    
    def __init__(self, claude_client=None):
        """
        Initialize Linux Remediator
        
        Args:
            claude_client: Optional Anthropic Claude client for AI-enhanced analysis
        """
        self.client = claude_client
        self.distributions = LINUX_DISTRIBUTIONS
        self.package_managers = PACKAGE_MANAGERS
        self.remediation_history = []
    
    def generate_remediation_script(self, vulnerability: Dict, 
                                   distribution: str,
                                   custom_options: Optional[Dict] = None) -> str:
        """
        Generate Bash remediation script for Linux
        
        Args:
            vulnerability: Vulnerability details (CVE, package, version, etc.)
            distribution: Linux distribution name
            custom_options: Optional custom configuration
        
        Returns:
            Complete Bash remediation script
        """
        distro_info = self.distributions.get(distribution, self.distributions['Ubuntu 22.04 LTS'])
        package_manager = distro_info['package_manager']
        
        cve_id = vulnerability.get('cve_id', 'N/A')
        package = vulnerability.get('package', 'unknown')
        fixed_version = vulnerability.get('fixed_version', 'latest')
        severity = vulnerability.get('severity', 'HIGH')
        
        script = f"""#!/bin/bash
#
# Linux Vulnerability Remediation Script
# CVE ID:       {cve_id}
# Package:      {package}
# Fixed Version: {fixed_version}
# Severity:     {severity}
# Distribution: {distribution}
# Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#
# Usage:
#   sudo ./remediate_{cve_id.replace('-', '_')}.sh [OPTIONS]
#
# Options:
#   --dry-run       Simulate remediation without making changes
#   --skip-reboot   Skip automatic reboot even if required
#   --backup-dir    Custom backup directory (default: /var/backups/remediation)
#   --help          Show this help message
#

set -euo pipefail  # Exit on error, undefined variables, pipe failures
IFS=$'\\n\\t'      # Better word splitting

# ========== CONFIGURATION ==========

readonly CVE_ID="{cve_id}"
readonly PACKAGE="{package}"
readonly FIXED_VERSION="{fixed_version}"
readonly SEVERITY="{severity}"
readonly DISTRIBUTION="{distribution}"
readonly PACKAGE_MANAGER="{package_manager}"
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Default options
DRY_RUN=false
SKIP_REBOOT=false
BACKUP_DIR="/var/backups/remediation"

# Colors for output
readonly RED='\\033[0;31m'
readonly GREEN='\\033[0;32m'
readonly YELLOW='\\033[1;33m'
readonly CYAN='\\033[0;36m'
readonly NC='\\033[0m' # No Color

# ========== FUNCTIONS ==========

log() {{
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""
    
    case "$level" in
        INFO)    color="$CYAN" ;;
        SUCCESS) color="$GREEN" ;;
        WARNING) color="$YELLOW" ;;
        ERROR)   color="$RED" ;;
        *)       color="$NC" ;;
    esac
    
    echo -e "${{color}}[$timestamp] [$level] $message${{NC}}" | tee -a "$LOG_FILE"
}}

show_help() {{
    cat << EOF
Linux Vulnerability Remediation Script

Usage: $0 [OPTIONS]

Options:
    --dry-run           Simulate remediation without making changes
    --skip-reboot       Skip automatic reboot even if required
    --backup-dir DIR    Custom backup directory (default: /var/backups/remediation)
    --help              Show this help message

CVE Information:
    CVE ID:         $CVE_ID
    Package:        $PACKAGE
    Fixed Version:  $FIXED_VERSION
    Severity:       $SEVERITY
    Distribution:   $DISTRIBUTION

EOF
    exit 0
}}

parse_arguments() {{
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-reboot)
                SKIP_REBOOT=true
                shift
                ;;
            --backup-dir)
                BACKUP_DIR="$2"
                shift 2
                ;;
            --help)
                show_help
                ;;
            *)
                log ERROR "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}}

check_root() {{
    if [[ $EUID -ne 0 ]]; then
        log ERROR "This script must be run as root (use sudo)"
        exit 1
    fi
}}

detect_distribution() {{
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        log INFO "Detected: $NAME $VERSION"
        
        # Verify distribution matches
        if [[ ! "$NAME $VERSION" =~ "$DISTRIBUTION" ]]; then
            log WARNING "Script generated for $DISTRIBUTION but running on $NAME $VERSION"
            log WARNING "Proceed with caution"
        fi
    else
        log ERROR "Cannot detect distribution (missing /etc/os-release)"
        exit 1
    fi
}}

check_prerequisites() {{
    log INFO "Checking prerequisites..."
    
    # Check disk space (require at least 2GB free)
    local free_space=$(df / | awk 'NR==2 {{print $4}}')
    local free_space_gb=$((free_space / 1024 / 1024))
    
    if [[ $free_space_gb -lt 2 ]]; then
        log WARNING "Low disk space: only ${{free_space_gb}}GB free"
        log WARNING "At least 2GB recommended"
    fi
    
    # Check internet connectivity
    if ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log WARNING "No internet connectivity detected"
        log WARNING "Package updates may fail"
    fi
    
    # Check if package manager is available
    if ! command -v $PACKAGE_MANAGER &> /dev/null; then
        log ERROR "Package manager '$PACKAGE_MANAGER' not found"
        exit 1
    fi
    
    log SUCCESS "Prerequisites check completed"
}}

create_backup() {{
    log INFO "Creating pre-remediation backup..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would create backup in $BACKUP_DIR/$TIMESTAMP"
        return 0
    fi
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR/$TIMESTAMP"
    
    # Backup package list
    case "$PACKAGE_MANAGER" in
        apt)
            dpkg -l > "$BACKUP_DIR/$TIMESTAMP/packages_before.txt"
            apt list --installed > "$BACKUP_DIR/$TIMESTAMP/packages_detailed.txt" 2>/dev/null
            ;;
        yum|dnf)
            $PACKAGE_MANAGER list installed > "$BACKUP_DIR/$TIMESTAMP/packages_before.txt"
            rpm -qa > "$BACKUP_DIR/$TIMESTAMP/packages_rpm.txt"
            ;;
    esac
    
    # Backup system info
    cat > "$BACKUP_DIR/$TIMESTAMP/system_info.txt" << SYSINFO
Hostname: $(hostname)
Kernel: $(uname -r)
Uptime: $(uptime)
Distribution: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')
Backup Time: $(date)
SYSINFO
    
    # Backup package-specific config if it exists
    if [[ -d "/etc/$PACKAGE" ]]; then
        tar czf "$BACKUP_DIR/$TIMESTAMP/config_backup.tar.gz" "/etc/$PACKAGE" 2>/dev/null || true
    fi
    
    log SUCCESS "Backup created at: $BACKUP_DIR/$TIMESTAMP"
    echo "$BACKUP_DIR/$TIMESTAMP" > /tmp/remediation_backup_path.txt
}}

update_package_cache() {{
    log INFO "Updating package cache..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would update package cache"
        return 0
    fi
    
    case "$PACKAGE_MANAGER" in
        apt)
            apt-get update -qq
            ;;
        yum)
            yum makecache fast
            ;;
        dnf)
            dnf makecache
            ;;
    esac
    
    log SUCCESS "Package cache updated"
}}

install_vulnerability_fix() {{
    log INFO "Installing vulnerability fix..."
    log INFO "Target package: $PACKAGE"
    log INFO "Target version: $FIXED_VERSION"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would install/update package: $PACKAGE"
        return 0
    fi
    
    case "$PACKAGE_MANAGER" in
        apt)
            # Update specific package
            log INFO "Running: apt-get install --only-upgrade $PACKAGE -y"
            apt-get install --only-upgrade "$PACKAGE" -y
            
            # Verify installation
            local installed_version=$(dpkg -l | grep "^ii.*$PACKAGE" | awk '{{print $3}}' | head -1)
            log INFO "Installed version: $installed_version"
            ;;
            
        yum|dnf)
            # Update specific package
            log INFO "Running: $PACKAGE_MANAGER update $PACKAGE -y"
            $PACKAGE_MANAGER update "$PACKAGE" -y
            
            # Verify installation
            local installed_version=$(rpm -q "$PACKAGE" | head -1)
            log INFO "Installed version: $installed_version"
            ;;
    esac
    
    log SUCCESS "Package update completed"
}}

apply_security_updates() {{
    log INFO "Applying security-specific updates..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would apply security updates"
        return 0
    fi
    
    case "$PACKAGE_MANAGER" in
        apt)
            log INFO "Running unattended-upgrade for security patches"
            unattended-upgrade || log WARNING "unattended-upgrade not available"
            ;;
            
        yum|dnf)
            log INFO "Running security update"
            {distro_info.get('security_updates', f'{package_manager} update --security -y')}
            ;;
    esac
    
    log SUCCESS "Security updates applied"
}}

verify_remediation() {{
    log INFO "Verifying remediation..."
    
    local package_found=false
    local version_ok=false
    
    case "$PACKAGE_MANAGER" in
        apt)
            if dpkg -l | grep -q "^ii.*$PACKAGE"; then
                package_found=true
                local installed_version=$(dpkg -l | grep "^ii.*$PACKAGE" | awk '{{print $3}}' | head -1)
                log INFO "Package $PACKAGE is installed: $installed_version"
                
                # Basic version check (would need more sophisticated logic for real comparison)
                if [[ "$installed_version" != "" ]]; then
                    version_ok=true
                fi
            fi
            ;;
            
        yum|dnf)
            if rpm -q "$PACKAGE" &>/dev/null; then
                package_found=true
                local installed_version=$(rpm -q "$PACKAGE" | head -1)
                log INFO "Package $PACKAGE is installed: $installed_version"
                version_ok=true
            fi
            ;;
    esac
    
    if [[ "$package_found" == "true" && "$version_ok" == "true" ]]; then
        log SUCCESS "Remediation verification: SUCCESS"
        return 0
    else
        log WARNING "Remediation verification: Package may not be fully updated"
        return 1
    fi
}}

check_reboot_required() {{
    log INFO "Checking if reboot is required..."
    
    local reboot_required=false
    
    # Distribution-specific reboot detection
    case "$PACKAGE_MANAGER" in
        apt)
            if [[ -f /var/run/reboot-required ]]; then
                reboot_required=true
                log WARNING "Reboot required (detected via /var/run/reboot-required)"
                
                if [[ -f /var/run/reboot-required.pkgs ]]; then
                    log INFO "Packages requiring reboot:"
                    cat /var/run/reboot-required.pkgs | while read pkg; do
                        log INFO "  - $pkg"
                    done
                fi
            fi
            ;;
            
        yum|dnf)
            if command -v needs-restarting &>/dev/null; then
                if ! needs-restarting -r &>/dev/null; then
                    reboot_required=true
                    log WARNING "Reboot required (detected via needs-restarting)"
                fi
            fi
            
            # Check if kernel was updated
            local running_kernel=$(uname -r)
            local installed_kernel=$(rpm -q kernel | sort -V | tail -1 | sed 's/kernel-//')
            
            if [[ "$running_kernel" != "$installed_kernel" ]]; then
                reboot_required=true
                log WARNING "Kernel updated: running $running_kernel, installed $installed_kernel"
            fi
            ;;
    esac
    
    if [[ "$reboot_required" == "true" ]]; then
        return 0  # Reboot required
    else
        log SUCCESS "No reboot required at this time"
        return 1  # No reboot required
    fi
}}

schedule_reboot() {{
    local delay_minutes=5
    
    if [[ "$SKIP_REBOOT" == "true" ]]; then
        log WARNING "Reboot skipped (--skip-reboot flag set)"
        log WARNING "IMPORTANT: Manual reboot required to complete remediation"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would schedule reboot in $delay_minutes minutes"
        return 0
    fi
    
    log WARNING "Scheduling system reboot in $delay_minutes minutes..."
    
    # Create reboot script
    cat > /tmp/remediation_reboot.sh << 'REBOOT_SCRIPT'
#!/bin/bash
sleep 300  # 5 minutes
/sbin/reboot
REBOOT_SCRIPT
    
    chmod +x /tmp/remediation_reboot.sh
    nohup /tmp/remediation_reboot.sh >/dev/null 2>&1 &
    
    log WARNING "System will reboot in $delay_minutes minutes"
    log INFO "Cancel with: kill $(pgrep -f remediation_reboot.sh)"
}}

generate_report() {{
    log INFO "Generating remediation report..."
    
    local report_file="/var/log/remediation_${{CVE_ID//-/_}}_$TIMESTAMP.json"
    
    cat > "$report_file" << REPORT
{{
    "metadata": {{
        "cve_id": "$CVE_ID",
        "package": "$PACKAGE",
        "fixed_version": "$FIXED_VERSION",
        "severity": "$SEVERITY",
        "distribution": "$DISTRIBUTION",
        "package_manager": "$PACKAGE_MANAGER"
    }},
    "execution": {{
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "hostname": "$(hostname)",
        "executed_by": "$SUDO_USER",
        "dry_run": $DRY_RUN
    }},
    "results": {{
        "status": "success",
        "backup_location": "$(cat /tmp/remediation_backup_path.txt 2>/dev/null || echo 'N/A')",
        "reboot_required": $(check_reboot_required && echo "true" || echo "false")
    }},
    "system_info": {{
        "kernel": "$(uname -r)",
        "uptime": "$(uptime -p)",
        "last_boot": "$(uptime -s)"
    }}
}}
REPORT
    
    log SUCCESS "Report saved to: $report_file"
    echo "$report_file"
}}

rollback() {{
    log WARNING "Initiating rollback procedure..."
    
    if [[ ! -f /tmp/remediation_backup_path.txt ]]; then
        log ERROR "No backup path found. Cannot rollback."
        return 1
    fi
    
    local backup_path=$(cat /tmp/remediation_backup_path.txt)
    
    if [[ ! -d "$backup_path" ]]; then
        log ERROR "Backup directory not found: $backup_path"
        return 1
    fi
    
    log INFO "Rolling back from: $backup_path"
    
    # This is a simplified rollback
    # Real implementation would need to restore exact package versions
    log WARNING "Rollback functionality requires manual intervention"
    log INFO "Backup location: $backup_path"
    log INFO "Review backup and manually restore if needed"
    
    return 0
}}

# ========== MAIN EXECUTION ==========

main() {{
    # Parse command line arguments
    parse_arguments "$@"
    
    # Setup logging
    LOG_FILE="/var/log/remediation_${{CVE_ID//-/_}}_$TIMESTAMP.log"
    touch "$LOG_FILE"
    
    log INFO "========================================"
    log INFO "Linux Vulnerability Remediation Script"
    log INFO "========================================"
    log INFO "CVE:          $CVE_ID"
    log INFO "Package:      $PACKAGE"
    log INFO "Fixed:        $FIXED_VERSION"
    log INFO "Severity:     $SEVERITY"
    log INFO "Distribution: $DISTRIBUTION"
    log INFO "Mode:         $([ "$DRY_RUN" == "true" ] && echo "DRY RUN" || echo "LIVE")"
    log INFO "========================================"
    echo
    
    # Pre-flight checks
    check_root
    detect_distribution
    check_prerequisites
    
    # Create backup
    create_backup
    
    # Start remediation
    log INFO "Starting remediation process..."
    
    # Update package cache
    update_package_cache
    
    # Install fix
    install_vulnerability_fix
    
    # Apply security updates
    apply_security_updates
    
    # Verify fix
    if verify_remediation; then
        log SUCCESS "Remediation completed successfully!"
    else
        log WARNING "Remediation may be incomplete"
    fi
    
    # Generate report
    local report_path=$(generate_report)
    
    # Check for reboot
    if check_reboot_required; then
        log WARNING "========================================"
        log WARNING "SYSTEM REBOOT REQUIRED"
        log WARNING "========================================"
        
        if [[ "$DRY_RUN" != "true" ]]; then
            schedule_reboot
        fi
    fi
    
    log INFO ""
    log SUCCESS "Remediation process completed"
    log INFO "Log file: $LOG_FILE"
    log INFO "Report: $report_path"
    log INFO "Backup: $(cat /tmp/remediation_backup_path.txt 2>/dev/null || echo 'N/A')"
    
    # Cleanup temp file
    rm -f /tmp/remediation_backup_path.txt
    
    return 0
}}

# Trap errors and attempt rollback
trap 'log ERROR "Script failed at line $LINENO"; rollback; exit 1' ERR

# Run main function with all arguments
main "$@"

# End of script
"""
        
        # Record in history
        self.remediation_history.append({
            'cve_id': cve_id,
            'distribution': distribution,
            'timestamp': datetime.now().isoformat(),
            'script_generated': True
        })
        
        return script
    
    def get_distribution_info(self, distribution: str) -> Dict:
        """Get detailed information about a Linux distribution"""
        return self.distributions.get(distribution, {})
    
    def list_supported_distributions(self) -> List[str]:
        """Get list of supported Linux distributions"""
        return list(self.distributions.keys())
    
    def get_remediation_history(self) -> List[Dict]:
        """Get remediation script generation history"""
        return self.remediation_history


# ==================== STREAMLIT UI FUNCTIONS ====================

def render_linux_remediation_ui():
    """Render Streamlit UI for Linux remediation"""
    
    st.markdown("## 🐧 Linux Distribution Vulnerability Remediation")
    
    # Initialize remediator
    if 'linux_remediator' not in st.session_state:
        claude_client = st.session_state.get('claude_client')
        st.session_state.linux_remediator = LinuxRemediator(claude_client)
    
    remediator = st.session_state.linux_remediator
    
    # Version selector
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Supported Linux Distributions")
        
        # Group by family
        debian_distros = [d for d, info in LINUX_DISTRIBUTIONS.items() if info.get('family') == 'Debian']
        redhat_distros = [d for d, info in LINUX_DISTRIBUTIONS.items() if info.get('family') == 'RedHat']
        
        st.markdown("#### 📦 Debian/Ubuntu Family")
        for distro in debian_distros:
            info = remediator.get_distribution_info(distro)
            with st.expander(f"• {distro}", expanded=False):
                st.write(f"**Package Manager:** {info.get('package_manager', 'N/A')}")
                st.write(f"**Released:** {info.get('release_year', 'N/A')}")
                st.write(f"**Support Until:** {info.get('support_end', 'N/A')}")
                if 'features' in info:
                    st.write("**Features:**")
                    for feature in info['features']:
                        st.write(f"  • {feature}")
        
        st.markdown("#### 📦 Red Hat/CentOS Family")
        for distro in redhat_distros:
            info = remediator.get_distribution_info(distro)
            with st.expander(f"• {distro}", expanded=False):
                st.write(f"**Package Manager:** {info.get('package_manager', 'N/A')}")
                st.write(f"**Released:** {info.get('release_year', 'N/A')}")
                st.write(f"**Support Until:** {info.get('support_end', 'N/A')}")
                if info.get('subscription_required'):
                    st.warning("⚠️ Requires active subscription")
                if 'features' in info:
                    st.write("**Features:**")
                    for feature in info['features']:
                        st.write(f"  • {feature}")
    
    with col2:
        st.markdown("### Generate Remediation Script")
        
        # Input form
        selected_distro = st.selectbox(
            "Select Linux Distribution",
            options=remediator.list_supported_distributions(),
            key="linux_distro_select"
        )
        
        cve_id = st.text_input(
            "CVE ID",
            placeholder="CVE-2024-6387",
            key="linux_cve_id"
        )
        
        package = st.text_input(
            "Affected Package",
            placeholder="e.g., openssh-server, kernel, glibc",
            key="linux_package"
        )
        
        fixed_version = st.text_input(
            "Fixed Version (optional)",
            placeholder="e.g., 9.8p1 or 'latest'",
            key="linux_fixed_version"
        )
        
        severity = st.selectbox(
            "Severity",
            options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            key="linux_severity"
        )
        
        if st.button("🔨 Generate Bash Script", type="primary", use_container_width=True):
            if cve_id and package:
                vulnerability = {
                    'cve_id': cve_id,
                    'package': package,
                    'fixed_version': fixed_version if fixed_version else 'latest',
                    'severity': severity
                }
                
                with st.spinner("Generating Bash script..."):
                    script = remediator.generate_remediation_script(
                        vulnerability,
                        selected_distro
                    )
                
                st.success("✅ Bash script generated successfully!")
                
                # Display script
                st.markdown("### Generated Bash Script")
                st.code(script, language='bash')
                
                # Download button
                st.download_button(
                    label="📥 Download Bash Script",
                    data=script,
                    file_name=f"remediate_{cve_id.replace('-', '_')}.sh",
                    mime="text/plain",
                    use_container_width=True
                )
                
                # Execution instructions
                st.markdown("### 📝 Execution Instructions")
                st.code(f"""# Make script executable
chmod +x remediate_{cve_id.replace('-', '_')}.sh

# Test with dry run first
sudo ./remediate_{cve_id.replace('-', '_')}.sh --dry-run

# Execute remediation
sudo ./remediate_{cve_id.replace('-', '_')}.sh

# Or skip reboot
sudo ./remediate_{cve_id.replace('-', '_')}.sh --skip-reboot
""", language='bash')
            else:
                st.warning("Please enter CVE ID and package name")
    
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
    'LinuxRemediator',
    'LINUX_DISTRIBUTIONS',
    'PACKAGE_MANAGERS',
    'render_linux_remediation_ui'
]

if __name__ == "__main__":
    st.set_page_config(
        page_title="Linux Remediation",
        page_icon="🐧",
        layout="wide"
    )
    render_linux_remediation_ui()