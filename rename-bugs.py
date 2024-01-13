#!/usr/bin/env python

import argparse
import os.path
import re

import bugzilla
from rich.console import Console
from rich.theme import Theme


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
        pkg_re = re.compile(
            f"(^|[^\\w+_-])({args.old})(?!([\\w+_]|-[a-zA-Z]))")
        new_summary = pkg_re.sub(f"\\1{args.new}", bug.summary)
        if new_summary == bug.summary:
            continue

        console.print(
            f"[bugno]#{bug.id}[/bugno] - "
            f"{pkg_re.sub(r'\1[old]\2[/old]', bug.summary)}")
        console.print(
            f"{' ' * len(str(bug.id))}  + "
            f"{pkg_re.sub(f'\\1[new]{args.new}[/new]', bug.summary)}")

        if not args.pretend:
            update = bz.build_update(summary=new_summary)
            bz.update_bugs([bug.id], update)


if __name__ == "__main__":
    main()
