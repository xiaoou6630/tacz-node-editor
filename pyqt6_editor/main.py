"""
NodeForge - TACZ Lua 状态机图形化编辑器
基于 PyQt6 的节点编辑器

运行此文件启动编辑器
"""

import sys
import os


def get_exe_dir():
    """获取可执行文件所在目录（兼容开发和打包）"""
    if getattr(sys, 'frozen', False):
        # 打包后的 exe 路径
        return os.path.dirname(sys.executable)
    else:
        # 开发时的项目根目录
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    # 添加项目根目录到路径（兼容开发和打包）
    if getattr(sys, 'frozen', False):
        # 打包后的 exe 路径
        exe_dir = os.path.dirname(sys.executable)
        # 添加 exe 所在目录
        sys.path.insert(0, exe_dir)
        
        # PyInstaller 解压后的临时目录（包含所有模块）
        if hasattr(sys, '_MEIPASS'):
            # _MEIPASS 是 exe 解压的临时目录，所有文件都在这里
            # 需要手动添加到 sys.path 才能导入模块
            sys.path.insert(0, sys._MEIPASS)
    else:
        # 开发时的项目根目录
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_dir)
    
    # ========================================
    # 初始化日志系统并重定向stdout/stderr
    # ========================================
    from pyqt6_editor.logger import Logger, setup_exception_logging
    logger = Logger.setup("TLM编辑器")
    
    # 重定向print到日志（--noconsole模式下需要）
    import io
    class LoggerWriter:
        def __init__(self, log_func):
            self.log_func = log_func
            self.terminator = ''
        def write(self, text):
            if text.strip():
                self.log_func(text.strip())
        def flush(self):
            pass
        def isatty(self):
            return False
    
    sys.stdout = LoggerWriter(logger.info)
    sys.stderr = LoggerWriter(logger.error)
    
    setup_exception_logging()
    
    logger.info("程序启动")
    
    # ========================================
    # 激活保护模块（反调试+完整性检查）
    # ========================================
    try:
        from pyqt6_editor.protection import ProtectionManager
        
        # 初始化保护（打包时会自动生成密钥和哈希）
        ProtectionManager.initialize()
        logger.debug("保护模块初始化成功")
    except Exception as e:
        # 开发模式或保护模块不可用时跳过
        logger.warning(f"保护模块初始化失败: {e}")
    
    from PyQt6.QtWidgets import QApplication
    from pyqt6_editor.editor import NodeEditor

    # 导入 TACZ 节点库
    import pyqt6_editor.tacz_nodes

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    app.setStyleSheet("""
        QWidget {
            background-color: rgb(30, 30, 30);
            color: rgb(220, 220, 220);
        }
        QMenuBar {
            background-color: rgb(45, 45, 48);
            color: rgb(220, 220, 220);
        }
        QMenuBar::item:selected {
            background-color: rgb(70, 70, 75);
        }
        QMenu {
            background-color: rgb(45, 45, 48);
            color: rgb(220, 220, 220);
            border: 1px solid rgb(60, 60, 65);
        }
        QMenu::item:selected {
            background-color: rgb(70, 70, 75);
        }
        QToolBar {
            background-color: rgb(45, 45, 48);
            border: none;
        }
        QToolButton {
            background-color: rgb(45, 45, 48);
            color: rgb(220, 220, 220);
            padding: 5px;
        }
        QToolButton:hover {
            background-color: rgb(70, 70, 75);
        }
        QStatusBar {
            background-color: rgb(30, 30, 30);
            color: rgb(180, 180, 180);
        }
        QTreeWidget {
            background-color: rgb(35, 35, 38);
            color: rgb(220, 220, 220);
            border: none;
        }
        QTreeWidget::item:selected {
            background-color: rgb(60, 60, 140);
        }
        QTreeWidget::item:hover {
            background-color: rgb(55, 55, 60);
        }
        QTextEdit, QPlainTextEdit {
            background-color: rgb(35, 35, 38);
            color: rgb(220, 220, 220);
            border: 1px solid rgb(60, 60, 65);
        }
        QScrollBar:vertical {
            background: rgb(40, 40, 45);
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background: rgb(80, 80, 85);
            min-height: 20px;
        }
        QScrollBar:horizontal {
            background: rgb(40, 40, 45);
            height: 12px;
        }
        QScrollBar::handle:horizontal {
            background: rgb(80, 80, 85);
            min-width: 20px;
        }
        QSplitter::handle {
            background-color: rgb(60, 60, 65);
        }
        QLabel {
            background-color: transparent;
            color: rgb(220, 220, 220);
        }
        QPushButton {
            background-color: rgb(55, 55, 60);
            color: rgb(220, 220, 220);
            border: 1px solid rgb(70, 70, 75);
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: rgb(70, 70, 75);
        }
        QPushButton:pressed {
            background-color: rgb(45, 45, 50);
        }
        QInputDialog, QFileDialog {
            background-color: rgb(45, 45, 48);
        }
        QMessageBox {
            background-color: rgb(45, 45, 48);
        }
        QTabWidget::pane {
            border: 1px solid rgb(60, 60, 65);
            background-color: rgb(35, 35, 38);
        }
        QTabBar::tab {
            background-color: rgb(40, 40, 45);
            color: rgb(180, 180, 180);
            padding: 5px 15px;
        }
        QTabBar::tab:selected {
            background-color: rgb(35, 35, 38);
            color: rgb(220, 220, 220);
        }
    """)

    # 创建并显示编辑器
    editor = NodeEditor()
    editor.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
