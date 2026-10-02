"""Pure parsers for the PORTO ALEGRE (MediaPark) participatory-budget platform pages.

Every function takes HTML as text and returns plain data. No network, no side effects,
so everything here is unit-testable with small synthetic fixtures.
"""

from __future__ import annotations

import re
from datetime import date

from bs4 import BeautifulSoup, Tag

from wbo_tracker.model import Project, Result, ScheduleStep, Stats

_NBSP = "\u00a0"
_PL_MONTHS = {
    "stycznia": 1,
    "lutego": 2,
    "marca": 3,
    "kwietnia": 4,
    "maja": 5,
    "czerwca": 6,
    "lipca": 7,
    "sierpnia": 8,
    "września": 9,
    "października": 10,
    "listopada": 11,
    "grudnia": 12,
}


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _text(node: Tag | None) -> str:
    if node is None:
        return ""
    return node.get_text(" ", strip=True).replace(_NBSP, " ")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace(_NBSP, " ")).strip()


def parse_int(text: str | None) -> int | None:
    """'1 438' / '4&nbsp;928' / '12.' -> 1438 / 4928 / 12. None when no digits."""
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text.replace(_NBSP, " "))
    return int(digits) if digits else None


def parse_cost(text: str | None) -> float | None:
    """'897 340,05 zł' -> 897340.05, '1 009 000 zł' -> 1009000.0."""
    if not text:
        return None
    cleaned = text.replace(_NBSP, " ")
    match = re.search(r"(\d{1,3}(?:[ .]\d{3})*|\d+)(?:,(\d{1,2}))?", cleaned)
    if not match:
        return None
    whole = re.sub(r"[ .]", "", match.group(1))
    frac = match.group(2) or "0"
    return float(f"{whole}.{frac}")


def parse_pl_datetime(text: str | None) -> str | None:
    """'Poniedziałek, 1 września 2025 00:01' -> '2025-09-01T00:01'."""
    if not text:
        return None
    match = re.search(
        r"(\d{1,2})\s+([a-ząćęłńóśźż]+)\s+(\d{4})(?:\s*,?\s*(\d{1,2}):(\d{2}))?", text.lower()
    )
    if not match:
        return None
    month = _PL_MONTHS.get(match.group(2))
    if month is None:
        return None
    day, year = int(match.group(1)), int(match.group(3))
    stamp = f"{year:04d}-{month:02d}-{day:02d}"
    if match.group(4):
        stamp += f"T{int(match.group(4)):02d}:{match.group(5)}"
    return stamp


def parse_pl_date(text: str | None) -> str | None:
    """'27.04.2026 r.' -> '2026-04-27'."""
    if not text:
        return None
    match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
    if not match:
        return None
    try:
        return date(int(match.group(3)), int(match.group(2)), int(match.group(1))).isoformat()
    except ValueError:
        return None


def project_id_from_url(url: str | None) -> int | None:
    if not url:
        return None
    match = re.search(r"/projekt/(\d+)", url)
    return int(match.group(1)) if match else None


def parse_site_year(html: str) -> int | None:
    """Edition name of the site, e.g. 'Wałbrzyski Budżet Obywatelski 2027'.

    The <title> of sub-pages lacks the year, so the logo alt / meta keywords / any
    'Obywatelski 2027' text are searched as fallbacks."""
    soup = _soup(html)
    candidates = [_text(soup.find("title"))]
    candidates += [str(img.get("alt", "")) for img in soup.select("img[alt]")]
    keywords = soup.select_one('meta[name="keywords"]')
    candidates.append(str(keywords.get("content", "")) if keywords else "")
    candidates.append(html)
    for text in candidates:
        match = re.search(r"[Oo]bywatelski\s*(20\d{2})", text) or (
            re.search(r"(20\d{2})", text) if text is candidates[0] else None
        )
        if match:
            return int(match.group(1))
    return None


def parse_project_count(html: str) -> int | None:
    match = re.search(r"Liczba projektów:\s*(\d+)", html)
    return int(match.group(1)) if match else None


def parse_editions(html: str) -> list[tuple[int, int]]:
    """'/poprzednie-edycje' menu -> [(year, site_id), ...] newest first as listed."""
    # The live page never closes its <li class="non-click"> tags, so html.parser nests each
    # edition inside the previous one. Walk labels in document order instead of the tree.
    editions: list[tuple[int, int]] = []
    link_re = re.compile(r"/poprzednie-edycje/(\d+)(?:/|$)")
    for label in _soup(html).select("span.alike"):
        year_match = re.search(r"(20\d{2})", _text(label))
        link = label.find_next("a", href=link_re)
        href = str(link.get("href", "")) if isinstance(link, Tag) else ""
        id_match = link_re.search(href)
        if year_match and id_match:
            editions.append((int(year_match.group(1)), int(id_match.group(1))))
    return editions


def parse_projects(html: str) -> list[Project]:
    """Ballot list page ('/projekty' or '/poprzednie-edycje/{id}/projekty')."""
    projects: list[Project] = []
    for card in _soup(html).select(".project-item-content"):
        link = card.select_one('a[href*="/projekt/"]')
        url = str(link.get("href", "")) if link else ""
        pid = project_id_from_url(url)
        if pid is None:
            continue
        number = parse_int(_text(card.select_one(".project-nr")))
        title_node = card.select_one("h2.title")
        title = _norm(_text(title_node))
        if number is not None:
            title = re.sub(r"^\d+\.\s*", "", title)
        area_text = _text(card.select_one(".location"))
        area = _norm(re.sub(r"^Obszar:\s*", "", area_text)) or None
        cost = None
        for p in card.select(".additional-info p"):
            if "koszt" in _text(p).lower():
                cost = parse_cost(_text(p))
        status = _norm(_text(card.select_one(".project-status"))).capitalize()
        projects.append(
            Project(
                id=pid, number=number, title=title, area=area, cost_pln=cost, status=status, url=url
            )
        )
    return projects


