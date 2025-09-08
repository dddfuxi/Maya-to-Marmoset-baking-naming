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
        self.setWindowTitle("Maya烘焙命名工具 v1.0")
        self.setWindowFlags(Qt.Window)
        self.setMinimumSize(400, 500)
        self.resize(450, 600)
        
        # 创建界面
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
        # 更新界面状态
        self.update_ui()
    
    def create_widgets(self):
        """
        创建界面控件
        """
        # 标题标签
        self.title_label = QLabel("Maya烘焙命名工具")
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.title_label.setFont(font)
        
        # 选择信息组
        self.selection_group = QGroupBox("当前选择")
        self.selection_list = QListWidget()
        self.selection_list.setMaximumHeight(100)
        self.refresh_selection_btn = QPushButton("刷新选择")
        
        # 快速操作组
        self.quick_group = QGroupBox("快速操作")
        self.auto_rename_btn = QPushButton("自动重命名模式")
        self.auto_rename_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        self.low_suffix_btn = QPushButton("添加 _low 后缀")
        self.high_suffix_btn = QPushButton("添加 _high 后缀")
        
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
        
        # 批量操作组
        self.batch_group = QGroupBox("批量操作")
        self.batch_low_btn = QPushButton("批量添加 _low")
        self.batch_high_btn = QPushButton("批量添加 _high")
        self.clean_suffix_btn = QPushButton("清理所有后缀")
        
        # 历史操作组
        self.history_group = QGroupBox("历史操作")
        self.undo_btn = QPushButton("撤销上一次重命名")
        self.clear_history_btn = QPushButton("清空历史记录")
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(80)
        
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