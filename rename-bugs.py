#!/usr/bin/env python

import argparse
import os.path

import bugzilla
from rich.console import Console
from rich.theme import Theme


def mark_red(s: str):
    return f"[red]{s}[/red]"


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("-p", "--pretend",
                      action="store_true",
                      help="Print summary changes without applying them")
    argp.add_argument("old",
                      help="String to replace (old package name)")
    argp.add_argument("new",
                      help="New value (new package name)")
    args = argp.parse_args()

    token_file = os.path.expanduser('~/.bugz_token')
    try:
        with open(token_file, 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        argp.error("Put bugzilla API key into ~/.bugz_token")

    bz = bugzilla.Bugzilla("https://bugs.gentoo.org", api_key=token)
    console = Console(highlight=False,
                      theme=Theme({"bugno": "bright_cyan",
                                   "old": "bright_red",
                                   "new": "bright_green",
                                   }))

    search = bz.build_query(short_desc=args.old,
                            status=["UNCONFIRMED", "CONFIRMED", "IN_PROGRESS"])
    for bug in bz.query(search):
        old_color = f"[old]{args.old}[/old]"
        new_color = f"[new]{args.new}[/new]"
        console.print(f"[bugno]#{bug.id}[/bugno] - "
                      f"{bug.summary.replace(args.old, old_color)}")
        new_summary = bug.summary.replace(args.old, args.new)
        console.print(f"{' ' * len(str(bug.id))}  > "
                      f"{new_summary.replace(args.new, new_color)}")
        if not args.pretend:
            update = bz.build_update(summary=new_summary)
            bz.update_bugs([bug.id], update)


if __name__ == "__main__":
    main()
