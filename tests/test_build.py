import csv
import json
from pathlib import Path

from wbo_tracker import build


def _dataset() -> dict[str, object]:
    return {
        "generated_at": "2026-10-02T09:10:00+00:00",
        "source_name": "Platforma testowa",
        "source_url": "https://example.test",
        "platform": "PORTO ALEGRE (MediaPark)",
        "editions": [
            {
                "year": 2027,
                "site_id": None,
                "current": True,
                "projects": [
                    {
                        "id": 1,
                        "number": 1,
                        "title": "Ścieżka <b>rowerowa</b>",
                        "area": "Nowe Miasto",
                        "cost_pln": 1009000.0,
                        "status": "Wybrany do głosowania",
                        "url": "https://example.test/projekt/1",
                    }
                ],
                "results": [],
                "stats": None,
                "schedule": [
                    {"name": "Głosowanie", "date_from": "2026-09-01", "date_to": "2026-09-30"},
                    {
                        "name": "Oficjalne ogłoszenie wyników",
                        "date_from": None,
                        "date_to": "2026-10-15",
                    },
                ],
                "sources": {"projects": "https://example.test/projekty"},
            },
            {
                "year": 2026,
                "site_id": 11,
                "current": False,
                "projects": [
                    {
                        "id": 2,
                        "number": 7,
                        "title": "Strefa basketu",
                        "area": "Podzamcze",
                        "cost_pln": 900000.0,
                        "status": "Wybrany do realizacji",
                        "url": "https://example.test/projekt/2",
                    },
                    {
                        "id": 3,
                        "number": 1,
                        "title": "Bike park",
                        "area": "Nowe Miasto",
                        "cost_pln": 899365.0,
                        "status": "Wybrany do głosowania",
                        "url": "https://example.test/projekt/3",
                    },
                ],
                "results": [
                    {
                        "id": 2,
                        "position": 1,
                        "number": 7,
                        "votes": 1438,
                        "status": "Wybrany do realizacji",
                        "cost_pln": 900000.0,
                    },
                    {
                        "id": 3,
                        "position": 2,
                        "number": 1,
                        "votes": 225,
                        "status": "Niezakwalifikowany",
                        "cost_pln": 899365.0,
                    },
                ],
                "stats": {
                    "voters": 4928,
                    "valid_votes": 4928,
                    "desktop_votes": 794,
                    "mobile_votes": 4134,
                    "women": 2995,
                    "men": 1933,
                    "first_vote": "2025-09-01T00:01",
                    "last_vote": "2025-09-30T23:32",
                },
                "schedule": [],
                "sources": {
                    "projects": "https://example.test/poprzednie-edycje/11/projekty",
                    "results": "https://example.test/poprzednie-edycje/11/wyniki",
                },
            },
        ],
    }


def test_formatters() -> None:
    assert build.fmt_int(1009000) == "1 009 000"
    assert build.fmt_pln(897340.05) == "897 340,05 zł"
    assert build.fmt_pln(None) == "🚫"
    assert build.fmt_date("2025-09-01T00:01") == "01.09.2025 00:01"
    assert build.is_winner("Wybrany do realizacji") and not build.is_winner("Niezakwalifikowany")


def test_edition_view_joins_projects_and_results() -> None:
    view = build.edition_view(_dataset()["editions"][1])  # type: ignore[index]
    assert view.n_listed == 2 and view.n_winners == 1
    assert view.winners_cost == 900000.0
    assert view.voters == 4928
    assert [r["id"] for r in view.rows] == [2, 3]
    assert view.rows[0]["winner"] is True and view.rows[1]["votes"] == 225


def test_render_site_escapes_and_contains_sections() -> None:
    html = build.render_site(
        _dataset(),
        {
            2: {
                "project_id": 2,
                "status": "zrealizowany",
                "evidence": [
                    {
                        "date": "2026-05-01",
                        "title": "Otwarcie",
                        "url": "https://example.test/news/1",
                    }
                ],
                "note": "wspólna realizacja <dwóch> projektów",
            }
        },
    )
    assert "Ścieżka &lt;b&gt;rowerowa&lt;/b&gt;" in html
    assert "<b>rowerowa</b>" not in html
    assert 'id="edycja-2027"' in html and 'id="edycja-2026"' in html
    assert "Oficjalne ogłoszenie wyników: do 15.10.2026" in html
    assert "✅ zrealizowany (wg źródła)" in html and "https://example.test/news/1" in html
    assert "(wspólna realizacja &lt;dwóch&gt; projektów)" in html
    assert 'lang="pl"' in html


def test_write_csv(tmp_path: Path) -> None:
    out = tmp_path / "x.csv"
    n = build.write_csv(_dataset(), out)
    assert n == 3
    with out.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    assert rows[0]["edition_year"] == "2027"
    assert rows[1]["votes"] == "1438" and rows[1]["position"] == "1"
    assert rows[2]["cost_pln"] == "899365.00"


def test_build_end_to_end(tmp_path: Path) -> None:
    data = tmp_path / "wbo.json"
    data.write_text(json.dumps(_dataset(), ensure_ascii=False), encoding="utf-8")
    html_out = tmp_path / "docs" / "index.html"
    csv_out = tmp_path / "wbo.csv"
    build.build(data, html_out, csv_out, None)
    assert html_out.exists() and csv_out.exists()
    assert "WBO Tracker" in html_out.read_text(encoding="utf-8")
