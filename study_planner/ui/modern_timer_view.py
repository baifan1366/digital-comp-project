"""
现代化计时器显示组件

提供美观的倒计时显示，带有状态指示和进度条
"""

import tkinter as tk
from tkinter import ttk
from study_planner.core.state import SessionState
from study_planner.utils.time_utils import format_time


class ModernColors:
    """配色方案"""
    PRIMARY_BLUE = "#2196F3"
    SUCCESS = "#4CAF50"
    WARNING = "#FF9800"
    ERROR = "#F44336"
    INFO = "#2196F3"
    BG_LIGHT = "#F5F9FC"
    BG_CARD = "#FAFBFD"
    TEXT_PRIMARY = "#1A1A1A"
    TEXT_SECONDARY = "#666666"
    BORDER = "#E0E0E0"


class ModernTimerDisplay:
    """现代化计时器显示"""
    
    def __init__(self, parent: tk.Widget):
        """初始化计时器显示"""
        self.parent = parent
        
        # 创建主框架
        self.frame = tk.Frame(parent, bg=ModernColors.BG_LIGHT)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # 构建UI
        self._build_ui()
        
        # 初始化显示
        self.update_time(0)
        self.update_state(SessionState.IDLE)
        self.update_cycle(0, 0)

    
    def _build_ui(self):
        """构建UI组件"""
        # 计时器卡片
        timer_card = tk.Frame(
            self.frame,
            bg=ModernColors.BG_CARD,
            highlightbackground=ModernColors.BORDER,
            highlightthickness=1
        )
        timer_card.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # 状态标签
        self.state_label = tk.Label(
            timer_card,
            text="准备就绪",
            bg=ModernColors.BG_CARD,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 18, "bold")
        )
        self.state_label.pack(pady=(30, 10))
        
        # 计时器显示 - 大号数字
        self.timer_label = tk.Label(
            timer_card,
            text="00:00",
            bg=ModernColors.BG_CARD,
            fg=ModernColors.PRIMARY_BLUE,
            font=("Arial", 72, "bold")
        )
        self.timer_label.pack(pady=20)
        
        # 进度条容器
        progress_container = tk.Frame(timer_card, bg=ModernColors.BG_CARD)
        progress_container.pack(fill=tk.X, padx=50, pady=(10, 20))
        
        # 进度条背景
        self.progress_bg = tk.Canvas(
            progress_container,
            height=8,
            bg=ModernColors.BG_LIGHT,
            highlightthickness=0
        )
        self.progress_bg.pack(fill=tk.X)
        
        # 进度条
        self.progress_bar = self.progress_bg.create_rectangle(
            0, 0, 0, 8,
            fill=ModernColors.PRIMARY_BLUE,
            outline=""
        )
        
        # 循环进度标签
        self.cycle_label = tk.Label(
            timer_card,
            text="",
            bg=ModernColors.BG_CARD,
            fg=ModernColors.TEXT_SECONDARY,
            font=("Microsoft YaHei UI", 12)
        )
        self.cycle_label.pack(pady=(10, 30))
        
        # 保存总时间用于进度计算
        self.total_seconds = 0

    
    def update_time(self, remaining_seconds: int):
        """更新倒计时显示"""
        time_str = format_time(remaining_seconds)
        self.timer_label.config(text=time_str)
        
        # 更新进度条
        if self.total_seconds > 0:
            progress = (self.total_seconds - remaining_seconds) / self.total_seconds
            self._update_progress_bar(progress)
    
    def update_state(self, state: SessionState):
        """更新状态指示"""
        state_config = {
            SessionState.IDLE: ("准备就绪", ModernColors.TEXT_PRIMARY, ModernColors.PRIMARY_BLUE),
            SessionState.STUDY: ("学习时间 📚", ModernColors.SUCCESS, ModernColors.SUCCESS),
            SessionState.BREAK: ("休息时间 ☕", ModernColors.INFO, ModernColors.INFO),
            SessionState.LONG_BREAK: ("长休息 🌟", ModernColors.PRIMARY_BLUE, ModernColors.PRIMARY_BLUE),
            SessionState.PAUSED: ("已暂停 ⏸", ModernColors.WARNING, ModernColors.WARNING),
            SessionState.COMPLETED: ("完成 ✓", ModernColors.TEXT_SECONDARY, ModernColors.TEXT_SECONDARY)
        }
        
        text, label_color, timer_color = state_config.get(
            state,
            ("未知", ModernColors.TEXT_PRIMARY, ModernColors.PRIMARY_BLUE)
        )
        
        self.state_label.config(text=text, fg=label_color)
        self.timer_label.config(fg=timer_color)
        
        # 更新进度条颜色
        self.progress_bg.itemconfig(self.progress_bar, fill=timer_color)
    
    def update_cycle(self, current_cycle: int, total_cycles: int):
        """更新循环进度"""
        if total_cycles > 1 and current_cycle > 0:
            cycle_text = f"第 {current_cycle} / {total_cycles} 个循环"
        elif total_cycles == 1 and current_cycle > 0:
            cycle_text = "单次学习"
        else:
            cycle_text = ""
        
        self.cycle_label.config(text=cycle_text)
    
    def set_total_time(self, seconds: int):
        """设置总时间（用于进度条计算）"""
        self.total_seconds = seconds
    
    def _update_progress_bar(self, progress: float):
        """更新进度条"""
        # 确保进度在0-1之间
        progress = max(0.0, min(1.0, progress))
        
        # 获取画布宽度
        canvas_width = self.progress_bg.winfo_width()
        if canvas_width <= 1:
            canvas_width = 400  # 默认宽度
        
        # 计算进度条宽度
        bar_width = int(canvas_width * progress)
        
        # 更新进度条
        self.progress_bg.coords(self.progress_bar, 0, 0, bar_width, 8)
    
    def get_frame(self) -> tk.Frame:
        """获取主框架"""
        return self.frame
