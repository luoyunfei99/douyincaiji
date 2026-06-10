import time
from datetime import datetime
import requests
import json
import cfun
import os



# 业务标识：a8pruw88
# Authkey：A956887A
# Authpwd：CA0BCFDCEC47

def getip2():
    try:
        url = "https://exclusive.proxy.qg.net/replace?key=A956887A&num=1&area=&isp=0&format=json&seq=\r\n&distinct=false&keep_alive=1440"
        # 发送 POST 请求
        response = requests.get(url)
        # print(url)
        # print(params)
        print(response)
        # 检查响应状态码
        if response.status_code == 200:
            rdata = response.json()
            if rdata['code'] == 'SUCCESS':
                data = rdata.get('data')
                if data is not None:
                    # 将 data 转换为 JSON 字符串
                    json_str = json.dumps(data['ips'])
                    cfun.write_json_to_file(json_str,'ip.json')
                    return response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}，响应内容: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"请求发生异常: {e}")
        return None

def getip3():
    try:
        cfg_proxy = cfun.read_json_from_file('proxy.json')
        if cfg_proxy:
            key = cfg_proxy['key']
            num = cfg_proxy['num']
            area = cfg_proxy['area']
            #url = "https://share.proxy.qg.net/pool?key=7E4E8259&num=1&area=430100&isp=0&format=json&seq=\r\n&distinct=false"
            # https://share.proxy.qg.net/pool?key=A956887A&num=2&area=&isp=1&format=json&distinct=true
            url = f'https://share.proxy.qg.net/pool?key={key}&num={num}&area={area}&isp=1&format=json&distinct=true'
            # 发送 POST 请求
            response = requests.get(url)
            # print(url)
            # print(params)
            print(response)
            # 检查响应状态码
            if response.status_code == 200:
                rdata = response.json()
                if rdata['code'] == 'SUCCESS':
                    data = rdata.get('data')
                    if data is not None:
                        # 将 data 转换为 JSON 字符串
                        json_str = json.dumps(data)
                        cfun.write_json_to_file(json_str,'ip.json')
                        return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}，响应内容: {response.text}")
                return None
        else:
            print(f"代理信息设置不存在！")
            return None
    except requests.RequestException as e:
        print(f"请求发生异常: {e}")
        return None      

def beforeips():
    try:
        cfg_proxy = cfun.read_json_from_file('proxy.json')
        if cfg_proxy:
            key = cfg_proxy['key']
            url = f'https://longterm.proxy.qg.net/query?key={key}'
            response = requests.get(url)
            print(response)
            # 检查响应状态码
            rdata = response.json()
            print(rdata)
            if response.status_code == 200:
                if rdata['code'] == 'SUCCESS':
                    data = rdata.get('data')
                    if data is not None:
                        # 将 data 转换为 JSON 字符串
                        json_str = json.dumps(data)
                        cfun.write_json_to_file(json_str,'ip.json')
                        return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}，响应内容: {response.text}")
                return None
        else:
            print(f"代理信息设置不存在！")
            return None
    except requests.RequestException as e:
        print(f"请求发生异常: {e}")
        return None       
def getip():
    try:
        cfg_proxy = cfun.read_json_from_file('proxy.json')
        if cfg_proxy:
            key = cfg_proxy['key']
            num = cfg_proxy['num']
            area = cfg_proxy['area']
            url = f'https://longterm.proxy.qg.net/get?key={key}&num={num}&area={area}&isp=0&format=json&distinct=false'
            # 发送 POST 请求
            response = requests.get(url)
            # print(url)
            # print(params)
            print(response)
            # 检查响应状态码
            rdata = response.json()
            print(rdata)
            if response.status_code == 200:
                if rdata['code'] == 'SUCCESS':
                    data = rdata.get('data')
                    if data is not None:
                        # 将 data 转换为 JSON 字符串
                        json_str = json.dumps(data)
                        cfun.write_json_to_file(json_str,'ip.json')
                        return response.json()
            elif response.status_code == 400:
                if rdata['code'] == 'NO_AVAILABLE_CHANNEL':
                    return beforeips()

            else:
                print(f"请求失败，状态码: {response.status_code}，响应内容: {response.text}")
                return None
        else:
            print(f"代理信息设置不存在！")
            return None
    except requests.RequestException as e:
        print(f"请求发生异常: {e}")
        return None       
# 检查文件最后修改时间，如果超过 10 分钟则重新写入
def check_and_write(file_path):
    if os.path.exists(file_path):
        # 获取文件的最后修改时间
        last_modified_time = os.path.getmtime(file_path)

        modified_datetime = datetime.fromtimestamp(last_modified_time)
        today = datetime.today().date()

        current_time = time.time()
        # 计算时间差（单位：秒）
        time_diff = current_time - last_modified_time
        # 1天对应的秒数
        interval_minutes = 60 * 60 * 4
        # 检查文件内容是否为空
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            is_empty = len(content.strip()) == 0

        if time_diff > interval_minutes or is_empty or modified_datetime.date() != today:
            print("文件最后修改时间超过 240 分钟，重新从 API 获取数据并写入文件。")
            json_str = getip()
            print(json_str)
        # else:
            # print("文件最后修改时间未超过 10 分钟，不进行重新写入。")
    else:
        print("文件不存在，从 API 获取数据并写入文件。")
        json_str = getip()
        print(json_str)

if __name__ == '__main__':
    while True:
        file_path = 'ip.json'
        check_and_write(file_path) 
        time.sleep(3)
        