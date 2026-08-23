"""
kshiraj/ingestion/robots.py

Polite robots.txt parsing and crawl delay management for government web crawling.
Adheres to standard robots exclusion protocol without bypass mechanisms.
"""

from __future__ import annotations

import time
from typing import Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from shared.utils import get_logger

logger = get_logger(__name__)


class RobotsPolicy:
    """
    Manages robots.txt rules and crawl-delay policies across target domains.
    """

    def __init__(
        self,
        default_user_agent: str = "Project26108-GovtIngestionBot",
        default_crawl_delay: float = 0.5,
        enabled: bool = True,
    ) -> None:
        self.default_user_agent = default_user_agent
        self.default_crawl_delay = default_crawl_delay
        self.enabled = enabled
        self._parsers: Dict[str, RobotFileParser] = {}
        self._last_access_times: Dict[str, float] = {}

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc.lower()

    def parse_robots_txt(self, domain: str, robots_txt_content: str) -> None:
        """Parse raw robots.txt text for a specific domain."""
        parser = RobotFileParser()
        parser.parse(robots_txt_content.splitlines())
        self._parsers[domain.lower()] = parser
        logger.debug("Parsed robots.txt for domain '%s'", domain)

    def is_allowed(self, url: str, user_agent: Optional[str] = None) -> bool:
        """
        Check whether crawling the URL is permitted under robots.txt rules.
        """
        if not self.enabled:
            return True

        domain = self._get_domain(url)
        parser = self._parsers.get(domain)
        if parser is None:
            # If no robots.txt was fetched/parsed for this domain, default to allowed
            return True

        ua = user_agent or self.default_user_agent
        try:
            return parser.can_fetch(ua, url)
        except Exception as exc:
            logger.warning("Error evaluating robots.txt for %s: %s", url, exc)
            return True

    def get_crawl_delay(self, domain_or_url: str, user_agent: Optional[str] = None) -> float:
        """
        Get recommended crawl delay in seconds for the given domain.
        """
        domain = self._get_domain(domain_or_url) if "://" in domain_or_url else domain_or_url.lower()
        parser = self._parsers.get(domain)
        if parser is not None:
            ua = user_agent or self.default_user_agent
            try:
                delay = parser.crawl_delay(ua)
                if delay is not None and delay > 0:
                    return float(delay)
            except Exception:
                pass
        return self.default_crawl_delay

    def wait_if_needed(self, domain_or_url: str, sleep_fn=time.sleep) -> float:
        """
        Enforce crawl delay for polite crawling. Sleeps if necessary and records timestamp.
        Returns the duration waited.
        """
        domain = self._get_domain(domain_or_url) if "://" in domain_or_url else domain_or_url.lower()
        required_delay = self.get_crawl_delay(domain)
        last_time = self._last_access_times.get(domain, 0.0)
        now = time.time()
        elapsed = now - last_time

        waited = 0.0
        if elapsed < required_delay:
            waited = required_delay - elapsed
            sleep_fn(waited)

        self._last_access_times[domain] = time.time()
        return waited
