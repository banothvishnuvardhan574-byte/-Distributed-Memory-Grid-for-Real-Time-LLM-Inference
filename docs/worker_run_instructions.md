# Worker Run Instructions

## 1. Purpose

This document explains how to run and test the worker component locally.

## 2. Prerequisites

- Python is installed.
- The project virtual environment (`.venv`) is available.
- Project dependencies are installed.

## 3. Run the Worker Tests

Open the VS Code terminal in the project's main folder and run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_worker.py -v
```

This command runs the worker tests and shows whether they pass or fail.


## 4. Stop the Process

After the command finishes, the terminal returns to the prompt automatically.

If a running command needs to be interrupted, press `Ctrl + C` in the terminal.


## 5. Important Note

The current worker is a Python module that is called by code; it is not yet a standalone worker service with a separate start command.

The test command above tests the worker. It does not start a continuously running worker service.

A separate startup command can be documented after the team decides how the worker will run during integration.