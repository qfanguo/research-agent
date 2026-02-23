# Share copy · Reddit, X, HN, 即刻, 知乎, 公众号, 群

Ready-to-paste text for each platform. Replace `[LINK]` with your repo URL.

---

## GitHub (About)

**Topics** (pick 5–7):

```
ai, newsletter, rss, digest, llm, research, automation, gemini, python
```

**Short description:**

```
Daily AI research digest: RSS + ArXiv, summarized by LLM, delivered by email
```

---

## Reddit

**Subreddits:** r/MachineLearning, r/LocalLLaMA, r/sideproject, r/SideProject (check each sub’s rules).

**Title (pick one):**

```
Show HN: Daily AI research digest – RSS + ArXiv, summarized by LLM, email delivery
```

```
I built an open-source agent that emails me a curated AI/ML digest every morning
```

**Post body (short):**

```
I wanted to keep up with AI/ML news and papers without scrolling RSS all day, so I built a small pipeline:

- Fetches RSS (OpenAI, Anthropic, Hugging Face, GitHub, Cursor, etc.) + ArXiv + HN
- Sends each item to Gemini for summary, relevance score (1–10), and category
- Curates into Top Picks + Signals, different strategy on weekdays vs weekends
- Renders HTML and sends one email per day (e.g. via GitHub Actions)

Stack: Python, Gemini API, Jinja2. You can fork it and change RSS feeds / interests in config.

Repo: [LINK]
```

---

## X (Twitter)

**Tweet (short, under 280 if possible):**

```
Daily AI research digest: RSS + ArXiv → Gemini summary → one email. Open-source, self-host. [LINK]
```

```
I get a curated AI/ML digest in my inbox every morning. Built a small agent: fetch RSS + papers, LLM summarize & score, email. Open source: [LINK]
```

```
Built an open-source agent that emails me a daily AI research digest (blogs + ArXiv + HN). Fork and tweak your own feeds. [LINK]
```

---

## Hacker News

**Submit URL:** https://news.ycombinator.com/submit

**Title (pick one):**

```
Show HN: Daily AI research digest – RSS + ArXiv, summarized by LLM, email delivery
```

```
Show HN: Open-source agent that emails a curated AI/ML digest every morning
```

**No need for a long post** — HN uses title + link. If you later comment, you can add:

```
I built this to avoid manually scanning dozens of RSS feeds. Pipeline: fetch RSS + ArXiv + HN → Gemini (summarize, score, classify) → curate by weekday/weekend → HTML email. Configurable feeds and interests in config.py. Runs on GitHub Actions on a schedule.
```

---

## 即刻 (Jike)

**一句梗（可直接发）：**

```
做了一个小 agent：每天自动抓 AI 博客和 ArXiv，用 LLM 摘要打分，早上发我一封邮件。再也不用自己刷 RSS 了，开源在这：[LINK]
```

```
每日 AI 研究摘要：RSS + ArXiv → Gemini 摘要 → 一封邮件。开源可自托管，可改自己的源和兴趣。[LINK]
```

---

## 知乎 (Zhihu)

**标题示例：**

```
我写了一个每天自动生成 AI 研究摘要并发邮件的开源项目
```

**正文（可缩成一段）：**

```
平时要跟的 AI 博客和论文太多，又不想天天刷 RSS，就写了一个小流水线：

- 自动抓取主流 AI 博客（OpenAI、Anthropic、Hugging Face、GitHub、Cursor 等）+ ArXiv 论文 + HN 热点
- 用 Gemini 对每条做摘要、打相关度分、分类（Release / 工程博客 / 框架更新 / 论文 / 综合新闻）
- 按工作日/周末不同策略精选成「Top Picks」+「Signals」，生成 HTML
- 每天定时跑（如 GitHub Actions），发一封邮件到邮箱

技术栈：Python、Gemini API、Jinja2。RSS 列表和兴趣关键词都在 config 里可改，fork 后就能变成你自己的每日摘要。

项目链接：[LINK]
```

---

## 公众号 (WeChat Official Account)

**标题：**

```
开源一个「每日 AI 研究摘要」小工具：RSS + 论文 + LLM，早上收一封邮件
```

**正文（简短版，可直接用）：**

```
平时要跟的 AI 动态太多，又不想天天刷 RSS，就写了一个小 agent：

每天自动抓取主流 AI 博客（OpenAI、Anthropic、Hugging Face、Cursor 等）、ArXiv 论文和 HN 热点，用 LLM 做摘要和打分，按相关度精选后生成一份 digest，早上发到邮箱。

开源可自托管，RSS 和兴趣都能在配置文件里改，fork 就能变成你自己的每日摘要。技术栈：Python、Gemini API、GitHub Actions。

项目地址：[LINK]
```

---

## 群 (微信群 / 技术群 / Discord / Slack)

**中文短句（复制即发）：**

```
我开源了一个每天自动生成 AI 研究摘要并发邮件的项目，RSS+ArXiv 用 LLM 摘要打分，可 fork 改自己的源。有兴趣可以看看 / 给个 Star：[LINK]
```

```
做了一个小工具：RSS+ArXiv 用 LLM 做每日摘要发邮件，代码在这，可以 fork 改成自己的源：[LINK]
```

**English (for Discord/Slack):**

```
Sharing an open-source agent that emails me a daily AI research digest (RSS + ArXiv, summarized by LLM). Fork and tweak your feeds: [LINK]
```

---

## Checklist

- [ ] GitHub About: Topics + Short description
- [ ] Reddit: 1–2 subs, title + body
- [ ] X: 1 tweet with [LINK]
- [ ] HN: Submit with title + repo URL
- [ ] 即刻: 1 条 + [LINK]
- [ ] 知乎: 标题 + 一段正文 + [LINK]
- [ ] 公众号: 标题 + 正文 + [LINK]
- [ ] 群: 一句中文或英文 + [LINK]

Replace `[LINK]` everywhere with your actual repo URL (e.g. `https://github.com/yourusername/collect-info-agent`).
