# -*- coding: utf-8 -*-
"""
Maya烘焙命名工具 - Maya to Marmoset Baking Naming Tool
适用于Maya 2023及以前版本
作者: liudan
邮箱: 3236296040@qq.com

功能说明:
- 快速为选中物体添加_low或_high后缀
- 支持批量重命名
- 提供GUI界面操作
- 支持自定义后缀
- 包含撤销/重做功能
- 命名冲突检测
"""

import maya.cmds as cmds
import maya.mel as mel
try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
except ImportError:
    try:
        from PySide.QtGui import *
        from PySide.QtCore import *
    except ImportError:
        try:
            from PyQt4.QtGui import *
            from PyQt4.QtCore import *
        except ImportError:
            print("Warning: No Qt bindings found. GUI will not be available.")

class MayaBakingRenamer(object):
    """
    Maya烘焙命名工具主类
    提供物体重命名功能，支持_low和_high后缀
    """
    
    def __init__(self):
        """
        初始化烘焙命名工具
        """
        self.window_name = "MayaBakingRenamer"
        self.window_title = "Maya烘焙命名工具 v1.0"
        self.selection_history = []  # 选择历史记录
        self.rename_history = []     # 重命名历史记录
        self.current_mode = "auto"   # 当前模式: auto, low, high, custom
        self.custom_suffix = ""      # 自定义后缀
        
    def get_selected_objects(self):
        """
        获取当前选中的物体
        
        Returns:
            list: 选中的物体列表
        """
        selected = cmds.ls(selection=True, transforms=True)
        if not selected:
            cmds.warning("请先选择要重命名的物体")
            return []
        return selected
    
    def clean_object_name(self, obj_name):
        """
        清理物体名称，移除现有的后缀
        
        Args:
            obj_name (str): 原始物体名称
            
        Returns:
            str: 清理后的基础名称
        """
        # 移除常见的烘焙后缀
        suffixes = ['_low', '_high', '_cage', '_bake', '_LP', '_HP']
        base_name = obj_name
        
        for suffix in suffixes:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
                
        return base_name
    
    def check_name_conflict(self, new_name):
        """
        检查命名冲突
        
        Args:
            new_name (str): 新的物体名称
            
        Returns:
            bool: True表示有冲突，False表示无冲突
        """
        existing_objects = cmds.ls(new_name)
        return len(existing_objects) > 0
    
    def generate_unique_name(self, base_name):
        """
        生成唯一的物体名称
        
        Args:
            base_name (str): 基础名称
            
        Returns:
            str: 唯一的物体名称
        """
        if not self.check_name_conflict(base_name):
            return base_name
            
        counter = 1
        while True:
            new_name = f"{base_name}_{counter:02d}"
            if not self.check_name_conflict(new_name):
                return new_name
            counter += 1
    
    def rename_to_low(self, objects=None):
        """
        将选中物体重命名为_low后缀
        
        Args:
            objects (list, optional): 要重命名的物体列表，默认为当前选中物体
            
        Returns:
            list: 重命名后的物体列表
        """
        if objects is None:
            objects = self.get_selected_objects()
            
        if not objects:
            return []
            
        renamed_objects = []
        rename_record = []
        
        for obj in objects:
            try:
                # 获取基础名称
                base_name = self.clean_object_name(obj)
                new_name = f"{base_name}_low"
                
                # 检查冲突并生成唯一名称
                if self.check_name_conflict(new_name):
                    unique_name = self.generate_unique_name(new_name)
                    cmds.warning(f"名称冲突: {new_name} 已存在，使用 {unique_name}")
                    new_name = unique_name
                
                # 执行重命名
                renamed_obj = cmds.rename(obj, new_name)
                renamed_objects.append(renamed_obj)
                rename_record.append((obj, renamed_obj))
                
                print(f"重命名成功: {obj} -> {renamed_obj}")
                
            except Exception as e:
                cmds.error(f"重命名失败 {obj}: {str(e)}")
        
        # 记录到历史
        if rename_record:
            self.rename_history.append(rename_record)
            
        return renamed_objects
    
    def rename_to_high(self, objects=None):
        """
        将选中物体重命名为_high后缀
        
        Args:
            objects (list, optional): 要重命名的物体列表，默认为当前选中物体
            
        Returns:
            list: 重命名后的物体列表
        """
        if objects is None:
            objects = self.get_selected_objects()
            
        if not objects:
            return []
            
        renamed_objects = []
        rename_record = []
        
        for obj in objects:
            try:
                # 获取基础名称
                base_name = self.clean_object_name(obj)
                new_name = f"{base_name}_high"
                
                # 检查冲突并生成唯一名称
                if self.check_name_conflict(new_name):
                    unique_name = self.generate_unique_name(new_name)
                    cmds.warning(f"名称冲突: {new_name} 已存在，使用 {unique_name}")
                    new_name = unique_name
                
                # 执行重命名
                renamed_obj = cmds.rename(obj, new_name)
                renamed_objects.append(renamed_obj)
                rename_record.append((obj, renamed_obj))
                
                print(f"重命名成功: {obj} -> {renamed_obj}")
                
            except Exception as e:
                cmds.error(f"重命名失败 {obj}: {str(e)}")
        
        # 记录到历史
        if rename_record:
            self.rename_history.append(rename_record)
            
        return renamed_objects
    
    def rename_with_custom_suffix(self, suffix, objects=None):
        """
        使用自定义后缀重命名物体
        
        Args:
            suffix (str): 自定义后缀
            objects (list, optional): 要重命名的物体列表，默认为当前选中物体
            
        Returns:
            list: 重命名后的物体列表
        """
        if not suffix:
            cmds.warning("请输入有效的后缀")
            return []
            
        if objects is None:
            objects = self.get_selected_objects()
            
        if not objects:
            return []
            
        # 确保后缀以下划线开头
        if not suffix.startswith('_'):
            suffix = '_' + suffix
            
        renamed_objects = []
        rename_record = []
        
        for obj in objects:
            try:
                # 获取基础名称
                base_name = self.clean_object_name(obj)
                new_name = f"{base_name}{suffix}"
                
                # 检查冲突并生成唯一名称
                if self.check_name_conflict(new_name):
                    unique_name = self.generate_unique_name(new_name)
                    cmds.warning(f"名称冲突: {new_name} 已存在，使用 {unique_name}")
                    new_name = unique_name
                
                # 执行重命名
                renamed_obj = cmds.rename(obj, new_name)
                renamed_objects.append(renamed_obj)
                rename_record.append((obj, renamed_obj))
                
                print(f"重命名成功: {obj} -> {renamed_obj}")
                
            except Exception as e:
                cmds.error(f"重命名失败 {obj}: {str(e)}")
        
        # 记录到历史
        if rename_record:
            self.rename_history.append(rename_record)
            
        return renamed_objects
    
    def auto_rename_by_selection_order(self):
        """
        根据选择顺序自动重命名
        第一次选择的物体添加_low后缀，第二次选择的物体添加_high后缀
        """
        selected = self.get_selected_objects()
        if not selected:
            return
            
        # 记录选择历史
        self.selection_history.append(selected)
        
        selection_count = len(self.selection_history)
        
        if selection_count == 1:
            # 第一次选择，添加_low后缀
            self.rename_to_low(selected)
            cmds.inViewMessage(amg='已添加_low后缀，请选择下一组物体添加_high后缀', pos='midCenter', fade=True)
        elif selection_count == 2:
            # 第二次选择，添加_high后缀
            self.rename_to_high(selected)
            cmds.inViewMessage(amg='已添加_high后缀，自动模式完成', pos='midCenter', fade=True)
            # 重置选择历史
            self.selection_history = []
        else:
            # 重置并重新开始
            self.selection_history = [selected]
            self.rename_to_low(selected)
            cmds.inViewMessage(amg='重新开始：已添加_low后缀', pos='midCenter', fade=True)
    
    def undo_last_rename(self):
        """
        撤销上一次重命名操作
        """
        if not self.rename_history:
            cmds.warning("没有可撤销的重命名操作")
            return
            
        last_rename = self.rename_history.pop()
        
        for old_name, new_name in reversed(last_rename):
            try:
                # 检查物体是否仍然存在
                if cmds.objExists(new_name):
                    cmds.rename(new_name, old_name)
                    print(f"撤销重命名: {new_name} -> {old_name}")
            except Exception as e:
                cmds.error(f"撤销重命名失败 {new_name}: {str(e)}")
        
        cmds.inViewMessage(amg='已撤销上一次重命名操作', pos='midCenter', fade=True)
    
    def clear_history(self):
        """
        清空历史记录
        """
        self.selection_history = []
        self.rename_history = []
        print("历史记录已清空")

# 全局实例
baking_renamer = MayaBakingRenamer()

# 便捷函数
def rename_to_low():
    """
    便捷函数：将选中物体重命名为_low后缀
    """
    return baking_renamer.rename_to_low()

def rename_to_high():
    """
    便捷函数：将选中物体重命名为_high后缀
    """
    return baking_renamer.rename_to_high()

def auto_rename():
    """
    便捷函数：自动重命名（根据选择顺序）
    """
    baking_renamer.auto_rename_by_selection_order()

def undo_rename():
    """
    便捷函数：撤销上一次重命名
    """
    baking_renamer.undo_last_rename()

def clear_rename_history():
    """
    便捷函数：清空重命名历史
    """
    baking_renamer.clear_history()

if __name__ == "__main__":
    print("Maya烘焙命名工具已加载")
    print("使用方法:")
    print("  rename_to_low() - 添加_low后缀")
    print("  rename_to_high() - 添加_high后缀")
    print("  auto_rename() - 自动重命名模式")
    print("  undo_rename() - 撤销上一次重命名")
    print("  clear_rename_history() - 清空历史记录")