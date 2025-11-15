/**
 * 会话数据加载器（新版本）
 * 负责加载和解析 interaction_stats/sessions 目录下的聚合检索JSONL文件
 * 一行对应一次检索请求（QueryLogRecord）
 */

export interface BookLogEntry {
  title: string;
  author?: string;
  isbn?: string;
  logical_reason?: unknown;
  social_reason?: unknown;
  hover_count: number;
  total_hover_time_ms: number;
  click_count: number;
  rating?: number | null;
}

export interface QueryLogRecord {
  session_id: string;
  timestamp: string;
  query_text: string;
  books: BookLogEntry[];
  saved_timestamp?: string;
}

export interface SessionInfo {
  sessionId: string;
  fileName: string;
  queryCount: number;
  uniqueBooks: number;
}

export interface BookInteraction {
  isbn: string;
  title: string;
  author?: string;
  hoverCount: number;
  totalHoverTimeMs: number;
  clickCount: number;
}

export interface SessionAnalysis {
  sessionInfo: SessionInfo;
  records: QueryLogRecord[];
  bookInteractions: Map<string, BookInteraction>;
  stats: {
    totalQueries: number;
    uniqueBooks: number;
    totalHoverCount: number;
    totalHoverTimeMs: number;
    totalClicks: number;
  };
}

export class SessionDataLoader {
  private sessions: Map<string, SessionAnalysis> = new Map();
  
  /**
   * 从JSONL文件内容解析聚合检索数据
   */
  parseSessionFromText(fileName: string, content: string): SessionAnalysis {
    const lines = content.split('\n').filter(line => line.trim());
    const records: QueryLogRecord[] = [];
    
    for (const line of lines) {
      try {
        const record = JSON.parse(line) as QueryLogRecord;
        if (record && record.session_id && record.query_text && Array.isArray(record.books)) {
          records.push(record);
        }
      } catch (error) {
        console.warn(`解析聚合检索记录失败: ${line}`, error);
      }
    }
    
    return this.analyzeSession(fileName, records);
  }
  
  /**
   * 基于聚合检索记录分析单个文件
   */
  private analyzeSession(fileName: string, records: QueryLogRecord[]): SessionAnalysis {
    const bookInteractions = new Map<string, BookInteraction>();
    
    let sessionId = '';
    let totalHoverCount = 0;
    let totalHoverTimeMs = 0;
    let totalClicks = 0;
    
    records.forEach(record => {
      if (!sessionId && record.session_id) {
        sessionId = record.session_id;
      }
      
      record.books.forEach(book => {
        const isbn = book.isbn || book.title;
        if (!isbn) {
          return;
        }
        
        if (!bookInteractions.has(isbn)) {
          bookInteractions.set(isbn, {
            isbn,
            title: book.title,
            author: book.author,
            hoverCount: 0,
            totalHoverTimeMs: 0,
            clickCount: 0
          });
        }
        
        const interaction = bookInteractions.get(isbn)!;
        interaction.hoverCount += book.hover_count || 0;
        interaction.totalHoverTimeMs += book.total_hover_time_ms || 0;
        interaction.clickCount += book.click_count || 0;
        
        totalHoverCount += book.hover_count || 0;
        totalHoverTimeMs += book.total_hover_time_ms || 0;
        totalClicks += book.click_count || 0;
      });
    });
    
    const sessionInfo: SessionInfo = {
      sessionId: sessionId || fileName.replace('.jsonl', ''),
      fileName,
      queryCount: records.length,
      uniqueBooks: bookInteractions.size
    };
    
    const stats = {
      totalQueries: records.length,
      uniqueBooks: bookInteractions.size,
      totalHoverCount,
      totalHoverTimeMs,
      totalClicks
    };
    
    return {
      sessionInfo,
      records,
      bookInteractions,
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
    totalQueries: number;
    totalBooks: number;
    totalClicks: number;
    totalHovers: number;
    totalHoverTimeMs: number;
    topBooks: Array<{title: string; interactions: number; clicks: number; hovers: number; hoverTimeMs: number}>;
  } {
    const allAnalyses = Array.from(this.sessions.values());
    
    if (allAnalyses.length === 0) {
      return {
        totalSessions: 0,
        totalQueries: 0,
        totalBooks: 0,
        totalClicks: 0,
        totalHovers: 0,
        totalHoverTimeMs: 0,
        topBooks: []
      };
    }
    
    const combinedBooks = new Map<string, {title: string; interactions: number; clicks: number; hovers: number; hoverTimeMs: number}>();
    let totalQueries = 0;
    let totalClicks = 0;
    let totalHovers = 0;
    let totalHoverTimeMs = 0;
    
    allAnalyses.forEach(analysis => {
      totalQueries += analysis.stats.totalQueries;
      totalClicks += analysis.stats.totalClicks;
      totalHovers += analysis.stats.totalHoverCount;
      totalHoverTimeMs += analysis.stats.totalHoverTimeMs;
      
      analysis.bookInteractions.forEach(book => {
        const key = book.isbn;
        if (!combinedBooks.has(key)) {
          combinedBooks.set(key, {
            title: book.title,
            interactions: 0,
            clicks: 0,
            hovers: 0,
            hoverTimeMs: 0
          });
        }
        const combined = combinedBooks.get(key)!;
        combined.clicks += book.clickCount;
        combined.hovers += book.hoverCount;
        combined.hoverTimeMs += book.totalHoverTimeMs;
        combined.interactions = combined.clicks + combined.hovers;
      });
    });
    
    const topBooks = Array.from(combinedBooks.values())
      .sort((a, b) => b.interactions - a.interactions)
      .slice(0, 10);
    return {
      totalSessions: allAnalyses.length,
      totalQueries,
      totalBooks: combinedBooks.size,
      totalClicks,
      totalHovers,
      totalHoverTimeMs,
      topBooks
    };
  }
}

// 创建全局实例
export const sessionDataLoader = new SessionDataLoader();
