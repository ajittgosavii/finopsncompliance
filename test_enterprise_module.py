#!/usr/bin/env python3
"""
Quick test script to verify enterprise_module.py works correctly
Run this before integrating with your main app
"""

import sys

print("=" * 60)
print("Enterprise Module Test")
print("=" * 60)

# Test 1: Import
print("\n1. Testing import...")
try:
    from enterprise_module import (
        EnterpriseAuth,
        ControlTowerManager,
        RealTimeCostMonitor,
        init_enterprise_session,
        render_enterprise_login,
        render_enterprise_header,
        render_enterprise_sidebar,
        render_cfo_dashboard,
        render_control_tower,
        render_realtime_costs,
        check_enterprise_routing
    )
    print("   ✅ All imports successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Authentication
print("\n2. Testing authentication...")
user = EnterpriseAuth.authenticate("cfo@example.com", "demo123")
if user and user['name'] == 'Chief Financial Officer':
    print(f"   ✅ Authentication works: {user['name']}")
else:
    print("   ❌ Authentication failed")
    sys.exit(1)

# Test 3: Permissions
print("\n3. Testing permissions...")
if EnterpriseAuth.check_permission(user, 'dashboard:cfo:tenant'):
    print("   ✅ Permission check works: CFO can access CFO dashboard")
else:
    print("   ❌ Permission check failed")
    sys.exit(1)

if not EnterpriseAuth.check_permission(user, 'controltower:write:tenant'):
    print("   ✅ Permission check works: CFO cannot write to Control Tower")
else:
    print("   ❌ Permission check failed (should deny)")
    sys.exit(1)

# Test 4: Control Tower Manager
print("\n4. Testing Control Tower Manager...")
ct = ControlTowerManager()
lz = ct.get_landing_zone_status()
if lz['accounts_managed'] == 127:
    print(f"   ✅ Control Tower works: {lz['accounts_managed']} accounts")
else:
    print("   ❌ Control Tower failed")
    sys.exit(1)

# Test 5: Cost Monitor
print("\n5. Testing Real-Time Cost Monitor...")
monitor = RealTimeCostMonitor()
cost = monitor.get_current_hourly_cost()
if cost['total'] == 118.64:
    print(f"   ✅ Cost Monitor works: ${cost['total']}/hr")
else:
    print("   ❌ Cost Monitor failed")
    sys.exit(1)

# Test 6: Anomaly Detection
print("\n6. Testing anomaly detection...")
anomalies = monitor.detect_anomalies()
if len(anomalies) > 0 and anomalies[0]['service'] == 'EC2':
    print(f"   ✅ Anomaly detection works: {len(anomalies)} anomalies found")
else:
    print("   ❌ Anomaly detection failed")
    sys.exit(1)

# Test 7: All Demo Users
print("\n7. Testing all demo users...")
test_users = [
    ('admin@example.com', 'Global Administrator'),
    ('cfo@example.com', 'Chief Financial Officer'),
    ('ciso@example.com', 'Chief Information Security Officer'),
    ('cto@example.com', 'Chief Technology Officer'),
]

for email, expected_name in test_users:
    user = EnterpriseAuth.authenticate(email, "demo123")
    if user and user['name'] == expected_name:
        print(f"   ✅ {email}: {user['name']}")
    else:
        print(f"   ❌ {email}: Failed")
        sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nEnterprise module is working correctly!")
print("\nNext steps:")
print("1. Place enterprise_module.py in same directory as streamlit_app.py")
print("2. Follow SIMPLE_3LINE_INTEGRATION.md")
print("3. Run: streamlit run streamlit_app.py")
print("4. Login with: cfo@example.com / demo123")
print("\n" + "=" * 60)
