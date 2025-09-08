# -*- coding: utf-8 -*-
"""
Maya烘焙命名工具GUI界面
适用于Maya 2023及以前版本
作者: liudan
邮箱: 3236296040@qq.com
"""

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from maya_baking_renamer import MayaBakingRenamer

try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from shiboken2 import wrapInstance
except ImportError:
    try:
        from PySide.QtGui import *
        from PySide.QtCore import *
        from shiboken import wrapInstance
    except ImportError:
        try:
            from PyQt4.QtGui import *
            from PyQt4.QtCore import *
            from sip import wrapinstance as wrapInstance
        except ImportError:
            print("Error: No Qt bindings found. GUI cannot be loaded.")
            raise

def get_maya_main_window():
    """
    获取Maya主窗口
    
    Returns:
        QWidget: Maya主窗口对象
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return wrapInstance(int(main_window_ptr), QWidget)
    return None

class MaterialConfigDialog(QDialog):
    """
    材质配置对话框
    """
    def __init__(self, parent=None, suffix="", color=(1, 0, 0), transparency=0, enabled=True):
        super(MaterialConfigDialog, self).__init__(parent)
        self.setWindowTitle("材质配置")
        self.setModal(True)
        self.resize(350, 250)
        
        # 设置字体
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        
        # 创建界面元素
        layout = QVBoxLayout()
        
        # 后缀名输入
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("后缀名:"))
        self.suffix_input = QLineEdit(suffix)
        self.suffix_input.setPlaceholderText("如: _low, _high, _cage")
        suffix_layout.addWidget(self.suffix_input)
        layout.addLayout(suffix_layout)
        
        # 颜色选择
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("颜色:"))
        self.color_combo = QComboBox()
        self.color_options = [
            ("红色", (1, 0, 0)),
            ("绿色", (0, 1, 0)),
            ("蓝色", (0, 0, 1)),
            ("黄色", (1, 1, 0)),
            ("紫色", (1, 0, 1)),
            ("青色", (0, 1, 1)),
            ("橙色", (1, 0.5, 0))
        ]
        
        for name, rgb in self.color_options:
            self.color_combo.addItem(name)
            
        # 设置当前颜色
        for i, (name, rgb) in enumerate(self.color_options):
            if rgb == tuple(color):
                self.color_combo.setCurrentIndex(i)
                break
                
        color_layout.addWidget(self.color_combo)
        layout.addLayout(color_layout)
        
        # 透明度设置
        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(QLabel("透明度:"))
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(0, 100)
        self.transparency_slider.setValue(int(transparency))
        self.transparency_label = QLabel(f"{int(transparency)}%")
        self.transparency_label.setMinimumWidth(40)
        transparency_layout.addWidget(self.transparency_slider)
        transparency_layout.addWidget(self.transparency_label)
        layout.addLayout(transparency_layout)
        
        # 启用状态
        self.enabled_check = QCheckBox("启用此配置")
        self.enabled_check.setChecked(enabled)
        layout.addWidget(self.enabled_check)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        
        # 设置按钮样式
        button_style = "QPushButton { padding: 8px 16px; font-size: 12px; min-height: 28px; }"
        self.ok_btn.setStyleSheet(button_style + "QPushButton { background-color: #4CAF50; color: white; }")
        self.cancel_btn.setStyleSheet(button_style + "QPushButton { background-color: #f44336; color: white; }")
        
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.transparency_slider.valueChanged.connect(self.update_transparency_label)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def update_transparency_label(self, value):
        """
        更新透明度标签
        """
        self.transparency_label.setText(f"{value}%")
        
    def get_config(self):
        """
        获取配置信息
        """
        suffix = self.suffix_input.text().strip()
        if not suffix.startswith('_'):
            suffix = '_' + suffix
            
        color = self.color_options[self.color_combo.currentIndex()][1]
        transparency = self.transparency_slider.value()
        enabled = self.enabled_check.isChecked()
        
        return suffix, color, transparency, enabled

class MayaBakingRenamerGUI(QDialog):
    """
    Maya烘焙命名工具GUI界面类
    """
    
    def __init__(self, parent=None):
        """
        初始化GUI界面
        
        Args:
            parent (QWidget, optional): 父窗口
        """
        if parent is None:
            parent = get_maya_main_window()
            
        super(MayaBakingRenamerGUI, self).__init__(parent)
        
        # 初始化重命名工具
        self.renamer = MayaBakingRenamer()
        
        # 设置窗口属性
        self.setWindowTitle("Maya烘焙命名工具 v2.0")
        self.setWindowFlags(Qt.Window)
        self.setMinimumSize(500, 700)
        self.resize(550, 800)
        
        # 设置全局字体
        font = QFont()
        font.setPointSize(10)  # 增大字体大小
        self.setFont(font)
        
        # 创建界面
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
        # 更新界面状态
        self.update_ui()
        
        # 刷新材质配置列表
        self.refresh_material_config_list()
    
    def create_widgets(self):
        """
        创建界面控件
        """
        # 标题标签
        self.title_label = QLabel("伏羲Maya烘焙命名工具")
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.title_label.setFont(font)
        
        # 选择信息组
        self.selection_group = QGroupBox("当前选择")
        self.selection_list = QListWidget()
        self.selection_list.setMaximumHeight(120)
        self.selection_list.setFont(QFont("Arial", 9))
        self.refresh_selection_btn = QPushButton("刷新选择")
        
        # 快速操作组
        self.quick_group = QGroupBox("快速操作")
        self.auto_rename_btn = QPushButton("自动重命名模式")
        self.low_suffix_btn = QPushButton("添加 _low 后缀")
        self.high_suffix_btn = QPushButton("添加 _high 后缀")
        
        # 统一按钮样式
        compact_button_style = "QPushButton { padding: 8px 16px; font-size: 12px; min-height: 28px; }"
        self.auto_rename_btn.setStyleSheet(compact_button_style + "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.low_suffix_btn.setStyleSheet(compact_button_style)
        self.high_suffix_btn.setStyleSheet(compact_button_style)
        
        # 自定义后缀组
        self.custom_group = QGroupBox("自定义后缀")
        self.custom_suffix_input = QLineEdit()
        self.custom_suffix_input.setPlaceholderText("输入自定义后缀 (如: cage, bake)")
        self.custom_suffix_btn = QPushButton("应用自定义后缀")
        
        # 预设后缀按钮
        self.preset_cage_btn = QPushButton("_cage")
        self.preset_bake_btn = QPushButton("_bake")
        self.preset_lp_btn = QPushButton("_LP")
        self.preset_hp_btn = QPushButton("_HP")
        
        # 应用统一样式到自定义后缀按钮
        small_button_style = "QPushButton { padding: 6px 12px; font-size: 11px; min-width: 60px; min-height: 24px; }"
        self.custom_suffix_btn.setStyleSheet(compact_button_style)
        self.preset_cage_btn.setStyleSheet(small_button_style)
        self.preset_bake_btn.setStyleSheet(small_button_style)
        self.preset_lp_btn.setStyleSheet(small_button_style)
        self.preset_hp_btn.setStyleSheet(small_button_style)
        
        # 批量操作组
        self.batch_group = QGroupBox("批量操作")
        self.batch_low_btn = QPushButton("批量添加 _low")
        self.batch_high_btn = QPushButton("批量添加 _high")
        self.clean_suffix_btn = QPushButton("清理所有后缀")
        
        # 应用统一样式到批量操作按钮
        batch_button_style = "QPushButton { padding: 8px 16px; font-size: 12px; min-height: 28px; }"
        self.batch_low_btn.setStyleSheet(batch_button_style)
        self.batch_high_btn.setStyleSheet(batch_button_style)
        self.clean_suffix_btn.setStyleSheet(batch_button_style + "QPushButton { background-color: #FF5722; color: white; }")
        
        # 材质操作组
        self.material_group = QGroupBox("材质配置")
        
        # 全局透明度设置
        self.global_transparency_check = QCheckBox("使用全局透明度")
        self.global_transparency_check.setChecked(True)
        self.global_transparency_slider = QSlider(Qt.Horizontal)
        self.global_transparency_slider.setRange(0, 100)
        self.global_transparency_slider.setValue(0)
        self.global_transparency_value_label = QLabel("0%")
        self.global_transparency_value_label.setMinimumWidth(30)
        
        # 材质配置列表
        self.material_config_list = QListWidget()
        self.material_config_list.setMaximumHeight(140)
        self.material_config_list.setFont(QFont("Arial", 9))
        
        # 材质配置按钮
        self.add_config_btn = QPushButton("添加配置")
        self.edit_config_btn = QPushButton("编辑配置")
        self.remove_config_btn = QPushButton("删除配置")
        self.auto_material_btn = QPushButton("自动分配材质")
        
        # 设置按钮样式 - 适中的尺寸和更大字体
        button_style = "QPushButton { padding: 6px 12px; font-size: 12px; min-height: 26px; }"
        self.add_config_btn.setStyleSheet(button_style + "QPushButton { background-color: #4CAF50; color: white; }")
        self.edit_config_btn.setStyleSheet(button_style + "QPushButton { background-color: #2196F3; color: white; }")
        self.remove_config_btn.setStyleSheet(button_style + "QPushButton { background-color: #f44336; color: white; }")
        self.auto_material_btn.setStyleSheet(button_style + "QPushButton { background-color: #FF9800; color: white; font-weight: bold; }")
        
        # 历史操作组
        self.history_group = QGroupBox("历史操作")
        self.undo_btn = QPushButton("撤销上一次重命名")
        self.clear_history_btn = QPushButton("清空历史记录")
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        self.history_list.setFont(QFont("Arial", 9))
        
        # 应用统一样式到历史操作按钮
        history_button_style = "QPushButton { padding: 8px 16px; font-size: 12px; min-height: 28px; }"
        self.undo_btn.setStyleSheet(history_button_style + "QPushButton { background-color: #9C27B0; color: white; }")
        self.clear_history_btn.setStyleSheet(history_button_style + "QPushButton { background-color: #607D8B; color: white; }")
        
        # 设置组
        self.settings_group = QGroupBox("设置")
        self.conflict_check = QCheckBox("检查命名冲突")
        self.conflict_check.setChecked(True)
        self.auto_unique_check = QCheckBox("自动生成唯一名称")
        self.auto_unique_check.setChecked(True)
        self.show_messages_check = QCheckBox("显示操作消息")
        self.show_messages_check.setChecked(True)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        
        # 关于按钮
        self.about_btn = QPushButton("关于")
        self.close_btn = QPushButton("关闭")
        
        # 应用统一样式到底部按钮
        bottom_button_style = "QPushButton { padding: 8px 16px; font-size: 12px; min-height: 28px; }"
        self.about_btn.setStyleSheet(bottom_button_style + "QPushButton { background-color: #607D8B; color: white; }")
        self.close_btn.setStyleSheet(bottom_button_style + "QPushButton { background-color: #f44336; color: white; }")
    
    def create_layouts(self):
        """
        创建布局
        """
        main_layout = QVBoxLayout(self)
        
        # 标题
        main_layout.addWidget(self.title_label)
        main_layout.addSpacing(10)
        
        # 选择信息组布局
        selection_layout = QVBoxLayout()
        selection_layout.addWidget(self.selection_list)
        selection_layout.addWidget(self.refresh_selection_btn)
        self.selection_group.setLayout(selection_layout)
        main_layout.addWidget(self.selection_group)
        
        # 快速操作组布局
        quick_layout = QVBoxLayout()
        quick_layout.addWidget(self.auto_rename_btn)
        
        quick_buttons_layout = QHBoxLayout()
        quick_buttons_layout.addWidget(self.low_suffix_btn)
        quick_buttons_layout.addWidget(self.high_suffix_btn)
        quick_layout.addLayout(quick_buttons_layout)
        
        self.quick_group.setLayout(quick_layout)
        main_layout.addWidget(self.quick_group)
        
        # 自定义后缀组布局
        custom_layout = QVBoxLayout()
        
        custom_input_layout = QHBoxLayout()
        custom_input_layout.addWidget(self.custom_suffix_input)
        custom_input_layout.addWidget(self.custom_suffix_btn)
        custom_layout.addLayout(custom_input_layout)
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(self.preset_cage_btn)
        preset_layout.addWidget(self.preset_bake_btn)
        preset_layout.addWidget(self.preset_lp_btn)
        preset_layout.addWidget(self.preset_hp_btn)
        custom_layout.addLayout(preset_layout)
        
        self.custom_group.setLayout(custom_layout)
        main_layout.addWidget(self.custom_group)
        
        # 批量操作组布局
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(self.batch_low_btn)
        batch_layout.addWidget(self.batch_high_btn)
        batch_layout.addWidget(self.clean_suffix_btn)
        self.batch_group.setLayout(batch_layout)
        main_layout.addWidget(self.batch_group)
        
        # 材质操作组布局
        material_layout = QVBoxLayout()
        
        # 全局透明度设置布局
        global_transparency_layout = QVBoxLayout()
        global_transparency_layout.addWidget(self.global_transparency_check)
        transparency_control_layout = QHBoxLayout()
        transparency_control_layout.addWidget(QLabel("透明度:"))
        transparency_control_layout.addWidget(self.global_transparency_slider)
        transparency_control_layout.addWidget(self.global_transparency_value_label)
        global_transparency_layout.addLayout(transparency_control_layout)
        material_layout.addLayout(global_transparency_layout)
        
        # 材质配置列表
        material_layout.addWidget(QLabel("材质配置:"))
        material_layout.addWidget(self.material_config_list)
        
        # 材质配置按钮布局
        config_buttons_layout = QHBoxLayout()
        config_buttons_layout.addWidget(self.add_config_btn)
        config_buttons_layout.addWidget(self.edit_config_btn)
        config_buttons_layout.addWidget(self.remove_config_btn)
        material_layout.addLayout(config_buttons_layout)
        
        # 自动分配材质按钮
        material_layout.addWidget(self.auto_material_btn)
        
        self.material_group.setLayout(material_layout)
        main_layout.addWidget(self.material_group)
        
        # 历史操作组布局
        history_layout = QVBoxLayout()
        history_buttons_layout = QHBoxLayout()
        history_buttons_layout.addWidget(self.undo_btn)
        history_buttons_layout.addWidget(self.clear_history_btn)
        history_layout.addLayout(history_buttons_layout)
        history_layout.addWidget(self.history_list)
        self.history_group.setLayout(history_layout)
        main_layout.addWidget(self.history_group)
        
        # 设置组布局
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(self.conflict_check)
        settings_layout.addWidget(self.auto_unique_check)
        settings_layout.addWidget(self.show_messages_check)
        self.settings_group.setLayout(settings_layout)
        main_layout.addWidget(self.settings_group)
        
        # 状态栏
        main_layout.addWidget(self.status_label)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.about_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_btn)
        main_layout.addLayout(bottom_layout)
    
    def create_connections(self):
        """
        创建信号连接
        """
        # 选择相关
        self.refresh_selection_btn.clicked.connect(self.refresh_selection)
        
        # 快速操作
        self.auto_rename_btn.clicked.connect(self.auto_rename)
        self.low_suffix_btn.clicked.connect(self.add_low_suffix)
        self.high_suffix_btn.clicked.connect(self.add_high_suffix)
        
        # 自定义后缀
        self.custom_suffix_btn.clicked.connect(self.add_custom_suffix)
        self.custom_suffix_input.returnPressed.connect(self.add_custom_suffix)
        
        # 预设后缀
        self.preset_cage_btn.clicked.connect(lambda: self.add_preset_suffix("cage"))
        self.preset_bake_btn.clicked.connect(lambda: self.add_preset_suffix("bake"))
        self.preset_lp_btn.clicked.connect(lambda: self.add_preset_suffix("LP"))
        self.preset_hp_btn.clicked.connect(lambda: self.add_preset_suffix("HP"))
        
        # 批量操作
        self.batch_low_btn.clicked.connect(self.batch_add_low)
        self.batch_high_btn.clicked.connect(self.batch_add_high)
        self.clean_suffix_btn.clicked.connect(self.clean_all_suffixes)
        
        # 材质操作连接
        self.auto_material_btn.clicked.connect(self.auto_assign_materials)
        self.global_transparency_slider.valueChanged.connect(self.update_global_transparency_label)
        self.global_transparency_check.toggled.connect(self.toggle_global_transparency)
        
        # 材质配置按钮连接
        self.add_config_btn.clicked.connect(self.add_material_config)
        self.edit_config_btn.clicked.connect(self.edit_material_config)
        self.remove_config_btn.clicked.connect(self.remove_material_config)
        self.material_config_list.itemDoubleClicked.connect(self.edit_material_config)
        
        # 历史操作
        self.undo_btn.clicked.connect(self.undo_rename)
        self.clear_history_btn.clicked.connect(self.clear_history)
        
        # 底部按钮
        self.about_btn.clicked.connect(self.show_about)
        self.close_btn.clicked.connect(self.close)
    
    def update_ui(self):
        """
        更新界面状态
        """
        self.refresh_selection()
        self.update_history_list()
        self.update_status("就绪")
    
    def refresh_selection(self):
        """
        刷新选择列表
        """
        self.selection_list.clear()
        selected = cmds.ls(selection=True, transforms=True)
        
        if selected:
            for obj in selected:
                self.selection_list.addItem(obj)
            self.update_status(f"已选择 {len(selected)} 个物体")
        else:
            self.selection_list.addItem("未选择任何物体")
            self.update_status("请选择要重命名的物体")
    
    def update_history_list(self):
        """
        更新历史记录列表
        """
        self.history_list.clear()
        if self.renamer.rename_history:
            for i, record in enumerate(reversed(self.renamer.rename_history[-3:])):
                summary = f"操作 {len(self.renamer.rename_history)-i}: {len(record)} 个物体"
                self.history_list.addItem(summary)
        else:
            self.history_list.addItem("无历史记录")
    
    def update_status(self, message):
        """
        更新状态信息
        
        Args:
            message (str): 状态消息
        """
        self.status_label.setText(message)
    
    def auto_rename(self):
        """
        自动重命名模式
        """
        try:
            self.renamer.auto_rename_by_selection_order()
            self.refresh_selection()
            self.update_history_list()
            
            selection_count = len(self.renamer.selection_history)
            if selection_count == 1:
                self.update_status("已添加_low后缀，请选择下一组物体")
            elif selection_count == 0:
                self.update_status("自动重命名完成")
            
        except Exception as e:
            self.update_status(f"自动重命名失败: {str(e)}")
    
    def add_low_suffix(self):
        """
        添加_low后缀
        """
        try:
            result = self.renamer.rename_to_low()
            if result:
                self.refresh_selection()
                self.update_history_list()
                self.update_status(f"已为 {len(result)} 个物体添加_low后缀")
        except Exception as e:
            self.update_status(f"添加_low后缀失败: {str(e)}")
    
    def add_high_suffix(self):
        """
        添加_high后缀
        """
        try:
            result = self.renamer.rename_to_high()
            if result:
                self.refresh_selection()
                self.update_history_list()
                self.update_status(f"已为 {len(result)} 个物体添加_high后缀")
        except Exception as e:
            self.update_status(f"添加_high后缀失败: {str(e)}")
    
    def add_custom_suffix(self):
        """
        添加自定义后缀
        """
        suffix = self.custom_suffix_input.text().strip()
        if not suffix:
            self.update_status("请输入自定义后缀")
            return
            
        try:
            result = self.renamer.rename_with_custom_suffix(suffix)
            if result:
                self.refresh_selection()
                self.update_history_list()
                self.update_status(f"已为 {len(result)} 个物体添加_{suffix}后缀")
                self.custom_suffix_input.clear()
        except Exception as e:
            self.update_status(f"添加自定义后缀失败: {str(e)}")
    
    def add_preset_suffix(self, suffix):
        """
        添加预设后缀
        
        Args:
            suffix (str): 预设后缀
        """
        try:
            result = self.renamer.rename_with_custom_suffix(suffix)
            if result:
                self.refresh_selection()
                self.update_history_list()
                self.update_status(f"已为 {len(result)} 个物体添加_{suffix}后缀")
        except Exception as e:
            self.update_status(f"添加_{suffix}后缀失败: {str(e)}")
    
    def batch_add_low(self):
        """
        批量添加_low后缀
        """
        all_objects = cmds.ls(transforms=True)
        if all_objects:
            try:
                result = self.renamer.rename_to_low(all_objects)
                self.refresh_selection()
                self.update_history_list()
                self.update_status(f"批量操作完成：{len(result)} 个物体添加_low后缀")
            except Exception as e:
                self.update_status(f"批量添加_low失败: {str(e)}")
    
    def batch_add_high(self):
        """
        批量添加_high后缀
        """
        all_objects = cmds.ls(transforms=True)
        if all_objects:
            try:
                result = self.renamer.rename_to_high(all_objects)
                self.refresh_selection()
                self.update_history_list()
                self.update_status(f"批量操作完成：{len(result)} 个物体添加_high后缀")
            except Exception as e:
                self.update_status(f"批量添加_high失败: {str(e)}")
    
    def clean_all_suffixes(self):
        """
        清理所有后缀
        """
        selected = cmds.ls(selection=True, transforms=True)
        if not selected:
            self.update_status("请选择要清理后缀的物体")
            return
            
        try:
            cleaned_objects = []
            for obj in selected:
                base_name = self.renamer.clean_object_name(obj)
                if base_name != obj:
                    cmds.rename(obj, base_name)
                    cleaned_objects.append(base_name)
            
            if cleaned_objects:
                self.refresh_selection()
                self.update_status(f"已清理 {len(cleaned_objects)} 个物体的后缀")
            else:
                self.update_status("没有需要清理的后缀")
                
        except Exception as e:
            self.update_status(f"清理后缀失败: {str(e)}")
    
    def undo_rename(self):
        """
        撤销重命名
        """
        try:
            self.renamer.undo_last_rename()
            self.refresh_selection()
            self.update_history_list()
            self.update_status("已撤销上一次重命名操作")
        except Exception as e:
            self.update_status(f"撤销操作失败: {str(e)}")
    
    def clear_history(self):
        """
        清空历史记录
        """
        self.renamer.clear_history()
        self.update_history_list()
        self.update_status("历史记录已清空")
    
    def update_transparency_label(self, value):
        """
        更新透明度标签显示
        
        Args:
            value (int): 透明度值 (0-100)
        """
        self.transparency_value_label.setText(f"{value}%")
    
    def update_global_transparency_label(self, value):
        """
        更新全局透明度标签显示
        """
        self.global_transparency_value_label.setText(f"{value}%")
        
    def toggle_global_transparency(self, checked):
        """
        切换全局透明度模式
        """
        self.global_transparency_slider.setEnabled(checked)
        self.global_transparency_value_label.setEnabled(checked)
        
    def refresh_material_config_list(self):
        """
        刷新材质配置列表显示
        """
        self.material_config_list.clear()
        try:
            configs = self.renamer.get_material_configs()
            for suffix, config in configs.items():
                color_desc = self.get_color_description(config['color'])
                transparency = config.get('transparency', 0)
                enabled = "✓" if config.get('enabled', True) else "✗"
                item_text = f"{enabled} {suffix}: {color_desc} (透明度: {transparency}%)"
                self.material_config_list.addItem(item_text)
        except Exception as e:
            self.update_status(f"刷新材质配置失败: {str(e)}")
            
    def get_color_description(self, color):
        """
        根据RGB值获取颜色描述
        """
        color_map = {
            (0, 1, 0): "绿色",
            (1, 0, 0): "红色", 
            (0, 0, 1): "蓝色",
            (1, 1, 0): "黄色",
            (1, 0, 1): "紫色",
            (0, 1, 1): "青色",
            (1, 0.5, 0): "橙色"
        }
        return color_map.get(tuple(color), f"RGB({color[0]:.1f}, {color[1]:.1f}, {color[2]:.1f})")
        
    def add_material_config(self):
        """
        添加新的材质配置
        """
        dialog = MaterialConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            suffix, color, transparency, enabled = dialog.get_config()
            try:
                # 将透明度从0-100范围转换为0-1范围
                transparency_normalized = transparency / 100.0
                self.renamer.add_material_config(suffix, color, transparency_normalized, enabled)
                self.refresh_material_config_list()
                self.update_status(f"已添加材质配置: {suffix}")
            except Exception as e:
                self.update_status(f"添加材质配置失败: {str(e)}")
                
    def edit_material_config(self):
        """
        编辑选中的材质配置
        """
        current_item = self.material_config_list.currentItem()
        if not current_item:
            self.update_status("请先选择要编辑的材质配置")
            return
            
        # 解析当前选中项的后缀名
        item_text = current_item.text()
        suffix = item_text.split(":")[0].split(" ")[1]  # 提取后缀名
        
        try:
            configs = self.renamer.get_material_configs()
            if suffix in configs:
                config = configs[suffix]
                # 将透明度从0-1范围转换为0-100范围用于显示
                transparency_display = int(config.get('transparency', 0) * 100)
                dialog = MaterialConfigDialog(self, suffix, config['color'], 
                                            transparency_display, 
                                            config.get('enabled', True))
                if dialog.exec_() == QDialog.Accepted:
                    new_suffix, color, transparency, enabled = dialog.get_config()
                    # 将透明度从0-100范围转换为0-1范围
                    transparency_normalized = transparency / 100.0
                    if new_suffix != suffix:
                        # 如果后缀名改变了，需要删除旧的并添加新的
                        self.renamer.remove_material_config(suffix)
                        self.renamer.add_material_config(new_suffix, color, transparency_normalized, enabled)
                    else:
                        # 更新现有配置
                        self.renamer.update_material_color(suffix, color)
                        self.renamer.update_material_transparency(suffix, transparency_normalized)
                        configs[suffix]['enabled'] = enabled
                    self.refresh_material_config_list()
                    self.update_status(f"已更新材质配置: {new_suffix}")
        except Exception as e:
            self.update_status(f"编辑材质配置失败: {str(e)}")
            
    def remove_material_config(self):
        """
        删除选中的材质配置
        """
        current_item = self.material_config_list.currentItem()
        if not current_item:
            self.update_status("请先选择要删除的材质配置")
            return
            
        # 解析当前选中项的后缀名
        item_text = current_item.text()
        suffix = item_text.split(":")[0].split(" ")[1]  # 提取后缀名
        
        try:
            self.renamer.remove_material_config(suffix)
            self.refresh_material_config_list()
            self.update_status(f"已删除材质配置: {suffix}")
        except Exception as e:
            self.update_status(f"删除材质配置失败: {str(e)}")
    
    def auto_assign_materials(self):
        """
        自动分配材质
        """
        try:
            # 根据全局透明度设置决定透明度参数
            if self.global_transparency_check.isChecked():
                global_transparency = self.global_transparency_slider.value() / 100.0
            else:
                global_transparency = None
            
            # 执行自动分材质
            result = self.renamer.auto_assign_materials(global_transparency)
            
            # 统计结果
            total_objects = sum(len(result[key]['objects']) for key in result)
            
            if total_objects > 0:
                # 构建详细信息
                details = []
                for key in ['low', 'high', 'cage']:
                    count = len(result[key]['objects'])
                    if count > 0:
                        color_name = {'low': '绿色', 'high': '红色', 'cage': '蓝色'}[key]
                        details.append(f"{count}个_{key}({color_name})")
                
                detail_text = ", ".join(details)
                transparency_text = f", 透明度{int(global_transparency*100)}%" if global_transparency and global_transparency > 0 else ""
                
                self.update_status(f"自动分材质完成: {detail_text}{transparency_text}")
                
                # 刷新界面
                self.refresh_selection()
            else:
                self.update_status("未找到带有_low、_high或_cage后缀的物体")
                
        except Exception as e:
            self.update_status(f"自动分材质失败: {str(e)}")
    
    def show_about(self):
        """
        显示关于对话框
        """
        about_text = """
        Maya烘焙命名工具 v1.0
        
        作者: liudan
        邮箱: 3236296040@qq.com
        
        功能特性:
        • 快速为物体添加_low/_high后缀
        • 支持自动重命名模式
        • 自定义后缀支持
        • 批量重命名功能
        • 自动分材质功能 (NEW!)
          - _low模型: 绿色Lambert材质
          - _high模型: 红色Lambert材质
          - _cage模型: 蓝色Lambert材质
          - 支持透明度设置
        • 撤销/重做操作
        • 命名冲突检测
        
        适用于Maya 2023及以前版本
        专为Maya到Marmoset烘焙工作流设计
        """
        
        QMessageBox.about(self, "关于", about_text)

def show_maya_baking_renamer_gui():
    """
    显示Maya烘焙命名工具GUI
    """
    global maya_baking_renamer_gui
    
    try:
        maya_baking_renamer_gui.close()
        maya_baking_renamer_gui.deleteLater()
    except:
        pass
    
    maya_baking_renamer_gui = MayaBakingRenamerGUI()
    maya_baking_renamer_gui.show()
    
    return maya_baking_renamer_gui

# 全局变量
maya_baking_renamer_gui = None

if __name__ == "__main__":
    show_maya_baking_renamer_gui()