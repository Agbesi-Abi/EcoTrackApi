#!/usr/bin/env python3
"""
Quick test to verify email validation works
"""

try:
    from pydantic import BaseModel, EmailStr
    from email_validator import validate_email
    
    class TestUser(BaseModel):
        email: EmailStr
        name: str
    
    # Test valid email
    user = TestUser(email="test@example.com", name="Test User")
    print("✅ Email validation working correctly!")
    print(f"   Created user: {user.email}")
    
    # Test email validator directly
    validation = validate_email("demo@ecotrack.com")
    print(f"✅ Email validator working: {validation.email}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Run: pip install pydantic[email] email-validator")
except Exception as e:
    print(f"❌ Validation error: {e}")
