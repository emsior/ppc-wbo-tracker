"""Turn the dataset into a static site (docs/index.html) and a flat CSV. No JavaScript needed."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from html import escape
from importlib.resources import files
from pathlib import Path
from string import Template
from typing import Any

WINNER_STATUS_PREFIX = "wybrany do realizacji"
REALIZATION_LABELS = {
    "zrealizowany": "✅ zrealizowany (wg źródła)",
    "w_trakcie": "🔧 w trakcie (wg źródła)",
    "brak_informacji": "🚫 brak publicznej informacji w tym zestawieniu",
}


def fmt_int(value: int | float | None) -> str:
    if value is None:
        return "🚫"
    return f"{int(round(value)):,}".replace(",", " ")


def fmt_pln(value: float | None) -> str:
    if value is None:
        return "🚫"
    if float(value).is_integer():
        return f"{fmt_int(value)} zł"
    whole, frac = f"{value:.2f}".split(".")
    return f"{fmt_int(int(whole))},{frac} zł"


def fmt_date(value: str | None) -> str:
    if not value:
        return "🚫"
    date, _, time_part = value.partition("T")
    y, m, d = date.split("-")
    return f"{d}.{m}.{y}" + (f" {time_part}" if time_part else "")


def is_winner(status: str | None) -> bool:
    return (status or "").strip().lower().startswith(WINNER_STATUS_PREFIX)


@dataclass
class EditionView:
    year: int
    current: bool
    n_listed: int
    n_winners: int
    winners_cost: float
    voters: int | None
    valid_votes: int | None
    first_vote: str | None
    last_vote: str | None
    rows: list[dict[str, Any]]
    sources: dict[str, str]
    schedule: list[dict[str, Any]]
    stats: dict[str, Any] | None


def _edition_rows(edition: dict[str, Any]) -> list[dict[str, Any]]:
    projects = {p["id"]: p for p in edition.get("projects", [])}
    results = {r["id"]: r for r in edition.get("results", [])}
    rows: list[dict[str, Any]] = []
    for pid in projects.keys() | results.keys():
        p = projects.get(pid, {})
        r = results.get(pid, {})
        status = r.get("status") or p.get("status") or "🚫"
        rows.append(
            {
                "id": pid,
                "number": r.get("number") or p.get("number"),
                "title": p.get("title") or f"projekt {pid}",
                "area": p.get("area"),
                "cost_pln": p.get("cost_pln")
                if p.get("cost_pln") is not None
                else r.get("cost_pln"),
                "status": status,
                "position": r.get("position"),
                "votes": r.get("votes"),
                "url": p.get("url") or f"https://wbo.walbrzych.eu/projekt/{pid}",
                "winner": is_winner(status),
            }
        )
    rows.sort(key=lambda x: (x["position"] is None, x["position"] or 0, x["number"] or 0))
    return rows


def edition_view(edition: dict[str, Any]) -> EditionView:
    rows = _edition_rows(edition)
    winners = [r for r in rows if r["winner"]]
    stats = edition.get("stats") or None
    return EditionView(
        year=edition["year"],
        current=bool(edition.get("current")),
        n_listed=len(edition.get("projects", [])) or len(rows),
        n_winners=len(winners),
        winners_cost=sum(r["cost_pln"] or 0.0 for r in winners),
        voters=(stats or {}).get("voters"),
        valid_votes=(stats or {}).get("valid_votes"),
        first_vote=(stats or {}).get("first_vote"),
        last_vote=(stats or {}).get("last_vote"),
        rows=rows,
        sources=edition.get("sources", {}),
        schedule=edition.get("schedule", []),
        stats=stats,
    )


def area_summary(views: list[EditionView]) -> list[dict[str, Any]]:
    agg: dict[str, dict[str, float]] = defaultdict(lambda: {"listed": 0, "winners": 0, "cost": 0.0})
    for view in views:
        for row in view.rows:
            if not row["area"]:
                continue
            agg[row["area"]]["listed"] += 1
            if row["winner"]:
                agg[row["area"]]["winners"] += 1
                agg[row["area"]]["cost"] += row["cost_pln"] or 0.0
    return [
        {"area": area, **values}
        for area, values in sorted(agg.items(), key=lambda kv: (-kv[1]["winners"], kv[0]))
    ]


def load_realization(path: Path | None) -> dict[int, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {int(entry["project_id"]): entry for entry in payload.get("entries", [])}


def _link(url: str, text: str) -> str:
    return f'<a href="{escape(url, quote=True)}" rel="noopener">{escape(text)}</a>'


def _status_badge(status: str, winner: bool) -> str:
    cls = "win" if winner else "neutral"
    return f'<span class="badge {cls}">{escape(status)}</span>'


def _render_edition_table(view: EditionView) -> str:
    has_votes = any(r["votes"] is not None for r in view.rows)
    has_area = any(r["area"] for r in view.rows)
    head = ["Miejsce" if has_votes else "Nr", "Projekt"]
    if has_area:
        head.append("Obszar")
    head += ["Koszt (plan)", "Status"]
    if has_votes:
        head.append("Głosy")
    rows_html = []
    for r in view.rows:
        first = fmt_int(r["position"]) if has_votes else fmt_int(r["number"])
        number = f'<span class="muted">{r["number"]}.</span> ' if r["number"] else ""
        cells = [
            f'<td class="num">{first}</td>',
            f"<td>{number}{_link(r['url'], r['title'])}</td>",
        ]
        if has_area:
            cells.append(f"<td>{escape(r['area'] or '🚫')}</td>")
        cells.append(f'<td class="num">{fmt_pln(r["cost_pln"])}</td>')
        cells.append(f"<td>{_status_badge(r['status'], r['winner'])}</td>")
        if has_votes:
            cells.append(f'<td class="num">{fmt_int(r["votes"])}</td>')
        rows_html.append(f'<tr class="{"winner" if r["winner"] else ""}">{"".join(cells)}</tr>')
    thead = "".join(f'<th scope="col">{escape(h)}</th>' for h in head)
    return f"<table><thead><tr>{thead}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>"


def _render_schedule(view: EditionView) -> str:
    if not view.schedule:
        return ""
    items = "".join(
        f"<li><strong>{escape(s['name'])}</strong>: "
        f"{('od ' + fmt_date(s['date_from']) + ' ') if s.get('date_from') else ''}"
        f"do {fmt_date(s['date_to'])}</li>"
        for s in view.schedule
    )
    src = view.sources.get("schedule")
    src_html = f' <span class="muted">(źródło: {_link(src, "harmonogram")})</span>' if src else ""
    return f'<h3>Harmonogram edycji {view.year}{src_html}</h3><ol class="schedule">{items}</ol>'


def _render_stats(view: EditionView) -> str:
    s = view.stats
    if not s:
        return ""
    parts = [
        ("Osób głosujących", fmt_int(s.get("voters"))),
        ("Głosów ważnych", fmt_int(s.get("valid_votes"))),
        (
            "Komputer / mobilnie",
            f"{fmt_int(s.get('desktop_votes'))} / {fmt_int(s.get('mobile_votes'))}",
        ),
        ("Kobiety / mężczyźni", f"{fmt_int(s.get('women'))} / {fmt_int(s.get('men'))}"),
        ("Pierwszy głos", fmt_date(s.get("first_vote"))),
        ("Ostatni głos", fmt_date(s.get("last_vote"))),
    ]
    dl = "".join(f"<div><dt>{escape(k)}</dt><dd>{v}</dd></div>" for k, v in parts)
    return f'<dl class="stats">{dl}</dl>'


def _render_summary(views: list[EditionView]) -> str:
    rows = []
    for v in views:
        label = f"{v.year}" + (" (bieżąca)" if v.current else "")
        results_src = v.sources.get("results")
        results_cell = _link(results_src, "wyniki") if results_src else "jeszcze nie ogłoszone"
        rows.append(
            "<tr>"
            f'<th scope="row">{escape(label)}</th>'
            f'<td class="num">{v.n_listed}</td>'
            f'<td class="num">{v.n_winners if v.n_winners else "🚫"}</td>'
            f'<td class="num">{fmt_pln(v.winners_cost) if v.n_winners else "🚫"}</td>'
            f'<td class="num">{fmt_int(v.voters)}</td>'
            f"<td>{fmt_date(v.first_vote).split(' ')[0]} – "
            f"{fmt_date(v.last_vote).split(' ')[0]}</td>"
            f"<td>{results_cell}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr>"
        '<th scope="col">Edycja</th><th scope="col">Projekty na liście</th>'
        '<th scope="col">Wybrane do realizacji</th><th scope="col">Koszt zwycięzców (plan)</th>'
        '<th scope="col">Osób głosujących</th><th scope="col">Głosowanie</th>'
        '<th scope="col">Źródło</th>'
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


def _render_areas(areas: list[dict[str, Any]]) -> str:
    if not areas:
        return "<p>🚫 brak danych o obszarach.</p>"
    rows = "".join(
        f'<tr><th scope="row">{escape(a["area"])}</th><td class="num">{int(a["listed"])}</td>'
        f'<td class="num">{int(a["winners"])}</td>'
        f'<td class="num">{fmt_pln(a["cost"]) if a["winners"] else "—"}</td></tr>'
        for a in areas
    )
    return (
        '<table><thead><tr><th scope="col">Obszar</th><th scope="col">Projekty na liście</th>'
        '<th scope="col">Wybrane do realizacji</th><th scope="col">Koszt zwycięzców (plan)</th>'
        f"</tr></thead><tbody>{rows}</tbody></table>"
    )


def _render_realization(views: list[EditionView], realization: dict[int, dict[str, Any]]) -> str:
    rows = []
    winners_total = 0
    checked_dates: set[str] = set()
    for v in views:
        for r in v.rows:
            if not r["winner"]:
                continue
            winners_total += 1
            entry = realization.get(int(r["id"]))
            if entry and entry.get("checked_on"):
                checked_dates.add(str(entry["checked_on"]))
            status_key = (entry or {}).get("status", "brak_informacji")
            label = REALIZATION_LABELS.get(status_key, REALIZATION_LABELS["brak_informacji"])
            if status_key == "brak_informacji" and entry and entry.get("checked_on"):
                label += f" — sprawdzono {fmt_date(str(entry['checked_on']))}"
            evidence = (entry or {}).get("evidence", [])
            links = (
                "; ".join(
                    f"{fmt_date(e.get('date'))}: {_link(e['url'], e.get('title') or e['url'])}"
                    for e in evidence
                    if e.get("url")
                )
                or "—"
            )
            note = (entry or {}).get("note") or ""
            note_html = f' <span class="muted">({escape(note)})</span>' if note else ""
            rows.append(
                f'<tr><td class="num">{v.year}</td><td>{_link(r["url"], r["title"])}</td>'
                f'<td class="num">{fmt_pln(r["cost_pln"])}</td><td>{escape(label)}{note_html}</td>'
                f"<td>{links}</td></tr>"
            )
    if not rows:
        return "<p>🚫 brak zwycięskich projektów w zbiorze.</p>"
    checked = sum(1 for v in views for r in v.rows if r["winner"] and int(r["id"]) in realization)
    dates_text = ", ".join(fmt_date(d) for d in sorted(checked_dates)) or "🚫"
    procedure = (
        f'<p class="muted">Procedura: {checked} z {winners_total} zwycięzców sprawdzono tą samą '
        f"ścieżką (oficjalna platforma + wyszukiwanie publikacji w sieci + ręczne otwarcie "
        f"każdego źródła); daty sprawdzenia: {dates_text}. "
        "Status „w trakcie” obejmuje także sam plan w budżecie miasta lub podpisaną umowę.</p>"
    )
    return procedure + (
        '<table><thead><tr><th scope="col">Edycja</th><th scope="col">Zwycięski projekt</th>'
        '<th scope="col">Koszt (plan)</th><th scope="col">Co wiadomo publicznie</th>'
        '<th scope="col">Dowód (data: źródło)</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _render_sources(dataset: dict[str, Any], views: list[EditionView]) -> str:
    items = []
    for v in views:
        links = ", ".join(_link(url, name) for name, url in sorted(v.sources.items()))
        items.append(f"<li>Edycja {v.year}: {links or '🚫'}</li>")
    return "<ul>" + "".join(items) + "</ul>"


def _resource(name: str) -> str:
    return files("wbo_tracker").joinpath("templates", name).read_text(encoding="utf-8")


def _render_current_notice(views: list[EditionView]) -> str:
    current = next((v for v in views if v.current), None)
    if current is None:
        return ""
    voting = next((s for s in current.schedule if "głosowanie" in s["name"].lower()), None)
    results = next((s for s in current.schedule if "wynik" in s["name"].lower()), None)
    bits = [
        f"Edycja <strong>{current.year}</strong>: {current.n_listed} projektów "
        "na liście do głosowania."
    ]
    if voting:
        bits.append(
            f"Głosowanie: {fmt_date(voting.get('date_from'))} – {fmt_date(voting.get('date_to'))}."
        )
    if current.sources.get("results"):
        bits.append("Wyniki są już opublikowane — patrz tabela edycji.")
    elif results:
        bits.append(f"Oficjalne ogłoszenie wyników: do {fmt_date(results.get('date_to'))}.")
    return f'<div class="notice"><p>{" ".join(bits)}</p></div>'


def _render_editions(views: list[EditionView]) -> str:
    blocks = []
    for v in views:
        title = f"Edycja {v.year}" + (" — bieżąca" if v.current else "")
        meta = f"{v.n_listed} projektów na liście"
        if v.n_winners:
            meta += f", {v.n_winners} wybranych do realizacji ({fmt_pln(v.winners_cost)})"
        if v.voters:
            meta += f", {fmt_int(v.voters)} głosujących"
        body = (
            _render_schedule(v)
            + _render_stats(v)
            + f'<div class="table-wrap">{_render_edition_table(v)}</div>'
        )
        open_attr = " open" if v.current else ""
        blocks.append(
            f'<details id="edycja-{v.year}"{open_attr}><summary>{escape(title)} '
            f'<span class="muted">— {escape(meta)}</span></summary>{body}</details>'
        )
    return "".join(blocks)


def render_site(dataset: dict[str, Any], realization: dict[int, dict[str, Any]]) -> str:
    views = [edition_view(e) for e in dataset.get("editions", [])]
    views.sort(key=lambda v: v.year, reverse=True)
    generated_at = dataset.get("generated_at", "")
    template = Template(_resource("index.html"))
    return template.substitute(
        css=_resource("site.css"),
        source_url=escape(dataset.get("source_url", "https://wbo.walbrzych.eu")),
        source_name=escape(dataset.get("source_name", "wbo.walbrzych.eu")),
        platform=escape(dataset.get("platform", "")),
        generated_at=escape(generated_at),
        generated_at_pl=escape(fmt_date(generated_at[:16]) + " UTC"),
        current_notice=_render_current_notice(views),
        summary=_render_summary(views),
        editions=_render_editions(views),
        areas=_render_areas(area_summary(views)),
        realization=_render_realization(views, realization),
        sources_list=_render_sources(dataset, views),
    )


CSV_COLUMNS = [
    "edition_year",
    "project_id",
    "number",
    "title",
    "area",
    "cost_pln",
    "status",
    "position",
    "votes",
    "url",
]


def write_csv(dataset: dict[str, Any], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, delimiter=";")
        writer.writeheader()
        for edition in sorted(dataset.get("editions", []), key=lambda e: e["year"], reverse=True):
            for row in _edition_rows(edition):
                writer.writerow(
                    {
                        "edition_year": edition["year"],
                        "project_id": row["id"],
                        "number": row["number"] if row["number"] is not None else "",
                        "title": row["title"],
                        "area": row["area"] or "",
                        "cost_pln": f"{row['cost_pln']:.2f}" if row["cost_pln"] is not None else "",
                        "status": row["status"],
                        "position": row["position"] if row["position"] is not None else "",
                        "votes": row["votes"] if row["votes"] is not None else "",
                        "url": row["url"],
                    }
                )
                count += 1
    return count


def build(data_path: Path, out_html: Path, out_csv: Path, realization_path: Path | None) -> None:
    dataset = json.loads(data_path.read_text(encoding="utf-8"))
    realization = load_realization(realization_path)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(render_site(dataset, realization), encoding="utf-8")
    write_csv(dataset, out_csv)
