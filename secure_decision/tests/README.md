# Testing Guide

This directory contains mock testing setup for the Secure Decision application.

## Setup

1. Install test dependencies:

```bash
pip install -r requirements.txt
```

2. Run tests:

```bash
pytest
```

3. Run tests with coverage:

```bash
pytest --cov=app --cov-report=html
```

4. Run specific test file:

```bash
pytest tests/test_main.py
```

## Test Structure

- `test_main.py`: Tests for FastAPI endpoints using TestClient and mocked database
- `test_serializers.py`: Tests for data serialization functions
- `test_kb_matcher.py`: Tests for knowledge base matching logic
- `conftest.py`: Shared fixtures for all tests

## Mock Testing Strategy

### Database Mocking

- Uses `unittest.mock` to mock SQLAlchemy database sessions
- Tests focus on business logic without requiring actual database
- Fixtures provide consistent mock objects

### API Testing

- Uses FastAPI's `TestClient` for integration testing
- Mocks database dependencies using `pytest-mock`
- Tests both success and error scenarios

### Unit Testing

- Tests individual functions and classes
- Mocks external dependencies
- Focuses on logic validation

## Key Fixtures

- `mock_user`: Mock User object
- `mock_team`: Mock Team object
- `mock_decision`: Mock Decision object with relationships
- `mock_decision_revision`: Mock DecisionRevision object
- `mock_threat_assessment`: Mock ThreatLiteAssessment object

## Running Tests in CI/CD

Add to your CI pipeline:

```yaml
- name: Run Tests
  run: |
    cd secure_decision
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml
```

## Test Coverage Goals

- Aim for >80% code coverage
- Focus on critical business logic
- Test error handling and edge cases
- Include integration tests for key workflows
