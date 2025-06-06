/**
 * 新版书籍推荐理由显示组件
 * 用于展示包含逻辑分析和社交证据的书籍推荐
 */

function showBooksWithReasons(apiData) {
    let suggestionBox = document.getElementById('ai-suggestion-box');
    if (!suggestionBox) {
        suggestionBox = createSuggestionBox();
    }
    
    const contentElement = document.getElementById('suggestion-content');
    contentElement.innerHTML = ''; // 清空内容
    
    console.log("🎨 使用新版推荐理由UI组件");
    console.log("📊 API数据:", apiData);
    
    if (apiData.status !== 'success' || !apiData.books || apiData.books.length === 0) {
        showErrorMessage(contentElement, "暂无推荐结果");
        return;
    }
    
    // 创建书籍推荐容器
    createBooksReasonContainer(contentElement, apiData.books);
    
    // 显示建议框
    suggestionBox.style.display = 'block';
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
        bookItem.style.cssText = `
            flex: 1;
            min-width: 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background-color: #f8f9fa;
            cursor: pointer;
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
            background: #05a081;
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

        // 2b. 创建默认隐藏的详情浮层
        const detailPanel = document.createElement('div');
        detailPanel.className = 'detail-panel';
        detailPanel.style.cssText = `
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            margin-top: 5px;
            background: white;
            border: 1px solid #05a081;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 15px;
            z-index: 10;
            border-radius: 8px;
            opacity: 0;
            transform: translateY(-10px) scaleY(0.95);
            transform-origin: top center;
            pointer-events: none;
            transition: opacity 0.3s ease, transform 0.3s ease;
        `;
        
        // 将逻辑分析和社交证据的HTML内容填充到这里
        detailPanel.innerHTML = createDetailContentHTML(book);
        
        bookItem.appendChild(detailPanel);
        booksList.appendChild(bookItem);
    }
    
    container.appendChild(booksList);

    // 3. 在这里统一添加事件监听器
    addInteractionHandlers(booksList);
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

    return `
        <div style="display: flex; gap: 15px;">
            <div style="flex: 1;">
                <h4 style="margin: 0 0 8px 0; color: #4a90e2; font-size: 13px;">🧠 逻辑分析</h4>
                <p style="margin: 0 0 6px 0; font-size: 11px;"><strong>查询理解:</strong> ${book.logical_reason.user_query_recap}</p>
                <p style="margin: 0 0 6px 0; font-size: 11px;"><strong>AI分析:</strong> ${book.logical_reason.ai_understanding}</p>
                <p style="margin: 0; font-size: 11px;"><strong>匹配逻辑:</strong> ${book.logical_reason.keyword_match}</p>
            </div>
            <div style="flex: 1;">
                <h4 style="margin: 0 0 8px 0; color: #7b68ee; font-size: 13px;">👥 社交证据</h4>
                ${departmentsHTML}
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #eee; font-size: 11px;">
                    <strong>趋势分析:</strong> ${book.social_reason.trend}
                </div>
            </div>
        </div>
    `;
}

// 交互处理函数
function addInteractionHandlers(booksListContainer) {
    const allBookItems = booksListContainer.querySelectorAll('.book-item');
    
    allBookItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            // 1. 先隐藏所有其他的浮层
            const allDetailPanels = booksListContainer.querySelectorAll('.detail-panel');
            allDetailPanels.forEach(panel => {
                panel.classList.remove('visible');
                panel.style.opacity = '0';
                panel.style.transform = 'translateY(-10px) scaleY(0.95)';
                panel.style.pointerEvents = 'none';
                setTimeout(() => {
                    if (!panel.classList.contains('visible')) {
                        panel.style.display = 'none';
                    }
                }, 300);
            });

            // 2. 找到当前这本书对应的浮层并显示它
            const currentPanel = this.querySelector('.detail-panel');
            if (currentPanel) {
                currentPanel.style.display = 'block';
                // 延迟一帧应用class，确保CSS transition生效
                setTimeout(() => {
                    currentPanel.classList.add('visible');
                    currentPanel.style.opacity = '1';
                    currentPanel.style.transform = 'translateY(0) scaleY(1)';
                    currentPanel.style.pointerEvents = 'auto';
                }, 10);
            }

            // 书籍项的悬停效果
            this.style.borderColor = '#05a081';
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });
    });

    // 3. 在整个推荐组件的大容器上监听 mouseleave
    booksListContainer.addEventListener('mouseleave', function() {
        // 隐藏所有浮层
        const allDetailPanels = booksListContainer.querySelectorAll('.detail-panel');
        allDetailPanels.forEach(panel => {
            panel.classList.remove('visible');
            panel.style.opacity = '0';
            panel.style.transform = 'translateY(-10px) scaleY(0.95)';
            panel.style.pointerEvents = 'none';
            // 等动画结束后再彻底隐藏，防止动画闪烁
            setTimeout(() => {
                if (!panel.classList.contains('visible')) {
                    panel.style.display = 'none';
                }
            }, 300); // 300ms 对应CSS动画时长
        });

        // 重置所有书籍项的样式
        const allBookItems = booksListContainer.querySelectorAll('.book-item');
        allBookItems.forEach(item => {
            item.style.borderColor = '#ddd';
            item.style.transform = 'translateY(0)';
            item.style.boxShadow = 'none';
        });
    });
}



function showErrorMessage(container, message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        padding: 20px;
        text-align: center;
        color: #666;
        font-style: italic;
    `;
    errorDiv.textContent = message;
    container.appendChild(errorDiv);
}

// 导出函数以便在其他文件中使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { showBooksWithReasons };
} 