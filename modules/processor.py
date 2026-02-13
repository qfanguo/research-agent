# modules/processor.py
import os
import json
import google.generativeai as genai
from typing import Dict, Any

class Processor:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest') # Or gemini-1.5-flash for speed/cost

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
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            result = json.loads(response.text)
            
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
