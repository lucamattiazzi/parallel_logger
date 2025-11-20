# Parallel Logger

A Python logging utility designed for parallel processing applications. It provides an interactive curses-based terminal UI to monitor and debug logs from multiple threads in real-time.

## Features

- **Thread-aware logging**: Automatically tracks and organizes logs by thread name
- **Interactive TUI**: Navigate between different threads using arrow keys
- **Real-time updates**: Logs are displayed as they're generated
- **Easy integration**: Simple API with context manager support
- **Thread-safe**: Built with thread safety in mind using locks and events

## Installation

```bash
pip install parallel_logger
```

## Quick Start

### Using Context Manager (Recommended)

```python
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from parallel_logger import display_session, pl_print

def task(n):
    pl_print(f"Task {n} starting")
    sleep(n * 3)
    pl_print(f"Task {n} completed")
    return n * n

with display_session():
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(6):
            executor.submit(task, i)
```

### Manual Control

```python
from parallel_logger import start_display, stop_display, pl_print

start_display()
try:
    # Your parallel code here
    pl_print("Hello from thread!")
finally:
    stop_display()
```

## API Reference

### Core Functions

#### `pl_print(*args, sep=" ", end="\n")`

Records a message for the current thread. Works like Python's built-in `print()` function but routes output to the parallel logger instead of stdout.

**Parameters:**

- `*args`: Values to print
- `sep`: Separator between values (default: `" "`)
- `end`: String appended after the last value (default: `"\n"`)

#### `display_session(refresh_rate=0.1)`

Context manager that runs the curses viewer in a helper thread for the duration of the block.

**Parameters:**

- `refresh_rate`: How often to refresh the display in seconds (default: `0.1`)

**Example:**

```python
with display_session(refresh_rate=0.05):
    # Your parallel code here
    pass
```

#### `start_display(refresh_rate=0.1)`

Launches the curses UI on a helper thread and returns the thread object.

**Parameters:**

- `refresh_rate`: How often to refresh the display in seconds (default: `0.1`)

**Returns:** `threading.Thread` object

#### `stop_display()`

Programmatically stops the display loop if it is running.

#### `run_display(refresh_rate=0.1)`

Runs the interactive viewer. This is a blocking call that will run until stopped.

**Parameters:**

- `refresh_rate`: How often to refresh the display in seconds (default: `0.1`)

#### `is_display_running()`

Checks if the UI thread is currently alive.

**Returns:** `bool` - `True` if the display is running, `False` otherwise

## Interactive UI Controls

When the display is running, you can interact with it using:

- **Left Arrow (←)**: Switch to previous thread
- **Right Arrow (→)**: Switch to next thread
- **Q**: Quit the display

The UI shows:

- Current thread name and position (e.g., "Thread 2/5: ThreadPoolExecutor-0_1")
- All logs from the selected thread
- Navigation instructions in the footer

## Requirements

- Python >= 3.13
- Standard library only (no external dependencies)

## Example

See the included `example.py` for a complete working demonstration:

```bash
python example.py --mode context
python example.py --mode manual
```

## How It Works

The library uses a singleton `ParallelLogger` instance that:

1. Collects log messages from each thread separately
2. Maintains thread order based on first log appearance
3. Renders logs in a curses-based terminal UI
4. Allows interactive navigation between thread logs

All logging is thread-safe using `threading.Lock()` and coordination between threads is managed with `threading.Event()` objects.

## License

See LICENSE file for details.

## Author

Luca Mattiazzi
