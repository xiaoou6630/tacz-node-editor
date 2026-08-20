import win32file
import win32con
import win32api
import win32gui
import struct
import os

def list_cdrom_drives():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\x00')[:-1]
    for drive in drives:
        if win32file.GetDriveType(drive) == win32con.DRIVE_CDROM:
            print(f"CDROM: {drive}")
            try:
                h = win32file.CreateFile(
                    drive,
                    win32con.GENERIC_READ,
                    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                    None,
                    win32con.OPEN_EXISTING,
                    0,
                    None
                )
                vol_info = win32file.GetVolumeInformation(drive)
                print(f"  Volume: {vol_info[0]}, Serial: {vol_info[1]:08X}")
                print(f"  FileSystem: {vol_info[4]}, MaxLen: {vol_info[2]}")
                win32file.CloseHandle(h)
            except Exception as e:
                print(f"  Error: {e}")
    print()

def list_physical_drives():
    for i in range(10):
        path = f"\\\\.\\PhysicalDrive{i}"
        try:
            h = win32file.CreateFile(
                path,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )
            print(f"PhysicalDrive{i}: {path}")
            geometry = win32file.DeviceIoControl(
                h, 0x70000, None, 24
            )
            import struct
            cyl, media, hds, sectors = struct.unpack_from('<IHBB', geometry, 0)
            size = cyl * hds * sectors * 512
            print(f"  Size: {size} bytes ({size/1024/1024/1024:.2f} GB)")
            win32file.CloseHandle(h)
        except Exception as e:
            break

def list_cdrom_devices():
    for i in range(10):
        path = f"\\\\.\\CdRom{i}"
        try:
            h = win32file.CreateFile(
                path,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )
            print(f"CdRom{i}: {path} - OPENED")
            win32file.CloseHandle(h)
        except Exception as e:
            print(f"CdRom{i}: {path} - {e}")

if __name__ == "__main__":
    print("=== Logical CDROM Drives ===")
    list_cdrom_drives()
    print("\n=== Physical Drives ===")
    list_physical_drives()
    print("\n=== Raw CdRom Devices ===")
    list_cdrom_devices()
