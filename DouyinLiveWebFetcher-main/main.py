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
    
    while True:
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
                    print("是否重启直播间:")
                    is_restart = input()
                    if is_restart == 'y':
                        i = 0
                        isrun = True
                        write_to_file(file_path,'run')
                        DouyinLiveWebFetcher(live_id).start()
                        
            time.sleep(10)
        except Exception as e:
            isrun = False
            error_info = traceback.format_exc()
            print(f"发生异常: {type(e).__name__}, 详细错误信息:\n{error_info}")
    