# Clean Hexagonal Architecture v2

Guidelines for maintaining the clean hexagonal architecture pattern in this codebase, including specific implementation patterns.

## Core Architectural Principles

When working with this codebase, adhere to these architectural principles to maintain consistency and quality:

### Dependency Injection

- Use constructor-based dependency injection as the primary means of composition
- Avoid global state, service locators, or singletons
- Pass dependencies explicitly rather than importing them within functions
- No dependency injection framework is needed - explicit is better than implicit
- Explicit static DI provides excellent IDE support (autocompletion, navigation, refactoring)
- Type hints on injected dependencies enable better static analysis and type checking
- The approach encourages clear component boundaries and interfaces
- This makes code easier to understand, maintain, and refactor with IDE assistance

### Interface-First Design

- Define interfaces using Abstract Base Classes (ABCs) before implementations
- Keep interfaces small and focused on specific responsibilities (Interface Segregation)
- Program to interfaces, not implementations
- Place interfaces in `base.py` files within their respective adapter directories
- **IMPORTANT**: Every concrete implementation MUST implement an interface; direct implementation without an interface is not permitted

### Adapter Pattern

- Isolate all side effects and external dependencies into adapter classes
- Adapters should implement interfaces defined by the application
- External systems should only be accessed through appropriate adapters
- All inter-component communication should use Pydantic models
- Adapters MUST handle their own resource-specific setup (e.g., directory creation)
- If adapters require async initialization, they MUST provide an `initialize()` method

### Configuration Flow Pattern

- **CRITICAL**: Environment variables MUST be defined in `.env.*` files
- Variables MUST be loaded into `Settings` class in `config.py`
- Environment files (e.g., `default.py`) MUST import from `config.py`
- Adapters MUST receive configuration through constructor parameters
- **NEVER** access environment variables directly from adapters or services
- Default values for configuration should be specified in the `Settings` class

### Environment Bootstrapping Pattern

- Environment instantiation MUST occur in dedicated environment files (e.g., `default.py`)
- The environment file instantiates all adapters with proper configuration
- Bootstrap mechanism (`bootstrap.py`) MUST load and return this environment
- Application entry point MUST complete any necessary async initialization
- Two-phase initialization: construction in env files, async init in application startup

### Platform Separation

- Platforms serve as entry points for client communication
- Unlike adapters, platforms are instigators/initiators of workloads
- Each platform (REST API, Discord webhook, CLI, etc.) should implement a common interface
- Platforms should delegate business logic to services, never implementing it directly
- Keep platform-specific code isolated from the core application logic

### Environment as Aggregate Root

- Use the Environment class as an explicit aggregate root for all dependencies
- Simplify complex dependency graphs by having a common ancestor
- Bootstrap the application through a central entry point that constructs the environment
- Environment MUST contain the Adapters container, which holds all adapter instances

### Adapter Naming and Structure

- Adapters MUST be organized by their purpose (e.g., `user_repository`, `scheduling`)
- Each adapter category MUST follow the pattern: base interface + implementations
- Base interfaces MUST be in `base.py` and define the contract using ABC
- Implementations MUST be named by their backend technology (e.g., `sqlite.py`)

### Asynchronous Design

- Design for asynchronous operation by default
- Use async/await patterns consistently throughout the codebase
- Ensure all I/O operations are non-blocking
- If adapters require async initialization, provide an `initialize()` method

### Type Safety

- Use Python type hints for all function parameters and return values
- Use Pydantic models for data validation at system boundaries
- Leverage static type checking tools (mypy) to catch type errors early

### Composition Over Inheritance

- Prefer composing objects through dependencies rather than inheritance hierarchies
- Use functional composition where appropriate (e.g., scenario functions)

### Testability

- Design components to be easily testable in isolation
- Use dependency injection to facilitate mocking in tests
- Write unit tests for core domain logic independent of adapters

## Example Project Structure

```
myapp/
├── domain/           # Core business entities and logic
│   ├── __init__.py
│   └── models.py     # Core domain models using Pydantic
├── adapters/         # External system integrations
│   ├── __init__.py
│   ├── storage/
│   │   ├── base.py   # Storage interface as ABC
│   │   └── file_storage.py
│   └── api/
│       ├── base.py   # API interface as ABC
│       └── rest_api.py
├── platforms/        # Client communication entry points
│   ├── __init__.py
│   ├── base.py       # Platform interface as ABC
│   ├── discord.py    # Discord webhook platform
│   ├── cli.py        # Command-line interface platform
│   └── rest.py       # REST API platform
├── services/         # Application use cases and orchestration
│   ├── __init__.py
│   └── user_service.py
├── envs/             # Environment configurations
│   ├── __init__.py
│   ├── types.py      # Environment and Adapters type definitions
│   └── default.py    # Default environment configuration
├── config.py         # Centralized configuration management
├── bootstrap.py      # Application initialization
└── main.py           # Entry point
```

