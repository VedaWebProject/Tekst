import linecache
import os
import tracemalloc

from tekst.logs import log


def _sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def mem_trace_start():
    log.debug("Starting memory trace...")
    tracemalloc.start()


def mem_trace_snapshot(key_type: str = "lineno", limit: int = 5):
    log.debug("Taking memory trace snapshot...")
    snapshot = tracemalloc.take_snapshot().filter_traces(
        (
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        )
    )
    top_stats = snapshot.statistics(key_type)

    print(f"Top {limit} lines")
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print(f"#{index}: {filename}:{frame.lineno}: {_sizeof_fmt(stat.size)}")
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print(f"    {line}")

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print(f"{len(other)} other: {_sizeof_fmt(size)}")
    total = sum(stat.size for stat in top_stats)
    print(f"Total allocated size: {_sizeof_fmt(total)}")
