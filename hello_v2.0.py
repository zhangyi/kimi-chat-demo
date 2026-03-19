"""
Kimi-K2.5 简单聊天应用
基于 AiHubMix API
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

def chat_with_kimi():
    """简单的命令行聊天函数"""
    print("=" * 50)
    print("🤖 Kimi-K2.5 聊天助手")
    print("=" * 50)
    print("输入你的问题，按回车发送。输入 'quit' 或 'exit' 退出。")
    print("-" * 50)
    
    # 存储对话历史
    messages = [
        {"role": "system", "content": "用最简短的语言回复内容"}
    ]
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()
            
            # 检查退出条件
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("\n👋 再见！感谢使用 Kimi 聊天助手！")
                break
            
            # 跳过空输入
            if not user_input:
                continue
            
            # 添加用户消息到历史
            messages.append({"role": "user", "content": user_input})
            
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
            
            # 添加助手回复到历史
            messages.append({"role": "assistant", "content": assistant_reply})
            
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            print("请检查 API Key 是否正确，或网络连接是否正常。")

if __name__ == "__main__":   
    chat_with_kimi()