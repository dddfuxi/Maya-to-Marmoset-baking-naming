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

class MaterialConfig(object):
    """
    材质配置管理类
    """
    
    def __init__(self):
        """
        初始化材质配置
        """
        # 默认材质配置
        self.material_configs = {
            '_low': {
                'color': (0.0, 0.8, 0.0),  # 绿色
                'transparency': 0.0,
                'material_name': 'BakingMaterial_Low',
                'enabled': True
            },
            '_high': {
                'color': (0.8, 0.0, 0.0),  # 红色
                'transparency': 0.0,
                'material_name': 'BakingMaterial_High',
                'enabled': True
            },
            '_cage': {
                'color': (0.0, 0.0, 0.8),  # 蓝色
                'transparency': 0.0,
                'material_name': 'BakingMaterial_Cage',
                'enabled': True
            }
        }
    
    def add_suffix_config(self, suffix, color, transparency=0.0, material_name=None, enabled=True):
        """
        添加或更新后缀配置
        
        Args:
            suffix (str): 后缀名称 (如: '_low', '_custom')
            color (tuple): RGB颜色值 (0-1范围)
            transparency (float): 透明度值 (0-1范围)
            material_name (str): 材质名称，如果为None则自动生成
            enabled (bool): 是否启用此配置
        """
        if not suffix.startswith('_'):
            suffix = '_' + suffix
            
        if material_name is None:
            clean_suffix = suffix.replace('_', '').title()
            material_name = f'BakingMaterial_{clean_suffix}'
            
        self.material_configs[suffix] = {
            'color': color,
            'transparency': transparency,
            'material_name': material_name,
            'enabled': enabled
        }
    
    def remove_suffix_config(self, suffix):
        """
        移除后缀配置
        
        Args:
            suffix (str): 要移除的后缀
        """
        if suffix in self.material_configs:
            del self.material_configs[suffix]
    
    def get_enabled_configs(self):
        """
        获取所有启用的配置
        
        Returns:
            dict: 启用的材质配置
        """
        return {k: v for k, v in self.material_configs.items() if v.get('enabled', True)}
    
    def update_suffix_transparency(self, suffix, transparency):
        """
        更新指定后缀的透明度
        
        Args:
            suffix (str): 后缀名称
            transparency (float): 透明度值 (0-1范围)
        """
        if suffix in self.material_configs:
            self.material_configs[suffix]['transparency'] = transparency
    
    def update_suffix_color(self, suffix, color):
        """
        更新指定后缀的颜色
        
        Args:
            suffix (str): 后缀名称
            color (tuple): RGB颜色值 (0-1范围)
        """
        if suffix in self.material_configs:
            self.material_configs[suffix]['color'] = color

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
        self.material_config = MaterialConfig()  # 材质配置管理器
        
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
    
    def create_lambert_material(self, name, color, transparency=0.0):
        """
        创建Lambert材质
        
        Args:
            name (str): 材质名称
            color (tuple): RGB颜色值 (0-1范围)
            transparency (float): 透明度值 (0-1范围)
            
        Returns:
            str: 创建的材质名称
        """
        try:
            # 检查材质是否已存在
            if cmds.objExists(name):
                cmds.delete(name)
                
            # 创建Lambert材质
            material = cmds.shadingNode('lambert', asShader=True, name=name)
            
            # 设置颜色
            cmds.setAttr(f"{material}.color", color[0], color[1], color[2], type="double3")
            
            # 设置透明度
            if transparency > 0.0:
                cmds.setAttr(f"{material}.transparency", transparency, transparency, transparency, type="double3")
            
            print(f"创建材质成功: {material}")
            return material
            
        except Exception as e:
            cmds.error(f"创建材质失败 {name}: {str(e)}")
            return None
    
    def assign_material_to_objects(self, objects, material):
        """
        为物体分配材质
        
        Args:
            objects (list): 物体列表
            material (str): 材质名称
            
        Returns:
            list: 成功分配材质的物体列表
        """
        if not objects or not material:
            return []
            
        assigned_objects = []
        
        try:
            # 获取或创建着色组
            shading_group = None
            connections = cmds.listConnections(material, type='shadingEngine')
            
            if connections:
                shading_group = connections[0]
            else:
                # 创建新的着色组
                shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{material}SG")
                cmds.connectAttr(f"{material}.outColor", f"{shading_group}.surfaceShader")
            
            # 为每个物体分配材质
            for obj in objects:
                if cmds.objExists(obj):
                    cmds.sets(obj, edit=True, forceElement=shading_group)
                    assigned_objects.append(obj)
                    print(f"材质分配成功: {obj} -> {material}")
                    
        except Exception as e:
            cmds.error(f"分配材质失败: {str(e)}")
            
        return assigned_objects
    
    def find_objects_by_suffix(self, suffix):
        """
        根据后缀查找场景中的物体
        
        Args:
            suffix (str): 要查找的后缀 (如: '_low', '_high', '_cage')
            
        Returns:
            list: 匹配后缀的物体列表
        """
        all_objects = cmds.ls(transforms=True)
        matching_objects = []
        
        for obj in all_objects:
            if obj.endswith(suffix):
                matching_objects.append(obj)
                
        return matching_objects
    
    def auto_assign_materials(self, global_transparency=None):
        """
        自动为不同后缀的模型分配对应颜色的Lambert材质
        支持灵活的后缀配置和独立的透明度设置
        
        Args:
            global_transparency (float, optional): 全局透明度值 (0-1范围)，如果提供则覆盖各后缀的独立透明度
            
        Returns:
            dict: 分配结果统计
        """
        result = {}
        
        try:
            # 获取启用的材质配置
            enabled_configs = self.material_config.get_enabled_configs()
            
            if not enabled_configs:
                cmds.warning("没有启用的材质配置")
                return result
            
            # 为每种配置创建材质并分配
            for suffix, config in enabled_configs.items():
                # 查找匹配的物体
                objects = self.find_objects_by_suffix(suffix)
                
                # 初始化结果记录
                clean_suffix = suffix.replace('_', '')
                result[clean_suffix] = {'objects': objects, 'material': None}
                
                if objects:
                    # 确定使用的透明度值
                    transparency = global_transparency if global_transparency is not None else config['transparency']
                    
                    # 创建材质
                    material = self.create_lambert_material(
                        config['material_name'],
                        config['color'],
                        transparency
                    )
                    
                    if material:
                        result[clean_suffix]['material'] = material
                        # 分配材质
                        self.assign_material_to_objects(objects, material)
                        
                        # 构建颜色描述
                        color_desc = self._get_color_description(config['color'])
                        transparency_desc = f", 透明度{int(transparency*100)}%" if transparency > 0 else ""
                        
                        print(f"为 {len(objects)} 个{suffix}物体分配了{color_desc}材质{transparency_desc}")
            
            # 输出统计信息
            total_objects = sum(len(result[key]['objects']) for key in result)
            if total_objects > 0:
                cmds.inViewMessage(
                    amg=f'自动分材质完成: {total_objects}个物体',
                    pos='midCenter',
                    fade=True
                )
            else:
                suffix_list = ', '.join(enabled_configs.keys())
                cmds.warning(f"未找到带有以下后缀的物体: {suffix_list}")
                
        except Exception as e:
            cmds.error(f"自动分材质失败: {str(e)}")
            
        return result
    
    def _get_color_description(self, color):
        """
        根据RGB值获取颜色描述
        
        Args:
            color (tuple): RGB颜色值 (0-1范围)
            
        Returns:
            str: 颜色描述
        """
        r, g, b = color
        
        # 预定义的颜色映射
        color_map = {
            (0.0, 0.8, 0.0): "绿色",
            (0.8, 0.0, 0.0): "红色",
            (0.0, 0.0, 0.8): "蓝色",
            (0.8, 0.8, 0.0): "黄色",
            (0.8, 0.0, 0.8): "紫色",
            (0.0, 0.8, 0.8): "青色",
            (0.8, 0.4, 0.0): "橙色",
            (0.5, 0.5, 0.5): "灰色",
            (1.0, 1.0, 1.0): "白色",
            (0.0, 0.0, 0.0): "黑色"
        }
        
        # 查找最接近的预定义颜色
        min_distance = float('inf')
        closest_color = "自定义颜色"
        
        for preset_color, name in color_map.items():
            distance = sum((a - b) ** 2 for a, b in zip(color, preset_color))
            if distance < min_distance:
                min_distance = distance
                closest_color = name
        
        # 如果距离很小，认为是匹配的
        if min_distance < 0.1:
            return closest_color
        else:
            return f"自定义颜色(R:{r:.1f},G:{g:.1f},B:{b:.1f})"
    
    def add_material_config(self, suffix, color, transparency=0.0, material_name=None, enabled=True):
        """
        添加材质配置的便捷方法
        
        Args:
            suffix (str): 后缀名称
            color (tuple): RGB颜色值 (0-1范围)
            transparency (float): 透明度值 (0-1范围)
            material_name (str): 材质名称
            enabled (bool): 是否启用
        """
        self.material_config.add_suffix_config(suffix, color, transparency, material_name, enabled)
    
    def remove_material_config(self, suffix):
        """
        移除材质配置的便捷方法
        
        Args:
            suffix (str): 要移除的后缀
        """
        self.material_config.remove_suffix_config(suffix)
    
    def update_material_transparency(self, suffix, transparency):
        """
        更新材质透明度的便捷方法
        
        Args:
            suffix (str): 后缀名称
            transparency (float): 透明度值 (0-1范围)
        """
        self.material_config.update_suffix_transparency(suffix, transparency)
    
    def update_material_color(self, suffix, color):
        """
        更新材质颜色的便捷方法
        
        Args:
            suffix (str): 后缀名称
            color (tuple): RGB颜色值 (0-1范围)
        """
        self.material_config.update_suffix_color(suffix, color)
    
    def get_material_configs(self):
        """
        获取所有材质配置
        
        Returns:
            dict: 材质配置字典
        """
        return self.material_config.material_configs.copy()

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

