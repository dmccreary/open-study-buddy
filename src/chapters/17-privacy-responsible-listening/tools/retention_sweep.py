#!/usr/bin/env python3
"""Chapter 17: enforce a retention period. Finds files older than N days in a
folder (for example the buddy server's log folder) and, only when you add
--delete, removes them. The default is a DRY RUN that deletes nothing.

    python3 retention_sweep.py ./server-logs --days 7
    python3 retention_sweep.py ./server-logs --days 7 --delete

Only plain files directly inside the folder you name are considered, only
files whose names end in one of EXTENSIONS, and the folder itself is never
removed. Run it from a scheduler (cron) so the rule is kept without anyone
remembering it. A retention number nobody enforces is only a wish.
"""
import os
import sys
import time

EXTENSIONS = (".wav", ".raw", ".txt", ".log", ".json", ".jsonl")


def old_files(folder, days, now=None):
    now = time.time() if now is None else now
    cutoff = now - days * 86400
    found = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if (os.path.isfile(path) and not os.path.islink(path)
                and name.endswith(EXTENSIONS) and os.path.getmtime(path) < cutoff):
            found.append((name, (now - os.path.getmtime(path)) / 86400))
    return found


def main(argv):
    if len(argv) < 2 or "--days" not in argv:
        print(__doc__)
        return 2
    folder = argv[1]
    days = float(argv[argv.index("--days") + 1])
    delete = "--delete" in argv
    found = old_files(folder, days)
    for name, age in found:
        print("{} {:<24} {:.1f} days old".format("DELETE" if delete else "would delete", name, age))
        if delete:
            os.remove(os.path.join(folder, name))
    print("{} file(s) {} (limit {} days){}".format(
        len(found), "deleted" if delete else "found", days,
        "" if delete else "; dry run, nothing removed"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
