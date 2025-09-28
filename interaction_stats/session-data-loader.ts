/**
 * 会话数据加载器
 * 负责加载和解析interaction_stats/sessions目录下的JSONL文件
 */

export interface SessionEvent {
  session_id: string;
  event_type: string;
  timestamp: string;
  timestamp_since_session_start: number;
  book_isbn?: string;
  book_title?: string;
  book_author?: string;
  hover_duration_ms?: number;
  total_hover_time_ms?: number;
  total_expand_count?: number;
  expand_count?: number;
  click_timestamp?: string;
  search_id?: string;
  user_agent?: string;
  page_url?: string;
  screen_resolution?: string;
  viewport_size?: string;
  timezone?: string;
  server_received_timestamp?: string;
  saved_timestamp?: string;
  session_duration_ms?: number;
  end_reason?: string;
  total_events_recorded?: number;
  book_interactions_count?: number;
  book_interactions_summary?: Array<{
    isbn: string;
    expand_count: number;
    total_hover_time: number;
    click_count: number;
  }>;
  active_search_session?: any;
  pending_events_count?: number;
}

export interface SessionInfo {
  sessionId: string;
  fileName: string;
  startTime?: string;
  endTime?: string;
  eventCount: number;
  duration?: number;
  bookInteractionCount: number;
}

export interface BookInteraction {
  isbn: string;
  title: string;
  author?: string;
  hovers: number;
  clicks: number;
  totalHoverTime: number;
  expandCount: number;
}

export interface SessionAnalysis {
  sessionInfo: SessionInfo;
  events: SessionEvent[];
  bookInteractions: Map<string, BookInteraction>;
  eventTypes: Map<string, number>;
  timeline: Array<{
    time: number;
    type: string;
    title?: string;
    description: string;
  }>;
  hoverDurations: number[];
  clickedBooks: Array<{
    title: string;
    author?: string;
    isbn: string;
    timestamp: string;
  }>;
  stats: {
    totalEvents: number;
    uniqueBooks: number;
    totalClicks: number;
    totalHovers: number;
    sessionDuration: number;
    avgHoverDuration: number;
  };
}

export class SessionDataLoader {
  private sessions: Map<string, SessionAnalysis> = new Map();
  
  /**
   * 从JSONL文件内容解析会话数据
   */
  parseSessionFromText(fileName: string, content: string): SessionAnalysis {
    const lines = content.split('\n').filter(line => line.trim());
    const events: SessionEvent[] = [];
    
    for (const line of lines) {
      try {
        const event = JSON.parse(line) as SessionEvent;
        events.push(event);
      } catch (error) {
        console.warn(`解析事件失败: ${line}`, error);
      }
    }
    
    return this.analyzeSession(fileName, events);
  }
  
  /**
   * 分析单个会话的事件数据
   */
  private analyzeSession(fileName: string, events: SessionEvent[]): SessionAnalysis {
    const bookInteractions = new Map<string, BookInteraction>();
    const eventTypes = new Map<string, number>();
    const timeline: Array<{time: number; type: string; title?: string; description: string}> = [];
    const hoverDurations: number[] = [];
    const clickedBooks: Array<{title: string; author?: string; isbn: string; timestamp: string}> = [];
    
    let sessionStart: string | undefined;
    let sessionEnd: string | undefined;
    let sessionId = '';
    
    // 处理每个事件
    events.forEach(event => {
      // 记录会话ID
      if (!sessionId && event.session_id) {
        sessionId = event.session_id;
      }
      
      // 统计事件类型
      const eventType = event.event_type;
      eventTypes.set(eventType, (eventTypes.get(eventType) || 0) + 1);
      
      // 记录会话开始和结束时间
      if (eventType === 'session_start') {
        sessionStart = event.timestamp;
      } else if (eventType === 'session_end') {
        sessionEnd = event.timestamp;
      }
      
      // 处理图书交互事件
      if (event.book_isbn && event.book_title) {
        const isbn = event.book_isbn;
        
        if (!bookInteractions.has(isbn)) {
          bookInteractions.set(isbn, {
            isbn,
            title: event.book_title,
            author: event.book_author,
            hovers: 0,
            clicks: 0,
            totalHoverTime: 0,
            expandCount: 0
          });
        }
        
        const bookData = bookInteractions.get(isbn)!;
        
        switch (eventType) {
          case 'book_hover_start':
            bookData.hovers++;
            if (event.expand_count) {
              bookData.expandCount = Math.max(bookData.expandCount, event.expand_count);
            }
            break;
            
          case 'book_hover_end':
            if (event.hover_duration_ms) {
              bookData.totalHoverTime += event.hover_duration_ms;
              hoverDurations.push(event.hover_duration_ms);
            }
            break;
            
          case 'book_clicked':
            bookData.clicks++;
            clickedBooks.push({
              title: event.book_title,
              author: event.book_author,
              isbn: event.book_isbn,
              timestamp: event.timestamp
            });
            break;
        }
      }
      
      // 构建时间线
      const timeInSeconds = Math.round(event.timestamp_since_session_start / 1000);
      let description = '';
      
      switch (eventType) {
        case 'session_start':
          description = '会话开始';
          break;
        case 'session_end':
          description = `会话结束 (${event.end_reason || '未知原因'})`;
          break;
        case 'book_hover_start':
          description = `开始悬停: ${event.book_title}`;
          break;
        case 'book_hover_end':
          description = `结束悬停: ${event.book_title} (${event.hover_duration_ms}ms)`;
          break;
        case 'book_clicked':
          description = `点击图书: ${event.book_title}`;
          break;
        case 'page_hidden':
          description = '页面隐藏';
          break;
        case 'page_visible':
          description = '页面可见';
          break;
        case 'heartbeat':
          description = '心跳检测';
          break;
        default:
          description = eventType;
      }
      
      timeline.push({
        time: timeInSeconds,
        type: eventType,
        title: event.book_title,
        description
      });
    });
    
    // 计算会话统计信息
    const sessionDuration = events.length > 0 
      ? Math.max(...events.map(e => e.timestamp_since_session_start)) / 1000 
      : 0;
    
    const avgHoverDuration = hoverDurations.length > 0
      ? Math.round(hoverDurations.reduce((a, b) => a + b, 0) / hoverDurations.length)
      : 0;
    
    const sessionInfo: SessionInfo = {
      sessionId: sessionId || fileName.replace('.jsonl', ''),
      fileName,
      startTime: sessionStart,
      endTime: sessionEnd,
      eventCount: events.length,
      duration: sessionDuration,
      bookInteractionCount: bookInteractions.size
    };
    
    const stats = {
      totalEvents: events.length,
      uniqueBooks: bookInteractions.size,
      totalClicks: clickedBooks.length,
      totalHovers: Array.from(bookInteractions.values()).reduce((sum, book) => sum + book.hovers, 0),
      sessionDuration,
      avgHoverDuration
    };
    
    return {
      sessionInfo,
      events,
      bookInteractions,
      eventTypes,
      timeline,
      hoverDurations,
      clickedBooks,
      stats
    };
  }
  
