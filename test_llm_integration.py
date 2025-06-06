#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LLM 集成功能
验证星火API的书籍推荐理由生成是否正常工作
"""

import requests
import json
import time

# 测试配置
API_BASE_URL = "http://localhost:5001"
API_ENDPOINT = "/api/books_with_reasons"

def test_direct_spark_function():
    """直接测试 spark.py 中的新函数"""
    print("🔬 直接测试星火API函数...")
    
    try:
        from spark import get_spark_books_with_reasons
        
        test_queries = ["机器学习", "数据结构", "Python编程"]
        
        for query in test_queries:
            print(f"\n📚 测试查询: '{query}'")
            result = get_spark_books_with_reasons(query)
            
            if result.get("status") == "success":
                print("✅ 星火API调用成功")
                print(f"   推荐书籍数量: {len(result.get('books', []))}")
                
                for i, book in enumerate(result.get('books', [])[:1]):  # 只显示第一本书的详细信息
                    print(f"   书籍{i+1}: {book.get('title', 'Unknown')}")
                    print(f"     作者: {book.get('author', 'Unknown')}")
                    
                    logical = book.get('logical_reason', {})
                    print(f"     逻辑分析: {logical.get('ai_understanding', 'N/A')[:50]}...")
                    
                    social = book.get('social_reason', {})
                    dept_count = len(social.get('departments', []))
                    print(f"     社交证据: 包含{dept_count}个院系数据")
                    
            else:
                print(f"❌ 星火API调用失败: {result.get('error', 'Unknown error')}")
            
            time.sleep(2)  # 避免请求过于频繁
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def test_full_api_integration():
    """测试完整的API集成"""
    print("\n🌐 测试完整API集成...")
    
    test_queries = ["深度学习", "算法设计"]
    
    for query in test_queries:
        print(f"\n📡 API测试查询: '{query}'")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}{API_ENDPOINT}",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30  # 增加超时时间，因为LLM调用可能较慢
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if validate_api_response(data, query):
                    print("✅ API集成测试通过")
                    print_api_response_summary(data)
                else:
                    print("❌ API响应数据格式不正确")
                    
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏱️ 请求超时（这是正常的，LLM调用需要时间）")
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
        
        time.sleep(3)  # LLM调用间隔

def validate_api_response(data, expected_query):
    """验证API响应数据"""
    try:
        # 检查基本结构
        if data.get("status") != "success":
            print(f"⚠️ 状态不是success: {data.get('status')}")
            return False
        
        if data.get("user_query") != expected_query:
            print(f"⚠️ 查询不匹配: 期望'{expected_query}', 实际'{data.get('user_query')}'")
            return False
        
        books = data.get("books", [])
        if not isinstance(books, list):
            print("⚠️ books字段不是数组")
            return False
        
        if len(books) == 0:
            print("⚠️ 没有返回书籍数据")
            return False
        
        # 检查每本书的结构
        for i, book in enumerate(books):
            if not validate_book_structure(book, i):
                return False
        
        return True
        
    except Exception as e:
        print(f"⚠️ 验证过程异常: {e}")
        return False

def validate_book_structure(book, index):
    """验证书籍数据结构"""
    required_fields = ["title", "author", "logical_reason", "social_reason"]
    
    for field in required_fields:
        if field not in book:
            print(f"⚠️ 书籍{index+1}缺少字段: {field}")
            return False
    
    # 检查逻辑分析
    logical = book["logical_reason"]
    logical_fields = ["user_query_recap", "ai_understanding", "keyword_match"]
    for field in logical_fields:
        if field not in logical:
            print(f"⚠️ 书籍{index+1}的逻辑分析缺少字段: {field}")
            return False
    
    # 检查社交证据
    social = book["social_reason"]
    if "departments" not in social or "trend" not in social:
        print(f"⚠️ 书籍{index+1}的社交证据结构不完整")
        return False
    
    departments = social["departments"]
    if not isinstance(departments, list) or len(departments) == 0:
        print(f"⚠️ 书籍{index+1}的院系数据无效")
        return False
    
    return True

def print_api_response_summary(data):
    """打印API响应摘要"""
    print(f"📊 响应摘要:")
    print(f"   查询: {data.get('user_query')}")
    print(f"   书籍数量: {len(data.get('books', []))}")
    
    for i, book in enumerate(data.get('books', [])[:2]):  # 显示前两本书
        print(f"   📖 书籍{i+1}: {book.get('title')}")
        print(f"      作者: {book.get('author')}")
        
        logical = book.get('logical_reason', {})
        ai_understanding = logical.get('ai_understanding', '')
        print(f"      AI理解: {ai_understanding[:60]}{'...' if len(ai_understanding) > 60 else ''}")
        
        social = book.get('social_reason', {})
        trend = social.get('trend', '')
        print(f"      借阅趋势: {trend[:60]}{'...' if len(trend) > 60 else ''}")

def check_server_availability():
    """检查服务器是否可用"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return True
    except:
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("🧪 LLM 集成测试工具")
    print("=" * 70)
    
    print(f"🎯 测试目标: 验证星火API的书籍推荐理由生成功能")
    print(f"📡 API地址: {API_BASE_URL}{API_ENDPOINT}")
    print()
    
    # 检查服务器
    if not check_server_availability():
        print("❌ 服务器未运行，请先启动 web_monitor.py")
        print("💡 提示: python web_monitor.py")
        return
    
    print("✅ 服务器连接正常")
    
    # 测试1: 直接测试星火函数
    test_direct_spark_function()
    
    # 测试2: 完整API集成测试
    test_full_api_integration()
    
    print("\n" + "=" * 70)
    print("🎉 测试完成!")
    print("💡 如果测试通过，说明LLM集成成功，可以开始前端开发")
    print("💡 如果有错误，请检查星火API配置和网络连接")
    print("=" * 70)

if __name__ == "__main__":
    main() 