def parse_results(html: str) -> list[Result]:
    """Results page ('/poprzednie-edycje/{id}/wyniki' or '/wyniki')."""
    results: list[Result] = []
    for row in _soup(html).select(".result-row"):
        pid = parse_int(str(row.get("data-project-id", "")))
        if pid is None:
            link = row.select_one('a[href*="/projekt/"]')
            pid = project_id_from_url(str(link.get("href", "")) if link else None)
        if pid is None:
            continue
        status = _norm(_text(row.select_one(".details .status") or row.select_one(".status")))
        results.append(
            Result(
                id=pid,
                position=parse_int(_text(row.select_one(".vote-position"))),
                number=parse_int(_text(row.select_one(".project_nr, .project-nr"))),
                votes=parse_int(_text(row.select_one(".votes"))),
                status=status.capitalize(),
                cost_pln=parse_cost(_text(row.select_one(".price"))),
            )
        )
    return results


def _pair_numbers(block_text: str, label: str) -> int | None:
    """'Komputery 794 16,11% Urządzenia mobilne 4 134 83,89%' + 'Komputery' -> 794."""
    match = re.search(re.escape(label) + r"\s*([\d ]+?)\s*\d+(?:,\d+)?%", block_text)
    return parse_int(match.group(1)) if match else None


def _first_number(text: str) -> int | None:
    """First number group in free text: '1 234 (100%)' -> 1234, never 1234100."""
    match = re.search(r"\d[\d ]*", text.replace(_NBSP, " "))
    return parse_int(match.group(0)) if match else None


def _counters(block: Tag) -> list[int]:
    """Animated counters <span class="timer" data-to="4928">0</span>; percentages skipped."""
    values: list[int] = []
    for span in block.select("span.timer[data-to]"):
        raw = str(span.get("data-to", ""))
        if re.fullmatch(r"\d+", raw):
            values.append(int(raw))
    return values


def parse_stats(html: str) -> Stats | None:
    """Statistics tab of a results page. Returns None when the page has no stats section."""
    soup = _soup(html)
    blocks = soup.select(".info-graph")
    if not blocks:
        return None
    stats = Stats()
    for block in blocks:
        heading = _text(block.select_one("h3")).lower()
        body = _norm(block.get_text(" ", strip=True))
        body_wo_heading = _norm(body.replace(_text(block.select_one("h3")), "", 1))
        counters = _counters(block)
        if "osób głosujących" in heading:
            stats.voters = counters[0] if counters else _first_number(body_wo_heading)
        elif "oddanych głosów" in heading:
            stats.valid_votes = counters[0] if counters else _first_number(body_wo_heading)
        elif "komputery" in heading:
            stats.desktop_votes = counters[0] if counters else _pair_numbers(body, "Komputery")
            mobile_text = _pair_numbers(body, "Urządzenia mobilne")
            stats.mobile_votes = counters[1] if len(counters) > 1 else mobile_text
        elif "kobiety" in heading:
            stats.women = counters[0] if counters else _pair_numbers(body, "Kobiety")
            stats.men = counters[1] if len(counters) > 1 else _pair_numbers(body, "Mężczyźni")
        elif "pierwszy" in body.lower() and "ostatni" in body.lower():
            first = re.search(r"Pierwszy oddany głos\s*(.+?)\s*Ostatni", body)
            last = re.search(r"Ostatni oddany głos\s*(.+)$", body)
            stats.first_vote = parse_pl_datetime(first.group(1) if first else None)
            stats.last_vote = parse_pl_datetime(last.group(1) if last else None)
    return stats


def parse_schedule(html: str) -> list[ScheduleStep]:
    """Harmonogram page: numbered steps followed by 'od DD.MM.YYYY r. do DD.MM.YYYY r.'.

    Titles and dates may be split over several lines ('3. Analiza projektów /', 'Rozpatrzenie
    odwołań', 'od 29.06.2026 r.', 'do 31.07.2026 r.'), so lines are grouped per step first."""
    lines = [
        _norm(line) for line in _soup(html).get_text("\n", strip=True).splitlines() if line.strip()
    ]
    step_re = re.compile(r"^(\d{1,2})\.\s*(\S.*)$")
    date_pat = r"\d{1,2}\.\d{1,2}\.\d{4}"
    dates_re = re.compile(rf"(?:od\s*({date_pat})\s*r?\.?\s*)?\bdo\s*({date_pat})")
    groups: list[list[str]] = []
    for line in lines:
        step = step_re.match(line)
        if step:
            groups.append([step.group(2)])
        elif groups:
            groups[-1].append(line)
    steps: list[ScheduleStep] = []
    for parts in groups:
        joined = _norm(" ".join(parts))
        dates = dates_re.search(joined)
        if not dates:
            continue
        steps.append(
            ScheduleStep(
                name=joined[: dates.start()].strip(" :–-"),
                date_from=parse_pl_date(dates.group(1)),
                date_to=parse_pl_date(dates.group(2)),
            )
        )
    return steps
