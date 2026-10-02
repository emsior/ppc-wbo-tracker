"""Polite HTTP access to the official platform: one session, a real User-Agent, a pause
between requests, optional on-disk cache of raw pages (never committed) and TLS verified
through the operating-system trust store (the platform serves an incomplete chain)."""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path

import requests

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://wbo.walbrzych.eu"
DEFAULT_USER_AGENT = (
    "ppc-wbo-tracker/0.1 (+https://github.com/emsior/ppc-wbo-tracker; prochpc@gmail.com)"
)


def _install_os_trust_store() -> None:
    """Use the OS certificate store (Windows/macOS/Linux) instead of certifi.

    The platform's HTTPS chain lacks an intermediate certificate; browsers fetch it on the
    fly, certifi-based clients fail. truststore delegates verification to the OS, so TLS
    verification stays ON."""
    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:  # pragma: no cover - optional at runtime, required in pyproject
        log.warning("truststore not installed; TLS verification uses certifi")


class Fetcher:
    """GET pages from the platform, slowly, with an optional raw cache."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        delay_s: float = 1.0,
        cache_dir: Path | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout_s: float = 30.0,
    ) -> None:
        _install_os_trust_store()
        self.base_url = base_url.rstrip("/")
        self.delay_s = delay_s
        self.cache_dir = cache_dir
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Language": "pl"})
        self._last_request_at = 0.0
        self.requests_made = 0

    def _cache_path(self, path: str) -> Path | None:
        if self.cache_dir is None:
            return None
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", path.strip("/")) or "index"
        return self.cache_dir / f"{slug}.html"

    def get(self, path: str) -> str | None:
        """Return page HTML; None when the platform answers 404 (results not published yet)."""
        cache_path = self._cache_path(path)
        if cache_path is not None and cache_path.exists():
            log.debug("cache hit %s", path)
            return cache_path.read_text(encoding="utf-8")

        wait = self.delay_s - (time.monotonic() - self._last_request_at)
        if wait > 0:
            time.sleep(wait)
        url = f"{self.base_url}/{path.lstrip('/')}"
        log.info("GET %s", url)
        response = self.session.get(url, timeout=self.timeout_s)
        self._last_request_at = time.monotonic()
        self.requests_made += 1
        if response.status_code == 404:
            return None
        response.raise_for_status()
        response.encoding = response.encoding or "utf-8"
        html = response.text
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(html, encoding="utf-8")
        return html
