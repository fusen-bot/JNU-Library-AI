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
    // 创建标题
    const titleElement = document.createElement('div');
    titleElement.style.cssText = `
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 12px;
        color: #333;
        text-align: center;
        padding-bottom: 8px;
        border-bottom: 2px solid #05a081;
    `;
    titleElement.textContent = '🤖 AI智能推荐理由';
    container.appendChild(titleElement);
    
    // 限制最多显示3本书
    const maxBooks = Math.min(books.length, 3);
    
    for (let i = 0; i < maxBooks; i++) {
        const book = books[i];
        createBookReasonCard(container, book, i);
    }
}

function createBookReasonCard(container, book, index) {
    // 创建书籍卡片容器
    const bookCard = document.createElement('div');
    bookCard.style.cssText = `
        margin-bottom: 16px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background: linear-gradient(135deg, #f8fffe 0%, #f0f7f5 100%);
        overflow: hidden;
        transition: all 0.3s ease;
    `;
    
    // 书籍标题栏
    const bookHeader = document.createElement('div');
    bookHeader.style.cssText = `
        padding: 12px 15px;
        background: linear-gradient(90deg, #05a081 0%, #048068 100%);
        color: white;
        font-weight: bold;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 8px;
    `;
    
    // 书籍序号
    const bookNumber = document.createElement('span');
    bookNumber.style.cssText = `
        background: rgba(255,255,255,0.2);
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        flex-shrink: 0;
    `;
    bookNumber.textContent = index + 1;
    
    // 书籍标题
    const bookTitle = document.createElement('span');
    bookTitle.style.cssText = `
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    `;
    bookTitle.textContent = `《${book.title}》`;
    
    // 作者信息
    const bookAuthor = document.createElement('span');
    bookAuthor.style.cssText = `
        font-size: 11px;
        opacity: 0.9;
        font-weight: normal;
    `;
    bookAuthor.textContent = `- ${book.author}`;
    
    bookHeader.appendChild(bookNumber);
    bookHeader.appendChild(bookTitle);
    bookHeader.appendChild(bookAuthor);
    
    // 推荐理由块容器
    const reasonsContainer = document.createElement('div');
    reasonsContainer.style.cssText = `
        padding: 15px;
        display: flex;
        gap: 1px;
        background: #f8f8f8;
    `;
    
    // 创建逻辑分析块
    const logicalBlock = createReasonBlock(
        '🧠 逻辑分析',
        book.logical_reason,
        '#4a90e2',  // 蓝色主题
        '#e8f2ff'
    );
    
    // 创建社交证据块
    const socialBlock = createReasonBlock(
        '👥 社交证据', 
        book.social_reason,
        '#7b68ee',  // 紫色主题
        '#f0ecff'
    );
    
    reasonsContainer.appendChild(logicalBlock);
    reasonsContainer.appendChild(socialBlock);
    
    bookCard.appendChild(bookHeader);
    bookCard.appendChild(reasonsContainer);
    container.appendChild(bookCard);
    
    // 添加卡片悬停效果
    bookCard.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 4px 12px rgba(5,160,129,0.15)';
    });
    
    bookCard.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'none';
    });
}

function createReasonBlock(title, reasonData, themeColor, bgColor) {
    const block = document.createElement('div');
    block.style.cssText = `
        flex: 1;
        background: ${bgColor};
        border-radius: 6px;
        padding: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        border: 2px solid transparent;
    `;
    
    // 标题
    const blockTitle = document.createElement('div');
    blockTitle.style.cssText = `
        font-weight: bold;
        font-size: 12px;
        color: ${themeColor};
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    `;
    blockTitle.textContent = title;
    
    // 简要内容（默认显示）
    const briefContent = document.createElement('div');
    briefContent.style.cssText = `
        font-size: 11px;
        color: #666;
        line-height: 1.4;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    `;
    
    // 详细内容（悬停展开）
    const detailContent = document.createElement('div');
    detailContent.style.cssText = `
        font-size: 11px;
        color: #555;
        line-height: 1.5;
        margin-top: 8px;
        opacity: 0;
        max-height: 0;
        overflow: hidden;
        transition: all 0.3s ease;
        background: rgba(255,255,255,0.5);
        border-radius: 4px;
        padding: 0;
    `;
    
    // 根据理由类型填充内容
    if (title.includes('逻辑分析')) {
        briefContent.textContent = reasonData.ai_understanding;
        
        const detailHTML = `
            <div style="padding: 8px;">
                <div style="margin-bottom: 6px;"><strong>🎯 查询理解:</strong> ${reasonData.user_query_recap}</div>
                <div style="margin-bottom: 6px;"><strong>🤖 AI分析:</strong> ${reasonData.ai_understanding}</div>
                <div><strong>🔗 匹配逻辑:</strong> ${reasonData.keyword_match}</div>
            </div>
        `;
        detailContent.innerHTML = detailHTML;
        
    } else if (title.includes('社交证据')) {
        briefContent.textContent = reasonData.trend;
        
        let departmentsHTML = '<div style="margin-bottom: 6px;"><strong>📊 各学院借阅率:</strong></div>';
        reasonData.departments.forEach(dept => {
            const percentage = Math.round(dept.rate * 100);
            const barWidth = dept.rate * 100;
            departmentsHTML += `
                <div style="margin: 4px 0; font-size: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis;">${dept.name}</span>
                        <span style="font-weight: bold; color: ${themeColor};">${percentage}%</span>
                    </div>
                    <div style="background: #ddd; height: 3px; border-radius: 2px; margin-top: 2px;">
                        <div style="background: ${themeColor}; height: 100%; width: ${barWidth}%; border-radius: 2px; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            `;
        });
        
        const detailHTML = `
            <div style="padding: 8px;">
                ${departmentsHTML}
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #eee;">
                    <strong>📈 趋势分析:</strong> ${reasonData.trend}
                </div>
            </div>
        `;
        detailContent.innerHTML = detailHTML;
    }
    
    block.appendChild(blockTitle);
    block.appendChild(briefContent);
    block.appendChild(detailContent);
    
    // 悬停展开效果
    block.addEventListener('mouseenter', function() {
        this.style.border = `2px solid ${themeColor}`;
        this.style.background = '#ffffff';
        briefContent.style.opacity = '0.7';
        detailContent.style.opacity = '1';
        detailContent.style.maxHeight = '200px';
        detailContent.style.padding = '0';
    });
    
    block.addEventListener('mouseleave', function() {
        this.style.border = '2px solid transparent';
        this.style.background = bgColor;
        briefContent.style.opacity = '1';
        detailContent.style.opacity = '0';
        detailContent.style.maxHeight = '0';
        detailContent.style.padding = '0';
    });
    
    return block;
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