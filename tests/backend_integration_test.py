#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端 API 联调测试工具
确保 API 能稳定返回符合数据契约的 JSON 数据
支持多种测试方式：Python requests + curl 命令示例
"""

import requests
import json
import time
import subprocess
import os
from datetime import datetime

# 测试配置
API_BASE_URL = "http://localhost:5001"
API_ENDPOINT = "/api/books_with_reasons"
FULL_URL = f"{API_BASE_URL}{API_ENDPOINT}"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
    
    def test_with_requests(self):
        """使用 Python requests 进行测试"""
        print("🐍 使用 Python requests 进行 API 测试...")
        
        test_cases = [
            {"query": "机器学习", "description": "基础AI领域查询"},
            {"query": "数据结构与算法", "description": "计算机基础课程"},
            {"query": "深度学习框架", "description": "具体技术查询"},
            {"query": "python web开发", "description": "实用技能查询"},
            {"query": "操作系统原理", "description": "系统层面查询"},
            {"query": "a", "description": "短查询测试"},
            {"query": "这是一个非常长的查询词用来测试系统对长输入的处理能力包含各种技术关键词", "description": "长查询测试"},
            {"query": "", "description": "空查询测试（应该失败）"}
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n📋 测试案例 {i}: {case['description']}")
            print(f"   查询词: '{case['query']}'")
            
            try:
                start_time = time.time()
                response = requests.post(
                    FULL_URL,
                    json={"query": case['query']},
                    headers={"Content-Type": "application/json"},
                    timeout=45  # 给LLM足够的响应时间
                )
                response_time = time.time() - start_time
                
                result = self._analyze_response(response, case['query'], response_time)
                self.test_results.append({
                    "case": case['description'],
                    "query": case['query'],
                    "result": result,
                    "response_time": response_time
                })
                
                print(f"   ⏱️ 响应时间: {response_time:.2f}秒")
                
                if result['success']:
                    print(f"   ✅ 测试通过: {result['message']}")
                else:
                    print(f"   ❌ 测试失败: {result['message']}")
                
                # 显示返回的书籍摘要
                if 'books_count' in result:
                    print(f"   📚 返回书籍数量: {result['books_count']}")
                    if 'first_book' in result:
                        print(f"   📖 首本书籍: {result['first_book']}")
                
            except requests.exceptions.Timeout:
                print(f"   ⏱️ 请求超时（45秒）")
                self.test_results.append({
                    "case": case['description'],
                    "query": case['query'],
                    "result": {"success": False, "message": "请求超时"},
                    "response_time": 45.0
                })
            except Exception as e:
                print(f"   ❌ 请求异常: {e}")
                self.test_results.append({
                    "case": case['description'],
                    "query": case['query'],
                    "result": {"success": False, "message": f"请求异常: {e}"},
                    "response_time": 0.0
                })
            
            time.sleep(1)  # 避免请求过于密集
    
    def _analyze_response(self, response, query, response_time):
        """分析响应结果"""
        try:
            # 检查HTTP状态码
            if response.status_code != 200:
                if response.status_code == 400 and query == "":
                    return {"success": True, "message": "空查询正确返回400错误"}
                return {"success": False, "message": f"HTTP错误: {response.status_code}"}
            
            # 解析JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                return {"success": False, "message": "响应不是有效的JSON"}
            
            # 验证数据契约
            validation_result = self._validate_contract(data, query)
            if not validation_result['valid']:
                return {"success": False, "message": f"数据契约验证失败: {validation_result['error']}"}
            
            # 提取关键信息
            books = data.get('books', [])
            result = {
                "success": True,
                "message": "数据契约验证通过",
                "books_count": len(books),
                "status": data.get('status'),
                "response_time_category": self._categorize_response_time(response_time)
            }
            
            # 获取第一本书的信息
            if books:
                first_book = books[0]
                result['first_book'] = f"{first_book.get('title', 'Unknown')} - {first_book.get('author', 'Unknown')}"
                
                # 检查推荐理由质量
                logical = first_book.get('logical_reason', {})
                if logical.get('ai_understanding'):
                    result['has_quality_reasoning'] = True
            
            return result
            
        except Exception as e:
            return {"success": False, "message": f"响应分析异常: {e}"}
    
    def _validate_contract(self, data, query):
        """验证数据契约"""
        try:
            # 检查顶级字段
            required_top_fields = ["status", "user_query", "books"]
            for field in required_top_fields:
                if field not in data:
                    return {"valid": False, "error": f"缺少顶级字段: {field}"}
            
            # 检查状态
            if data["status"] not in ["success", "error"]:
                return {"valid": False, "error": f"状态值无效: {data['status']}"}
            
            if data["status"] == "error":
                if "error" in data:
                    return {"valid": True}  # 错误响应也是合法的
                else:
                    return {"valid": False, "error": "错误响应缺少error字段"}
            
            # 检查成功响应
            if data["user_query"] != query:
                return {"valid": False, "error": f"查询不匹配: 期望'{query}', 实际'{data['user_query']}'"}
            
            books = data["books"]
            if not isinstance(books, list):
                return {"valid": False, "error": "books字段不是数组"}
            
            if len(books) == 0:
                return {"valid": False, "error": "书籍数组为空"}
            
            # 验证每本书的结构
            for i, book in enumerate(books):
                book_validation = self._validate_book(book, i)
                if not book_validation['valid']:
                    return {"valid": False, "error": f"书籍{i+1}: {book_validation['error']}"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"验证异常: {e}"}
    
    def _validate_book(self, book, index):
        """验证单本书的数据结构"""
        try:
            # 基本字段
            basic_fields = ["title", "author", "isbn", "cover_url"]
            for field in basic_fields:
                if field not in book:
                    return {"valid": False, "error": f"缺少基本字段: {field}"}
            
            # 逻辑分析字段
            if "logical_reason" not in book:
                return {"valid": False, "error": "缺少logical_reason字段"}
            
            logical = book["logical_reason"]
            logical_fields = ["user_query_recap", "ai_understanding", "keyword_match"]
            for field in logical_fields:
                if field not in logical:
                    return {"valid": False, "error": f"logical_reason缺少字段: {field}"}
                if not isinstance(logical[field], str) or not logical[field].strip():
                    return {"valid": False, "error": f"logical_reason.{field}无效"}
            
            # 社交证据字段
            if "social_reason" not in book:
                return {"valid": False, "error": "缺少social_reason字段"}
            
            social = book["social_reason"]
            if "departments" not in social or "trend" not in social:
                return {"valid": False, "error": "social_reason缺少必需字段"}
            
            departments = social["departments"]
            if not isinstance(departments, list) or len(departments) == 0:
                return {"valid": False, "error": "departments数据无效"}
            
            for dept in departments:
                if not isinstance(dept, dict) or "name" not in dept or "rate" not in dept:
                    return {"valid": False, "error": "department项格式错误"}
                if not isinstance(dept["rate"], (int, float)) or not (0 <= dept["rate"] <= 1):
                    return {"valid": False, "error": f"借阅率无效: {dept['rate']}"}
            
            if not isinstance(social["trend"], str) or not social["trend"].strip():
                return {"valid": False, "error": "trend字段无效"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"书籍验证异常: {e}"}
    
    def _categorize_response_time(self, response_time):
        """响应时间分类"""
        if response_time < 5:
            return "极快"
        elif response_time < 15:
            return "快速"
        elif response_time < 30:
            return "正常"
        else:
            return "较慢"
    
    def generate_curl_commands(self):
        """生成 curl 测试命令示例"""
        print("\n🌐 生成 curl 测试命令...")
        
        test_queries = [
            "机器学习",
            "数据结构",
            "Python编程"
        ]
        
        print("以下是可以直接在终端运行的 curl 命令:")
        print("=" * 60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n# 测试{i}: {query}")
            curl_cmd = f"""curl -X POST "{FULL_URL}" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "{query}"}}' \\
  --max-time 45 \\
  | python -m json.tool"""
            
            print(curl_cmd)
        
        # 错误测试
        print(f"\n# 错误测试: 空查询")
        error_curl = f"""curl -X POST "{FULL_URL}" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": ""}}' \\
  --max-time 45 \\
  | python -m json.tool"""
        print(error_curl)
        
        print("\n" + "=" * 60)
        print("💡 提示: 在另一个终端窗口运行上述命令来独立测试API")
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 70)
        print("📊 后端联调测试总结")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['result']['success'])
        
        print(f"🎯 测试总数: {total_tests}")
        print(f"✅ 成功测试: {successful_tests}")
        print(f"❌ 失败测试: {total_tests - successful_tests}")
        print(f"📈 成功率: {(successful_tests/total_tests)*100:.1f}%")
        
        # 响应时间统计
        response_times = [r['response_time'] for r in self.test_results if r['result']['success']]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\n⏱️ 响应时间统计:")
            print(f"   平均: {avg_time:.2f}秒")
            print(f"   最快: {min_time:.2f}秒")
            print(f"   最慢: {max_time:.2f}秒")
        
        # 详细结果
        print(f"\n📋 详细测试结果:")
        for r in self.test_results:
            status = "✅" if r['result']['success'] else "❌"
            print(f"   {status} {r['case']}: {r['result']['message']}")
        
        # 数据质量检查
        quality_count = sum(1 for r in self.test_results 
                          if r['result'].get('has_quality_reasoning', False))
        
        if quality_count > 0:
            print(f"\n🎨 推荐理由质量: {quality_count}/{successful_tests} 包含高质量推荐理由")
        
        print(f"\n⏰ 总测试时间: {(datetime.now() - self.start_time).total_seconds():.1f}秒")

def check_server_status():
    """检查服务器状态"""
    try:
        response = requests.get(API_BASE_URL, timeout=5)
        return True
    except:
        return False

def main():
    """主函数"""
    print("🔧 后端 API 联调测试工具")
    print("=" * 70)
    print(f"🎯 测试目标: 验证 API 稳定性和数据契约符合性")
    print(f"📡 API地址: {FULL_URL}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查服务器状态
    if not check_server_status():
        print("❌ 服务器未运行!")
        print("💡 请先启动服务器: python web_monitor.py")
        return
    
    print("✅ 服务器连接正常")
    
    # 创建测试器
    tester = BackendTester()
    
    # 执行Python requests测试
    tester.test_with_requests()
    
    # 生成curl命令
    tester.generate_curl_commands()
    
    # 打印总结
    tester.print_summary()
    
    print("\n🎉 联调测试完成!")
    print("💡 如果成功率达到90%以上，说明后端API已经稳定可靠")
    print("🚀 现在可以开始前端UI适配工作了")

if __name__ == "__main__":
    main() 