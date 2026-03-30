import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EffectSizeCalculator:
    """效应量计算器"""
    
    def __init__(self):
        self.thresholds = {
            'small': 0.2,
            'medium': 0.5,
            'large': 0.8
        }
    
    def cohens_d(self, group1, group2):
        """计算Cohen's d
        
        Args:
            group1: 第一组数据
            group2: 第二组数据
            
        Returns:
            dict: Cohen's d结果
        """
        logger.info("计算Cohen's d...")
        
        mean1 = group1.mean()
        mean2 = group2.mean()
        std1 = group1.std()
        std2 = group2.std()
        n1 = len(group1)
        n2 = len(group2)
        
        # 计算合并标准差
        pooled_std = np.sqrt(
            ((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)
        )
        
        # 计算Cohen's d
        d = (mean1 - mean2) / pooled_std
        
        # 效应大小解释
        magnitude = self._interpret_effect_size(abs(d))
        
        logger.info(f"  Cohen's d = {d:.4f}, 效应大小: {magnitude}")
        
        return {
            'value': d,
            'magnitude': magnitude,
            'interpretation': f"{magnitude}效应"
        }
    
    def cramers_v(self, contingency_table):
        """计算Cramer's V
        
        Args:
            contingency_table: 列联表
            
        Returns:
            dict: Cramer's V结果
        """
        logger.info("计算Cramer's V...")
        
        # 计算卡方值
        from scipy.stats import chi2_contingency
        chi2, _, _, _ = chi2_contingency(contingency_table)
        
        # 计算样本量
        n = contingency_table.sum().sum()
        
        # 计算最小维度
        min_dim = min(contingency_table.shape) - 1
        
        # 计算Cramer's V
        v = np.sqrt(chi2 / (n * min_dim))
        
        # 效应大小解释（针对Cramer's V的阈值）
        if abs(v) < 0.1:
            magnitude = '微小'
        elif abs(v) < 0.3:
            magnitude = '小'
        elif abs(v) < 0.5:
            magnitude = '中等'
        else:
            magnitude = '大'
        
        logger.info(f"  Cramer's V = {v:.4f}, 效应大小: {magnitude}")
        
        return {
            'value': v,
            'magnitude': magnitude,
            'interpretation': f"{magnitude}效应"
        }
    
    def cliffs_delta(self, group1, group2):
        """计算Cliff's delta
        
        Args:
            group1: 第一组数据
            group2: 第二组数据
            
        Returns:
            dict: Cliff's delta结果
        """
        logger.info("计算Cliff's delta...")
        
        larger = 0
        smaller = 0
        equal = 0
        
        for x in group1:
            for y in group2:
                if x > y:
                    larger += 1
                elif x < y:
                    smaller += 1
                else:
                    equal += 1
        
        n1, n2 = len(group1), len(group2)
        delta = (larger - smaller) / (n1 * n2)
        
        # 效应大小解释
        if abs(delta) < 0.147:
            magnitude = '微小'
        elif abs(delta) < 0.33:
            magnitude = '小'
        elif abs(delta) < 0.474:
            magnitude = '中等'
        else:
            magnitude = '大'
        
        logger.info(f"  Cliff's delta = {delta:.4f}, 效应大小: {magnitude}")
        
        return {
            'value': delta,
            'magnitude': magnitude,
            'interpretation': f"{magnitude}效应"
        }
    
    def eta_squared(self, data, group_var, target_var):
        """计算Eta平方
        
        Args:
            data: 数据
            group_var: 分组变量
            target_var: 目标变量
            
        Returns:
            dict: Eta平方结果
        """
        logger.info("计算Eta平方...")
        
        # 计算总平方和
        grand_mean = data[target_var].mean()
        SST = ((data[target_var] - grand_mean) ** 2).sum()
        
        # 计算组间平方和
        group_means = data.groupby(group_var)[target_var].mean()
        group_counts = data.groupby(group_var).size()
        SSB = (group_counts * (group_means - grand_mean) ** 2).sum()
        
        # 计算Eta平方
        eta_squared = SSB / SST
        
        # 效应大小解释
        if abs(eta_squared) < 0.01:
            magnitude = '微小'
        elif abs(eta_squared) < 0.06:
            magnitude = '小'
        elif abs(eta_squared) < 0.14:
            magnitude = '中等'
        else:
            magnitude = '大'
        
        logger.info(f"  Eta squared = {eta_squared:.4f}, 效应大小: {magnitude}")
        
        return {
            'value': eta_squared,
            'magnitude': magnitude,
            'interpretation': f"{magnitude}效应"
        }
    
    def pearson_correlation(self, x, y):
        """计算Pearson相关系数
        
        Args:
            x: 第一个变量
            y: 第二个变量
            
        Returns:
            dict: Pearson相关系数结果
        """
        logger.info("计算Pearson相关系数...")
        
        from scipy.stats import pearsonr
        corr, p_value = pearsonr(x, y)
        
        # 效应大小解释
        if abs(corr) < 0.1:
            magnitude = '微弱'
        elif abs(corr) < 0.3:
            magnitude = '弱'
        elif abs(corr) < 0.5:
            magnitude = '中等'
        elif abs(corr) < 0.7:
            magnitude = '强'
        else:
            magnitude = '很强'
        
        logger.info(f"  Pearson r = {corr:.4f}, 效应大小: {magnitude}")
        
        return {
            'value': corr,
            'p_value': p_value,
            'magnitude': magnitude,
            'interpretation': f"{magnitude}相关"
        }
    
    def spearman_correlation(self, x, y):
        """计算Spearman相关系数
        
        Args:
            x: 第一个变量
            y: 第二个变量
            
        Returns:
            dict: Spearman相关系数结果
        """
        logger.info("计算Spearman相关系数...")
        
        from scipy.stats import spearmanr
        corr, p_value = spearmanr(x, y)
        
        # 效应大小解释
        if abs(corr) < 0.1:
            magnitude = '微弱'
        elif abs(corr) < 0.3:
            magnitude = '弱'
        elif abs(corr) < 0.5:
            magnitude = '中等'
        elif abs(corr) < 0.7:
            magnitude = '强'
        else:
            magnitude = '很强'
        
        logger.info(f"  Spearman r = {corr:.4f}, 效应大小: {magnitude}")
        
        return {
            'value': corr,
            'p_value': p_value,
            'magnitude': magnitude,
            'interpretation': f"{magnitude}相关"
        }
    
    def odds_ratio(self, contingency_table):
        """计算优势比
        
        Args:
            contingency_table: 2x2列联表
            
        Returns:
            dict: 优势比结果
        """
        logger.info("计算优势比...")
        
        if contingency_table.shape != (2, 2):
            logger.error("优势比仅适用于2x2列联表")
            return {'error': '仅适用于2x2列联表'}
        
        a = contingency_table.iloc[0, 0]
        b = contingency_table.iloc[0, 1]
        c = contingency_table.iloc[1, 0]
        d = contingency_table.iloc[1, 1]
        
        if b == 0 or c == 0:
            logger.error("列联表中存在零值，无法计算优势比")
            return {'error': '列联表中存在零值'}
        
        odds_ratio = (a * d) / (b * c)
        
        # 效应大小解释
        if odds_ratio < 0.67 or odds_ratio > 1.5:
            magnitude = '中等'
        elif odds_ratio < 0.5 or odds_ratio > 2:
            magnitude = '大'
        else:
            magnitude = '小'
        
        logger.info(f"  优势比 = {odds_ratio:.4f}, 效应大小: {magnitude}")
        
        return {
            'value': odds_ratio,
            'magnitude': magnitude,
            'interpretation': f"{magnitude}效应"
        }
    
    def _interpret_effect_size(self, effect_size):
        """解释效应大小
        
        Args:
            effect_size: 效应量值
            
        Returns:
            str: 效应大小解释
        """
        if effect_size < self.thresholds['small']:
            return '微小'
        elif effect_size < self.thresholds['medium']:
            return '小'
        elif effect_size < self.thresholds['large']:
            return '中等'
        else:
            return '大'
    
    def calculate_effect_size(self, data, test_type, **kwargs):
        """根据检验类型计算效应量
        
        Args:
            data: 数据
            test_type: 检验类型
            **kwargs: 其他参数
            
        Returns:
            dict: 效应量结果
        """
        if test_type == 't-test' or test_type == 'mann-whitney':
            group1 = kwargs.get('group1')
            group2 = kwargs.get('group2')
            if group1 is not None and group2 is not None:
                if test_type == 't-test':
                    return self.cohens_d(group1, group2)
                else:
                    return self.cliffs_delta(group1, group2)
        
        elif test_type == 'anova' or test_type == 'kruskal-wallis':
            group_var = kwargs.get('group_var')
            target_var = kwargs.get('target_var')
            if group_var is not None and target_var is not None:
                return self.eta_squared(data, group_var, target_var)
        
        elif test_type == 'chi-square':
            contingency_table = kwargs.get('contingency_table')
            if contingency_table is not None:
                if contingency_table.shape == (2, 2):
                    return self.odds_ratio(contingency_table)
                else:
                    return self.cramers_v(contingency_table)
        
        elif test_type == 'correlation':
            x = kwargs.get('x')
            y = kwargs.get('y')
            method = kwargs.get('method', 'pearson')
            if x is not None and y is not None:
                if method == 'pearson':
                    return self.pearson_correlation(x, y)
                else:
                    return self.spearman_correlation(x, y)
        
        logger.error("无法计算效应量：参数不足")
        return {'error': '参数不足'}
    
    def get_effect_size_report(self, data, analysis_results):
        """生成效应量报告
        
        Args:
            data: 数据
            analysis_results: 分析结果
            
        Returns:
            dict: 效应量报告
        """
        logger.info("生成效应量报告...")
        
        effect_size_results = {}
        
        # 处理分类变量效应量
        if 'chi2_tests' in analysis_results:
            for test_name, test_result in analysis_results['chi2_tests'].items():
                contingency_table = test_result['contingency_table']
                effect_size = self.calculate_effect_size(
                    data, 'chi-square', contingency_table=contingency_table
                )
                effect_size_results[test_name] = effect_size
        
        # 处理分组差异效应量
        if 'descriptive_stats' in analysis_results:
            # 这里可以根据实际情况添加效应量计算
            pass
        
        logger.info("效应量报告生成完成")
        return effect_size_results