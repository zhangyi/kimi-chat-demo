"""
Kimi-K2.5 简单聊天应用 v0.1
基于 AiHubMix API
单次对话版本 - 无循环
"""

import os
from openai import OpenAI

# 参考 https://aihubmix.com/model/kimi-k2.5
# 初始化客户端
# 请将 <AIHUBMIX_API_KEY> 替换为你在 AiHubMix 生成的密钥
# 或者设置环境变量 AIHUBMIX_API_KEY
client = OpenAI(
    api_key=os.environ.get("AIHUBMIX_API_KEY"),
    base_url="https://aihubmix.com/v1",
)

def chat_with_kimi_once():
    """单次对话函数 - 无循环"""
    print("=" * 50)
    print("🤖 Kimi-K2.5 聊天助手 v0.1 (单次对话)")
    print("=" * 50)
    
    # 获取用户输入
    user_input = input("👤 请输入你的问题: ").strip()
    
    # 跳过空输入
    if not user_input:
        print("❌ 输入为空，程序结束。")
        return
    
    # 消息
    messages = [{"role": "user", "content": user_input}]

    # 调用 Kimi API
    print("\n🤖 Kimi: ", end="", flush=True)
    response = client.chat.completions.create(
        model="kimi-k2.5",
        messages=messages,
        temperature=0.1,
        max_tokens=2000,
    )
    
    # 获取回复
    assistant_reply = response.choices[0].message.content
    print(assistant_reply)

if __name__ == "__main__":   
    chat_with_kimi_once()
