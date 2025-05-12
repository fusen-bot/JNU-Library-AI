// 创建一个建议框元素
function createSuggestionBox() {
    const suggestionBox = document.createElement('div');
    suggestionBox.id = 'ai-suggestion-box';
    suggestionBox.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 300px;
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
        margin-bottom: 8px;
        color: #333;
        display: flex;
        justify-content: space-between;
    `;
    title.innerHTML = '<span>智能输入建议</span><span id="suggestion-close" style="cursor:pointer;">×</span>';
    
    // 添加内容区域
    const content = document.createElement('div');
    content.id = 'suggestion-content';
    content.style.cssText = `
        font-size: 13px;
        line-height: 1.5;
        color: #555;
    `;
    
    suggestionBox.appendChild(title);
    suggestionBox.appendChild(content);
    document.body.appendChild(suggestionBox);
    
    // 添加关闭事件
    document.getElementById('suggestion-close').addEventListener('click', function() {
        suggestionBox.style.display = 'none';
    });
    
    return suggestionBox;
}

// 显示建议
function showSuggestion(suggestion) {
    let suggestionBox = document.getElementById('ai-suggestion-box');
    if (!suggestionBox) {
        suggestionBox = createSuggestionBox();
    }
    
    const contentElement = document.getElementById('suggestion-content');
    contentElement.textContent = suggestion;
    suggestionBox.style.display = 'block';
    
    // 5秒后自动隐藏
    setTimeout(() => {
        suggestionBox.style.display = 'none';
    }, 5001);
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
                            // 请求建议
                            fetch('http://localhost:5001/input', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    element: e.target.tagName,
                                    id: e.target.id,
                                    value: value,
                                    timestamp: new Date().getTime()
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.suggestion) {
                                    showSuggestion(data.suggestion);
                                }
                            })
                            .catch(err => console.error('获取建议失败:', err));
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