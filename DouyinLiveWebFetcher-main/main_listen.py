#!/usr/bin/python
# coding:utf-8

# @FileName:    main.py
# @Time:        2024/1/2 22:27
# @Author:      bubu
# @Project:     douyinLiveWebFetcher

from liveMan import DouyinLiveWebFetcher
import traceback
import sys
import time
import os
from my_sql import MySQLHandler
import datetime
from config.mysql_config import mysql_config
def read_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 未找到！")
    except Exception as e:
        print(f"读取文件时出错: {e}")
    return 

def write_to_file(file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"内容已成功写入 {file_path}")
        except Exception as e:
            print(f"写入文件时出错: {e}")

if __name__ == '__main__':
    i = 0
    max_try = 20
    
    if len(sys.argv) > 1:
        print("传递的参数如下:")
        for i, arg in enumerate(sys.argv[1:], start=1):
            print(f"参数 {i}: {arg}") 
        live_id = sys.argv[1]
        print(f'直播间：https://live.douyin.com/{live_id}')   
    else:
        print("没有传递额外的参数。")
        exit()
    isrun = False
    file_path = f'live/{live_id}.txt'
    try:
        while True:
            db = MySQLHandler(**mysql_config)
            db.connect()
            # print(f"请输入直播ID:")
            # live_id = input()
            # if live_id == 'q':
            # 
            if isrun: 
                file_content = read_from_file(file_path)
                if file_content is not None:
                    print(file_content)     
                    if file_content.strip() == "close":
                        isrun = False
                        print("直播已结束")
                    
            try:
                if not isrun and i<= max_try: 
                    if i>0:
                        print(f'重试第{i}次') 
                    i = i+1
                    isrun = True
                    write_to_file(file_path,'run')
                    DouyinLiveWebFetcher(live_id).start()
                    
                else:
                    if i>max_try: 
                        now = datetime.datetime.now()
                        nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                        db.update('craw_lives', {'is_run': 0,'status':0,'last_runtime':nowtime}, f'liveid={live_id}')
                        # 关闭当前 CMD 窗口
                        os._exit(0)
                        print("是否重启直播间:")
                        is_restart = input()
                        if is_restart == 'y':
                            i = 0
                            isrun = True
                            write_to_file(file_path,'run')
                            DouyinLiveWebFetcher(live_id).start()
                            
            except:
                pass
            db.disconnect()
            time.sleep(10)
    except KeyboardInterrupt:
        isrun = False
        print("\n用户中断程序...")
        db = MySQLHandler(**mysql_config)
        db.connect()
        db.execute_update(f'UPDATE craw_lives SET is_run=0 WHERE is_run=1 and liveid={live_id}')
        db.disconnect()
        sys.exit(0)
    except Exception as e:
        isrun = False
        print(f"[主程序异常] {str(e)}")
        db = MySQLHandler(**mysql_config)
        db.connect()
        db.execute_update(f'UPDATE craw_lives SET is_run=0 WHERE is_run=1 and liveid={live_id}')
        db.disconnect()
        sys.exit(0)
    