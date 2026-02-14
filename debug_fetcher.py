import asyncio
import datetime
from modules.fetcher import Fetcher
import feedparser
import httpx
import ssl
import urllib.request
import urllib.error

# Mock or subclass Fetcher to add detailed logging
class DebugFetcher(Fetcher):
    async def _fetch_single_rss_feed_with_retry(self, client, url):
        print(f"Checking {url}...")
        try:
            # We copy the logic but add more print statements
            response = await client.get(url, headers=self.headers, timeout=15.0, follow_redirects=True)
            if response.status_code != 200:
                 print(f"  [ERROR] HTTP {response.status_code}")
                 # Fallback logic is omitted for brevity unless we want to test it too. 
                 # Let's just focus on the primary path first.
            
            rss_content = response.text
            feed = feedparser.parse(rss_content)
            
            print(f"  [INFO] Found {len(feed.entries)} entries total.")
            
            kept = 0
            filtered = 0
            future = 0
            
            for entry in feed.entries:
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
                
                if pub_date:
                    if pub_date > self.cutoff_date:
                        kept += 1
                        # print(f"    [KEEP] {entry.title} ({pub_date})")
                    else:
                        filtered += 1
                        # print(f"    [DROP] {entry.title} ({pub_date})")
                else:
                    print(f"    [WARN] No date found for {getattr(entry, 'title', 'No Title')}")
            
            print(f"  [STATS] Kept: {kept}, Filtered (Old): {filtered}, Future/Unknown: {future}")
            return [] # We don't care about the return value for this debug script
            
        except Exception as e:
            print(f"  [FAIL] Exception: {e}")
            return []

async def run_debug():
    print("Debug Start")
    print(f"Current Time (UTC): {datetime.datetime.now(datetime.timezone.utc)}")
    f = DebugFetcher()
    print(f"Cutoff Date (UTC): {f.cutoff_date}")
    
    await f.fetch_rss()

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    asyncio.run(run_debug())
