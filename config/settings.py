# 配置文件

# 全局设置
GLOBAL_SETTINGS = {
    # 图表设置
    'figure': {
        'dpi': 600,
        'font_size': 11,
        'font_family': ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi'],
        'figure_size': (10, 6),
        'dpi_output': 600
    },
    
    # 分析设置
    'analysis': {
        'alpha': 0.05,
        'effect_size_thresholds': {
            'small': 0.2,
            'medium': 0.5,
            'large': 0.8
        }
    },
    
    # 输出设置
    'output': {
        'formats': ['png', 'pdf', 'tiff'],
        'figure_dirs': {
            'png': 'figures/png',
            'pdf': 'figures/pdf',
            'tiff': 'figures/tiff'
        }
    }
}

# 颜色配置
COLORS = {
    # 分类变量颜色
    'categorical': [
        '#E74C3C', '#3498DB', '#2ECC71', '#9B59B6',
        '#F39C12', '#1ABC9C', '#E67E22', '#34495E'
    ],
    
    # 连续变量颜色
    'continuous': [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
    ],
    
    # 热图颜色
    'heatmap': 'YlOrRd',
    
    # 其他颜色
    'background': '#FFFFFF',
    'text': '#000000',
    'grid': '#E0E0E0'
}

# 图表标题
CHART_TITLES = {
    'descriptive': '描述性统计',
    'categorical': '分类性状分布',
    'quantitative': '数量性状分布',
    'correlation': '相关性分析',
    'boxplot': '箱线图分析',
    'violinplot': '小提琴图分析',
    'scatterplot': '散点图分析',
    'heatmap': '相关性热图'
}

# 分析方法映射
ANALYSIS_METHODS = {
    'normality': 'Shapiro-Wilk',
    'homogeneity': 'Levene',
    'two_sample': 't-test',
    'non_parametric': 'Mann-Whitney U',
    'anova': 'ANOVA',
    'chi2': 'Chi-square'
}