## Configuration Flow Example

### Environment Variables (.env.debug)

```
DISCORD_TOKEN="your-token-here"
USER_DB_PATH=".local/users/debug.db"
IS_DEBUG=True
```

### Settings Class (config.py)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DISCORD_TOKEN: str
    USER_DB_PATH: str = ".local/users/users.db"  # Default to production path
    IS_DEBUG: bool = False

    model_config = SettingsConfigDict()

# Load settings from environment files
settings = Settings(_env_file=(".env.base", ".env.debug"))
```

### Environment Setup (envs/default.py)

```python
from checkin.adapters.user_repository.sqlite import SQLiteUserRepository
from checkin.config import settings
from checkin.envs.types import Adapters, Environment

# Initialize SQLite user repository with path from settings
user_repository = SQLiteUserRepository(db_path=settings.USER_DB_PATH)

adapters = Adapters(
    # Other adapters...
    user_repository=user_repository,
)

environment = Environment(adapters=adapters, is_debug=settings.IS_DEBUG)
```

### Application Entry Point (main.py)

```python
async def main():
    # Initialize environment
    environment = create_environment()

    # Perform async initialization of adapters
    await environment.adapters.user_repository.initialize()

    # Start application...
```

## Repository Implementation Example

### Interface Definition (adapters/user_repository/base.py)

```python
from abc import ABC, abstractmethod
from typing import Optional

from myapp.domain.models import User

class UserRepositoryInterface(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the repository."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID."""
        pass
```

### Implementation (adapters/user_repository/sqlite.py)

```python
import os
import sqlite3
import aiosqlite
from typing import Optional

from myapp.adapters.user_repository.base import UserRepositoryInterface
from myapp.domain.models import User

class SQLiteUserRepository(UserRepositoryInterface):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_directory_exists()

    def _ensure_db_directory_exists(self) -> None:
        """Ensure the directory for the database file exists."""
        directory = os.path.dirname(self.db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize the database with required tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL
                )
            """)
            await db.commit()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = await cursor.fetchone()

        return User(id=row["id"], email=row["email"]) if row else None
```

## Common Anti-Patterns to Avoid

1. **Directly accessing environment variables in adapters or services**

   ```python
   # WRONG: Direct access to env vars
   db_path = os.environ.get("USER_DB_PATH", ".local/users/default.db")

   # CORRECT: Access through settings
   from myapp.config import settings
   db_path = settings.USER_DB_PATH
   ```

2. **Creating adapters without using their interfaces**

   ```python
   # WRONG: Direct implementation without interface
   class DirectSQLiteRepo:  # Not implementing an interface
       pass

   # CORRECT: Implementing an interface
   class SQLiteUserRepository(UserRepositoryInterface):
       pass
   ```

3. **Putting application configuration logic in adapters**

   ```python
   # WRONG: Configuration logic in adapter
   class BadAdapter:
       def __init__(self):
           # Adapter deciding its own configuration
           if os.environ.get("IS_DEBUG") == "True":
               self.db_path = ".local/users/debug.db"
           else:
               self.db_path = ".local/users/prod.db"

   # CORRECT: Configuration passed to adapter
   class GoodAdapter:
       def __init__(self, db_path: str):
           self.db_path = db_path
   ```

4. **Initializing adapters in services rather than environment**

   ```python
   # WRONG: Service creating its own dependencies
   class BadService:
       def __init__(self):
           self.repository = SQLiteUserRepository(".local/users/users.db")

   # CORRECT: Dependencies injected into service
   class GoodService:
       def __init__(self, repository: UserRepositoryInterface):
           self.repository = repository
   ```

5. **Skipping async initialization for adapters that need it**

   ```python
   # WRONG: Using adapter without initialization
   repo = SQLiteUserRepository(db_path)
   await repo.get_user_by_id("123")  # Tables might not exist!

   # CORRECT: Initializing before use
   repo = SQLiteUserRepository(db_path)
   await repo.initialize()
   await repo.get_user_by_id("123")
   ```

Remember: This architecture emphasizes explicit dependencies, clear interfaces, and separation of concerns. Following these principles consistently will result in a maintainable, testable, and extensible codebase.
