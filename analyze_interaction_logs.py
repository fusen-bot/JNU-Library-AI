#!/usr/bin/env python3
"""
交互日志数据分析工具
用于分析用户行为数据和生成统计报告
"""

import pandas as pd
import json
from datetime import datetime
import os

def load_interaction_logs():
    """加载交互日志数据"""
    if not os.path.exists('interaction_logs.csv'):
        print("❌ 未找到日志文件 interaction_logs.csv")
        return None
    
    try:
        df = pd.read_csv('interaction_logs.csv')
        print(f"✅ 成功加载 {len(df)} 条日志记录")
        return df
    except Exception as e:
        print(f"❌ 加载日志文件失败: {str(e)}")
        return None

def analyze_search_performance(df):
    """分析搜索性能数据"""
    print("\n🔍 搜索性能分析")
    print("-" * 50)
    
    # 搜索开始和结束记录
    search_starts = df[df['event_type'] == 'search_start']
    search_ends = df[df['event_type'] == 'search_end']
    
    print(f"📊 搜索会话统计:")
    print(f"   总搜索开始次数: {len(search_starts)}")
    print(f"   总搜索完成次数: {len(search_ends)}")
    
    if len(search_ends) > 0:
        # 分析搜索耗时（从session_stats或其他字段）
        durations = []
        for _, row in search_ends.iterrows():
            if pd.notna(row.get('duration_ms', None)):
                durations.append(row['duration_ms'])
        
        if durations:
            print(f"   平均搜索耗时: {sum(durations) / len(durations):.1f}ms")
            print(f"   最快搜索: {min(durations)}ms")
            print(f"   最慢搜索: {max(durations)}ms")
    
    # 按会话分析
    sessions = df['session_id'].unique()
    print(f"   活跃会话数量: {len([s for s in sessions if pd.notna(s)])}")

def analyze_panel_interactions(df):
    """分析悬浮面板交互数据"""
    print("\n📖 悬浮面板交互分析")
    print("-" * 50)
    
    panel_opens = df[df['event_type'] == 'panel_opened']
    panel_closes = df[df['event_type'] == 'panel_closed']
    
    print(f"📊 面板交互统计:")
    print(f"   面板打开次数: {len(panel_opens)}")
    print(f"   面板关闭次数: {len(panel_closes)}")
    
    # 分析各书籍的受欢迎程度
    if len(panel_opens) > 0:
        book_interactions = panel_opens['book_title'].value_counts()
        print(f"\n📚 最受关注的书籍:")
        for i, (book, count) in enumerate(book_interactions.head(5).items(), 1):
            if pd.notna(book):
                print(f"   {i}. {book}: {count}次")
    
    # 分析停留时长
    if len(panel_closes) > 0:
        durations = []
        for _, row in panel_closes.iterrows():
            if pd.notna(row.get('duration_ms', None)):
                durations.append(row['duration_ms'])
        
        if durations:
            print(f"\n⏱️ 面板停留时长统计:")
            print(f"   平均停留时长: {sum(durations) / len(durations):.1f}ms")
            print(f"   最短停留: {min(durations)}ms")
            print(f"   最长停留: {max(durations)}ms")

def analyze_results_display(df):
    """分析结果页面显示数据"""
    print("\n📄 结果页面分析")
    print("-" * 50)
    
    results_shown = df[df['event_type'] == 'results_displayed']
    results_hidden = df[df['event_type'] == 'results_hidden']
    
    print(f"📊 结果页面统计:")
    print(f"   结果显示次数: {len(results_shown)}")
    print(f"   结果隐藏次数: {len(results_hidden)}")
    
    # 分析停留时长
    if len(results_hidden) > 0:
        durations = []
        for _, row in results_hidden.iterrows():
            if pd.notna(row.get('duration_ms', None)):
                durations.append(row['duration_ms'])
        
        if durations:
            print(f"\n⏱️ 结果页面停留时长:")
            print(f"   平均停留时长: {sum(durations) / len(durations):.1f}ms")
            print(f"   最短停留: {min(durations)}ms")
            print(f"   最长停留: {max(durations)}ms")

def analyze_session_summaries(df):
    """分析会话总结数据"""
    print("\n📊 会话总结分析")
    print("-" * 50)
    
    summaries = df[df['event_type'] == 'session_summary']
    
    if len(summaries) == 0:
        print("   暂无会话总结数据")
        return
    
    print(f"📊 会话总结统计:")
    print(f"   会话总结数量: {len(summaries)}")
    
    # 尝试解析会话统计数据
    total_search_count = 0
    total_search_duration = 0
    total_panel_duration = 0
    unique_books_total = 0
    
    for _, row in summaries.iterrows():
        if pd.notna(row.get('session_stats', None)):
            try:
                stats = json.loads(row['session_stats'])
                search_stats = stats.get('searchStats', {})
                panel_stats = stats.get('panelStats', {})
                
                total_search_count += search_stats.get('totalCount', 0)
                total_search_duration += search_stats.get('totalDuration', 0)
                total_panel_duration += panel_stats.get('totalDuration', 0)
                unique_books_total += panel_stats.get('uniqueBooksViewed', 0)
                
            except json.JSONDecodeError:
                continue
    
    if total_search_count > 0:
        print(f"\n🔍 聚合搜索统计:")
        print(f"   总搜索次数: {total_search_count}")
        print(f"   总搜索耗时: {total_search_duration}ms")
        print(f"   平均搜索耗时: {total_search_duration / total_search_count:.1f}ms")
    
    if unique_books_total > 0:
        print(f"\n📖 聚合面板统计:")
        print(f"   总面板停留时长: {total_panel_duration}ms")
        print(f"   总查看书籍数: {unique_books_total}")

def generate_time_analysis(df):
    """生成时间分析"""
    print("\n⏰ 时间分布分析")
    print("-" * 50)
    
    # 转换时间戳
    df['datetime'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df_with_time = df.dropna(subset=['datetime'])
    
    if len(df_with_time) == 0:
        print("   无有效时间数据")
        return
    
    # 按小时分析活动
    df_with_time['hour'] = df_with_time['datetime'].dt.hour
    hourly_activity = df_with_time['hour'].value_counts().sort_index()
    
    print("📈 按小时活动分布:")
    for hour, count in hourly_activity.head(10).items():
        print(f"   {hour:02d}:00 - {count}次交互")

def main():
    print("=" * 70)
    print("📊 用户交互行为日志分析报告")
    print("=" * 70)
    
    # 加载数据
    df = load_interaction_logs()
    if df is None:
        return
    
    print(f"\n📅 数据时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
    print(f"📈 总交互事件数: {len(df)}")
    print(f"🎯 事件类型分布:")
    event_counts = df['event_type'].value_counts()
    for event_type, count in event_counts.items():
        if pd.notna(event_type):
            print(f"   {event_type}: {count}次")
    
    # 执行各项分析
    analyze_search_performance(df)
    analyze_panel_interactions(df)
    analyze_results_display(df)
    analyze_session_summaries(df)
    generate_time_analysis(df)
    
    print("\n" + "=" * 70)
    print("✨ 分析完成！")
    print("💡 提示: 可以基于这些数据进一步优化用户体验")
    print("=" * 70)

if __name__ == "__main__":
    main()
