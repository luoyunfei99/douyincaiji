#!/usr/bin/python
# coding:utf-8
import subprocess
from my_sql import MySQLHandler
import sys
import time
from pathlib import Path
# 获取当前文件所在目录的父目录，并添加到系统路径
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.mysql_config import mysql_config
import os
import datetime

# 定义要运行的命令及其参数
# commands = [
#     ["python", "main.py", "arg1"],
#     ["python", "main.py", "arg2"]
# ]

# 循环遍历每个命令并在新的 CMD 窗口中运行
# for command in commands:
#     try:
#         # 使用 start cmd /k 来打开新的 CMD 窗口并保持窗口打开
#         full_command = ["start", "cmd", "/k"] + command
#         # 使用 shell=True 来确保命令在新的 CMD 窗口中正确执行
#         subprocess.Popen(full_command, shell=True)
#     except Exception as e:
#         print(f"运行命令时出错: {e}")

def reset_runstatus(db):
    db.execute_update('update craw_lives a set a.is_run=0 where a.is_run=1 and a.islisten=1 and a.status=1 and last_runtime<date_add(now(),INTERVAL -20 minute) and not exists(select 1 from craw_douyin_live_message where liveid=a.liveid and updatetime>date_add(now(),INTERVAL -10 minute) )')

if __name__ == '__main__':
    i=0
    while True:
        try:
            db = MySQLHandler(**mysql_config)
            db.connect()
            reset_runstatus(db)
            turlinfo = db.execute_query(
                f'select * from craw_lives where  status=1 and is_run=0 and islisten=1 limit 1')
            if not turlinfo:
                if i==0:
                    print('没有要操作的数据')
                time.sleep(60)
            else:
                liveid = turlinfo[0]['liveid']
                tid = turlinfo[0]['id']
                print(liveid)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                print(f"当前文件绝对路径: {script_dir}")
                command = ["python", f"{script_dir}\main_listen.py", liveid]
                # 使用 start cmd /k 来打开新的 CMD 窗口并保持窗口打开
                full_command = ["start", "cmd", "/k"] + command
                # 使用 shell=True 来确保命令在新的 CMD 窗口中正确执行
                subprocess.Popen(full_command, shell=True)
                now = datetime.datetime.now()
                nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                db.update('craw_lives', {'is_run': 1,'last_runtime':nowtime}, f"id={tid}")
            db.disconnect()
            i += 1

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            # db.disconnect()
            time.sleep(60)
            pass
    