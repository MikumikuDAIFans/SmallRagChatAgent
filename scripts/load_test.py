import asyncio
import httpx
import time
import sys
import os
from dotenv import load_dotenv

load_dotenv()
port = os.getenv("APP_PORT", 8000)

URL = f"http://127.0.0.1:{port}/chat"
CONCURRENT_REQUESTS = 5

async def send_request(session_id, query):
    async with httpx.AsyncClient() as client:
        payload = {
            "session_id": session_id,
            "query": query,
            "new_session": True
        }
        start_time = time.time()
        try:
            response = await client.post(URL, json=payload, timeout=60.0)
            duration = time.time() - start_time
            if response.status_code == 200:
                print(f"✅ Session {session_id} finished in {duration:.2f}s")
                return duration
            else:
                print(f"❌ Session {session_id} failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Session {session_id} error: {e}")
            return None

async def main():
    print(f"🚀 Starting load test with {CONCURRENT_REQUESTS} concurrent requests...")
    
    tasks = []
    for i in range(CONCURRENT_REQUESTS):
        session_id = f"load_test_{i}"
        query = "你好" # Simple query to trigger full flow
        tasks.append(send_request(session_id, query))
    
    start_total = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_total
    
    valid_results = [r for r in results if r is not None]
    avg_time = sum(valid_results) / len(valid_results) if valid_results else 0
    
    print("="*40)
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Request Time: {avg_time:.2f}s")
    print(f"Successful Requests: {len(valid_results)}/{CONCURRENT_REQUESTS}")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())
