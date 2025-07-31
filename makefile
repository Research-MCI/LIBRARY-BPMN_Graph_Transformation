# Cross-platform Python project Makefile
.PHONY: env install dev run lint format test shell clean upgrade help

PYTHON ?= python
VENV_DIR := .venv
# Use unique temporary test directory with timestamp
TEST_TMP_BASE := .pytest_tmp
TEST_TMP_DIR := $(TEST_TMP_BASE)_$(shell date +%s)

# Detect shell type for correct command syntax
SHELL_TYPE := $(shell echo $$0)

# Platform-specific settings
ifeq ($(OS),Windows_NT)
    # Windows paths
    VENV_BIN := $(VENV_DIR)/Scripts
    # Check if running in a Unix-like shell on Windows (Git Bash, etc.)
    ifeq ($(findstring bash,$(SHELL_TYPE)),bash)
        # Git Bash on Windows
        RM_CMD := rm -rf
        RM_FILE := rm -f
        MKDIR := mkdir -p
        NULL_DEV := /dev/null
        # Set PYTHONPATH for Git Bash
        PYTHONPATH_CMD := PYTHONPATH='$$(pwd)'
    else
        # Windows CMD/PowerShell
        RM_CMD := if exist
        RM_DIR := rmdir /s /q
        RM_FILE := if exist "$(1)" del /f /q "$(1)"
        MKDIR := mkdir
        NULL_DEV := nul
        # Set PYTHONPATH for Windows CMD
        PYTHONPATH_CMD := set "PYTHONPATH=%cd%"
    endif
else
    # Unix systems (Linux/macOS)
    VENV_BIN := $(VENV_DIR)/bin
    RM_CMD := rm -rf
    RM_FILE := rm -f
    MKDIR := mkdir -p
    NULL_DEV := /dev/null
    # Set PYTHONPATH for Unix
    PYTHONPATH_CMD := PYTHONPATH='$$(pwd)'
endif

# Tool paths
PIP := $(VENV_BIN)/pip
PYTHON_VENV := $(VENV_BIN)/python
FLASK := $(VENV_BIN)/flask
GUNICORN := $(VENV_BIN)/gunicorn
PYTEST := $(VENV_BIN)/pytest
BLACK := $(VENV_BIN)/black
ISORT := $(VENV_BIN)/isort
FLAKE8 := $(VENV_BIN)/flake8

# Activation command for different shells
ifeq ($(findstring bash,$(SHELL_TYPE)),bash)
    # Bash-style activation
    ACTIVATE := . $(VENV_BIN)/activate
    EXEC_CMD := $(ACTIVATE) &&
else ifeq ($(OS),Windows_NT)
    # Windows CMD activation
    ACTIVATE := $(VENV_BIN)/activate.bat
    EXEC_CMD := call $(ACTIVATE) &&
else
    # Default Unix activation
    ACTIVATE := . $(VENV_BIN)/activate
    EXEC_CMD := $(ACTIVATE) &&
endif

# Create virtual environment
env:
	@echo "Checking for virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

# Install dependencies
install: env
	@echo "Installing dependencies..."
	@$(EXEC_CMD) $(PIP) install --upgrade pip
	@$(EXEC_CMD) $(PIP) install -r requirements-dev.txt

# Run Flask development server using python -m flask
dev: env
	@echo "Running Flask development server..."
	@$(EXEC_CMD) $(PYTHON_VENV) -m flask --app main:app run

# Run production server
run: env
	@echo "Running Gunicorn production server..."
	@$(EXEC_CMD) $(GUNICORN) --bind 0.0.0.0:5000 --workers 4 'main:app'

# Run linting
lint: env
	@echo "Linting code with flake8..."
	@$(EXEC_CMD) $(FLAKE8) app/ tests/

# Format code
format: env
	@echo "Formatting code with black and isort..."
	@$(EXEC_CMD) $(BLACK) app/ tests/
	@$(EXEC_CMD) $(ISORT) app/ tests/

# Run tests with improved Python path handling
test: env
	@echo "Creating unique temp directory for tests..."
	@$(MKDIR) $(TEST_TMP_DIR) 2>$(NULL_DEV) || true
	@echo "Running tests with pytest..."
ifeq ($(OS),Windows_NT)
ifeq ($(findstring bash,$(SHELL_TYPE)),bash)
	@$(EXEC_CMD) export PYTHONPATH="$$(pwd):$${PYTHONPATH}" && $(PYTEST) --cov=app --basetemp="$(TEST_TMP_DIR)" tests/
