#!/usr/bin/env python3
"""
DeepSeek 网页版聊天记录爬取工具
使用 Playwright 自动化浏览器，通过 DeepSeek 内部 API 获取指定会话的聊天记录。

功能：
  - 列出所有会话（--list）
  - 按会话 ID 精确获取（--id）
  - 按关键词筛选标题（--filter）
  - 交互模式：列出会话后手动选择编号
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装 Playwright: python3 -m pip install playwright")
    sys.exit(1)

DEEPSEEK_CHAT_URL = "https://chat.deepseek.com"
DEFAULT_OUTPUT = "deepseek_chat_history.json"
DEFAULT_STATE_FILE = "deepseek_browser_state.json"


def main():
    parser = argparse.ArgumentParser(
        description="爬取 DeepSeek 网页版指定会话的聊天记录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 列出所有会话（仅查看，不拉取消息）
  python3 deepseek_scraper.py --list

  # 按会话 ID 拉取指定会话
  python3 deepseek_scraper.py --id abc123 --id def456

  # 按标题关键词筛选并拉取
  python3 deepseek_scraper.py --filter "Python"

  # 交互模式：列出所有会话，手动选择要拉取的编号
  python3 deepseek_scraper.py

  # 指定输出文件
  python3 deepseek_scraper.py --id abc123 -o my_chat.json
        """,
    )
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"输出 JSON 文件路径 (默认: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--state-file",
        default=DEFAULT_STATE_FILE,
        help=f"浏览器状态文件，用于保存登录态 (默认: {DEFAULT_STATE_FILE})",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="仅列出所有会话（标题+ID），不拉取消息",
    )
    parser.add_argument(
        "--id", "-i",
        action="append",
        dest="session_ids",
        metavar="SESSION_ID",
        help="指定要拉取的会话 ID，可多次使用。例如: --id aaa --id bbb",
    )
    parser.add_argument(
        "--filter", "-f",
        metavar="KEYWORD",
        help="按标题关键词筛选会话（不区分大小写）",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    state_file = Path(args.state_file)

    existing_sessions = {}
    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if isinstance(existing_data, list):
                    for entry in existing_data:
                        session = entry.get("chat_session", {})
                        sid = session.get("id")
                        if sid:
                            existing_sessions[sid] = entry
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context_args = {"viewport": {"width": 1280, "height": 800}}

        if state_file.exists():
            print(f"加载浏览器状态: {state_file}")
            context = browser.new_context(storage_state=str(state_file), **context_args)
        else:
            context = browser.new_context(**context_args)

        page = context.new_page()
        print("正在打开 DeepSeek 聊天页面...")
        page.goto(DEEPSEEK_CHAT_URL, wait_until="domcontentloaded")

        print("\n" + "=" * 60)
        print("请在浏览器中登录你的 DeepSeek 账号")
        print("登录成功后，脚本将自动检测并继续")
        print("=" * 60 + "\n")

        try:
            page.wait_for_selector("textarea", timeout=300000)
            print("检测到登录成功！保存登录状态...")
            context.storage_state(path=str(state_file))
            print(f"登录状态已保存到: {state_file}\n")
        except Exception:
            print("错误: 等待登录超时（5分钟），请重试")
            browser.close()
            sys.exit(1)

        time.sleep(2)

        print("正在获取聊天会话列表...")
        all_sessions = fetch_all_sessions(page)

        if not all_sessions:
            print("未找到任何聊天会话，请确认账号中有聊天记录")
            browser.close()
            sys.exit(1)

        total = len(all_sessions)
        print(f"共发现 {total} 个聊天会话\n")

        # --- 确定要拉取的会话 ---
        if args.list:
            print_session_list(all_sessions)
            browser.close()
            return

        if args.session_ids:
            target_sessions = match_by_ids(all_sessions, args.session_ids)
        elif args.filter:
            target_sessions = match_by_keyword(all_sessions, args.filter)
        else:
            target_sessions = interactive_select(all_sessions)

        if not target_sessions:
            print("没有匹配到任何会话，退出。")
            browser.close()
            sys.exit(0)

        # --- 拉取选中会话的消息 ---
        selected_count = len(target_sessions)
        print(f"\n将拉取以下 {selected_count} 个会话的消息:\n")
        for i, s in enumerate(target_sessions, 1):
            sid = s.get("id", "?")
            title = s.get("title", "(无标题)")
            updated = format_timestamp(s.get("updated_at"))
            print(f"  {i}. [{sid}] {title}  (更新于: {updated})")
        print()

        results = []
        for idx, session in enumerate(target_sessions, 1):
            session_id = session.get("id")
            if not session_id:
                continue

            server_updated_at = session.get("updated_at", 0.0)
            existing_entry = existing_sessions.get(session_id)

            if existing_entry and not args.session_ids and not args.filter:
                existing_updated_at = existing_entry.get("chat_session", {}).get("updated_at", 0.0)
                if server_updated_at <= existing_updated_at:
                    results.append(existing_entry)
                    print(f"[{idx}/{selected_count}] {session.get('title', '(无标题)')} - 使用缓存（未更新）")
                    continue

            session_data = fetch_session_messages(page, session_id)
            if session_data:
                results.append(session_data)
                print(f"[{idx}/{selected_count}] {session.get('title', '(无标题)')} - 已获取")
            else:
                if existing_entry:
                    results.append(existing_entry)
                    print(f"[{idx}/{selected_count}] {session.get('title', '(无标题)')} - 获取失败，使用缓存")
                else:
                    print(f"[{idx}/{selected_count}] {session.get('title', '(无标题)')} - 获取失败")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n完成！共导出 {len(results)} 个会话，保存到: {output_path}")
        browser.close()


# ============================================================
# 会话筛选函数
# ============================================================

def print_session_list(sessions):
    """列出所有会话的标题和 ID"""
    print(f"{'序号':>4}  {'标题':<50} {'会话 ID':<24} {'更新时间'}")
    print("-" * 100)
    for i, s in enumerate(sessions, 1):
        sid = s.get("id", "?")
        title = s.get("title", "(无标题)")[:48]
        updated = format_timestamp(s.get("updated_at"))
        print(f"{i:>4}  {title:<50} {sid:<24} {updated}")
    print("-" * 100)
    print(f"共 {len(sessions)} 个会话")


def match_by_ids(sessions, ids):
    """按会话 ID 精确匹配"""
    id_set = set(ids)
    result = [s for s in sessions if s.get("id") in id_set]
    not_found = id_set - {s.get("id") for s in result}
    if not_found:
        print(f"警告: 以下 ID 未匹配到会话: {', '.join(sorted(not_found))}")
    return result


def match_by_keyword(sessions, keyword):
    """按标题关键词筛选（不区分大小写）"""
    kw = keyword.lower()
    result = [s for s in sessions if kw in (s.get("title") or "").lower()]
    print(f"关键词 \"{keyword}\" 匹配到 {len(result)} 个会话")
    return result


def interactive_select(sessions):
    """交互模式：列出会话，用户输入编号选择"""
    print_session_list(sessions)
    print()
    print("请输入要拉取的会话编号，多个编号用逗号或空格分隔")
    print("示例: 1,3,5  或  1 3 5  或  all（全部拉取）")
    print("直接回车 = 取消\n")

    while True:
        try:
            raw = input("请输入编号: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已取消")
            return []

        if not raw:
            return []

        if raw.lower() == "all":
            return list(sessions)

        parts = raw.replace(",", " ").split()
        indices = []
        valid = True
        for p in parts:
            try:
                n = int(p)
                if 1 <= n <= len(sessions):
                    indices.append(n - 1)
                else:
                    print(f"  编号 {n} 超出范围 (1~{len(sessions)})，请重新输入")
                    valid = False
                    break
            except ValueError:
                print(f"  \"{p}\" 不是有效数字，请重新输入")
                valid = False
                break

        if valid and indices:
            return [sessions[i] for i in indices]


# ============================================================
# API 请求函数
# ============================================================

def fetch_all_sessions(page):
    """获取所有聊天会话列表（支持分页）"""
    all_sessions = []
    has_more = True
    params = None

    while has_more:
        js_code = """
            const params = arguments[0];
            let url = '/api/v0/chat_session/fetch_page';
            if (params) {
                url += '?' + new URLSearchParams(params).toString();
            }
            return fetch(url, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    Authorization: 'Bearer ' + JSON.parse(localStorage.getItem('userToken')).value,
                    accept: '*/*',
                    'accept-language': 'zh-CN,zh;q=0.9',
                    referer: 'https://chat.deepseek.com/',
                    'x-app-version': '20241129.1',
                    'x-client-locale': 'zh_CN',
                    'x-client-platform': 'web',
                    'x-client-version': '1.2.0-sse-hint'
                }
            })
            .then(res => res.json())
            .catch(err => ({ error: err.message }));
        """
        response = page.evaluate(js_code, params)

        if "error" in response:
            raise Exception(f"API 错误: {response['error']}")

        biz_data = response.get("data", {}).get("biz_data", {})
        sessions = biz_data.get("chat_sessions", [])
        has_more = biz_data.get("has_more", False)

        all_sessions.extend(sessions)

        if has_more and sessions:
            last_seq = sessions[-1].get("seq_id")
            params = {"before_seq_id": last_seq}
        else:
            params = None

    return all_sessions


def fetch_session_messages(page, session_id):
    """获取指定会话的所有消息"""
    js_code = """
        const sessionId = arguments[0];
        return fetch('/api/v0/chat/history_messages?chat_session_id=' + sessionId, {
            method: 'GET',
            credentials: 'include',
            headers: {
                Authorization: 'Bearer ' + JSON.parse(localStorage.getItem('userToken')).value,
                accept: '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
                referer: 'https://chat.deepseek.com/',
                'x-app-version': '20241129.1',
                'x-client-locale': 'zh_CN',
                'x-client-platform': 'web',
                'x-client-version': '1.2.0-sse-hint'
            }
        })
        .then(res => res.json())
        .catch(err => ({ error: err.message }));
    """
    response = page.evaluate(js_code, session_id)

    if "error" in response:
        print(f"  获取会话 {session_id} 消息失败: {response['error']}")
        return None

    return response.get("data", {}).get("biz_data", {})


# ============================================================
# 工具函数
# ============================================================

def format_timestamp(ts):
    """将时间戳（秒）转为可读格式"""
    if not ts:
        return "未知"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError):
        if ts > 1e12:
            return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M")
        return str(ts)


if __name__ == "__main__":
    main()