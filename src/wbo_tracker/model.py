"""Data model of the tracker. Facts only: no project descriptions, no images, no authors."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Project:
    """One project as listed on the ballot page of an edition."""

    id: int
    number: int | None
    title: str
    area: str | None
    cost_pln: float | None
    status: str
    url: str


@dataclass(frozen=True)
class Result:
    """One row of the official voting results of an edition."""

    id: int
    position: int | None
    number: int | None
    votes: int | None
    status: str
    cost_pln: float | None


@dataclass
class Stats:
    """Voting statistics published by the platform for a finished edition."""

    voters: int | None = None
    valid_votes: int | None = None
    desktop_votes: int | None = None
    mobile_votes: int | None = None
    women: int | None = None
    men: int | None = None
    first_vote: str | None = None
    last_vote: str | None = None


@dataclass(frozen=True)
class ScheduleStep:
    """One step of the official schedule (harmonogram)."""

    name: str
    date_from: str | None
    date_to: str | None


@dataclass
class Edition:
    """One edition of the participatory budget."""

    year: int
    site_id: int | None
    current: bool
    projects: list[Project] = field(default_factory=list)
    results: list[Result] = field(default_factory=list)
    stats: Stats | None = None
    schedule: list[ScheduleStep] = field(default_factory=list)
    sources: dict[str, str] = field(default_factory=dict)


@dataclass
class Dataset:
    """Everything the site is built from."""

    generated_at: str
    source_name: str
    source_url: str
    platform: str
    editions: list[Edition] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
