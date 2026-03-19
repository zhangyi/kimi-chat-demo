"""
Kimi-K2.5 简单聊天应用 v2.0
基于 AiHubMix API
支持存储对话历史 - 多轮对话
"""

import os
import json
from openai import OpenAI

# 参考 https://aihubmix.com/model/kimi-k2.5
# 初始化客户端
# 请将 <AIHUBMIX_API_KEY> 替换为你在 AiHubMix 生成的密钥
# 或者设置环境变量 AIHUBMIX_API_KEY
client = OpenAI(
    api_key=os.environ.get("AIHUBMIX_API_KEY"),
    base_url="https://aihubmix.com/v1",
)

# 对话历史文件
HISTORY_FILE = "chat_history.json"


def load_history():
    """加载对话历史"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(messages):
    """保存对话历史"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def clear_history():
    """清空对话历史"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        print("🗑️ 对话历史已清空！")
    else:
        print("📭 没有历史记录可清空。")


def show_history():
    """显示对话历史"""
    messages = load_history()
    if not messages:
        print("📭 暂无对话历史。")
        return
    
    print("\n" + "=" * 50)
    print("📜 对话历史")
    print("=" * 50)
    for i, msg in enumerate(messages):
        role = "👤 你" if msg["role"] == "user" else "🤖 Kimi"
        content = msg["content"]
        # 截断过长内容
        if len(content) > 100:
            content = content[:100] + "..."
        print(f"{i+1}. {role}: {content}")
    print("=" * 50)


def chat_with_kimi():
    """带历史记录的命令行聊天函数"""
    print("=" * 50)
    print("🤖 Kimi-K2.5 聊天助手 v2.0 (多轮对话)")
    print("=" * 50)
    print("输入你的问题，按回车发送。")
    print("命令: 'quit'退出 | 'history'查看历史 | 'clear'清空历史")
    print("-" * 50)
    
    # 加载历史对话
    messages = load_history()
    
    # 如果没有历史，添加系统提示
    if not messages:
        messages = [
            {"role": "system", "content": "你是一个有帮助的AI助手，请用友好、清晰的方式回答用户的问题。"}
        ]
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()
            
            # 检查退出条件
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("\n👋 再见！感谢使用 Kimi 聊天助手！")
                break
            
            # 检查命令
            if user_input.lower() in ['history', '历史', 'h']:
                show_history()
                continue
            elif user_input.lower() in ['clear', '清空', 'c']:
                clear_history()
                messages = [
                    {"role": "system", "content": "你是一个有帮助的AI助手，请用友好、清晰的方式回答用户的问题。"}
                ]
                continue
            
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
            
            # 保存历史
            save_history(messages)
            
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            print("请检查 API Key 是否正确，或网络连接是否正常。")


if __name__ == "__main__":   
    chat_with_kimi()
