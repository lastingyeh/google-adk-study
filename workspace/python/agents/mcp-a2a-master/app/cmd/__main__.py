"""Module entrypoint for `app.cmd` package.

Provides a small dispatcher to run either the interactive A2A CLI (`cmd.py`)
or the new `tree` utility.
"""
import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog='app.cmd', description='CMD utilities')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('chat', help='Run interactive A2A chat CLI')
    sub.add_parser('tree', help='Print project tree')

    parsed, rest = parser.parse_known_args(argv)

    if parsed.command == 'chat':
        # Run existing async CLI
        import asyncio
        from . import cmd as chat_cmd

        asyncio.run(chat_cmd.cli())
    elif parsed.command == 'tree':
        from . import tree as tree_mod
        sys.exit(tree_mod.main(rest))
    else:
        parser.print_help()


if __name__ == '__main__':
    raise SystemExit(main())
