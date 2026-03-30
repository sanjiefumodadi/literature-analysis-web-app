import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class DataReader:
    """数据读取器"""
    
    def __init__(self):
        pass
    
    def read_file(self, file_path):
        """读取数据文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            pd.DataFrame: 读取的数据
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext in ['.txt', '.tsv']:
                logger.info(f"读取文本文件: {file_path}")
                return self._read_txt(file_path)
            elif file_ext == '.csv':
                logger.info(f"读取CSV文件: {file_path}")
                return self._read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                logger.info(f"读取Excel文件: {file_path}")
                return self._read_excel(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            raise
    
    def _read_txt(self, file_path):
        """读取文本文件"""
        try:
            # 自动检测分隔符
            return pd.read_csv(file_path, sep=None, engine='python')
        except Exception:
            # 尝试使用制表符分隔
            return pd.read_csv(file_path, sep='\t')
    
    def _read_csv(self, file_path):
        """读取CSV文件"""
        return pd.read_csv(file_path, encoding='utf-8')
    
    def _read_excel(self, file_path):
        """读取Excel文件"""
        return pd.read_excel(file_path)
    
    def detect_delimiter(self, file_path):
        """检测文件分隔符"""
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
        
        delimiters = ['\t', ',', ';', ' ']
        for delimiter in delimiters:
            if delimiter in first_line:
                return delimiter
        
        return '\t'  # 默认使用制表符