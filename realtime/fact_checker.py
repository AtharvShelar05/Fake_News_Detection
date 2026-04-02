"""
realtime/fact_checker.py
========================
Google Fact Check Tools API integration with MULTI-QUERY strategy.

Instead of sending the full text once, this module extracts multiple
searchable queries (key phrases, individual sentences, topic keywords)
and tries each one against the API to maximize hit rate.

Graceful fallback:
  - No API key   -> returns empty result (no crash)
  - No match     -> returns empty result
  - API error    -> logs warning, returns empty result

API key setup:
  1. Get a free key at https://console.cloud.google.com/
  2. Enable "Fact Check Tools API"
  3. Set in .env:  FACT_CHECK_API_KEY=YOUR_KEY

Usage:
    from realtime.fact_checker import FactChecker
    fc = FactChecker()
    result = fc.check("vaccine causes autism")
"""

import os
import re
import sys
import logging
import urllib.parse
import urllib.request
import urllib.error
import json
from typing import Any, Dict, List, Optional, Set, Tuple

# Load .env if python-dotenv is available (optional dependency)
try:
    from dotenv import load_dotenv  # type: ignore[import-untyped]
    _env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    load_dotenv(_env_path)
except ImportError:
    pass

logger = logging.getLogger(__name__)

FACT_CHECK_API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# Common stopwords to filter out when extracting key phrases
_STOPWORDS: Set[str] = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "that", "this",
    "these", "those", "it", "its", "not", "no", "nor", "so", "as", "if",
    "then", "than", "too", "very", "just", "about", "above", "after",
    "again", "all", "also", "am", "because", "before", "between", "both",
    "during", "each", "few", "here", "how", "into", "more", "most",
    "other", "out", "over", "own", "same", "she", "he", "they", "them",
    "there", "their", "what", "when", "where", "which", "who", "whom",
    "why", "your", "our", "my", "his", "her", "up", "down", "under",
    "said", "says", "news", "top", "day", "new", "report", "reports",
}


