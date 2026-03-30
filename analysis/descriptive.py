import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DescriptiveAnalyzer:
    """描述性统计分析器"""
    
    def __init__(self):
        pass
    
    def descriptive_statistics(self, data):
        """计算描述性统计
        
        Args:
            data: 数据
            
        Returns:
            pd.DataFrame: 描述性统计结果
        """
        logger.info("计算描述性统计...")
        
        stats = data.describe().T
        stats['skewness'] = data.skew()
        stats['kurtosis'] = data.kurtosis()
        stats['missing'] = data.isnull().sum()
        stats['unique'] = data.nunique()
        
        # 重新排序列
        cols = ['count', 'missing', 'unique', 'mean', 'std', 'min', 
                '25%', '50%', '75%', 'max', 'skewness', 'kurtosis']
        stats = stats[cols]
        
        logger.info("描述性统计计算完成")
        return stats
    
    def frequency_table(self, data):
        """计算频率表
        
        Args:
            data: 数据
            
        Returns:
            pd.DataFrame: 频率表
        """
        logger.info("计算频率表...")
        
        freq = data.value_counts().sort_index()
        freq_table = pd.DataFrame({
            'value': freq.index,
            'frequency': freq.values,
            'percentage': (freq.values / len(data) * 100).round(2)
        })
        
        logger.info("频率表计算完成")
        return freq_table
    
    def correlation_matrix(self, data):
        """计算相关矩阵
        
        Args:
            data: 数据
            
        Returns:
            pd.DataFrame: 相关矩阵
        """
        logger.info("计算相关矩阵...")
        
        # 计算Pearson相关系数
        corr_matrix = data.corr(method='pearson')
        
        # 计算Spearman相关系数
        spearman_corr = data.corr(method='spearman')
        
        logger.info("相关矩阵计算完成")
        return {
            'pearson': corr_matrix,
            'spearman': spearman_corr
        }
    
    def group_statistics(self, data, group_var, target_vars):
        """分组统计
        
        Args:
            data: 数据
            group_var: 分组变量
            target_vars: 目标变量列表
            
        Returns:
            dict: 分组统计结果
        """
        logger.info(f"计算分组统计（按{group_var}）...")
        
        results = {}
        for var in target_vars:
            if var in data.columns:
                group_stats = data.groupby(group_var)[var].agg([
                    'count', 'mean', 'std', 'min', 'max', 'median'
                ]).round(2)
                results[var] = group_stats
                logger.info(f"  - {var}的分组统计完成")
        
        return results
    
    def percentile_analysis(self, data, percentiles=[10, 25, 50, 75, 90]):
        """百分位数分析
        
        Args:
            data: 数据
            percentiles: 百分位数列表
            
        Returns:
            pd.DataFrame: 百分位数分析结果
        """
        logger.info("计算百分位数...")
        
        percentile_data = {}
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                percentiles_values = data[col].quantile([p/100 for p in percentiles])
                percentile_data[col] = percentiles_values
        
        percentile_df = pd.DataFrame(percentile_data)
        percentile_df.index = [f'{p}%' for p in percentiles]
        
        logger.info("百分位数分析完成")
        return percentile_df
    
    def distribution_analysis(self, data, bins=10):
        """分布分析
        
        Args:
            data: 数据
            bins: 分箱数量
            
        Returns:
            dict: 分布分析结果
        """
        logger.info("进行分布分析...")
        
        results = {}
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                # 计算直方图数据
                hist, bin_edges = np.histogram(data[col], bins=bins)
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                
                results[col] = {
                    'hist': hist,
                    'bin_edges': bin_edges,
                    'bin_centers': bin_centers
                }
                logger.info(f"  - {col}的分布分析完成")
        
        return results
    
    def get_variable_summary(self, data):
        """获取变量摘要
        
        Args:
            data: 数据
            
        Returns:
            pd.DataFrame: 变量摘要
        """
        logger.info("生成变量摘要...")
        
        summary = []
        for col in data.columns:
            col_data = data[col]
            
            info = {
                'variable': col,
                'type': str(col_data.dtype),
                'non_missing': col_data.notnull().sum(),
                'missing': col_data.isnull().sum(),
                'unique_values': col_data.nunique()
            }
            
            if pd.api.types.is_numeric_dtype(col_data):
                info.update({
                    'mean': col_data.mean(),
                    'std': col_data.std(),
                    'min': col_data.min(),
                    'max': col_data.max()
                })
            else:
                info.update({
                    'top_value': col_data.mode().iloc[0] if not col_data.mode().empty else None,
                    'top_frequency': col_data.value_counts().iloc[0] if len(col_data.value_counts()) > 0 else 0
                })
            
            summary.append(info)
        
        summary_df = pd.DataFrame(summary)
        logger.info("变量摘要生成完成")
        return summary_df