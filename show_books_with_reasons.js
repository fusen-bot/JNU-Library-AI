/**
 * 新版书籍推荐理由显示组件
 * 用于展示包含推荐依据和借阅热度的书籍推荐
 * 支持异步加载推荐理由
 */

function showBooksWithReasons(apiData) {
    // 注入增强样式
    injectEnhancedStyles();
    // 初始化测试事件收集器
    initializeTestEventCollector();
    
    console.log("🎨 使用真实环境新版推荐理由UI组件");
    console.log("📊 API数据:", apiData);
    
    const displayArea = document.getElementById('suggestion-display');
    if (!displayArea) return;
    
    // 清除加载动画
    if (displayArea._blinkInterval) {
        clearInterval(displayArea._blinkInterval);
        displayArea._blinkInterval = null;
    }
    
    if (apiData.status !== 'success' || !apiData.books || apiData.books.length === 0) {
        showErrorMessage(displayArea, "暂无推荐结果");
        return;
    }
    
    // 清空并重新创建内容
    displayArea.innerHTML = '';
    createBooksReasonContainer(displayArea, apiData.books);
    showDisplayArea(displayArea);
}

function createBooksReasonContainer(container, books) {
    // 1. 创建一个统一的书籍列表容器
    const booksList = document.createElement('div');
    booksList.className = 'books-container';
    booksList.style.cssText = `
        display: flex;
        gap: 10px;
        position: relative;
        margin-bottom: 16px;
    `;

    // 限制最多显示3本书
    const maxBooks = Math.min(books.length, 3);
    
    // 2. 循环创建每一本书的基础展示项
    for (let i = 0; i < maxBooks; i++) {
        const book = books[i];
        const bookItem = document.createElement('div');
        bookItem.className = 'book-item';
        
        // 根据是否有推荐理由来设置不同的样式和行为
        const hasReasons = book.logical_reason && book.social_reason;
        const isLoading = book.reasons_loading === true;
        
        bookItem.style.cssText = `
            flex: 1;
            min-width: 0;
            padding: 10px;
            border: 1px solid ${isLoading ? '#01A081' : (hasReasons ? '#05a081' : '#ddd')};
            border-radius: 6px;
            cursor: ${hasReasons ? 'pointer' : 'default'};
            position: relative;
            transition: all 0.3s ease;
        `;
        
        // 2a. 书籍标题等基础信息
        const bookHeader = document.createElement('div');
        bookHeader.style.cssText = `
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;
        `;
        
        // 书籍序号
        const bookNumber = document.createElement('span');
        bookNumber.style.cssText = `
            background: ${isLoading ? '#01A081' : '#05a081'};
            color: white;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            flex-shrink: 0;
        `;
        bookNumber.textContent = i + 1;
        
        // 书籍标题
        const bookTitle = document.createElement('span');
        bookTitle.style.cssText = `
            font-weight: bold;
            font-size: 12px;
            color: #333;
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        `;
        bookTitle.textContent = `《${book.title}》`;
        
        bookHeader.appendChild(bookNumber);
        bookHeader.appendChild(bookTitle);
        
        // 作者信息
        const bookAuthor = document.createElement('div');
        bookAuthor.style.cssText = `
            font-size: 10px;
            color: #666;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        `;
        
        // 作者文本
        const authorText = document.createElement('span');
        authorText.style.cssText = `
            flex: 1;
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        `;
        authorText.textContent = `作者：${book.author}`;
        
        // 星级显示
        const starsContainer = document.createElement('div');
        starsContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 2px;
            flex-shrink: 0;
            margin-right: 20px;
        `;
        
        // 根据match_stars添加星星
        const stars = book.match_stars || 0;
        
        for (let i = 0; i < 3; i++) {
            const star = document.createElement('span');
            star.textContent = i < stars ? '★' : '☆';
            star.style.cssText = `
                color: ${i < stars ? '#FFD700' : '#ddd'};
                font-size: 12px;
            `;
            starsContainer.appendChild(star);
        }
        
        bookAuthor.appendChild(authorText);
        bookAuthor.appendChild(starsContainer);
        
        bookItem.appendChild(bookHeader);
        bookItem.appendChild(bookAuthor);
        
        // 2b. 如果正在加载理由，添加加载指示器
        if (isLoading) {
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'loading-indicator';
            loadingIndicator.style.cssText = `
                position: absolute;
                top: 5px;
                right: 5px;
                width: 12px;
                height: 12px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #01A081;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            `;
            
            // 添加CSS动画
            if (!document.getElementById('spinner-style')) {
                const style = document.createElement('style');
                style.id = 'spinner-style';
                style.textContent = `
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
            }
            
            bookItem.appendChild(loadingIndicator);
            
        }

        // 添加 bookIndex 数据属性用于后续查找
        bookItem.dataset.bookIndex = i;
        // 📖【修复】添加唯一的ISBN作为数据属性，确保数据和视图的稳定链接
        if (book.isbn) {
            bookItem.dataset.bookIsbn = book.isbn;
        }
        booksList.appendChild(bookItem);
    }
    
    container.appendChild(booksList);

    // 2c. 在书籍列表后创建一个共享的、全宽度的详情浮层
    const sharedDetailPanel = document.createElement('div');
    sharedDetailPanel.className = 'shared-detail-panel';
    sharedDetailPanel.style.cssText = `
        display: none;
        width: 100%;
        background: white;
        border: 1px solid #05a081;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 20px;
        margin-top: 10px;
        border-radius: 8px;
        opacity: 0;
        transform: translateY(-10px);
        transition: opacity 0.3s ease, transform 0.3s ease;
        box-sizing: border-box;
        z-index: 10;
    `;
    container.appendChild(sharedDetailPanel);

    // 3. 只有当书籍有完整推荐理由时才添加交互事件
    const booksWithReasons = books.filter(book => book.logical_reason && book.social_reason);
    if (booksWithReasons.length > 0) {
        addInteractionHandlers(container, books);
    }
}

// 辅助函数: 创建浮层的详细内容
function createDetailContentHTML(book) {
    // 生成左右分栏布局：
    let departmentsHTML = '';
    book.social_reason.departments.forEach(dept => {
        const percentage = Math.round(dept.rate * 100);
        const barWidth = dept.rate * 100;
        departmentsHTML += `
            <div style="margin: 4px 0; font-size: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis;">${dept.name}</span>
                    <span style="font-weight: bold; color: #7b68ee;">${percentage}%</span>
                </div>
                <div style="background: #ddd; height: 3px; border-radius: 2px; margin-top: 2px;">
                    <div style="background: #7b68ee; height: 100%; width: ${barWidth}%; border-radius: 2px; transition: width 0.3s ease;"></div>
                </div>
            </div>
        `;
    });

    // 处理不同的API返回格式（新API和旧格式兼容）
    const logicalReason = book.logical_reason || {};
    const coreConcepts = Array.isArray(logicalReason.book_core_concepts) 
        ? logicalReason.book_core_concepts.join('、') 
        : logicalReason.book_core_concepts || 'N/A';
    const appFields = Array.isArray(logicalReason.application_fields_match) 
        ? logicalReason.application_fields_match.join('、') 
        : logicalReason.application_fields_match || 'N/A';
    const userIntent = logicalReason.user_query_intent || logicalReason.user_query_recap || 'N/A';

    return `
        <div style="display: flex; gap: 15px;">
            <div style="flex: 1;">
                <h4 style="margin: 0 0 8px 0; color: #4a90e2; font-size: 13px;">推荐依据</h4>
                <p style="margin: 0 0 6px 0; font-size: 11px;"><strong>你的检索意图:</strong> ${userIntent}</p>
                <p style="margin: 0 0 6px 0; font-size: 11px;"><strong>本书核心概念:</strong> ${coreConcepts}</p>
                <p style="margin: 0; font-size: 11px;"><strong>应用领域匹配:</strong> ${appFields}</p>
            </div>
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
                    <h4 style="margin: 0; color: #7b68ee; font-size: 13px;">借阅热度</h4>
                    <div style="font-size: 12px; color: #333;"><strong>📊 各学院借阅率</strong></div>
                </div>
                ${departmentsHTML}
            </div>
        </div>
    `;
}

// 交互处理函数 - 增强版：支持悬停显示详情和点击跳转搜索
function addInteractionHandlers(container, books) {
    const booksListContainer = container.querySelector('.books-container');
    const allBookItems = booksListContainer.querySelectorAll('.book-item');
    const sharedDetailPanel = container.querySelector('.shared-detail-panel');
    let hidePanelTimeout; // 用于延迟隐藏浮层
    
    allBookItems.forEach(item => {
        // 📖【修复】使用ISBN从数据中查找对应的书籍，不再依赖数组顺序
        const itemIsbn = item.dataset.bookIsbn;
        if (!itemIsbn) {
            console.warn('⚠️ 书籍项缺少ISBN标识，无法附加精确的点击事件。');
            return;
        }
        const book = books.find(b => b.isbn === itemIsbn);

        // 只为有完整推荐理由的书籍项添加交互
        if (!book || !book.logical_reason || !book.social_reason) {
            return;
        }

        // 🆕 添加点击事件处理
        item.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log(`📚 用户点击了书籍: ${book.title}`);
            
            // 使用新的Session管理器记录点击事件
            if (window.recordBookClick) {
                window.recordBookClick({
                    title: book.title,
                    author: book.author,
                    isbn: book.isbn
                });
            }
            
            // 保留旧的测试事件记录以兼容现有测试
            if (window.__testSearchEvents) {
                window.__testSearchEvents.push({
                    timestamp: new Date().toISOString(),
                    action: 'book_item_clicked',
                    bookTitle: book.title,
                    bookAuthor: book.author,
                    bookISBN: book.isbn
                });
            }
            
            // 添加点击反馈效果
            this.style.transform = 'scale(0.98)';
            this.classList.add('search-success-flash');
            
            setTimeout(() => {
                this.style.transform = 'translateY(-2px)';
                this.classList.remove('search-success-flash');
            }, 300);
            
            // 执行搜索跳转
            try {
                searchBookInLibrary(book.title, book.author, book.isbn);
                
                // 结束当前搜索会话
                if (window.endSearchSession) {
                    window.endSearchSession('book_clicked');
                }
                
                // 隐藏推荐面板
                setTimeout(() => {
                    const displayArea = document.getElementById('suggestion-display');
                    if (displayArea) {
                        console.log('🚪 隐藏推荐面板');
                        hideDisplayArea(displayArea);
                    }
                }, 1500);
                
            } catch (error) {
                console.error('❌ 执行搜索跳转时发生错误:', error);
                if (window.__testSearchEvents) {
                    window.__testSearchEvents.push({
                        timestamp: new Date().toISOString(),
                        action: 'search_execution_error',
                        error: error.message,
                        bookTitle: book.title
                    });
                }
            }
        });

        // 增强鼠标进入事件
        item.addEventListener('mouseenter', function() {
            // 记录书籍悬停开始事件
            if (window.recordBookHover) {
                window.recordBookHover({
                    title: book.title,
                    author: book.author,
                    isbn: book.isbn
                }, 'hover_start');
            }
            
            // 清除可能存在的隐藏定时器
            clearTimeout(hidePanelTimeout);

            if (sharedDetailPanel) {
                // 更新浮层内容
                sharedDetailPanel.innerHTML = createDetailContentHTML(book);
                
                // 显示共享浮层
                sharedDetailPanel.style.display = 'block';
                setTimeout(() => {
                    sharedDetailPanel.style.opacity = '1';
                    sharedDetailPanel.style.transform = 'translateY(0)';
                }, 10);
            }

            // 高亮当前悬停的书籍项，重置其他项
            allBookItems.forEach(i => {
                if (i !== this) {
                    // 只有带有完整理由的项才改变样式
                    const otherBookIndex = parseInt(i.dataset.bookIndex, 10);
                    const otherBook = books[otherBookIndex];
                    if (otherBook && otherBook.logical_reason && otherBook.social_reason) {
                        i.style.borderColor = '#05a081'; // 保持完成状态的边框颜色
                    } else if (!otherBook.reasons_loading) {
                        i.style.borderColor = '#ddd';
                    }
                    i.style.transform = 'translateY(0)';
                    i.style.boxShadow = 'none';
                }
            });
            this.style.borderColor = '#05a081';
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });
    });

    // 隐藏浮层的函数
    const hidePanel = () => {
        if (sharedDetailPanel) {
            sharedDetailPanel.style.opacity = '0';
            sharedDetailPanel.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                sharedDetailPanel.style.display = 'none';
            }, 300);
        }

        // 重置所有书籍项的样式
        allBookItems.forEach(item => {
            const bookIndex = parseInt(item.dataset.bookIndex, 10);
            const book = books[bookIndex];
            if (book && book.logical_reason && book.social_reason) {
                item.style.borderColor = '#05a081';
            } else if (!book.reasons_loading) {
                item.style.borderColor = '#ddd';
            }
            item.style.transform = 'translateY(0)';
            item.style.boxShadow = 'none';
        });
    };

    // 为每个书籍项添加鼠标离开事件
    allBookItems.forEach(item => {
        const itemIsbn = item.dataset.bookIsbn;
        const book = books.find(b => b.isbn === itemIsbn);
        
        if (book && book.logical_reason && book.social_reason) {
            item.addEventListener('mouseleave', function() {
                // 记录书籍悬停结束事件
                if (window.recordBookHover) {
                    window.recordBookHover({
                        title: book.title,
                        author: book.author,
                        isbn: book.isbn
                    }, 'hover_end');
                }
            });
        }
    });

    // 鼠标离开整个容器时，延迟隐藏浮层
    container.addEventListener('mouseleave', () => {
        hidePanelTimeout = setTimeout(hidePanel, 100);
    });

    // 当鼠标进入共享浮层时，取消隐藏操作
    if (sharedDetailPanel) {
        sharedDetailPanel.addEventListener('mouseenter', () => {
            clearTimeout(hidePanelTimeout);
        });
        
        // 当鼠标离开共享浮层时，立即隐藏
        sharedDetailPanel.addEventListener('mouseleave', () => {
            hidePanel();
        });
    }
}
        
function showErrorMessage(container, message) {
    // 清除加载动画
    if (container._blinkInterval) {
        clearInterval(container._blinkInterval);
        container._blinkInterval = null;
    }
    
    container.innerHTML = '';
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        padding: 20px;
        text-align: center;
        color: #e74c3c;
        background: #ffe6e6;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        font-style: italic;
    `;
    errorDiv.textContent = message;
    container.appendChild(errorDiv);
}

function showDisplayArea(displayArea) {
    if (!displayArea) return;
    displayArea.style.display = 'block';
    setTimeout(() => {
        displayArea.style.opacity = '1';
        displayArea.style.pointerEvents = 'auto';
    }, 10);
}

function hideDisplayArea(displayArea) {
    if (!displayArea) return;
    displayArea.style.opacity = '0';
    displayArea.style.pointerEvents = 'none';
    setTimeout(() => {
        displayArea.style.display = 'none';
    }, 300);
}

/**
 * ===========================================
 * 书籍搜索跳转功能模块
 * ===========================================
 */

// 注入增强样式
function injectEnhancedStyles() {
    if (document.getElementById('book-interaction-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'book-interaction-styles';
    style.textContent = `
        .book-item {
            cursor: pointer !important;
            user-select: none;
        }
        
        .book-item:hover {
            cursor: pointer !important;
        }
        
        .book-item:active {
            transform: scale(0.98) !important;
        }
        
        .book-item::after {
            content: "🔍";
            position: absolute;
            top: 40px;
            right: 1px;
            font-size: 10px;
            opacity: 0;
            transition: opacity 0.2s ease;
            pointer-events: none;
            background: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(132, 223, 233, 0.17);
        }
        
        .book-item:hover::after {
            opacity: 0.9;
        }
        
        .search-success-flash {
            animation: searchFlash 0.6s ease-out;
        }
        
        @keyframes searchFlash {
            0% { background-color: #d4edda; transform: scale(1); }
            50% { background-color: #a7d4aa; transform: scale(1.02); }
            100% { background-color: transparent; transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
}

// 在图书馆系统中搜索指定书籍
function searchBookInLibrary(bookTitle, bookAuthor, bookISBN) {
    console.log(`🔍 开始在图书馆系统中搜索: ${bookTitle}`);
    
    // 记录搜索事件用于测试
    if (window.__testSearchEvents) {
        window.__testSearchEvents.push({
            timestamp: new Date().toISOString(),
            bookTitle: bookTitle,
            bookAuthor: bookAuthor,
            bookISBN: bookISBN,
            method: 'searchBookInLibrary'
        });
    }
    
    // 方案1: 模拟在当前页面搜索
    const searchSuccess = simulateLibrarySearch(bookTitle, bookAuthor);
    
    if (!searchSuccess) {
        console.log('模拟搜索失败，尝试备用方案');
        // 方案2: 备用 - 构造URL跳转
        jumpToBookSearch(bookTitle, bookISBN);
    }
    
    return true;
}

// 模拟图书馆搜索操作
function simulateLibrarySearch(bookTitle, bookAuthor) {
    try {
        console.log('🎯 尝试模拟图书馆搜索操作');
        
        // 记录模拟搜索尝试
        if (window.__testSearchEvents) {
            window.__testSearchEvents.push({
                timestamp: new Date().toISOString(),
                action: 'simulateLibrarySearch_attempt',
                bookTitle: bookTitle
            });
        }
        
        // 1. 找到搜索输入框 - 使用多种选择器尝试
        const inputSelectors = [
            '.ant-input.ant-select-search__field[data-monitored="true"]',
            '.ant-select-search__field',
            'input.ant-input',
            'input[placeholder*="搜索"]',
            'input[placeholder*="检索"]'
        ];
        
        let searchInput = null;
        for (const selector of inputSelectors) {
            searchInput = document.querySelector(selector);
            if (searchInput) {
                console.log(`✅ 找到搜索输入框，使用选择器: ${selector}`);
                break;
            }
        }
        
        if (!searchInput) {
            console.warn('❌ 未找到搜索输入框，记录页面状态');
            if (window.__testSearchEvents) {
                window.__testSearchEvents.push({
                    timestamp: new Date().toISOString(),
                    action: 'simulateLibrarySearch_failed',
                    reason: 'input_not_found',
                    availableInputs: Array.from(document.querySelectorAll('input')).map(input => ({
                        className: input.className,
                        placeholder: input.placeholder,
                        type: input.type
                    }))
                });
            }
            return false;
        }
        
        // 2. 构造搜索关键词 - 优先使用书名
        const searchQuery = bookTitle.replace(/《|》/g, '').trim();
        console.log(`📝 构造搜索关键词: "${searchQuery}"`);
        
        // 3. 🔧 设置书籍点击标志，防止输入监听器循环触发
        if (window.__isBookClickTriggered !== undefined) {
            window.__isBookClickTriggered = true;
            // 清除之前的超时
            if (window.__bookClickTimeout) {
                clearTimeout(window.__bookClickTimeout);
            }
            // 2秒后自动重置标志
            window.__bookClickTimeout = setTimeout(() => {
                window.__isBookClickTriggered = false;
                console.log('✅ 书籍点击标志已重置');
            }, 2000);
        }
        
        // 4. 使用React兼容的方式来更新输入框的值
        // 这是关键修复：直接设置 .value 属性可能不会被React的状态管理系统捕获
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(searchInput, searchQuery);

        // 5. 触发React能够识别的`input`事件，以确保状态更新
        const inputEvent = new Event('input', { bubbles: true });
        searchInput.dispatchEvent(inputEvent);
        
        // 记录输入设置
        if (window.__testSearchEvents) {
            window.__testSearchEvents.push({
                timestamp: new Date().toISOString(),
                action: 'input_value_set',
                searchQuery: searchQuery,
                isBookClickTriggered: window.__isBookClickTriggered,
                inputElement: {
                    className: searchInput.className,
                    placeholder: searchInput.placeholder
                }
            });
        }
        
        console.log('📤 已触发React兼容的输入事件');
        
        // 6. 延迟点击搜索按钮以等待页面响应
        setTimeout(() => {
            const searchButtonSelectors = [
                'button.ant-btn.searchBtn___eV8Vn',
                'button.searchBtn___eV8Vn',
                'button.ant-btn.newSearchBtn___3p7dd',
                'button[type="button"]:has(.anticon-search)',
                'button:contains("检索")',
                '.ant-btn-primary:has(.anticon-search)'
            ];
            
            let searchBtn = null;
            for (const selector of searchButtonSelectors) {
                try {
                    searchBtn = document.querySelector(selector);
                    if (searchBtn) {
                        console.log(`✅ 找到搜索按钮，使用选择器: ${selector}`);
                        break;
                    }
                } catch (e) {
                    // 某些选择器可能不支持，继续尝试下一个
                    continue;
                }
            }
            
            if (searchBtn) {
                console.log('🔍 模拟点击搜索按钮');
                searchBtn.click();
                
                // 记录搜索按钮点击
                if (window.__testSearchEvents) {
                    window.__testSearchEvents.push({
                        timestamp: new Date().toISOString(),
                        action: 'search_button_clicked',
                        success: true
                    });
                }
            } else {
                console.warn('❌ 未找到搜索按钮');
                if (window.__testSearchEvents) {
                    window.__testSearchEvents.push({
                        timestamp: new Date().toISOString(),
                        action: 'search_button_not_found',
                        availableButtons: Array.from(document.querySelectorAll('button')).map(btn => ({
                            className: btn.className,
                            textContent: btn.textContent.trim(),
                            type: btn.type
                        }))
                    });
                }
            }
        }, 500);
        
        return true;
        
    } catch (error) {
        console.error('❌ 模拟搜索过程中发生错误:', error);
        if (window.__testSearchEvents) {
            window.__testSearchEvents.push({
                timestamp: new Date().toISOString(),
                action: 'simulateLibrarySearch_error',
                error: error.message,
                stack: error.stack
            });
        }
        return false;
    }
}

// 备用方案：直接URL跳转
function jumpToBookSearch(bookTitle, bookISBN) {
    try {
        const cleanTitle = bookTitle.replace(/《|》/g, '').trim();
        const baseUrl = 'https://opac.jiangnan.edu.cn';
        
        // 构造搜索URL（根据实际的URL格式调整）
        let searchUrl = `${baseUrl}/#/search?query=${encodeURIComponent(cleanTitle)}`;
        
        if (bookISBN && bookISBN !== 'N/A') {
            searchUrl += `&isbn=${encodeURIComponent(bookISBN)}`;
        }
        
        console.log(`🌐 跳转到搜索页面: ${searchUrl}`);
        
        // 记录URL跳转
        if (window.__testSearchEvents) {
            window.__testSearchEvents.push({
                timestamp: new Date().toISOString(),
                action: 'url_jump',
                searchUrl: searchUrl,
                bookTitle: cleanTitle,
                bookISBN: bookISBN
            });
        }
        
        window.open(searchUrl, '_blank');
        
    } catch (error) {
        console.error('❌ URL跳转失败:', error);
        if (window.__testSearchEvents) {
            window.__testSearchEvents.push({
                timestamp: new Date().toISOString(),
                action: 'url_jump_error',
                error: error.message
            });
        }
        // 最后的备用方案：直接跳转到首页
        window.open('https://opac.jiangnan.edu.cn/#/Home', '_blank');
    }
}

/**
 * ===========================================
 * 测试和调试工具
 * ===========================================
 */

// 初始化测试事件收集器
function initializeTestEventCollector() {
    if (!window.__testSearchEvents) {
        window.__testSearchEvents = [];
        console.log('📊 测试事件收集器已初始化');
    }
}

// 调试图书馆页面元素
function debugLibraryElements() {
    console.log('🔍 调试图书馆页面元素:');
    
    const searchInput = document.querySelector('.ant-input.ant-select-search__field[data-monitored="true"]');
    console.log('主搜索输入框:', searchInput);
    
    const searchBtn = document.querySelector('button.ant-btn.searchBtn___eV8Vn');
    console.log('主搜索按钮:', searchBtn);
    
    const allInputs = document.querySelectorAll('input');
    console.log('页面所有输入框数量:', allInputs.length);
    allInputs.forEach((input, index) => {
        console.log(`输入框 ${index + 1}:`, {
            className: input.className,
            placeholder: input.placeholder,
            type: input.type,
            visible: input.offsetParent !== null
        });
    });
    
    const allButtons = document.querySelectorAll('button');
    console.log('页面所有按钮数量:', allButtons.length);
    allButtons.forEach((button, index) => {
        console.log(`按钮 ${index + 1}:`, {
            className: button.className,
            textContent: button.textContent.trim(),
            type: button.type,
            visible: button.offsetParent !== null
        });
    });
    
    // 检查是否有搜索相关的图标
    const searchIcons = document.querySelectorAll('.anticon-search');
    console.log('搜索图标数量:', searchIcons.length);
}

// 获取测试报告
function getTestReport() {
    if (!window.__testSearchEvents || window.__testSearchEvents.length === 0) {
        console.log('📋 暂无测试事件记录');
        return null;
    }
    
    const report = {
        totalEvents: window.__testSearchEvents.length,
        events: window.__testSearchEvents,
        summary: {
            searchAttempts: window.__testSearchEvents.filter(e => e.method === 'searchBookInLibrary').length,
            simulationAttempts: window.__testSearchEvents.filter(e => e.action === 'simulateLibrarySearch_attempt').length,
            simulationSuccesses: window.__testSearchEvents.filter(e => e.action === 'search_button_clicked').length,
            urlJumps: window.__testSearchEvents.filter(e => e.action === 'url_jump').length,
            errors: window.__testSearchEvents.filter(e => e.action && e.action.includes('error')).length
        },
        generatedAt: new Date().toISOString()
    };
    
    console.log('📊 测试报告:', report);
    return report;
}

// 清除测试事件
function clearTestEvents() {
    if (window.__testSearchEvents) {
        window.__testSearchEvents = [];
        console.log('🧹 测试事件已清除');
    }
}

// 全局暴露测试工具
window.debugLibraryElements = debugLibraryElements;
window.getTestReport = getTestReport;
window.clearTestEvents = clearTestEvents;
window.searchBookInLibrary = searchBookInLibrary;

// 导出函数以便在其他文件中使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { showBooksWithReasons };
} 