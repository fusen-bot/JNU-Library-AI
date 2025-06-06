/**
 * 新版书籍推荐理由显示组件
 * 用于展示包含逻辑分析和社交证据的书籍推荐
 * 支持异步加载推荐理由
 */

function showBooksWithReasons(apiData) {
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
        `;
        bookAuthor.textContent = `作者：${book.author}`;
        
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
    let departmentsHTML = '<div style="margin-bottom: 6px;"><strong>📊 各学院借阅率:</strong></div>';
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
                <h4 style="margin: 0 0 8px 0; color: #4a90e2; font-size: 13px;">🧠 逻辑分析</h4>
                <p style="margin: 0 0 6px 0; font-size: 11px;"><strong>你的检索意图:</strong> ${userIntent}</p>
                <p style="margin: 0 0 6px 0; font-size: 11px;"><strong>本书核心概念:</strong> ${coreConcepts}</p>
                <p style="margin: 0; font-size: 11px;"><strong>应用领域匹配:</strong> ${appFields}</p>
            </div>
            <div style="flex: 1;">
                <h4 style="margin: 0 0 8px 0; color: #7b68ee; font-size: 13px;">👥 社交证据</h4>
                ${departmentsHTML}
            </div>
        </div>
    `;
}

// 交互处理函数 - 重构为共享浮层模式
function addInteractionHandlers(container, books) {
    const booksListContainer = container.querySelector('.books-container');
    const allBookItems = booksListContainer.querySelectorAll('.book-item');
    const sharedDetailPanel = container.querySelector('.shared-detail-panel');
    let hidePanelTimeout; // 用于延迟隐藏浮层
    
    allBookItems.forEach(item => {
        // 只为有完整推荐理由的书籍项添加交互
        const bookIndex = parseInt(item.dataset.bookIndex, 10);
        const book = books[bookIndex];
        if (!book || !book.logical_reason || !book.social_reason) {
            return;
        }

        item.addEventListener('mouseenter', function() {
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

// 导出函数以便在其他文件中使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { showBooksWithReasons };
} 