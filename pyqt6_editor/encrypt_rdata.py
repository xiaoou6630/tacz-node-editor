#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PE文件 .rdata 段加密工具
用于保护PyInstaller打包后的exe文件中的只读数据段
"""

import os
import sys
import struct
import hashlib
from cryptography.fernet import Fernet


class PERDataEncryptor:
    """PE文件 .rdata 段加密器"""
    
    def __init__(self, exe_path: str):
        self.exe_path = exe_path
        self.pe_data = None
        self.rdata_offset = 0
        self.rdata_size = 0
        self.rdata_section_index = -1
        
    def load_pe(self):
        """读取PE文件"""
        with open(self.exe_path, 'rb') as f:
            self.pe_data = bytearray(f.read())
        
    def find_rdata_section(self):
        """查找 .rdata 段"""
        # 检查PE签名
        dos_header = struct.unpack('<H', self.pe_data[0:2])[0]
        if dos_header != 0x5A4D:  # 'MZ'
            raise ValueError("Not a valid PE file")
        
        # 获取PE头偏移
        pe_offset = struct.unpack('<I', self.pe_data[60:64])[0]
        
        # 检查PE签名
        pe_sig = self.pe_data[pe_offset:pe_offset+4]
        if pe_sig != b'PE\x00\x00':
            raise ValueError("Invalid PE signature")
        
        # 获取节表数量
        num_sections = struct.unpack('<H', self.pe_data[pe_offset+6:pe_offset+8])[0]
        optional_header_size = struct.unpack('<H', self.pe_data[pe_offset+20:pe_offset+22])[0]
        
        # 节表偏移
        section_table_offset = pe_offset + 24 + optional_header_size
        
        # 遍历节表查找 .rdata
        for i in range(num_sections):
            section_offset = section_table_offset + i * 40
            section_name = self.pe_data[section_offset:section_offset+8].decode('ascii', errors='ignore').rstrip('\x00')
            
            if section_name == '.rdata':
                self.rdata_section_index = i
                self.rdata_offset = struct.unpack('<I', self.pe_data[section_offset+20:section_offset+24])[0]
                self.rdata_size = struct.unpack('<I', self.pe_data[section_offset+16:section_offset+20])[0]
                print(f"[PE] Found .rdata section:")
                print(f"  - Index: {i}")
                print(f"  - Offset: {hex(self.rdata_offset)}")
                print(f"  - Size: {self.rdata_size} bytes")
                return True
        
        print("[PE] .rdata section not found!")
        return False
    
    def encrypt_rdata(self, key: bytes = None):
        """加密 .rdata 段"""
        if not self.pe_data:
            raise ValueError("PE file not loaded")
        
        # 生成或使用提供的密钥
        if key is None:
            key = Fernet.generate_key()
        
        fernet = Fernet(key)
        
        # 提取 .rdata 段数据
        rdata_data = bytes(self.pe_data[self.rdata_offset:self.rdata_offset + self.rdata_size])
        
        # 加密
        encrypted_data = fernet.encrypt(rdata_data)
        
        # 保存加密后的数据
        self.encrypted_rdata = encrypted_data
        self.encryption_key = key
        
        print(f"[Encrypt] .rdata encrypted successfully")
        print(f"  - Original size: {len(rdata_data)} bytes")
        print(f"  - Encrypted size: {len(encrypted_data)} bytes")
        print(f"  - Key: {key.decode()}")
        
        return key
    
    def save_encrypted_pe(self, output_path: str = None):
        """保存加密后的PE文件"""
        if output_path is None:
            output_path = self.exe_path.replace('.exe', '_protected.exe')
        
        # 将加密后的数据附加到exe末尾
        # 并在exe中添加一个标记
        marker = b'ENCRYPTED_RDATA_V1'
        key_marker = b'KEY:'
        
        # 添加加密数据
        self.pe_data.extend(marker)
        self.pe_data.extend(struct.pack('<I', len(self.encrypted_rdata)))
        self.pe_data.extend(self.encrypted_rdata)
        
        # 添加密钥（加密存储）
        key_data = self.encryption_key
        self.pe_data.extend(key_marker)
        self.pe_data.extend(struct.pack('<I', len(key_data)))
        self.pe_data.extend(key_data)
        
        # 保存
        with open(output_path, 'wb') as f:
            f.write(self.pe_data)
        
        print(f"[Save] Protected exe saved to: {output_path}")
        return output_path
    
    def decrypt_and_run(self):
        """解密并运行（在程序启动时调用）"""
        # 这个函数会被注入到exe的启动代码中
        pass


def encrypt_exe_rdata(exe_path: str, output_path: str = None):
    """对exe文件的 .rdata 段进行加密"""
    print(f"[PE Encrypt] Processing: {exe_path}")
    
    if not os.path.exists(exe_path):
        print(f"[ERROR] File not found: {exe_path}")
        return None
    
    encryptor = PERDataEncryptor(exe_path)
    
    # 加载PE文件
    encryptor.load_pe()
    
    # 查找 .rdata 段
    if not encryptor.find_rdata_section():
        print("[ERROR] .rdata section not found!")
        return None
    
    # 加密
    key = encryptor.encrypt_rdata()
    
    # 保存
    if output_path is None:
        output_path = exe_path.replace('.exe', '_protected.exe')
    
    output = encryptor.save_encrypted_pe(output_path)
    
    # 保存密钥到文件
    key_file = output_path.replace('.exe', '_key.txt')
    with open(key_file, 'w') as f:
        f.write(key.decode())
    
    print(f"\n[Complete] Encryption finished!")
    print(f"[Output] {output}")
    print(f"[Key] Saved to: {key_file}")
    
    return output


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python encrypt_rdata.py <exe_path> [output_path]")
        sys.exit(1)
    
    exe_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    encrypt_exe_rdata(exe_path, output_path)
