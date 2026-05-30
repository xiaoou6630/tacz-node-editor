"""
综合保护模块
包含：
1. 字符串加密 - 对敏感字符串加密，运行时解密
2. 反调试保护 - 防止调试器分析
3. 代码完整性检查 - 检测exe是否被篡改
"""

import os
import sys
import time
import ctypes
import hashlib
from cryptography.fernet import Fernet


class StringProtector:
    """字符串加密/解密器"""
    
    _key = None
    
    @classmethod
    def set_key(cls, key: bytes):
        cls._key = key
    
    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """加密字符串"""
        if cls._key is None:
            raise ValueError("Key not set")
        fernet = Fernet(cls._key)
        encrypted = fernet.encrypt(plaintext.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    @classmethod
    def decrypt(cls, encrypted: str) -> str:
        """解密字符串"""
        if cls._key is None:
            raise ValueError("Key not set")
        fernet = Fernet(cls._key)
        return fernet.decrypt(encrypted.encode('utf-8')).decode('utf-8')


class AntiDebug:
    """反调试保护"""
    
    @staticmethod
    def is_debugger_present():
        """检测是否存在调试器"""
        try:
            return ctypes.windll.kernel32.IsDebuggerPresent() != 0
        except Exception:
            return False
    
    @staticmethod
    def check_remote_debugger():
        """检测远程调试器"""
        try:
            NtGlobalFlag = ctypes.c_ulong()
            result = ctypes.windll.ntdll.NtQueryInformationProcess(
                ctypes.c_void_p(-1),
                0,
                ctypes.byref(NtGlobalFlag),
                ctypes.sizeof(NtGlobalFlag),
                None
            )
            return result == 0 and (NtGlobalFlag.value & 0x70) != 0
        except Exception:
            return False
    
    @staticmethod
    def check_virtual_machine():
        """检测是否在虚拟机中运行"""
        try:
            # 检查常见的虚拟机特征
            import subprocess
            result = subprocess.run(
                ['wmic', 'computersystem', 'get', 'model'],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.lower()
            vm_indicators = ['virtualbox', 'vmware', 'virtual machine', 'qemu']
            return any(vm in output for vm in vm_indicators)
        except Exception:
            return False
    
    @staticmethod
    def protect():
        """执行反调试检查"""
        if AntiDebug.is_debugger_present():
            print("[Protected] Debugger detected! Exiting...")
            sys.exit(1)
        
        # 延迟检查（防止断点调试）
        start_time = time.time()
        time.sleep(0.01)
        elapsed = time.time() - start_time
        
        if elapsed > 0.1:  # 如果延迟超过预期，可能被调试
            print("[Protected] Timing anomaly detected! Exiting...")
            sys.exit(1)


class IntegrityChecker:
    """代码完整性检查"""
    
    # 打包时会自动替换为exe的SHA256哈希
    # 空字符串表示禁用完整性检查（开发模式）
    EXPECTED_HASH = ""
    
    # 是否启用完整性检查（打包脚本会自动设置为True）
    ENABLE_INTEGRITY_CHECK = False
    
    @staticmethod
    def get_exe_hash():
        """获取exe文件的SHA256哈希值"""
        if not getattr(sys, 'frozen', False):
            return None
        
        exe_path = sys.executable
        sha256 = hashlib.sha256()
        
        with open(exe_path, 'rb') as f:
            # 分块读取，避免大文件占用过多内存
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    @staticmethod
    def verify(expected_hash: str = None):
        """验证exe完整性"""
        if not getattr(sys, 'frozen', False):
            return True  # 开发模式跳过检查
        
        # 如果未启用完整性检查，直接返回
        if not IntegrityChecker.ENABLE_INTEGRITY_CHECK:
            return True
        
        # 使用内置的预期哈希值（打包时自动生成）
        if expected_hash is None:
            expected_hash = IntegrityChecker.EXPECTED_HASH
        
        # 如果没有预期哈希值，跳过验证
        if not expected_hash:
            return True
        
        current_hash = IntegrityChecker.get_exe_hash()
        
        if current_hash != expected_hash:
            print("[Protected] Integrity check failed! File has been modified.")
            print(f"Expected: {expected_hash}")
            print(f"Current:  {current_hash}")
            sys.exit(1)
        
        return True


class ProtectionManager:
    """综合保护管理器"""
    
    _initialized = False
    
    @classmethod
    def initialize(cls, encryption_key: bytes = None, expected_hash: str = None):
        """初始化所有保护"""
        if cls._initialized:
            return
        
        # 1. 字符串加密
        if encryption_key:
            StringProtector.set_key(encryption_key)
        
        # 2. 反调试检查
        AntiDebug.protect()
        
        # 3. 完整性检查
        IntegrityChecker.verify(expected_hash)
        
        cls._initialized = True
        print("[Protected] All protections activated")
    
    @classmethod
    def encrypt_string(cls, text: str) -> str:
        """加密字符串"""
        return StringProtector.encrypt(text)
    
    @classmethod
    def decrypt_string(cls, encrypted: str) -> str:
        """解密字符串"""
        return StringProtector.decrypt(encrypted)


# ========================================
# 使用示例
# ========================================
if __name__ == '__main__':
    # 生成密钥
    key = Fernet.generate_key()
    print(f"Generated key: {key.decode()}")
    
    # 初始化保护
    ProtectionManager.initialize(key)
    
    # 测试字符串加密
    original = "secret_config_value"
    encrypted = ProtectionManager.encrypt_string(original)
    decrypted = ProtectionManager.decrypt_string(encrypted)
    
    print(f"Original:  {original}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}")
    
    # 测试反调试
    print(f"\nDebugger present: {AntiDebug.is_debugger_present()}")
    print(f"VM detected: {AntiDebug.check_virtual_machine()}")
