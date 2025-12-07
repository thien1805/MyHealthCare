#!/usr/bin/env python3
"""
Test script for AI API endpoints
Tests both suggest_department and health_chatbot
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhealthcare.settings')
django.setup()

from apps.services.ai_services import ai_service
import json

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_api_key_configuration():
    """Test 1: Check if API key is configured"""
    print_section("TEST 1: API Key Configuration")
    
    if ai_service.api_key:
        print("✅ API Key is configured")
        print(f"   Key prefix: {ai_service.api_key[:20]}...")
        print(f"   Base URL: {ai_service.base_url}")
        print(f"   Model: {ai_service.model}")
        return True
    else:
        print("❌ API Key NOT configured")
        print("   Environment variable OPENROUTER_API_KEY not found")
        return False

def test_suggest_department():
    """Test 2: Test department suggestion"""
    print_section("TEST 2: AI Suggest Department")
    
    if not ai_service.client:
        print("⏭️  Skipped - API client not initialized")
        return False
    
    test_cases = [
        {
            "symptoms": "I have chest pain and difficulty breathing",
            "description": "English - Cardiac symptoms"
        },
        {
            "symptoms": "Tôi bị đau đầu và chóng mặt kéo dài 3 ngày",
            "description": "Vietnamese - Neurological symptoms"
        },
        {
            "symptoms": "Đau bụng, tiêu chảy",
            "description": "Vietnamese - Gastro symptoms"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['description']} ---")
        print(f"Symptoms: {test_case['symptoms']}")
        
        try:
            result = ai_service.suggest_department(test_case['symptoms'])
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                if "raw_response" in result:
                    print(f"   Raw response: {result['raw_response'][:200]}...")
                return False
            else:
                print("✅ Success!")
                print(f"   Primary Department: {result.get('primary_department', 'N/A')}")
                print(f"   Reason: {result.get('reason', 'N/A')[:100]}...")
                print(f"   Urgency: {result.get('urgency', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    return True

def test_health_chatbot():
    """Test 3: Test health chatbot"""
    print_section("TEST 3: Health Chatbot")
    
    if not ai_service.client:
        print("⏭️  Skipped - API client not initialized")
        return False
    
    questions = [
        "What should I do if I have a fever?",
        "Cảm cúm có nguy hiểm không?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i} ---")
        print(f"Q: {question}")
        
        try:
            response = ai_service.health_chatbot(question)
            
            if response:
                print("✅ Response received!")
                print(f"A: {response[:200]}...")
            else:
                print("❌ No response from chatbot")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    return True

def test_departments_loading():
    """Test 4: Check if departments are loaded from database"""
    print_section("TEST 4: Database Departments")
    
    try:
        departments = ai_service._get_available_departments()
        
        if departments:
            print(f"✅ Found {len(departments)} active departments:")
            for dept in departments[:5]:  # Show first 5
                print(f"   - {dept}")
            if len(departments) > 5:
                print(f"   ... and {len(departments) - 5} more")
            return True
        else:
            print("⚠️  No departments found in database")
            print("   AI will still work but may suggest generic departments")
            return True
            
    except Exception as e:
        print(f"❌ Error loading departments: {str(e)}")
        return False

def main():
    print("\n" + "🏥"*30)
    print("  MyHealthCare AI Service - API Test Suite")
    print("🏥"*30)
    
    results = {}
    
    # Run all tests
    results['api_key'] = test_api_key_configuration()
    results['departments'] = test_departments_loading()
    
    # Only run AI tests if API key is configured
    if results['api_key']:
        results['suggest'] = test_suggest_department()
        results['chatbot'] = test_health_chatbot()
    else:
        print("\n⚠️  Skipping AI tests - API key not configured")
        print("   To fix: Set OPENROUTER_API_KEY environment variable")
        results['suggest'] = None
        results['chatbot'] = None
    
    # Summary
    print_section("TEST SUMMARY")
    
    total = 0
    passed = 0
    
    for test_name, result in results.items():
        if result is not None:
            total += 1
            if result:
                passed += 1
                print(f"✅ {test_name.upper()}: PASSED")
            else:
                print(f"❌ {test_name.upper()}: FAILED")
        else:
            print(f"⏭️  {test_name.upper()}: SKIPPED")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total and total > 0:
        print("\n🎉 All tests passed! AI service is working correctly.")
        return 0
    elif results['api_key']:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return 1
    else:
        print("\n⚠️  API key not configured. Please add OPENROUTER_API_KEY to environment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