class FactChecker:
    """
    Integrates with Google Fact Check Tools API.
    Uses multi-query strategy to maximize API hit rate.
    Returns structured fact-check results or empty if unavailable.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Args:
            api_key: Google API key. Falls back to env var FACT_CHECK_API_KEY.
        """
        self.api_key: str = api_key or os.environ.get("FACT_CHECK_API_KEY", "")
        self._available: bool = bool(self.api_key)

        if not self._available:
            logger.info("FactChecker: No API key found — running in ML-only mode.")

    # ── Public API ───────────────────────────────────────────────────────────

    def check(self, text: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Query fact-check API using MULTIPLE search strategies.

        Strategy:
          1. Full text (first 15 words)
          2. Individual sentences (if multiple)
          3. Extracted key phrases (nouns, entities)
          4. Topic keywords

        Args:
            text:        Raw news text to check.
            max_results: Maximum number of matching claims to return per query.

        Returns:
            dict with keys:
              available, matched, verified_label, confidence_adj, claims, error
        """
        empty: Dict[str, Any] = {
            "available":      self._available,
            "matched":        False,
            "verified_label": None,
            "confidence_adj": 0.0,
            "claims":         [],
            "error":          None,
        }

        if not self._available:
            return empty

        # Generate multiple search queries from the input
        queries = self._extract_queries(text)
        logger.info(f"FactChecker: trying {len(queries)} search queries: {queries}")

        # Try each query until we find results (or exhaust all)
        all_claims: List[Dict[str, str]] = []
        seen_texts: Set[str] = set()  # deduplicate claims

        for query in queries:
            try:
                results = self._query_api(query, max_results)
                for claim in results:
                    claim_key = claim.get("text", "").strip().lower()
                    if claim_key and claim_key not in seen_texts:
                        seen_texts.add(claim_key)
                        all_claims.append(claim)
            except Exception as exc:
                logger.debug(f"FactChecker: query '{query}' failed: {exc}")
                continue

            # Stop early if we have enough results
            if len(all_claims) >= max_results:
                break

        if not all_claims:
            logger.info("FactChecker: no matching claims found across all queries.")
            return empty

        # Limit total claims
        all_claims = all_claims[:max_results]

        # Analyse claim ratings to determine overall verdict
        verdict, adj = self._analyse_ratings(all_claims)
        logger.info(
            f"FactChecker: found {len(all_claims)} claim(s), verdict={verdict}"
        )

        return {
            "available":      True,
            "matched":        True,
            "verified_label": verdict,
            "confidence_adj": adj,
            "claims":         all_claims,
            "error":          None,
        }

    def is_available(self) -> bool:
        """Return True if an API key is configured."""
        return self._available

    # ── Query extraction (multi-strategy) ─────────────────────────────────────

    def _extract_queries(self, text: str) -> List[str]:
        """
        Extract multiple searchable queries from the input text.

        Strategy:
          1. Full headline (first 12 words) — catches exact claims
          2. Each sentence individually (for multi-sentence input)
          3. Key phrase clusters (3-5 important words)
          4. Named entity / topic search (proper nouns)
        """
        queries: List[str] = []
        seen: Set[str] = set()
        text = text.strip()

        def add_query(q: str) -> None:
            q = q.strip()
            q_lower = q.lower()
            if len(q) >= 10 and q_lower not in seen:
                seen.add(q_lower)
                queries.append(q)

        # ── Strategy 1: Full text (first 12 words) ───────────────────────
        words = text.split()
        add_query(" ".join(words[:12]))

        # ── Strategy 2: Individual sentences ─────────────────────────────
        sentences = re.split(r'[.!?;]\s+', text)
        for sent in sentences[:4]:  # max 4 sentences
            sent_words = sent.strip().split()
            if len(sent_words) >= 4:
                add_query(" ".join(sent_words[:15]))

        # ── Strategy 3: Key phrases (content words only) ─────────────────
        content_words = [
            w for w in words
            if w.lower().strip(",.!?;:\"'()[]") not in _STOPWORDS
            and len(w) > 2
        ]

        # Take the first 5 content words as a key phrase
        if len(content_words) >= 3:
            add_query(" ".join(content_words[:5]))

        # Take middle content words as another key phrase
        if len(content_words) >= 6:
            mid = len(content_words) // 2
            add_query(" ".join(content_words[mid-2:mid+3]))

        # ── Strategy 4: Proper nouns / named entities ────────────────────
        # Extract capitalized words (likely names, places, organizations)
        proper_nouns = [
            w.strip(",.!?;:\"'()[]")
            for w in words
            if w[0:1].isupper() and w.lower() not in _STOPWORDS
            and len(w) > 2 and not w.isupper()  # skip ALL-CAPS words like "SHOCKING"
        ]
        if len(proper_nouns) >= 2:
            add_query(" ".join(proper_nouns[:6]))

        # ── Strategy 5: Direct claim patterns ────────────────────────────
        # Look for common claim-like phrases in the text
        claim_patterns = [
            r'(?:claim|allege|report|accuse|reveal|discover|confirm|announce|deny)\w*\s+.{10,80}',
            r'(?:cause|prevent|cure|treat|spread|kill|infect)\w*\s+.{5,50}',
        ]
        for pattern in claim_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                add_query(match.group(0)[:80])

        return queries[:6]  # max 6 queries to avoid rate limiting

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _query_api(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Call the Google Fact Check Tools API and return parsed claims."""
        params = urllib.parse.urlencode({
            "query":        query,
            "key":          self.api_key,
            "pageSize":     max_results,
            "languageCode": "en",
        })
        url = f"{FACT_CHECK_API_URL}?{params}"

        req = urllib.request.Request(
            url, headers={"User-Agent": "FakeNewsDetector/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data: Dict[str, Any] = json.loads(resp.read().decode("utf-8"))

        raw_claims: List[Dict[str, Any]] = data.get("claims", [])
        parsed: List[Dict[str, str]] = []
        for claim in raw_claims:
            reviews = claim.get("claimReview") or [{}]   # type: ignore[assignment]
            review = reviews[0]                           # type: ignore[index]
            publisher_info = review.get("publisher", {})  # type: ignore[union-attr]
            parsed.append({
                "text":       claim.get("text", ""),
                "claimant":   claim.get("claimant", "Unknown"),
                "rating":     review.get("textualRating", "Unknown"),  # type: ignore[union-attr]
                "rating_url": review.get("url", ""),                   # type: ignore[union-attr]
                "publisher":  publisher_info.get("name", "Unknown"),   # type: ignore[union-attr]
            })
        return parsed

    def _analyse_ratings(self, claims: List[Dict[str, str]]) -> Tuple[str, float]:
        """
        Parse textual ratings and return (verdict_label, confidence_adjustment).

        Common rating keywords come from PolitiFact, Snopes, AFP, etc.
        """
        false_keywords = {
            "false", "fake", "misleading", "incorrect", "inaccurate",
            "wrong", "hoax", "fabricated", "pants on fire", "lie",
            "misinformation", "disinformation", "debunked", "fiction",
            "partly false", "mostly false", "not true", "unproven",
            "unsupported", "manipulated", "altered", "out of context",
        }
        true_keywords = {
            "true", "accurate", "correct", "verified", "confirmed",
            "mostly true", "real", "fact", "legit", "half true",
        }

        false_count = 0
        true_count = 0

        for claim in claims:
            rating = claim.get("rating", "").lower()
            if any(kw in rating for kw in false_keywords):
                false_count = false_count + 1
            elif any(kw in rating for kw in true_keywords):
                true_count = true_count + 1

        if false_count > true_count:   # type: ignore[operator]
            return "Verified Fake", -0.15
        elif true_count > false_count: # type: ignore[operator]
            return "Verified True", +0.15
        else:
            return "Fact-Checked", 0.0
