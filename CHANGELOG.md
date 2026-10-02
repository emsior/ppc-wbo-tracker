# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions: [SemVer](https://semver.org/).

## [Unreleased]

### Fixed
- Parser hardening after an external code review (8 edge cases): dot thousands separators in
  costs, comma before time in Polish timestamps, calendar validation of `DD.MM.YYYY` dates,
  archive links without trailing slash, `project-nr`/`project_nr` class variants, statistics
  fallback no longer concatenates all numbers, schedule steps without a space after the number
  and with 1-digit day/month.

## [0.1.0] — 2026-10-02

### Added
- Scraper for the official WBO platform (ballot lists, results, voting statistics, schedule,
  archive of previous editions) with polite throttling, OS trust store TLS and git-ignored raw cache.
- Static site generator: `docs/index.html` (no JavaScript, dark-mode aware, accessible tables)
  and `data/wbo_projects.csv`.
- Curated `data/realization.json` for dated public evidence about winning projects.
- Test suite with synthetic fixtures, `ruff`, `mypy --strict`, GitHub Actions CI.
