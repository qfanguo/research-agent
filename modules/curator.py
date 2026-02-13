# modules/curator.py
import json
import os
import datetime
from typing import List, Dict, Any

BACKLOG_FILE = "backlog.json"

class Curator:
    def __init__(self):
        pass

    def load_backlog(self) -> List[Dict[str, Any]]:
        if os.path.exists(BACKLOG_FILE):
            with open(BACKLOG_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_backlog(self, items: List[Dict[str, Any]]):
        with open(BACKLOG_FILE, 'w') as f:
            json.dump(items, f, indent=2)

    def curate(self, items: List[Dict[str, Any]], is_weekend: bool = False) -> Dict[str, Any]:
        """
        Curates items based on relevance and day of the week.
        """
        # Load backlog if weekend
        backlog = self.load_backlog() if is_weekend else []
        
        # Combine current items with backlog if it's the weekend or we need to manage backlog
        # First, deduplicate all available items (current + backlog) by link
        all_pool_raw = items + (backlog if is_weekend else backlog) # Always consider backlog for potential cleanup? No, usually we just append.
        # Let's simple: 
        # Weekday: pool = items. Backlog remains (will be appended to).
        # Weekend: pool = items + backlog. Backlog cleared.
        
        all_pool = []
        seen_links = set()
        
        # Priority to new items, then backlog? Or score?
        # Let's merge them.
        sources = [items]
        if is_weekend:
            sources.append(backlog)
            
        for source in sources:
            for item in source:
                if item['link'] not in seen_links:
                    all_pool.append(item)
                    seen_links.add(item['link'])
        
        # Filter by minimal relevance to reduce noise
        valid_items = [i for i in all_pool if i.get('processed', {}).get('relevance_score', 0) >= 4]
        
        # Sort by score
        valid_items.sort(key=lambda x: x.get('processed', {}).get('relevance_score', 0), reverse=True)

        if is_weekend:
            # Weekend Strategy: 
            # 1. Trending Topics (This would require more complex clustering, for now we just take the highest scores)
            # 2. Deep Dive (Highest scored item)
            # 3. Everything else valuable
            
            selected = valid_items # Take all valid items for the weekend digest? Or maybe top 30?
            # Let's say top 30 for weekend to catch up.
            selected = selected[:30]
            
            # Clear backlog
            self.save_backlog([])
            
            return {
                "type": "weekend",
                "top_story": selected[0] if selected else None,
                "items": selected[1:],
                "trending": [] # Placeholder for future implementation
            }
        else:
            # Weekday Strategy: Max 15 items.
            selected = valid_items[:15]
            remaining = valid_items[15:]
            
            # Add unselected valid items to backlog (plus any existing backlog if we ignored it today)
            # We need to load the existing backlog to append to it if we didn't use it today.
            existing_backlog = self.load_backlog()
            
            # Avoid duplicates in backlog (dedupe by link)
            current_links = {i['link'] for i in existing_backlog}
            new_backlog = existing_backlog
            for item in remaining:
                if item['link'] not in current_links:
                    new_backlog.append(item)
                    current_links.add(item['link'])
            
            self.save_backlog(new_backlog)
            
            return {
                "type": "weekday",
                "items": selected
            }
