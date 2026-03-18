import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config.config import settings
from backend.base.llm_base import LLMBase
from backend.base.searxng_service import SearxngService
from backend.base.comfy_base import ComfyUIService

async def test_llm():
    print("\n--- Testing LLM ---")
    print(f"URL: {settings.LOCAL_LLM_URL}")
    print(f"Model: {settings.MODEL}")
    try:
        llm = LLMBase()
        # Test a simple generation
        response = await llm.generate_output("You are a helpful assistant.", "Say 'Hello, I am working!'")
        print(f"Response: {response}")
        if response:
            print("✅ LLM is working.")
        else:
            print("❌ LLM returned empty response.")
    except Exception as e:
        print(f"❌ LLM Test FAILED: {e}")

async def test_searxng():
    print("\n--- Testing Searxng ---")
    print(f"URL: {settings.SEARXNG_URL}")
    try:
        service = SearxngService()
        result = await service.search("Python news", payload={}, num_results=1)
        print(f"Found {len(result.search_items)} results.")
        if result.search_items:
            print(f"First result: {result.search_items[0].title}")
            print("✅ Searxng is working.")
        else:
            print("❌ Searxng returned no results.")
    except Exception as e:
        print(f"❌ Searxng Test FAILED: {e}")

async def test_comfyui():
    print("\n--- Testing ComfyUI ---")
    print(f"URL: {settings.COMFYUI_API_URL}")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.COMFYUI_API_URL}/view?filename=test.png", timeout=5.0)
            # We just check if we can connect to the server
            if response.status_code in [200, 404]: # 404 is fine, means server responded
                print("✅ ComfyUI server is reachable.")
            else:
                print(f"❌ ComfyUI returned status {response.status_code}")
    except Exception as e:
        print(f"❌ ComfyUI Test FAILED: {e}")

async def main():
    print("Starting Backend Services Verification...")
    await test_llm()
    await test_searxng()
    await test_comfyui()
    print("\nVerification complete.")

if __name__ == "__main__":
    asyncio.run(main())
