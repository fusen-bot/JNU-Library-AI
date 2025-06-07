/**
 * 书籍搜索跳转功能测试脚本
 * 用于收集和分析跳转事件，帮助调试和优化
 */

console.log('🧪 书籍搜索跳转测试脚本已加载');

/**
 * ===========================================
 * 测试工具类
 * ===========================================
 */

class BookSearchTester {
    constructor() {
        this.testResults = [];
        this.startTime = Date.now();
        this.isTestMode = true;
        this.init();
    }

    init() {
        console.log('🚀 初始化书籍搜索测试器');
        
        // 确保测试事件收集器存在
        if (!window.__testSearchEvents) {
            window.__testSearchEvents = [];
        }
        
        // 监听页面变化
        this.observePageChanges();
        
        // 设置自动测试
        this.setupAutoTests();
    }

    /**
     * 模拟点击书籍项进行测试
     */
    simulateBookClick(bookTitle = null) {
        console.log('🎯 开始模拟书籍点击测试');
        
        const bookItems = document.querySelectorAll('.book-item');
        if (bookItems.length === 0) {
            console.warn('⚠️ 未找到可点击的书籍项');
            return false;
        }

        let targetItem = null;
        if (bookTitle) {
            // 查找指定书名的书籍项
            bookItems.forEach(item => {
                const titleElement = item.querySelector('span[style*="font-weight: bold"]');
                if (titleElement && titleElement.textContent.includes(bookTitle)) {
                    targetItem = item;
                }
            });
        } else {
            // 随机选择一个书籍项
            targetItem = bookItems[Math.floor(Math.random() * bookItems.length)];
        }

        if (!targetItem) {
            console.warn('⚠️ 未找到目标书籍项');
            return false;
        }

        console.log('🖱️ 模拟点击书籍项...');
        
        // 记录测试开始
        const testStart = {
            timestamp: new Date().toISOString(),
            action: 'test_click_started',
            target: targetItem.textContent.trim()
        };
        
        this.testResults.push(testStart);
        window.__testSearchEvents.push(testStart);

        // 模拟点击
        const clickEvent = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        
        targetItem.dispatchEvent(clickEvent);
        
        console.log('✅ 模拟点击已执行');
        return true;
    }

    /**
     * 测试页面元素检测
     */
    testPageElements() {
        console.log('🔍 开始页面元素检测测试');
        
        const testReport = {
            timestamp: new Date().toISOString(),
            action: 'page_elements_test',
            results: {}
        };

        // 检测输入框
        const inputs = document.querySelectorAll('input');
        testReport.results.inputs = {
            total: inputs.length,
            searchInputs: [],
            monitoredInputs: []
        };

        inputs.forEach((input, index) => {
            const inputInfo = {
                index: index,
                className: input.className,
                placeholder: input.placeholder,
                type: input.type,
                visible: input.offsetParent !== null,
                hasMonitoredAttribute: input.hasAttribute('data-monitored')
            };

            if (input.placeholder && (input.placeholder.includes('搜索') || input.placeholder.includes('检索'))) {
                testReport.results.inputs.searchInputs.push(inputInfo);
            }

            if (input.hasAttribute('data-monitored')) {
                testReport.results.inputs.monitoredInputs.push(inputInfo);
            }
        });

        // 检测按钮
        const buttons = document.querySelectorAll('button');
        testReport.results.buttons = {
            total: buttons.length,
            searchButtons: []
        };

        buttons.forEach((button, index) => {
            if (button.className.includes('search') || 
                button.textContent.includes('检索') || 
                button.querySelector('.anticon-search')) {
                testReport.results.buttons.searchButtons.push({
                    index: index,
                    className: button.className,
                    textContent: button.textContent.trim(),
                    hasSearchIcon: !!button.querySelector('.anticon-search'),
                    visible: button.offsetParent !== null
                });
            }
        });

        // 检测书籍项
        const bookItems = document.querySelectorAll('.book-item');
        testReport.results.bookItems = {
            total: bookItems.length,
            withClickHandlers: 0,
            details: []
        };

        bookItems.forEach((item, index) => {
            const hasClickHandler = item.onclick !== null || 
                                  item.addEventListener !== undefined;
            if (hasClickHandler) testReport.results.bookItems.withClickHandlers++;
            
            testReport.results.bookItems.details.push({
                index: index,
                hasClickHandler: hasClickHandler,
                textContent: item.textContent.trim().substring(0, 50) + '...',
                visible: item.offsetParent !== null
            });
        });

        this.testResults.push(testReport);
        window.__testSearchEvents.push(testReport);
        
        console.log('📊 页面元素检测完成:', testReport.results);
        return testReport;
    }

    /**
     * 测试搜索功能
     */
    async testSearchFunction(searchQuery = '计算机') {
        console.log(`🔍 开始搜索功能测试，查询: "${searchQuery}"`);
        
        const testStart = {
            timestamp: new Date().toISOString(),
            action: 'search_function_test_started',
            searchQuery: searchQuery
        };
        
        this.testResults.push(testStart);
        window.__testSearchEvents.push(testStart);

        try {
            // 尝试调用搜索函数
            if (typeof window.searchBookInLibrary === 'function') {
                const result = window.searchBookInLibrary(searchQuery, '测试作者', '9787111000000');
                console.log('✅ searchBookInLibrary 函数调用成功:', result);
                
                this.testResults.push({
                    timestamp: new Date().toISOString(),
                    action: 'search_function_called',
                    success: true,
                    result: result
                });
            } else {
                console.warn('⚠️ searchBookInLibrary 函数未找到');
                this.testResults.push({
                    timestamp: new Date().toISOString(),
                    action: 'search_function_not_found',
                    success: false
                });
            }

            // 等待一段时间收集事件
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            console.log('✅ 搜索功能测试完成');
            return true;
            
        } catch (error) {
            console.error('❌ 搜索功能测试失败:', error);
            this.testResults.push({
                timestamp: new Date().toISOString(),
                action: 'search_function_test_error',
                error: error.message
            });
            return false;
        }
    }

