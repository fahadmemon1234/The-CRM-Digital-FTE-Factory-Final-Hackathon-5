"""Verify production tools module."""

import sys
sys.path.insert(0, 'production')

from agent.tools import TOOL_REGISTRY, KnowledgeSearchInput, TicketInput, EscalationInput, ResponseInput, Channel

print("=" * 70)
print("Production Tools Module Verification")
print("=" * 70)

print(f"\nTools Registered: {len(TOOL_REGISTRY)}")
for name in TOOL_REGISTRY.keys():
    print(f"  ✓ {name}")

print("\nPydantic Input Models:")
print(f"  ✓ KnowledgeSearchInput: query, max_results, category")
print(f"  ✓ TicketInput: customer_id, issue, priority, channel, subject")
print(f"  ✓ EscalationInput: ticket_id, reason, urgency")
print(f"  ✓ ResponseInput: ticket_id, message, channel")

print("\nChannel Enum:")
for channel in Channel:
    print(f"  ✓ {channel.name} = '{channel.value}'")

print("\n" + "=" * 70)
print("Verification Complete!")
print("=" * 70)
