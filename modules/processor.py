# modules/processor.py
import os
import json
try:
    from google import genai
except ImportError:
    try:
        import google.genai as genai
    except ImportError:
        raise ImportError("Could not find 'google-genai' package. Please run: pip install google-genai")
from typing import Dict, Any

class Processor:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)
        # Correct model ID from list_models.py
        self.model_name = "gemini-3-flash-preview" 

    def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends the item content/summary to Gemini for scoring and summarization.
        """
        prompt = f"""
        You are a research assistant for a Senior ML Engineer.
        Your goal is to analyze the following article/paper and extract key information.
        The user is interested in: Vibe Coding, RAG (Retrieval-Augmented Generation), and LLM Agents.

        Title: {item.get('title')}
        Source: {item.get('source')}
        Content/Summary: {item.get('summary')}

        Please provide a JSON response with the following fields:
        - summary: A concise technical summary (2-3 sentences).
        - relevance_score: An integer from 1 to 10 based on the user's interests. 10 is a direct match (e.g., a new RAG technique), 1 is irrelevant.
        - one_sentence_takeaway: A snappy, single-sentence takeaway.
        - tags: A list of 3-5 keywords.

        Output strictly valid JSON.
        """

        try:
            # New generate_content API structure
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            
            # The response.text might contain the JSON
            result = json.loads(response.text)
            
            # CRITICAL FIX: Sometimes Gemini returns [ {...} ] instead of {...}
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            
            if not isinstance(result, dict):
                result = {}

            # Merge result into item
            item['processed'] = result
            return item
        except Exception as e:
            print(f"Error processing {item.get('title')}: {e}")
            item['processed'] = {
                "summary": "Error processing summary.",
                "relevance_score": 0,
                "one_sentence_takeaway": "Error.",
                "tags": []
            }
            return item

    def process_batch(self, items: list) -> list:
        processed_items = []
        for item in items:
            processed_items.append(self.process_item(item))
        return processed_items

    def generate_global_summary(self, items: list) -> str:
        """
        Synthesizes a master summary from the top items.
        """
        if not items:
            return ""
        
        # Take the best items as context
        context = "\n".join([f"- {i['title']}: {i['processed']['one_sentence_takeaway']}" for i in items[:8]])
        
        prompt = f"""
        You are a lead researcher summarizing today's key breakthroughs in AI (RAG, Agents, Vibe Coding).
        Based on the following titles and takeaways, write a single, authoritative, and snappy executive summary (The Signal). 
        It should be 3-4 sentences long and sound professional like the AlphaSignal newsletter.

        Context:
        {context}

        The Signal:
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text.strip()
            # Handle potential markdown wrapper
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            return text
        except Exception as e:
            print(f"Error generating global summary: {e}")
            return "Breaking updates in RAG and Agentic systems continue to push the boundaries of LLM capabilities."

    def generate_trending_topics(self, items: list) -> dict:
        """
        Identifies trending themes and writes a deep dive for Saturday.
        """
        if not items:
            return {"topic": "AI Market Consolidation", "deep_dive": "This week saw continued refinement of RAG and Agentic frameworks..."}

        # Context from all items in the week
        context = "\n".join([f"- {i['title']}: {i['processed'].get('summary', '')}" for i in items])

        prompt = f"""
        You are an AI Industry Analyst writing for the AlphaSignal Saturday Deep Dive.
        Analyze the following research papers and blog posts from the past week and:
        1. Identify the single most significant "Trending Topic".
        2. Write a 200-word "Deep Dive" analysis on why this trend matters for ML engineers.

        Context:
        {context}

        Respond ONLY in JSON format:
        {{
            "topic": "The trending name",
            "deep_dive": "The detailed analysis"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error generating trending topics: {e}")
            return {"topic": "Agentic Orchestration", "deep_dive": "A significant trend this week has been the emergence of more robust agentic orchestration layers, moving from simple LLM wrappers to complex, stateful systems."}
