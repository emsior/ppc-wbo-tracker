# AGENTS.md — ppc-wbo-tracker

Instrukcje dla agentów AI pracujących w tym repozytorium. Zasady wkładu dla ludzi: `CONTRIBUTING.md`.

## Czym jest
Statyczny tracker Wałbrzyskiego Budżetu Obywatelskiego: projekty na kartach do głosowania, koszty, oficjalne wyniki, statystyki frekwencji,
archiwum edycji (2020 → bieżąca) i kuratorowane, datowane dowody realizacji zwycięskich projektów. Same fakty z oficjalnej platformy
(`wbo.walbrzych.eu`, PORTO ALEGRE / MediaPark). Zero opisów i zdjęć projektów, zero opinii, zero danych osobowych.
Stos: Python 3.12, `requests` + `truststore`, `beautifulsoup4`; strona `docs/index.html` bez JS; dane `data/wbo.json`, `data/wbo_projects.csv`,
`data/realization.json` (ręcznie kuratorowane: każdy wpis ma `status`, `evidence[{date,title,url}]`, `checked_on`, `checked_how`).

## Komendy
```
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest                      # testy na syntetycznych fixture'ach (tests/fixtures.py), bez sieci
ruff check . ; ruff format --check . ; python -m mypy
wbo-tracker scrape          # pobiera platformę do data/wbo.json (cache data/raw, 1 s przerwy, UA z kontaktem)
wbo-tracker build           # data/*.json -> docs/index.html + data/wbo_projects.csv
wbo-tracker all
```

## Stan i gałęzie
`main` = aktualny stan: 7 edycji (2020–2027, bez 2024), 115 projektów; wyniki edycji 2027 dodane 18.10.2026.
27 z 32 zwycięzców sprawdzonych jednolitą procedurą (02.10.2026); pięciu zwycięzców edycji 2027 czeka na sprawdzenie.
Strona to GitHub Pages z `/docs` na `main` — każdy push na `main` zmienia stronę publiczną, więc push tylko po słowie właściciela.

## Reguły tego repo
- Dane tylko z oficjalnej platformy i publicznych, datowanych źródeł (BIP, um.walbrzych.pl, media lokalne). Opisy i zdjęcia projektów są chronione regulaminem platformy — nie kopiować.
- `realization.json`: status zmienia się wyłącznie z nowym datowanym źródłem; brak źródła = `brak_informacji` z `checked_on`. Wszystkich zwycięzców sprawdza się tą samą ścieżką (bez wyjątków „bo wiem”).
- Każda zmiana parsera dostaje test regresji w `tests/test_parse.py`; każda zmiana renderera — w `tests/test_build.py`.
- Nie obchodzić TLS/robots inaczej niż `truststore`; nie zwiększać tempa zapytań.
- Porównania kosztów między edycjami tylko przy porównywalnym zakresie (nota w szablonie zostaje).

## Następna sesja
1. `git status` (tree czysty), potem pytest / ruff / mypy — wszystko zielone, zanim cokolwiek ruszysz.
2. Jeśli są uwagi z review: wdrożyć z testami, wpis w `CHANGELOG.md` [Unreleased], commit po ścieżkach.
3. Nic więcej bez słowa właściciela (w tym push na `main`).
