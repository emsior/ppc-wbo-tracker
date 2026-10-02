# ppc-wbo-tracker

**Facts-only, static tracker of the Wałbrzych participatory budget (Wałbrzyski Budżet Obywatelski, WBO).**
Projects on the ballot, planned costs, official voting results, turnout statistics and the full
history of editions (2020 → current) — every number links back to its page on the official
platform. No project descriptions, no photos, no opinions.

> Polish summary / streszczenie po polsku: [niżej](#po-polsku).

## What it does

| Step | Command | Output |
|---|---|---|
| Collect | `wbo-tracker scrape` | `data/wbo.json` — one JSON with every edition: ballot list, results, stats, schedule, source URLs |
| Render | `wbo-tracker build` | `docs/index.html` (static page, no JavaScript) and `data/wbo_projects.csv` (one row per project) |
| Both | `wbo-tracker all` | — |

The page shows: a summary of all editions, the current edition with its official schedule,
per-edition result tables (place, votes, cost, status), a per-district breakdown, and a
section **"What is publicly known about the winners"** — the official platform shows the same
status ("selected for realisation") for a 2020 winner and a 2026 winner, so this tracker keeps a
curated, dated list of public evidence (`data/realization.json`). An empty entry means
*no information in this dataset*, never *not realised*.

## Data policy (why the repository holds only facts)

* Source: the official platform run by the City of Wałbrzych (software: PORTO ALEGRE by MediaPark).
  Only facts are stored: project number, title (as identifier), district, planned cost, status,
  position, vote count, voting statistics, schedule dates, source URLs.
* Project descriptions, attachments and photos belong to their authors (platform terms) and are
  **never** copied. Raw HTML is cached under `data/raw/` for reproducibility but is git-ignored.
* No personal data of applicants. No ratings, no commentary — the tracker is neutral; in case of
  discrepancy the official platform is the source of truth.
* Polite crawling: one session, honest `User-Agent`, 1 s between requests, ~15 requests per run.
* TLS: the platform serves an incomplete certificate chain, so verification goes through the OS
  trust store (`truststore`). Verification is never disabled.

## Install and run

```bash
python -m venv .venv && . .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
wbo-tracker all                                      # scrape + build
python -m http.server -d docs 8000                   # open http://localhost:8000
```

Quality gates (all must be green before a commit):

```bash
ruff check . && ruff format --check . && mypy && pytest
```

Tests use small synthetic HTML fixtures (no network, no platform content).

## Repository layout

```
src/wbo_tracker/   parse.py (pure parsers) · http.py (polite fetcher) · scrape.py · build.py · templates/
data/              wbo.json (dataset) · wbo_projects.csv · realization.json (curated evidence) · raw/ (ignored)
docs/              index.html — publishable as-is (GitHub Pages: branch main, folder /docs)
tests/             pytest, fixtures.py
```

## Contributing evidence about realised projects

See [CONTRIBUTING.md](CONTRIBUTING.md): one JSON entry per project with a dated public source.

## License

MIT — see [LICENSE](LICENSE). Data on the page remains subject to the rules of its public source.

---

## Po polsku

**ppc-wbo-tracker** to niezależne, neutralne zestawienie faktów o Wałbrzyskim Budżecie
Obywatelskim: projekty na listach do głosowania, planowane koszty, oficjalne wyniki, frekwencja
i historia edycji od 2020 r. Każda liczba prowadzi do strony źródłowej na oficjalnej platformie
`wbo.walbrzych.eu`. Nie kopiujemy opisów projektów, załączników ani zdjęć (należą do autorów),
nie publikujemy danych osobowych wnioskodawców i niczego nie oceniamy.

Dodatkowo tabela **„Co wiadomo o realizacji zwycięskich projektów”** zbiera wyłącznie publiczne,
datowane informacje o losach projektów po głosowaniu (plik `data/realization.json`). Brak wpisu
znaczy „brak informacji w tym zestawieniu”, nie „niezrealizowany”.

Uruchomienie: `pip install -e ".[dev]"`, potem `wbo-tracker all` → `docs/index.html`.
Błędy w danych: zakładka *Issues* w tym repozytorium.

Proch PC (PPC) · Wałbrzych
