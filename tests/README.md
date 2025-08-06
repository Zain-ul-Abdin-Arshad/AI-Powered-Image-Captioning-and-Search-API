# Testing Suite

This directory contains all testing files.

## Test Files Overview

### Comprehensive Tests
- **`test_pytest.py`** - Pytest-based test suite
  - Unit tests for all API functionality
  - Database connection tests
  - ML model loading tests
  - Authentication integration tests
  - Project structure validation
  - API endpoint testing with authentication
  - Error handling and edge cases

### Test Runner
- **`run_all_tests.py`** - Comprehensive test runner
  - Runs all test suites
  - Provides detailed reporting
  - Checks API health before testing
  - Generates test summary

## Running Tests

### Quick Test (All Tests)
```bash
# Run all tests
python tests/run_all_tests.py
```

### Individual Test Files
```bash
# Pytest test suite (comprehensive)
python -m pytest tests/test_pytest.py -v

# Run all tests
python tests/run_all_tests.py
```

### Manual Testing
```bash
# Start the API first
python src/main.py

# Then run tests in another terminal
python tests/test_auth.py
```

## Test Categories

### 1. Authentication Tests
- Done JWT token generation
- Done Password validation
- Done Protected endpoint access
- Done Unauthorized access rejection
- Done Token expiry handling

### 2. API Endpoint Tests
- Done Welcome endpoint
- Done Image upload with auth
- Done Image search with auth
- Done History retrieval with auth
- Done User info endpoint
- Done Error handling

### 3. Integration Tests
- Done Database connectivity
- Done ML model loading
- Done File upload processing
- Done Image captioning
- Done Semantic search
- Done Error scenarios

### 4. Demo Tests
- Done Server startup
- Done Sample data upload
- Done Search functionality
- Done UI demonstration

## Test Requirements

### Prerequisites
- API server running on `http://localhost:8000`
- All dependencies installed (`pip install -r requirements.txt`)
- Sample images available (optional)

### Environment Setup
```bash

pip install pytest requests pillow

# Start API server
python src/main.py

# Run tests
python tests/run_all_tests.py
```

## Test Data

### Default Users (for authentication tests)
- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

### Test Images
- Automatically generated test images
- Blue square (200x200) for upload testing
- Red square (100x100) for pytest tests

## Expected Results

### Successful Test Run
```
AI-Powered Image Captioning and Search API - Test Suite
============================================================

Checking API Health...
Done API is running and healthy

Running Manual Tests
==================================================
Done SUCCESS

Running Pytest Tests
==================================================
Done SUCCESS

Running Demo Tests
==================================================
Done SUCCESS

============================================================
TEST SUMMARY
============================================================
Manual Tests: PASSED
Pytest Tests: PASSED
Demo Tests:   PASSED

============================================================
ALL TESTS PASSED!
Your API is working correctly with all features.
```

## Troubleshooting

### Common Issues

1. **API Not Running**
   ```
   API is not running. Please start the API first:
      python src/main.py
   ```

2. **Authentication Failed**
   ```
   Authentication failed - cannot test protected endpoints
   ```
   - Check if JWT dependencies are installed
   - Verify API server is running

3. **Import Errors**
   ```
   Module not found
   ```
   - Install missing dependencies
   - Check Python path

4. **Connection Errors**
   ```
   Could not connect to API
   ```
   - Ensure API server is running on port 8000
   - Check firewall settings

### Debug Mode
```bash
# Run with verbose output
python -m pytest tests/test_pytest.py -v -s

# Run specific test
python -m pytest tests/test_pytest.py::TestAuthentication::test_login_success -v
```

## Contributing

When adding new tests:

1. **Follow naming convention**: `test_*.py`
2. **Include authentication**: All protected endpoints need auth
3. **Add to test runner**: Update `run_all_tests.py`
4. **Document changes**: Update this README
5. **Test thoroughly**: Run all tests before committing

## Test Coverage

- Done Authentication (JWT)
- Done Database Operations
- Done API Endpoints (CRUD)
- Done ML Model Integration
- Done Error Handling
- Done File Upload/Download
- Done Image Processing
- Done Search Functionality
- Done User Management
- Done Security Validation 