import React, { useState, useMemo, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Clock, Book, Eye, MousePointer, Activity, FileText } from 'lucide-react';

// 类型定义
interface InteractionEvent {
  session_id: string;
  event_type: string;
  timestamp: string;
  timestamp_since_session_start: number;
  book_isbn?: string;
  book_title?: string;
  book_author?: string;
  hover_duration_ms?: number;
  total_hover_time_ms?: number;
  expand_count?: number;
  total_expand_count?: number;
}

interface BookInteraction {
  title: string;
  hovers: number;
  clicks: number;
  totalHoverTime: number;
}

interface ClickedBook {
  title: string;
  author: string;
  isbn: string;
  timestamp: string;
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
  const [events, setEvents] = useState<InteractionEvent[]>([]);
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
    // Fetch and parse the selected session file
    fetch(`./sessions/${selectedSession}`)
      .then(response => response.text())
      .then(rawData => {
        const parsedEvents = rawData.split('\n')
          .filter(line => line.trim())
          .map(line => {
            try {
              return JSON.parse(line);
            } catch (e) {
              console.error('Failed to parse line:', line, e);
              return null;
            }
          })
          .filter((event): event is InteractionEvent => event !== null);
        setEvents(parsedEvents);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error loading session data:', error);
        setIsLoading(false);
      });
  }, [selectedSession]);
  
  // Calculate statistics
  const stats = useMemo(() => {
    if (events.length === 0) {
      return {
        eventTypes: {},
        bookInteractions: {},
        clickedBooks: [],
        sessionDuration: 0,
        avgHoverDuration: 0,
        totalEvents: 0,
        uniqueBooks: 0
      };
    }
    const eventTypes: Record<string, number> = {};
    const bookInteractions: Record<string, BookInteraction> = {};
    const hoverDurations: number[] = [];
    const clickedBooks: ClickedBook[] = [];
    
    events.forEach((event: InteractionEvent) => {
      // Count event types
      eventTypes[event.event_type] = (eventTypes[event.event_type] || 0) + 1;
      
      // Track book interactions
      if (event.book_isbn && event.book_title) {
        if (!bookInteractions[event.book_isbn]) {
          bookInteractions[event.book_isbn] = {
            title: event.book_title,
            hovers: 0,
            clicks: 0,
            totalHoverTime: 0
          };
        }
        
        if (event.event_type === 'book_hover_start') {
          bookInteractions[event.book_isbn].hovers++;
        } else if (event.event_type === 'book_clicked') {
          bookInteractions[event.book_isbn].clicks++;
          clickedBooks.push({
            title: event.book_title || '',
            author: event.book_author || '未知作者',
            isbn: event.book_isbn || '',
            timestamp: event.timestamp
          });
        } else if (event.event_type === 'book_hover_end' && event.hover_duration_ms) {
          bookInteractions[event.book_isbn].totalHoverTime += event.hover_duration_ms;
          hoverDurations.push(event.hover_duration_ms);
        }
      }
    });
    
    const sessionDuration = Math.max(...events.map(e => e.timestamp_since_session_start)) / 1000; // in seconds
    const avgHoverDuration = hoverDurations.length > 0 
      ? Math.round(hoverDurations.reduce((a, b) => a + b, 0) / hoverDurations.length)
      : 0;
    
    return {
      eventTypes,
      bookInteractions,
      clickedBooks,
      sessionDuration,
      avgHoverDuration,
      totalEvents: events.length,
      uniqueBooks: Object.keys(bookInteractions).length
    };
  }, [events]);

  // Prepare chart data
  const eventTypeData = Object.entries(stats.eventTypes).map(([type, count]) => ({
    type: type.replace('_', ' '),
    count
  }));

  const topBooksData = Object.values(stats.bookInteractions)
    .sort((a, b) => (b.hovers + b.clicks) - (a.hovers + a.clicks))
    .slice(0, 5)
    .map(book => ({
      title: book.title.length > 20 ? book.title.substring(0, 20) + '...' : book.title,
      interactions: book.hovers + book.clicks,
      hovers: book.hovers,
      clicks: book.clicks
    }));

  const timelineData = events
    .filter(e => ['book_hover_start', 'book_clicked'].includes(e.event_type))
    .map(event => ({
      time: Math.round(event.timestamp_since_session_start / 1000),
      type: event.event_type,
      title: event.book_title
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
                title="总事件数"
                value={stats.totalEvents}
                subtitle="记录的交互事件"
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
                title="图书点击数"
                value={stats.clickedBooks.length}
                subtitle="实际点击查看详情"
                color="purple"
              />
              <StatCard
                icon={Clock}
                title="会话时长"
                value={formatTime(stats.sessionDuration)}
                subtitle={`平均悬停 ${stats.avgHoverDuration}ms`}
                color="orange"
              />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Event Types Chart */}
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold mb-4">事件类型分布</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={eventTypeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({type, percent}) => `${type} (${(percent * 100).toFixed(0)}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {eventTypeData.map((entry, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Top Books Chart */}
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
                    <Bar dataKey="hovers" stackId="a" fill="#8884d8" name="悬停次数" />
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
            {/* Clicked Books */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">已点击图书列表</h3>
              <div className="space-y-4">
                {stats.clickedBooks.map((book, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{book.title}</h4>
                      <p className="text-sm text-gray-500">作者: {book.author}</p>
                      <p className="text-xs text-gray-400">ISBN: {book.isbn}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">
                        {new Date(book.timestamp).toLocaleTimeString('zh-CN')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

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
                        悬停次数
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        点击次数
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        总悬停时间 (ms)
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
                          {book.hovers}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {book.clicks}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {book.totalHoverTime}
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
            <h3 className="text-lg font-semibold mb-4">用户交互时间线</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  tickFormatter={(value: number) => `${Math.floor(value / 60)}:${(value % 60).toString().padStart(2, '0')}`}
                />
                <YAxis hide />
                <Tooltip 
                  labelFormatter={(value) => `时间: ${formatTime(value)}`}
                  formatter={(value: any, name: any, props: any) => [
                    props.payload.title, 
                    props.payload.type === 'book_clicked' ? '点击图书' : '开始悬停'
                  ]}
                />
                <Line 
                  type="monotone" 
                  dataKey="time" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
            
            {/* Timeline Events List */}
            <div className="mt-6 space-y-3 max-h-60 overflow-y-auto">
              {timelineData.map((event, index: number) => (
                <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                  <div className={`w-3 h-3 rounded-full ${
                    event.type === 'book_clicked' ? 'bg-green-500' : 'bg-blue-500'
                  }`}></div>
                  <div className="flex-1">
                    <span className="text-sm font-medium">
                      {event.type === 'book_clicked' ? '点击' : '悬停'}: {event.title}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      {formatTime(event.time)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InteractionDashboard;