# orchestrator.py
import asyncio
import datetime
import os
import os
import sys
import json
import glob
from modules.fetcher import Fetcher
from modules.processor import Processor
from modules.curator import Curator
from modules.designer import Designer

LOG_DIR = "logs"

def cleanup_old_logs(days=7):
    """Deletes log files older than 'days'."""
    if not os.path.exists(LOG_DIR):
        return
    
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    # Pattern match for our log files
    for log_file in glob.glob(os.path.join(LOG_DIR, "digest_*.json")):
        try:
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff:
                os.remove(log_file)
                print(f"Deleted old log: {log_file}")
        except OSError as e:
            print(f"Error deleting {log_file}: {e}")

def save_daily_log(data):
    """Saves the curated data to a JSON log file."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"digest_{date_str}.json"
    filepath = os.path.join(LOG_DIR, filename)
    
    try:
        with open(filepath, 'w') as f:
            # Use default=str to handle datetime objects
            json.dump(data, f, indent=2, default=str)
        print(f"Daily log saved to {filepath}")
    except Exception as e:
        print(f"Failed to save log: {e}")

async def main():
    print(f"Starting Research Agent at {datetime.datetime.now()}")

    # Cleanup old logs
    cleanup_old_logs()

    weekday = datetime.datetime.now().weekday()
    is_weekend = (weekday == 5)
    
    print(f"Day is {weekday} (Is Weekend/Saturday mode: {is_weekend})")

    # 1. Fetch
    print("Stage 1: Fetching content in parallel...")
    fetcher = Fetcher()
    raw_items = await fetcher.fetch_all()
    print(f"Fetched {len(raw_items)} items.")

    if not raw_items:
        print("No items found. Generating empty digest.")
        # Generate an empty digest file so email can still be sent
        designer = Designer()
        html_content = designer.render(
            data={'detailed_items': [], 'items': [], 'signals': []}, 
            global_summary="No content found today.", 
            trending_info=None
        )
        output_file = "daily_digest.html"
        with open(output_file, "w") as f:
            f.write(html_content)
        print(f"Empty digest generated at {output_file}")
        return

    # 2. Process (Summarize & Score)
    print("Stage 2: Processing content with Gemini in parallel...")
    processor = Processor()
    processed_items = await processor.process_batch(raw_items)
    print("Processing complete.")

    # 3. Curate
    print("Stage 3: Curating content...")
    curator = Curator()
    curated_data = curator.curate(processed_items, is_weekend=is_weekend)
    
    # Save log of curated data (includes sources & relevance scores)
    save_daily_log(curated_data)
    
    # 4. Global Summary
    print("Stage 4: Generating Global Summary...")
    global_summary = await processor.generate_global_summary(curated_data.get('detailed_items', []))
    
    # 5. Saturday Special: Trending Deep Dive
    trending_info = None
    if is_weekend:
        print("Stage 5: Generating Weekly Deep Dive...")
        trending_info = await processor.generate_trending_topics(curated_data.get('items', []))

    # 6. Design
    print("Stage 6: Designing content...")
    designer = Designer()
    html_content = designer.render(
        data=curated_data, 
        global_summary=global_summary, 
        trending_info=trending_info
    )
    
    output_file = "daily_digest.html"
    with open(output_file, "w") as f:
        f.write(html_content)
    
    print(f"Digest generated at {output_file}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    asyncio.run(main())
