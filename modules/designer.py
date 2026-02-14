# modules/designer.py
import os
from jinja2 import Environment, FileSystemLoader
import datetime
import re
from . import config

class Designer:
    def __init__(self, template_dir="templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template("email_template.html")

    def render(self, data: dict, global_summary: str = None, trending_info: dict = None) -> str:
        """
        Renders the HTML digest.
        data: Dict returned by Curator.
        """
        # Calculate read time (approx 200 wpm)
        total_words = 0
        detailed_items = data.get('detailed_items', [])
        signals = data.get('signals', [])
        
        # Clean markdown from global summary if present
        if global_summary:
            global_summary = global_summary.replace('**', '')
            
        if trending_info:
            # Plan HTML is already formatted by Processor
            pass

        for item in detailed_items:
            processed = item.get('processed', {})
            summary = processed.get('summary', '')
            
            # Entities to highlight orange (AlphaSignal style)
            # This is a heuristic - we highlight capitalized words or specific tech terms
            def highlight_entities(text):
                # Common tech names + User Interests
                tech_terms = ['Claude', 'Gemini', 'GPT', 'OpenAI', 'Anthropic', 'Google', 'Meta', 'Meta AI', 'RAG', 'Agent', 'Llama', 'NVIDIA', 'LLM', 'DeepMind']
                # Add user interests to highlight list
                tech_terms.extend(config.USER_INTERESTS)
                
                # Deduplicate
                tech_terms = list(set(tech_terms))
                # Sort by length descending to match longest terms first
                tech_terms.sort(key=len, reverse=True)
                
                # Single regex for all terms
                pattern = r'\b(' + '|'.join(map(re.escape, tech_terms)) + r')\b'
                return re.sub(pattern, r'<span class="highlight-orange">\1</span>', text, flags=re.IGNORECASE)

            if summary:
                processed['summary_html'] = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', summary).replace('\n', '<br>')
                total_words += len(summary.split())
            
            takeaway = processed.get('one_sentence_takeaway', '')
            if takeaway:
                processed['takeaway_clean'] = takeaway.replace('**', '')
                # Process takeaway with orange highlights
                processed['takeaway_html'] = highlight_entities(takeaway.replace('**', ''))

        for item in signals:
            processed = item.get('processed', {})
            takeaway = processed.get('one_sentence_takeaway', '')
            if takeaway:
                processed['takeaway_clean'] = takeaway.replace('**', '')
                total_words += len(takeaway.split())
            
        read_time_val = max(1, round(total_words / 200))
        # Format read time like AlphaSignal (e.g. 4 min 29 sec)
        # We'll just simulate the seconds for flavor or keep it simple.
        import random
        read_time_str = f"{read_time_val} min {random.randint(10, 55)} sec"
        
        # Prepare summary groups
        # We need to group detailed items by category for the template
        # { "Top News": [item1, item2], "Top Paper": [item3] }
        category_map = {}
        for item in detailed_items:
            cat = item.get('display_category', 'Top News')
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(item)
            
        # Define a consistent order for categories
        category_order = ["Top News", "Top Paper", "Top Repo", "Top Video", "Top Blog"]
        sorted_categories = []
        for cat in category_order:
            if cat in category_map:
                sorted_categories.append({"name": cat, "content_items": category_map[cat]})
        
        # Add any remaining categories not in the explicit order
        for cat in category_map:
            if cat not in category_order:
                sorted_categories.append({"name": cat, "content_items": category_map[cat]})

        context = {
            "date": datetime.datetime.now().strftime("%B %d, %Y"),
            "read_time": read_time_str,
            "detailed_items": detailed_items, # Keep raw list just in case
            "grouped_items": sorted_categories, # New grouped structure
            "signals": signals,
            "global_summary": global_summary,
            "trending_info": trending_info,
            "items": data.get('items', [])
        }
        
        return self.template.render(context)
