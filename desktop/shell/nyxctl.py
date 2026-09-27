#!/usr/bin/env python3
"""NyxOS CLI Shell — nyxctl

A terminal-first command interface for NyxOS core.
GUI will be added later on top of the same API.
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database.db import Database
from core.events.bus import EventBus
from core.api.api import CoreAPI


def build_api():
    db = Database()
    bus = EventBus(db=db)
    return CoreAPI(db, bus)


def cmd_case_create(args):
    api = build_api()
    print(json.dumps(api.case_create({"name": args.name,
                                       "description": args.desc or ""}), indent=2))


def cmd_case_list(args):
    api = build_api()
    print(json.dumps(api.case_list(), indent=2))


def cmd_asset_add(args):
    api = build_api()
    print(json.dumps(api.asset_add({
        "case_id": args.case,
        "type": args.type,
        "identifier": args.identifier,
    }), indent=2))


def cmd_asset_list(args):
    api = build_api()
    print(json.dumps(api.asset_list({"case_id": args.case}), indent=2))


def cmd_ping(args):
    api = build_api()
    print(json.dumps(api.ping(), indent=2))


def main():
    p = argparse.ArgumentParser(prog="nyxctl", description="NyxOS CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping").set_defaults(func=cmd_ping)

    pc = sub.add_parser("case-create")
    pc.add_argument("name")
    pc.add_argument("--desc", default="")
    pc.set_defaults(func=cmd_case_create)

    sub.add_parser("case-list").set_defaults(func=cmd_case_list)

    pa = sub.add_parser("asset-add")
    pa.add_argument("--case", type=int, required=True)
    pa.add_argument("--type", required=True)
    pa.add_argument("--identifier", required=True)
    pa.set_defaults(func=cmd_asset_add)

    pal = sub.add_parser("asset-list")
    pal.add_argument("--case", type=int, required=True)
    pal.set_defaults(func=cmd_asset_list)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
