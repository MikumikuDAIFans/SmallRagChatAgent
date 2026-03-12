import requests
import json
import time

url = "http://127.0.0.1:8000/chat"
payload = {
    "session_id": "test_verification",
    "query": "介绍一下ArtiMaker支持的文件格式"
}

print("Testing updated server...")
try:
    # Retry loop in case server is still starting up
    for i in range(5):
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                print("Response received!")
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
                break
        except requests.exceptions.ConnectionError:
            print(f"Server not ready, retrying ({i+1}/5)...")
            time.sleep(2)
    else:
        print("Failed to connect to server after retries.")
except Exception as e:
    print("Request failed:", e)
