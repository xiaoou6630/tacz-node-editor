from PyInstaller.utils.hooks import collect_submodules

# 排除所有不需要的 Qt 子模块
excludedimports = [
    # Qt 多媒体相关
    'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets',
    # Qt 网络
    'PyQt6.QtNetwork',
    # Qt 3D/OpenGL
    'PyQt6.QtOpenGL',
    'PyQt6.QtOpenGLWidgets',
    # Qt 打印
    'PyQt6.QtPrintSupport',
    # Qt QML/Quick
    'PyQt6.QtQml',
    'PyQt6.QtQuick',
    'PyQt6.QtQuick3D',
    'PyQt6.QtQuickWidgets',
    # Qt 数据库
    'PyQt6.QtSql',
    # Qt SVG
    'PyQt6.QtSvg',
    'PyQt6.QtSvgWidgets',
    # Qt 测试
    'PyQt6.QtTest',
    # Qt Web
    'PyQt6.QtWebChannel',
    'PyQt6.QtWebSockets',
    # Qt XML
    'PyQt6.QtXml',
    # Qt PDF
    'PyQt6.QtPdf',
    'PyQt6.QtPdfWidgets',
    # Qt 定位
    'PyQt6.QtPositioning',
    # Qt 传感器
    'PyQt6.QtSensors',
    'PyQt6.QtSerialPort',
    # Qt 远程对象
    'PyQt6.QtRemoteObjects',
    # Qt 语音
    'PyQt6.QtTextToSpeech',
    # Qt 状态机
    'PyQt6.QtStateMachine',
    'PyQt6.QtSpatialAudio',
    # Qt NFC/蓝牙
    'PyQt6.QtNfc',
    'PyQt6.QtBluetooth',
    # Qt 设计器/帮助
    'PyQt6.QtDesigner',
    'PyQt6.QtHelp',
    'PyQt6.QtDBus',
    # Qt 轴控件
    'PyQt6.QAxContainer',
    # 其他不需要的
    'PyQt6.lupdate',
]