    /**
     * 监听页面变化
     */
    observePageChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // 检查是否添加了新的书籍项
                            if (node.classList && node.classList.contains('book-item')) {
                                console.log('📚 检测到新的书籍项被添加');
                                this.testResults.push({
                                    timestamp: new Date().toISOString(),
                                    action: 'new_book_item_detected',
                                    nodeInfo: {
                                        className: node.className,
                                        textContent: node.textContent.trim().substring(0, 50)
                                    }
                                });
                            }
                            
                            // 检查是否添加了推荐显示区域
                            if (node.id === 'suggestion-display') {
                                console.log('💡 检测到推荐显示区域被添加');
                                this.testResults.push({
                                    timestamp: new Date().toISOString(),
                                    action: 'suggestion_display_detected'
                                });
                            }
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        console.log('👀 页面变化监听器已启动');
    }

    /**
     * 设置自动测试
     */
    setupAutoTests() {
        // 每30秒自动执行一次页面元素检测
        setInterval(() => {
            if (this.isTestMode) {
                this.testPageElements();
            }
        }, 30000);

        console.log('⏰ 自动测试已设置');
    }

    /**
     * 生成测试报告
     */
    generateReport() {
        const report = {
            testSession: {
                startTime: new Date(this.startTime).toISOString(),
                endTime: new Date().toISOString(),
                duration: Date.now() - this.startTime
            },
            testResults: this.testResults,
            searchEvents: window.__testSearchEvents || [],
            summary: {
                totalTestActions: this.testResults.length,
                totalSearchEvents: (window.__testSearchEvents || []).length,
                clickTests: this.testResults.filter(r => r.action === 'test_click_started').length,
                searchFunctionTests: this.testResults.filter(r => r.action === 'search_function_test_started').length,
                pageElementTests: this.testResults.filter(r => r.action === 'page_elements_test').length,
                errors: this.testResults.filter(r => r.action && r.action.includes('error')).length
            },
            recommendations: this.generateRecommendations()
        };

        console.log('📊 测试报告生成完成:', report);
        return report;
    }

    /**
     * 生成改进建议
     */
    generateRecommendations() {
        const recommendations = [];
        
        // 分析搜索事件
        const searchEvents = window.__testSearchEvents || [];
        const failedSearches = searchEvents.filter(e => 
            e.action === 'simulateLibrarySearch_failed' || 
            e.action === 'search_button_not_found'
        );
        
        if (failedSearches.length > 0) {
            recommendations.push({
                type: 'search_failure',
                message: '检测到搜索失败事件，建议检查页面元素选择器',
                priority: 'high',
                details: failedSearches
            });
        }

        // 分析点击事件
        const clickEvents = searchEvents.filter(e => e.action === 'book_item_clicked');
        if (clickEvents.length === 0) {
            recommendations.push({
                type: 'no_clicks',
                message: '未检测到书籍点击事件，可能需要添加更多测试',
                priority: 'medium'
            });
        }

        return recommendations;
    }

    /**
     * 清除测试数据
     */
    clearTestData() {
        this.testResults = [];
        if (window.__testSearchEvents) {
            window.__testSearchEvents = [];
        }
        console.log('🧹 测试数据已清除');
    }

    /**
     * 停止测试模式
     */
    stopTesting() {
        this.isTestMode = false;
        console.log('⏹️ 测试模式已停止');
    }
}

/**
 * ===========================================
 * 全局测试工具函数
 * ===========================================
 */

// 创建全局测试实例
window.bookSearchTester = new BookSearchTester();

// 快速测试函数
window.testBookClick = function(bookTitle) {
    return window.bookSearchTester.simulateBookClick(bookTitle);
};

window.testPageElements = function() {
    return window.bookSearchTester.testPageElements();
};

window.testSearchFunction = function(query) {
    return window.bookSearchTester.testSearchFunction(query);
};

window.getTestReport = function() {
    return window.bookSearchTester.generateReport();
};

window.clearTestData = function() {
    window.bookSearchTester.clearTestData();
};

// 键盘快捷键支持
document.addEventListener('keydown', function(e) {
    // Ctrl + Shift + T: 执行完整测试
    if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        console.log('🚀 执行完整测试套件...');
        Promise.resolve()
            .then(() => window.testPageElements())
            .then(() => window.testSearchFunction('计算机'))
            .then(() => {
                setTimeout(() => {
                    window.testBookClick();
                    console.log('✅ 完整测试套件执行完成');
                }, 1000);
            });
    }
    
    // Ctrl + Shift + R: 生成测试报告
    if (e.ctrlKey && e.shiftKey && e.key === 'R') {
        const report = window.getTestReport();
        console.table(report.summary);
    }
    
    // Ctrl + Shift + C: 清除测试数据
    if (e.ctrlKey && e.shiftKey && e.key === 'C') {
        window.clearTestData();
    }
});

console.log('📚 书籍搜索测试工具已就绪！');
console.log('💡 快捷键:');
console.log('  - Ctrl+Shift+T: 执行完整测试');
console.log('  - Ctrl+Shift+R: 生成测试报告');  
console.log('  - Ctrl+Shift+C: 清除测试数据');
console.log('🔧 可用函数:');
console.log('  - testBookClick(bookTitle): 模拟点击书籍');
console.log('  - testPageElements(): 检测页面元素');
console.log('  - testSearchFunction(query): 测试搜索功能');
console.log('  - getTestReport(): 生成测试报告'); 