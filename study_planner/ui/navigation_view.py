"""
导航视图 - 带有Home、Analysis、History三个页面的主界面
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from study_planner.core.plans import StudyPlan, PlanManager
from study_planner.data.history import HistoryManager
from study_planner.data.statistics import StatisticsTracker
from study_planner.ui.modern_main_view import ModernMainWindow, ModernColors


class NavigationView:
    """带导航的主视图"""
    
    def __init__(
        self,
        root,
        plan_manager: PlanManager,
        history_manager: HistoryManager,
        statistics_tracker: Optional[StatisticsTracker] = None
    ):
        self.root = root
        self.plan_manager = plan_manager
        self.history_manager = history_manager
        self.statistics_tracker = statistics_tracker
        
        # 当前页面
        self.current_page = "home"
        
        # 回调函数
        self._on_start_callback: Optional[Callable[[StudyPlan], None]] = None
        self._on_pause_callback: Optional[Callable[[], None]] = None
        self._on_resume_callback: Optional[Callable[[], None]] = None
        self._on_stop_callback: Optional[Callable[[], None]] = None
        
        # 配置窗口
        if isinstance(self.root, tk.Tk):
            self.root.title("Study Planner - 学习计划助手")
            self.root.geometry("1100x900")
            self.root.resizable(True, True)
            self.root.configure(bg=ModernColors.BG_LIGHT)
        
        # 构建UI
        self._build_ui()
    
    def _build_ui(self):
        """构建UI"""
        # 主容器
        main_container = tk.Frame(self.root, bg=ModernColors.BG_LIGHT)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 标题栏和导航
        self._build_header_with_nav(main_container)
        
        # 页面容器
        self.pages_container = tk.Frame(main_container, bg=ModernColors.BG_LIGHT)
        self.pages_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个页面
        self._create_pages()
        
        # 显示首页
        self._show_page("home")
    
    def _build_header_with_nav(self, parent):
        """构建带导航按钮的标题栏"""
        header = tk.Frame(parent, bg=ModernColors.PRIMARY_BLUE, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # 左侧：标题
        left_frame = tk.Frame(header, bg=ModernColors.PRIMARY_BLUE)
        left_frame.pack(side=tk.LEFT, padx=30, pady=20)
        
        title = tk.Label(
            left_frame,
            text="📚 Study Planner",
            bg=ModernColors.PRIMARY_BLUE,
            fg="white",
            font=("Microsoft YaHei UI", 20, "bold")
        )
        title.pack(side=tk.LEFT)
        
        # 右侧：导航按钮
        nav_frame = tk.Frame(header, bg=ModernColors.PRIMARY_BLUE)
        nav_frame.pack(side=tk.RIGHT, padx=30, pady=20)
        
        # 导航按钮配置
        nav_buttons = [
            ("🏠 Home", "home"),
            ("📊 Analysis", "analysis"),
            ("📜 History", "history")
        ]
        
        self.nav_buttons = {}
        for text, page_name in nav_buttons:
            btn = tk.Button(
                nav_frame,
                text=text,
                bg=ModernColors.DARK_BLUE if page_name == "home" else ModernColors.PRIMARY_BLUE,
                fg="white",
                font=("Microsoft YaHei UI", 11, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                padx=20,
                pady=10,
                command=lambda p=page_name: self._show_page(p)
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.nav_buttons[page_name] = btn
            
            # 悬停效果
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=ModernColors.DARK_BLUE))
            btn.bind("<Leave>", lambda e, b=btn, p=page_name: 
                    b.configure(bg=ModernColors.DARK_BLUE if self.current_page == p else ModernColors.PRIMARY_BLUE))
    
    def _create_pages(self):
        """创建所有页面"""
        self.pages = {}
        
        # Home页面 - 使用现有的ModernMainWindow
        home_frame = tk.Frame(self.pages_container, bg=ModernColors.BG_LIGHT)
        self.home_page = ModernMainWindow(
            home_frame,
            self.plan_manager,
            self.history_manager,
            self.statistics_tracker
        )
        self.pages["home"] = home_frame
        
        # Analysis页面
        analysis_frame = tk.Frame(self.pages_container, bg=ModernColors.BG_LIGHT)
        self._build_analysis_page(analysis_frame)
        self.pages["analysis"] = analysis_frame
        
        # History页面
        history_frame = tk.Frame(self.pages_container, bg=ModernColors.BG_LIGHT)
        self._build_history_page(history_frame)
        self.pages["history"] = history_frame
    
    def _show_page(self, page_name: str):
        """显示指定页面"""
        # 隐藏所有页面
        for page in self.pages.values():
            page.pack_forget()
        
        # 显示指定页面
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_name
            
            # 更新导航按钮状态
            for name, btn in self.nav_buttons.items():
                if name == page_name:
                    btn.configure(bg=ModernColors.DARK_BLUE)
                else:
                    btn.configure(bg=ModernColors.PRIMARY_BLUE)
            
            # 刷新页面数据
            if page_name == "analysis":
                self._refresh_analysis_page()
            elif page_name == "history":
                self._refresh_history_page()
    
    def _build_analysis_page(self, parent):
        """构建分析页面"""
        # 页面标题
        title_frame = tk.Frame(parent, bg=ModernColors.BG_LIGHT)
        title_frame.pack(fill=tk.X, padx=30, pady=20)
        
        title = tk.Label(
            title_frame,
            text="📊 学习分析",
            bg=ModernColors.BG_LIGHT,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 18, "bold")
        )
        title.pack(anchor=tk.W)
        
        # 内容区域
        content = tk.Frame(parent, bg=ModernColors.BG_LIGHT)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # 本周学习统计卡片
        self._build_week_stats_card(content)
        
        # 计划使用统计卡片
        self._build_plan_stats_card(content)
    
    def _build_week_stats_card(self, parent):
        """构建本周学习统计卡片"""
        card = self._create_card(parent, "📅 本周学习统计")
        card.pack(fill=tk.X, pady=(0, 15))
        
        # 统计容器
        stats_container = tk.Frame(card, bg=ModernColors.BG_CARD)
        stats_container.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # 统计项
        stats_items = [
            ("总学习时间", "week_total_time", "0 分钟", ModernColors.SUCCESS),
            ("学习次数", "week_session_count", "0", ModernColors.INFO),
            ("完成次数", "week_completed_count", "0", ModernColors.PRIMARY_BLUE),
            ("中断次数", "week_interrupted_count", "0", ModernColors.WARNING)
        ]
        
        for i, (title, attr_name, default_value, color) in enumerate(stats_items):
            row = i // 2
            col = i % 2
            
            stat_item = tk.Frame(stats_container, bg=ModernColors.BG_WHITE, 
                               highlightbackground=ModernColors.BORDER, highlightthickness=1)
            stat_item.grid(row=row, column=col, padx=(0, 10) if col == 0 else 0, 
                          pady=(0, 10) if row == 0 else 0, sticky="ew")
            
            # 标题
            title_label = tk.Label(
                stat_item,
                text=title,
                bg=ModernColors.BG_WHITE,
                fg=ModernColors.TEXT_SECONDARY,
                font=("Microsoft YaHei UI", 10)
            )
            title_label.pack(anchor=tk.W, padx=15, pady=(12, 5))
            
            # 数值
            value_label = tk.Label(
                stat_item,
                text=default_value,
                bg=ModernColors.BG_WHITE,
                fg=color,
                font=("Microsoft YaHei UI", 20, "bold")
            )
            value_label.pack(anchor=tk.W, padx=15, pady=(0, 12))
            
            setattr(self, attr_name, value_label)
        
        stats_container.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
    
    def _build_plan_stats_card(self, parent):
        """构建计划使用统计卡片"""
        card = self._create_card(parent, "🎯 计划使用统计")
        card.pack(fill=tk.X, pady=(0, 15))
        
        # 统计容器
        stats_container = tk.Frame(card, bg=ModernColors.BG_CARD)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        # 最常用计划
        most_used_frame = tk.Frame(stats_container, bg=ModernColors.BG_WHITE,
                                   highlightbackground=ModernColors.BORDER, highlightthickness=1)
        most_used_frame.pack(fill=tk.X, pady=(0, 10))
        
        most_used_title = tk.Label(
            most_used_frame,
            text="最常用的计划",
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.TEXT_SECONDARY,
            font=("Microsoft YaHei UI", 10)
        )
        most_used_title.pack(anchor=tk.W, padx=15, pady=(12, 5))
        
        self.most_used_plan_label = tk.Label(
            most_used_frame,
            text="暂无数据",
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.PRIMARY_BLUE,
            font=("Microsoft YaHei UI", 16, "bold")
        )
        self.most_used_plan_label.pack(anchor=tk.W, padx=15, pady=(0, 12))
        
        # 总学习时间
        total_time_frame = tk.Frame(stats_container, bg=ModernColors.BG_WHITE,
                                    highlightbackground=ModernColors.BORDER, highlightthickness=1)
        total_time_frame.pack(fill=tk.X)
        
        total_time_title = tk.Label(
            total_time_frame,
            text="总学习时间",
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.TEXT_SECONDARY,
            font=("Microsoft YaHei UI", 10)
        )
        total_time_title.pack(anchor=tk.W, padx=15, pady=(12, 5))
        
        self.total_time_label = tk.Label(
            total_time_frame,
            text="0 分钟",
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.SUCCESS,
            font=("Microsoft YaHei UI", 16, "bold")
        )
        self.total_time_label.pack(anchor=tk.W, padx=15, pady=(0, 12))
    
    def _build_history_page(self, parent):
        """构建历史页面"""
        # 页面标题
        title_frame = tk.Frame(parent, bg=ModernColors.BG_LIGHT)
        title_frame.pack(fill=tk.X, padx=30, pady=20)
        
        title = tk.Label(
            title_frame,
            text="📜 学习历史",
            bg=ModernColors.BG_LIGHT,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 18, "bold")
        )
        title.pack(anchor=tk.W)
        
        # 内容区域
        content = tk.Frame(parent, bg=ModernColors.BG_LIGHT)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # 历史记录卡片
        card = self._create_card(content, "运行记录")
        card.pack(fill=tk.BOTH, expand=True)
        
        # 表格容器
        table_container = tk.Frame(card, bg=ModernColors.BG_WHITE)
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        # 创建Treeview表格
        columns = ("plan_name", "study_time", "break_time", "cycles", "timestamp")
        self.history_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=15
        )
        
        # 设置列标题
        self.history_tree.heading("plan_name", text="计划名称")
        self.history_tree.heading("study_time", text="学习时间")
        self.history_tree.heading("break_time", text="休息时间")
        self.history_tree.heading("cycles", text="循环次数")
        self.history_tree.heading("timestamp", text="使用时间")
        
        # 设置列宽
        self.history_tree.column("plan_name", width=200)
        self.history_tree.column("study_time", width=100)
        self.history_tree.column("break_time", width=100)
        self.history_tree.column("cycles", width=100)
        self.history_tree.column("timestamp", width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Run Again按钮
        btn_frame = tk.Frame(card, bg=ModernColors.BG_CARD)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        run_again_btn = tk.Button(
            btn_frame,
            text="▶️ Run Again",
            bg=ModernColors.SUCCESS,
            fg="white",
            font=("Microsoft YaHei UI", 11, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=25,
            pady=12,
            command=self._run_again_selected
        )
        run_again_btn.pack(side=tk.LEFT)
        
        # 悬停效果
        run_again_btn.bind("<Enter>", lambda e: run_again_btn.configure(bg=self._darken_color(ModernColors.SUCCESS)))
        run_again_btn.bind("<Leave>", lambda e: run_again_btn.configure(bg=ModernColors.SUCCESS))
    
    def _create_card(self, parent, title):
        """创建卡片容器"""
        card_outer = tk.Frame(parent, bg=ModernColors.BG_LIGHT)
        
        card = tk.Frame(
            card_outer,
            bg=ModernColors.BG_CARD,
            highlightbackground=ModernColors.BORDER,
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        title_frame = tk.Frame(card, bg=ModernColors.BG_CARD)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 5))
        
        title_label = tk.Label(
            title_frame,
            text=title,
            bg=ModernColors.BG_CARD,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 12, "bold")
        )
        title_label.pack(anchor=tk.W)
        
        separator = tk.Frame(card, bg=ModernColors.DIVIDER, height=1)
        separator.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        return card
    
    def _darken_color(self, hex_color):
        """使颜色变暗"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _refresh_analysis_page(self):
        """刷新分析页面数据"""
        if not self.statistics_tracker:
            return
        
        # 获取本周统计数据
        from study_planner.utils.time_utils import format_duration
        
        week_time = self.statistics_tracker.get_week_study_time()
        self.week_total_time.config(text=format_duration(week_time))
        
        # 获取本周会话数据
        from datetime import datetime, timedelta
        week_start = self._get_week_start()
        
        # 从统计数据中获取本周的完成和中断次数
        stats_data = self.statistics_tracker._stats
        week_key = week_start.isoformat()
        
        if week_key in stats_data.get("weekly", {}):
            week_data = stats_data["weekly"][week_key]
            completed = week_data.get("completed_pomodoros", 0)
            self.week_completed_count.config(text=str(completed))
        else:
            self.week_completed_count.config(text="0")
        
        # 计算本周总会话数和中断数
        total_sessions = 0
        interrupted = 0
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_key = day.isoformat()
            if day_key in stats_data.get("daily", {}):
                day_data = stats_data["daily"][day_key]
                total_sessions += day_data.get("completed_sessions", 0)
                interrupted += day_data.get("interrupted_sessions", 0)
        
        self.week_session_count.config(text=str(total_sessions))
        self.week_interrupted_count.config(text=str(interrupted))
        
        # 获取最常用的计划
        recent_plans = self.history_manager.get_recent(100)
        if recent_plans:
            plan_counts = {}
            total_time = 0
            
            for plan in recent_plans:
                plan_name = plan.name
                if plan_name not in plan_counts:
                    plan_counts[plan_name] = 0
                plan_counts[plan_name] += 1
                total_time += plan.study_minutes * plan.cycles
            
            # 找出最常用的计划
            most_used = max(plan_counts.items(), key=lambda x: x[1])
            self.most_used_plan_label.config(text=f"{most_used[0]} ({most_used[1]}次)")
            self.total_time_label.config(text=format_duration(total_time))
        else:
            self.most_used_plan_label.config(text="暂无数据")
            self.total_time_label.config(text="0 分钟")
    
    def _refresh_history_page(self):
        """刷新历史页面数据"""
        # 清空现有数据
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # 直接访问历史管理器的内部数据以获取时间戳
        history_entries = self.history_manager._history[:50]
        
        # 添加到表格
        for entry in history_entries:
            from study_planner.core.plans import StudyPlan
            from datetime import datetime
            
            plan = StudyPlan.from_dict(entry["plan"])
            timestamp_str = entry.get("timestamp", "")
            
            # 格式化时间戳
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = "最近使用"
            
            self.history_tree.insert("", tk.END, values=(
                plan.name,
                f"{plan.study_minutes} 分钟",
                f"{plan.break_minutes} 分钟",
                plan.cycles,
                formatted_time
            ))
    
    def _run_again_selected(self):
        """运行选中的历史记录"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        # 获取选中的项的索引
        item = selection[0]
        item_index = self.history_tree.index(item)
        
        # 从历史记录中获取对应的计划
        history_entries = self.history_manager._history[:50]
        if item_index < len(history_entries):
            from study_planner.core.plans import StudyPlan
            
            entry = history_entries[item_index]
            plan = StudyPlan.from_dict(entry["plan"])
            
            # 切换到Home页面
            self._show_page("home")
            
            # 选择该计划
            self.home_page._select_preset(plan)
            
            # 如果设置了开始回调，自动开始
            if self._on_start_callback:
                self._on_start_callback(plan)
    
    def _get_week_start(self):
        """获取本周开始日期（周一）"""
        from datetime import datetime, timedelta
        today = datetime.now().date()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        return week_start
    
    # ========== 公共方法 - 转发到home_page ==========
    
    def set_session_active(self, active: bool):
        """设置会话活动状态"""
        self.home_page.set_session_active(active)
    
    def set_session_paused(self, paused: bool):
        """设置会话暂停状态"""
        self.home_page.set_session_paused(paused)
    
    def set_start_callback(self, callback: Callable[[StudyPlan], None]):
        """设置开始回调"""
        self._on_start_callback = callback
        self.home_page.set_start_callback(callback)
    
    def set_pause_callback(self, callback: Callable[[], None]):
        """设置暂停回调"""
        self._on_pause_callback = callback
        self.home_page.set_pause_callback(callback)
    
    def set_resume_callback(self, callback: Callable[[], None]):
        """设置继续回调"""
        self._on_resume_callback = callback
        self.home_page.set_resume_callback(callback)
    
    def set_stop_callback(self, callback: Callable[[], None]):
        """设置停止回调"""
        self._on_stop_callback = callback
        self.home_page.set_stop_callback(callback)
    
    def _show_error(self, message: str):
        """显示错误消息"""
        self.home_page._show_error(message)
