dotenv-filename := ".env"

# Define source directory for the project

SOURCE_DIR := "app"
TESTS_DIR := "tests"

# Help command to show all available commands
[group('default')]
help:
    @just --list

# Run pre-commit for all files
[group('formatters')]
precommit:
    pre-commit run --all-files

# Combined format command (includes linting and security)
[group('formatters')]
format: ruff mypy security

# Run Ruff linter with auto-fix
[group('formatters')]
ruff:
    ruff check --fix .

# Type checking with mypy
[group('formatters')]
mypy:
    mypy .

# Group of security checking commands
[group('security')]
security: bandit safety

# Run bandit security checker
[group('security')]
bandit:
    bandit -r ./{{ SOURCE_DIR }}

# Check dependencies for known security vulnerabilities
[group('security')]
safety:
    safety check

# Run project tests
[group('run-time')]
test:
    pytest -vs ./{{ TESTS_DIR }}

# Build local environment
[group('run-time')]
build-local:
    docker compose \
      -f .docker/local/docker-compose.yaml \
      --env-file .docker/local/docker-compose-variables.env \
      up \
      -d \
      --remove-orphans \
      --build

# Stop run local environment
[group('run-time')]
down-local:
    docker compose \
      -f .docker/local/docker-compose.yaml \
      --env-file .docker/local/docker-compose-variables.env \
      down

# Build test environment
[group('run-time')]
build-test:
    docker compose \
      -f .docker/test/docker-compose.yaml \
      --env-file .docker/test/docker-compose-variables.env \
      up \
      --remove-orphans \
      --build \
      --abort-on-container-exit

# Stop run test environment
[group('run-time')]
down-test:
    docker compose \
      -f .docker/test/docker-compose.yaml \
      --env-file .docker/test/docker-compose-variables.env \
      down
