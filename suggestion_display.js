// 创建一个建议框元素
function createSuggestionBox() {
    const suggestionBox = document.createElement('div');
    suggestionBox.id = 'ai-suggestion-box';
    suggestionBox.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 320px;
        max-height: 80vh; 
        overflow-y: auto;
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-family: Arial, sans-serif;
        z-index: 10000;
        display: none;
    `;
    
    // 添加标题
    const title = document.createElement('div');
    title.style.cssText = `
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 12px;
        color: #333;
        display: flex;
        justify-content: space-between;
        position: sticky;
        top: 0;
        background-color: #f8f9fa;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
    `;
    
    // 添加内容区域
    const content = document.createElement('div');
    content.id = 'suggestion-content';
    content.style.cssText = `
        font-size: 13px;
        line-height: 1.5;
        color: #555;
        margin-top: 10px;
    `;
    
    suggestionBox.appendChild(title);
    suggestionBox.appendChild(content);
    document.body.appendChild(suggestionBox);
    

    
    return suggestionBox;
}

// 显示建议
function showSuggestion(suggestion) {
    let suggestionBox = document.getElementById('ai-suggestion-box');
    if (!suggestionBox) {
        suggestionBox = createSuggestionBox();
    }
    
    const contentElement = document.getElementById('suggestion-content');
    contentElement.innerHTML = ''; // 清空内容
    
    console.log("处理建议内容:", suggestion); // 调试日志
    

    // 解析内容，分割书籍和问题部分
    let booksPart = '';
    let questionsPart = '';
    
    // 更严格的格式检查，支持多种格式
    // 1. 尝试匹配"书籍："和"问题："分隔的标准格式
    const standardFormat = /书籍[:：](.+?)问题[:：](.+?)$/is;
    const standardMatch = suggestion.match(standardFormat);
    
    if (standardMatch && standardMatch.length >= 3) {
        booksPart = standardMatch[1].trim();
        questionsPart = standardMatch[2].trim();
    } else {
        // 2. 尝试分别匹配书籍和问题部分
        const booksMatch = suggestion.match(/书籍[:：](.+?)(?=问题[:：]|$)/is);
        const questionsMatch = suggestion.match(/问题[:：](.+?)$/is);
        
        if (booksMatch && booksMatch[1]) {
            booksPart = booksMatch[1].trim();
        }
        
        if (questionsMatch && questionsMatch[1]) {
            questionsPart = questionsMatch[1].trim();
        }
    }
    
    console.log("解析结果 - 书籍部分:", booksPart);
    console.log("解析结果 - 问题部分:", questionsPart);
    
    // 如果无法识别格式，则原样显示
    if (!booksPart && !questionsPart) {
        const defaultContainer = document.createElement('div');
        defaultContainer.style.marginBottom = '8px';
        defaultContainer.style.padding = '8px';
        defaultContainer.style.backgroundColor = '#f8f9fa';
        defaultContainer.style.borderRadius = '4px';
        defaultContainer.style.cursor = 'text';
        defaultContainer.textContent = suggestion;
        contentElement.appendChild(defaultContainer);
        suggestionBox.style.display = 'block';
        return;
    }
    
    // 创建书籍部分
    if (booksPart) {
        // 创建标题
        const booksTitle = document.createElement('div');
        booksTitle.style.fontWeight = 'bold';
        booksTitle.style.marginBottom = '6px';
        booksTitle.style.fontSize = '13px';
        booksTitle.style.color = '#333';
        booksTitle.textContent = '推荐书籍';
        contentElement.appendChild(booksTitle);
        
        // 创建书籍内容容器
        const booksContainer = document.createElement('div');
        booksContainer.style.marginBottom = '15px'; // 增加间距
        booksContainer.style.padding = '0';
        booksContainer.style.display = 'flex';
        booksContainer.style.flexWrap = 'wrap';
        booksContainer.style.gap = '8px';
        
        // 尝试分割多本书
        const books = booksPart.match(/《[^《》]+》/g) || [booksPart];
        
        // 限制最多显示3本书
        const maxBooks = Math.min(books.length, 3);
        
        for (let i = 0; i < maxBooks; i++) {
            const book = books[i];
            // 创建独立的书籍项容器
            const bookItem = document.createElement('div');
            bookItem.style.flex = '1';
            bookItem.style.minWidth = '30%';
            bookItem.style.backgroundColor = '#e8f4f2';
            bookItem.style.borderRadius = '4px';
            bookItem.style.padding = '8px';
            bookItem.style.cursor = 'pointer';
            bookItem.style.color = '#2a6a5c';
            bookItem.style.border = '1px solid #d0e6e2';
            bookItem.style.transition = 'all 0.2s ease';
            bookItem.setAttribute('data-item-type', 'book');
            bookItem.setAttribute('data-item-index', i.toString());
            
            // 添加悬停效果
            bookItem.addEventListener('mouseover', function() {
                this.style.backgroundColor = '#d4ebe7';
                this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            });
            
            bookItem.addEventListener('mouseout', function() {
                this.style.backgroundColor = '#e8f4f2';
                this.style.boxShadow = 'none';
            });
            
            // 内容布局
            const bookContent = document.createElement('div');
            bookContent.style.display = 'flex';
            bookContent.style.alignItems = 'center';
            
            // 添加序号圆圈
            const bookIndex = document.createElement('span');
            bookIndex.style.minWidth = '18px';
            bookIndex.style.height = '18px';
            bookIndex.style.backgroundColor = '#05a081';
            bookIndex.style.color = '#fff';
            bookIndex.style.borderRadius = '50%';
            bookIndex.style.fontSize = '10px';
            bookIndex.style.display = 'flex';
            bookIndex.style.alignItems = 'center';
            bookIndex.style.justifyContent = 'center';
            bookIndex.style.marginRight = '8px';
            bookIndex.style.flexShrink = '0';
            bookIndex.textContent = (i + 1).toString();
            
            // 添加文本
            const bookText = document.createElement('span');
            bookText.style.overflow = 'hidden';
            bookText.style.textOverflow = 'ellipsis';
            bookText.style.wordBreak = 'break-word'; // 允许在任何字符间断行
            bookText.textContent = book.trim();
            
            bookContent.appendChild(bookIndex);
            bookContent.appendChild(bookText);
            bookItem.appendChild(bookContent);
            booksContainer.appendChild(bookItem);
        }
        
        contentElement.appendChild(booksContainer);
    }
    
    // 创建问题部分
    if (questionsPart) {
        // 创建标题
        const questionsTitle = document.createElement('div');
        questionsTitle.style.fontWeight = 'bold';
        questionsTitle.style.marginBottom = '6px';
        questionsTitle.style.fontSize = '13px';
        questionsTitle.style.color = '#333';
        questionsTitle.textContent = '热门话题';
        contentElement.appendChild(questionsTitle);
        
        // 创建问题内容容器
        const questionsContainer = document.createElement('div');
        questionsContainer.style.display = 'flex';
        questionsContainer.style.flexDirection = 'column';
        questionsContainer.style.gap = '8px';
        
        // 处理问题部分
        let questions = [];
        if (questionsPart.includes('？') || questionsPart.includes('?')) {
            // 尝试分割多个问题 (按问号分割)
            questions = questionsPart.split(/[？?]/).filter(q => q.trim());
        } else {
            // 如果没有问号，则将整个文本作为一个问题
            questions = [questionsPart];
        }
        
        // 限制最多显示2个问题
        const maxQuestions = Math.min(questions.length, 2);
        
        for (let i = 0; i < maxQuestions; i++) {
            if (!questions[i].trim()) continue;
            
            // 创建独立的问题项容器
            const questionItem = document.createElement('div');
            questionItem.style.backgroundColor = '#f0f2f7';
            questionItem.style.borderRadius = '4px';
            questionItem.style.padding = '8px';
            questionItem.style.cursor = 'pointer';
            questionItem.style.color = '#3a5ca8';
            questionItem.style.border = '1px solid #dce1ec';
            questionItem.style.transition = 'all 0.2s ease';
            questionItem.setAttribute('data-item-type', 'question');
            questionItem.setAttribute('data-item-index', i.toString());
            
            // 添加悬停效果
            questionItem.addEventListener('mouseover', function() {
                this.style.backgroundColor = '#e4e8f3';
                this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            });
            
            questionItem.addEventListener('mouseout', function() {
                this.style.backgroundColor = '#f0f2f7';
                this.style.boxShadow = 'none';
            });
            
            // 内容布局
            const questionContent = document.createElement('div');
            questionContent.style.display = 'flex';
            questionContent.style.alignItems = 'center';
            
            // 添加序号圆圈
            const questionIndex = document.createElement('span');
            questionIndex.style.minWidth = '18px';
            questionIndex.style.height = '18px';
            questionIndex.style.backgroundColor = '#4671d5';
            questionIndex.style.color = '#fff';
            questionIndex.style.borderRadius = '50%';
            questionIndex.style.fontSize = '10px';
            questionIndex.style.display = 'flex';
            questionIndex.style.alignItems = 'center';
            questionIndex.style.justifyContent = 'center';
            questionIndex.style.marginRight = '8px';
            questionIndex.style.flexShrink = '0';
            questionIndex.textContent = (i + 1).toString();
            
            // 添加文本
            const questionText = document.createElement('span');
            questionText.style.overflow = 'hidden';
            questionText.style.textOverflow = 'ellipsis';
            questionText.style.wordBreak = 'break-word'; // 允许在任何字符间断行
            
            // 只有在不是原始文本结尾处的问题才添加问号
            if (i < questions.length - 1 || questionsPart.endsWith('？') || questionsPart.endsWith('?')) {
                questionText.textContent = questions[i].trim() + '？';
            } else {
                questionText.textContent = questions[i].trim();
            }
            
            questionContent.appendChild(questionIndex);
            questionContent.appendChild(questionText);
            questionItem.appendChild(questionContent);
            questionsContainer.appendChild(questionItem);
        }
        
        contentElement.appendChild(questionsContainer);
    }
    
    suggestionBox.style.display = 'block';
    

}



(function() {
    // 保证脚本只初始化一次的标志
    if (window.__inputMonitorInitialized) return;
    window.__inputMonitorInitialized = true;
    
    // 添加请求状态追踪变量及加载定时器句柄
    window.__suggestionsInFlight = false;
    window.__lastSuggestionsContent = '';
    window.__loadingTimer = null;
    
    // 🔧 添加书籍点击状态追踪，防止循环触发
    window.__isBookClickTriggered = false;
    window.__bookClickTimeout = null;
    
    // 🔧 添加请求去重机制：记录最近的请求和匹配结果
    window.__lastRequestCache = {
        query_normalized: '',
        books_signature: '',
        timestamp: 0,
        task_id: ''
    };
    
    console.log('🚀 初始化输入监控系统 - 集成新版推荐理由UI');
    
    // ================================
    // 辅助函数：去重逻辑
    // ================================
    
    /**
     * 规范化查询字符串，用于去重判断
     * - 去除首尾空格
     * - 转换为小写
     * - 去除特殊标点符号（保留中文和英文字符）
     */
    function normalizeQuery(query) {
        // 去除首尾空格并转小写
        let normalized = query.trim().toLowerCase();
        // 去除特殊标点符号，只保留中文、英文、数字和空格
        normalized = normalized.replace(/[^\w\s\u4e00-\u9fff]/g, '');
        // 压缩多个空格为一个
        normalized = normalized.replace(/\s+/g, ' ');
        return normalized;
    }
    
    /**
     * 生成书籍列表的唯一签名，用于判断匹配结果是否相同
     * 基于书籍的ISBN列表（有序）
     */
    function getBooksSignature(books) {
        if (!books || books.length === 0) {
            return 'empty';
        }
        const isbnList = books.map(book => book.isbn || '').sort();
        return isbnList.join(',');
    }
    
    /**
     * 检查是否为重复请求
     * @param {string} inputValue - 用户输入的查询
     * @returns {boolean} - 如果是重复请求返回true
     */
    function isDuplicateRequest(inputValue) {
        const normalized = normalizeQuery(inputValue);
        const currentTime = Date.now();
        const cache = window.__lastRequestCache || { query_normalized: '', timestamp: 0 };
        const timeDiff = currentTime - cache.timestamp;

        // 10秒内，相同或互为前缀的规范化查询，视为重复
        if (timeDiff < 10000) {
            const prev = cache.query_normalized || '';
            const similar =
                normalized === prev ||
                (normalized && prev && (normalized.startsWith(prev) || prev.startsWith(normalized)));
            if (similar) {
                console.log(`⚠️ 检测到相似重复请求（${(timeDiff/1000).toFixed(2)}秒内）: ${normalized} ~ ${prev}`);
                return true;
            }
        }

        return false;
    }
    
    // ================================
    // 监控和显示逻辑
    // ================================
    
    const targetSelector = '.ant-select-search__field';
    let lastRequestTime = 0;
    const REQUEST_DELAY = 2000; 
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000; 
    
    // 创建显示区域
    function createDisplayArea() {
        // 先检查是否已存在
        let displayDiv = document.getElementById('suggestion-display');
        if (displayDiv) return displayDiv;
        
        const inputElement = document.querySelector(targetSelector);
        if (!inputElement) return null;
        
        const parent = inputElement.parentElement;
        displayDiv = document.createElement('div');
        displayDiv.id = 'suggestion-display';
        displayDiv.style.cssText = `
            position: absolute;
            left: 0;
            top: 100%;
            width: 100%;
            background-color: #fff;
            padding: 12px 15px;
            border-radius: 4px;
            border: 1px solid #05a081;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 9999;
            font-size: 14px;
            max-height: 500px;
            min-height: 50px;
            overflow-y: auto;
            margin-top: 4px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.15s ease;
            display: none;
            line-height: 1.6;
            color: #333;
            user-select: text;
            -webkit-user-select: text;
        `;
        parent.style.position = 'relative'; // 保证绝对定位基于输入框父元素
        parent.appendChild(displayDiv);
        return displayDiv;
    }
    
    // ===========================================
    // iOS风格加载动画
    // ===========================================
    
    // 显示优雅的加载动画
    function showLoadingAnimation(container) {
        if (!container) return;
        
        container.innerHTML = '';
        
        // 创建加载动画容器 - 紧凑高度，与书籍展示一致
        const loadingContainer = document.createElement('div');
        loadingContainer.className = 'suggestion-loading';
        loadingContainer.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px 20px;
            min-height: 60px;
            gap: 12px;
        `;
        
        // 创建三个脉动点
        const dotsContainer = document.createElement('div');
        dotsContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
        `;
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.style.cssText = `
                width: 8px;
                height: 8px;
                background: #05a081;
                border-radius: 50%;
                animation: pulse 1.4s ease-in-out ${i * 0.2}s infinite;
            `;
            dotsContainer.appendChild(dot);
        }
        
        // 加载文本
        const loadingText = document.createElement('div');
        loadingText.style.cssText = `
            font-size: 13px;
            color: #666;
            font-weight: 400;
        `;
        loadingText.textContent = '正在为你推荐';
        
        loadingContainer.appendChild(dotsContainer);
        loadingContainer.appendChild(loadingText);
        container.appendChild(loadingContainer);
        
        // 确保动画CSS已注入
        if (!document.getElementById('loading-animation-style')) {
            const style = document.createElement('style');
            style.id = 'loading-animation-style';
            style.textContent = `
                @keyframes pulse {
                    0%, 100% {
                        transform: scale(0.8);
                        opacity: 0.5;
                    }
                    50% {
                        transform: scale(1.2);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // ===========================================
    // 异步任务轮询管理
    // ===========================================
    let currentPollingTaskId = null;
    let pollingInterval = null;
    
    function startTaskPolling(taskId) {
        console.log(`🔄 开始轮询任务状态: ${taskId}`);
        currentPollingTaskId = taskId;
        
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }
        
        pollTaskStatus(taskId);
        
        pollingInterval = setInterval(() => {
            pollTaskStatus(taskId);
        }, 250);  // 从500ms改为250ms，更实时
    }
    
    function stopTaskPolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
        currentPollingTaskId = null;
        console.log('⏹️ 停止任务轮询');
    }
    
    async function pollTaskStatus(taskId) {
        try {
            const response = await fetch(`http://localhost:5001/api/task_status/${taskId}`);
            if (!response.ok) {
                console.error(`轮询失败: ${response.status}`);
                stopTaskPolling();
                return;
            }
            
            const taskData = await response.json();
            console.log(`📊 任务 ${taskId} 状态:`, taskData.status, '-', taskData.progress);
            
            // 🔧 新增：处理processing状态的渐进式更新
            if (taskData.status === 'processing' && taskData.completed_books) {
                console.log(`🔄 渐进式更新: ${taskData.completed_books.length}/${taskData.total_books} 本书已完成`);
                updateBooksProgressively(taskData.completed_books);
            } else if (taskData.status === 'completed') {
                console.log('✅ 任务完成，所有书籍推荐理由生成成功');
                stopTaskPolling();
                updateDisplayWithCompletedReasons(taskData);
            } else if (taskData.status === 'partial_failure') {
                console.warn('⚠️ 任务部分失败:', taskData.failed_books);
                console.warn('警告信息:', taskData.warning);
                stopTaskPolling();
                updateDisplayWithCompletedReasons(taskData);
                showPartialFailureWarning(taskData.failed_books);
            } else if (taskData.status === 'error') {
                console.error('❌ 任务失败:', taskData.error);
                stopTaskPolling();
                showTaskError(taskData.error);
            }
        } catch (error) {
            console.error('轮询请求失败:', error);
            stopTaskPolling();
        }
    }
    
    function updateBooksProgressively(completedBooks) {
        const displayArea = document.getElementById('suggestion-display');
        if (!displayArea) return;
        
        // 获取当前显示的书籍元素
        const bookItems = displayArea.querySelectorAll('.book-item');
        
        // 为每本已完成的书籍更新UI
        completedBooks.forEach((book, index) => {
            if (index < bookItems.length) {
                const bookItem = bookItems[index];
                
                // 移除加载指示器
                const loadingIndicator = bookItem.querySelector('.loading-indicator');
                if (loadingIndicator) {
                    loadingIndicator.remove();
                }
                
                // 移除加载文本
                const loadingText = bookItem.querySelector('div[style*="font-size: 9px"]');
                if (loadingText) {
                    loadingText.remove();
                }
                
                // 添加完成指示器
                if (!bookItem.querySelector('.completed-indicator')) {
                    const completedIndicator = document.createElement('div');
                    completedIndicator.className = 'completed-indicator';
                    completedIndicator.style.cssText = `
                        position: absolute;
                        top: 5px;
                        right: 5px;
                        width: 12px;
                        height: 12px;
                        background: #28a745;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 8px;
                    `;
                    completedIndicator.innerHTML = '✓';
                    bookItem.appendChild(completedIndicator);
                }
                
                // 更新样式，表示可以交互
                bookItem.style.borderColor = '#05a081';
                bookItem.style.backgroundColor = '#f8f9fa';
                bookItem.style.cursor = 'pointer';
                
                // 🔧 关键：更新书籍的悬停数据，使其可以立即展开查看
                // 将完成的书籍数据存储到元素的data属性中
                bookItem.dataset.bookData = JSON.stringify(book);
            }
        });
        
        // 🔧 关键修改：有一本书完成后就添加交互handler和提示信息
        if (completedBooks.length > 0 && typeof addInteractionHandlers === 'function') {
            // 重新添加交互handlers（只对已完成的书生效）
            addInteractionHandlers(displayArea, completedBooks);
            
            // 显示提示信息（只显示一次）
            if (!displayArea.querySelector('.completion-message')) {
                showCompletionMessage(displayArea);
            }
        }
        
        console.log(`✅ 已更新 ${completedBooks.length} 本书的显示状态`);
    }
    
    function updateDisplayWithCompletedReasons(taskData) {
        const displayArea = document.getElementById('suggestion-display');
        if (!displayArea) return;
        
        console.log('📚 更新完整推荐理由:', taskData.books);
        
        const bookItems = displayArea.querySelectorAll('.book-item');
        bookItems.forEach((item, index) => {
            const book = taskData.books[index];
            if (!book) return;

            const loadingIndicator = item.querySelector('.loading-indicator');
            if (loadingIndicator) loadingIndicator.remove();
            
            const loadingText = item.querySelector('div[style*="font-size: 9px"]');
            if (loadingText) loadingText.remove();
            
            const completedIndicator = document.createElement('div');
            completedIndicator.className = 'completed-indicator';
            completedIndicator.style.cssText = `
                position: absolute;
                top: 5px;
                right: 5px;
                width: 12px;
                height: 12px;
                background: #28a745;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 8px;
            `;
            completedIndicator.innerHTML = '✓';
            item.appendChild(completedIndicator);
            
            item.style.borderColor = '#05a081';
            item.style.backgroundColor = '#f8f9fa';
            item.style.cursor = 'pointer';
        });
        
        addInteractionHandlers(displayArea, taskData.books);
        showCompletionMessage(displayArea);
    }
    
    function showCompletionMessage(displayArea) {
        const completionMsg = document.createElement('div');
        completionMsg.className = 'completion-message';  // 添加class以便识别
        completionMsg.style.cssText = `
            background: #d4edda;
            color: #155724;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-top: 10px;
            border: 1px solid #c3e6cb;
            text-align: center;
        `;
        completionMsg.textContent = '✨ 想知道推荐理由？将鼠标悬停在书籍上查看详细分析';
        
        displayArea.appendChild(completionMsg);
        
        setTimeout(() => {
            if (completionMsg.parentNode) {
                completionMsg.remove();
            }
        }, 5000);
    }
    
    function showTaskError(error) {
        const displayArea = document.getElementById('suggestion-display');
        if (!displayArea) return;
        
        const errorMsg = document.createElement('div');
        errorMsg.style.cssText = `
            background: #f8d7da;
            color: #721c24;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-top: 10px;
            border: 1px solid #f5c6cb;
            text-align: center;
        `;
        errorMsg.textContent = `❌ 推荐理由生成失败: ${error}`;
        displayArea.appendChild(errorMsg);
    }
    
    function showPartialFailureWarning(failedBooks) {
        const displayArea = document.getElementById('suggestion-display');
        if (!displayArea) return;
        
        const warningMsg = document.createElement('div');
        warningMsg.style.cssText = `
            background: #fff3cd;
            color: #856404;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-top: 10px;
            border: 1px solid #ffeaa7;
            text-align: center;
        `;
        
        if (failedBooks && failedBooks.length > 0) {
            warningMsg.textContent = `⚠️ ${failedBooks.length}本书生成推荐理由失败（${failedBooks.join('、')}），已显示默认信息`;
        } else {
            warningMsg.textContent = `⚠️ 部分书籍生成推荐理由失败，已显示默认信息`;
        }
        
        displayArea.appendChild(warningMsg);
        
        // 5秒后自动隐藏警告
        setTimeout(() => {
            if (warningMsg.parentNode) {
                warningMsg.remove();
            }
        }, 5000);
    }

    async function sendToServer(inputValue, retryCount = 0) {
        // 🔧 检查是否为重复请求
        if (isDuplicateRequest(inputValue)) {
            console.log('🔄 跳过重复请求，使用缓存的任务ID:', window.__lastRequestCache.task_id);
            // 如果有缓存的任务ID且任务仍在进行中，继续使用该任务
            if (window.__lastRequestCache.task_id && currentPollingTaskId === window.__lastRequestCache.task_id) {
                console.log('✅ 当前正在轮询缓存的任务，无需重新请求');
                return;
            }
            // 如果缓存的任务已完成或不存在，也跳过请求
            console.log('✅ 使用缓存结果，跳过API请求');
            return;
        }
        
        window.__suggestionsInFlight = true;
        if (window.__loadingTimer) clearTimeout(window.__loadingTimer);
        stopTaskPolling();
        
        const now = Date.now();
        if (now - lastRequestTime < REQUEST_DELAY) {
            console.log('请求过于频繁，等待中...');
            await new Promise(resolve => setTimeout(resolve, REQUEST_DELAY - (now - lastRequestTime)));
        }
        lastRequestTime = Date.now();
        
        try {
            const response = await fetch('http://localhost:5001/api/books_with_reasons', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: inputValue,
                    session_id: window.JNULibrarySessionManager ? window.JNULibrarySessionManager.getSessionId() : null
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('🔍 服务器响应（异步API）:', data);
            
            // 🔧 更新请求缓存
            if (data.status === 'success' && data.books && data.books.length > 0) {
                const normalized = normalizeQuery(inputValue);
                const booksSignature = getBooksSignature(data.books);
                window.__lastRequestCache = {
                    query_normalized: normalized,
                    books_signature: booksSignature,
                    timestamp: Date.now(),
                    task_id: data.task_id
                };
                console.log('📝 更新前端请求缓存:', normalized, '-> 任务ID:', data.task_id);
                
                // 如果是从后端缓存返回的结果，记录日志
                if (data.from_cache) {
                    console.log('🔄 后端返回缓存结果，任务ID:', data.task_id);
                }
            }
            
            window.__suggestionsInFlight = false;
            clearTimeout(window.__loadingTimer);

            if (data.status === 'success' && data.books && data.books.length > 0) {
                showBooksWithReasons(data);
                window.__lastSuggestionsContent = JSON.stringify(data);
                if (data.task_id && data.reasons_loading) {
                    console.log('📡 启动异步理由轮询，任务ID:', data.task_id);
                    startTaskPolling(data.task_id);
                }
            } else {
                // 没有匹配结果时，保持加载动画，不显示错误信息
                // 让用户继续输入，直到有结果为止
                console.log('📝 暂无匹配结果，保持加载状态等待用户继续输入');
            }
        } catch (error) {
            console.error('请求失败:', error);
            window.__suggestionsInFlight = false;
            if (retryCount < MAX_RETRIES) {
                const retryDelay = RETRY_DELAY * Math.pow(2, retryCount);
                console.log(`重试中... (${retryCount + 1}/${MAX_RETRIES}), 等待 ${retryDelay}ms`);
                await new Promise(resolve => setTimeout(resolve, retryDelay));
                return sendToServer(inputValue, retryCount + 1);
            } else {
                // 网络错误且重试次数用尽时，也保持加载状态
                // 让用户继续输入，系统会自动重新请求
                console.log('⚠️ 请求失败但保持加载状态，等待用户继续输入');
                stopTaskPolling();
            }
        }
    }
    
    function handleInput(event) {
        const inputValue = event.target.value.trim();
        let displayArea = document.getElementById('suggestion-display');

        // 输入为空时隐藏
        if (inputValue.length === 0) {
            if (displayArea) hideDisplayArea(displayArea);
            stopTaskPolling();
            // 清空缓存
            window.__lastRequestCache = {
                query_normalized: '',
                books_signature: '',
                timestamp: 0,
                task_id: ''
            };
            return;
        }

        // 输入第1个字符：显示加载动画但不请求
        if (inputValue.length === 1) {
            displayArea = displayArea || createDisplayArea();
            if (displayArea) {
                showLoadingAnimation(displayArea);
                showDisplayArea(displayArea);
            }
            return;
        }
        
        // 🔧 检查是否是书籍点击触发的输入变化
        if (window.__isBookClickTriggered) {
            console.log('⚠️ 忽略书籍点击触发的输入变化:', inputValue);
            return; // 忽略这次输入，避免循环触发
        }
        
        // 🔧 关键修改：在显示加载动画之前先检查重复请求
        if (isDuplicateRequest(inputValue)) {
            console.log('🔄 检测到重复请求，保持当前显示不变');
            // 如果缓存任务已完成但没有轮询，尝试重新启动轮询
            if (!currentPollingTaskId && window.__lastRequestCache.task_id) {
                console.log('🔄 重新启动缓存任务的轮询');
                startTaskPolling(window.__lastRequestCache.task_id);
            }
            return; // 直接返回，不改变UI
        }
        
        // 输入≥2个字符且非重复：显示加载动画并请求API
        displayArea = displayArea || createDisplayArea();
        if (displayArea) {
            showLoadingAnimation(displayArea);
            showDisplayArea(displayArea);
        }
        
        console.log('捕获到输入:', inputValue);
        sendToServer(inputValue);
    }

    function setupMonitor() {
        const inputElement = document.querySelector(targetSelector);
        if (inputElement && !inputElement.hasAttribute('data-monitored')) {
            console.log('找到输入框，设置监听器');
            inputElement.setAttribute('data-monitored', 'true');
            
            let debounceTimer;
            inputElement.addEventListener('input', (event) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    handleInput(event);
                }, 350); // 适度提升防抖，降低无效请求频率
            });

            // --- 🚀 新增: 添加Enter键监听器 ---
            inputElement.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault(); // 阻止默认的回车提交行为
                    
                    const displayArea = document.getElementById('suggestion-display');
                    
                    // 检查推荐面板是否可见
                    if (displayArea && displayArea.style.opacity === '1') {
                        const activeBookItem = displayArea.querySelector('.book-item.active-suggestion');
                        
                        if (activeBookItem) {
                            console.log('🎯 Enter键触发，搜索高亮书籍');
                            const booksDataStr = displayArea.dataset.booksData;
                            const bookIndex = parseInt(activeBookItem.dataset.bookIndex, 10);
                            
                            if (booksDataStr && !isNaN(bookIndex)) {
                                try {
                                    const books = JSON.parse(booksDataStr);
                                    const bookToSearch = books[bookIndex];
                                    
                                    if (bookToSearch && typeof window.searchBookInLibrary === 'function') {
                                        window.searchBookInLibrary(bookToSearch.title, bookToSearch.author, bookToSearch.isbn);
                                        // 搜索后隐藏推荐
                                        hideDisplayArea(displayArea);
                                    }
                                } catch (e) {
                                    console.error("解析书籍数据或搜索时出错:", e);
                                }
                            }
                        }
                    }
                }
            });
            // --- 🚀 监听器添加完毕 ---

            createDisplayArea();

            document.addEventListener('click', function(event) {
                const displayArea = document.getElementById('suggestion-display');
                const isClickInside = displayArea && displayArea.contains(event.target);
                const isClickOnInput = inputElement.contains(event.target);
                if (!isClickInside && !isClickOnInput) {
                    if (displayArea) hideDisplayArea(displayArea);
                }
            });
        }
    }

    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.addedNodes.length) {
                if (document.querySelector(targetSelector)) {
                    setupMonitor();
                    break;
                }
            }
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // setInterval(setupMonitor, 2000);

    setupMonitor();
    
    console.log('监听脚本加载完成，等待输入框出现');
})();
