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
        # Load backlog - now always load it to allow quiet day recovery on weekdays
        backlog = self.load_backlog()
        
        # Combine current items with backlog
        all_pool_raw = items + backlog
        
        all_pool = []
        seen_links = set()
        
        # Merge items and backlog, prioritizing new items
        for item in items:
            if isinstance(item, dict) and item.get('link') not in seen_links:
                all_pool.append(item)
                seen_links.add(item['link'])
        
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
            # CRITICAL FIX: Ensure 'processed' is a dict
            if isinstance(processed, list) and len(processed) > 0:
                processed = processed[0]
            
            if not isinstance(processed, dict):
                processed = {}
                
            score = processed.get('relevance_score', 0)
            if score >= 4:
                i['processed'] = processed
                valid_items.append(i)
        
        # Sort by score
        valid_items.sort(key=lambda x: x.get('processed', {}).get('relevance_score', 0), reverse=True)

        if is_weekend:
            # Weekend Strategy: 
            # 1. Trending Topics (Highest scores) - Max 30 candidates
            selected = valid_items[:30]
            
            # Clear backlog on weekend
            self.save_backlog([])
            
            # High-Fidelity V3 Categorization (Weekend)
            # Max 5 detailed for weekend
            candidates = [i for i in selected if i.get('processed', {}).get('relevance_score', 0) >= 8]
            top_detailed = candidates[:5]
            
            # Signals (Limit to total 20 items for weekend)
            remaining_for_signals = [i for i in selected if i not in top_detailed]
            signals = remaining_for_signals[:(20 - len(top_detailed))]

            return {
                "type": "weekend",
                "detailed_items": top_detailed,
                "signals": signals,
                "items": selected,
                "trending": [] 
            }
        else:
            # Weekday Strategy: Max 15 items total pool.
            selected_pool = valid_items[:15]
            
            # The new backlog should be all valid items that were NOT selected
            # Plus any items that were below the score threshold but already in backlog (to keep them for later)
            selected_links = {item['link'] for item in selected_pool}
            new_backlog = [item for item in all_pool if item['link'] not in selected_links]
            
            # Limit backlog size to prevent bloat (e.g. max 100 items)
            new_backlog = new_backlog[:100]
            self.save_backlog(new_backlog)
            
            # High-Fidelity V3 Categorization (Weekday)
            # 1. Identify high-scoring candidates (relevance >= 8)
            candidates = [i for i in selected_pool if i.get('processed', {}).get('relevance_score', 0) >= 8]
            
            # 2. Select up to 3 "Top Picks" for detailed view
            # Strategy: Try to get at least 1 item from each main category if available and high quality (>=7)
            # Categories: Top News, Top Paper, Top Repo, Top Video (defined in processor.py)
            
            top_detailed = []
            seen_links = set()
            
            # Sort candidates by score descending
            candidates.sort(key=lambda x: x.get('processed', {}).get('relevance_score', 0), reverse=True)

            # First pass: Get best of each category
            categories_to_find = ["Top News", "Top Paper", "Top Repo"]
            for cat in categories_to_find:
                for item in candidates:
                    if item.get('display_category') == cat and item['link'] not in seen_links:
                        # Ensure minimal quality for forced diversity
                        if item.get('processed', {}).get('relevance_score', 0) >= 7:
                            top_detailed.append(item)
                            seen_links.add(item['link'])
                            break # Found best for this category
            
            # Second pass: Fill remaining slots with highest scoring items regardless of category
            for item in candidates:
                if len(top_detailed) >= 5: # Increased to 5 per user request
                    break
                if item['link'] not in seen_links:
                    top_detailed.append(item)
                    seen_links.add(item['link'])
            
            # Re-sort final selection by score
            top_detailed.sort(key=lambda x: x.get('processed', {}).get('relevance_score', 0), reverse=True)
            
            # 3. Signals (Fill up to a STRICT total of 15 items for the newsletter)
            # System-Systematic Signal Selection (Relaxed Logic)
            # Prioritize specific signal types, but fallback to any valid item if scarce.
            # EXCLUSION: User requested NO PAPERS in Signals.
            
            signal_types = ["Release", "Engineering Blog", "Framework Update", "General News"]
            
            # Helper to check if item is a paper
            def is_paper(item):
                return item.get('type') == 'paper' or item.get('display_category') == 'Top Paper'
            
            # Primary candidates: specific types (excluding papers)
            primary_signals = [
                i for i in selected_pool 
                if i not in top_detailed 
                and not is_paper(i)
                and i.get('processed', {}).get('signal_type') in signal_types
            ]
            
            # Secondary candidates: anything else not in detailed (excluding papers)
            secondary_signals = [
                 i for i in selected_pool
                 if i not in top_detailed 
                 and i not in primary_signals
                 and not is_paper(i)
            ]
            
            # Combine and sort by score
            all_signals = primary_signals + secondary_signals
            all_signals.sort(key=lambda x: x.get('processed', {}).get('relevance_score', 0), reverse=True)
            
            # Take needed amount
            signals = all_signals[:(15 - len(top_detailed))]

            return {
                "type": "weekday",
                "detailed_items": top_detailed,
                "signals": signals,
                "items": selected_pool
            }
