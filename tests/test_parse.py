from tests.fixtures import EDITIONS_HTML, PROJECTS_HTML, RESULTS_HTML, SCHEDULE_HTML
from wbo_tracker import parse


def test_parse_int_and_cost() -> None:
    assert parse.parse_int("1 438") == 1438
    assert parse.parse_int("4 928") == 4928
    assert parse.parse_int("12.") == 12
    assert parse.parse_int("") is None
    assert parse.parse_cost("897 340,05 zł") == 897340.05
    assert parse.parse_cost("1 009 000 zł") == 1009000.0
    assert parse.parse_cost("brak") is None


def test_parse_pl_datetime_and_date() -> None:
    assert parse.parse_pl_datetime("Poniedziałek, 1 września 2025 00:01") == "2025-09-01T00:01"
    assert parse.parse_pl_datetime("30 września 2025") == "2025-09-30"
    assert parse.parse_pl_datetime("kiedyś") is None
    assert parse.parse_pl_date("27.04.2026 r.") == "2026-04-27"


def test_parse_site_year_and_count() -> None:
    assert parse.parse_site_year(PROJECTS_HTML) == 2027
    assert parse.parse_project_count(PROJECTS_HTML) == 2
    assert parse.parse_site_year("<html><title>bez roku</title></html>") is None
    no_year_title = (
        "<html><head><title>Lista projektów - BO</title>"
        '<meta name="keywords" content="budżet obywatelski 2027"></head>'
        '<body><img alt="Testowy Budżet Obywatelski 2027"></body></html>'
    )
    assert parse.parse_site_year(no_year_title) == 2027


def test_parse_projects() -> None:
    projects = parse.parse_projects(PROJECTS_HTML)
    assert [p.id for p in projects] == [34572, 29485]
    first, second = projects
    assert first.number == 1
    assert first.title == "Ścieżka rowerowa nad rzeką"
    assert first.area == "Nowe Miasto, Stary Zdrój"
    assert first.cost_pln == 1009000.0
    assert first.status == "Wybrany do głosowania"
    assert first.url == "https://example.test/projekt/34572"
    assert second.area is None
    assert second.cost_pln == 897340.05
    assert second.status == "Wybrany do realizacji"


def test_parse_results() -> None:
    results = parse.parse_results(RESULTS_HTML)
    assert [r.id for r in results] == [29485, 34572]
    winner, other = results
    assert (winner.position, winner.number, winner.votes) == (1, 2, 1438)
    assert winner.status == "Wybrany do realizacji"
    assert winner.cost_pln == 900000.0
    assert (other.position, other.votes, other.status) == (2, 226, "Niezakwalifikowany")


def test_parse_stats() -> None:
    stats = parse.parse_stats(RESULTS_HTML)
    assert stats is not None
    assert stats.voters == 4928
    assert stats.valid_votes == 4928
    assert (stats.desktop_votes, stats.mobile_votes) == (794, 4134)
    assert (stats.women, stats.men) == (2995, 1933)
    assert stats.first_vote == "2025-09-01T00:01"
    assert stats.last_vote == "2025-09-30T23:32"
    assert parse.parse_stats("<html><body>nic</body></html>") is None


def test_parse_editions() -> None:
    assert parse.parse_editions(EDITIONS_HTML) == [(2026, 11), (2025, 10)]


def test_parse_schedule() -> None:
    steps = parse.parse_schedule(SCHEDULE_HTML)
    assert [s.name for s in steps] == [
        "Zgłaszanie projektów do Budżetu Obywatelskiego",
        "Analiza projektów / Rozpatrzenie odwołań",
        "Głosowanie",
        "Oficjalne ogłoszenie wyników",
    ]
    assert steps[0].date_from == "2026-04-27" and steps[0].date_to == "2026-05-15"
    assert steps[1].date_from == "2026-06-29" and steps[1].date_to == "2026-07-31"
    assert steps[3].date_from is None and steps[3].date_to == "2026-10-15"
