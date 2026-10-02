# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions: [SemVer](https://semver.org/).

## [Unreleased]

## [0.1.0] — 2026-10-02

### Added
- Scraper for the official WBO platform (ballot lists, results, voting statistics, schedule,
  archive of previous editions) with polite throttling, OS trust store TLS and git-ignored raw cache.
- Static site generator: `docs/index.html` (no JavaScript, dark-mode aware, accessible tables)
  and `data/wbo_projects.csv`.
- Curated `data/realization.json` for dated public evidence about winning projects.
- Test suite with synthetic fixtures, `ruff`, `mypy --strict`, GitHub Actions CI.
