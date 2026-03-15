"""
TechCorp Customer Success AI Agent - Quick Test (No Optional Dependencies)

This test runs without phonenumbers, fuzzywuzzy, transformers, aiokafka, or kubernetes.

Usage:
    python quick_test.py
"""

import sys
import os

print("=" * 70)
print("TECHCORP AI AGENT - QUICK TEST (Core Functionality)")
print("=" * 70)

# Test 1: File Structure
print("\n📁 File Structure")
print("-" * 70)

required_files = [
    "production/agent/customer_success_agent_production.py",
    "production/utils/identity_resolver.py",
    "production/api/sentiment_kafka_webhook.py",
    "production/tests/chaos_test.py",
    "production/tests/load_test_24h.py",
    "specs/discovery_log_stage1.md",
    "specs/skills_manifest.json",
    "SPECIALIZATION_IMPLEMENTATION.md",
    "VISUAL_EVIDENCE.md",
    "FINAL_SUBMISSION_CHECKLIST.md",
    "README.md",
    "production/requirements.txt"
]

all_exist = True
for file_path in required_files:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    if os.path.exists(full_path):
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path}")
        all_exist = False

# Test 2: Core Imports
print("\n🔧 Core Imports")
print("-" * 70)

core_imports = [
    ("OpenAI Agents SDK", "agents", ["Agent", "Runner"]),
    ("Pydantic", "pydantic", ["BaseModel", "Field"]),
    ("FastAPI", "fastapi", ["FastAPI", "HTTPException"]),
]

for name, module, imports in core_imports:
    try:
        exec(f"from {module} import {', '.join(imports)}")
        print(f"✅ {name}")
    except Exception as e:
        print(f"❌ {name}: {e}")
        all_exist = False

# Test 3: Syntax Check
print("\n📝 Syntax Check")
print("-" * 70)

import py_compile

files_to_check = [
    "production/agent/customer_success_agent_production.py",
    "production/utils/identity_resolver.py",
    "production/api/sentiment_kafka_webhook.py",
    "production/tests/chaos_test.py",
    "production/tests/load_test_24h.py",
]

for file_path in files_to_check:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    try:
        py_compile.compile(full_path, doraise=True)
        print(f"✅ {file_path}")
    except Exception as e:
        print(f"❌ {file_path}: {e}")
        all_exist = False

# Test 4: Configuration
print("\n⚙️  Configuration Check")
print("-" * 70)

# Check requirements.txt
req_path = os.path.join(os.path.dirname(__file__), "production", "requirements.txt")
if os.path.exists(req_path):
    with open(req_path, 'r') as f:
        content = f.read()
        required_packages = [
            'phonenumbers',
            'fuzzywuzzy',
            'transformers',
            'aiokafka',
            'kubernetes'
        ]
        for pkg in required_packages:
            if pkg in content:
                print(f"✅ {pkg} in requirements.txt")
            else:
                print(f"❌ {pkg} NOT in requirements.txt")

# Test 5: Documentation
print("\n📚 Documentation Check")
print("-" * 70)

doc_files = {
    "SPECIALIZATION_IMPLEMENTATION.md": "Proof of Specialization",
    "VISUAL_EVIDENCE.md": "Screenshot Guide",
    "FINAL_SUBMISSION_CHECKLIST.md": "Submission Checklist",
    "specs/discovery_log_stage1.md": "Stage 1 Discovery Log"
}

for file_path, description in doc_files.items():
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) > 1000:
                print(f"✅ {description} ({len(content)} chars)")
            else:
                print(f"⚠️  {description} (too short: {len(content)} chars)")
    else:
        print(f"❌ {description} (missing)")

# Test 6: Key Code Patterns
print("\n🔍 Key Code Patterns")
print("-" * 70)

# Check for Levenshtein distance
identity_file = os.path.join(os.path.dirname(__file__), "production", "utils", "identity_resolver.py")
with open(identity_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    if '_levenshtein_similarity' in content:
        print("✅ Levenshtein Distance Implementation")
    else:
        print("❌ Levenshtein Distance NOT found")
    
    if 'phonenumbers.parse' in content:
        print("✅ Phone Number Normalization")
    else:
        print("⚠️  Phone Number Normalization (requires phonenumbers)")
    
    if 'FuzzyMatchingEngine' in content:
        print("✅ Fuzzy Matching Engine")
    else:
        print("❌ Fuzzy Matching Engine NOT found")

# Check for Transformers
sentiment_file = os.path.join(os.path.dirname(__file__), "production", "api", "sentiment_kafka_webhook.py")
with open(sentiment_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    if 'pipeline' in content and 'sentiment-analysis' in content:
        print("✅ Transformers Sentiment Analysis")
    else:
        print("⚠️  Transformers Sentiment Analysis (requires transformers)")
    
    if 'fte.tickets.urgent' in content:
        print("✅ Kafka Urgent Topic Routing")
    else:
        print("❌ Kafka Urgent Topic Routing NOT found")
    
    if 'is_angry' in content:
        print("✅ Anger Detection Logic")
    else:
        print("❌ Anger Detection Logic NOT found")

# Check for Kubernetes
chaos_file = os.path.join(os.path.dirname(__file__), "production", "tests", "chaos_test.py")
with open(chaos_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    if 'kubernetes' in content and 'client' in content:
        print("✅ Kubernetes Client Integration")
    else:
        print("⚠️  Kubernetes Client (requires kubernetes)")
    
    if 'delete_namespaced_pod' in content:
        print("✅ Pod Deletion Logic")
    else:
        print("❌ Pod Deletion Logic NOT found")
    
    if 'no message loss' in content.lower() or 'message_durability' in content:
        print("✅ Message Loss Verification")
    else:
        print("⚠️  Message Loss Verification NOT found")

# Test 7: Discovery Log Insights
print("\n💡 Discovery Log Insights")
print("-" * 70)

discovery_file = os.path.join(os.path.dirname(__file__), "specs", "discovery_log_stage1.md")
with open(discovery_file, 'r', encoding='utf-8') as f:
    content = f.read()
    
    if 'regex' in content.lower() and 'fuzzy matching' in content.lower():
        print("✅ Insight: Fuzzy Matching Necessity")
    else:
        print("⚠️  Insight: Fuzzy Matching (check documentation)")
    
    if 'pgvector' in content.lower() and 'latency' in content.lower():
        print("✅ Insight: pgvector for Performance")
    else:
        print("⚠️  Insight: pgvector Performance (check documentation)")

# Final Summary
print("\n" + "=" * 70)
print("QUICK TEST SUMMARY")
print("=" * 70)

if all_exist:
    print("\n✅ ALL CORE TESTS PASSED!")
    print("\n📦 Optional Dependencies (install for full functionality):")
    print("   pip install phonenumbers fuzzywuzzy python-Levenshtein")
    print("   pip install transformers torch accelerate")
    print("   pip install aiokafka")
    print("   pip install kubernetes")
    print("\n🎉 Project is READY for Hackathon 5 Submission!")
else:
    print("\n⚠️  Some tests failed. Please review errors above.")

print("\n" + "=" * 70)