def auto_assign_materials(global_transparency=None):
    """
    便捷函数：自动为不同后缀的模型分配对应颜色的Lambert材质
    
    Args:
        global_transparency (float, optional): 全局透明度值 (0-1范围)，如果提供则覆盖各后缀的独立透明度
        
    Returns:
        dict: 分配结果统计
    """
    return baking_renamer.auto_assign_materials(global_transparency)

def add_material_config(suffix, color, transparency=0.0, material_name=None, enabled=True):
    """
    便捷函数：添加材质配置
    
    Args:
        suffix (str): 后缀名称
        color (tuple): RGB颜色值 (0-1范围)
        transparency (float): 透明度值 (0-1范围)
        material_name (str): 材质名称
        enabled (bool): 是否启用
    """
    return baking_renamer.add_material_config(suffix, color, transparency, material_name, enabled)

def update_material_transparency(suffix, transparency):
    """
    便捷函数：更新材质透明度
    
    Args:
        suffix (str): 后缀名称
        transparency (float): 透明度值 (0-1范围)
    """
    return baking_renamer.update_material_transparency(suffix, transparency)

def update_material_color(suffix, color):
    """
    便捷函数：更新材质颜色
    
    Args:
        suffix (str): 后缀名称
        color (tuple): RGB颜色值 (0-1范围)
    """
    return baking_renamer.update_material_color(suffix, color)

def get_material_configs():
    """
    便捷函数：获取材质配置
    
    Returns:
        dict: 材质配置字典
    """
    return baking_renamer.get_material_configs()

if __name__ == "__main__":
    print("Maya烘焙命名工具已加载")
    print("使用方法:")
    print("  rename_to_low() - 添加_low后缀")
    print("  rename_to_high() - 添加_high后缀")
    print("  auto_rename() - 自动重命名模式")
    print("  auto_assign_materials(global_transparency=None) - 自动分材质")
    print("  add_material_config(suffix, color, transparency=0.0) - 添加材质配置")
    print("  update_material_transparency(suffix, transparency) - 更新透明度")
    print("  update_material_color(suffix, color) - 更新颜色")
    print("  get_material_configs() - 获取材质配置")
    print("  undo_rename() - 撤销上一次重命名")
    print("  clear_rename_history() - 清空历史记录")
    print("")
    print("材质配置示例:")
    print("  add_material_config('_custom', (1.0, 0.5, 0.0), 0.3) - 添加橙色半透明材质")
    print("  update_material_transparency('_low', 0.5) - 设置_low材质50%透明度")