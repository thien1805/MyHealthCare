#!/usr/bin/env python3
"""Quick test for AI suggest department (no Django needed for basic check)"""
import os
from openai import OpenAI

# Get API key from environment
api_key = os.environ.get('OPENROUTER_API_KEY', '')

print("="*60)
print("  Quick AI API Test")
print("="*60)

if not api_key:
    print("❌ OPENROUTER_API_KEY not found in environment")
    print("   Set it with: export OPENROUTER_API_KEY='your-key-here'")
    exit(1)

print(f"✅ API Key found: {api_key[:20]}...")

# Initialize client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://myhealthcare-api.com",
        "X-Title": "MyHealthCare",
    }
)

print("\n🧪 Testing AI suggestion...")
print("Symptoms: Chest pain and difficulty breathing")

try:
    response = client.chat.completions.create(
        model="tngtech/deepseek-r1t2-chimera:free",
        messages=[
            {
                "role": "system",
                "content": """You are a medical AI. Suggest a department based on symptoms.
                Available departments: Cardiology, Internal Medicine, Emergency, Neurology.
                Return ONLY JSON: {"primary_department": "name", "reason": "explanation", "urgency": "low|medium|high"}"""
            },
            {
                "role": "user",
                "content": "Patient has chest pain and difficulty breathing"
            }
        ]
    )
    
    result = response.choices[0].message.content
    print("\n✅ AI Response:")
    print(result)
    print("\n🎉 API is working correctly!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    exit(1)
