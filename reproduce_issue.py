
import asyncio
import os
from modules.processor import Processor

# Mock item that simulates an ArXiv paper with a GitHub link in the summary
mock_item = {
    "title": "DeepSeek-V3 Technical Report",
    "link": "https://arxiv.org/abs/2412.19437",
    "source": "ArXiv",
    "published": "2024-12-27T00:00:00+00:00",
    "type": "paper",
    "summary": "We present DeepSeek-V3... Code available at https://github.com/deepseek-ai/DeepSeek-V3"
}

async def main():
    print("Initializing Processor...")
    try:
        processor = Processor()
        
        print("Processing item...")
        # process_item modifies the item in place
        # We need to run it. However, it requires an API key.
        # To avoid making a real API call if possible, or just to test the pre-processing logic:
        # The logic is at the start of process_item.
        
        # Let's inspect the code of process_item again.
        # It sets display_category BEFORE the API call.
        
        # We can simulate the logic without the full class if we want, 
        # but importing the class ensures we test the actual code.
        # But we need to mock the API call or just check the item before it fails?
        # Actually, let's just copy the logic to verify our understanding, 
        # or subclass Processor to override the API call.
        
        # Let's just run the relevant logic snippet to verify behavior.
        item = mock_item.copy()
        is_repo = "github.com" in item.get('link', '').lower() or "github.com" in item.get('summary', '').lower()
        if is_repo:
            item['type'] = 'repo'
            item['display_category'] = "Top Repo"
        elif item.get('type') == 'paper':
            item['display_category'] = "Top Paper"
            
        print(f"Item Type: {item.get('type')}")
        print(f"Display Category: {item.get('display_category')}")
        
        if item.get('display_category') == "Top Repo" and "arxiv.org" in item['link']:
            print("ISSUE REPRODUCED: ArXiv paper classified as Top Repo.")
        else:
             print("Issue NOT reproduced.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
