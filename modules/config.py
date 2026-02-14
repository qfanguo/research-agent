# modules/config.py

RSS_FEEDS = [
    "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml", # Community feed
    "https://any-feeds.com/api/feeds/custom/cmkoaiogm0000lf04qmtirq2g/rss.xml", # Community feed for Cursor
    "https://github.com/Tencent.atom",
    "https://openai.com/news/rss.xml", 
    "https://research.google/blog/rss", 
    "https://huggingface.co/blog/feed.xml", 
    "https://engineering.fb.com/feed/",
    "https://deepmind.google/blog/rss.xml",
    "https://blog.langchain.dev/rss/",
    "https://medium.com/feed/llamaindex-blog",
    "https://arize.com/feed/",
    "https://wandb.ai/feed",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://hai.stanford.edu/news/blog/rss",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
    "https://blogs.nvidia.com/feed/",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://machinelearning.apple.com/rss.xml",
    "https://netflixtechblog.com/feed",
    "https://engineering.atspotify.com/feed/",
    "https://engineering.linkedin.com/blog.rss.html",
    "https://eugeneyan.com/rss/",
    "https://lilianweng.github.io/lil-log/feed.xml",
    "https://karpathy.ai/feed.xml",
    "https://hnrss.org/newest?q=domain:perplexity.ai+OR+domain:cohere.com+OR+domain:mistral.ai+OR+domain:adept.ai+OR+domain:character.ai+OR+domain:midjourney.com+OR+domain:deepseek.com+OR+domain:01.ai+OR+domain:moonshot.ai+OR+domain:baichuan-ai.com+OR+domain:minimax.io"
]

USER_INTERESTS = [
    "Vibe Coding", 
    "RAG", 
    "LLM Agents",
    "Generative AI Trends",
    "Multimodal AI",
    "Local LLMs / SLMs",
    "Prompt Engineering",
    "Model Fine-tuning",
    "AI Evaluation",
    "Reasoning Models"
]

# Dynamically build ArXiv query
# Broader query to capture more candidates for LLM filtering
ARXIV_QUERY = 'abs:LLM OR abs:Agent OR abs:RAG OR abs:"Machine Learning" OR abs:"Generative AI" OR abs:"Multimodal" OR abs:"Reasoning"'
ARXIV_MAX_RESULTS = 100  # Increased to let LLM decide relevance
