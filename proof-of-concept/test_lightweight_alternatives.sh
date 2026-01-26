#!/bin/bash
# Quick test script to check for lightweight alternatives to Selenium
# Usage: ./test_lightweight_alternatives.sh [switch-ip]

SWITCH_IP="${1:-192.168.2.1}"
TIMEOUT=3

echo "=========================================="
echo "Testing Lightweight Alternatives"
echo "Switch IP: $SWITCH_IP"
echo "=========================================="
echo ""

# Test 1: Ping
echo "[1/5] Testing network connectivity..."
if ping -c 2 -W 2 "$SWITCH_IP" > /dev/null 2>&1; then
    echo "  ✓ Switch is reachable at $SWITCH_IP"
else
    echo "  ✗ Switch is NOT reachable (no ping response)"
    echo ""
    echo "Cannot proceed without network connectivity."
    echo "Please check:"
    echo "  - Switch is powered on"
    echo "  - Network cable is connected"
    echo "  - You're on the same subnet (e.g., 192.168.2.x)"
    exit 1
fi
echo ""

# Test 2: SSH (port 22)
echo "[2/5] Testing SSH access (port 22)..."
if timeout $TIMEOUT ssh -o ConnectTimeout=$TIMEOUT -o StrictHostKeyChecking=no \
    admin@"$SWITCH_IP" exit 2>&1 | grep -q "password"; then
    echo "  ✓ SSH is AVAILABLE (port 22 open, login prompt detected)"
    echo "  → This is your BEST option (minimal dependencies)"
    echo "  → Next step: ssh admin@$SWITCH_IP and document CLI commands"
    SSH_AVAILABLE=true
elif timeout $TIMEOUT nc -z -w $TIMEOUT "$SWITCH_IP" 22 2>&1 | grep -q "succeeded"; then
    echo "  ⚠ SSH port is open but no login prompt detected"
    echo "  → Try manually: ssh admin@$SWITCH_IP"
    SSH_AVAILABLE=maybe
else
    echo "  ✗ SSH is NOT available (connection refused or timeout)"
    SSH_AVAILABLE=false
fi
echo ""

# Test 3: Telnet (port 23)
echo "[3/5] Testing Telnet access (port 23)..."
if timeout $TIMEOUT nc -z -w $TIMEOUT "$SWITCH_IP" 23 2>&1 | grep -q "succeeded"; then
    echo "  ✓ Telnet is AVAILABLE (port 23 open)"
    echo "  → This is a GOOD option (built-in Python telnetlib)"
    echo "  → Next step: telnet $SWITCH_IP and document CLI commands"
    TELNET_AVAILABLE=true
else
    echo "  ✗ Telnet is NOT available (connection refused or timeout)"
    TELNET_AVAILABLE=false
fi
echo ""

# Test 4: SNMP (port 161)
echo "[4/5] Testing SNMP access (port 161)..."
if command -v snmpwalk &> /dev/null; then
    # Try multiple community strings
    for community in public private admin switch; do
        if timeout $TIMEOUT snmpwalk -v2c -c "$community" -t 1 "$SWITCH_IP" system 2>&1 | grep -q "SNMPv2-MIB"; then
            echo "  ✓ SNMP is AVAILABLE (community string: $community)"
            echo "  → This is a GOOD option (~2MB dependency)"
            echo "  → Next step: Identify IP configuration OIDs"
            SNMP_AVAILABLE=true
            SNMP_COMMUNITY=$community
            break
        fi
    done

    if [ "$SNMP_AVAILABLE" != "true" ]; then
        echo "  ✗ SNMP is NOT available (tried: public, private, admin, switch)"
        SNMP_AVAILABLE=false
    fi
else
    echo "  ⚠ SNMP tools not installed (cannot test)"
    echo "  → Install with: sudo apt-get install snmp snmp-mibs-downloader"
    SNMP_AVAILABLE=unknown
fi
echo ""

# Test 5: HTTP (port 80) - just for reference
echo "[5/5] Testing HTTP web interface (port 80)..."
if curl -s -m $TIMEOUT "http://$SWITCH_IP/" > /dev/null 2>&1; then
    echo "  ✓ HTTP web interface is accessible"
    echo "  → Selenium uses this (but it's the heavy option)"
