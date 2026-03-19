"""
Kimi-K2.5 简单聊天应用 v4.0
基于 AiHubMix API
支持流式输出
"""

import os
import sys
import time
import threading
from openai import OpenAI

# 参考 https://aihubmix.com/model/kimi-k2.5
# 初始化客户端
# 请将 <AIHUBMIX_API_KEY> 替换为你在 AiHubMix 生成的密钥
# 或者设置环境变量 AIHUBMIX_API_KEY
client = OpenAI(
    api_key=os.environ.get("AIHUBMIX_API_KEY"),
    base_url="https://aihubmix.com/v1",
)


class LoadingAnimation:
    """Loading 动画显示"""
    def __init__(self):
        self.running = False
        self.thread = None
        self.chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def _animate(self):
        """播放动画"""
        index = 0
        while self.running:
            sys.stdout.write(f"\r🤖 Kimi: {self.chars[index]} 思考中...")
            sys.stdout.flush()
            index = (index + 1) % len(self.chars)
            time.sleep(0.1)
    
    def start(self):
        """开始动画"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._animate, daemon=True)
            self.thread.start()
    
    def stop(self, clear=True):
        """停止动画"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=0.5)
            if clear:
                # 清除 loading 行
                sys.stdout.write('\r' + ' ' * 30 + '\r')
                sys.stdout.flush()


def chat_with_kimi():
    """流式输出的命令行聊天函数"""
    print("=" * 50)
    print("🤖 Kimi-K2.5 聊天助手 v4.0 (流式输出)")
    print("=" * 50)
    print("输入你的问题，按回车发送。输入 'quit' 或 'exit' 退出。")
    print("-" * 50)
    
    # 存储对话历史
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
            
            # 跳过空输入
            if not user_input:
                continue
            
            # 添加用户消息到历史
            messages.append({"role": "user", "content": user_input})
            
            # 调用 Kimi API（流式输出）
            stream = client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
                stream=True,  # 开启流式输出
            )
            
            # 开始 loading 动画
            loading = LoadingAnimation()
            loading.start()
            
            # 流式接收并打印回复
            assistant_reply = ""
            first_content = True
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    # 首次收到内容时，停止 loading
                    if first_content:
                        loading.stop(clear=True)
                        print("\n🤖 Kimi: ", end="", flush=True)
                        first_content = False
                    
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    assistant_reply += content
            
            # 确保 loading 已停止
            loading.stop(clear=False)
            
            if not assistant_reply:
                # 如果没有收到任何内容
                loading.stop(clear=True)
                print("\n⚠️ Kimi: 未收到回复，请重试。")
            else:
                print()  # 换行
            
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
