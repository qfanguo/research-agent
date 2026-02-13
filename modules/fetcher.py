# modules/fetcher.py
import feedparser
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
        cutoff = now - datetime.timedelta(hours=24) # Adjustable

        for url in self.rss_feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    # Normalize publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                         pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
                    
                    if pub_date and pub_date > cutoff:
                        articles.append({
                            "title": entry.title,
                            "link": entry.link,
                            "summary": getattr(entry, 'summary', '') or getattr(entry, 'description', ''),
                            "source": feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else url,
                            "published": pub_date.isoformat(),
                            "type": "blog"
                        })
            except Exception as e:
                print(f"Error fetching {url}: {e}")
        
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
