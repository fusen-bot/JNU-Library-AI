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

// 连接到输入事件，当用户输入时发送到Python服务器
document.addEventListener('DOMContentLoaded', function() {
    // 为所有输入框添加事件监听
    const addListeners = () => {
        const inputs = document.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            if (!input.hasAttribute('data-suggestion-attached')) {
                input.setAttribute('data-suggestion-attached', 'true');
                
                // 添加输入事件防抖处理
                let debounceTimer;
                input.addEventListener('input', function(e) {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => {
                        const value = e.target.value;
                        if (value.length > 3) {
                            // 注释掉自动开始搜索会话记录 - 改为手动控制
                            // if (window.startSearchSession) {
                            //     window.startSearchSession(value);
                            // }
                            
                            // 请求新的书籍推荐API
                            fetch('http://localhost:5001/api/books_with_reasons', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    query: value,
                                    session_id: window.JNULibrarySessionManager ? window.JNULibrarySessionManager.getSessionId() : null
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                console.log("🔍 新API返回的完整数据:", data); // 改进日志
                                console.log("📋 数据契约验证:");
                                console.log("  - status:", data.status);
                                console.log("  - user_query:", data.user_query);
                                console.log("  - books数量:", data.books ? data.books.length : 0);
                                
                                                                 if (data.status === 'success' && data.books && data.books.length > 0) {
                                     // ✨ 使用新版推荐理由UI组件
                                     if (typeof showBooksWithReasons === 'function') {
                                         showBooksWithReasons(data);
                                     } else {
                                         // 备用：旧版显示方式
                                         let displayText = "书籍：";
                                         data.books.forEach((book, index) => {
                                             displayText += `《${book.title}》`;
                                             if (index < data.books.length - 1) displayText += "，";
                                         });
                                         displayText += "\n问题：相关推荐理由展示？学术影响力如何？";
                                         showSuggestion(displayText);
                                     }
                                     
                                     // 详细打印每本书的推荐理由
                                     data.books.forEach((book, index) => {
                                         console.log(`📚 书籍${index + 1}: ${book.title}`);
                                         console.log("  📖 作者:", book.author);
                                         console.log("  🧠 推荐依据:", book.logical_reason);
                                         console.log("  👥 借阅热度:", book.social_reason);
                                         console.log("  ---");
                                     });
                                 } else {
                                     console.warn("⚠️ API返回数据格式异常:", data);
                                 }
                            })
                            .catch(err => console.error('❌ 获取书籍推荐失败:', err));
                        }
                    }, 500); // 500ms的防抖延迟
                });
            }
        });
    };
    
    // 初始添加监听器
    addListeners();
    
    // 监听DOM变化，为新添加的输入元素添加监听器
    const observer = new MutationObserver(mutations => {
        addListeners();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('建议显示脚本已加载');
});

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
    
    console.log('🚀 初始化输入监控系统 - 集成新版推荐理由UI');
    
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
        }, 500);
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
            
            if (taskData.status === 'completed') {
                console.log('🎉 任务完成，更新UI');
                stopTaskPolling();
                updateDisplayWithCompletedReasons(taskData);
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

    async function sendToServer(inputValue, retryCount = 0) {
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
                const displayArea = document.getElementById('suggestion-display');
                if (displayArea) {
                    showErrorMessage(displayArea, data.error || data.message || '暂无推荐结果');
                    showDisplayArea(displayArea);
                }
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
                const displayArea = document.getElementById('suggestion-display');
                if (displayArea) {
                    showErrorMessage(displayArea, '多次尝试后无法连接到推荐服务。');
                    showDisplayArea(displayArea);
                }
                stopTaskPolling();
            }
        }
    }
    
    function handleInput(event) {
        const inputValue = event.target.value.trim();
        const displayArea = document.getElementById('suggestion-display');

        if (inputValue.length < 2) {
            if (displayArea) hideDisplayArea(displayArea);
            stopTaskPolling();
            // 注释掉自动结束搜索会话 - 改为手动控制
            // if (window.endSearchSession) {
            //     window.endSearchSession('input_too_short');
            // }
            return;
        }
        
        // 🔧 检查是否是书籍点击触发的输入变化
        if (window.__isBookClickTriggered) {
            console.log('⚠️ 忽略书籍点击触发的输入变化:', inputValue);
            return; // 忽略这次输入，避免循环触发
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
                }, 300);
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
    
    setInterval(setupMonitor, 2000);

    setupMonitor();
    
    console.log('监听脚本加载完成，等待输入框出现');
})();

function showErrorMessage(container, message) {
    // 清除加载动画
    
    
    container.innerHTML = '';
}

