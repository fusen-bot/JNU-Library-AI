#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话控制器 - 手动控制搜索会话的开始和结束
使用方法:
  python session_controller.py start [查询内容] [描述]
  python session_controller.py end [结束原因]
  python session_controller.py status
"""

import sys
import json
from datetime import datetime

class SessionController:
    def __init__(self):
        self.instructions = {
            'start': self._get_start_instructions,
            'end': self._get_end_instructions,
            'status': self._get_status_instructions,
            'reset': self._get_reset_instructions
        }
    
    def _get_start_instructions(self, participant_name="", experiment_description=""):
        """获取开始被试实验会话的指令"""
        if not experiment_description:
            experiment_description = f"实验_{datetime.now().strftime('%H:%M:%S')}"
        
        instructions = [
            "🎯 请在浏览器控制台执行以下命令开始被试实验会话:",
            "",
            f"manualStartParticipantSession('{participant_name}', '{experiment_description}')",
            "",
            "或者复制以下完整脚本到控制台执行:",
            f"""
if (window.manualStartParticipantSession) {{
    window.manualStartParticipantSession('{participant_name}', '{experiment_description}');
    console.log('✅ 被试实验会话已开始');
    const status = window.getCurrentSessionStatus();
    console.log('📊 当前状态:', status);
    console.log(`👤 被试姓名: ${{status.participant_name}}`);
    console.log(`🆔 被试ID: ${{status.session_id}}`);
    console.log(`📝 实验描述: ${{status.experiment_description}}`);
    console.log(`🔢 全局被试总数: ${{status.global_participant_count}}`);
}} else {{
    console.error('❌ 手动控制方法未加载，请确保session_manager.js已正确加载');
}}
            """.strip()
        ]
        
        return instructions
    
    def _get_end_instructions(self, reason="experiment_completed"):
        """获取结束被试实验会话的指令"""
        instructions = [
            "🏁 请在浏览器控制台执行以下命令结束被试实验会话:",
            "",
            f"manualEndParticipantSession('{reason}')",
            "",
            "或者复制以下完整脚本到控制台执行:",
            f"""
if (window.manualEndParticipantSession) {{
    window.manualEndParticipantSession('{reason}');
    console.log('🏁 被试实验会话已结束');
    const status = window.getCurrentSessionStatus();
    console.log('📊 当前状态:', status);
}} else {{
    console.error('❌ 手动控制方法未加载，请确保session_manager.js已正确加载');
}}
            """.strip()
        ]
        
        return instructions
    
    def _get_status_instructions(self):
        """获取查看状态的指令"""
        instructions = [
            "📊 请在浏览器控制台执行以下命令查看当前会话状态:",
            "",
            "getCurrentSessionStatus()",
            "",
            "或者复制以下完整脚本到控制台执行:",
            """
if (window.getCurrentSessionStatus) {
    const status = window.getCurrentSessionStatus();
    console.log('📊 当前会话状态:', status);
    
    console.log(`🆔 当前被试ID: ${status.session_id}`);
    console.log(`👤 被试姓名: ${status.participant_name || '未设置'}`);
    console.log(`📝 实验描述: ${status.experiment_description || '未设置'}`);
    console.log(`🔢 全局被试总数: ${status.global_participant_count}`);
    console.log(`📝 待发送事件: ${status.pending_events}个`);
    
    if (status.has_active_session) {
        const session = status.current_session;
        console.log(`✅ 有活跃实验会话:`);
        console.log(`   👤 被试: ${session.participant_name || '未知'}`);
        console.log(`   📝 描述: ${session.experiment_description || session.description || '无描述'}`);
        console.log(`   ⏱️  持续时间: ${Math.round(session.duration_ms / 1000)}秒`);
        console.log(`   📚 已点击书籍: ${session.books_clicked_count}本`);
    } else {
        console.log('❌ 当前没有活跃的实验会话');
    }
} else {
    console.error('❌ 状态查询方法未加载，请确保session_manager.js已正确加载');
}
            """.strip()
        ]
        
        return instructions
    
    def _get_reset_instructions(self):
        """获取重置计数器的指令"""
        instructions = [
            "🔄 请在浏览器控制台执行以下命令重置全局被试计数器:",
            "",
            "resetGlobalParticipantCounter()",
            "",
            "⚠️  警告: 这将重置全局被试计数器，下次开始的实验将从001开始",
            "",
            "或者复制以下完整脚本到控制台执行:",
            """
if (window.resetGlobalParticipantCounter) {
    const confirmReset = confirm('⚠️ 确定要重置全局被试计数器吗？\\n\\n这将使下次开始的实验从001开始编号。');
    if (confirmReset) {
        const status = window.resetGlobalParticipantCounter();
        console.log('🔄 全局被试计数器已重置');
        console.log('📊 当前状态:', status);
    } else {
        console.log('❌ 用户取消重置操作');
    }
} else {
    console.error('❌ 重置方法未加载，请确保session_manager.js已正确加载');
}
            """.strip()
        ]
        
        return instructions
    
    def execute_command(self, command, *args):
        """执行命令并显示指令"""
        if command not in self.instructions:
            return self._show_help()
        
        instructions = self.instructions[command](*args)
        
        print("\n" + "="*60)
        for instruction in instructions:
            print(instruction)
        print("="*60 + "\n")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = [
            "📖 被试实验控制器使用帮助:",
            "",
            "使用方法:",
            "  python session_controller.py start [被试姓名] [实验描述]",
            "  python session_controller.py end [结束原因]",
            "  python session_controller.py status",
            "  python session_controller.py reset",
            "",
            "示例:",
            "  python session_controller.py start '张三' '研究机器学习相关书籍'",
            "  python session_controller.py end '实验完成'",
            "  python session_controller.py status",
            "  python session_controller.py reset",
            "",
            "说明:",
            "  - start: 开始新的被试实验会话，自动分配全局连续ID",
            "  - end: 结束当前被试实验会话，可以指定结束原因",
            "  - status: 查看当前会话状态和统计信息",
            "  - reset: 重置全局被试计数器（谨慎使用）",
            "",
            "ID格式:",
            "  - 被试ID: 被试_001, 被试_002, 被试_003... (全局连续)",
            "  - 跨天连续，不会重置",
            "",
            "注意: 需要在浏览器控制台中执行显示的JavaScript代码"
        ]
        
        print("\n" + "="*60)
        for line in help_text:
            print(line)
        print("="*60 + "\n")

def main():
    controller = SessionController()
    
    if len(sys.argv) < 2:
        controller._show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        participant_name = sys.argv[2] if len(sys.argv) > 2 else ""
        experiment_description = sys.argv[3] if len(sys.argv) > 3 else ""
        controller.execute_command("start", participant_name, experiment_description)
    
    elif command == "end":
        reason = sys.argv[2] if len(sys.argv) > 2 else "experiment_completed"
        controller.execute_command("end", reason)
    
    elif command == "status":
        controller.execute_command("status")
    
    elif command == "reset":
        controller.execute_command("reset")
    
    elif command in ["help", "-h", "--help"]:
        controller._show_help()
    
    else:
        print(f"❌ 未知命令: {command}")
        controller._show_help()

if __name__ == "__main__":
    main()
