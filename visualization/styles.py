import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 全局样式配置
class StyleConfig:
    """图表样式配置"""
    
    def __init__(self):
        # 中文字体设置
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 基础设置
        plt.rcParams['font.size'] = 11
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 600
        
        # 图表样式
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # 颜色配置
        self.colors = {
            'categorical': [
                '#E74C3C', '#3498DB', '#2ECC71', '#9B59B6',
                '#F39C12', '#1ABC9C', '#E67E22', '#34495E'
            ],
            'continuous': [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
            ],
            'heatmap': 'YlOrRd',
            'background': '#FFFFFF',
            'text': '#000000',
            'grid': '#E0E0E0'
        }
        
        # 图表尺寸
        self.figure_sizes = {
            'small': (6, 4),
            'medium': (10, 6),
            'large': (12, 8),
            'wide': (14, 6),
            'tall': (8, 10)
        }
        
        # 字体设置
        self.fonts = {
            'title': {'fontsize': 16, 'fontweight': 'bold'},
            'subtitle': {'fontsize': 14, 'fontweight': 'semibold'},
            'axis_label': {'fontsize': 12, 'fontweight': 'bold'},
            'tick_label': {'fontsize': 10},
            'annotation': {'fontsize': 9, 'fontweight': 'bold'}
        }
        
        # 图表元素设置
        self.elements = {
            'linewidth': 1.5,
            'edgecolor': '#000000',
            'alpha': 0.7,
            'capsize': 5,
            'marker_size': 8,
            'grid_alpha': 0.3
        }
    
    def get_color(self, index=None, category=None):
        """获取颜色
        
        Args:
            index: 颜色索引
            category: 颜色类别
            
        Returns:
            str: 颜色代码
        """
        if category == 'categorical':
            return self.colors['categorical'][index % len(self.colors['categorical'])]
        elif category == 'continuous':
            return self.colors['continuous'][index % len(self.colors['continuous'])]
        else:
            return self.colors['categorical'][index % len(self.colors['categorical'])]
    
    def get_figure_size(self, size='medium'):
        """获取图表尺寸
        
        Args:
            size: 尺寸类型
            
        Returns:
            tuple: 宽高
        """
        return self.figure_sizes.get(size, self.figure_sizes['medium'])
    
    def apply_style(self):
        """应用样式"""
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.size'] = 11
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 600
        plt.style.use('seaborn-v0_8-whitegrid')

# 创建全局样式实例
style_config = StyleConfig()