else
	@$(EXEC_CMD) $(PYTHONPATH_CMD) && $(PYTEST) --cov=app --basetemp="$(TEST_TMP_DIR)" tests/
endif
else
	@$(EXEC_CMD) PYTHONPATH="$$(pwd):$${PYTHONPATH}" $(PYTEST) --cov=app --basetemp="$(TEST_TMP_DIR)" tests/
endif
	@echo "Note: Temporary test files in $(TEST_TMP_DIR) will be cleaned on next 'make clean'"

# Create app initialization files if missing
init:
	@echo "Creating app package structure if not exists..."
	@if [ ! -d "app" ]; then \
		echo "Creating app directory structure..."; \
		$(MKDIR) app app/infrastructure/db app/utils; \
		echo "# App package" > app/__init__.py; \
		echo "# Infrastructure package" > app/infrastructure/__init__.py; \
		echo "# DB package" > app/infrastructure/db/__init__.py; \
		echo "# Utils package" > app/utils/__init__.py; \
	fi
	@if [ ! -d "tests" ]; then \
		echo "Creating tests directory structure..."; \
		$(MKDIR) tests/infrastructure tests/utils; \
		echo "# Tests package" > tests/__init__.py; \
		echo "# Infrastructure tests" > tests/infrastructure/__init__.py; \
		echo "# Utils tests" > tests/utils/__init__.py; \
	fi

# Open Flask shell using python -m flask
shell: env
	@echo "Opening Flask shell (with venv active)..."
	@$(EXEC_CMD) $(PYTHON_VENV) -m flask --app main:app shell

# Show activation command
activate: env
	@echo "To activate the virtual environment:"
ifeq ($(OS),Windows_NT)
ifeq ($(findstring bash,$(SHELL_TYPE)),bash)
	@echo "In Git Bash/MSYS: source $(VENV_BIN)/activate"
else
	@echo "In CMD: $(VENV_BIN)\activate.bat"
	@echo "In PowerShell: & '$(VENV_BIN)\Activate.ps1'"
endif
else
	@echo "source $(VENV_BIN)/activate"
endif

# Clean up with enhanced error handling
clean:
	@echo "Cleaning up project directories..."
ifeq ($(OS),Windows_NT)
ifeq ($(findstring bash,$(SHELL_TYPE)),bash)
	@$(RM_CMD) $(VENV_DIR) 2>$(NULL_DEV) || true
	@$(RM_CMD) $(TEST_TMP_BASE)* 2>$(NULL_DEV) || true
	@$(RM_CMD) .mypy_cache .pytest_cache __pycache__ htmlcov 2>$(NULL_DEV) || true
	@$(RM_FILE) .coverage 2>$(NULL_DEV) || true
else
	@$(RM_CMD) $(VENV_DIR) $(RM_DIR) $(VENV_DIR)
	@for /d %%i in ($(TEST_TMP_BASE)*) do @if exist %%i $(RM_DIR) %%i
	@if exist .mypy_cache $(RM_DIR) .mypy_cache
	@if exist .pytest_cache $(RM_DIR) .pytest_cache
	@if exist __pycache__ $(RM_DIR) __pycache__
	@if exist htmlcov $(RM_DIR) htmlcov
	@if exist .coverage del /f /q .coverage
endif
else
	@$(RM_CMD) $(VENV_DIR) $(TEST_TMP_BASE)* .mypy_cache .pytest_cache __pycache__ htmlcov .coverage 2>$(NULL_DEV) || true
endif

# Upgrade dependencies
upgrade: env
	@echo "Upgrading pip and dependencies..."
	@$(EXEC_CMD) $(PIP) install --upgrade pip setuptools wheel
	@$(EXEC_CMD) $(PIP) install --upgrade -r requirements-dev.txt

# Help message
help:
	@echo "Available commands:"
	@echo "  make env       # Create python virtual environment"
	@echo "  make install   # Install dev requirements"
	@echo "  make init      # Create app package structure if missing"
	@echo "  make dev       # Run Flask development server"
	@echo "  make run       # Run Gunicorn production server"
	@echo "  make lint      # Run flake8 linting"
	@echo "  make format    # Format code (black + isort)"
	@echo "  make test      # Run tests with pytest"
	@echo "  make shell     # Flask shell"
	@echo "  make activate  # Show activation command"
	@echo "  make clean     # Remove virtualenv and caches"
	@echo "  make upgrade   # Upgrade pip and all dependencies"
	@echo "  make help      # Show this help message"

.DEFAULT_GOAL := help