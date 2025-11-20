import threading
from contextlib import contextmanager
from typing import Iterator, Optional

from parallel_logger.instance import ParallelLogger

_SINGLETON_LOGGER = ParallelLogger()
_DISPLAY_THREAD_LOCK = threading.Lock()
_DISPLAY_THREAD: Optional[threading.Thread] = None


def pl_print(*args, sep: str = " ", end: str = "\n") -> None:
    """Proxy to the singleton logger's ``pl_print``."""

    _SINGLETON_LOGGER.pl_print(*args, sep=sep, end=end)


def run_display(refresh_rate: float = 0.1) -> None:
    """Run the interactive viewer for the shared logger."""

    _SINGLETON_LOGGER.run_display(refresh_rate=refresh_rate)


def stop_display() -> None:
    """Programmatically stop the display loop if it is running."""

    _SINGLETON_LOGGER.stop_display()


def start_display(refresh_rate: float = 0.1) -> threading.Thread:
    """Launch the curses UI on a helper thread and return it."""

    global _DISPLAY_THREAD
    with _DISPLAY_THREAD_LOCK:
        if _DISPLAY_THREAD and _DISPLAY_THREAD.is_alive():
            return _DISPLAY_THREAD

        def _runner() -> None:
            try:
                run_display(refresh_rate=refresh_rate)
            finally:
                with _DISPLAY_THREAD_LOCK:
                    _DISPLAY_THREAD = None

        thread = threading.Thread(
            target=_runner,
            name="ParallelLoggerUI",
            daemon=True,
        )
        _DISPLAY_THREAD = thread
        thread.start()
        return thread


def is_display_running() -> bool:
    """Return ``True`` if the UI thread is alive."""

    with _DISPLAY_THREAD_LOCK:
        return _DISPLAY_THREAD is not None and _DISPLAY_THREAD.is_alive()


@contextmanager
def display_session(refresh_rate: float = 0.1) -> Iterator[None]:
    """Run the curses viewer in a helper thread for the duration of the block."""

    already_running = is_display_running()
    display_thread = start_display(refresh_rate=refresh_rate)
    try:
        yield
    finally:
        if not already_running:
            stop_display()
            display_thread.join()


__all__ = [
    "pl_print",
    "run_display",
    "stop_display",
    "start_display",
    "is_display_running",
    "display_session",
]
