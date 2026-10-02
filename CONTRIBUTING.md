# Contributing

## Adding evidence about a winning project (most welcome contribution)

Edit `data/realization.json` and add one entry per project:

```json
{
  "project_id": 29485,
  "edition_year": 2026,
  "status": "zrealizowany",
  "evidence": [
    {"date": "2026-06-12", "title": "Otwarcie strefy basketu — komunikat UM Wałbrzych", "url": "https://..."}
  ],
  "note": ""
}
```

Rules:

* `project_id` is the number from the project URL on the official platform (`/projekt/<id>`).
* `status` is one of `zrealizowany`, `w_trakcie`, `brak_informacji`.
* Every entry needs at least one **public, dated** source: city/BIP announcement, tender notice,
  council resolution, local press. No screenshots of private messages, no hearsay.
* Neutral wording only. We record what a source says and when; we do not judge.
* Then run `wbo-tracker build` and open `docs/index.html` to check the row.

## Code changes

1. `pip install -e ".[dev]"`
2. Make the change with a test (parsers are tested on synthetic fixtures in `tests/fixtures.py`).
3. `ruff check . && ruff format --check . && mypy && pytest` must be green.
4. Commit with explicit paths (`git add <files>`), open a pull request against `main`.

## Reporting a data error

Open an issue with the project URL on the official platform and the value you believe is wrong.
The official platform is always the source of truth.
