import requests
import json

url = "http://127.0.0.1:8000/chat"
payload = {
    "session_id": "test_user_1",
    "query": "这个Agent怎么部署？"
}

try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("Response:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print("Error:", response.text)
except Exception as e:
    print("Request failed:", e)
