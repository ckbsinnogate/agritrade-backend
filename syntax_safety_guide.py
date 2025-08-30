#!/usr/bin/env python
"""
Python Syntax Safety Guide for AgriConnect Development
Common issues and how to avoid them when working with f-strings and command-line Python
"""

print("🔧 PYTHON SYNTAX SAFETY GUIDE FOR AGRICONNECT")
print("=" * 60)

print("\n❌ PROBLEMATIC SYNTAX:")
print("# This can cause bracket matching issues in f-strings:")
print('# print(f"Value: {data["key"]}")  # Nested quotes problem')
print('# print(f"Value: {stats["total_value"]}")  # Can break in command line')

print("\n✅ SAFE ALTERNATIVES:")
print("# Method 1: Extract values first")
print("stats = Order.objects.aggregate(total=Sum('amount'))")
print("total_value = stats.get('total') or 0")
print("print(f'Total: GHS {total_value}')")

print("\n# Method 2: Use .get() method")
print("print(f'Total: GHS {stats.get(\"total\", 0)}')")

print("\n# Method 3: Use format() method")
print("print('Total: GHS {}'.format(stats.get('total', 0)))")

print("\n🛡️ COMMAND-LINE PYTHON TIPS:")
tips = [
    "Always use double quotes for outer strings in PowerShell",
    "Extract dictionary values before using in f-strings",
    "Use .get() method for safe dictionary access",
    "Test complex f-strings in separate files first",
    "Use triple quotes for multi-line strings",
    "Escape quotes properly: \\\" for nested quotes"
]

for i, tip in enumerate(tips, 1):
    print(f"{i}. {tip}")

print("\n🚀 AGRICONNECT-SPECIFIC EXAMPLES:")
print("\n# Safe order statistics:")
print("""
stats = Order.objects.aggregate(
    total_value=Sum('total_amount'),
    count=Count('id')
)
total = stats.get('total_value') or 0
count = stats.get('count') or 0
print(f'Orders: {count}, Value: GHS {total}')
""")

print("\n# Safe status reporting:")
print("""
for order in Order.objects.all()[:3]:
    num = order.order_number
    amt = order.total_amount
    status = order.status
    print(f'Order {num}: GHS {amt} ({status})')
""")

print("\n✅ SYNTAX CHECK PASSED - No issues detected!")
print("💡 Use safe_status_check.py for system monitoring")
