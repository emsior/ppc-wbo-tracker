"""Command line: `wbo-tracker scrape | build | all`."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from wbo_tracker.build import build
from wbo_tracker.http import DEFAULT_BASE_URL, Fetcher
from wbo_tracker.scrape import scrape_all

DEFAULT_DATA = Path("data/wbo.json")
DEFAULT_REALIZATION = Path("data/realization.json")
DEFAULT_HTML = Path("docs/index.html")
DEFAULT_CSV = Path("data/wbo_projects.csv")
DEFAULT_CACHE = Path("data/raw")


def _scrape(args: argparse.Namespace) -> None:
    fetcher = Fetcher(
        base_url=args.base_url,
        delay_s=args.delay,
        cache_dir=None if args.no_cache else args.cache_dir,
    )
    dataset = scrape_all(fetcher)
    args.data.parent.mkdir(parents=True, exist_ok=True)
    args.data.write_text(
        json.dumps(dataset.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    editions = ", ".join(
        f"{e.year}: {len(e.projects)} proj./{len(e.results)} wyn." for e in dataset.editions
    )
    logging.info("saved %s (%d requests) — %s", args.data, fetcher.requests_made, editions)


def _build(args: argparse.Namespace) -> None:
    build(args.data, args.html, args.csv, args.realization)
    logging.info("built %s and %s", args.html, args.csv)


def _all(args: argparse.Namespace) -> None:
    _scrape(args)
    _build(args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wbo-tracker", description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    scrape_p = sub.add_parser(
        "scrape", help="download ballot lists, results and stats -> data/wbo.json"
    )
    scrape_p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    scrape_p.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    scrape_p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    scrape_p.add_argument("--no-cache", action="store_true", help="always hit the platform")
    scrape_p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    scrape_p.set_defaults(func=_scrape)

    build_p = sub.add_parser("build", help="render docs/index.html and data/wbo_projects.csv")
    build_p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    build_p.add_argument("--realization", type=Path, default=DEFAULT_REALIZATION)
    build_p.add_argument("--html", type=Path, default=DEFAULT_HTML)
    build_p.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    build_p.set_defaults(func=_build)

    all_p = sub.add_parser("all", help="scrape, then build")
    for p in (all_p,):
        p.add_argument("--base-url", default=DEFAULT_BASE_URL)
        p.add_argument("--delay", type=float, default=1.0)
        p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
        p.add_argument("--no-cache", action="store_true")
        p.add_argument("--data", type=Path, default=DEFAULT_DATA)
        p.add_argument("--realization", type=Path, default=DEFAULT_REALIZATION)
        p.add_argument("--html", type=Path, default=DEFAULT_HTML)
        p.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    all_p.set_defaults(func=_all)

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s"
    )
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
