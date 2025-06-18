# Pytest Best Practices

Rules for writing and organizing tests in this codebase using pytest.

<rule>
name: pytest_best_practices
description: Standards for writing and organizing pytest tests in the codebase
filters:
  # Match Python test files
  - type: file_path
    pattern: "tests/.*\\.py$"
  # Match pytest fixtures and test functions
  - type: content
    pattern: "(?:@pytest|def test_|async def test_)"

actions:
  - type: suggest
    message: |
      # Pytest Guidelines

      Follow these guidelines when writing pytest tests in this codebase:

      ## Async/Await Support

      1. **Always use `pytest_asyncio.fixture` for async fixtures**:
         ```python
         # CORRECT: Using pytest_asyncio for async fixtures
         import pytest_asyncio

         @pytest_asyncio.fixture
         async def repository(test_db_path):
             repo = SQLiteUserRepository(test_db_path)
             await repo.initialize()
             yield repo
             # Clean up...
         ```

         ```python
         # INCORRECT: Using pytest.fixture for async fixtures
         import pytest

         @pytest.fixture  # Will not work correctly with async
         async def repository(test_db_path):
             # ...
         ```

      2. For async tests, mark them with `@pytest.mark.asyncio`:
         ```python
         @pytest.mark.asyncio
         async def test_async_function():
             result = await my_async_function()
             assert result == expected_value
         ```

      ## Fixture Organization

      3. **Use appropriate fixture scopes**:
         - `scope="function"`: Default, recreated for each test function
         - `scope="class"`: Shared across all test methods in a class
         - `scope="module"`: Shared across all tests in a module
         - `scope="session"`: Created once for the entire test session

      4. **Use fixture layering** - build complex fixtures from simpler ones:
         ```python
         @pytest_asyncio.fixture
         async def repository(test_db_path):  # Depends on test_db_path fixture
             # ...
         ```

      5. **Clean up resources** in fixtures using `yield` pattern:
         ```python
         @pytest_asyncio.fixture
         async def repository(test_db_path):
             # Setup
             repo = SQLiteUserRepository(test_db_path)
             await repo.initialize()
             yield repo
             # Teardown
             try:
                 os.unlink(test_db_path)  # Clean up resources
             except (OSError, FileNotFoundError):
                 pass
         ```

      ## Test Structure and Organization

      6. **Keep test files aligned with implementation structure**:
         - Unit tests should mirror the structure of the source code
         - Integration tests should focus on component interactions
         - E2E tests should align with user workflows

      7. **Follow naming conventions**:
         - Test files: `test_<component_name>.py`
         - Test classes: `Test<ComponentName>`
         - Test functions: `test_<functionality_being_tested>`

      8. **Group related tests in classes**:
         ```python
         class TestSQLiteUserRepository:
             """Tests for SQLiteUserRepository."""

             @pytest.mark.asyncio
             async def test_create_user(self, repository, sample_user):
                 # ...

             @pytest.mark.asyncio
             async def test_get_user_by_id(self, repository, sample_user):
                 # ...
         ```

      9. **Use descriptive test names** that explain the functionality being tested

      ## Testing Against Interfaces

      10. **Test against interfaces, not implementations**:
          - Mock or provide test implementations of interfaces
          - Avoid tight coupling to specific implementations

      11. **Use explicit assertions** with clear failure messages:
          ```python
          assert user.id == expected_id, f"User ID {user.id} doesn't match expected {expected_id}"
          ```

      ## Testing in Clean Architecture

      12. **Apply Clean Architecture principles to tests**:
          - Unit tests should test domain and services in isolation
          - Integration tests should verify adapter implementations
          - Adapters should be tested through their interfaces
          - Use dependency injection for test doubles

      13. **For adapter tests**:
          - Test that adapters fulfill their interface contract
          - Test all required initialization and cleanup
          - Verify error handling and edge cases
          - Test actual integration with external systems in integration tests

  - type: warn
    conditions:
      - pattern: "@pytest.fixture\\s+async\\s+def"
        message: "Use @pytest_asyncio.fixture for async fixture functions instead of @pytest.fixture"

      - pattern: "def\\s+test_[^(]+\\(\\s*self\\s*\\):"
        message: "Test function doesn't use any class attributes. Consider making it a standalone function"

      - pattern: "assert\\s+\\w+[^,]*$"
        message: "Consider adding a descriptive failure message to assert statements"

examples:
  - input: |
      # Bad: Using pytest.fixture with async def
      @pytest.fixture
      async def database():
          # Setup
          yield db
          # Teardown
    output: "Use @pytest_asyncio.fixture for async fixture functions"

  - input: |
      # Good: Using pytest_asyncio.fixture with async def
      @pytest_asyncio.fixture
      async def database():
          # Setup
          yield db
          # Teardown
    output: "Correctly using pytest_asyncio.fixture for async fixtures"

  - input: |
      # Missing async mark
      async def test_async_function():
          result = await some_function()
          assert result
    output: "Add @pytest.mark.asyncio to async test functions"

  - input: |
      # Good async test
      @pytest.mark.asyncio
      async def test_async_function():
          result = await some_function()
          assert result
    output: "Correctly marked async test function"

metadata:
  priority: high
  version: 1.0
  applies_to:
    - "tests/**/*.py"
</rule>
