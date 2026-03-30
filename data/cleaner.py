import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        pass
    
    def clean(self, data):
        """清洗数据
        
        Args:
            data: 原始数据
            
        Returns:
            pd.DataFrame: 清洗后的数据
        """
        logger.info("开始数据清洗...")
        
        # 1. 去除重复行
        data = self._remove_duplicates(data)
        
        # 2. 处理缺失值
        data = self._handle_missing_values(data)
        
        # 3. 处理异常值
        data = self._handle_outliers(data)
        
        # 4. 数据类型转换
        data = self._convert_data_types(data)
        
        logger.info("数据清洗完成")
        return data
    
    def _remove_duplicates(self, data):
        """去除重复行"""
        before = len(data)
        data = data.drop_duplicates()
        after = len(data)
        if before != after:
            logger.info(f"去除{before - after}个重复行")
        return data
    
    def _handle_missing_values(self, data):
        """处理缺失值"""
        # 统计缺失值
        missing_stats = data.isnull().sum()
        missing_vars = missing_stats[missing_stats > 0]
        
        if len(missing_vars) > 0:
            logger.info("缺失值统计:")
            for var, count in missing_vars.items():
                percent = (count / len(data)) * 100
                logger.info(f"  - {var}: {count}个缺失值 ({percent:.2f}%)")
        
        # 对于分类变量，使用众数填充
        categorical_vars = data.select_dtypes(include=['object', 'category']).columns
        for var in categorical_vars:
            if data[var].isnull().sum() > 0:
                mode = data[var].mode()[0]
                data[var] = data[var].fillna(mode)
                logger.info(f"  - 填充分类变量 {var} 的缺失值为众数: {mode}")
        
        # 对于数值变量，使用均值填充
        numerical_vars = data.select_dtypes(include=['int64', 'float64']).columns
        for var in numerical_vars:
            if data[var].isnull().sum() > 0:
                mean_val = data[var].mean()
                data[var] = data[var].fillna(mean_val)
                logger.info(f"  - 填充数值变量 {var} 的缺失值为均值: {mean_val:.2f}")
        
        return data
    
    def _handle_outliers(self, data):
        """处理异常值"""
        numerical_vars = data.select_dtypes(include=['int64', 'float64']).columns
        
        for var in numerical_vars:
            # 使用IQR方法检测异常值
            Q1 = data[var].quantile(0.25)
            Q3 = data[var].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # 统计异常值
            outliers = data[(data[var] < lower_bound) | (data[var] > upper_bound)]
            if len(outliers) > 0:
                logger.info(f"  - {var}: 检测到{len(outliers)}个异常值")
                # 用上下限替换异常值
                data[var] = data[var].clip(lower=lower_bound, upper=upper_bound)
                logger.info(f"  - 已将{var}的异常值限制在合理范围内")
        
        return data
    
    def _convert_data_types(self, data):
        """数据类型转换"""
        # 尝试将适合的列转换为数值类型
        for col in data.columns:
            if data[col].dtype == 'object':
                try:
                    # 尝试转换为数值类型
                    data[col] = pd.to_numeric(data[col], errors='ignore')
                except Exception:
                    pass
        
        return data
    
    def get_cleaning_report(self, data):
        """生成清洗报告"""
        report = {
            'total_samples': len(data),
            'total_variables': len(data.columns),
            'missing_values': data.isnull().sum().to_dict(),
            'data_types': data.dtypes.to_dict()
        }
        return report