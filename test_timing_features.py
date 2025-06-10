#!/usr/bin/env python3
"""
测试交互日志记录的计时功能
专门验证搜索耗时、停留时长等功能
"""

import requests
import json
import time
import uuid

API_BASE_URL = "http://localhost:5001"
TEST_SESSION_ID = f"timing_test_{int(time.time())}"

def test_search_timing():
    """测试搜索计时功能"""
    print("🔍 测试搜索计时功能...")
    
    # 1. 开始搜索
    search_start_data = {
        "session_id": TEST_SESSION_ID,
        "event_type": "search_start",
        "user_query": "人工智能算法",
        "start_time": "2025-06-10T10:00:00.000Z",
        "search_count": 1
    }
    
    response = requests.post(f"{API_BASE_URL}/api/log_interaction", json=search_start_data)
    print(f"   搜索开始记录: {'✅ 成功' if response.status_code == 200 else '❌ 失败'}")
    
    # 模拟搜索耗时
    time.sleep(1.5)
    
    # 2. 结束搜索
    search_end_data = {
        "session_id": TEST_SESSION_ID,
        "event_type": "search_end",
        "user_query": "人工智能算法",
        "start_time": "2025-06-10T10:00:00.000Z",
        "end_time": "2025-06-10T10:00:01.500Z",
        "duration_ms": 1500,
        "total_duration_ms": 1500,
        "total_search_count": 1,
        "average_duration_ms": 1500
    }
    
    response = requests.post(f"{API_BASE_URL}/api/log_interaction", json=search_end_data)
    print(f"   搜索结束记录: {'✅ 成功' if response.status_code == 200 else '❌ 失败'}")
    
    return True

def test_results_display_timing():
    """测试结果页面停留时长功能"""
    print("📄 测试结果页面停留时长功能...")
    
    # 1. 结果页面显示
    display_data = {
        "session_id": TEST_SESSION_ID,
        "event_type": "results_displayed",
        "user_query": "人工智能算法",
        "display_time": "2025-06-10T10:00:02.000Z"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/log_interaction", json=display_data)
    print(f"   结果显示记录: {'✅ 成功' if response.status_code == 200 else '❌ 失败'}")
    
    # 模拟停留时长
    time.sleep(2)
    
    # 2. 结果页面隐藏
    hide_data = {
        "session_id": TEST_SESSION_ID,
        "event_type": "results_hidden",
        "user_query": "人工智能算法",
        "display_time": "2025-06-10T10:00:02.000Z",
        "hide_time": "2025-06-10T10:00:04.000Z",
        "duration_ms": 2000,
        "total_display_duration_ms": 2000
    }
    
    response = requests.post(f"{API_BASE_URL}/api/log_interaction", json=hide_data)
    print(f"   结果隐藏记录: {'✅ 成功' if response.status_code == 200 else '❌ 失败'}")
    
    return True

def test_panel_timing():
    """测试悬浮面板停留时长功能"""
    print("📖 测试悬浮面板停留时长功能...")
    
    books = [
        {"id": "book_ai_1", "title": "人工智能导论"},
        {"id": "book_ai_2", "title": "机器学习实战"},
        {"id": "book_ai_3", "title": "深度学习基础"}
    ]
    
    total_panel_duration = 0
    book_durations = {}
    
    for i, book in enumerate(books):
        print(f"   测试书籍 {i+1}: {book['title']}")
        
        # 1. 面板打开
        open_data = {
            "session_id": TEST_SESSION_ID,
            "event_type": "panel_opened",
            "book_id": book["id"],
            "book_title": book["title"],
            "user_query": "人工智能算法",
            "open_time": f"2025-06-10T10:01:0{i}.000Z"
        }
        
        response = requests.post(f"{API_BASE_URL}/api/log_interaction", json=open_data)
        print(f"     面板打开记录: {'✅ 成功' if response.status_code == 200 else '❌ 失败'}")
        
        # 模拟停留时长（每本书不同的停留时间）
        stay_duration = 1 + i * 0.5  # 1s, 1.5s, 2s
        time.sleep(stay_duration)
        
        duration_ms = int(stay_duration * 1000)
        total_panel_duration += duration_ms
        book_durations[book["id"]] = duration_ms
        
        # 2. 面板关闭
        close_data = {
            "session_id": TEST_SESSION_ID,
            "event_type": "panel_closed",
            "book_id": book["id"],
            "book_title": book["title"],
            "user_query": "人工智能算法",
            "open_time": f"2025-06-10T10:01:0{i}.000Z",
            "close_time": f"2025-06-10T10:01:0{i+1}.000Z",
            "duration_ms": duration_ms,
            "book_total_duration_ms": duration_ms,  # 第一次访问这本书
            "panel_total_duration_ms": total_panel_duration,
            "unique_books_viewed": i + 1
        }
        
        response = requests.post(f"{API_BASE_URL}/api/log_interaction", json=close_data)
        print(f"     面板关闭记录: {'✅ 成功' if response.status_code == 200 else '❌ 失败'}")
    
    print(f"   📊 总面板停留时长: {total_panel_duration}ms")
    print(f"   📚 各书籍停留时长: {book_durations}")
    
    return True

def test_session_summary():
    """测试会话总结功能"""
    print("📊 测试会话总结功能...")
    
    session_stats = {
        "sessionId": TEST_SESSION_ID,
        "searchStats": {
            "totalCount": 1,
            "totalDuration": 1500,
            "averageDuration": 1500
        },
        "resultsStats": {
            "totalDisplayDuration": 2000,
            "currentlyDisplayed": False
        },
        "panelStats": {
            "totalDuration": 4500,  # 1000 + 1500 + 2000
            "uniqueBooksViewed": 3,
            "currentlyOpen": False,
            "bookDurations": {
                "book_ai_1": 1000,
                "book_ai_2": 1500,
                "book_ai_3": 2000
            }
        }
    }
    
    summary_data = {
        "session_id": TEST_SESSION_ID,
        "event_type": "session_summary",
        "user_query": "人工智能算法",
        "session_stats": json.dumps(session_stats)
    }
    
    response = requests.post(f"{API_BASE_URL}/api/log_interaction", json=summary_data)
    print(f"   会话总结记录: {'✅ 成功' if response.status_code == 200 else '❌ 失败'}")
    
    return True

def main():
    print("=" * 70)
    print("⏱️  交互日志计时功能测试")
    print("=" * 70)
    
    try:
        # 测试各项功能
        print(f"\n🎯 会话ID: {TEST_SESSION_ID}")
        print(f"🌐 API地址: {API_BASE_URL}")
        
        test_search_timing()
        print()
        
        test_results_display_timing()
        print()
        
        test_panel_timing()
        print()
        
        test_session_summary()
        print()
        
        print("=" * 70)
        print("✨ 所有计时功能测试完成！")
        print("💾 请查看 interaction_logs.csv 文件以验证数据记录")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到服务器")
        print("请确保服务器正在运行: python web_monitor.py")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()
