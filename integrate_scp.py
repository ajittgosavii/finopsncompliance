#!/usr/bin/env python3
"""
Automated SCP Policy Engine Integration Script
Automatically integrates render_scp_policy_engine() into your streamlit_app.py

Usage:
    python integrate_scp.py

This script will:
1. Backup your original streamlit_app.py
2. Replace the SCP tab content with render_scp_policy_engine()
3. Verify the changes
"""

import os
import shutil
from datetime import datetime

def integrate_scp_engine():
    """Integrate SCP Policy Engine into streamlit_app.py"""
    
    filename = "streamlit_app.py"
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"❌ Error: {filename} not found in current directory")
        print(f"   Current directory: {os.getcwd()}")
        print(f"\n   Please run this script from the directory containing {filename}")
        return False
    
    # Create backup
    backup_name = f"streamlit_app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy2(filename, backup_name)
    print(f"✅ Backup created: {backup_name}")
    
    # Read the file
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Read {len(lines)} lines from {filename}")
    
    # Find the SCP tab section
    scp_start = None
    scp_end = None
    
    for i, line in enumerate(lines):
        # Find start of SCP tab (around line 3577-3578)
        if 'with guardrail_tabs[0]:' in line and scp_start is None:
            scp_start = i
            print(f"✅ Found SCP tab start at line {i+1}")
        
        # Find end of SCP tab (before OPA tab, around line 3728)
        if scp_start is not None and scp_end is None:
            if 'with guardrail_tabs[1]:' in line or '# OPA Tab' in line:
                scp_end = i
                print(f"✅ Found SCP tab end at line {i+1}")
                break
    
    if scp_start is None:
        print("❌ Error: Could not find 'with guardrail_tabs[0]:' in the file")
        print("   The file structure might be different than expected")
        return False
    
    if scp_end is None:
        print("❌ Error: Could not find end of SCP tab section")
        return False
    
    # Prepare the replacement
    indent = '    '  # 4 spaces
    replacement = [
        f"{indent}# SCP Tab - Enhanced Policy Engine\n",
        f"{indent}with guardrail_tabs[0]:\n",
        f"{indent}    render_scp_policy_engine()\n",
        "\n"
    ]
    
    # Build new file content
    new_lines = lines[:scp_start] + replacement + lines[scp_end:]
    
    # Write the modified file
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ Successfully integrated SCP Policy Engine!")
    print(f"   Replaced {scp_end - scp_start} lines with {len(replacement)} lines")
    print(f"   Old lines: {scp_start+1} to {scp_end}")
    print(f"   New code: {scp_start+1} to {scp_start+len(replacement)}")
    
    # Verify the change
    with open(filename, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    if 'render_scp_policy_engine()' in new_content:
        print(f"\n✅ Verification passed: render_scp_policy_engine() found in file")
    else:
        print(f"\n⚠️  Warning: Could not verify the change")
    
    print(f"\n📝 Summary:")
    print(f"   - Original file backed up to: {backup_name}")
    print(f"   - Modified file: {filename}")
    print(f"   - Lines removed: {scp_end - scp_start}")
    print(f"   - Lines added: {len(replacement)}")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Make sure scp_policy_engine.py is in the same directory")
    print(f"   2. Run: streamlit run {filename}")
    print(f"   3. Navigate to: Tech Guardrails → Service Control Policies (SCP)")
    print(f"   4. You should see the full SCP Policy Engine!")
    
    print(f"\n💡 To revert changes:")
    print(f"   cp {backup_name} {filename}")
    
    return True

def check_prerequisites():
    """Check if required files exist"""
    
    print("🔍 Checking prerequisites...")
    
    files_to_check = {
        'streamlit_app.py': 'Main application file',
        'scp_policy_engine.py': 'SCP Policy Engine module',
        'account_lifecycle_enhanced.py': 'Account Lifecycle module'
    }
    
    all_good = True
    
    for filename, description in files_to_check.items():
        if os.path.exists(filename):
            print(f"   ✅ {filename} ({description})")
        else:
            print(f"   ❌ {filename} NOT FOUND ({description})")
            if filename != 'streamlit_app.py':
                print(f"      → Copy {filename} to this directory")
            all_good = False
    
    return all_good

def main():
    """Main function"""
    
    print("=" * 70)
    print("🛡️  SCP Policy Engine Integration Script")
    print("=" * 70)
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please ensure all files are in place.")
        return
    
    print("\n" + "=" * 70)
    print("📋 What this script will do:")
    print("=" * 70)
    print("1. Create a backup of your streamlit_app.py")
    print("2. Find the SCP tab section (around line 3578-3727)")
    print("3. Replace ~150 lines of old SCP code with 3 lines:")
    print("   - with guardrail_tabs[0]:")
    print("   -     render_scp_policy_engine()")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Integration cancelled")
        return
    
    print("\n" + "=" * 70)
    print("🔧 Starting integration...")
    print("=" * 70)
    print()
    
    if integrate_scp_engine():
        print("\n" + "=" * 70)
        print("✅ INTEGRATION COMPLETE!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ INTEGRATION FAILED")
        print("=" * 70)
        print("\nPlease check the error messages above and try manual integration")
        print("See EXACT_INTEGRATION_STEPS.md for manual instructions")

if __name__ == "__main__":
    main()
