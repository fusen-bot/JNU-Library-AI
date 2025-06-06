#!/usr/bin/env python3
"""
测试异步书籍推荐API的脚本
测试新的 /api/books_with_reasons 端点的快速响应和异步理由生成功能
"""

import requests
import json
import time

def test_async_api():
    """
    测试异步API的完整流程
    """
    base_url = "http://localhost:5001"
    
    print("🧪 开始测试异步书籍推荐API")
    print("=" * 50)
    
    # 1. 测试基本信息快速返回
    print("📤 发送书籍推荐请求...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/books_with_reasons",
            json={"query": "python编程"},
            headers={"Content-Type": "application/json"}
        )
        
        first_response_time = time.time() - start_time
        print(f"⚡ 首次响应时间: {first_response_time:.2f}秒")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 首次响应成功")
            print(f"📋 响应数据:")
            print(f"   - 状态: {data.get('status')}")
            print(f"   - 用户查询: {data.get('user_query')}")
            print(f"   - 书籍数量: {len(data.get('books', []))}")
            print(f"   - 任务ID: {data.get('task_id')}")
            print(f"   - 理由加载中: {data.get('reasons_loading')}")
            print(f"   - 消息: {data.get('message')}")
            
            # 显示书籍基本信息
            for i, book in enumerate(data.get('books', [])):
                print(f"   📚 书籍{i+1}: {book.get('title')} - {book.get('author')}")
            
            task_id = data.get('task_id')
            
            if task_id and data.get('reasons_loading'):
                print("\n🔄 开始轮询任务状态...")
                test_task_polling(base_url, task_id)
            
        else:
            print(f"❌ 首次响应失败: {response.status_code}")
            print(f"   错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

def test_task_polling(base_url, task_id):
    """
    测试任务状态轮询
    """
    max_attempts = 20  # 最多轮询20次
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"🔍 轮询尝试 {attempt}/{max_attempts}...")
        
        try:
            response = requests.get(f"{base_url}/api/task_status/{task_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                progress = data.get('progress')
                
                print(f"   状态: {status} - {progress}")
                
                if status == 'completed':
                    print("🎉 任务完成！")
                    print("📚 完整推荐理由:")
                    
                    for i, book in enumerate(data.get('books', [])):
                        print(f"\n   书籍{i+1}: {book.get('title')}")
                        print(f"   作者: {book.get('author')}")
                        
                        logical_reason = book.get('logical_reason', {})
                        social_reason = book.get('social_reason', {})
                        
                        if logical_reason:
                            print("   🧠 逻辑分析:")
                            print(f"      - 查询意图: {logical_reason.get('user_query_intent', 'N/A')}")
                            print(f"      - 核心概念: {logical_reason.get('book_core_concepts', 'N/A')}")
                            print(f"      - 应用领域: {logical_reason.get('application_fields_match', 'N/A')}")
                        
                        if social_reason:
                            print("   👥 社交证据:")
                            departments = social_reason.get('departments', [])
                            for dept in departments:
                                print(f"      - {dept.get('name')}: {dept.get('rate', 0)*100:.0f}%")
                    
                    break
                    
                elif status == 'error':
                    print(f"❌ 任务失败: {data.get('error', '未知错误')}")
                    break
                    
                elif status in ['pending', 'processing']:
                    print("   ⏳ 等待5秒后继续轮询...")
                    time.sleep(5)
                    
            else:
                print(f"❌ 轮询失败: {response.status_code}")
                print(f"   错误: {response.text}")
                break
                
        except Exception as e:
            print(f"❌ 轮询请求失败: {str(e)}")
            break
    
    if attempt >= max_attempts:
        print("⏰ 轮询超时，任务可能仍在处理中")

def test_edge_cases():
    """
    测试边缘情况
    """
    print("\n🧪 测试边缘情况")
    print("=" * 30)
    
    base_url = "http://localhost:5001"
    
    # 测试空查询
    print("📤 测试空查询...")
    try:
        response = requests.post(
            f"{base_url}/api/books_with_reasons",
            json={"query": ""},
            headers={"Content-Type": "application/json"}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code != 200:
            data = response.json()
            print(f"   预期错误: {data.get('error')}")
    except Exception as e:
        print(f"   异常: {str(e)}")
    
    # 测试不存在的任务ID
    print("📤 测试不存在的任务ID...")
    try:
        response = requests.get(f"{base_url}/api/task_status/nonexistent-task-id")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            print(f"   预期错误: {data.get('error')}")
    except Exception as e:
        print(f"   异常: {str(e)}")

if __name__ == "__main__":
    print("🚀 启动异步API测试")
    print("请确保 web_monitor.py 正在运行在 localhost:5001")
    print("")
    
    # 等待用户确认
    input("按 Enter 键开始测试...")
    
    test_async_api()
    test_edge_cases()
    
    print("\n✅ 测试完成") 