import React from 'react';
import { createRoot } from 'react-dom/client';
import InteractionDashboard from './interaction-dashboard';
import './styles.css';

/**
 * 独立的可视化分析应用
 * 可以通过文件上传功能加载和分析会话数据
 */
const StandaloneAnalysisApp: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <InteractionDashboard />
    </div>
  );
};

// 初始化应用
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<StandaloneAnalysisApp />);
} else {
  console.error('找不到根容器元素，请确保HTML中有id="root"的元素');
}

export default StandaloneAnalysisApp;
