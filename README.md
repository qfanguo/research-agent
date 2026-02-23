# Collect Info Agent

**One email every morning:** Fetches major AI blogs, ArXiv papers, and HN highlights, then uses an LLM to summarize, score, and categorize them into a readable Research Digest delivered to your inbox.

![Pipeline](https://img.shields.io/badge/pipeline-Fetch→Process→Curate→Design-blue)  
For engineers, researchers, and PMs who want to stay on top of AI/ML without manually scanning RSS.

---

## What the digest looks like

- **Top Picks:** 3–5 high-relevance items (score ≥ 8) with a one-sentence takeaway, key results, and tags.
- **Signals:** Short items (Release / Engineering Blog / Framework Update / Paper / General News) for a quick scan.
- **Global Summary:** A short LLM-generated summary of the day’s or week’s trends.
- **Weekends:** Extra “Trending Deep Dive” and more items.

Sources include: OpenAI, Anthropic, DeepMind, Google AI, Meta AI, Hugging Face, GitHub Blog, Cursor, LangChain, LlamaIndex, Netflix/Spotify/LinkedIn engineering blogs, Berkeley/Stanford/MIT AI, ArXiv (LLM/Agent/RAG/multimodal, etc.), and HN highlights. You can add or remove RSS feeds and interest keywords in `modules/config.py`.

---

## Stack and pipeline

```
RSS + ArXiv + HN  →  Fetcher (parallel fetch)
       →  Processor (Gemini summarize / score / classify)
       →  Curator (weekday vs weekend strategy, backlog, Top Picks + Signals)
       →  Designer (Jinja2 HTML)
       →  daily_digest.html → email (e.g. GitHub Actions + SMTP)
```

- **Fetcher:** Async multi-RSS + ArXiv API, time-window filter, optional domain exclusion.
- **Processor:** Each item goes through Gemini for structured summary, 1–10 relevance score, and signal type (Release / Engineering Blog / Framework Update / Paper / General News).
- **Curator:** Weekday = fewer items + backlog; weekend = more items + clear backlog; picks Top Picks and Signals by score and category.
- **Designer:** HTML email template; open locally or send via CI.

---

## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/collect-info-agent.git
cd collect-info-agent
pip install -r requirements.txt
```

1. **Env:** Set `GEMINI_API_KEY` (required).
2. **Run once:** `python orchestrator.py` — writes `daily_digest.html` in the repo root.
3. **Email:** Use the [GitHub Actions workflow](.github/workflows/daily_digest.yml) on schedule or push; set secrets `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_RECIPIENT` to send the digest by email.

To customize interests, RSS feeds, or ArXiv query, edit `USER_INTERESTS`, `RSS_FEEDS`, and `ARXIV_QUERY` in `modules/config.py`.

---

## Project layout

| Path | Description |
|------|-------------|
| `orchestrator.py` | Main flow: fetch → process → curate → summarize → render |
| `modules/fetcher.py` | RSS + ArXiv + time window |
| `modules/processor.py` | Gemini summarize, score, classify |
| `modules/curator.py` | Curation logic, backlog, weekday/weekend |
| `modules/designer.py` | HTML email template rendering |
| `modules/config.py` | RSS list, interests, ArXiv query, excluded domains |
| `templates/email_template.html` | Email HTML template |
| `.github/workflows/daily_digest.yml` | Daily schedule + manual trigger + send email |

---

## License

MIT.

---

## Spreading the word

- **GitHub:** Add **Topics** in About (e.g. `ai`, `newsletter`, `rss`, `digest`, `llm`, `research`, `automation`) so the repo shows up in search.
- **Social / communities:** Post the repo link with a one-liner (e.g. “I get a daily AI research digest in my inbox from this open-source agent”) on Reddit, X, 即刻, 知乎, HN, or in groups. A screenshot of `daily_digest.html` helps.
- **Copy-paste ready text** for Reddit, X, HN, 即刻, 知乎, 公众号, and groups is in [SHARE.md](SHARE.md).

Fork it, tweak RSS and interests, and it becomes *your* daily digest. Issues and PRs welcome.
