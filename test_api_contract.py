#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的书籍推荐 API 数据契约
验证 /api/books_with_reasons 端点是否返回正确的数据结构
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5001"
API_ENDPOINT = "/api/books_with_reasons"

def test_api_contract():
    """测试 API 数据契约"""
    print("🔍 开始测试书籍推荐 API 数据契约...")
    
    # 测试用例
    test_queries = [
        "计算机",
        "算法",
        "编程语言",
        "数据结构"
    ]
    
    for query in test_queries:
        print(f"\n📚 测试查询: '{query}'")
        
        try:
            # 发送请求
            response = requests.post(
                f"{API_BASE_URL}{API_ENDPOINT}",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 验证数据结构
                if validate_response_structure(data, query):
                    print("✅ 数据契约验证通过")
                    print_response_summary(data)
                else:
                    print("❌ 数据契约验证失败")
                    
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
        
        time.sleep(1)  # 避免请求过于频繁

def validate_response_structure(data, expected_query):
    """验证响应数据结构是否符合契约"""
    try:
        # 检查顶级字段
        required_fields = ["status", "user_query", "books"]
        for field in required_fields:
            if field not in data:
                print(f"❌ 缺少必需字段: {field}")
                return False
        
        # 检查状态
        if data["status"] != "success":
            print(f"❌ 状态不正确: {data['status']}")
            return False
        
        # 检查用户查询
        if data["user_query"] != expected_query:
            print(f"❌ 用户查询不匹配: 期望 '{expected_query}', 实际 '{data['user_query']}'")
            return False
        
        # 检查书籍数组
        books = data["books"]
        if not isinstance(books, list) or len(books) != 3:
            print(f"❌ 书籍数组格式错误或数量不正确: 期望3本书，实际{len(books)}本")
            return False
        
        # 检查每本书的结构
        for i, book in enumerate(books):
            if not validate_book_structure(book, i):
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 验证过程中发生异常: {e}")
        return False

def validate_book_structure(book, index):
    """验证单本书的数据结构"""
    try:
        # 检查基本信息字段
        basic_fields = ["title", "author", "isbn", "cover_url"]
        for field in basic_fields:
            if field not in book:
                print(f"❌ 书籍{index+1}缺少基本字段: {field}")
                return False
        
        # 检查逻辑分析部分
        if "logical_reason" not in book:
            print(f"❌ 书籍{index+1}缺少 logical_reason 字段")
            return False
        
        logical_fields = ["user_query_recap", "ai_understanding", "keyword_match"]
        for field in logical_fields:
            if field not in book["logical_reason"]:
                print(f"❌ 书籍{index+1}的 logical_reason 缺少字段: {field}")
                return False
        
        # 检查社交证据部分
        if "social_reason" not in book:
            print(f"❌ 书籍{index+1}缺少 social_reason 字段")
            return False
        
        social_reason = book["social_reason"]
        if "departments" not in social_reason or "trend" not in social_reason:
            print(f"❌ 书籍{index+1}的 social_reason 缺少必需字段")
            return False
        
        # 检查院系数据格式
        departments = social_reason["departments"]
        if not isinstance(departments, list) or len(departments) == 0:
            print(f"❌ 书籍{index+1}的院系数据格式错误")
            return False
        
        for dept in departments:
            if not isinstance(dept, dict) or "name" not in dept or "rate" not in dept:
                print(f"❌ 书籍{index+1}的院系数据项格式错误")
                return False
            
            if not isinstance(dept["rate"], (int, float)) or not (0 <= dept["rate"] <= 1):
                print(f"❌ 书籍{index+1}的借阅率数据无效: {dept['rate']}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 验证书籍{index+1}时发生异常: {e}")
        return False

def print_response_summary(data):
    """打印响应数据摘要"""
    print(f"📊 数据摘要:")
    print(f"   用户查询: {data['user_query']}")
    print(f"   推荐书籍数量: {len(data['books'])}")
    
    for i, book in enumerate(data['books']):
        print(f"   书籍{i+1}: {book['title']}")
        print(f"     作者: {book['author']}")
        print(f"     推荐理由包含: 逻辑分析 ✓, 社交证据 ✓")
        print(f"     涉及院系数量: {len(book['social_reason']['departments'])}")

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 书籍推荐 API 数据契约测试工具")
    print("=" * 60)
    
    print(f"📡 API 地址: {API_BASE_URL}{API_ENDPOINT}")
    print(f"🎯 测试目标: 验证新的数据契约是否正确实现")
    print()
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        print("✅ 服务器连接正常")
    except:
        print("❌ 无法连接到服务器，请确保 web_monitor.py 正在运行")
        print("💡 提示: 运行 python web_monitor.py 启动服务器")
        return
    
    # 执行测试
    test_api_contract()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("💡 如果所有测试通过，说明数据契约定义正确，可以开始前端开发")
    print("=" * 60)

if __name__ == "__main__":
    main() 