"""
Kimi-K2.5 任务拆解助手 v5.0 (互动执行版)
基于 AiHubMix API
单步执行：输出任务 → 本地执行 → 汇报结果 → 继续下一步
"""

import os
import json
import requests
import subprocess
from openai import OpenAI

# 参考 https://aihubmix.com/model/kimi-k2.5
# 初始化客户端
# 请将 <AIHUBMIX_API_KEY> 替换为你在 AiHubMix 生成的密钥
# 或者设置环境变量 AIHUBMIX_API_KEY
client = OpenAI(
    api_key=os.environ.get("AIHUBMIX_API_KEY"),
    base_url="https://aihubmix.com/v1",
)


# ========== 全局状态 ==========
results = {}          # 存储每步执行结果


# ========== System Prompt - 参考 WorkBuddy 风格 ==========
SYSTEM_PROMPT = """你是一个任务拆解与执行助手。

核心原则：直接行动 → 执行 → 反馈结果 → 继续

工作流程（每轮循环）：
1. 你输出一条待执行的步骤（JSON格式）
2. 本地执行该步骤
3. 执行完成后，将结果反馈给你
4. 你根据结果决定下一步操作

输出格式（每轮只输出一条）：
{
  "type": "text",
  "text": "描述这一步要做什么"
}
或
{
  "type": "tool-call",
  "tool": {"name": "工具名", "args": {...}}
}
或
{
  "type": "done",
  "summary": "任务完成总结"
}

支持的工具：
- write_to_file: 写入文件，参数: filename, content
- read_file: 读取文件，参数: filename
- web_fetch: 获取网页，参数: url
- execute_command: 执行命令，参数: command
- python_eval: 执行Python代码，参数: code
- web_search: 网络搜索，参数: query

重要规则：
- 每次只输出一条JSON，不要输出数组
- 使用 {step_N_result} 引用上一步结果
- 如果某步依赖上一步结果，必须等上一步执行完后再输出依赖步骤
- 工具执行结果会返回给你，继续输出下一步
- 完成后输出 {"type": "done", "summary": "..."} 结束任务

示例对话：
用户：帮我下载百度首页并统计字数
你：{"type": "tool-call", "tool": {"name": "web_fetch", "args": {"url": "https://www.baidu.com"}}}
（本地执行，返回结果给你）
你：{"type": "tool-call", "tool": {"name": "python_eval", "args": {"code": "text = '''{step_1_result}'''; result = {'char_count': len(text), 'line_count': len(text.split())}"}}}
（本地执行，返回结果给你）
你：{"type": "done", "summary": "百度首页字数统计完成：xxx字符，xxx行"}
"""


def replace_placeholders(text: str) -> str:
    """替换占位符 {step_N_result}"""
    for key, value in results.items():
        placeholder = f"{{{key}}}"
        if placeholder in text:
            text = text.replace(placeholder, str(value))
    return text


