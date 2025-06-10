#!/usr/bin/env python3
"""
测试用户交互行为日志采集API
用于验证后端接口是否正常工作
"""

import requests
import json
import time
import uuid

# 测试配置
API_BASE_URL = "http://localhost:5001"
TEST_SESSION_ID = str(uuid.uuid4())

def test_log_interaction_api():
    """测试交互日志API"""
    
    print("🧪 开始测试用户交互日志API...")
    
    # 测试数据集
    test_cases = [
        {
            "name": "点击逻辑理由",
            "data": {
                "session_id": TEST_SESSION_ID,
                "event_type": "click_reason",
                "book_id": "9787111321312",
                "book_title": "深入理解计算机系统",
                "reason_type": "logical",
                "user_query": "计算机原理"
            }
        },
        {
            "name": "点击社交理由",
            "data": {
                "session_id": TEST_SESSION_ID,
                "event_type": "click_reason",
                "book_id": "9787111187776",
                "book_title": "算法导论",
                "reason_type": "social",
                "user_query": "算法学习"
            }
        },
        {
            "name": "展开详细说明",
            "data": {
                "session_id": TEST_SESSION_ID,
                "event_type": "expand_details",
                "book_id": "9787111213826",
                "book_title": "Java核心技术",
                "user_query": "Java编程"
            }
        },
        {
            "name": "页面停留",
            "data": {
                "session_id": TEST_SESSION_ID,
                "event_type": "dwell_time",
                "book_id": "9787111321312",
                "book_title": "深入理解计算机系统",
                "dwell_time_ms": 5000,
                "user_query": "计算机原理"
            }
        },
        {
            "name": "滚动深度",
            "data": {
                "session_id": TEST_SESSION_ID,
                "event_type": "scroll_depth",
                "book_id": "9787111187776",
                "book_title": "算法导论",
                "scroll_depth": 0.85,
                "user_query": "算法学习"
            }
        }
    ]
    
    # 执行测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}/{len(test_cases)}: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/log_interaction",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 成功: {result.get('message', '无消息')}")
            else:
                print(f"   ❌ 失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接失败: 无法连接到服务器 {API_BASE_URL}")
            print("   请确保服务器正在运行 (python web_monitor.py)")
            break
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
        
        # 短暂延迟
        time.sleep(0.5)
    
    print(f"\n🏁 测试完成！日志文件: interaction_logs.csv")

def test_invalid_requests():
    """测试无效请求的处理"""
    
    print(f"\n🔍 测试无效请求处理...")
    
    invalid_cases = [
        {
            "name": "空请求体",
            "data": None
        },
        {
            "name": "缺少必需字段",
            "data": {"session_id": TEST_SESSION_ID}
        },
        {
            "name": "空event_type",
            "data": {"event_type": ""}
        }
    ]
    
    for i, test_case in enumerate(invalid_cases, 1):
        print(f"\n   测试 {i}: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/log_interaction",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 400:
                result = response.json()
                print(f"   ✅ 正确拒绝: {result.get('message', '无消息')}")
            else:
                print(f"   ⚠️  意外状态码: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接失败")
            break
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("📊 用户交互日志API测试工具")
    print("=" * 60)
    
    # 基本功能测试
    test_log_interaction_api()
    
    # 错误处理测试
    test_invalid_requests()
    
    print(f"\n" + "=" * 60)
    print("✨ 所有测试已完成")
    print("💡 提示: 检查生成的 interaction_logs.csv 文件查看日志记录")
    print("=" * 60)