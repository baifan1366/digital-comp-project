"""
简化版现代化主窗口 - 不使用Canvas滚动

这个版本移除了Canvas滚动，直接使用Frame布局，
确保所有内容都能正常显示。
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from study_planner.core.plans import StudyPlan, PlanManager
from study_planner.data.history import HistoryManager
from study_planner.data.statistics import StatisticsTracker
from study_planner.utils.validation import validate_numeric_input
from study_planner.utils.time_utils import format_duration


class ModernColors:
    """现代蓝白配色方案"""
    PRIMARY_BLUE = "#2196F3"
    LIGHT_BLUE = "#64B5F6"
    DARK_BLUE = "#1976D2"
    ACCENT_BLUE = "#03A9F4"
    BG_WHITE = "#FFFFFF"
    BG_LIGHT = "#F5F9FC"
    BG_CARD = "#FAFBFD"
    TEXT_PRIMARY = "#1A1A1A"
    TEXT_SECONDARY = "#666666"
    TEXT_LIGHT = "#999999"
    SUCCESS = "#4CAF50"
    WARNING = "#FF9800"
    ERROR = "#F44336"
    INFO = "#2196F3"
    BORDER = "#E0E0E0"
    DIVIDER = "#EEEEEE"


class ModernMainWindowSimple:
    """简化版现代化主窗口"""
    
    def __init__(
        self,
        root,
        plan_manager: PlanManager,
        history_manager: HistoryManager,
        statistics_tracker: Optional[StatisticsTracker] = None
    ):
        """初始化"""
        self.root = root
        self.plan_manager = plan_manager
        self.history_manager = history_manager
        self.statistics_tracker = statistics_tracker
        
        self._selected_plan: Optional[StudyPlan] = None
        self._on_start_callback: Optional[Callable[[StudyPlan], None]] = None
        self._on_pause_callback: Optional[Callable[[], None]] = None
        self._on_resume_callback: Optional[Callable[[], None]] = None
        self._on_stop_callback: Optional[Callable[[], None]] = None
        self._session_active = False
        self._session_paused = False
        
        if isinstance(self.root, tk.Tk):
            self.root.title("Study Planner - 学习计划助手")
            self.root.geometry("950x900")
            self.root.configure(bg=ModernColors.BG_LIGHT)
        
        self._build_ui()

    
    def _build_ui(self):
        """构建UI - 简化版，不使用Canvas"""
        # 主容器
        main_container = tk.Frame(self.root, bg=ModernColors.BG_LIGHT)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 标题栏
        header = tk.Frame(main_container, bg=ModernColors.PRIMARY_BLUE, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="📚 Study Planner",
            bg=ModernColors.PRIMARY_BLUE,
            fg="white",
            font=("Microsoft YaHei UI", 18, "bold")
        )
        title.pack(side=tk.LEFT, padx=25, pady=15)
        
        subtitle = tk.Label(
            header,
            text="专注学习，高效成长",
            bg=ModernColors.PRIMARY_BLUE,
            fg="white",
            font=("Microsoft YaHei UI", 10)
        )
        subtitle.pack(side=tk.LEFT, padx=(0, 25))
        
        # 内容区域
        content_frame = tk.Frame(main_container, bg=ModernColors.BG_LIGHT)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        # 预设计划
        self._build_preset_section(content_frame)
        
        # 自定义计划
        self._build_custom_section(content_frame)
        
        # 历史和统计 - 简化为单列
        self._build_history_section(content_frame)
        
        if self.statistics_tracker:
            self._build_stats_section(content_frame)
        
        # 控制按钮
        self._build_controls(content_frame)
        
        # 错误标签
        self.error_label = tk.Label(
            content_frame,
            text="",
            bg=ModernColors.BG_LIGHT,
            fg=ModernColors.ERROR,
            font=("Microsoft YaHei UI", 9),
            wraplength=850
        )
        self.error_label.pack(pady=(5, 0))
