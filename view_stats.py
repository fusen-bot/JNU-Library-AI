#!/usr/bin/env python3
"""
交互统计文件查看工具
用于快速查看和分析交互统计文件夹中的数据
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, date
from interaction_stats_manager import stats_manager

def view_latest_files(file_type=None, count=5):
    """查看最新的统计文件"""
    print(f"📊 最新的{count}个{file_type or '所有类型'}统计文件:")
    print("-" * 60)
    
    files = stats_manager.list_files_by_type(file_type)
    # 按修改时间排序，最新的在前
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    for i, file_path in enumerate(files[:count], 1):
        try:
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            file_size = file_path.stat().st_size
            
            print(f"{i}. {file_path.name}")
            print(f"   📅 修改时间: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   📦 文件大小: {file_size} bytes")
            
            # 尝试读取并显示简要内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'user_query' in data:
                    print(f"   🔍 查询: {data['user_query']}")
                if 'search_stats' in data and 'duration_ms' in data['search_stats']:
                    print(f"   ⏱️  耗时: {data['search_stats']['duration_ms']}ms")
                if 'panel_stats' in data and 'book_title' in data['panel_stats']:
                    print(f"   📖 书籍: {data['panel_stats']['book_title']}")
                    
            except Exception as e:
                print(f"   ⚠️ 读取内容失败: {e}")
                
            print()
            
        except Exception as e:
            print(f"   ❌ 处理文件失败: {e}")

def view_file_content(file_path):
    """查看指定文件的详细内容"""
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"📄 文件内容: {path.name}")
        print("=" * 60)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

def view_daily_summary(target_date=None):
    """查看指定日期的统计总结"""
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    print(f"📅 {target_date.strftime('%Y-%m-%d')} 的统计总结:")
    print("-" * 60)
    
    # 生成或读取日统计
    daily_file = stats_manager.save_daily_summary(target_date)
    
    try:
        with open(daily_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        daily_stats = data.get('daily_statistics', {})
        summary = daily_stats.get('summary', {})
        
        print(f"🔍 搜索统计:")
        print(f"   总搜索次数: {daily_stats.get('total_searches', 0)}")
        print(f"   总搜索耗时: {summary.get('total_search_duration_ms', 0)}ms")
        print(f"   平均搜索耗时: {summary.get('average_search_duration_ms', 0):.1f}ms")
        print(f"   唯一查询数: {summary.get('unique_queries', 0)}")
        
        print(f"\n📖 面板统计:")
        print(f"   面板交互次数: {daily_stats.get('total_panel_interactions', 0)}")
        print(f"   总面板停留时长: {summary.get('total_panel_duration_ms', 0)}ms")
        print(f"   查看的书籍数: {summary.get('unique_books_viewed', 0)}")
        
        print(f"\n📋 会话统计:")
        print(f"   总会话数: {daily_stats.get('total_sessions', 0)}")
        
        # 显示搜索详情
        if daily_stats.get('search_details'):
            print(f"\n🔍 搜索详情:")
            for i, search in enumerate(daily_stats['search_details'][:5], 1):
                print(f"   {i}. '{search['query']}' - {search['duration_ms']}ms")
        
        # 显示面板交互详情
        if daily_stats.get('panel_details'):
            print(f"\n📖 面板交互详情:")
            for i, panel in enumerate(daily_stats['panel_details'][:5], 1):
                print(f"   {i}. '{panel['book_title']}' - {panel['duration_ms']}ms")
        
    except Exception as e:
        print(f"❌ 读取日统计失败: {e}")

def view_comprehensive_report(days=7):
    """查看综合报告"""
    print(f"📈 最近{days}天的综合报告:")
    print("-" * 60)
    
    report_file = stats_manager.generate_comprehensive_report(days)
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        overall_stats = data.get('overall_statistics', {})
        
        print(f"📊 总体统计 (最近{days}天):")
        print(f"   总搜索次数: {overall_stats.get('total_searches', 0)}")
        print(f"   总会话数: {overall_stats.get('total_sessions', 0)}")
        print(f"   总面板交互: {overall_stats.get('total_panel_interactions', 0)}")
        print(f"   日均搜索: {overall_stats.get('average_searches_per_day', 0):.1f}")
        print(f"   日均会话: {overall_stats.get('average_sessions_per_day', 0):.1f}")
        
        print(f"\n📅 每日详情:")
        for day_stats in data.get('daily_summaries', [])[:5]:
            date_str = day_stats.get('date', 'Unknown')
            searches = day_stats.get('total_searches', 0)
            sessions = day_stats.get('total_sessions', 0)
            panels = day_stats.get('total_panel_interactions', 0)
            print(f"   {date_str}: {searches}次搜索, {sessions}个会话, {panels}次面板交互")
        
    except Exception as e:
        print(f"❌ 读取综合报告失败: {e}")

def list_all_files():
    """列出所有统计文件"""
    print("📁 所有统计文件:")
    print("-" * 60)
    
    categories = {
        'search': '搜索结果统计',
        'panel': '面板交互统计', 
        'session': '会话总结',
        'daily': '日统计',
        'report': '综合报告'
    }
    
    for cat_key, cat_name in categories.items():
        files = stats_manager.list_files_by_type(cat_key)
        print(f"\n{cat_name} ({len(files)}个文件):")
        
        for file_path in files[-3:]:  # 显示最新的3个
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            print(f"   📄 {file_path.name} ({mod_time.strftime('%m-%d %H:%M')})")

def main():
    parser = argparse.ArgumentParser(description='交互统计文件查看工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # latest 命令
    latest_parser = subparsers.add_parser('latest', help='查看最新文件')
    latest_parser.add_argument('--type', choices=['search', 'panel', 'session', 'daily', 'report'], 
                              help='文件类型')
    latest_parser.add_argument('--count', type=int, default=5, help='显示文件数量')
    
    # view 命令
    view_parser = subparsers.add_parser('view', help='查看指定文件')
    view_parser.add_argument('file_path', help='文件路径')
    
    # daily 命令
    daily_parser = subparsers.add_parser('daily', help='查看日统计')
    daily_parser.add_argument('--date', help='日期 (YYYY-MM-DD格式，默认今天)')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='查看综合报告')
    report_parser.add_argument('--days', type=int, default=7, help='报告天数')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有文件')
    
    args = parser.parse_args()
    
    if args.command == 'latest':
        view_latest_files(args.type, args.count)
    elif args.command == 'view':
        view_file_content(args.file_path)
    elif args.command == 'daily':
        view_daily_summary(args.date)
    elif args.command == 'report':
        view_comprehensive_report(args.days)
    elif args.command == 'list':
        list_all_files()
    else:
        # 默认显示最新文件
        view_latest_files(count=5)
        print("\n" + "="*60)
        print("💡 使用示例:")
        print("   python view_stats.py latest --type search --count 3")
        print("   python view_stats.py daily --date 2025-06-10")
        print("   python view_stats.py report --days 7")
        print("   python view_stats.py list")

if __name__ == "__main__":
    main()
