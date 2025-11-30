"""
Test script to verify the SEO Analyzer project setup.
Run this to check if all components are working correctly.
"""

import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    errors = []
    
    # Test config
    try:
        import config
        print("✅ config.py imported")
    except Exception as e:
        errors.append(f"❌ config.py: {e}")
    
    # Test database
    try:
        from database import DatabaseClient, get_db_client
        db = get_db_client()
        print("✅ database.py imported and initialized")
    except Exception as e:
        errors.append(f"❌ database.py: {e}")
    
    # Test tools (without ADK dependency for basic test)
    try:
        # Import the utility functions
        from tools import normalize_url, fetch_page, get_base_url
        print("✅ tools.py utilities imported")
    except Exception as e:
        errors.append(f"❌ tools.py: {e}")
    
    # Test observability
    try:
        from observability import get_logger, tracer, metrics
        logger = get_logger("test")
        print("✅ observability.py imported")
    except Exception as e:
        errors.append(f"❌ observability.py: {e}")
    
    return errors


def test_tools_basic():
    """Test basic tool functionality without ADK."""
    print("\nTesting basic tool functions...")
    
    # Import tool functions directly (they don't need ADK to work)
    import requests
    from bs4 import BeautifulSoup
    import ssl
    import socket
    from urllib.parse import urlparse
    
    def normalize_url(url):
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    url = "https://example.com"
    url = normalize_url(url)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ HTTP request successful - Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"✅ HTML parsing successful - Title: {title.text[:50]}")
        
    except Exception as e:
        print(f"❌ HTTP/Parsing error: {e}")


def test_database():
    """Test database operations."""
    print("\nTesting database operations...")
    
    try:
        from database import get_db_client
        
        db = get_db_client()
        
        # Create a test request
        result = db.create_analysis_request("https://test.example.com")
        print(f"✅ Created request: {result['unique_identifier']}")
        
        # Get the request
        fetched = db.get_request_by_identifier(result['unique_identifier'])
        if fetched:
            print(f"✅ Retrieved request: {fetched['website_url']}")
        
        # Update status
        db.update_request_status(result['unique_identifier'], "testing")
        print("✅ Updated request status")
        
        # Log an action
        db.log_agent_action(
            request_id=result['unique_identifier'],
            agent_name="test_agent",
            action="test_action",
            details={"test": True},
            duration_ms=100
        )
        print("✅ Logged agent action")
        
        # Get logs
        logs = db.get_analysis_logs(result['unique_identifier'])
        print(f"✅ Retrieved {len(logs)} log entries")
        
    except Exception as e:
        print(f"❌ Database error: {e}")


def test_adk_import():
    """Test ADK imports."""
    print("\nTesting Google ADK imports...")
    
    try:
        from google.adk.agents import Agent
        print("✅ google.adk.agents.Agent imported")
    except ImportError as e:
        print(f"⚠️ ADK Agent not available: {e}")
        print("   Make sure google-adk is installed: pip install google-adk")
        return False
    
    try:
        from google.adk.tools import FunctionTool
        print("✅ google.adk.tools.FunctionTool imported")
    except ImportError as e:
        print(f"⚠️ ADK FunctionTool not available: {e}")
        return False
    
    try:
        from google.adk.runners import Runner
        print("✅ google.adk.runners.Runner imported")
    except ImportError as e:
        print(f"⚠️ ADK Runner not available: {e}")
        return False
    
    try:
        from google.adk.sessions import InMemorySessionService
        print("✅ google.adk.sessions.InMemorySessionService imported")
    except ImportError as e:
        print(f"⚠️ ADK InMemorySessionService not available: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("SEO Analyzer - Project Verification")
    print("=" * 60)
    
    # Test basic imports
    errors = test_imports()
    
    # Test basic tools
    test_tools_basic()
    
    # Test database
    test_database()
    
    # Test ADK
    adk_ok = test_adk_import()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if errors:
        print("\nImport errors:")
        for err in errors:
            print(f"  {err}")
    else:
        print("\n✅ All basic imports successful")
    
    if adk_ok:
        print("✅ Google ADK is properly installed")
        print("\nYou can now run: python main.py analyze https://example.com")
    else:
        print("\n⚠️ Google ADK not fully available")
        print("Install it with: pip install google-adk")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
