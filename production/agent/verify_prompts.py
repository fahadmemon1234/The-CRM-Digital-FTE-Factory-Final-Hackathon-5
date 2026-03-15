"""Verify the prompts module."""

import sys
sys.path.insert(0, 'production')

from agent.prompts import CUSTOMER_SUCCESS_SYSTEM_PROMPT

print("=" * 70)
print("Production Prompts Module Verification")
print("=" * 70)

print(f"\nPrompt loaded successfully: YES")
print(f"Prompt length: {len(CUSTOMER_SUCCESS_SYSTEM_PROMPT):,} chars")

# Check required sections
sections = {
    "Agent purpose": "purpose",
    "Channel awareness": "channel",
    "Required workflow": "workflow",
    "Hard constraints (NEVER)": "NEVER",
    "Escalation triggers": "escalat",
    "Response quality standards": "quality",
    "Context variables": "customer_id"
}

print("\nRequired Sections:")
for name, keyword in sections.items():
    found = keyword.lower() in CUSTOMER_SUCCESS_SYSTEM_PROMPT.lower()
    status = "✓" if found else "✗"
    print(f"  {status} {name}")

# Count escalation triggers
escalation_keywords = [
    "lawyer", "attorney", "lawsuit", "refund", "chargeback",
    "pricing", "discount", "human", "sentiment", "legal", "security"
]
print(f"\nEscalation Keywords Found:")
for kw in escalation_keywords:
    count = CUSTOMER_SUCCESS_SYSTEM_PROMPT.lower().count(kw)
    if count > 0:
        print(f"  - {kw}: {count} occurrences")

print("\n" + "=" * 70)
print("Verification Complete!")
print("=" * 70)
