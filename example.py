from concurrent.futures import ThreadPoolExecutor
from time import sleep

from parallel_logger import display_session, pl_print


def task(n):
    pl_print(f"Task {n} starting")
    sleep(n * 3)
    pl_print(f"Task {n} completed")
    return n * n


def main() -> None:
    with display_session(), ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(6):
            executor.submit(task, i)


if __name__ == "__main__":
    main()
