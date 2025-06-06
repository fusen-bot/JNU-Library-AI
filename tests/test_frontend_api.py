#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端API接入测试工具
用于验证前端是否能正确接入新的 /api/books_with_reasons API
"""

import webbrowser
import os
import time
import subprocess
import threading
import requests
from pathlib import Path

def check_server_status():
    """检查后端服务器状态"""
    try:
        response = requests.get('http://localhost:5001/api/books_with_reasons', 
                              json={'query': 'test'}, timeout=3)
        return True
    except:
        return False

def start_server_if_needed():
    """如果服务器未启动，则启动它"""
    if not check_server_status():
        print("🚀 后端服务器未启动，正在启动...")
        # 在新的线程中启动服务器
        def run_server():
            subprocess.run(['python', 'web_monitor.py'], cwd=os.getcwd())
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        for i in range(30):  # 最多等待30秒
            time.sleep(1)
            if check_server_status():
                print("✅ 服务器启动成功！")
                return True
            print(f"   等待中... ({i+1}/30)")
        
        print("❌ 服务器启动失败，请手动启动 web_monitor.py")
        return False
    else:
        print("✅ 后端服务器已运行")
        return True

def main():
    print("=" * 60)
    print("🧪 前端API接入测试工具")
    print("=" * 60)
    
    # 检查测试文件是否存在
    test_file = Path('test_frontend_integration.html')
    if not test_file.exists():
        print("❌ 测试文件不存在：test_frontend_integration.html")
        return
    
    # 检查suggestion_display.js是否存在
    js_file = Path('suggestion_display.js')
    if not js_file.exists():
        print("❌ JavaScript文件不存在：suggestion_display.js")
        return
    
    print("📁 文件检查通过")
    
    # 检查并启动服务器
    if not start_server_if_needed():
        return
    
    # 获取绝对路径
    test_file_path = test_file.absolute()
    
    print(f"🌐 正在打开测试页面...")
    print(f"📄 文件路径: {test_file_path}")
    
    # 在浏览器中打开测试页面
    webbrowser.open(f'file://{test_file_path}')
    
    print("\n" + "=" * 60)
    print("📋 测试指南")
    print("=" * 60)
    print("1. 🌐 浏览器已打开测试页面")
    print("2. 🔧 请按F12打开开发者控制台")
    print("3. 📝 在输入框中输入查询词（如：python编程）")
    print("4. 👀 观察控制台中的API数据日志")
    print("5. ✅ 验证数据是否符合契约格式")
    print("\n🔍 期望看到的日志格式：")
    print("   🔍 新API返回的完整数据: {status: 'success', books: [...]}")
    print("   📋 数据契约验证: status, user_query, books数量")
    print("   📚 书籍详情: 标题、作者、逻辑分析、社交证据")
    print("\n⚠️  注意：API调用可能需要15-30秒，请耐心等待")
    print("=" * 60)
    
    # 测试一些示例查询
    print("\n🧪 建议测试的查询词：")
    test_queries = [
        "python编程",
        "深度学习", 
        "操作系统",
        "数据结构",
        "web开发"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"   {i}. {query}")
    
    print(f"\n💡 提示：如需手动测试API，可以运行：")
    print(f"   curl -X POST http://localhost:5001/api/books_with_reasons \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d '{{\"query\": \"python编程\"}}'")

if __name__ == "__main__":
    main() 