def exec_tool(tool_name: str, args: dict) -> str:
    """执行工具调用"""
    
    # 替换占位符
    args = {k: replace_placeholders(str(v)) for k, v in args.items()}
    
    try:
        if tool_name == "write_to_file":
            content = args.get("content", "")
            filepath = args.get("filename", args.get("filePath", "output.txt"))
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ 写入成功: {filepath}"
        
        elif tool_name == "read_file":
            filepath = args.get("filename", args.get("filePath"))
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return content[:2000] + "..." if len(content) > 2000 else content
        
        elif tool_name == "web_fetch":
            url = args.get("url")
            r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            content = r.text[:3000]
            return content + "..." if len(r.text) > 3000 else content
        
        elif tool_name == "execute_command":
            cmd = args.get("command", args.get("cmd"))
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout or result.stderr or "命令执行完成"
            return output[:2000] + "..." if len(output) > 2000 else output
        
        elif tool_name == "python_eval":
            code = args.get("code", args.get("expression"))
            local_vars = {}
            exec(code, {}, local_vars)
            result = local_vars.get("result", local_vars.get("output", "执行完成"))
            return str(result)
        
        elif tool_name == "web_search":
            query = args.get("query", "")
            r = requests.get(f"https://www.baidu.com/s?wd={query}", timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            # 提取搜索结果标题
            titles = []
            import re
            matches = re.findall(r'<a[^>]+class="result_title[^>]*>([^<]+)</a>', r.text[:5000])
            for m in matches[:5]:
                titles.append(m.strip())
            if titles:
                return "搜索结果: " + " | ".join(titles)
            return r.text[:500] + "..."
        
        else:
            return f"❌ 未知工具: {tool_name}"
    
    except Exception as e:
        return f"❌ 执行错误: {str(e)}"


def parse_step(json_str: str) -> dict:
    """解析单条 JSON 步骤"""
    json_str = json_str.strip()
    
    # 尝试找到完整的 JSON 对象
    start = json_str.find('{')
    end = json_str.rfind('}')
    
    if start == -1 or end == -1:
        return None
    
    full_json = json_str[start:end+1]
    
    try:
        return json.loads(full_json)
    except json.JSONDecodeError:
        return None


def run_task_loop(messages: list) -> None:
    """任务执行主循环：执行一步 → 汇报结果 → 继续下一步"""
    global results
    
    step_count = 0
    max_steps = 20  # 防止无限循环
    
    while step_count < max_steps:
        step_count += 1
        
        # 调用模型获取下一步（流式输出）
        stream = client.chat.completions.create(
            model="kimi-k2.5",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            stream=True,
        )
        
        # 流式接收响应
        assistant_msg = ""
        print(f"\n{'='*50}")
        print("🤖 Kimi: ", end="", flush=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                assistant_msg += content
        print()  # 换行
        
        # 添加助手回复到对话历史
        messages.append({"role": "assistant", "content": assistant_msg})
        
        # 解析步骤
        step = parse_step(assistant_msg)
        
        if not step:
            print("⚠️ 无法解析 JSON，继续等待...")
            continue
        
        # 处理不同类型的步骤
        if step.get("type") == "done":
            # 任务完成
            summary = step.get("summary", "任务完成")
            print(f"\n{'='*50}")
            print(f"🎉 任务完成: {summary}")
            break
        
        elif step.get("type") == "text":
            # 文本提示，直接继续
            text = step.get("text", "")
            print(f"💬 {text}")
            # 继续下一步，不需要执行工具
        
        elif step.get("type") == "tool-call":
            # 工具调用
            tool_name = step["tool"]["name"]
            args = step["tool"]["args"]
            
            print(f"🔧 执行工具: {tool_name}")
            print(f"📝 参数: {args}")
            
            # 执行工具
            step_result = exec_tool(tool_name, args)
            results[f"step_{step_count}_result"] = step_result
            
            print(f"📤 结果: {step_result[:300]}...")
            
            # 向模型汇报执行结果
            feedback = f"步骤 {step_count} 执行完成，结果: {step_result[:1500]}"
            messages.append({"role": "user", "content": feedback})
        
        else:
            print(f"⚠️ 未知步骤类型: {step}")
    
    if step_count >= max_steps:
        print(f"\n⚠️ 达到最大步骤数 {max_steps}，停止执行")


def chat_with_kimi():
    """主聊天函数"""
    print("=" * 50)
    print("🤖 Kimi-K2.5 任务拆解助手 v5.0")
    print(" 单步执行：输出 → 执行 → 反馈 → 继续")
    print("=" * 50)
    print("输入你的任务，按回车发送。输入 'quit' 或 'exit' 退出。")
    print("-" * 50)
    
    while True:
        try:
            # 推荐输入： 制订一份江浙沪8天7晚的旅游攻略
            user_input = input("\n👤 你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("\n👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 重置状态
            global results
            results = {}
            
            # 初始化对话
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
            
            # 开始任务执行循环
            run_task_loop(messages)
            
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":   
    chat_with_kimi()
