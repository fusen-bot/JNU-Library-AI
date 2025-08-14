#!/usr/bin/env python3
"""
交互统计管理器
用于管理交互统计文件的创建、读取和分析
"""

import json
import os
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

class StatsManager:
    """统计管理器类"""
    
    def __init__(self):
        self.base_dir = Path("interaction_stats")
        self.search_dir = self.base_dir / "search_results"
        self.panel_dir = self.base_dir / "panel_interactions"
        self.session_dir = self.base_dir / "sessions"
        self.daily_dir = self.base_dir / "daily"
        self.report_dir = self.base_dir / "summary_reports"
        
        # 确保目录存在
        for dir_path in [self.search_dir, self.panel_dir, self.session_dir, 
                        self.daily_dir, self.report_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def list_files_by_type(self, file_type: Optional[str] = None) -> List[Path]:
        """根据类型列出文件"""
        if file_type == 'search':
            return list(self.search_dir.glob("*.json"))
        elif file_type == 'panel':
            return list(self.panel_dir.glob("*.json"))
        elif file_type == 'session':
            return list(self.session_dir.glob("*.json"))
        elif file_type == 'daily':
            return list(self.daily_dir.glob("*.json"))
        elif file_type == 'report':
            return list(self.report_dir.glob("*.json"))
        else:
            # 返回所有类型的文件
            all_files = []
            for dir_path in [self.search_dir, self.panel_dir, self.session_dir, 
                           self.daily_dir, self.report_dir]:
                all_files.extend(dir_path.glob("*.json"))
            return all_files
    
    def save_daily_summary(self, target_date: date) -> Path:
        """保存日统计总结"""
        date_str = target_date.strftime('%Y-%m-%d')
        daily_file = self.daily_dir / f"daily_summary_{date_str}.json"
        
        # 如果文件已存在，直接返回
        if daily_file.exists():
            return daily_file
        
        # 收集当天的数据
        daily_stats = self._collect_daily_data(target_date)
        
        # 保存到文件
        with open(daily_file, 'w', encoding='utf-8') as f:
            json.dump(daily_stats, f, ensure_ascii=False, indent=2)
        
        return daily_file
    
    def generate_comprehensive_report(self, days: int = 7) -> Path:
        """生成综合报告"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        report_file = self.report_dir / f"comprehensive_report_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.json"
        
        # 如果文件已存在，直接返回
        if report_file.exists():
            return report_file
        
        # 收集多天数据
        report_data = self._collect_comprehensive_data(start_date, end_date)
        
        # 保存到文件
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_file
    
    def _collect_daily_data(self, target_date: date) -> Dict[str, Any]:
        """收集指定日期的数据"""
        date_str = target_date.strftime('%Y-%m-%d')
        
        # 收集搜索数据
        search_files = [f for f in self.search_dir.glob("*.json") 
                       if date_str in f.name]
        search_details = []
        total_searches = 0
        total_search_duration = 0
        unique_queries = set()
        
        for file_path in search_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    search_details.append({
                        'query': data.get('user_query', ''),
                        'duration_ms': data.get('search_stats', {}).get('duration_ms', 0)
                    })
                    total_searches += 1
                    total_search_duration += data.get('search_stats', {}).get('duration_ms', 0)
                    unique_queries.add(data.get('user_query', ''))
            except Exception:
                continue
        
        # 收集面板交互数据
        panel_files = [f for f in self.panel_dir.glob("*.json") 
                      if date_str in f.name]
        panel_details = []
        total_panel_interactions = 0
        total_panel_duration = 0
        unique_books = set()
        
        for file_path in panel_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    panel_details.append({
                        'book_title': data.get('panel_stats', {}).get('book_title', ''),
                        'duration_ms': data.get('panel_stats', {}).get('duration_ms', 0)
                    })
                    total_panel_interactions += 1
                    total_panel_duration += data.get('panel_stats', {}).get('duration_ms', 0)
                    unique_books.add(data.get('panel_stats', {}).get('book_title', ''))
            except Exception:
                continue
        
        # 收集会话数据
        session_files = [f for f in self.session_dir.glob("*.json") 
                        if date_str in f.name]
        total_sessions = len(session_files)
        
        # 生成统计摘要
        summary = {
            'total_search_duration_ms': total_search_duration,
            'average_search_duration_ms': total_search_duration / max(total_searches, 1),
            'unique_queries': len(unique_queries),
            'total_panel_duration_ms': total_panel_duration,
            'unique_books_viewed': len(unique_books)
        }
        
        return {
            'date': date_str,
            'daily_statistics': {
                'total_searches': total_searches,
                'total_panel_interactions': total_panel_interactions,
                'total_sessions': total_sessions,
                'search_details': search_details[:10],  # 只保留前10个
                'panel_details': panel_details[:10],    # 只保留前10个
                'summary': summary
            }
        }
    
    def _collect_comprehensive_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """收集综合数据"""
        daily_summaries = []
        total_searches = 0
        total_sessions = 0
        total_panel_interactions = 0
        
        current_date = start_date
        while current_date <= end_date:
            daily_file = self.save_daily_summary(current_date)
            try:
                with open(daily_file, 'r', encoding='utf-8') as f:
                    daily_data = json.load(f)
                    daily_stats = daily_data.get('daily_statistics', {})
                    daily_summaries.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'total_searches': daily_stats.get('total_searches', 0),
                        'total_sessions': daily_stats.get('total_sessions', 0),
                        'total_panel_interactions': daily_stats.get('total_panel_interactions', 0)
                    })
                    total_searches += daily_stats.get('total_searches', 0)
                    total_sessions += daily_stats.get('total_sessions', 0)
                    total_panel_interactions += daily_stats.get('total_panel_interactions', 0)
            except Exception:
                pass
            current_date += timedelta(days=1)
        
        days_count = (end_date - start_date).days + 1
        
        return {
            'report_period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': days_count
            },
            'overall_statistics': {
                'total_searches': total_searches,
                'total_sessions': total_sessions,
                'total_panel_interactions': total_panel_interactions,
                'average_searches_per_day': total_searches / max(days_count, 1),
                'average_sessions_per_day': total_sessions / max(days_count, 1)
            },
            'daily_summaries': daily_summaries
        }

# 创建全局实例
stats_manager = StatsManager()
