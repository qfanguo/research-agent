# modules/config.py

RSS_FEEDS = [
    # --- Major AI Labs ---
    "https://openai.com/news/rss.xml",
    "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",  # Community feed
    "https://deepmind.google/blog/rss.xml",
    "https://research.google/blog/rss",
    "https://ai.meta.com/blog/rss/",
    "https://engineering.fb.com/feed/",
    "https://mistral.ai/feed/rss2.xml",

    # --- Model Providers & Platforms ---
    "https://huggingface.co/blog/feed.xml",
    "https://qwenlm.github.io/index.xml",  # Fixed Qwen blog URL
    "https://github.blog/feed/",  # GitHub Blog (for MCP, Copilot news etc.)
    "https://any-feeds.com/api/feeds/custom/cmkoaiogm0000lf04qmtirq2g/rss.xml",  # Cursor
    # "https://blogs.microsoft.com/ai/feed/",  # Microsoft AI Blog (Frequently returns 403 in CI)
    "https://blog.google/technology/ai/rss/",  # Google AI Blog

    # --- Cloud & Infra ---
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://blogs.nvidia.com/feed/",
    "https://machinelearning.apple.com/rss.xml",

    # --- AI Frameworks & Tools ---
    "https://blog.langchain.dev/rss/",
    "https://medium.com/feed/llamaindex-blog",
    "https://arize.com/feed/",
    "https://wandb.ai/feed",

    # --- Tech Company Engineering Blogs ---
    "https://netflixtechblog.com/feed",
    "https://engineering.atspotify.com/feed/",
    "https://engineering.linkedin.com/blog.rss.html",
    "https://github.com/Tencent.atom",

    # --- Academic & Research ---
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://hai.stanford.edu/news/blog/rss",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",

    # --- Individual Researchers ---
    "https://eugeneyan.com/rss/",
    "https://lilianweng.github.io/lil-log/feed.xml",
    "https://karpathy.ai/feed.xml",

    # --- HN aggregation for companies without good RSS ---
    "https://hnrss.org/newest?q=domain:perplexity.ai+OR+domain:cohere.com+OR+domain:adept.ai+OR+domain:character.ai+OR+domain:midjourney.com+OR+domain:deepseek.com+OR+domain:01.ai+OR+domain:moonshot.ai+OR+domain:baichuan-ai.com+OR+domain:minimax.io+OR+domain:bytedance.com+OR+domain:tinyfish.io",
    # --- HN top stories about major AI topics (36h window ensures we catch weekend news on Monday/Tuesday) ---
    "https://hnrss.org/newest?q=OpenClaw+OR+Qwen+OR+TinyFish+OR+%22Seed+2.0%22+OR+%22Seed+2%22+OR+%22MCP+support%22+OR+%22GPT-5%22+OR+%22Claude+4%22+OR+%22Gemini+3%22+OR+%22delegate+work%22+OR+%22Gemini+attackers%22+OR+%22MCP%22&points=30",
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
