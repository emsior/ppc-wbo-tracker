# AGENTS.md — ppc-wbo-tracker

Zasady globalne (role AI, rama 02.10, OPSEC, git) są w `~/.Codex/AGENTS.md` i `workspace\STACK.md` — nie powielać, nie nadpisywać.

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
`main` = szkielet (ef65633). Cała praca z 02.10 jest na `Codex/wbo-tracker-v0` (7 edycji, 115 projektów, 27/27 zwycięzców sprawdzonych
jednolitą procedurą). Repo jest **niepubliczne** — publikacja (gh repo create, push, Pages z `/docs`) tylko po słowie właściciela.
Review Codexa zamówiony w `workspace\.handoff\DO_CODEX.md` (blok 8); odpowiedź przyjdzie do `.handoff\DO_CLAUDE.md`.

## Reguły tego repo
- Dane tylko z oficjalnej platformy i publicznych, datowanych źródeł (BIP, um.walbrzych.pl, media lokalne). Opisy i zdjęcia projektów są chronione regulaminem platformy — nie kopiować.
- `realization.json`: status zmienia się wyłącznie z nowym datowanym źródłem; brak źródła = `brak_informacji` z `checked_on`. Wszystkich zwycięzców sprawdza się tą samą ścieżką (bez wyjątków „bo wiem”).
- Każda zmiana parsera dostaje test regresji w `tests/test_parse.py`; każda zmiana renderera — w `tests/test_build.py`.
- Nie obchodzić TLS/robots inaczej niż `truststore`; nie zwiększać tempa zapytań.
- Porównania kosztów między edycjami tylko przy porównywalnym zakresie (nota w szablonie zostaje).

## Następna sesja
1. `git status` (tree czysty), potem pytest / ruff / mypy — wszystko zielone, zanim cokolwiek ruszysz.
2. Jeśli w `workspace\.handoff\DO_CLAUDE.md` jest review Codexa o trackerze: wdrożyć uwagi z testami, wpis w `CHANGELOG.md` [Unreleased], commit po ścieżkach.
3. Po ogłoszeniu wyników edycji 2027 (miasto: do 15.10.2026): `wbo-tracker all`, sprawdzić w `data/wbo.json`, że edycja 2027 ma `results` i `stats`, obejrzeć `docs/index.html`, commit „data: WBO 2027 results”.
4. Nic więcej. Publikacja i nazwa docelowa repo = decyzja właściciela.
