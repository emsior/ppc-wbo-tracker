"""Collect the dataset: every edition's ballot list, official results and voting statistics."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from wbo_tracker.http import Fetcher
from wbo_tracker.model import Dataset, Edition
from wbo_tracker.parse import (
    parse_editions,
    parse_projects,
    parse_results,
    parse_schedule,
    parse_site_year,
    parse_stats,
)

log = logging.getLogger(__name__)

SOURCE_NAME = "Wałbrzyski Budżet Obywatelski — oficjalna platforma Urzędu Miejskiego w Wałbrzychu"
PLATFORM = "PORTO ALEGRE (MediaPark)"
SCHEDULE_PATH = "/wszystko-o-budzecie/harmonogram,32"


def scrape_current_edition(fetcher: Fetcher) -> Edition:
    """The edition currently served at the site root (ballot list + results if published)."""
    list_html = fetcher.get("/projekty") or ""
    year = parse_site_year(list_html) or datetime.now(tz=UTC).year
    edition = Edition(year=year, site_id=None, current=True)
    edition.projects = parse_projects(list_html)
    edition.sources["projects"] = f"{fetcher.base_url}/projekty"

    results_html = fetcher.get("/wyniki")
    if results_html:
        edition.results = parse_results(results_html)
        edition.stats = parse_stats(results_html)
        edition.sources["results"] = f"{fetcher.base_url}/wyniki"
    else:
        log.info("current edition: results not published yet (404)")

    schedule_html = fetcher.get(SCHEDULE_PATH)
    if schedule_html:
        edition.schedule = parse_schedule(schedule_html)
        edition.sources["schedule"] = f"{fetcher.base_url}{SCHEDULE_PATH}"
    return edition


def scrape_past_edition(fetcher: Fetcher, year: int, site_id: int) -> Edition:
    base = f"/poprzednie-edycje/{site_id}"
    edition = Edition(year=year, site_id=site_id, current=False)
    list_html = fetcher.get(f"{base}/projekty")
    if list_html:
        edition.projects = parse_projects(list_html)
        edition.sources["projects"] = f"{fetcher.base_url}{base}/projekty"
    results_html = fetcher.get(f"{base}/wyniki")
    if results_html:
        edition.results = parse_results(results_html)
        edition.stats = parse_stats(results_html)
        edition.sources["results"] = f"{fetcher.base_url}{base}/wyniki"
    return edition


def scrape_all(fetcher: Fetcher) -> Dataset:
    dataset = Dataset(
        generated_at=datetime.now(tz=UTC).replace(microsecond=0).isoformat(),
        source_name=SOURCE_NAME,
        source_url=fetcher.base_url,
        platform=PLATFORM,
    )
    dataset.editions.append(scrape_current_edition(fetcher))
    archive_html = fetcher.get("/poprzednie-edycje") or ""
    for year, site_id in parse_editions(archive_html):
        log.info("edition %s (site id %s)", year, site_id)
        dataset.editions.append(scrape_past_edition(fetcher, year, site_id))
    dataset.editions.sort(key=lambda e: e.year, reverse=True)
    return dataset
