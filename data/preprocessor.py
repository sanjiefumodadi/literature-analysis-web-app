import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """数据预处理器"""
    
    def __init__(self):
        pass
    
    def preprocess(self, data):
        """预处理数据
        
        Args:
            data: 清洗后的数据
            
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        logger.info("开始数据预处理...")
        
        # 1. 变量类型识别
        self._identify_variable_types(data)
        
        # 2. 标准化处理
        data = self._standardize(data)
        
        # 3. 分类变量编码
        data = self._encode_categorical(data)
        
        logger.info("数据预处理完成")
        return data
    
    def _identify_variable_types(self, data):
        """识别变量类型"""
        numerical_vars = self.get_quantitative_variables(data)
        categorical_vars = self.get_categorical_variables(data)
        
        logger.info(f"变量类型识别结果:")
        logger.info(f"  - 数量变量: {len(numerical_vars)}个")
        if numerical_vars:
            logger.info(f"    {numerical_vars}")
        logger.info(f"  - 分类变量: {len(categorical_vars)}个")
        if categorical_vars:
            logger.info(f"    {categorical_vars}")
    
    def get_quantitative_variables(self, data):
        """获取数量变量"""
        numerical_vars = []
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                # 检查唯一值数量，排除可能的分类变量
                unique_count = data[col].nunique()
                if unique_count > 5:  # 阈值可以调整
                    numerical_vars.append(col)
        return numerical_vars
    
    def get_categorical_variables(self, data):
        """获取分类变量"""
        categorical_vars = []
        for col in data.columns:
            if pd.api.types.is_categorical_dtype(data[col]) or \
               pd.api.types.is_object_dtype(data[col]) or \
               (pd.api.types.is_numeric_dtype(data[col]) and data[col].nunique() <= 5):
                categorical_vars.append(col)
        return categorical_vars
    
    def _standardize(self, data):
        """标准化处理"""
        numerical_vars = self.get_quantitative_variables(data)
        
        for var in numerical_vars:
            # Z-score标准化
            mean = data[var].mean()
            std = data[var].std()
            if std > 0:
                data[f'{var}_std'] = (data[var] - mean) / std
                logger.info(f"  - 标准化变量: {var}")
        
        return data
    
    def _encode_categorical(self, data):
        """分类变量编码"""
        categorical_vars = self.get_categorical_variables(data)
        
        for var in categorical_vars:
            # 检查是否已经是数值类型
            if not pd.api.types.is_numeric_dtype(data[var]):
                # 尝试自动编码
                try:
                    # 创建映射
                    unique_values = data[var].unique()
                    value_map = {v: i+1 for i, v in enumerate(unique_values)}
                    data[f'{var}_encoded'] = data[var].map(value_map)
                    logger.info(f"  - 编码分类变量: {var}")
                    logger.info(f"    编码映射: {value_map}")
                except Exception as e:
                    logger.warning(f"  - 编码分类变量 {var} 失败: {str(e)}")
        
        return data
    
    def split_data(self, data, target=None, test_size=0.2):
        """拆分数据集"""
        from sklearn.model_selection import train_test_split
        
        if target:
            X = data.drop(target, axis=1)
            y = data[target]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            return X_train, X_test, y_train, y_test
        else:
            train, test = train_test_split(data, test_size=test_size, random_state=42)
            return train, test
    
    def feature_selection(self, data, target, method='correlation', threshold=0.3):
        """特征选择"""
        if method == 'correlation':
            # 基于相关性的特征选择
            corr_matrix = data.corr()
            if target in corr_matrix:
                corr_with_target = corr_matrix[target].abs()
                selected_features = corr_with_target[corr_with_target > threshold].index.tolist()
                if target in selected_features:
                    selected_features.remove(target)
                logger.info(f"  - 基于相关性选择特征: {selected_features}")
                return selected_features
        
        return data.columns.tolist()