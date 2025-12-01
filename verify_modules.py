#!/usr/bin/env python3
"""
Verify Remediation Module Files
Tests that the modules can be imported without errors
"""

import sys

print("=" * 70)
print("REMEDIATION MODULE VERIFICATION")
print("=" * 70)

errors = []

# Test 1: Windows Module
print("\n1. Testing Windows Server Remediation Module...")
try:
    from windows_server_remediation_MERGED_ENHANCED import WindowsServerRemediator
    print("   ✅ Windows module imported successfully")
    print(f"   ✅ WindowsServerRemediator class available")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")
    errors.append("Windows module import failed")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    errors.append(f"Windows module error: {e}")

# Test 2: Linux Module
print("\n2. Testing Linux Distribution Remediation Module...")
try:
    from linux_distribution_remediation_MERGED_ENHANCED import LinuxEC2Connector, LinuxDistributionRemediator
    print("   ✅ Linux module imported successfully")
    print(f"   ✅ LinuxEC2Connector class available")
    print(f"   ✅ LinuxDistributionRemediator class available")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")
    errors.append("Linux module import failed")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    errors.append(f"Linux module error: {e}")

# Test 3: EKS Module
print("\n3. Testing EKS Remediation Module...")
try:
    from eks_remediation_complete import EKSConnector, EKSRemediationEngine
    print("   ✅ EKS module imported successfully")
    print(f"   ✅ EKSConnector class available")
    print(f"   ✅ EKSRemediationEngine class available")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")
    errors.append("EKS module import failed")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    errors.append(f"EKS module error: {e}")

# Test 4: Check for Streamlit imports (should NOT be present)
print("\n4. Checking for unnecessary Streamlit imports...")
import_found = False

for module_name in ['windows_server_remediation_MERGED_ENHANCED', 
                    'linux_distribution_remediation_MERGED_ENHANCED',
                    'eks_remediation_complete']:
    try:
        with open(f"{module_name}.py", 'r') as f:
            content = f.read()
            if 'import streamlit' in content:
                print(f"   ⚠️  WARNING: {module_name}.py contains 'import streamlit'")
                import_found = True
    except FileNotFoundError:
        print(f"   ⚠️  WARNING: {module_name}.py not found in current directory")

if not import_found:
    print("   ✅ No unnecessary Streamlit imports found")
else:
    errors.append("Streamlit imports found in backend modules")

# Summary
print("\n" + "=" * 70)
if errors:
    print("❌ VERIFICATION FAILED")
    print("\nErrors found:")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    print("\n⚠️  DO NOT upload these files to Streamlit Cloud")
    print("⚠️  Fix the errors above first")
    sys.exit(1)
else:
    print("✅ ALL TESTS PASSED")
    print("\n✅ Modules imported successfully")
    print("✅ No Streamlit imports in backend modules")
    print("✅ Files are ready for deployment")
    print("\nYou can now upload these files to GitHub!")
    sys.exit(0)

print("=" * 70)
