"""
现代化蓝白色主题UI - Study Planner

采用扁平化设计，蓝白配色方案，提供优雅的用户体验。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from study_planner.core.plans import StudyPlan, PlanManager
from study_planner.data.history import HistoryManager
from study_planner.data.statistics import StatisticsTracker
from study_planner.utils.validation import validate_numeric_input
from study_planner.utils.time_utils import format_duration


class ModernColors:
    """现代蓝白配色方案"""
    # 主色调 - 蓝色系
    PRIMARY_BLUE = "#2196F3"      # 主蓝色
    LIGHT_BLUE = "#64B5F6"        # 浅蓝色
    DARK_BLUE = "#1976D2"         # 深蓝色
    ACCENT_BLUE = "#03A9F4"       # 强调蓝色
    
    # 背景色
    BG_WHITE = "#FFFFFF"          # 纯白背景
    BG_LIGHT = "#F5F9FC"          # 浅蓝白背景
    BG_CARD = "#FAFBFD"           # 卡片背景
    
    # 文字颜色
    TEXT_PRIMARY = "#1A1A1A"      # 主文字
    TEXT_SECONDARY = "#666666"    # 次要文字
    TEXT_LIGHT = "#999999"        # 浅色文字
    
    # 状态颜色
    SUCCESS = "#4CAF50"           # 成功/学习
    WARNING = "#FF9800"           # 警告/暂停
    ERROR = "#F44336"             # 错误
    INFO = "#2196F3"              # 信息/休息
    
    # 边框和分隔线
    BORDER = "#E0E0E0"            # 边框颜色
    DIVIDER = "#EEEEEE"           # 分隔线


class ModernMainWindow:
    """现代化主窗口"""

    
    def __init__(
        self,
        root,
        plan_manager: PlanManager,
        history_manager: HistoryManager,
        statistics_tracker: Optional[StatisticsTracker] = None
    ):
        """初始化现代化主窗口"""
        self.root = root
        self.plan_manager = plan_manager
        self.history_manager = history_manager
        self.statistics_tracker = statistics_tracker
        
        # 当前选中的计划
        self._selected_plan: Optional[StudyPlan] = None
        
        # 回调函数
        self._on_start_callback: Optional[Callable[[StudyPlan], None]] = None
        self._on_pause_callback: Optional[Callable[[], None]] = None
        self._on_resume_callback: Optional[Callable[[], None]] = None
        self._on_stop_callback: Optional[Callable[[], None]] = None
        
        # UI状态
        self._session_active = False
        self._session_paused = False
        
        # 配置窗口
        if isinstance(self.root, tk.Tk):
            self.root.title("Study Planner - 学习计划助手")
            self.root.geometry("900x850")
            self.root.resizable(True, True)
            self.root.configure(bg=ModernColors.BG_LIGHT)
        
        # 配置样式
        self._configure_styles()
        
        # 构建UI
        self._build_ui()

    
    def _configure_styles(self):
        """配置现代化样式"""
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 配置Frame样式
        style.configure(
            "Card.TFrame",
            background=ModernColors.BG_CARD,
            relief="flat"
        )
        
        # 配置Label样式
        style.configure(
            "Title.TLabel",
            background=ModernColors.BG_LIGHT,
            foreground=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 16, "bold")
        )
        
        style.configure(
            "Subtitle.TLabel",
            background=ModernColors.BG_CARD,
            foreground=ModernColors.TEXT_SECONDARY,
            font=("Microsoft YaHei UI", 11, "bold")
        )
        
        style.configure(
            "Normal.TLabel",
            background=ModernColors.BG_CARD,
            foreground=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 10)
        )
        
        # 配置Button样式 - 主按钮
        style.configure(
            "Primary.TButton",
            background=ModernColors.PRIMARY_BLUE,
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("Microsoft YaHei UI", 10, "bold"),
            padding=(20, 10)
        )
        
        style.map(
            "Primary.TButton",
            background=[("active", ModernColors.DARK_BLUE), ("pressed", ModernColors.DARK_BLUE)]
        )

        
        # 配置Button样式 - 次要按钮
        style.configure(
            "Secondary.TButton",
            background=ModernColors.BG_WHITE,
            foreground=ModernColors.PRIMARY_BLUE,
            borderwidth=1,
            relief="solid",
            font=("Microsoft YaHei UI", 10),
            padding=(15, 8)
        )
        
        # 配置Button样式 - 预设按钮
        style.configure(
            "Preset.TButton",
            background=ModernColors.BG_WHITE,
            foreground=ModernColors.TEXT_PRIMARY,
            borderwidth=1,
            relief="solid",
            font=("Microsoft YaHei UI", 9),
            padding=(15, 12)
        )
        
        # 配置Entry样式
        style.configure(
            "Modern.TEntry",
            fieldbackground=ModernColors.BG_WHITE,
            borderwidth=1,
            relief="solid",
            padding=8
        )
        
        # 配置LabelFrame样式
        style.configure(
            "Card.TLabelframe",
            background=ModernColors.BG_CARD,
            borderwidth=0,
            relief="flat"
        )
        
        style.configure(
            "Card.TLabelframe.Label",
            background=ModernColors.BG_CARD,
            foreground=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 11, "bold")
        )

    
    def _build_ui(self):
        """构建现代化UI - 移除Canvas滚动，直接使用Frame"""
        # 主容器
        main_container = tk.Frame(self.root, bg=ModernColors.BG_LIGHT)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 标题栏
        self._build_header(main_container)
        
        # 内容区域 - 直接使用Frame，不用Canvas
        content_frame = tk.Frame(main_container, bg=ModernColors.BG_LIGHT)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        # 预设计划卡片
        self._build_preset_cards(content_frame)
        
        # 自定义计划卡片
        self._build_custom_card(content_frame)
        
        # 历史记录（简化为单列）
        self._build_history_card(content_frame)
        
        # 统计数据（如果有）
        if self.statistics_tracker:
            self._build_statistics_card(content_frame)
        
        # 控制按钮区域
        self._build_control_buttons(content_frame)
        
        # 错误提示标签
        self.error_label = tk.Label(
            content_frame,
            text="",
            bg=ModernColors.BG_LIGHT,
            fg=ModernColors.ERROR,
            font=("Microsoft YaHei UI", 10),
            wraplength=800
        )
        self.error_label.pack(pady=(10, 0))

    
    def _build_header(self, parent):
        """构建标题栏"""
        header = tk.Frame(parent, bg=ModernColors.PRIMARY_BLUE, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # 标题
        title = tk.Label(
            header,
            text="📚 Study Planner",
            bg=ModernColors.PRIMARY_BLUE,
            fg="white",
            font=("Microsoft YaHei UI", 20, "bold")
        )
        title.pack(side=tk.LEFT, padx=30, pady=20)
        
        # 副标题
        subtitle = tk.Label(
            header,
            text="专注学习，高效成长",
            bg=ModernColors.PRIMARY_BLUE,
            fg="white",
            font=("Microsoft YaHei UI", 11)
        )
        subtitle.pack(side=tk.LEFT, padx=(0, 30))

    
    def _build_preset_cards(self, parent):
        """构建预设计划卡片"""
        # 卡片容器
        card = self._create_card(parent, "⚡ 快速开始")
        card.pack(fill=tk.X, pady=(0, 15))
        
        # 预设按钮容器
        presets_container = tk.Frame(card, bg=ModernColors.BG_CARD)
        presets_container.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # 获取预设计划
        presets = self.plan_manager.get_preset_plans()
        
        # 为每个预设创建卡片式按钮
        for i, plan in enumerate(presets):
            preset_btn = self._create_preset_button(presets_container, plan)
            preset_btn.pack(side=tk.LEFT, padx=(0, 15) if i < len(presets)-1 else 0, fill=tk.BOTH, expand=True)
    
    def _create_preset_button(self, parent, plan: StudyPlan):
        """创建预设计划按钮 - 使用Button代替Frame"""
        # 图标映射
        icons = {
            "Pomodoro": "🍅",
            "Deep Focus": "🎯",
            "Light Review": "📖"
        }
        
        icon = icons.get(plan.name, "📝")
        
        # 按钮文本
        btn_text = f"{icon}\n{plan.name}\n{plan.study_minutes}分钟学习\n{plan.break_minutes}分钟休息"
        if plan.cycles > 1:
            btn_text += f"\n{plan.cycles}个循环"
        
        # 创建Button
        btn = tk.Button(
            parent,
            text=btn_text,
            command=lambda: self._select_preset(plan),
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=15,
            width=18,
            height=7,
            justify=tk.CENTER,
            highlightbackground=ModernColors.BORDER,
            highlightthickness=1,
            activebackground=ModernColors.BG_LIGHT,
            activeforeground=ModernColors.TEXT_PRIMARY
        )
        
        # 悬停效果
        def on_enter(e):
            btn.configure(
                bg=ModernColors.BG_LIGHT,
                highlightbackground=ModernColors.PRIMARY_BLUE,
                highlightthickness=2
            )
        
        def on_leave(e):
            btn.configure(
                bg=ModernColors.BG_WHITE,
                highlightbackground=ModernColors.BORDER,
                highlightthickness=1
            )
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn



    
    def _build_custom_card(self, parent):
        """构建自定义计划卡片"""
        card = self._create_card(parent, "✏️ 自定义计划")
        card.pack(fill=tk.X, pady=(0, 15))
        
        # 表单容器
        form_container = tk.Frame(card, bg=ModernColors.BG_CARD)
        form_container.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # 第一行：计划名称
        row1 = tk.Frame(form_container, bg=ModernColors.BG_CARD)
        row1.pack(fill=tk.X, pady=(0, 12))
        
        self._create_form_field(row1, "计划名称", "name_entry", "例如：考试冲刺", width=40)
        self.name_entry.insert(0, "自定义计划")
        
        # 第二行：学习时间和休息时间
        row2 = tk.Frame(form_container, bg=ModernColors.BG_CARD)
        row2.pack(fill=tk.X, pady=(0, 12))
        
        left_col = tk.Frame(row2, bg=ModernColors.BG_CARD)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self._create_form_field(left_col, "学习时间 (分钟)", "study_entry", "1-180", width=15)
        
        right_col = tk.Frame(row2, bg=ModernColors.BG_CARD)
        right_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_form_field(right_col, "休息时间 (分钟)", "break_entry", "1-180", width=15)
        
        # 第三行：循环次数和长休息
        row3 = tk.Frame(form_container, bg=ModernColors.BG_CARD)
        row3.pack(fill=tk.X, pady=(0, 15))
        
        left_col = tk.Frame(row3, bg=ModernColors.BG_CARD)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self._create_form_field(left_col, "循环次数", "cycles_entry", "≥1", width=15)
        self.cycles_entry.insert(0, "1")
        
        right_col = tk.Frame(row3, bg=ModernColors.BG_CARD)
        right_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_form_field(right_col, "长休息 (分钟)", "long_break_entry", "可选，0-180", width=15)
        self.long_break_entry.insert(0, "0")
        
        # 创建按钮
        self.create_btn = tk.Button(
            form_container,
            text="创建计划",
            bg=ModernColors.PRIMARY_BLUE,
            fg="white",
            font=("Microsoft YaHei UI", 11, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=12,
            command=self._create_custom_plan
        )
        self.create_btn.pack(pady=(5, 0))
        
        # 按钮悬停效果
        self.create_btn.bind("<Enter>", lambda e: self.create_btn.configure(bg=ModernColors.DARK_BLUE))
        self.create_btn.bind("<Leave>", lambda e: self.create_btn.configure(bg=ModernColors.PRIMARY_BLUE))

    
    def _create_form_field(self, parent, label_text, entry_name, placeholder, width=20):
        """创建表单字段"""
        # 标签
        label = tk.Label(
            parent,
            text=label_text,
            bg=ModernColors.BG_CARD,
            fg=ModernColors.TEXT_SECONDARY,
            font=("Microsoft YaHei UI", 9)
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # 输入框
        entry = tk.Entry(
            parent,
            width=width,
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 10),
            relief=tk.FLAT,
            highlightbackground=ModernColors.BORDER,
            highlightthickness=1,
            highlightcolor=ModernColors.PRIMARY_BLUE
        )
        entry.pack(fill=tk.X, ipady=8)
        
        # 保存引用
        setattr(self, entry_name, entry)
        
        return entry

    
    def _build_history_card(self, parent):
        """构建历史记录卡片 - 紧凑版"""
        card = self._create_card(parent, "📜 最近使用")
        card.pack(fill=tk.X, pady=(0, 10))
        
        # 列表容器 - 减小高度
        list_container = tk.Frame(card, bg=ModernColors.BG_WHITE)
        list_container.pack(fill=tk.X, padx=20, pady=(10, 10))
        
        # 创建Listbox - 减小高度
        self.history_listbox = tk.Listbox(
            list_container,
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 9),
            relief=tk.FLAT,
            highlightthickness=0,
            selectbackground=ModernColors.LIGHT_BLUE,
            selectforeground="white",
            height=3
        )
        self.history_listbox.pack(fill=tk.X)
        
        # 加载按钮 - 更小
        load_btn = tk.Button(
            card,
            text="加载选中的配置",
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.PRIMARY_BLUE,
            font=("Microsoft YaHei UI", 9),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=6,
            command=self._load_from_history,
            highlightbackground=ModernColors.BORDER,
            highlightthickness=1
        )
        load_btn.pack(padx=20, pady=(0, 10))
        
        # 刷新历史记录
        self._refresh_history()

    
    def _build_statistics_card(self, parent):
        """构建统计数据卡片 - 紧凑版"""
        card = self._create_card(parent, "📊 学习统计")
        card.pack(fill=tk.X, pady=(0, 10))
        
        # 统计容器 - 使用网格布局
        stats_container = tk.Frame(card, bg=ModernColors.BG_CARD)
        stats_container.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        # 统计项 - 2x2网格
        stats_data = [
            ("今日学习", "today_time_label", "0 分钟", ModernColors.SUCCESS),
            ("本周学习", "week_time_label", "0 分钟", ModernColors.INFO),
            ("完成次数", "completed_label", "0", ModernColors.PRIMARY_BLUE),
            ("中断次数", "interrupted_label", "0", ModernColors.WARNING)
        ]
        
        for i, (title, attr_name, default_value, color) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            stat_item = tk.Frame(stats_container, bg=ModernColors.BG_WHITE, highlightbackground=ModernColors.BORDER, highlightthickness=1)
            stat_item.grid(row=row, column=col, padx=(0, 10) if col == 0 else 0, pady=(0, 10) if row == 0 else 0, sticky="ew")
            
            # 标题
            title_label = tk.Label(
                stat_item,
                text=title,
                bg=ModernColors.BG_WHITE,
                fg=ModernColors.TEXT_SECONDARY,
                font=("Microsoft YaHei UI", 8)
            )
            title_label.pack(anchor=tk.W, padx=12, pady=(8, 3))
            
            # 数值
            value_label = tk.Label(
                stat_item,
                text=default_value,
                bg=ModernColors.BG_WHITE,
                fg=color,
                font=("Microsoft YaHei UI", 14, "bold")
            )
            value_label.pack(anchor=tk.W, padx=12, pady=(0, 8))
            
            # 保存引用
            setattr(self, attr_name, value_label)
        
        # 配置网格权重
        stats_container.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        
        # 初始化统计数据
        self._update_statistics_display()

    
    def _build_control_buttons(self, parent):
        """构建控制按钮"""
        controls_container = tk.Frame(parent, bg=ModernColors.BG_LIGHT)
        controls_container.pack(fill=tk.X, pady=(15, 0))
        
        # 按钮配置
        buttons_config = [
            ("开始学习", "start_btn", self._on_start_clicked, ModernColors.SUCCESS, "white"),
            ("暂停", "pause_btn", self._on_pause_clicked, ModernColors.WARNING, "white"),
            ("继续", "resume_btn", self._on_resume_clicked, ModernColors.INFO, "white"),
            ("停止", "stop_btn", self._on_stop_clicked, ModernColors.ERROR, "white")
        ]
        
        for i, (text, attr_name, command, bg_color, fg_color) in enumerate(buttons_config):
            # 初始状态：只有开始按钮启用（如果有选中的计划）
            initial_state = tk.NORMAL if attr_name == "start_btn" else tk.DISABLED
            
            btn = tk.Button(
                controls_container,
                text=text,
                bg=bg_color,
                fg=fg_color,
                font=("Microsoft YaHei UI", 11, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                padx=25,
                pady=15,
                command=command,
                state=initial_state
            )
            btn.pack(side=tk.LEFT, padx=(0, 15) if i < len(buttons_config)-1 else 0, fill=tk.X, expand=True)
            
            # 保存引用
            setattr(self, attr_name, btn)
            
            # 悬停效果
            btn.bind("<Enter>", lambda e, b=btn, c=bg_color: self._on_button_hover(b, c, True))
            btn.bind("<Leave>", lambda e, b=btn, c=bg_color: self._on_button_hover(b, c, False))
        
        # 注意：开始按钮初始应该是禁用的，直到用户选择了计划
        # 但为了测试，我们先让它启用
        # self.start_btn.configure(state=tk.DISABLED)
    
    def _on_button_hover(self, button, original_color, is_hover):
        """按钮悬停效果"""
        if button['state'] == tk.DISABLED:
            return
        
        if is_hover:
            # 颜色变暗
            button.configure(bg=self._darken_color(original_color))
        else:
            button.configure(bg=original_color)
    
    def _darken_color(self, hex_color):
        """使颜色变暗"""
        # 简单的变暗算法
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f'#{r:02x}{g:02x}{b:02x}'

    
    def _create_card(self, parent, title):
        """创建卡片容器"""
        # 卡片外框
        card_outer = tk.Frame(parent, bg=ModernColors.BG_LIGHT)
        
        # 卡片内容
        card = tk.Frame(
            card_outer,
            bg=ModernColors.BG_CARD,
            highlightbackground=ModernColors.BORDER,
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 卡片标题
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
        
        # 分隔线
        separator = tk.Frame(card, bg=ModernColors.DIVIDER, height=1)
        separator.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        return card

    
    # ========== 事件处理方法 ==========
    
    def _select_preset(self, plan: StudyPlan):
        """选择预设计划"""
        print(f"\n[DEBUG] 点击了预设计划: {plan.name}")  # 调试输出
        
        if self._session_active and not self._can_modify():
            self._show_error("无法在活动会话期间更改计划")
            print("[DEBUG] 会话活动中，无法更改计划")
            return
        
        self._selected_plan = plan
        self._clear_error()
        self.start_btn.config(state=tk.NORMAL)
        print(f"[DEBUG] 计划已选中，开始按钮已启用")
        
        # 更新表单显示预设值
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, plan.name)
        self.study_entry.delete(0, tk.END)
        self.study_entry.insert(0, str(plan.study_minutes))
        self.break_entry.delete(0, tk.END)
        self.break_entry.insert(0, str(plan.break_minutes))
        self.cycles_entry.delete(0, tk.END)
        self.cycles_entry.insert(0, str(plan.cycles))
        self.long_break_entry.delete(0, tk.END)
        self.long_break_entry.insert(0, str(plan.long_break_minutes))
        print(f"[DEBUG] 表单已更新: 学习{plan.study_minutes}分钟, 休息{plan.break_minutes}分钟")
    
    def _create_custom_plan(self):
        """创建自定义计划"""
        if self._session_active and not self._can_modify():
            self._show_error("无法在活动会话期间更改计划")
            return
        
        # 获取并验证输入
        name = self.name_entry.get().strip()
        if not name:
            self._show_error("请输入计划名称")
            return
        
        # 验证学习时间
        study_str = self.study_entry.get().strip()
        study_min = validate_numeric_input(study_str)
        if study_min is None:
            self._show_error("请输入有效的学习时间数字")
            return
        
        # 验证休息时间
        break_str = self.break_entry.get().strip()
        break_min = validate_numeric_input(break_str)
        if break_min is None:
            self._show_error("请输入有效的休息时间数字")
            return
        
        # 验证循环次数
        cycles_str = self.cycles_entry.get().strip()
        cycles = validate_numeric_input(cycles_str)
        if cycles is None:
            self._show_error("请输入有效的循环次数")
            return
        
        # 验证长休息时间
        long_break_str = self.long_break_entry.get().strip()
        try:
            long_break_min = int(long_break_str)
            if long_break_min < 0:
                self._show_error("长休息时间不能为负数")
                return
        except ValueError:
            self._show_error("请输入有效的长休息时间数字")
            return
        
        # 创建计划
        try:
            plan = self.plan_manager.create_custom_plan(
                name=name,
                study_min=study_min,
                break_min=break_min,
                cycles=cycles,
                long_break_min=long_break_min
            )
            
            self._selected_plan = plan
            self._clear_error()
            self.start_btn.config(state=tk.NORMAL)
            
        except ValueError as e:
            self._show_error(str(e))

    
    def _refresh_history(self):
        """刷新历史记录列表"""
        self.history_listbox.delete(0, tk.END)
        
        recent_plans = self.history_manager.get_recent(5)
        for plan in recent_plans:
            display_text = f"{plan.name}: {plan.study_minutes}分钟/{plan.break_minutes}分钟"
            if plan.cycles > 1:
                display_text += f", {plan.cycles}个循环"
            if plan.long_break_minutes > 0:
                display_text += f", {plan.long_break_minutes}分钟长休息"
            
            self.history_listbox.insert(tk.END, display_text)
    
    def _load_from_history(self):
        """从历史记录加载配置"""
        if self._session_active and not self._can_modify():
            self._show_error("无法在活动会话期间更改计划")
            return
        
        selection = self.history_listbox.curselection()
        if not selection:
            self._show_error("请从历史记录中选择一个配置")
            return
        
        index = selection[0]
        recent_plans = self.history_manager.get_recent(5)
        
        if index < len(recent_plans):
            plan = recent_plans[index]
            self._select_preset(plan)
    
    def _on_start_clicked(self):
        """开始按钮点击"""
        if not self._selected_plan:
            self._show_error("请先选择或创建一个计划")
            return
        
        if self._on_start_callback:
            self._on_start_callback(self._selected_plan)
    
    def _on_pause_clicked(self):
        """暂停按钮点击"""
        if self._on_pause_callback:
            self._on_pause_callback()
    
    def _on_resume_clicked(self):
        """继续按钮点击"""
        if self._on_resume_callback:
            self._on_resume_callback()
    
    def _on_stop_clicked(self):
        """停止按钮点击"""
        if self._on_stop_callback:
            self._on_stop_callback()
    
    def _show_error(self, message: str):
        """显示错误消息"""
        self.error_label.config(text=message)
    
    def _clear_error(self):
        """清除错误消息"""
        self.error_label.config(text="")
    
    def _can_modify(self) -> bool:
        """检查是否可以修改计划"""
        return not self._session_active
    
    def _update_statistics_display(self):
        """更新统计数据显示"""
        if not self.statistics_tracker:
            return
        
        # 获取统计数据
        today_minutes = self.statistics_tracker.get_today_study_time()
        week_minutes = self.statistics_tracker.get_week_study_time()
        completed_count = self.statistics_tracker.get_completed_pomodoros()
        interrupted_count = self.statistics_tracker.get_interrupted_count()
        
        # 更新标签
        self.today_time_label.config(text=format_duration(today_minutes))
        self.week_time_label.config(text=format_duration(week_minutes))
        self.completed_label.config(text=str(completed_count))
        self.interrupted_label.config(text=str(interrupted_count))

    
    # ========== 公共方法 ==========
    
    def set_session_active(self, active: bool):
        """设置会话活动状态"""
        self._session_active = active
        
        if active:
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.resume_btn.config(state=tk.DISABLED)
            self.create_btn.config(state=tk.DISABLED)
        else:
            self.start_btn.config(state=tk.NORMAL if self._selected_plan else tk.DISABLED)
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.resume_btn.config(state=tk.DISABLED)
            self.create_btn.config(state=tk.NORMAL)
            
            # 刷新历史记录和统计数据
            self._refresh_history()
            self._update_statistics_display()
    
    def set_session_paused(self, paused: bool):
        """设置会话暂停状态"""
        self._session_paused = paused
        
        if paused:
            self.pause_btn.config(state=tk.DISABLED)
            self.resume_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.pause_btn.config(state=tk.NORMAL)
            self.resume_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
    
    def set_start_callback(self, callback: Callable[[StudyPlan], None]):
        """设置开始回调"""
        self._on_start_callback = callback
    
    def set_pause_callback(self, callback: Callable[[], None]):
        """设置暂停回调"""
        self._on_pause_callback = callback
    
    def set_resume_callback(self, callback: Callable[[], None]):
        """设置继续回调"""
        self._on_resume_callback = callback
    
    def set_stop_callback(self, callback: Callable[[], None]):
        """设置停止回调"""
        self._on_stop_callback = callback
