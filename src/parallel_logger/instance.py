import curses
import textwrap
import threading


class ParallelLogger:
    """Collects per-thread log lines and renders them in a curses UI."""

    _logs: dict[str, list[str]] = {}
    _lock = threading.Lock()
    _event_update = threading.Event()
    _event_stop = threading.Event()
    _current_index = 0

    def __init__(self) -> None:
        pass

    def pl_print(self, *args, sep: str = " ", end: str = "\n") -> None:
        """Record a message for the current thread."""
        thread_name = threading.current_thread().name
        rendered = sep.join(str(arg) for arg in args)
        payload = f"{rendered}{end}"
        lines = payload.split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        with self._lock:
            if thread_name not in self._logs:
                self._logs[thread_name] = []
                if len(self._order()) == 1:
                    self._current_index = 0
            self._logs[thread_name].extend(lines or [""])
        self._event_update.set()

    def run_display(self, refresh_rate: float = 0.1) -> None:
        """Start the curses UI. This call blocks until the display is stopped."""

        self._event_stop.clear()
        try:
            curses.wrapper(lambda stdscr: self._display_loop(stdscr, refresh_rate))
        finally:
            self._event_stop.set()

    def stop_display(self) -> None:
        """Request the display loop to exit."""

        self._event_stop.set()
        self._event_update.set()
        self._logs.clear()

    def _order(self) -> list[str]:
        return list(self._logs.keys())

    def _display_loop(self, stdscr, refresh_rate: float) -> None:  # type: ignore[override]
        curses.curs_set(0)
        curses.use_default_colors()
        stdscr.nodelay(True)
        while not self._event_stop.is_set():
            self._render(stdscr)
            key = stdscr.getch()
            self._handle_keypress(key)
            self._event_update.wait(timeout=refresh_rate)
            self._event_update.clear()

    def _handle_keypress(self, key: int) -> None:
        if key == -1:
            return
        if key == curses.KEY_RIGHT:
            self._select_next()
        elif key == curses.KEY_LEFT:
            self._select_previous()
        elif key in (ord("q"), ord("Q")):
            self.stop_display()

    def _select_next(self) -> None:
        with self._lock:
            if self._order():
                self._current_index = (self._current_index + 1) % len(self._order())
        self._event_update.set()

    def _select_previous(self) -> None:
        with self._lock:
            if self._order():
                self._current_index = (self._current_index - 1) % len(self._order())
        self._event_update.set()

    def _render(self, stdscr) -> None:
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        with self._lock:
            order = list(self._order())
            selected_index = self._current_index if order else 0
            current_thread = order[selected_index] if order else None
            lines = list(self._logs.get(current_thread, [])) if current_thread else []
            total_threads = len(order)
        if current_thread is None:
            msg = "Waiting for threads to call pl_print()..."
            y = max(0, height // 2)
            x = max(0, (width - len(msg)) // 2)
            try:
                stdscr.addnstr(y, x, msg, width)
            except curses.error:
                pass
            stdscr.refresh()
            return

        header = f"Thread {selected_index + 1}/{total_threads}: {current_thread}"
        info_line = f"{header}"
        try:
            stdscr.addnstr(0, 0, info_line.ljust(width), width)
        except curses.error:
            pass
        try:
            stdscr.addnstr(1, 0, "".ljust(width, "-"), width)
        except curses.error:
            pass

        wrapped_lines: list[str] = []
        for line in lines:
            if not line:
                wrapped_lines.append("")
                continue
            wrapped = textwrap.wrap(
                line,
                width=max(width, 1),
                drop_whitespace=False,
                replace_whitespace=False,
            )
            wrapped_lines.extend(wrapped or [""])
        max_body_rows = max(0, height - 3)
        start = max(0, len(wrapped_lines) - max_body_rows)
        body = wrapped_lines[start:]
        for row, content in enumerate(body, start=2):
            if row >= height:
                break
            try:
                stdscr.addnstr(row, 0, content.ljust(width)[:width], width)
            except curses.error:
                continue
        footer = "Use <- / -> to change thread - q to quit"
        if height > 2:
            try:
                stdscr.addnstr(height - 1, 0, footer.ljust(width), width)
            except curses.error:
                pass
        stdscr.refresh()
