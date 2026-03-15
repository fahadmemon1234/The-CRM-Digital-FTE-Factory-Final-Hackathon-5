"""Verify database schema and queries module."""

import sys
sys.path.insert(0, 'production')

from database import queries

print("=" * 70)
print("Database Module Verification")
print("=" * 70)

# List all exported functions
functions = [f for f in dir(queries) if not f.startswith('_')]
print(f"\nExported Functions: {len(functions)}")

# Categorize functions
categories = {
    "Connection": ["get_db_pool", "close_db_pool", "init_db"],
    "Customer": ["find_customer_by_email", "find_customer_by_phone", 
                 "find_or_create_customer", "create_customer", 
                 "add_customer_identifier"],
    "Conversation": ["create_conversation", "get_conversation_history",
                     "get_customer_full_history", "update_conversation_status"],
    "Message": ["store_message", "update_delivery_status"],
    "Ticket": ["create_ticket", "update_ticket_status", "get_ticket"],
    "Metrics": ["get_channel_metrics_24h", "record_metric"],
    "Knowledge": ["search_knowledge_base"],
    "Config": ["get_channel_config"]
}

for category, funcs in categories.items():
    print(f"\n{category}:")
    for func in funcs:
        if func in functions:
            print(f"  ✓ {func}")
        else:
            print(f"  ✗ {func} (MISSING)")

print("\n" + "=" * 70)
print("Verification Complete!")
print("=" * 70)
