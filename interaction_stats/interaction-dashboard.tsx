import React, { useState, useMemo, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Clock, Book, Eye, MousePointer, Activity, FileText } from 'lucide-react';

// 类型定义（新的聚合检索日志结构）
interface BookLogEntry {
  title: string;
  author?: string;
  isbn?: string;
  hover_count: number;
  total_hover_time_ms: number;
  click_count: number;
  rating?: number | null;
}

interface QueryLogRecord {
  session_id: string;
  timestamp: string;
  query_text: string;
  books: BookLogEntry[];
}

interface BookInteraction {
  isbn: string;
  title: string;
  author?: string;
  hoverCount: number;
  totalHoverTimeMs: number;
  clickCount: number;
}

interface StatCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  value: string | number;
  subtitle?: string;
  color?: string;
}

const InteractionDashboard = () => {
  const [sessionFiles, setSessionFiles] = useState<string[]>([]);
  const [selectedSession, setSelectedSession] = useState<string>('');
  const [records, setRecords] = useState<QueryLogRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedTab, setSelectedTab] = useState('overview');
  
  useEffect(() => {
    fetch('./session-list.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((files: string[]) => {
        if (files && files.length > 0) {
          const sortedFiles = files.sort();
          setSessionFiles(sortedFiles);
          setSelectedSession(sortedFiles[sortedFiles.length - 1]); // Select the last file by default
        } else {
          setSessionFiles([]);
          setIsLoading(false);
        }
      })
      .catch(error => {
        console.error('Error loading session list:', error);
        setSessionFiles([]); // Set to empty array on error
        setIsLoading(false); // Stop loading indicator
      });
  }, []);

  useEffect(() => {
    if (!selectedSession) return;

    setIsLoading(true);
    // 读取并解析选中的聚合日志文件
    fetch(`./sessions/${selectedSession}`)
      .then(response => response.text())
      .then(rawData => {
        const parsedRecords = rawData.split('\n')
          .filter(line => line.trim())
          .map(line => {
            try {
              return JSON.parse(line);
            } catch (e) {
              console.error('Failed to parse line:', line, e);
              return null;
            }
          })
          .filter((record): record is QueryLogRecord => record !== null && !!record.session_id && !!record.query_text && Array.isArray(record.books));
        setRecords(parsedRecords);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error loading session data:', error);
        setIsLoading(false);
      });
  }, [selectedSession]);
  
  // 统计信息（基于聚合检索记录）
  const stats = useMemo(() => {
    if (records.length === 0) {
      return {
        totalQueries: 0,
        uniqueBooks: 0,
        totalHoverCount: 0,
        totalHoverTimeMs: 0,
        totalClicks: 0,
        bookInteractions: {} as Record<string, BookInteraction>
      };
    }
    const bookInteractions: Record<string, BookInteraction> = {};

    let totalHoverCount = 0;
    let totalHoverTimeMs = 0;
    let totalClicks = 0;

    records.forEach(record => {
      record.books.forEach(book => {
        const isbn = book.isbn || book.title;
        if (!isbn) return;

        if (!bookInteractions[isbn]) {
          bookInteractions[isbn] = {
            isbn,
            title: book.title,
            author: book.author,
            hoverCount: 0,
            totalHoverTimeMs: 0,
            clickCount: 0
          };
        }

        const interaction = bookInteractions[isbn];
        interaction.hoverCount += book.hover_count || 0;
        interaction.totalHoverTimeMs += book.total_hover_time_ms || 0;
        interaction.clickCount += book.click_count || 0;

        totalHoverCount += book.hover_count || 0;
        totalHoverTimeMs += book.total_hover_time_ms || 0;
        totalClicks += book.click_count || 0;
      });
    });

    return {
      totalQueries: records.length,
      uniqueBooks: Object.keys(bookInteractions).length,
      totalHoverCount,
      totalHoverTimeMs,
      totalClicks,
      bookInteractions
    };
  }, [records]);

  const topBooksData = Object.values(stats.bookInteractions)
    .sort((a, b) => b.totalHoverTimeMs - a.totalHoverTimeMs)
    .slice(0, 5)
    .map(book => ({
      title: book.title.length > 20 ? book.title.substring(0, 20) + '...' : book.title,
      hoverTime: book.totalHoverTimeMs,
      hoverCount: book.hoverCount,
      clicks: book.clickCount
    }));

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];

  const StatCard: React.FC<StatCardProps> = ({ icon: Icon, title, value, subtitle, color = "blue" }) => (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
          {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
        </div>
        <Icon className={`h-8 w-8 text-${color}-500`} />
      </div>
    </div>
  );

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载分析数据...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">交互数据统计面板</h1>
          <p className="text-gray-600 mt-2">江南大学图书馆OPAC系统用户行为分析</p>
        </div>

        {/* Session Selector */}
        <div className="mb-6">
          <label htmlFor="session-select" className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <FileText className="w-4 h-4 mr-2" />
            选择分析的会话文件:
          </label>
          <select
            id="session-select"
            value={selectedSession}
            onChange={(e) => setSelectedSession(e.target.value)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md shadow-sm"
          >
            {sessionFiles.map(file => (
              <option key={file} value={file}>
                {file}
              </option>
            ))}
          </select>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: '总览', icon: Activity },
              { id: 'books', label: '图书交互', icon: Book },
              { id: 'timeline', label: '时间线', icon: Clock }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  selectedTab === tab.id
                    ? 'text-blue-600 bg-blue-100'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {selectedTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                icon={Activity}
                title="总检索次数"
                value={stats.totalQueries}
                subtitle="聚合后的检索请求数"
                color="blue"
              />
              <StatCard
                icon={Book}
                title="涉及图书数"
                value={stats.uniqueBooks}
                subtitle="用户浏览的不同图书"
                color="green"
              />
              <StatCard
                icon={MousePointer}
                title="总悬停次数"
                value={stats.totalHoverCount}
                subtitle="所有图书的悬停次数总和"
                color="purple"
              />
              <StatCard
                icon={Clock}
                title="总悬停时长"
                value={`${stats.totalHoverTimeMs} ms`}
                subtitle={`总点击 ${stats.totalClicks} 次`}
                color="orange"
              />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top Books Chart（按总悬停时长排序） */}
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold mb-4">热门图书交互</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topBooksData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="title" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      fontSize={12}
                    />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="hoverTime" stackId="a" fill="#8884d8" name="总悬停时间(ms)" />
                    <Bar dataKey="clicks" stackId="a" fill="#82ca9d" name="点击次数" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Books Tab */}
        {selectedTab === 'books' && (
          <div className="space-y-6">
            {/* Book Interaction Details */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">图书交互详情</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        图书标题
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        作者
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        悬停次数
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        总悬停时间 (ms)
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        点击次数
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.values(stats.bookInteractions).map((book: BookInteraction, index: number) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{book.title}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {book.author || '未知作者'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {book.hoverCount}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {book.totalHoverTimeMs}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {book.clickCount}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Timeline Tab */}
        {selectedTab === 'timeline' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold mb-4">时间线视图</h3>
            <p className="text-gray-500 text-sm">
              新的聚合日志结构不再记录逐条时间线事件，此标签页仅保留占位，后续如需时间线可在生成阶段额外导出。
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InteractionDashboard;