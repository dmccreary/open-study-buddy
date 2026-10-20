#!/usr/bin/env python3
"""Chapter 17: is anything secret about to be committed to git?

Checks, from the git repository you run it in:
  1. .gitignore lists secrets.py
  2. git is not tracking any secrets*.py file (except secrets-template.py)
  3. no tracked text file assigns a long string to a name that looks like a
     password, token, or key

It prints WHERE a problem is (file and line number) and NEVER prints the
secret itself. Print where, not what: logs and chat messages get shared.

    python3 check_secrets.py          (run it inside the repository)
"""
import re
import subprocess
import sys

# Lines that contain one of these are teaching placeholders, not secrets.
PLACEHOLDERS = ("example", "changeme", "placeholder", "random-string", "your-", "xxxx")

SUSPICIOUS = re.compile(
    r"""(pass|pwd|token|secret|api_?key|psk)\w*\s*=\s*["'][^"']{8,}["']""",
    re.IGNORECASE)


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True).stdout


def main():
    problems = []

    ignored = False
    try:
        with open(".gitignore") as f:
            ignored = any(line.strip() in ("secrets.py", "**/secrets.py", "/secrets.py")
                          for line in f)
    except OSError:
        pass
    if not ignored:
        problems.append(".gitignore does not list secrets.py")

    tracked = git("ls-files").splitlines()
    for name in tracked:
        base = name.rsplit("/", 1)[-1]
        if base.startswith("secrets") and base.endswith(".py") and base != "secrets-template.py":
            problems.append("git is tracking {}".format(name))

    for name in tracked:
        if not name.endswith((".py", ".json", ".yml", ".yaml", ".env", ".md", ".txt", ".sh")):
            continue
        try:
            with open(name, encoding="utf-8") as f:
                for number, line in enumerate(f, 1):
                    if SUSPICIOUS.search(line) and \
                            not any(word in line.lower() for word in PLACEHOLDERS):
                        problems.append("{}:{} looks like a secret".format(name, number))
        except (OSError, UnicodeDecodeError):
            pass

    for p in problems:
        print("PROBLEM", p)
    print("PASS" if not problems else "FAIL: {} problem(s). If a real secret was ever committed, "
          "changing the file is not enough: rotate the secret.".format(len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
