"""
Base scraper — rate-limited, cached HTTP client.

Features:
  - Disk-based HTML cache under data_pipeline/.cache/
  - Configurable delay between requests (be kind to public servers)
  - Retry with exponential back-off
  - User-Agent identification
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

import requests

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"


class BaseScraper:
    """Rate-limited HTTP client with local caching."""

    USER_AGENT = (
        "HomeopathyGraphRAG/1.0 "
        "(academic research; https://github.com/homeopathy-graph-rag)"
    )

    def __init__(
        self,
        delay_seconds: float = 1.5,
        max_retries: int = 3,
        cache_dir: Path = CACHE_DIR,
        use_cache: bool = True,
    ):
        self.delay = delay_seconds
        self.max_retries = max_retries
        self.cache_dir = cache_dir
        self.use_cache = use_cache
        self._last_request_time: float = 0.0
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.USER_AGENT})

        if self.use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ── cache helpers ────────────────────────────────────
    def _cache_key(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    def _cache_path(self, url: str) -> Path:
        return self.cache_dir / f"{self._cache_key(url)}.html"

    def _meta_path(self, url: str) -> Path:
        return self.cache_dir / f"{self._cache_key(url)}.meta.json"

    def _read_cache(self, url: str) -> Optional[str]:
        path = self._cache_path(url)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def _write_cache(self, url: str, html: str) -> None:
        self._cache_path(url).write_text(html, encoding="utf-8")
        self._meta_path(url).write_text(
            json.dumps({"url": url, "fetched_at": time.time()}),
            encoding="utf-8",
        )

    # ── rate-limiting ────────────────────────────────────
    def _throttle(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    # ── fetch ────────────────────────────────────────────
    def fetch(self, url: str, encoding: str = "utf-8") -> str:
        """Fetch a URL; returns cached HTML if available."""
        if self.use_cache:
            cached = self._read_cache(url)
            if cached is not None:
                return cached

        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            try:
                resp = self._session.get(url, timeout=30)
                self._last_request_time = time.time()
                resp.raise_for_status()
                resp.encoding = encoding
                html = resp.text
                if self.use_cache:
                    self._write_cache(url, html)
                return html
            except requests.RequestException as exc:
                if attempt == self.max_retries:
                    raise
                wait = 2 ** attempt
                print(f"  ⚠ Retry {attempt}/{self.max_retries} for {url} "
                      f"({exc}), waiting {wait}s...")
                time.sleep(wait)

        raise RuntimeError(f"Failed to fetch {url}")  # unreachable

    # ── convenience ──────────────────────────────────────
    def clear_cache(self) -> int:
        """Delete all cached files. Returns count of files removed."""
        count = 0
        if self.cache_dir.exists():
            for f in self.cache_dir.iterdir():
                f.unlink()
                count += 1
        return count

    def cache_stats(self) -> dict:
        """Return cache statistics."""
        if not self.cache_dir.exists():
            return {"files": 0, "size_mb": 0}
        files = list(self.cache_dir.glob("*.html"))
        total_bytes = sum(f.stat().st_size for f in files)
        return {"files": len(files), "size_mb": round(total_bytes / 1_048_576, 2)}
