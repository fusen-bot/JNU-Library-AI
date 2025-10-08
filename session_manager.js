/**
 * 全局Session ID管理器
 * 负责生成和管理用户会话ID，以及统一的交互事件记录
 */

(function() {
    'use strict';
    
    // 防止重复初始化
    if (window.JNULibrarySessionManager) {
        console.log('Session Manager already initialized');
        return;
    }
    
    /**
     * Session管理器类
     */
    class SessionManager {
        constructor() {
            this.sessionId = null;
            this.sessionStartTime = null;
            this.currentSearchSession = null; // 当前搜索会话信息
            this.searchTimeoutId = null; // 搜索会话超时ID
            this.bookInteractions = new Map(); // 书籍交互记录 Map<bookISBN, {展开次数, 停留时间等}>
            this.pendingEvents = []; // 待发送的事件队列
            
            this.init();
        }
        
        /**
         * 初始化Session管理器
         */
        init() {
            const isNewSession = this.restoreOrGenerateSessionId();
            this.setupEventListeners();
            this.setupHeartbeat();

            // 只有在新会话创建时，才记录 session_start 事件
            if (isNewSession) {
                this.logSessionStart();
            }
            
            console.log(`🎯 Session Manager初始化完成，Session ID: ${this.sessionId}`);
        }
        
        /**
         * 恢复或生成新的Session ID
         * @returns {boolean} - 如果是新生成的Session，返回true，否则返回false
         */
        restoreOrGenerateSessionId() {
            // 尝试从sessionStorage恢复
            const existingSessionId = sessionStorage.getItem('jnu_library_session_id');
            const existingSessionStart = sessionStorage.getItem('jnu_library_session_start');

            if (existingSessionId && existingSessionStart) {
                this.sessionId = existingSessionId;
                this.sessionStartTime = existingSessionStart;
                console.log(`🎯 恢复已有 Session: ${this.sessionId}`);
                return false; // 不是新会话
            }

            // 如果没有，则生成新的Session ID
            const today = new Date();
            const dateStr = today.getFullYear().toString() +
                           (today.getMonth() + 1).toString().padStart(2, '0') +
                           today.getDate().toString().padStart(2, '0');

            // 获取今日的Session序号
            const todaySessionKey = `jnu_sessions_${dateStr}`;
            let sessionCounter = parseInt(localStorage.getItem(todaySessionKey) || '0');
            sessionCounter += 1;

            // 保存新的序号
            localStorage.setItem(todaySessionKey, sessionCounter.toString());

            // 生成格式化的序号（01, 02, 03...）
            const formattedCounter = sessionCounter.toString().padStart(2, '0');

            // 生成最终的Session ID
            this.sessionId = `交互 ${formattedCounter}_${dateStr}`;
            this.sessionStartTime = new Date().toISOString();

            // 存储到sessionStorage中，以便页面刷新后恢复
            sessionStorage.setItem('jnu_library_session_id', this.sessionId);
            sessionStorage.setItem('jnu_library_session_start', this.sessionStartTime);

            console.log(`🎯 生成新的Session ID: ${this.sessionId} (今日第${sessionCounter}个Session)`);
            return true; // 是新会话
        }
        
        /**
         * 获取当前Session ID
         */
        getSessionId() {
            return this.sessionId;
        }
        
        /**
         * 记录交互事件的通用方法
         * @param {string} eventType - 事件类型 
         * @param {Object} eventData - 事件数据
         * @param {boolean} immediate - 是否立即发送（默认false，会加入队列批量发送）
         */
        recordEvent(eventType, eventData = {}, immediate = false) {
            const event = {
                session_id: this.sessionId,
                event_type: eventType,
                timestamp: new Date().toISOString(),
                timestamp_since_session_start: Date.now() - new Date(this.sessionStartTime).getTime(),
                ...eventData
            };
            
            console.log(`📝 记录事件: ${eventType}`, event);
            
            if (immediate) {
                this.sendEventToServer(event);
            } else {
                this.pendingEvents.push(event);
                // 防止事件积累过多，定期发送
                if (this.pendingEvents.length >= 5) {
                    this.flushPendingEvents();
                }
            }
        }
        
        /**
         * 开始单次检索书籍会话
         * @param {string} query - 搜索查询
         */
        startSearchSession(query) {
            // 如果有正在进行的搜索会话，先结束它
            if (this.currentSearchSession) {
                this.endSearchSession('new_search_started');
            }
            
            this.currentSearchSession = {
                search_id: `search_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
                query: query,
                start_time: new Date().toISOString(),
                start_timestamp: Date.now(),
                books_clicked: [],
                events: []
            };
            
            console.log(`🔍 开始搜索会话: ${query}`, this.currentSearchSession);
            
            // 记录搜索开始事件
            this.recordEvent('search_session_start', {
                search_id: this.currentSearchSession.search_id,
                query: query,
                query_length: query.length
            });
            
            // 设置10分钟超时，自动结束搜索会话
            this.searchTimeoutId = setTimeout(() => {
                this.endSearchSession('timeout');
            }, 10 * 60 * 1000); // 10分钟
        }
        
        /**
         * 结束单次检索书籍会话
         * @param {string} reason - 结束原因
         */
        endSearchSession(reason = 'completed') {
            if (!this.currentSearchSession) {
                return;
            }
            
            const duration = Date.now() - this.currentSearchSession.start_timestamp;
            
            console.log(`🏁 结束搜索会话: ${this.currentSearchSession.query}，原因: ${reason}，耗时: ${duration}ms`);
            
            // 记录搜索结束事件
            this.recordEvent('search_session_end', {
                search_id: this.currentSearchSession.search_id,
                query: this.currentSearchSession.query,
                duration_ms: duration,
                end_reason: reason,
                books_clicked_count: this.currentSearchSession.books_clicked.length,
                books_clicked: this.currentSearchSession.books_clicked,
                events_count: this.currentSearchSession.events.length
            }, true); // 立即发送
            
            // 清除超时定时器
            if (this.searchTimeoutId) {
                clearTimeout(this.searchTimeoutId);
                this.searchTimeoutId = null;
            }
            
            // 重置当前搜索会话
            this.currentSearchSession = null;
        }
        
        /**
         * 记录书籍点击事件
         * @param {Object} bookInfo - 书籍信息
         */
        recordBookClick(bookInfo) {
            const clickEvent = {
                book_title: bookInfo.title,
                book_author: bookInfo.author,
                book_isbn: bookInfo.isbn,
                click_timestamp: new Date().toISOString()
            };
            
            // 如果有当前搜索会话，添加到会话中
            if (this.currentSearchSession) {
                this.currentSearchSession.books_clicked.push(clickEvent);
                this.currentSearchSession.events.push({
                    type: 'book_clicked',
                    timestamp: new Date().toISOString(),
                    data: clickEvent
                });
            }
            
            // 记录独立的书籍点击事件
            this.recordEvent('book_clicked', {
                search_id: this.currentSearchSession?.search_id || null,
                ...clickEvent
            });
            
            // 更新书籍交互统计
            this.updateBookInteraction(bookInfo.isbn, 'click');
        }
        
        /**
         * 记录书籍悬停事件（用于计算停留时间）
         * @param {Object} bookInfo - 书籍信息
         * @param {string} action - 'hover_start' 或 'hover_end'
         */
        recordBookHover(bookInfo, action) {
            const isbn = bookInfo.isbn;
            
            if (action === 'hover_start') {
                // 记录悬停开始时间
                if (!this.bookInteractions.has(isbn)) {
                    this.bookInteractions.set(isbn, {
                        isbn: isbn,
                        title: bookInfo.title,
                        expand_count: 0,
                        total_hover_time: 0,
                        hover_start_time: null,
                        hover_sessions: []
                    });
                }
                
                const interaction = this.bookInteractions.get(isbn);
                interaction.hover_start_time = Date.now();
                interaction.expand_count += 1;
                
                this.recordEvent('book_hover_start', {
                    search_id: this.currentSearchSession?.search_id || null,
                    book_isbn: isbn,
                    book_title: bookInfo.title,
                    expand_count: interaction.expand_count
                });
                
            } else if (action === 'hover_end') {
                const interaction = this.bookInteractions.get(isbn);
                if (interaction && interaction.hover_start_time) {
                    const hoverDuration = Date.now() - interaction.hover_start_time;
                    interaction.total_hover_time += hoverDuration;
                    interaction.hover_sessions.push({
                        start: new Date(interaction.hover_start_time).toISOString(),
                        end: new Date().toISOString(),
                        duration_ms: hoverDuration
                    });
                    interaction.hover_start_time = null;
                    
                    this.recordEvent('book_hover_end', {
                        search_id: this.currentSearchSession?.search_id || null,
                        book_isbn: isbn,
                        book_title: bookInfo.title,
                        hover_duration_ms: hoverDuration,
                        total_hover_time_ms: interaction.total_hover_time,
                        total_expand_count: interaction.expand_count
                    });
                }
            }
        }
        
        /**
         * 更新书籍交互统计
         * @param {string} isbn - 书籍ISBN
         * @param {string} action - 交互类型
         */
        updateBookInteraction(isbn, action) {
            if (!this.bookInteractions.has(isbn)) {
                this.bookInteractions.set(isbn, {
                    isbn: isbn,
                    expand_count: 0,
                    total_hover_time: 0,
                    click_count: 0,
                    last_interaction: null
                });
            }
            
            const interaction = this.bookInteractions.get(isbn);
            
            if (action === 'click') {
                interaction.click_count += 1;
            }
            
            interaction.last_interaction = new Date().toISOString();
        }
        
        /**
         * 设置页面卸载时的清理逻辑
         */
        setupEventListeners() {
            // 页面卸载时发送session结束事件和剩余的事件
            window.addEventListener('beforeunload', () => {
                this.logSessionEnd('page_unload');
                this.flushPendingEvents();
            });
            
            // 页面可见性变化时的处理
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.recordEvent('page_hidden');
                    this.flushPendingEvents();
                } else {
                    this.recordEvent('page_visible');
                }
            });
        }
        
        /**
         * 设置心跳机制（每30秒发送一次）
         */
        setupHeartbeat() {
            setInterval(() => {
                this.recordEvent('heartbeat', {
                    active_search_session: this.currentSearchSession ? this.currentSearchSession.search_id : null,
                    pending_events_count: this.pendingEvents.length
                });
                
                // 定期发送待处理事件
                if (this.pendingEvents.length > 0) {
                    this.flushPendingEvents();
                }
            }, 30000); // 30秒
        }
        
        /**
         * 记录Session开始事件
         */
        logSessionStart() {
            this.recordEvent('session_start', {
                user_agent: navigator.userAgent,
                page_url: window.location.href,
                screen_resolution: `${screen.width}x${screen.height}`,
                viewport_size: `${window.innerWidth}x${window.innerHeight}`,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            }, true); // 立即发送
        }
        
        /**
         * 记录Session结束事件
         * @param {string} reason - 结束原因
         */
        logSessionEnd(reason = 'normal') {
            const sessionDuration = Date.now() - new Date(this.sessionStartTime).getTime();
            
            // 如果有进行中的搜索会话，先结束它
            if (this.currentSearchSession) {
                this.endSearchSession('session_end');
            }
            
            this.recordEvent('session_end', {
                session_duration_ms: sessionDuration,
                end_reason: reason,
                total_events_recorded: this.pendingEvents.length,
                book_interactions_count: this.bookInteractions.size,
                book_interactions_summary: Array.from(this.bookInteractions.values()).map(interaction => ({
                    isbn: interaction.isbn,
                    title: interaction.title,
                    expand_count: interaction.expand_count,
                    total_hover_time: interaction.total_hover_time,
                    click_count: interaction.click_count || 0
                }))
            }, true); // 立即发送
        }
        
        /**
         * 批量发送待处理的事件到服务器
         */
        async flushPendingEvents() {
            if (this.pendingEvents.length === 0) {
                return;
            }
            
            const eventsToSend = [...this.pendingEvents];
            this.pendingEvents = [];
            
            try {
                await this.sendEventsToServer(eventsToSend);
                console.log(`📤 成功发送 ${eventsToSend.length} 个事件到服务器`);
            } catch (error) {
                console.error('❌ 发送事件到服务器失败:', error);
                // 将失败的事件重新加入队列
                this.pendingEvents.unshift(...eventsToSend);
            }
        }
        
        /**
         * 发送单个事件到服务器
         * @param {Object} event - 事件对象
         */
        async sendEventToServer(event) {
            return this.sendEventsToServer([event]);
        }
        
        /**
         * 发送事件数组到服务器
         * @param {Array} events - 事件数组
         */
        async sendEventsToServer(events) {
            try {
                const response = await fetch('http://localhost:5001/api/interaction_events', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        events: events,
                        timestamp: new Date().toISOString()
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                console.log('🎯 服务器响应:', result);
                
                return result;
            } catch (error) {
                console.error('❌ 发送事件到服务器时发生错误:', error);
                throw error;
            }
        }
        
        /**
         * 获取当前会话的统计信息
         */
        getSessionStats() {
            return {
                session_id: this.sessionId,
                session_start_time: this.sessionStartTime,
                session_duration_ms: Date.now() - new Date(this.sessionStartTime).getTime(),
                current_search_session: this.currentSearchSession,
                pending_events_count: this.pendingEvents.length,
                book_interactions_count: this.bookInteractions.size,
                book_interactions: Array.from(this.bookInteractions.values())
            };
        }
    }
    
    // 创建全局Session管理器实例
    window.JNULibrarySessionManager = new SessionManager();
    
    // 暴露一些常用的方法到全局
    window.recordInteractionEvent = (eventType, eventData, immediate) => {
        window.JNULibrarySessionManager.recordEvent(eventType, eventData, immediate);
    };
    
    window.startSearchSession = (query) => {
        window.JNULibrarySessionManager.startSearchSession(query);
    };
    
    window.endSearchSession = (reason) => {
        window.JNULibrarySessionManager.endSearchSession(reason);
    };
    
    window.recordBookClick = (bookInfo) => {
        window.JNULibrarySessionManager.recordBookClick(bookInfo);
    };
    
    window.recordBookHover = (bookInfo, action) => {
        window.JNULibrarySessionManager.recordBookHover(bookInfo, action);
    };
    
    window.getSessionStats = () => {
        return window.JNULibrarySessionManager.getSessionStats();
    };
    
    console.log('🎯 JNU Library Session Manager 已成功加载');
})();
