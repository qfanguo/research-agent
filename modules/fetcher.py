import asyncio
import httpx
import feedparser
import time
import arxiv
import datetime
from dateutil import parser
from typing import List, Dict, Any
from . import config
import urllib.request
import urllib.error
import ssl


import http.client
import urllib3

class Fetcher:
    def __init__(self):
        self.rss_feeds = config.RSS_FEEDS
        self.arxiv_query = config.ARXIV_QUERY
        # Initialize cutoff date (last 24 hours) for both RSS and ArXiv
        self.cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/xml,application/xml,application/atom+xml,application/rss+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'
        }

    async def _fetch_single_rss_feed_with_retry(self, client: httpx.AsyncClient, url: str) -> List[Dict[str, Any]]:
        """
        Fetches and parses a single RSS feed with retry logic and custom headers.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use httpx for parallel fetching with custom headers and optional SSL verification bypass
                response = await client.get(url, headers=self.headers, timeout=15.0, follow_redirects=True)
                if response.status_code == 200:
                    rss_content = response.text
                elif response.status_code == 403:
                    # Fallback to urllib for 403 (e.g. MIT News blocks httpx)
                    try:
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE
                        req = urllib.request.Request(url, headers=self.headers, method='GET')
                        
                        # run_in_executor or to_thread for blocking call
                        content = await asyncio.to_thread(lambda: urllib.request.urlopen(req, context=ctx, timeout=15).read())
                        rss_content = content.decode('utf-8', errors='ignore')
                    except (http.client.IncompleteRead, urllib3.exceptions.IncompleteRead) as e:
                        # Attempt to use partial content if available
                        print(f"IncompleteRead for {url}. Attempting to use partial content.")
                        if hasattr(e, 'partial') and e.partial:
                             rss_content = e.partial.decode('utf-8', errors='ignore')
                        else:
                             print(f"No partial content for {url}")
                             raise e
                    except Exception as e_urllib:
                        print(f"Fallback urllib failed for {url}: {e_urllib}")
                        raise Exception(f"HTTP Error {response.status_code} and Fallback Failed")
                else:
                    raise Exception(f"HTTP Error {response.status_code}")
                
                feed = feedparser.parse(rss_content)
                
                # Check for parsing errors, but allow one more attempt if it's not the last one
                if feed.bozo and attempt < max_retries - 1:
                    # Some "bozo" errors are harmless (e.g. non-XML content type but valid XML)
                    # We only retry for more severe errors
                    pass

                items = []
                for entry in feed.entries:
                    # Normalize publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                         pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
                    
                    # Filter by date (last 24 hours)
                    if pub_date and pub_date > self.cutoff_date:
                        items.append({
                            "title": getattr(entry, 'title', 'No Title'),
                            "link": getattr(entry, 'link', url),
                            "summary": getattr(entry, 'summary', '') or getattr(entry, 'description', ''),
                            "source": feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else url,
                            "published": pub_date.isoformat(),
                            "type": "blog"
                        })
                return items
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    print(f"Error fetching {url} after {max_retries} attempts: {e}")
        return []

    async def fetch_rss(self) -> List[Dict[str, Any]]:
        """Fetches and parses all configured RSS feeds in parallel."""
        # SSL verify=False for robustness against poor cert configurations (like Netflix sometimes)
        async with httpx.AsyncClient(verify=False) as client:
            tasks = [self._fetch_single_rss_feed_with_retry(client, url) for url in self.rss_feeds]
            results = await asyncio.gather(*tasks)
            # Flatten list of lists
            return [item for sublist in results for item in sublist]

    def fetch_arxiv(self) -> List[Dict[str, Any]]:
        """Fetches recent ArXiv papers matching the query."""
        client = arxiv.Client()
        search = arxiv.Search(
            query=self.arxiv_query,
            max_results=config.ARXIV_MAX_RESULTS,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = []
        for result in client.results(search):
            if result.published > self.cutoff_date:
                papers.append({
                    "title": result.title,
                    "link": result.entry_id,
                    "summary": result.summary,
                    "source": "ArXiv",
                    "published": result.published.isoformat(),
                    "type": "paper"
                })
        return papers

    async def fetch_all(self) -> List[Dict[str, Any]]:
        rss_data = await self.fetch_rss()
        # Arxiv library is synchronous, we run it in a thread or just let it be if it's fast
        # Given it's a single call usually, we'll keep it simple
        arxiv_data = self.fetch_arxiv()
        return rss_data + arxiv_data

if __name__ == "__main__":
    async def test():
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        f = Fetcher()
        items = await f.fetch_all()
        print(f"Fetched {len(items)} items.")
        for item in items[:10]:
            print(f"- [{item['type']}] {item['title']} ({item['source']})")
    
    asyncio.run(test())
