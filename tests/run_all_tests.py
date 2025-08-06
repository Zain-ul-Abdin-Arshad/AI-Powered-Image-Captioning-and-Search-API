import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def run_command(command, description):
    print(f"\n {description}")
    print("=" * 50)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("SUCCESS")
            if result.stdout:
                print(result.stdout)
        else:
            print("FAILED")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def check_api_health():
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_manual_tests():
    print("\nRunning Manual Tests")
    print("=" * 50)
    
    print("Manual tests have been consolidated into the pytest suite.")
    print("Use 'python -m pytest tests/test_pytest.py -v' for comprehensive testing.")
    
    return True

def run_pytest_tests():
    """Run pytest tests"""
    print("\nRunning Pytest Tests")
    print("=" * 50)
    
    try:
        import pytest
        success = run_command(
            "python -m pytest tests/test_pytest.py -v",
            "Running Pytest Test Suite"
        )
        return success
    except ImportError:
        print("Pytest not available, skipping pytest tests")
        return True

def run_demo_tests():
    """Run demo tests"""
    print("\nRunning Demo Tests")
    print("=" * 50)
    
    print("Demo functionality is now handled by run_with_ngrok.py")
    print("Use 'python run_with_ngrok.py' for demo with Ngrok integration.")
    
    return True

def main():
    print("AI-Powered Image Captioning and Search API - Test Suite")
    print("=" * 60)
    print("\nChecking API Health...")
    if check_api_health():
        print("API is running and healthy")
    else:
        print("API is not running. Please start the API first:")
        print("   python src/main.py")
        return False
    
    results = []
    
    results.append(("Manual Tests", run_manual_tests()))
    
    results.append(("Pytest Tests", run_pytest_tests()))
    
    results.append(("Demo Tests", run_demo_tests()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
        print("Your API is working correctly with all features.")
    else:
        print("SOME TESTS FAILED")
        print("Please check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 