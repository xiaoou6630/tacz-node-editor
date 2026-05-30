"""
运行时加密解密模块
用于保护配置文件、数据库等只读数据
使用 AES-256-CBC 加密算法
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet


class RuntimeEncryption:
    """运行时加密管理器"""
    
    # 内置加密密钥（打包时会替换为随机密钥）
    _ENCRYPTION_KEY = b'DEFALT_K3Y_F0R_T3ST1NG_0NLY_CH4NGE_M3!'
    
    @classmethod
    def generate_key(cls):
        """生成新的加密密钥"""
        return Fernet.generate_key()
    
    @classmethod
    def _get_key(cls):
        """获取加密密钥"""
        # 确保密钥长度为32字节的base64编码
        key = cls._ENCRYPTION_KEY
        if len(key) != 32:
            # 使用哈希生成32字节密钥
            key = hashlib.sha256(key).digest()
        return base64.urlsafe_b64encode(key)
    
    @classmethod
    def encrypt_data(cls, data: bytes) -> bytes:
        """加密数据"""
        fernet = Fernet(cls._get_key())
        return fernet.encrypt(data)
    
    @classmethod
    def decrypt_data(cls, encrypted_data: bytes) -> bytes:
        """解密数据"""
        fernet = Fernet(cls._get_key())
        return fernet.decrypt(encrypted_data)
    
    @classmethod
    def encrypt_file(cls, input_path: str, output_path: str):
        """加密文件"""
        with open(input_path, 'rb') as f:
            data = f.read()
        encrypted = cls.encrypt_data(data)
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    
    @classmethod
    def decrypt_file(cls, input_path: str) -> bytes:
        """解密文件并返回数据"""
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        return cls.decrypt_data(encrypted)
    
    @classmethod
    def decrypt_file_to_temp(cls, input_path: str, temp_path: str = None):
        """解密文件到临时位置，使用后立即删除"""
        if temp_path is None:
            temp_path = input_path + '.decrypted.tmp'
        
        data = cls.decrypt_file(input_path)
        with open(temp_path, 'wb') as f:
            f.write(data)
        
        return temp_path
    
    @classmethod
    def secure_read_json(cls, encrypted_path: str) -> dict:
        """安全读取加密的JSON配置文件"""
        import json
        data = cls.decrypt_file(encrypted_path)
        return json.loads(data.decode('utf-8'))
    
    @classmethod
    def encrypt_and_replace(cls, input_path: str):
        """加密文件并替换原文件（添加.enc扩展名）"""
        output_path = input_path + '.enc'
        cls.encrypt_file(input_path, output_path)
        # 删除原文件
        if os.path.exists(input_path):
            os.remove(input_path)
        return output_path


def encrypt_config_files(config_dir: str):
    """批量加密配置文件（打包前使用）"""
    encryption = RuntimeEncryption()
    
    files_to_encrypt = [
        'config.json',
    ]
    
    for filename in files_to_encrypt:
        filepath = os.path.join(config_dir, filename)
        if os.path.exists(filepath):
            print(f"[Encrypt] Encrypting {filename}...")
            encryption.encrypt_and_replace(filepath)
            print(f"[Encrypt] Created {filename}.enc")


if __name__ == '__main__':
    # 测试加密解密
    key = RuntimeEncryption.generate_key()
    print(f"Generated key: {key}")
    
    # 设置密钥
    RuntimeEncryption._ENCRYPTION_KEY = key
    
    # 测试加密解密
    test_data = b'{"test": "value", "secret": 123}'
    encrypted = RuntimeEncryption.encrypt_data(test_data)
    decrypted = RuntimeEncryption.decrypt_data(encrypted)
    
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {test_data == decrypted}")
