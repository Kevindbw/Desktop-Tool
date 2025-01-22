import os
import sys
import subprocess

def startup():
    try:
        # 切换到程序所在目录
        os.chdir(r"D:\67678\Develop\Desktop-Tool\dist")
        # 启动主程序
        subprocess.Popen(r"D:\67678\Develop\Desktop-Tool\dist\Course.exe")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    startup()
