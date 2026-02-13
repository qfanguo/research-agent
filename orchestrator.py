# orchestrator.py
import datetime
import os
import sys
from modules.fetcher import Fetcher
from modules.processor import Processor
from modules.curator import Curator
from modules.designer import Designer

def main():
    print(f"Starting Research Agent at {datetime.datetime.now()}")

    # 0. Determin Day
    # Monday is 0, Saturday is 5, Sunday is 6
    weekday = datetime.datetime.now().weekday()
    is_weekend = (weekday == 5) # Only Saturday as per requirements ("On Saturday...")
    # User said: "Saturday: Regular ones + trending...". 
    # If it is Sunday, maybe we shouldn't run? Or just run as weekday? 
    # Let's assume Saturday is the special day.
    
    print(f"Day is {weekday} (Is Weekend/Saturday mode: {is_weekend})")

    # 1. Fetch
    print("Stage 1: Fetching content...")
    fetcher = Fetcher()
    raw_items = fetcher.fetch_all()
    print(f"Fetched {len(raw_items)} items.")

    if not raw_items:
        print("No items found. Exiting.")
        return

    # 2. Process (Summarize & Score)
    print("Stage 2: Processing content with Gemini...")
    processor = Processor()
    processed_items = processor.process_batch(raw_items)
    print("Processing complete.")

    # 3. Curate
    print("Stage 3: Curating content...")
    curator = Curator()
    curated_data = curator.curate(processed_items, is_weekend=is_weekend)
    print(f"Curated {len(curated_data.get('items', []))} items (Top Story: {bool(curated_data.get('top_story'))})")

    # 3.5 Generate Global Summary
    print("Stage 3.5: Generating Global Summary...")
    global_summary = processor.generate_global_summary(curated_data.get('items', []))
    curated_data['global_summary'] = global_summary

    # 3.6 Saturday Special: Trending Deep Dive
    if is_weekend:
        print("Stage 3.6: Generating Weekly Deep Dive...")
        trending_info = processor.generate_trending_topics(curated_data.get('items', []))
        curated_data['trending_info'] = trending_info

    # 4. Design
    print("Stage 4: Designing content...")
    designer = Designer()
    html_content = designer.render(curated_data)
    
    output_file = "daily_digest.html"
    with open(output_file, "w") as f:
        f.write(html_content)
    
    print(f"Digest generated at {output_file}")

    # 5. Connect to Email Sending (Placeholder for GitHub Actions)
    # The GitHub Action will read this file and send it.

if __name__ == "__main__":
    main()
