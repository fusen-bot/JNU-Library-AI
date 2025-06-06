#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI升级验证工具
验证新的推荐理由块UI组件是否正常工作
"""

import webbrowser
import time
import requests
import json

def test_api_data():
    """测试API返回的数据格式"""
    try:
        response = requests.post('http://localhost:5001/api/books_with_reasons', 
                               json={'query': '深度学习'}, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API测试成功")
            print(f"   状态: {data.get('status')}")
            print(f"   查询: {data.get('user_query')}")
            print(f"   书籍数量: {len(data.get('books', []))}")
            
            # 验证每本书的数据结构
            for i, book in enumerate(data.get('books', [])[:3], 1):
                print(f"\n📚 书籍{i}: {book.get('title')}")
                print(f"   作者: {book.get('author')}")
                
                # 验证逻辑分析
                logical = book.get('logical_reason', {})
                print(f"   🧠 逻辑分析完整性: {len(logical)} 字段")
                for key in ['user_query_recap', 'ai_understanding', 'keyword_match']:
                    if key in logical:
                        print(f"      ✅ {key}")
                    else:
                        print(f"      ❌ 缺少 {key}")
                
                # 验证社交证据
                social = book.get('social_reason', {})
                departments = social.get('departments', [])
                print(f"   👥 社交证据: {len(departments)} 个学院数据")
                if social.get('trend'):
                    print(f"      ✅ 趋势分析")
                else:
                    print(f"      ❌ 缺少趋势分析")
            
            return True
        else:
            print(f"❌ API测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API测试异常: {e}")
        return False

def main():
    print("=" * 60)
    print("🎨 UI升级验证工具")
    print("=" * 60)
    
    # 1. 测试API数据
    print("1️⃣ 测试API数据结构...")
    api_ok = test_api_data()
    
    if not api_ok:
        print("\n❌ API测试失败，请先确保后端服务器正常运行")
        return
    
    # 2. 打开测试页面
    print("\n2️⃣ 打开UI测试页面...")
    test_url = "http://localhost:8000/test_frontend_integration.html"
    webbrowser.open(test_url)
    
    print(f"🌐 已打开: {test_url}")
    
    # 3. 测试指导
    print("\n" + "=" * 60)
    print("🧪 UI升级验证清单")
    print("=" * 60)
    
    checklist = [
        "按F12打开开发者控制台",
        "在输入框中输入'深度学习'",
        "等待15-30秒API调用完成",
        "观察是否出现新的卡片式UI界面",
        "验证是否显示'🤖 AI智能推荐理由'标题",
        "检查每本书是否有绿色标题栏",
        "确认左右是否有蓝色'🧠 逻辑分析'和紫色'👥 社交证据'块",
        "测试鼠标悬停在理由块上是否有展开效果",
        "验证是否显示借阅率柱状图",
        "确认控制台是否显示'🎨 使用新版推荐理由UI组件'日志"
    ]
    
    for i, item in enumerate(checklist, 1):
        print(f"   {i:2d}. {item}")
    
    print("\n🔍 预期UI效果:")
    print("   📱 卡片式布局，替代原来的简单文本列表")
    print("   🎨 渐变绿色主题，符合江南大学色彩规范")
    print("   📊 动态借阅率图表，可视化社交证据")
    print("   🖱️ 流畅的悬停动画和内容展开效果")
    
    print("\n⚠️ 如果看到旧版UI，说明:")
    print("   1. show_books_with_reasons.js 文件未正确加载")
    print("   2. JavaScript函数未正确定义")
    print("   3. 备用机制启动，显示旧版格式")
    
    print(f"\n💡 问题排查:")
    print(f"   - 检查网络请求: {test_url}")
    print(f"   - 验证文件存在: show_books_with_reasons.js")
    print(f"   - 查看控制台错误信息")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 