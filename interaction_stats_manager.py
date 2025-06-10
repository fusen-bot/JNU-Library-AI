#!/usr/bin/env python3
"""
交互事件统计管理器
专门负责将交互数据输出到不同的统计文件夹中
"""

import os
import json
import csv
from datetime import datetime, date
from pathlib import Path
import pandas as pd

class InteractionStatsManager:
    def __init__(self, base_dir="interaction_stats"):
        """
        初始化交互统计管理器
        
        Args:
            base_dir (str): 统计文件的基础目录
        """
        self.base_dir = Path(base_dir)
        self.ensure_directories()
        
    def ensure_directories(self):
        """确保所有必要的目录存在"""
        subdirs = [
            'daily',           # 日统计
            'sessions',        # 会话统计  
            'search_results',  # 搜索结果统计
            'panel_interactions',  # 面板交互统计
            'summary_reports'  # 总结报告
        ]
        
        for subdir in subdirs:
            (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def save_search_result_stats(self, session_id, user_query, search_data):
        """
        保存搜索结果统计
        
        Args:
            session_id (str): 会话ID
            user_query (str): 用户查询
            search_data (dict): 搜索数据
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H-%M-%S')
        
        # 搜索结果文件名
        filename = f"search_{date_str}_{time_str}_{session_id[:8]}.json"
        filepath = self.base_dir / 'search_results' / filename
        
        # 构建搜索结果数据
        result_data = {
            'timestamp': timestamp.isoformat(),
            'session_id': session_id,
            'user_query': user_query,
            'search_stats': search_data,
            'metadata': {
                'file_created': timestamp.isoformat(),
                'data_type': 'search_result'
            }
        }
        
        # 保存到JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 搜索结果统计已保存: {filepath}")
        return filepath
    
    def save_panel_interaction_stats(self, session_id, panel_data):
        """
        保存面板交互统计
        
        Args:
            session_id (str): 会话ID
            panel_data (dict): 面板交互数据
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H-%M-%S')
        
        # 面板交互文件名
        filename = f"panel_{date_str}_{time_str}_{session_id[:8]}.json"
        filepath = self.base_dir / 'panel_interactions' / filename
        
        # 构建面板交互数据
        interaction_data = {
            'timestamp': timestamp.isoformat(),
            'session_id': session_id,
            'panel_stats': panel_data,
            'metadata': {
                'file_created': timestamp.isoformat(),
                'data_type': 'panel_interaction'
            }
        }
        
        # 保存到JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(interaction_data, f, ensure_ascii=False, indent=2)
        
        print(f"📖 面板交互统计已保存: {filepath}")
        return filepath
    
    def save_session_summary(self, session_id, session_stats):
        """
        保存会话总结
        
        Args:
            session_id (str): 会话ID
            session_stats (dict): 会话统计数据
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H-%M-%S')
        
        # 会话文件名
        filename = f"session_{date_str}_{time_str}_{session_id[:8]}.json"
        filepath = self.base_dir / 'sessions' / filename
        
        # 构建会话数据
        session_data = {
            'timestamp': timestamp.isoformat(),
            'session_id': session_id,
            'session_summary': session_stats,
            'metadata': {
                'file_created': timestamp.isoformat(),
                'data_type': 'session_summary'
            }
        }
        
        # 保存到JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        print(f"📋 会话总结已保存: {filepath}")
        return filepath
    
    def save_daily_summary(self, target_date=None):
        """
        生成并保存日统计总结
        
        Args:
            target_date (date): 目标日期，默认为今天
        """
        if target_date is None:
            target_date = date.today()
        
        date_str = target_date.strftime('%Y-%m-%d')
        
        # 收集当天的所有统计数据
        daily_stats = self._collect_daily_stats(target_date)
        
        # 日统计文件名
        filename = f"daily_summary_{date_str}.json"
        filepath = self.base_dir / 'daily' / filename
        
        # 构建日统计数据
        daily_data = {
            'date': date_str,
            'generated_at': datetime.now().isoformat(),
            'daily_statistics': daily_stats,
            'metadata': {
                'file_created': datetime.now().isoformat(),
                'data_type': 'daily_summary'
            }
        }
        
        # 保存到JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(daily_data, f, ensure_ascii=False, indent=2)
        
        print(f"📅 日统计总结已保存: {filepath}")
        return filepath
    
    def _collect_daily_stats(self, target_date):
        """
        收集指定日期的统计数据
        
        Args:
            target_date (date): 目标日期
            
        Returns:
            dict: 日统计数据
        """
        date_str = target_date.strftime('%Y-%m-%d')
        
        # 统计当天的搜索结果
        search_files = list((self.base_dir / 'search_results').glob(f"search_{date_str}_*.json"))
        panel_files = list((self.base_dir / 'panel_interactions').glob(f"panel_{date_str}_*.json"))
        session_files = list((self.base_dir / 'sessions').glob(f"session_{date_str}_*.json"))
        
        stats = {
            'total_searches': len(search_files),
            'total_panel_interactions': len(panel_files),
            'total_sessions': len(session_files),
            'search_details': [],
            'panel_details': [],
            'session_details': []
        }
        
        # 收集搜索详情
        total_search_duration = 0
        search_queries = []
        
        for search_file in search_files:
            try:
                with open(search_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    search_stats = data.get('search_stats', {})
                    
                    if 'duration_ms' in search_stats:
                        total_search_duration += search_stats['duration_ms']
                    
                    if data.get('user_query'):
                        search_queries.append(data['user_query'])
                    
                    stats['search_details'].append({
                        'query': data.get('user_query', ''),
                        'duration_ms': search_stats.get('duration_ms', 0),
                        'timestamp': data.get('timestamp', '')
                    })
            except Exception as e:
                print(f"⚠️ 读取搜索文件失败: {search_file}, 错误: {e}")
        
        # 收集面板交互详情
        total_panel_duration = 0
        unique_books = set()
        
        for panel_file in panel_files:
            try:
                with open(panel_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    panel_stats = data.get('panel_stats', {})
                    
                    if 'duration_ms' in panel_stats:
                        total_panel_duration += panel_stats['duration_ms']
                    
                    if 'book_title' in panel_stats:
                        unique_books.add(panel_stats['book_title'])
                    
                    stats['panel_details'].append({
                        'book_title': panel_stats.get('book_title', ''),
                        'duration_ms': panel_stats.get('duration_ms', 0),
                        'timestamp': data.get('timestamp', '')
                    })
            except Exception as e:
                print(f"⚠️ 读取面板文件失败: {panel_file}, 错误: {e}")
        
        # 添加汇总统计
        stats['summary'] = {
            'total_search_duration_ms': total_search_duration,
            'average_search_duration_ms': total_search_duration / len(search_files) if search_files else 0,
            'total_panel_duration_ms': total_panel_duration,
            'unique_books_viewed': len(unique_books),
            'unique_queries': len(set(search_queries))
        }
        
        return stats
    
    def generate_comprehensive_report(self, days=7):
        """
        生成综合报告
        
        Args:
            days (int): 报告覆盖的天数
        """
        timestamp = datetime.now()
        filename = f"comprehensive_report_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        filepath = self.base_dir / 'summary_reports' / filename
        
        # 收集多天的数据
        report_data = {
            'generated_at': timestamp.isoformat(),
            'report_period_days': days,
            'daily_summaries': [],
            'overall_statistics': {}
        }
        
        # 生成每日总结
        for i in range(days):
            target_date = date.today() - pd.Timedelta(days=i)
            daily_stats = self._collect_daily_stats(target_date)
            daily_stats['date'] = target_date.strftime('%Y-%m-%d')
            report_data['daily_summaries'].append(daily_stats)
        
        # 计算总体统计
        total_searches = sum(day['total_searches'] for day in report_data['daily_summaries'])
        total_sessions = sum(day['total_sessions'] for day in report_data['daily_summaries'])
        total_panels = sum(day['total_panel_interactions'] for day in report_data['daily_summaries'])
        
        report_data['overall_statistics'] = {
            'total_searches': total_searches,
            'total_sessions': total_sessions,
            'total_panel_interactions': total_panels,
            'average_searches_per_day': total_searches / days if days > 0 else 0,
            'average_sessions_per_day': total_sessions / days if days > 0 else 0
        }
        
        # 保存报告
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📈 综合报告已生成: {filepath}")
        return filepath
    
    def list_files_by_type(self, data_type=None):
        """
        列出指定类型的统计文件
        
        Args:
            data_type (str): 数据类型 ('search', 'panel', 'session', 'daily', 'report')
        
        Returns:
            list: 文件路径列表
        """
        if data_type == 'search':
            return list((self.base_dir / 'search_results').glob('*.json'))
        elif data_type == 'panel':
            return list((self.base_dir / 'panel_interactions').glob('*.json'))
        elif data_type == 'session':
            return list((self.base_dir / 'sessions').glob('*.json'))
        elif data_type == 'daily':
            return list((self.base_dir / 'daily').glob('*.json'))
        elif data_type == 'report':
            return list((self.base_dir / 'summary_reports').glob('*.json'))
        else:
            # 返回所有文件
            all_files = []
            for subdir in ['search_results', 'panel_interactions', 'sessions', 'daily', 'summary_reports']:
                all_files.extend((self.base_dir / subdir).glob('*.json'))
            return all_files
    
    def cleanup_old_files(self, days_to_keep=30):
        """
        清理旧的统计文件
        
        Args:
            days_to_keep (int): 保留的天数
        """
        cutoff_date = datetime.now() - pd.Timedelta(days=days_to_keep)
        deleted_count = 0
        
        for file_path in self.list_files_by_type():
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"🗑️ 已删除旧文件: {file_path}")
            except Exception as e:
                print(f"⚠️ 删除文件失败: {file_path}, 错误: {e}")
        
        print(f"🧹 清理完成，共删除 {deleted_count} 个旧文件")
        return deleted_count

# 创建全局实例
stats_manager = InteractionStatsManager()

if __name__ == "__main__":
    # 示例用法
    print("📊 交互统计管理器测试")
    
    # 测试数据
    test_session_id = "test_session_123"
    test_search_data = {
        "duration_ms": 1500,
        "total_duration_ms": 1500,
        "total_search_count": 1
    }
    test_panel_data = {
        "book_title": "测试书籍",
        "duration_ms": 2500,
        "panel_total_duration_ms": 2500
    }
    test_session_stats = {
        "searchStats": {"totalCount": 1, "totalDuration": 1500},
        "panelStats": {"totalDuration": 2500, "uniqueBooksViewed": 1}
    }
    
    # 保存测试数据
    stats_manager.save_search_result_stats(test_session_id, "测试查询", test_search_data)
    stats_manager.save_panel_interaction_stats(test_session_id, test_panel_data)
    stats_manager.save_session_summary(test_session_id, test_session_stats)
    
    # 生成日统计
    stats_manager.save_daily_summary()
    
    # 生成综合报告
    stats_manager.generate_comprehensive_report(7)
    
    print("✅ 测试完成！")