  /**
   * 添加会话分析数据
   */
  addSession(analysis: SessionAnalysis): void {
    this.sessions.set(analysis.sessionInfo.sessionId, analysis);
  }
  
  /**
   * 获取所有会话信息
   */
  getAllSessions(): SessionInfo[] {
    return Array.from(this.sessions.values()).map(analysis => analysis.sessionInfo);
  }
  
  /**
   * 获取特定会话的分析数据
   */
  getSessionAnalysis(sessionId: string): SessionAnalysis | undefined {
    return this.sessions.get(sessionId);
  }
  
  /**
   * 清空所有会话数据
   */
  clear(): void {
    this.sessions.clear();
  }
  
  /**
   * 获取多会话汇总统计
   */
  getCombinedStats(): {
    totalSessions: number;
    totalEvents: number;
    totalBooks: number;
    totalClicks: number;
    totalHovers: number;
    avgSessionDuration: number;
    avgHoverDuration: number;
    topBooks: Array<{title: string; interactions: number; clicks: number; hovers: number}>;
  } {
    const allAnalyses = Array.from(this.sessions.values());
    
    if (allAnalyses.length === 0) {
      return {
        totalSessions: 0,
        totalEvents: 0,
        totalBooks: 0,
        totalClicks: 0,
        totalHovers: 0,
        avgSessionDuration: 0,
        avgHoverDuration: 0,
        topBooks: []
      };
    }
    
    const combinedBooks = new Map<string, {title: string; interactions: number; clicks: number; hovers: number}>();
    let totalEvents = 0;
    let totalClicks = 0;
    let totalHovers = 0;
    let totalDuration = 0;
    let totalHoverDurations: number[] = [];
    
    allAnalyses.forEach(analysis => {
      totalEvents += analysis.stats.totalEvents;
      totalClicks += analysis.stats.totalClicks;
      totalHovers += analysis.stats.totalHovers;
      totalDuration += analysis.stats.sessionDuration;
      totalHoverDurations.push(...analysis.hoverDurations);
      
      analysis.bookInteractions.forEach(book => {
        const key = book.isbn;
        if (!combinedBooks.has(key)) {
          combinedBooks.set(key, {
            title: book.title,
            interactions: 0,
            clicks: 0,
            hovers: 0
          });
        }
        const combined = combinedBooks.get(key)!;
        combined.clicks += book.clicks;
        combined.hovers += book.hovers;
        combined.interactions = combined.clicks + combined.hovers;
      });
    });
    
    const topBooks = Array.from(combinedBooks.values())
      .sort((a, b) => b.interactions - a.interactions)
      .slice(0, 10);
    
    const avgHoverDuration = totalHoverDurations.length > 0
      ? Math.round(totalHoverDurations.reduce((a, b) => a + b, 0) / totalHoverDurations.length)
      : 0;
    
    return {
      totalSessions: allAnalyses.length,
      totalEvents,
      totalBooks: combinedBooks.size,
      totalClicks,
      totalHovers,
      avgSessionDuration: totalDuration / allAnalyses.length,
      avgHoverDuration,
      topBooks
    };
  }
}

// 创建全局实例
export const sessionDataLoader = new SessionDataLoader();
