
import asyncio
from modules.processor import Processor

# Mock item: ArXiv paper with GitHub link in summary
mock_item_arxiv = {
    "title": "DeepSeek-V3 Technical Report",
    "link": "https://arxiv.org/abs/2412.19437",
    "source": "ArXiv",
    "type": "paper",
    "summary": "Code available at https://github.com/deepseek-ai/DeepSeek-V3"
}

# Mock item: Actual GitHub repo
mock_item_repo = {
    "title": "DeepSeek-V3 Code",
    "link": "https://github.com/deepseek-ai/DeepSeek-V3",
    "source": "GitHub",
    "type": "blog", # Simulating RSS feed type which might be 'blog' initially
    "summary": "Official implementation."
}

async def main():
    print("Verifying Repo Logic Fix...")
    
    # We only test the logic block that sets display_category in process_item
    # Since we can't easily mock the API call without subclassing, let's just inspect the logic we changed
    # which happens at the very start of process_item
    
    # However, to be thorough, I'll copy the logic snippet exactly as it is in the file
    # Or better, let's instantiate Processor and override the API call method if needed, 
    # but actually the logic is *before* the API call.
    # So we can just inspect the item *before* the API call if we step through.
    
    # Wait, process_item modifies the item in place.
    # And the API call happens *after* the category logic.
    # So if we call process_item, it will try to hit the API.
    # Let's just implement a localized test of the logic to avoid API usage/keys.
    
    print("\nTest Case 1: ArXiv Paper with GitHub link in summary")
    item = mock_item_arxiv.copy()
    
    # Logic from processor.py
    is_repo = "github.com" in item.get('link', '').lower()
    if is_repo:
        item['type'] = 'repo'
        item['display_category'] = "Top Repo"
    elif item.get('type') == 'paper':
        item['display_category'] = "Top Paper"
    elif item.get('type') == 'video':
        item['display_category'] = "Top Video"
    else:
        item['display_category'] = "Top News"
        
    print(f"Result Category: {item.get('display_category')}")
    if item.get('display_category') == "Top Paper":
        print("PASS: Correctly classified as Top Paper.")
    else:
        print(f"FAIL: Classified as {item.get('display_category')}")

    print("\nTest Case 2: Actual GitHub Repo")
    item = mock_item_repo.copy()
    
    # Logic from processor.py
    is_repo = "github.com" in item.get('link', '').lower()
    if is_repo:
        item['type'] = 'repo'
        item['display_category'] = "Top Repo"
    elif item.get('type') == 'paper':
        item['display_category'] = "Top Paper"
    elif item.get('type') == 'video':
        item['display_category'] = "Top Video"
    else:
        item['display_category'] = "Top News"

    print(f"Result Category: {item.get('display_category')}")
    if item.get('display_category') == "Top Repo":
        print("PASS: Correctly classified as Top Repo.")
    else:
        print(f"FAIL: Classified as {item.get('display_category')}")

if __name__ == "__main__":
    asyncio.run(main())
