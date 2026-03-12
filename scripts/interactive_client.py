import requests
import sys
import time

# 配置
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
port = os.getenv("APP_PORT", 8000)
API_URL = f"http://127.0.0.1:{port}/chat"
SESSION_ID = f"test_user_{int(time.time())}" #生成一个唯一的会话ID

def main():
    print("=" * 60)
    print(f"RAG Agent 交互式测试终端")
    print(f"Server URL: {API_URL}")
    print(f"Session ID: {SESSION_ID}")
    print("输入 'exit' 或 'quit' 退出")
    print("输入 'reset' 或 'clear' 开启新会话（清空历史）")
    print("=" * 60)

    # 先检查一下服务是否通
    try:
        requests.get(API_URL.replace("/chat", "/docs"), timeout=2)
        print("✅ 服务连接成功！")
    except Exception:
        print("⚠️  无法连接到服务，请确保 Docker 容器已启动且端口映射为 8000:8000")
        print("   如果您的 Docker 部署在远程服务器，请修改脚本中的 API_URL")

    while True:
        try:
            query = input("\n👤 你: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                print("Bye!")
                break

            new_session = False
            if query.lower() in ['reset', 'clear']:
                print("🔄 正在开始新会话...")
                new_session = True
                query = "你好" # 发送一个默认问候以触发重置

            payload = {
                "session_id": SESSION_ID,
                "query": query,
                "new_session": new_session
            }

            print("🤖 Agent 思考中...", end="", flush=True)
            start_time = time.time()
            response = requests.post(API_URL, json=payload)
            duration = time.time() - start_time
            print(f"\r", end="")

            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Agent ({duration:.2f}s): {data['response']}")
                
                if data.get('references'):
                    print("\n   📚 参考文档:")
                    for ref in data['references']:
                        # 处理换行，只显示第一行，避免刷屏
                        ref_preview = ref.split('\n')[0][:60] + "..."
                        print(f"   - {ref_preview}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"\n❌ 错误: 无法连接到服务器。请检查 Docker 容器是否正在运行。")
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
