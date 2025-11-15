#!/usr/bin/env python3
"""
交互统计管理器
用于管理交互统计文件的创建、读取和分析
"""

import json
import os
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, TypedDict

class BookLogRecord(TypedDict, total=False):
    """单本图书在一次检索中的聚合交互记录"""
    title: str
    author: Optional[str]
    isbn: Optional[str]
    logical_reason: Optional[Dict[str, Any]]
    social_reason: Optional[Dict[str, Any]]
    hover_count: int
    total_hover_time_ms: int
    click_count: int
    rating: Optional[float]


class QueryLogRecord(TypedDict, total=False):
    """
    聚合检索日志记录（按“检索请求”维度）

    - 一行 JSONL 对应一次检索
    - 仅包含本次检索相关的聚合信息
    """
    session_id: str
    timestamp: str
    query_text: str
    books: List[BookLogRecord]


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
    
    def save_session_event(self, session_id: str, event: Dict[str, Any]) -> Optional[Path]:
        """
        保存Session事件到文件
        使用JSON Lines格式，一个Session一个文件，事件追加写入

        Args:
            session_id: 会话ID（格式：被试_001 或 交互 XX_YYYYMMDD）
            event: 事件数据字典

        Returns:
            保存的文件路径，如果保存失败返回None
        """
        try:
            # 将Session ID转换为文件名格式（替换空格为下划线，保持中文字符）
            # 例如：被试_001 -> 被试_001.jsonl
            # 例如：交互 01_20250905 -> 交互_01_20250905.jsonl
            filename = session_id.replace(' ', '_') + '.jsonl'
            session_file = self.session_dir / filename

            # 添加事件记录时间
            event_with_metadata = {
                **event,
                'saved_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                'session_id': session_id
            }

            # 追加写入到JSON Lines文件
            with open(session_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_with_metadata, ensure_ascii=False) + '\n')

            return session_file

        except Exception as e:
            print(f"保存Session事件失败: {str(e)}")
            return None

    def save_query_log_record(self, record: QueryLogRecord) -> Optional[Path]:
        """
        保存聚合后的检索日志记录（QueryLogRecord）到JSONL文件

        与 save_session_event 不同：
        - 不再依赖 event_type / 事件流
        - 一行记录一个完整的检索请求及其图书交互聚合结果

        Args:
            record: 聚合后的检索日志记录

        Returns:
            保存的文件路径，如果保存失败返回None
        """
        try:
            session_id: Optional[str] = record.get("session_id")
            if not session_id:
                raise ValueError("缺少 session_id 字段，无法保存聚合检索日志")

            filename = session_id.replace(" ", "_") + ".jsonl"
            session_file = self.session_dir / filename

            record_with_metadata: Dict[str, Any] = {
                **record,
                "saved_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            }

            with open(session_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record_with_metadata, ensure_ascii=False) + "\n")

            return session_file
        except Exception as e:
            print(f"保存聚合检索日志失败: {str(e)}")
            return None
    
    def load_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """
        加载指定Session的所有事件

        Args:
            session_id: 会话ID（格式：交互 XX_YYYYMMDD）

        Returns:
            事件列表
        """
        # 将Session ID转换为文件名格式
        filename = session_id.replace(' ', '_') + '.jsonl'
        session_file = self.session_dir / filename

        if not session_file.exists():
            return []

        events = []
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        event = json.loads(line)
                        events.append(event)
        except Exception as e:
            print(f"加载Session事件失败: {str(e)}")

        return events
    
    def list_sessions(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        列出最近几天的Session

        Args:
            days: 天数

        Returns:
            Session摘要列表
        """
        sessions = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for session_file in self.session_dir.glob("*.jsonl"):
            try:
                # 从文件修改时间判断是否在时间范围内
                if datetime.fromtimestamp(session_file.stat().st_mtime) < cutoff_date:
                    continue

                # 从文件名解析Session ID（将下划线转换回空格）
                # 例如：交互_01_20250905.jsonl -> 交互 01_20250905
                filename = session_file.stem
                session_id = filename.replace('_', ' ', 1)  # 只替换第一个下划线

                events = self.load_session_events(session_id)

                if not events:
                    continue

                # 分析Session基本信息
                session_start = None
                session_end = None
                event_types = {}
                search_sessions = []

                for event in events:
                    event_type = event.get('event_type', 'unknown')
                    event_types[event_type] = event_types.get(event_type, 0) + 1

                    if event_type == 'session_start' and not session_start:
                        session_start = event.get('timestamp')
                    elif event_type == 'session_end':
                        session_end = event.get('timestamp')
                    elif event_type == 'search_session_start':
                        search_sessions.append({
                            'search_id': event.get('search_id'),
                            'query': event.get('query'),
                            'timestamp': event.get('timestamp')
                        })

                sessions.append({
                    'session_id': session_id,
                    'session_start': session_start,
                    'session_end': session_end,
                    'total_events': len(events),
                    'event_types': event_types,
                    'search_sessions_count': len(search_sessions),
                    'search_sessions': search_sessions[:5],  # 只显示前5个
                    'file_path': str(session_file)
                })

            except Exception as e:
                print(f"分析Session文件失败 {session_file}: {str(e)}")
                continue

        # 按开始时间排序
        sessions.sort(key=lambda x: x.get('session_start', ''), reverse=True)
        return sessions
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取特定Session的详细摘要
        
        Args:
            session_id: 会话ID
            
        Returns:
            Session摘要字典
        """
        events = self.load_session_events(session_id)
        
        if not events:
            return None
        
        # 分析Session数据
        session_start = None
        session_end = None
        search_sessions = []
        book_interactions = {}
        event_timeline = []
        
        for event in events:
            event_type = event.get('event_type', 'unknown')
            timestamp = event.get('timestamp')
            
            event_timeline.append({
                'timestamp': timestamp,
                'event_type': event_type,
                'summary': self._get_event_summary(event)
            })
            
            if event_type == 'session_start':
                session_start = timestamp
            elif event_type == 'session_end':
                session_end = timestamp
            elif event_type == 'search_session_start':
                search_sessions.append({
                    'search_id': event.get('search_id'),
                    'query': event.get('query'),
                    'start_time': timestamp
                })
            elif event_type == 'search_session_end':
                # 更新对应的搜索会话结束信息
                search_id = event.get('search_id')
                for search in search_sessions:
                    if search['search_id'] == search_id:
                        search.update({
                            'end_time': timestamp,
                            'duration_ms': event.get('duration_ms'),
                            'books_clicked_count': event.get('books_clicked_count', 0),
                            'end_reason': event.get('end_reason')
                        })
                        break
            elif event_type in ['book_clicked', 'book_hover_start', 'book_hover_end']:
                book_isbn = event.get('book_isbn', 'unknown')
                book_title = event.get('book_title', 'unknown')
                
                if book_isbn not in book_interactions:
                    book_interactions[book_isbn] = {
                        'isbn': book_isbn,
                        'title': book_title,
                        'click_count': 0,
                        'hover_count': 0,
                        'total_hover_time': 0
                    }
                
                if event_type == 'book_clicked':
                    book_interactions[book_isbn]['click_count'] += 1
                elif event_type == 'book_hover_start':
                    book_interactions[book_isbn]['hover_count'] += 1
                elif event_type == 'book_hover_end':
                    hover_duration = event.get('hover_duration_ms', 0)
                    book_interactions[book_isbn]['total_hover_time'] += hover_duration
        
        session_duration = None
        if session_start and session_end:
            start_dt = datetime.fromisoformat(session_start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(session_end.replace('Z', '+00:00'))
            session_duration = int((end_dt - start_dt).total_seconds() * 1000)
        
        return {
            'session_id': session_id,
            'session_start': session_start,
            'session_end': session_end,
            'session_duration_ms': session_duration,
            'total_events': len(events),
            'search_sessions': search_sessions,
            'book_interactions': list(book_interactions.values()),
            'event_timeline': event_timeline[-20:]  # 最近20个事件
        }
    
    def _get_event_summary(self, event: Dict[str, Any]) -> str:
        """生成事件的简短摘要"""
        event_type = event.get('event_type', 'unknown')
        
        if event_type == 'search_session_start':
            return f"开始搜索: {event.get('query', 'N/A')}"
        elif event_type == 'search_session_end':
            duration = event.get('duration_ms', 0)
            return f"结束搜索, 耗时: {duration}ms, 点击书籍: {event.get('books_clicked_count', 0)}本"
        elif event_type == 'book_clicked':
            return f"点击书籍: {event.get('book_title', 'N/A')}"
        elif event_type == 'book_hover_start':
            return f"悬停书籍: {event.get('book_title', 'N/A')}"
        elif event_type == 'book_hover_end':
            duration = event.get('hover_duration_ms', 0)
            return f"离开书籍: {event.get('book_title', 'N/A')}, 停留: {duration}ms"
        elif event_type == 'heartbeat':
            return "心跳事件"
        else:
            return event_type
    
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
