#!/usr/bin/env python3
"""
Bulk-run migrate_account.py over a CSV (from;to format).

=============================================================================
PLACEHOLDER / OPERATIONAL COPY
This is a copy of the original production script located in the
/opt/seafile/scripts/migration/ directory on the automation host.

This script is legacy (for bulk department migrations). It is kept here
as a reference and for continued use during the transition.

The new self-service worker (process_keeper_email_migrations.py) follows
a similar subprocess pattern but sources work from the DB table instead.
=============================================================================
"""

"""Bulk-run migrate_account.py over a CSV (from;to format).

For each row, runs `python3 migrate_account.py --from <from> --to <to> -c` as a
subprocess, captures stdout/stderr to a log file, and continues even on failure.
Use --skip N to resume after a partial run.

Notes:
  - Stdin is connected to /dev/null; if SEAFILE_AUTH_TOKEN is expired and the
    child would interactively prompt, it will fail fast instead of hanging.
    Refresh the token by running migrate_account.py once manually first.
"""

import argparse
import csv
import os
import subprocess
import sys
from datetime import datetime


def read_csv(csv_path):
    """Yield (from_email, to_email). Auto-detects ',' vs ';' delimiter; skips header."""
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        delim = ";" if sample.count(";") >= sample.count(",") else ","
        reader = csv.reader(f, delimiter=delim)
        for i, row in enumerate(reader):
            if not row or not row[0].strip():
                continue
            first = row[0].strip()
            if i == 0 and "@" not in first:
                continue
            from_email = first
            to_email = row[1].strip() if len(row) > 1 else ""
            if not to_email:
                continue
            yield from_email, to_email


def main():
    parser = argparse.ArgumentParser(
        description="Bulk-run migrate_account.py over a CSV (from;to)."
    )
    parser.add_argument("csv_path", help="CSV with from;to columns (header optional)")
    parser.add_argument(
        "--log", default=None,
        help="Log file path (default: bulk_migrate_<timestamp>.log next to this script)",
    )
    parser.add_argument(
        "--skip", type=int, default=0,
        help="Skip the first N rows (for resuming after a failure)",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--no-create", action="store_true",
        help="Do NOT pass -c to migrate_account.py (target users must already exist)",
    )
    args = parser.parse_args()

    rows = list(read_csv(args.csv_path))
    total = len(rows)
    if args.skip:
        rows = rows[args.skip:]
    if not rows:
        print("No rows to process.")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = args.log or os.path.join(
        script_dir,
        f"bulk_migrate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    )
    migrate_script = os.path.join(script_dir, "migrate_account.py")

    print(f"\nWill migrate {len(rows)} user(s) from {args.csv_path}"
          f"{f' (skipping first {args.skip} of {total})' if args.skip else ''}:")
    for from_email, to_email in rows:
        print(f"  {from_email} -> {to_email}")
    print(f"Log: {log_path}")
    if not args.yes:
        if input("\nProceed? [y/N] ").strip().lower() != "y":
            print("Aborted.")
            sys.exit(0)

    ok = 0
    failed = []
    cmd_base = ["python3", migrate_script]
    if not args.no_create:
        cmd_base_suffix = ["-c"]
    else:
        cmd_base_suffix = []

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n===== bulk_migrate started at {datetime.now().isoformat()} =====\n")
        log.write(f"Source: {args.csv_path} ({len(rows)} rows)\n\n")
        log.flush()
        for idx, (from_email, to_email) in enumerate(rows, start=1):
            banner = f"\n----- [{idx}/{len(rows)}] {from_email} -> {to_email} -----\n"
            print(banner, end="")
            log.write(banner)
            log.flush()
            cmd = cmd_base + ["--from", from_email, "--to", to_email] + cmd_base_suffix
            try:
                proc = subprocess.run(
                    cmd,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            except Exception as e:
                msg = f"  Exception running subprocess: {e}\n"
                print(msg, end="")
                log.write(msg)
                log.flush()
                failed.append(from_email)
                continue
            print(proc.stdout, end="")
            log.write(proc.stdout)
            log.flush()
            if proc.returncode == 0:
                ok += 1
            else:
                failed.append(from_email)
                tail = f"  [exit code {proc.returncode}]\n"
                print(tail, end="")
                log.write(tail)
                log.flush()

        summary = (f"\n===== Summary: ok={ok}, failed={len(failed)}, "
                   f"total={len(rows)} =====\n")
        if failed:
            summary += "Failed: " + ", ".join(failed) + "\n"
        print(summary, end="")
        log.write(summary)

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
