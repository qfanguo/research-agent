import asyncio
import os
import json
import re
try:
    from google import genai
except ImportError:
    try:
        import google.genai as genai
    except ImportError:
        raise ImportError("Could not find 'google-genai' package. Please run: pip install google-genai")
from typing import Dict, Any, List
from . import config

class Processor:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)
        # Correct model ID
        self.model_name = "gemini-3-flash-preview" 
        # Add a semaphore to limit concurrent API calls
        self.sem = asyncio.Semaphore(5)
        self.max_retries = 3 

    def _repair_json(self, text: str) -> str:
        """
        Fixes common AI JSON errors: trailing commas and improper LaTeX escapes.
        """
        # 1. Remove trailing commas before closing braces/brackets
        text = re.sub(r',\s*([\]}])', r'\1', text)
        
        # 2. Fix improper backslashes (common in ArXiv LaTeX math)
        # Avoid doubling if it's already doubled or part of a valid escape.
        # We look for a backslash that is:
        # - NOT preceded by another backslash (to avoid doubling valid \\)
        # - NOT followed by a valid JSON escape char [\"/bfnrtu]
        text = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', text)
        
        return text

    async def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends the item content/summary to Gemini for scoring and summarization (Async).
        """
        is_repo = "github.com" in item.get('link', '').lower()
        if is_repo:
            item['type'] = 'repo'
            item['display_category'] = "Top Repo"
        elif item.get('type') == 'paper':
            item['display_category'] = "Top Paper"
        elif item.get('type') == 'video':
            item['display_category'] = "Top Video"
        else:
            # Default RSS/Blogs to Top News for a cleaner look, or Top Blog if preferred.
            # AlphaSignal often uses "Top News".
            item['display_category'] = "Top News"

        raw_summary = item.get('summary', '')
        # Pre-process ArXiv math: Replace single backslashes in input to prevent AI from mimicking them.
        sanitized_summary = raw_summary.replace("\\", " ")

        prompt = f"""
        You are a research assistant for a Senior ML Engineer.
        Analyze the following article/paper and extract key information.
        Interests: {", ".join(config.USER_INTERESTS)}.

        Title: {item.get('title')}
        Source: {item.get('source')}
        Content: {sanitized_summary}

        Please provide a JSON response with:
        - summary: A structured technical summary consisting of 3-4 bulleted points (using \n before each point). Focus on architecture and impact. Use **bold** for key terms.
        - key_results: List of 5 concise bullet points.
        - relevance_score: Integer 1-10.
        - signal_type: One of ["Release", "Engineering Blog", "Framework Update", "Paper", "General News"].
          - "Release": Foundation Model releases (e.g. GLM-5, Qwen-Image), Major Product Launches, Business Updates from Major Labs (e.g. OpenAI testing ads).
          - "Engineering Blog": Tool Updates (e.g. Cursor, ElevenLabs), Deep Technical "How we built it", Industry Tweets (if applicable).
          - "Framework Update": Major library release (LangChain, LlamaIndex, HF).
          - "Paper": ArXiv papers AND Deep Research Blogs (e.g. DeepMind DeepThink, Google Research).
          - "General News": General commentary, opinion pieces, low-technical news.
        - one_sentence_takeaway: A snappy, subject-action-result takeaway (MAX 20 words). 
          CRITICAL: Start with the organization, university, or lead author (e.g., "DeepMind introduces...", "Stanford Research shows...", "OpenAI launches...").
        - lead_institution: String. If this is a paper, extract the primary university or lab name. Otherwise use the source name.
        - tags: List of 5 keywords.

        CRITICAL OUTPUT RULES:
        1. DO NOT use LaTeX math symbols.
        2. one_sentence_takeaway MUST start with an Entity/Institution name.
        3. summary MUST be formatted with clear line breaks (\n) and bullets.
        4. Output strictly valid, parsable JSON.
        5. PENALIZE PROMOTIONAL CONTENT: If the content is an event announcement, webinar, sales pitch, or a simple "join us" call to action, set relevance_score to 1-3. We want technical depth, not ads.
        """

        async with self.sem:
            for attempt in range(self.max_retries):
                try:
                    # Use async client for parallel processing
                    response = await self.client.aio.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config={
                            "response_mime_type": "application/json"
                        }
                    )
                    
                    text = response.text.strip()
                    repaired_text = self._repair_json(text)
                    result = json.loads(repaired_text)
                    
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]
                    
                    if not isinstance(result, dict):
                        result = {}

                    item['processed'] = result
                    return item
                    
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                         print(f"Error processing {item.get('title')}: {repr(e)}")
                         item['processed'] = {
                            "summary": f"Error processing content: {repr(e)}",
                            "relevance_score": 0,
                            "one_sentence_takeaway": "Error.",
                            "tags": []
                         }
                         return item

    async def process_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes a batch of items in parallel."""
        tasks = [self.process_item(item) for item in items]
        return await asyncio.gather(*tasks)

    async def generate_global_summary(self, items: List[Dict[str, Any]]) -> str:
        """Synthesizes a master summary from the top items (Async)."""
        if not items:
            return ""
        
        context_items = []
        for i in items[:8]:
            title = i.get('title', 'Untitled')
            takeaway = i.get('processed', {}).get('one_sentence_takeaway', 'No takeaway available')
            if title == 'Untitled':
                 print(f"Warning: Item missing title found in global summary generation: {i}")
            context_items.append(f"- {title}: {takeaway}")

        context = "\n".join(context_items)
        
        prompt = f"""
        You are a lead researcher summarizing today's key breakthroughs in AI (RAG, Agents, Vibe Coding).
        Write a single, authoritative, and snappy executive summary (The Signal) (3-4 sentences).

        Context:
        {context}
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating global summary: {e}")
            return "Breaking updates in RAG and Agentic systems continue to push the boundaries of LLM capabilities."

    async def generate_trending_topics(self, items: List[Dict[str, Any]]) -> dict:
        """Identifies trending themes and writes a personalized Saturday plan (Async)."""
        if not items:
            return {"plan_html": "<p>Relax and recharge! No major trends this week.</p>"}

        context_items = []
        for i in items[:20]:
            title = i.get('title', 'Untitled')
            summary = i.get('processed', {}).get('summary', 'No summary available')
            if title == 'Untitled':
                 print(f"Warning: Item missing title found in trending topics generation: {i}")    
            context_items.append(f"- {title}: {summary}")
        
        context = "\n".join(context_items)
        interests_str = ", ".join(config.USER_INTERESTS)

        prompt = f"""
        You are an elite productivity & learning coach for a Senior ML Engineer.
        User Interests: {interests_str}

        Based on this week's top research below, create a "Personalized Saturday Learning Plan".
        
        Context:
        {context}

        Output strictly a JSON object with a single key "plan_html".
        The value should be an HTML string (NO markdown, NO ```html``` blocks) representing the plan.
        
        HTML Format Requirements:
        - Use clean, semantic HTML.
        - Structure:
            <div class="saturday-plan">
                <p class="plan-intro">Here is your high-leverage learning plan for the weekend, curated for {interests_str}.</p>
                <div class="plan-item">
                    <span class="plan-time">Morning: Deep Dive</span>
                    <div class="plan-content">[Specific paper/repo to study based on trends] - Focus on [specific technical aspect].</div>
                </div>
                <div class="plan-item">
                    <span class="plan-time">Afternoon: Experimentation</span>
                    <div class="plan-content">[suggest a small experiment or code to write related to the morning topic].</div>
                </div>
                <div class="plan-item">
                    <span class="plan-time">Evening: Reflection</span>
                    <div class="plan-content">[A thought-provoking question or perspective to consider].</div>
                </div>
            </div>
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error generating Saturday plan: {e}")
            return {"plan_html": "<p>Could not generate plan due to an error.</p>"}