else
    echo "  ✗ HTTP web interface is NOT accessible"
fi
echo ""

# Summary
echo "=========================================="
echo "SUMMARY & RECOMMENDATIONS"
echo "=========================================="
echo ""

FOUND_LIGHTWEIGHT=false

if [ "$SSH_AVAILABLE" = "true" ]; then
    echo "✅ SSH AVAILABLE - This is your BEST option!"
    echo ""
    echo "   Next steps:"
    echo "   1. Connect: ssh admin@$SWITCH_IP"
    echo "   2. Document login prompt and welcome message"
    echo "   3. List commands: help, ?, or show ?"
    echo "   4. Find IP config commands (likely 'interface management')"
    echo "   5. Document exact syntax for IP address change"
    echo ""
    echo "   Dependencies: paramiko (~500KB) or built-in ssh client"
    echo "   Execution time: ~1-2 seconds"
    echo "   ✅ 400x smaller than Selenium!"
    echo ""
    FOUND_LIGHTWEIGHT=true
fi

if [ "$TELNET_AVAILABLE" = "true" ]; then
    echo "✅ TELNET AVAILABLE - This is a GOOD option!"
    echo ""
    echo "   Next steps:"
    echo "   1. Connect: telnet $SWITCH_IP"
    echo "   2. Document login prompt and welcome message"
    echo "   3. List commands: help, ?, or show ?"
    echo "   4. Find IP config commands (likely 'interface management')"
    echo "   5. Document exact syntax for IP address change"
    echo ""
    echo "   Dependencies: Built-in telnetlib (zero extra dependencies!)"
    echo "   Execution time: ~1-2 seconds"
    echo "   ✅ No extra dependencies needed!"
    echo ""
    FOUND_LIGHTWEIGHT=true
fi

if [ "$SNMP_AVAILABLE" = "true" ]; then
    echo "✅ SNMP AVAILABLE - This is a GOOD option!"
    echo ""
    echo "   Next steps:"
    echo "   1. Walk MIB tree: snmpwalk -v2c -c $SNMP_COMMUNITY $SWITCH_IP"
    echo "   2. Find IP-MIB: snmpwalk -v2c -c $SNMP_COMMUNITY $SWITCH_IP ip"
    echo "   3. Identify OIDs for IP address, subnet, gateway"
    echo "   4. Test SET: snmpset -v2c -c $SNMP_COMMUNITY $SWITCH_IP [OID] [value]"
    echo "   5. Verify configuration persists"
    echo ""
    echo "   Dependencies: pysnmp (~2MB)"
    echo "   Execution time: ~1-2 seconds"
    echo "   ✅ 100x smaller than Selenium!"
    echo ""
    FOUND_LIGHTWEIGHT=true
fi

if [ "$FOUND_LIGHTWEIGHT" = "false" ]; then
    echo "❌ No lightweight alternatives found"
    echo ""
    echo "   The switch does not support CLI (SSH/Telnet) or SNMP access."
    echo "   You will need to use one of these options:"
    echo ""
    echo "   Option A: Keep Selenium (current solution)"
    echo "   - ✅ Production-ready and works reliably"
    echo "   - ✅ Well-documented (see SELENIUM_USAGE.md)"
    echo "   - ⚠️  Heavy dependency (~200MB Chrome browser)"
    echo "   - 💡 Consider Docker containerization for easier deployment"
    echo ""
    echo "   Option B: Try requests-html (lighter browser)"
    echo "   - Install: pip install requests-html"
    echo "   - Size: ~50MB (4x smaller than Selenium)"
    echo "   - ⚠️  May still fail with HTTP 201 error"
    echo "   - Worth testing but not guaranteed"
    echo ""
    echo "   Option C: Check switch documentation"
    echo "   - Look for CLI reference manual"
    echo "   - Check if SSH/Telnet can be enabled in settings"
    echo "   - Search for SNMP configuration instructions"
    echo ""
fi

echo "=========================================="
echo "For detailed analysis, see:"
echo "docs/LIGHTWEIGHT_ALTERNATIVES_INVESTIGATION.md"
echo "=========================================="
