import time
from datetime import datetime
import requests
import json
import cfun
import os
    
def setwithip(ip):
    try:
        cfg_proxy = cfun.read_json_from_file('proxy.json')
        if cfg_proxy:
            key = cfg_proxy['key']
            url = f"https://proxy.qg.net/whitelist/add?Key={key}&IP={ip}"
            # 发送 POST 请求
            response = requests.get(url)
            # print(url)
            # print(params)
            print(response)
            # 检查响应状态码
            if response.status_code == 200:
                rdata = response.json()
                if rdata:
                    print(rdata)
            else:
                print(f"setwithip请求失败，状态码: {response.status_code}，响应内容: {response.text}")
                return None
        else:
                print(f"代理信息设置不存在！")
                return None
    except requests.RequestException as e:
        print(f"setwithip请求发生异常: {e}")
        return None

# 检查文件最后修改时间，如果超过 10 分钟则重新写入
def check_and_write(file_path):
    old_ip = ''
    ip = ''
    if os.path.exists(file_path):

        with open(file_path, 'r', encoding='utf-8') as file:
            old_ip = file.read()
            # print(old_ip)

        # 获取文件的最后修改时间
        last_modified_time = os.path.getmtime(file_path)

        modified_datetime = datetime.fromtimestamp(last_modified_time)
        today = datetime.today().date()

        current_time = time.time()
        # 计算时间差（单位：秒）
        time_diff = current_time - last_modified_time
        # 1天对应的秒数
        interval_minutes = 30 * 60
        # 检查文件内容是否为空
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            is_empty = len(content.strip()) == 0
        if time_diff > interval_minutes or is_empty or modified_datetime.date() != today:
            print("文件最后修改时间超过 30 分钟，重新从 API 获取数据并写入文件。")
            ip = cfun.getip()
            print(ip)
        # else:
            # print("文件最后修改时间未超过 10 分钟，不进行重新写入。")
    else:
        print("文件不存在，从 API 获取数据并写入文件。")
        ip = cfun.getip()
        print(ip)
    if ip:    
        print("重新设置ip白名单。")
        cfun.write_json_to_file(ip,file_path)
        setwithip(ip)


if __name__ == '__main__':
    while True:
        file_path = 'ipwhite.json'
        check_and_write(file_path) 
        time.sleep(3)
        