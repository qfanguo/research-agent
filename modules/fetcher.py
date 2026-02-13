# modules/fetcher.py
import feedparser
import time
import arxiv
import datetime
from dateutil import parser
from typing import List, Dict, Any
from . import config

class Fetcher:
    def __init__(self):
        self.rss_feeds = config.RSS_FEEDS
        self.arxiv_query = config.ARXIV_QUERY

    def fetch_rss(self) -> List[Dict[str, Any]]:
        """Fetches and parses all configured RSS feeds."""
        articles = []
        # Get start of today (local time assumption or UTC as per preference, using UTC for consistency)
        # Actually, for a daily run, we want anything published in the last 24h or since last run.
        # For simplicity, we'll filter by "published today or yesterday" to catch everything.
        now = datetime.datetime.now(datetime.timezone.utc)
        # Initialize cutoff date for RSS feeds
        self.rss_cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)

    def _fetch_single_rss_feed_with_retry(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetches and parses a single RSS feed with retry logic.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                feed = feedparser.parse(url)
                # Check for parsing errors, but allow one more attempt if it's not the last one
                if feed.bozo and attempt < max_retries - 1:
                    raise Exception(f"Feed parsing error: {feed.bozo_exception}")

                items = []
                for entry in feed.entries:
                    # Normalize publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                         pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
                    
                    # Filter by date (last 24 hours, using self.rss_cutoff_date)
                    if pub_date and pub_date > self.rss_cutoff_date:
                        items.append({
                            "title": getattr(entry, 'title', 'No Title'),
                            "link": getattr(entry, 'link', url), # Fallback to feed URL if no link
                            "summary": getattr(entry, 'summary', '') or getattr(entry, 'description', ''),
                            "source": feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else url,
                            "published": pub_date.isoformat(),
                            "type": "blog"
                        })
                return items # Successfully fetched and parsed
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt) # Exponential backoff
                else:
                    print(f"Error fetching {url} after {max_retries} attempts.")
        return [] # Return empty list if all retries fail

    def fetch_rss(self) -> List[Dict[str, Any]]:
        """Fetches and parses all configured RSS feeds using retry logic."""
        articles = []
        for url in self.rss_feeds:
            articles.extend(self._fetch_single_rss_feed_with_retry(url))
        return articles

    def fetch_arxiv(self) -> List[Dict[str, Any]]:
        """Fetches recent ArXiv papers matching the query."""
        client = arxiv.Client()
        search = arxiv.Search(
            query=self.arxiv_query,
            max_results=config.ARXIV_MAX_RESULTS,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = []
        # ArXiv 'submittedDate' is reliable.
        # We only want very recent ones.
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(hours=24)

        for result in client.results(search):
            if result.published > cutoff:
                papers.append({
                    "title": result.title,
                    "link": result.entry_id,
                    "summary": result.summary,
                    "source": "ArXiv",
                    "published": result.published.isoformat(),
                    "type": "paper"
                })
        return papers

    def fetch_all(self) -> List[Dict[str, Any]]:
        rss_data = self.fetch_rss()
        arxiv_data = self.fetch_arxiv()
        return rss_data + arxiv_data

if __name__ == "__main__":
    # Test execution
    f = Fetcher()
    items = f.fetch_all()
    print(f"Fetched {len(items)} items.")
    for item in items:
        print(f"- [{item['type']}] {item['title']} ({item['source']})")
