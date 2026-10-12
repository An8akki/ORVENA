"""
Quick configuration verification script.
Checks that API keys are configured correctly without importing heavy dependencies.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

print("=" * 70)
print("🔍 ORVENA Multi-Provider Configuration Check")
print("=" * 70)
print()

# Check each provider
providers = []

# Gemini Key 1
gemini_key_1 = os.getenv("LLM_API_KEY")
if gemini_key_1 and len(gemini_key_1) > 10:
    print("✅ Gemini Key 1: Configured")
    print(f"   Model: {os.getenv('LLM_MODEL', 'Not set')}")
    print(f"   Key: {gemini_key_1[:15]}...{gemini_key_1[-10:]}")
    providers.append("Gemini (Key 1)")
else:
    print("❌ Gemini Key 1: Not configured")

print()

# Gemini Key 2
gemini_key_2 = os.getenv("GEMINI_API_KEY_2")
if gemini_key_2 and len(gemini_key_2) > 10:
    print("✅ Gemini Key 2: Configured")
    print(f"   Key: {gemini_key_2[:15]}...{gemini_key_2[-10:]}")
    providers.append("Gemini (Key 2)")
else:
    print("⚪ Gemini Key 2: Not configured (optional)")

print()

# NVIDIA NIM
nvidia_key = os.getenv("NVIDIA_API_KEY")
if nvidia_key and len(nvidia_key) > 10:
    print("✅ NVIDIA NIM: Configured")
    print(f"   Model: {os.getenv('NVIDIA_MODEL', 'Not set')}")
    print(f"   Key: {nvidia_key[:15]}...{nvidia_key[-10:]}")
    providers.append("NVIDIA NIM")
else:
    print("⚪ NVIDIA NIM: Not configured (optional)")

print()

# OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key and len(openai_key) > 10:
    print("✅ OpenAI: Configured")
    print(f"   Model: {os.getenv('OPENAI_MODEL', 'Not set')}")
    print(f"   Key: {openai_key[:10]}...{openai_key[-8:]}")
    providers.append("OpenAI")
else:
    print("⚪ OpenAI: Not configured (optional)")

print()
print("=" * 70)

if len(providers) == 0:
    print("❌ ERROR: No API keys configured!")
    print()
    print("Please configure at least one API key in backend/.env")
    print()
    print("See API_KEYS_SETUP_GUIDE.md for instructions")
elif len(providers) == 1:
    print("⚠️  WARNING: Only one provider configured")
    print()
    print(f"Current provider: {providers[0]}")
    print()
    print("Recommendation: Add at least one more provider for fallback")
    print("See API_KEYS_SETUP_GUIDE.md for instructions")
else:
    print("✅ SUCCESS: Multi-provider fallback configured!")
    print()
    print("Provider chain:")
    for i, provider in enumerate(providers, 1):
        arrow = " → " if i < len(providers) else ""
        print(f"  {i}. {provider}{arrow}", end="")
    print()
    print()
    print("🎉 Your system will automatically fall back when one provider fails")

print("=" * 70)
print()
print("Next steps:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Start backend: uvicorn app.main:app --reload")
print("  3. Test in UI: http://localhost:3000/career/discovery")
print()
