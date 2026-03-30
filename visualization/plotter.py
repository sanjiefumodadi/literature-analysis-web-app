import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import logging
from .styles import style_config

logger = logging.getLogger(__name__)

class PlotGenerator:
    """图表生成器"""
    
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.style_config = style_config
        self.style_config.apply_style()
    
    def generate_all(self, data, analysis_results):
        """生成所有图表
        
        Args:
            data: 数据
            analysis_results: 分析结果
            
        Returns:
            list: 生成的图表路径
        """
        logger.info("开始生成图表...")
        
        figures = []
        
        # 1. 描述性统计图表
        figures.extend(self._generate_descriptive_plots(data))
        
        # 2. 分类变量图表
        if any('categorical_' in key for key in analysis_results):
            figures.extend(self._generate_categorical_plots(data, analysis_results))
        
        # 3. 数量变量图表
        if 'descriptive_stats' in analysis_results:
            figures.extend(self._generate_quantitative_plots(data, analysis_results))
        
        # 4. 相关性图表
        if 'correlation_matrix' in analysis_results:
            figures.extend(self._generate_correlation_plots(analysis_results))
        
        logger.info(f"图表生成完成，共生成{len(figures)}个图表")
        return figures
    
    def _generate_descriptive_plots(self, data):
        """生成描述性统计图表"""
        figures = []
        
        # 选择数值变量
        numerical_vars = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]
        
        if numerical_vars:
            # 直方图
            fig_path = self._plot_histograms(data, numerical_vars)
            if fig_path:
                figures.append(fig_path)
            
            # 箱线图
            fig_path = self._plot_boxplots(data, numerical_vars)
            if fig_path:
                figures.append(fig_path)
        
        return figures
    
    def _generate_categorical_plots(self, data, analysis_results):
        """生成分类变量图表"""
        figures = []
        
        # 识别分类变量
        categorical_vars = [key.replace('categorical_', '') for key in analysis_results if 'categorical_' in key]
        
        for var in categorical_vars:
            if var in data.columns:
                # 条形图
                fig_path = self._plot_bar_chart(data, var)
                if fig_path:
                    figures.append(fig_path)
                
                # 饼图
                fig_path = self._plot_pie_chart(data, var)
                if fig_path:
                    figures.append(fig_path)
        
        # 列联表热图
        if 'chi2_tests' in analysis_results:
            for test_name, test_result in analysis_results['chi2_tests'].items():
                fig_path = self._plot_contingency_heatmap(test_result['contingency_table'], test_name)
                if fig_path:
                    figures.append(fig_path)
        
        return figures
    
    def _generate_quantitative_plots(self, data, analysis_results):
        """生成数量变量图表"""
        figures = []
        
        # 小提琴图
        numerical_vars = analysis_results['descriptive_stats'].index.tolist()
        fig_path = self._plot_violin_plots(data, numerical_vars)
        if fig_path:
            figures.append(fig_path)
        
        # 散点图矩阵
        if len(numerical_vars) >= 3:
            fig_path = self._plot_scatter_matrix(data, numerical_vars[:4])  # 最多4个变量
            if fig_path:
                figures.append(fig_path)
        
        return figures
    
    def _generate_correlation_plots(self, analysis_results):
        """生成相关性图表"""
        figures = []
        
        # 相关性热图
        correlation_data = analysis_results['correlation_matrix']
        
        if 'pearson' in correlation_data:
            fig_path = self._plot_correlation_heatmap(correlation_data['pearson'], 'pearson')
            if fig_path:
                figures.append(fig_path)
        
        if 'spearman' in correlation_data:
            fig_path = self._plot_correlation_heatmap(correlation_data['spearman'], 'spearman')
            if fig_path:
                figures.append(fig_path)
        
        return figures
    
    def _plot_histograms(self, data, variables):
        """绘制直方图"""
        logger.info(f"绘制直方图: {variables}")
        
        n_vars = len(variables)
        n_cols = min(3, n_vars)
        n_rows = (n_vars + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = np.array(axes).reshape(-1)
        
        for i, var in enumerate(variables):
            ax = axes[i]
            ax.hist(data[var].dropna(), bins=20, color=self.style_config.get_color(i), 
                   alpha=0.7, edgecolor='black', linewidth=1)
            ax.set_title(f'{var}分布', **self.style_config.fonts['subtitle'])
            ax.set_xlabel(var, **self.style_config.fonts['axis_label'])
            ax.set_ylabel('频率', **self.style_config.fonts['axis_label'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(alpha=self.style_config.elements['grid_alpha'])
        
        # 隐藏多余的子图
        for i in range(n_vars, len(axes)):
            axes[i].set_visible(False)
        
        fig.suptitle('数值变量分布直方图', **self.style_config.fonts['title'])
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        return self._save_figure(fig, '直方图_数值变量分布')
    
    def _plot_boxplots(self, data, variables):
        """绘制箱线图"""
        logger.info(f"绘制箱线图: {variables}")
        
        fig, ax = plt.subplots(figsize=self.style_config.get_figure_size('wide'))
        
        box_data = [data[var].dropna() for var in variables]
        bp = ax.boxplot(box_data, labels=variables, patch_artist=True, 
                      showmeans=True, meanprops=dict(marker='D', markerfacecolor='red', markersize=6))
        
        # 设置颜色
        for patch, color in zip(bp['boxes'], [self.style_config.get_color(i) for i in range(len(variables))]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title('数值变量箱线图', **self.style_config.fonts['title'])
        ax.set_ylabel('值', **self.style_config.fonts['axis_label'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=self.style_config.elements['grid_alpha'])
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return self._save_figure(fig, '箱线图_数值变量分布')
    
    def _plot_bar_chart(self, data, variable):
        """绘制条形图"""
        logger.info(f"绘制条形图: {variable}")
        
        freq = data[variable].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=self.style_config.get_figure_size('medium'))
        
        bars = ax.bar(freq.index.astype(str), freq.values, 
                     color=self.style_config.get_color(0), 
                     alpha=0.7, edgecolor='black', linewidth=1)
        
        # 添加数值标签
        for bar, val in zip(bars, freq.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                   f'{val}', ha='center', va='bottom', **self.style_config.fonts['annotation'])
        
        ax.set_title(f'{variable}分布', **self.style_config.fonts['title'])
        ax.set_xlabel(variable, **self.style_config.fonts['axis_label'])
        ax.set_ylabel('频率', **self.style_config.fonts['axis_label'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=self.style_config.elements['grid_alpha'])
        
        plt.tight_layout()
        
        return self._save_figure(fig, f'条形图_{variable}_分布')
    
    def _plot_pie_chart(self, data, variable):
        """绘制饼图"""
        logger.info(f"绘制饼图: {variable}")
        
        freq = data[variable].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=self.style_config.get_figure_size('small'))
        
        wedges, texts, autotexts = ax.pie(freq.values, labels=freq.index.astype(str), 
                                         autopct='%1.1f%%', startangle=90,
                                         colors=[self.style_config.get_color(i) for i in range(len(freq))],
                                         wedgeprops={'edgecolor': 'black', 'linewidth': 1})
        
        for autotext in autotexts:
            autotext.set_fontweight('bold')
        
        ax.set_title(f'{variable}构成', **self.style_config.fonts['title'])
        ax.axis('equal')
        
        plt.tight_layout()
        
        return self._save_figure(fig, f'饼图_{variable}_构成')
    
    def _plot_violin_plots(self, data, variables):
        """绘制小提琴图"""
        logger.info(f"绘制小提琴图: {variables}")
        
        n_vars = len(variables)
        n_cols = min(3, n_vars)
        n_rows = (n_vars + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = np.array(axes).reshape(-1)
        
        for i, var in enumerate(variables):
            ax = axes[i]
            sns.violinplot(data=data, y=var, ax=ax, 
                          color=self.style_config.get_color(i), alpha=0.7)
            ax.set_title(f'{var}分布', **self.style_config.fonts['subtitle'])
            ax.set_ylabel(var, **self.style_config.fonts['axis_label'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(alpha=self.style_config.elements['grid_alpha'])
        
        # 隐藏多余的子图
        for i in range(n_vars, len(axes)):
            axes[i].set_visible(False)
        
        fig.suptitle('数值变量小提琴图', **self.style_config.fonts['title'])
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        return self._save_figure(fig, '小提琴图_数值变量分布')
    
    def _plot_scatter_matrix(self, data, variables):
        """绘制散点图矩阵"""
        logger.info(f"绘制散点图矩阵: {variables}")
        
        fig = sns.pairplot(data[variables].dropna(), 
                          diag_kind='kde', 
                          plot_kws={'alpha': 0.5, 's': 50, 'edgecolor': 'k'})
        
        fig.fig.suptitle('变量相关性散点图矩阵', **self.style_config.fonts['title'])
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        return self._save_figure(fig.fig, '散点图矩阵_变量相关性')
    
    def _plot_correlation_heatmap(self, corr_matrix, method):
        """绘制相关性热图"""
        logger.info(f"绘制相关性热图: {method}")
        
        fig, ax = plt.subplots(figsize=self.style_config.get_figure_size('large'))
        
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', 
                   cmap=self.style_config.colors['heatmap'], ax=ax,
                   cbar_kws={'label': '相关系数'})
        
        ax.set_title(f'{method.capitalize()}相关系数热图', **self.style_config.fonts['title'])
        
        plt.tight_layout()
        
        return self._save_figure(fig, f'热图_{method}_相关性')
    
    def _plot_contingency_heatmap(self, contingency_table, test_name):
        """绘制列联表热图"""
        logger.info(f"绘制列联表热图: {test_name}")
        
        fig, ax = plt.subplots(figsize=self.style_config.get_figure_size('medium'))
        
        sns.heatmap(contingency_table, annot=True, fmt='d', 
                   cmap=self.style_config.colors['heatmap'], ax=ax,
                   cbar_kws={'label': '频率'})
        
        ax.set_title(f'{test_name}列联表', **self.style_config.fonts['title'])
        
        plt.tight_layout()
        
        return self._save_figure(fig, f'热图_{test_name}_列联表')
    
    def _save_figure(self, fig, filename):
        """保存图表
        
        Args:
            fig: 图表对象
            filename: 文件名
            
        Returns:
            list: 保存的文件路径
        """
        try:
            # 保存为PNG
            png_path = self.file_manager.save_figure(fig, filename, 'png')
            
            # 保存为PDF
            pdf_path = self.file_manager.save_figure(fig, filename, 'pdf')
            
            # 保存为TIFF
            tiff_path = self.file_manager.save_figure(fig, filename, 'tiff')
            
            plt.close(fig)
            
            return [png_path, pdf_path, tiff_path]
        except Exception as e:
            logger.error(f"保存图表失败: {str(e)}")
            plt.close(fig)
            return None