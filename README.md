# infraDevContainerTest

This repo is used to test the `infraDevContainer` submodule, which contains scripts and configuration for VSCode Dev Container support.

## Quick Start

```bash
python3 setup_venv.py
./.venv/bin/python -m pytest install_test.py -v
```

## Testing install.py

The `install_test.py` file contains a comprehensive pytest test suite that verifies `install.py` meets all requirements specified in `infraDevContainer/install.spec.md`.

### Setup

For a fresh clone, run the setup script from the repo root:

```bash
python3 setup_venv.py
```

This script will:

- Create `.venv` if it does not exist
- Upgrade `pip` inside `.venv`
- Install `pytest`

To force a clean rebuild of the environment:

```bash
python3 setup_venv.py --recreate
```

If you prefer manual setup:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install pytest
```

Optional: activate the virtual environment in your current shell:

```bash
source .venv/bin/activate
python -m pytest install_test.py -v
deactivate
```

Note: activation only affects the current shell session. It does not change your system Python installation.

### Running Tests

**Run all tests with detailed output:**
```bash
./.venv/bin/python -m pytest install_test.py -v
```

**Run tests with minimal output:**
```bash
./.venv/bin/python -m pytest install_test.py
```

**Run a specific test class:**
```bash
./.venv/bin/python -m pytest install_test.py::TestPerformInstall -v
```

**Run a specific test:**
```bash
./.venv/bin/python -m pytest install_test.py::TestPerformInstall::test_install_copy_creates_files -v
```

**Run with coverage report:**
```bash
./.venv/bin/python -m pytest install_test.py --cov=infraDevContainer/install --cov-report=html
```

**Run and stop on first failure:**
```bash
./.venv/bin/python -m pytest install_test.py -x
```

**Show print statements during tests:**
```bash
./.venv/bin/python -m pytest install_test.py -v -s
```

### Test Coverage

The test suite includes 44 tests covering:

- **Argument parsing**: Command-line argument validation
- **Configuration validation**: Valid/invalid operation and method combinations
- **File collection**: Verifying required source files exist
- **Copy installation**: File copying to .devcontainer
- **Symlink installation**: Relative symbolic link creation
- **Uninstall operations**: File and directory removal
- **User confirmation**: Install/uninstall prompts
- **Error handling**: Missing files, existing directories, extra files
- **Integration**: Full install/uninstall workflows
- **Cleanup**: Proper cleanup on installation failure

All tests pass when run successfully.