"""
日志系统模块
用于记录程序运行日志，方便用户反馈问题
日志保存到用户可访问的位置：%%LOCALAPPDATA%%\\TLM编辑器\\logs\\
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path


class Logger:
    """日志管理器"""
    
    _logger = None
    _log_dir = None
    _log_file = None
    
    @classmethod
    def setup(cls, app_name="TLM编辑器", log_level=logging.DEBUG):
        """设置日志系统"""
        if cls._logger is not None:
            return cls._logger
        
        # 确定日志目录
        if getattr(sys, 'frozen', False):
            # 打包后：使用exe同级目录下的logs文件夹
            exe_dir = os.path.dirname(sys.executable)
            cls._log_dir = Path(exe_dir) / "logs"
        else:
            # 开发时：使用项目根目录的 logs 文件夹
            project_dir = Path(__file__).parent.parent
            cls._log_dir = project_dir / "logs"
        
        # 创建日志目录
        cls._log_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成日志文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cls._log_file = cls._log_dir / f"{app_name}_{timestamp}.log"
        
        # 创建logger
        cls._logger = logging.getLogger(app_name)
        cls._logger.setLevel(log_level)
        
        # 清除已有的handlers
        cls._logger.handlers.clear()
        
        # 文件handler - 记录所有级别
        file_handler = logging.FileHandler(cls._log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        cls._logger.addHandler(file_handler)
        
        # 控制台handler - 只显示WARNING及以上
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_format = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_format)
        cls._logger.addHandler(console_handler)
        
        # 记录启动信息
        cls._logger.info("=" * 60)
        cls._logger.info(f"{app_name} 启动")
        cls._logger.info(f"日志文件: {cls._log_file}")
        cls._logger.info(f"Python版本: {sys.version}")
        cls._logger.info(f"是否打包: {getattr(sys, 'frozen', False)}")
        cls._logger.info("=" * 60)
        
        return cls._logger
    
    @classmethod
    def get_logger(cls):
        """获取logger实例"""
        if cls._logger is None:
            cls.setup()
        return cls._logger
    
    @classmethod
    def get_log_file_path(cls):
        """获取日志文件路径"""
        if cls._log_file:
            return str(cls._log_file)
        return None
    
    @classmethod
    def get_log_directory(cls):
        """获取日志目录路径"""
        if cls._log_dir:
            return str(cls._log_dir)
        return None
    
    @classmethod
    def cleanup_old_logs(cls, days=7):
        """清理7天前的日志文件"""
        if not cls._log_dir or not cls._log_dir.exists():
            return
        
        cutoff = datetime.now()
        for log_file in cls._log_dir.glob("*.log"):
            # 从文件名提取时间戳
            try:
                file_time_str = log_file.stem.split('_')[-2]  # 提取日期部分
                file_time = datetime.strptime(file_time_str, "%Y%m%d")
                if (cutoff - file_time).days > days:
                    log_file.unlink()
                    if cls._logger:
                        cls._logger.info(f"已清理旧日志: {log_file.name}")
            except Exception:
                pass


def setup_exception_logging():
    """设置全局异常捕获，将未捕获的异常记录到日志"""
    def exception_handler(exc_type, exc_value, exc_traceback):
        logger = Logger.get_logger()
        logger.critical(
            "未捕获的异常",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        # 同时输出到控制台
        print(f"\n[错误] {exc_type.__name__}: {exc_value}")
        print(f"详细信息已保存到日志文件: {Logger.get_log_file_path()}")
    
    # 设置全局异常处理器
    sys.excepthook = exception_handler


# ========================================
# 使用示例
# ========================================
if __name__ == '__main__':
    # 设置日志
    logger = Logger.setup()
    
    # 设置异常捕获
    setup_exception_logging()
    
    # 测试日志
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    print(f"\n日志文件位置: {Logger.get_log_file_path()}")
    print(f"日志目录: {Logger.get_log_directory()}")
