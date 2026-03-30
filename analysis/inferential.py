import pandas as pd
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class InferentialAnalyzer:
    """推断统计分析器"""
    
    def __init__(self):
        self.alpha = 0.05
    
    def normality_test(self, data):
        """正态性检验
        
        Args:
            data: 数据
            
        Returns:
            dict: 正态性检验结果
        """
        logger.info("进行正态性检验...")
        
        results = {}
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                stat, p_value = stats.shapiro(data[col])
                results[col] = {
                    'statistic': stat,
                    'p_value': p_value,
                    'is_normal': p_value > self.alpha
                }
                logger.info(f"  - {col}: W={stat:.4f}, p={p_value:.4f}, {'正态' if p_value > self.alpha else '非正态'}")
        
        return results
    
    def homogeneity_test(self, data, group_var):
        """方差齐性检验
        
        Args:
            data: 数据
            group_var: 分组变量
            
        Returns:
            dict: 方差齐性检验结果
        """
        logger.info(f"进行方差齐性检验（按{group_var}分组）...")
        
        groups = data[group_var].unique()
        numerical_vars = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]
        
        results = {}
        for var in numerical_vars:
            group_data = [data[data[group_var] == group][var].dropna() for group in groups]
            if len(group_data) > 1:
                stat, p_value = stats.levene(*group_data)
                results[var] = {
                    'statistic': stat,
                    'p_value': p_value,
                    'is_homogeneous': p_value > self.alpha
                }
                logger.info(f"  - {var}: W={stat:.4f}, p={p_value:.4f}, {'方差齐' if p_value > self.alpha else '方差不齐'}")
        
        return results
    
    def t_test(self, group1, group2, equal_var=True):
        """t检验
        
        Args:
            group1: 第一组数据
            group2: 第二组数据
            equal_var: 是否方差齐
            
        Returns:
            dict: t检验结果
        """
        logger.info("进行t检验...")
        
        stat, p_value = stats.ttest_ind(group1, group2, equal_var=equal_var)
        results = {
            'statistic': stat,
            'p_value': p_value,
            'significant': p_value < self.alpha
        }
        
        logger.info(f"  t={stat:.4f}, p={p_value:.4f}, {'显著' if p_value < self.alpha else '不显著'}")
        return results
    
    def mann_whitney_test(self, group1, group2):
        """Mann-Whitney U检验
        
        Args:
            group1: 第一组数据
            group2: 第二组数据
            
        Returns:
            dict: Mann-Whitney U检验结果
        """
        logger.info("进行Mann-Whitney U检验...")
        
        stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        results = {
            'statistic': stat,
            'p_value': p_value,
            'significant': p_value < self.alpha
        }
        
        logger.info(f"  U={stat:.4f}, p={p_value:.4f}, {'显著' if p_value < self.alpha else '不显著'}")
        return results
    
    def anova(self, data, group_var, target_vars):
        """方差分析
        
        Args:
            data: 数据
            group_var: 分组变量
            target_vars: 目标变量列表
            
        Returns:
            dict: 方差分析结果
        """
        logger.info(f"进行方差分析（按{group_var}分组）...")
        
        results = {}
        for var in target_vars:
            if var in data.columns:
                groups = [data[data[group_var] == group][var].dropna() for group in data[group_var].unique()]
                if len(groups) > 1:
                    stat, p_value = stats.f_oneway(*groups)
                    results[var] = {
                        'statistic': stat,
                        'p_value': p_value,
                        'significant': p_value < self.alpha
                    }
                    logger.info(f"  - {var}: F={stat:.4f}, p={p_value:.4f}, {'显著' if p_value < self.alpha else '不显著'}")
        
        return results
    
    def kruskal_wallis_test(self, data, group_var, target_vars):
        """Kruskal-Wallis检验
        
        Args:
            data: 数据
            group_var: 分组变量
            target_vars: 目标变量列表
            
        Returns:
            dict: Kruskal-Wallis检验结果
        """
        logger.info(f"进行Kruskal-Wallis检验（按{group_var}分组）...")
        
        results = {}
        for var in target_vars:
            if var in data.columns:
                groups = [data[data[group_var] == group][var].dropna() for group in data[group_var].unique()]
                if len(groups) > 1:
                    stat, p_value = stats.kruskal(*groups)
                    results[var] = {
                        'statistic': stat,
                        'p_value': p_value,
                        'significant': p_value < self.alpha
                    }
                    logger.info(f"  - {var}: H={stat:.4f}, p={p_value:.4f}, {'显著' if p_value < self.alpha else '不显著'}")
        
        return results
    
    def chi_square_test(self, data, categorical_vars):
        """卡方检验
        
        Args:
            data: 数据
            categorical_vars: 分类变量列表
            
        Returns:
            dict: 卡方检验结果
        """
        logger.info("进行卡方检验...")
        
        results = {}
        for i in range(len(categorical_vars)):
            for j in range(i+1, len(categorical_vars)):
                var1 = categorical_vars[i]
                var2 = categorical_vars[j]
                
                contingency_table = pd.crosstab(data[var1], data[var2])
                stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                
                results[f'{var1}_vs_{var2}'] = {
                    'statistic': stat,
                    'p_value': p_value,
                    'dof': dof,
                    'contingency_table': contingency_table,
                    'expected': expected,
                    'significant': p_value < self.alpha
                }
                
                logger.info(f"  - {var1} vs {var2}: χ²={stat:.4f}, df={dof}, p={p_value:.4f}, {'显著' if p_value < self.alpha else '不显著'}")
        
        return results
    
    def pairwise_comparison(self, data, group_var, target_var, method='tukey'):
        """多重比较
        
        Args:
            data: 数据
            group_var: 分组变量
            target_var: 目标变量
            method: 比较方法
            
        Returns:
            dict: 多重比较结果
        """
        logger.info(f"进行多重比较（{method}方法）...")
        
        try:
            from statsmodels.stats.multicomp import MultiComparison
            
            mc = MultiComparison(data[target_var], data[group_var])
            
            if method == 'tukey':
                result = mc.tukeyhsd()
            elif method == 'duncan':
                result = mc.duncan()
            else:
                result = mc.tukeyhsd()
            
            logger.info(f"  多重比较完成: {method}")
            return {
                'method': method,
                'result': result,
                'summary': str(result)
            }
        except Exception as e:
            logger.error(f"多重比较失败: {str(e)}")
            return {'error': str(e)}
    
    def choose_test_method(self, data, group_var, target_var):
        """选择合适的检验方法
        
        Args:
            data: 数据
            group_var: 分组变量
            target_var: 目标变量
            
        Returns:
            str: 推荐的检验方法
        """
        # 正态性检验
        normality = self.normality_test(data[[target_var]])[target_var]
        
        # 方差齐性检验
        homogeneity = self.homogeneity_test(data, group_var).get(target_var, {'is_homogeneous': True})
        
        # 分组数量
        group_count = data[group_var].nunique()
        
        if group_count == 2:
            if normality['is_normal']:
                if homogeneity['is_homogeneous']:
                    return 't-test'
                else:
                    return 'welch-t-test'
            else:
                return 'mann-whitney'
        else:
            if normality['is_normal']:
                if homogeneity['is_homogeneous']:
                    return 'anova'
                else:
                    return 'welch-anova'
            else:
                return 'kruskal-wallis'
    
    def run_appropriate_test(self, data, group_var, target_var):
        """运行合适的检验
        
        Args:
            data: 数据
            group_var: 分组变量
            target_var: 目标变量
            
        Returns:
            dict: 检验结果
        """
        method = self.choose_test_method(data, group_var, target_var)
        logger.info(f"选择检验方法: {method}")
        
        if method == 't-test':
            groups = data[group_var].unique()
            if len(groups) == 2:
                group1 = data[data[group_var] == groups[0]][target_var].dropna()
                group2 = data[data[group_var] == groups[1]][target_var].dropna()
                return self.t_test(group1, group2, equal_var=True)
        elif method == 'mann-whitney':
            groups = data[group_var].unique()
            if len(groups) == 2:
                group1 = data[data[group_var] == groups[0]][target_var].dropna()
                group2 = data[data[group_var] == groups[1]][target_var].dropna()
                return self.mann_whitney_test(group1, group2)
        elif method == 'anova':
            return self.anova(data, group_var, [target_var])[target_var]
        elif method == 'kruskal-wallis':
            return self.kruskal_wallis_test(data, group_var, [target_var])[target_var]
        
        return {'error': '无法选择合适的检验方法'}
    
    def get_significance_symbol(self, p_value):
        """获取显著性符号
        
        Args:
            p_value: P值
            
        Returns:
            str: 显著性符号
        """
        if p_value < 0.001:
            return '***'
        elif p_value < 0.01:
            return '**'
        elif p_value < 0.05:
            return '*'
        else:
            return 'ns'