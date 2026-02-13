# modules/config.py

RSS_FEEDS = [
    "https://engineering.fb.com/feed/",
    "https://ai.google/feed/",
    "https://openai.com/news/rss.xml",
    "http://bair.berkeley.edu/blog/feed.xml",
    "https://netflixtechblog.com/feed",
    "https://engineering.atspotify.com/feed/",
    "https://engineering.linkedin.com/blog.rss.html",
    "https://doordash.engineering/feed/",
    "https://eugeneyan.com/rss/",
    "https://lilianweng.github.io/lil-log/feed.xml",
    "https://karpathy.ai/feed.xml"
]

ARXIV_QUERY = "abs:RAG OR abs:Agent OR abs:Retrieval"
ARXIV_MAX_RESULTS = 20  # Fetch a few more to filter down
