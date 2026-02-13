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
        
        # Merge items and backlog
        # Items are current fetches, backlog is older stuff
        for item in items:
            if isinstance(item, dict) and item.get('link') not in seen_links:
                all_pool.append(item)
                seen_links.add(item['link'])
        
        if is_weekend:
            for item in backlog:
                if isinstance(item, dict) and item.get('link') not in seen_links:
                    all_pool.append(item)
                    seen_links.add(item['link'])
        
        # Filter by minimal relevance to reduce noise
        valid_items = []
        for i in all_pool:
            if not isinstance(i, dict):
                continue
            
            processed = i.get('processed', {})
            # CRITICAL FIX: Ensure 'processed' is a dict. Sometimes AI returns a singleton list.
            if isinstance(processed, list) and len(processed) > 0:
                processed = processed[0]
            
            if not isinstance(processed, dict):
                processed = {}
                
            score = processed.get('relevance_score', 0)
            if score >= 4:
                # Update item with the possibly flattened dict to avoid issues later
                i['processed'] = processed
                valid_items.append(i)
        
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
            
            # High-Fidelity Categorization
            top_paper = next((i for i in selected if i.get('type') == 'paper'), None)
            top_repo = next((i for i in selected if i.get('type') == 'repo'), None)
            top_news = next((i for i in selected if i.get('type') == 'blog' and i != top_paper and i != top_repo), None)
            
            tops = [i for i in [top_paper, top_repo, top_news] if i]
            signals = [i for i in selected if i not in tops]

            return {
                "type": "weekend",
                "top_news": top_news,
                "top_repo": top_repo,
                "top_paper": top_paper,
                "signals": signals[:15], # More signals for weekend
                "items": selected,
                "trending": [] 
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
            
            # High-Fidelity Categorization
            top_paper = next((i for i in selected if i.get('type') == 'paper'), None)
            top_repo = next((i for i in selected if i.get('type') == 'repo'), None)
            top_news = next((i for i in selected if i.get('type') == 'blog' and i != top_paper and i != top_repo), None)
            
            # The "Top Items" list to exclude from signals
            tops = [i for i in [top_paper, top_repo, top_news] if i]
            signals = [i for i in selected if i not in tops]

            return {
                "type": "weekday",
                "top_news": top_news,
                "top_repo": top_repo,
                "top_paper": top_paper,
                "signals": signals[:10], # Max 10 signals to keep it concise
                "items": selected
            }
