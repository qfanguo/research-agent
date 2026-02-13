# modules/designer.py
import os
from jinja2 import Environment, FileSystemLoader
import datetime

class Designer:
    def __init__(self, template_dir="templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template("email_template.html")

    def render(self, data: dict) -> str:
        """
        Renders the HTML digest.
        data: Dict returned by Curator.
        """
        # Calculate read time (approx 200 wpm)
        total_words = 0
        if data.get('top_story'):
            total_words += len(data['top_story']['processed']['summary'].split())
        for item in data.get('items', []):
            total_words += len(item['processed']['summary'].split())
        
        read_time = max(1, round(total_words / 200))
        
        context = {
            "date": datetime.datetime.now().strftime("%B %d, %Y"),
            "read_time": read_time,
            "top_story": data.get('top_story'),
            "items": data.get('items', [])
        }
        
        return self.template.render(context)
