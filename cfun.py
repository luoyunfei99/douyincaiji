from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
import re
import random
import time
from datetime import datetime, timedelta, time as dt_time
import hashlib
import requests
import json
from myclass.timeout import TimeoutThread
import base64
from fastapi import  Response
import csv
from io import StringIO
from typing import List, Dict, Any, Optional
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import json
from urllib.parse import urlparse, parse_qs
def extract_and_join_phone_numbers(input_string):
    #特殊替换
    translated_text  = ''.join(re.sub(r'[\s.-]', '', part) for part in input_string)

    # 定义汉字数字映射字典
    chinese_numbers = {'零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', 'o': '0', '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5',
                       '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9', '壹': '1', '贰': '2', '叁': '3', '肆': '4', '伍': '5', '陆': '6', '柒': '7', '捌': '8', '玖': '9'}
    # 将文本中的汉字数字替换为阿拉伯数字
    translated_text = ''.join(chinese_numbers.get(char, char) for char in translated_text)

    # 定义手机号的正则表达式
    phone_pattern = re.compile(r'1[3-9]\d{9}')
    # 查找所有匹配的手机号
    phone_numbers = re.findall(phone_pattern, translated_text)
    # 用逗号拼接手机号
    result = ",".join(phone_numbers)
    return result


def validate_phone_number(string):
    # 手机号的正则表达式
    pattern = re.compile(r'1[3-9]\d{9}')
    # 在字符串中查找是否有匹配的手机号
    match = re.search(pattern, string)
    if match:
        return True
    else:
        return False

def getRandUserAgent():
    # 定义操作系统和版本
    os_windows = [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 6.1; Win64; x64",
        "Windows NT 6.3; Win64; x64"
    ]
    os_mac = [
        "Macintosh; Intel Mac OS X 14_1",
        "Macintosh; Intel Mac OS X 13_4",
        "Macintosh; Intel Mac OS X 12_6"
    ]

    # 定义浏览器和版本
    chrome_versions = [
        "Chrome/119.0.0.0",
        "Chrome/118.0.0.0",
        "Chrome/117.0.0.0"
    ]
    firefox_versions = [
        "Firefox/119.0",
        "Firefox/118.0",
        "Firefox/117.0"
    ]
    safari_versions = [
        "Version/17.1 Safari/605.1.15",
        "Version/16.6 Safari/605.1.15",
        "Version/15.6 Safari/605.1.15"
    ]
    edge_versions = [
        "Edg/119.0.0.0",
        "Edg/118.0.0.0",
        "Edg/117.0.0.0"
    ]

    # 动态生成 pc_user_agents 数组
    pc_user_agents = []

    # 生成 Chrome 的 User-Agent
    for os in os_windows + os_mac:
        for version in chrome_versions:
            pc_user_agents.append(f'Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {version} Safari/537.36')

    # 生成 Firefox 的 User-Agent
    for os in os_windows + os_mac:
        for version in firefox_versions:
            pc_user_agents.append(f'Mozilla/5.0 ({os}; rv:109.0) Gecko/20100101 {version}')

    # 生成 Safari 的 User-Agent
    for os in os_mac:
        for version in safari_versions:
            pc_user_agents.append(f'Mozilla/5.0 ({os}) AppleWebKit/605.1.15 (KHTML, like Gecko) {version}')

    # 生成 Edge 的 User-Agent
    for os in os_windows:
        for version in edge_versions:
            pc_user_agents.append(f'Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 {version}')
    # pc_user_agents = [
    #     # Chrome
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    #     'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    #     # Firefox
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    #     'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/119.0',
    #     # Safari
    #     'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    #     # Edge
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
    # ]
    return random.choice(pc_user_agents)

# 将 JSON 字符串写入文件
def write_json_to_file(json_string, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(json_string)
        print(f"JSON 字符串已成功写入文件: {file_path}")
    except Exception as e:
        print(f"写入文件时出现错误: {e}")

# 从文件中读取内容并解析为 JSON 格式
def read_json_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # 将读取的内容解析为 JSON 格式
            json_data = json.loads(content)
        return json_data
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except json.JSONDecodeError:
        print(f"无法解析文件内容为 JSON 格式: {file_path}")
    except Exception as e:
        print(f"读取文件时出现错误: {e}")


def getproxys():
    jsonfile = 'ip.json'
    filtered_ips = None
    old_data = read_json_from_file(jsonfile)
    # 获取当前时间
    if old_data:
        current_time = datetime.now()
        # 解析JSON数据并筛选出deadline大于当前时间的数据
        filtered_ips = [ip['server'] for ip in old_data if datetime.strptime(ip['deadline'], '%Y-%m-%d %H:%M:%S') > current_time]
        return filtered_ips;


def randPage(local_port=9111, user_data_path=r'D:\data1', useproxy=True,i=None):
    random_user_agent = getRandUserAgent()
    # useproxy = False
    if useproxy:
        co = ChromiumOptions().set_argument('--no-sandbox').set_user_agent(
        random_user_agent).set_paths(local_port=local_port, user_data_path=user_data_path)
        proxys = getproxys()
        if proxys:
            if not isinstance(i, (int)) or i >= len(proxys):
                i=0
            proxy = proxys[i]  
            print(f'代理{i},{proxy}')
            if proxy:
                co.set_proxy(proxy=proxy)
        else:
            print('ip过期')
            return False
    else:
        co = ChromiumOptions().set_argument('--no-sandbox').set_user_agent(random_user_agent)
        # proxy='192.168.1.200:1092'
        # print(proxy)
        # co.set_proxy(proxy=proxy)
    # co.no_imgs(True)
    co.mute(True)    
    page = ChromiumPage(co)
    return page

def getip():
    try:
        url = "https://httpbin.org/ip"
        # 发送 POST 请求
        response = requests.get(url)
        # print(url)
        # print(params)
        print(response)
        # 检查响应状态码
        if response.status_code == 200:
            rdata = response.json()
            if rdata:
                data = rdata.get('origin')
                if data is not None:
                    return data
        else:
            print(f"getip请求失败，状态码: {response.status_code}，响应内容: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"getip请求发生异常: {e}")
        return None   
def getGoolePage(local_port=9111, user_data_path=None, useproxy=None, browser_path=None,headless = False):
    from config.common_config import cfg_google
    from proxy_manager import ProxyManager
    random_user_agent = getRandUserAgent()
    cfg_useproxy = cfg_google['useproxy']
    if local_port is None:
        local_port = cfg_google['port']
    if user_data_path is None:
        user_data_path = cfg_google['data_path']
    if useproxy is None:
        useproxy = cfg_google['useproxy']
    if not cfg_useproxy:
        useproxy = False
    if browser_path is None:
        browser_path = cfg_google['browser_path']
    print(f"端口号: {local_port}")
    print(f"数据路径: {user_data_path}")
    print(f"使用代理: {useproxy}")
    pre_proxy_file = f'tmp/preproxy_{local_port}.json'
    now_proxy_file = 'nowproxy.json'
    extension_autoplaystop_path = cfg_google['extension_autoplaystop_path']
    if useproxy:
        user_data_path += '_proxy'
        co = ChromiumOptions().headless(headless).set_argument('--no-sandbox').set_user_agent(
            random_user_agent).set_paths(browser_path=browser_path, local_port=local_port, user_data_path=user_data_path)
        # 获取当前设置代理
        proxy_info = read_json_from_file(now_proxy_file)
        pre_proxy_info = read_json_from_file(pre_proxy_file)

        proxytype = cfg_google['proxytype']
        # 获取代理配置信息
        cfg_proxy = read_json_from_file('proxy.json')
        if proxy_info:
            proxy = proxy_info['server']
            username = cfg_proxy['key']
            password = cfg_proxy['pwd']
            extension_proxy_path = cfg_google['extension_proxy_path']
            if proxy:
                print(f'代理:{proxy}')
                co.set_proxy(proxy=proxy)
                co.add_extension(extension_proxy_path)
                if extension_autoplaystop_path:
                    co.add_extension(extension_autoplaystop_path)
                co.mute(True)
                if headless:
                    co.headless(True)
                page = ChromiumPage(co)
                print(f'当前代理模式为：{proxytype}')
                if proxytype == '插件':
                    # 代理ip变更
                    if not pre_proxy_info or pre_proxy_info['server'] != proxy:
                        # 创建代理管理器实例
                        proxy_manager = ProxyManager(
                            extension_proxy_path, page)
                        proxy_server_info = proxy.split(':')
                        proxy_manager.set_proxy_profile_proxy(
                            proxy_type="HTTP",
                            proxy_host=proxy_server_info[0],
                            proxy_port=proxy_server_info[1],
                            username=username,
                            password=password
                        )

                        # 切换到认证代理
                        proxy_manager.switch_to_profile("proxy")
                        page = proxy_manager.page

                        local_ip = getip()
                        print(f'当前本地ip:{local_ip}')
                        # exit()
                        # 验证代理是否生效
                        page.get('https://httpbin.org/ip')
                        tempinfo = page.json
                        if tempinfo:
                            tmpstr = json.dumps(tempinfo)
                            print(f'查询代理ip结果：{tmpstr}')
                            proxy_ip = tempinfo['origin']
                            print(f'代理后本地ip:{proxy_ip}')
                            if local_ip == proxy_ip:
                                print('error：插件代理ip设置未生效，请手动修改走默认代理模式')
                                return False
                                # co.set_proxy(proxy=proxy)
                            else:
                                if not pre_proxy_info or pre_proxy_info['server'] != proxy:
                                    json_str = json.dumps(proxy_info)
                                    write_json_to_file(
                                        json_str, pre_proxy_file)
                        else:
                            print('切换代理后，当前ip获取错误')
                    else:
                        print('原代理ip和当前代理ip一致，无需调整')
                else:
                    co.set_proxy(proxy=proxy)
                    page = ChromiumPage(co)
            else:
                print('代理ip设置过期，请重新设置')
                return False
        else:
            print('代理ip设置过期，请重新设置')
            return False
    else:
        # headless = False
        co = ChromiumOptions()
        co.headless(headless)
        if headless:
            # 2. 可选：添加辅助参数（服务器环境/性能优化）
            co.set_argument('--disable-gpu')  # 禁用GPU（服务器无显卡时避免报错）
            co.set_argument('--blink-settings=imagesEnabled=false')  # 禁用图片，加快速度
            # co.set_argument('--single-process')  # 单进程模式（所有功能合并为一个进程，便于关闭）
            # co.set_argument('--disable-features=Translate')  # 禁用翻译功能（减少额外进程）
            # co.set_argument('--disable-popup-blocking')  # 禁用弹窗拦截（避免弹窗进程残留）
            # co.set_argument('--incognito')  # 隐身模式（退出后自动清理资源，无缓存残留）

        co.set_argument('--no-sandbox')
        co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
        # co.set_user_agent(random_user_agent)
        co.set_paths(browser_path=browser_path, local_port=local_port, user_data_path=user_data_path)

        co.set_argument("--disable-blink-features=AutomationControlled")
        co.set_argument("--exclude-switches=enable-automation")
        co.set_argument("--disable-extensions")
        
        # 模拟真实环境（不变）
        co.set_argument("--window-size=1920,1080")

        
        # 额外优化配置（不变）
        co.set_argument("--disable-infobars")
        co.set_argument("--disable-dev-shm-usage")    
        # if extension_autoplaystop_path:
        #     co.add_extension(extension_autoplaystop_path)
        # co.no_imgs(True)
        co.mute(True)
        # 清理插件，不走代理
        # co.remove_extensions()
        # json_str = '{"server": ""}'
        # write_json_to_file(json_str,pre_proxy_file)
        page = ChromiumPage(co)

    return page

def get_proxy_with_pac(proxy_url, username, password):
    """使用 PAC 文件设置带认证的代理"""
    # 构建 PAC 文件内容
    pac_content = f"""function FindProxyForURL(url, host) {{
        return "PROXY {username}:{password}@{proxy_url}";
    }}"""
    
    # 编码为 Base64
    pac_base64 = base64.b64encode(pac_content.encode('utf-8')).decode('utf-8')
    # 创建 Data URI
    pac_url = f'data:application/x-javascript-config;base64,{pac_base64}'
    
    return f'--proxy-pac-url={pac_url}'
    
def send_youdu_message(from_user, to_user, message, msgtype='text', title='', digest='', image='', showfront=1):
    # 有度消息发送 API 的 URL，这里需要替换为实际的 URL
    url = f"https://youdu-im.chinajumei.cn:21188/send.php?msgtype={msgtype}&title={title}&digest={digest}&image={image}&showfront={showfront}"
    token_str = f'{from_user}{to_user}{datetime.now().strftime("%Y%m%d")}im.chinajumei.cn{message}'
    token = hashlib.md5(token_str.encode()).hexdigest()

    # 请求头，包含访问令牌
    # headers = {
    #     "Content-Type": "application/json",
    # }
    # 请求体，包含接收者和消息内容
    params = {
        'from': from_user,
        'message': message,
        'to': to_user,
        'token': token
    }
    try:
        # 发送 POST 请求
        # 禁用不安全请求警告
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        response = requests.post(url, data=params,verify=False)
        # print(url)
        # print(params)
        # print(response)
        # 检查响应状态码
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}，响应内容: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"请求发生异常: {e}")
        return None
    
def replace_special_chars(input_string):
    # 定义正则表达式模式，包含英文标点
    pattern = r'[^a-zA-Z0-9\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef.,?!:;\'"()<>/\\-]'
    # 使用 re.sub() 方法替换匹配到的特殊字符为空字符串
    result = re.sub(pattern, '', input_string)
    return result
            

def with_timeout(timeout):
    def decorator(func):
        def wrapper(*args, **kwargs):
            thread = TimeoutThread(target=func, args=args, kwargs=kwargs)
            thread.start()
            thread.join(timeout)
            if thread.is_alive():
                print("Function timed out")
                raise Exception('Function timed out')
                result = None
            elif thread.error:
                raise thread.error
            else:
                result = thread.result
            return result
        return wrapper
    return decorator

def is_filter_keywords(content):
    from config.common_config import cfg_filter_keywords
    for keyword in cfg_filter_keywords:
        if keyword in content:
            return True
    return False

def get_hangye_type(hangye):
    from config.common_config import cfg_hangye_types
    # 遍历配置中的每个类别
    for category, industries in cfg_hangye_types.items():
        # 如果行业名称完全匹配列表中的某个行业
        if hangye in industries:
            # 只返回主行业或辅行业，忽略其他类别
            if category in ['主行业', '辅行业']:
                return category
            else:
                return '弱行业'  # 或根据需求处理其他类别
    
    # 如果没有找到匹配的行业
    return '弱行业'

def get_comment_level(text):
    from config.common_config import cfg_s_comment_keywords
    for keyword in cfg_s_comment_keywords:
        if keyword in text:
            return 'S'
    pattern = r'^\s*\[[^\]]*\](?:\s*\[[^\]]*\])*\s*$'
    if bool(re.match(pattern, text)):
        return 'B'
    else:
        return 'A'

def get_next_runtime(current_time: datetime, resource_level: str,type:str = 0) -> datetime:
    """根据资源等级计算下次运行时间
    
    Args:
        current_time: 当前时间
        resource_level: 资源等级，支持'S', 'A', 'B'
    
    Returns:
        下次运行时间
    """
    if resource_level == 'S':
        # 视频S级资源：每5分钟执行一次
        if type == 1:
            # 定义两个抓取时间点
            morning_time = dt_time(9, 0)  # 早上9点
            afternoon_time = dt_time(14, 0)  # 下午2点
            
            # 转换为今天的具体时间
            today_morning = datetime.combine(current_time.date(), morning_time)
            today_afternoon = datetime.combine(current_time.date(), afternoon_time)
            
            # 判断下次抓取时间
            if current_time < today_afternoon:
                return today_afternoon
            else:
                #下次抓取为明天早上
                return datetime.combine(current_time.date() + timedelta(days=1), morning_time)
        elif type == 2:
           next_run = current_time + timedelta(minutes=30)
        elif type == 3:
           next_run = current_time + timedelta(minutes=60)
        else:
            next_run = current_time + timedelta(minutes=10)
        return next_run
    
    elif resource_level == 'A':
        # A级资源：每天同一时间执行
        next_run = current_time + timedelta(days=1)
        return next_run
    
    elif resource_level == 'B':
        # B级资源：每周同一时间执行
        next_run = current_time + timedelta(days=7)
        return next_run
    
    else:
        raise ValueError(f"不支持的资源等级: {resource_level}")

def getToUser(db, hangye_type,touser = '',is_private = 0):
    # 获取今天的日期
    if is_private:
        return '骆云飞'
    today = datetime.today()
    if today.weekday() == 5:
        return '彭鑫萍'
    if touser: 
        return touser
    from config.common_config import cfg_send_users 
    # users = ['骆云飞','莫俊尧','张奎']
    users = cfg_send_users
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    userstr = "'" + "','".join(users) + "'"
    sql = f"SELECT touser, COUNT(*) as count,max(addtime) as maxtime FROM craw_douyin_comment_touser WHERE touser IN ({userstr}) AND addtime>'{today}' and hangye_type='{hangye_type}' GROUP BY touser order by count,maxtime"

    results = db.execute_query(sql)
    if results:
        queried_tousers = [result['touser'] for result in results]

        # 找出没出现过的 touser
        not_appeared_tousers = [
            touser for touser in users if touser not in queried_tousers]
        if not_appeared_tousers:
            # 如果有没出现过的，随机选一个
            print(not_appeared_tousers)
            return random.choice(not_appeared_tousers)
        else:
            # 如果都出现过，找到出现次数最少的 touser
            # print('如果都出现过，找到出现次数最少的 touser')
            min_count = float('inf')
            min_count_touser = None
            for result in results:
                touser = result['touser']
                count = result['count']
                print(touser, count)
                if count < min_count:
                    min_count = count
                    min_count_touser = touser
            return min_count_touser

    else:
        return random.choice(users)

def parse_arguments():
    """解析命令行参数"""
    import argparse
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='处理命令行参数')
    
    # 添加参数
    parser.add_argument('-port', type=int, help='端口号')
    parser.add_argument('-url', type=str, help='URL地址')
    parser.add_argument('-datapath', type=str, help='数据路径')
    parser.add_argument('-useproxy', type=int, help='使用代理')
    parser.add_argument('-liveid', type=str, help='直播id')
    
    # 解析参数
    args = parser.parse_args()
    
    # 返回解析后的参数
    return args

def export_to_csv(
    data: List[Dict[str, Any]],
    filename: str = "data.csv",
    fieldnames: Optional[List[str]] = None,
    encoding: str = "utf-8",
    with_bom: bool = True,  # 默认添加 BOM，提高兼容性
    excel_compatible: bool = True  # 是否为 Excel 兼容性优化
) -> Response:
    """
    将数据列表导出为 CSV 文件
    
    Args:
        data: 字典列表，每个字典代表一行数据
        filename: 导出的 CSV 文件名
        fieldnames: CSV 文件的列名，默认为 data 中第一个字典的键
        encoding: CSV 文件的编码，默认为 utf-8
        with_bom: 是否在 UTF-8 文件开头添加 BOM 标记
        excel_compatible: 是否为 Excel 兼容性优化
        
    Returns:
        FastAPI 响应对象，包含 CSV 文件内容
    """
    # 创建内存中的文件对象
    output = StringIO()
    
    try:
        # 如果未指定列名，则使用数据中的第一个字典的键
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        
        # 写入 CSV 数据
        writer = csv.DictWriter(
            output, 
            fieldnames=fieldnames or [],
            lineterminator='\r\n'  # 确保 Windows 换行符，提高 Excel 兼容性
        )
        
        # 写入头部
        writer.writeheader()
        
        # 写入数据行
        if excel_compatible:
            # 为 Excel 兼容性优化：
            # 1. 确保字符串值用双引号包围
            # 2. 处理特殊字符
            for row in data:
                processed_row = {}
                for key, value in row.items():
                    if value is None:
                        processed_row[key] = ''
                    elif isinstance(value, str):
                        # 确保字符串值用双引号包围
                        processed_row[key] = f'{value}'
                    else:
                        processed_row[key] = str(value)
                writer.writerow(processed_row)
        else:
            # 标准 CSV 写入
            writer.writerows(data)
        
        # 获取 CSV 内容
        csv_content = output.getvalue()
        
        # 编码处理
        if encoding.lower() == "utf-8" and with_bom:
            # 添加 UTF-8 BOM 标记
            csv_bytes = b'\xef\xbb\xbf' + csv_content.encode('utf-8')
            content_type = "text/csv; charset=utf-8-sig"
        else:
            # 普通编码
            csv_bytes = csv_content.encode(encoding)
            content_type = f"text/csv; charset={encoding}"
        
        # 创建响应对象
        response = Response(
            content=csv_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": content_type,
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
        return response
    
    except Exception as e:
        # 发生错误时返回错误信息
        error_message = f"Error: {str(e)}"
        if encoding.lower() == "utf-8" and with_bom:
            error_bytes = b'\xef\xbb\xbf' + error_message.encode('utf-8')
            content_type = "text/plain; charset=utf-8-sig"
        else:
            error_bytes = error_message.encode(encoding)
            content_type = f"text/plain; charset={encoding}"
            
        response = Response(
            content=error_bytes,
            status_code=500,
            media_type=content_type
        )
        return response

def get_ua_and_cookie(url = "https://www.douyin.com/"):
    print("\n🚀 正在自动打开浏览器，请登录抖音，登录完成后按回车继续...")
    print(url)
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    page = ChromiumPage(co)
    page.get(url)
    
    # 等待用户按回车
    input("\n✅ 登录完成后请按回车键开始抓取...")
    
    # 获取 UA
    ua = page.run_js("return navigator.userAgent")
    
    # 获取 Cookie
    cookies = page.run_js("return document.cookie")
    page.quit()
    
    print("✅ 已自动获取 UA 和 Cookie")
    return ua.strip(), cookies.strip()
def getemptypage(headless = False):
    print("\n🚀 启动浏览器...")
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    if headless:  
        print("隐藏浏览器")
        co.headless(True)
    page = ChromiumPage(co)
    return page
def navigate_to_url(url,isclose = True,headless = False):
    page = getemptypage(headless)
    tab = page.new_tab()
    flag = tab.get(url)
    if not flag:
        return False
    print("✅ 已打开浏览器")
    time.sleep(random.randint(1, 3))
    element = page.ele('x://*[contains(text(), "你要观看的视频不存在")]')
    if element:
        print('你要观看的视频不存在')
        return False
    element = page.ele('x://*[contains(text(), "用户不存在")]')
    if element:
        print('用户不存在')
        return False  
    if isclose:  
        tab.close()
    return page

def update_params_from_url(url: str, fixed_params: dict) -> str:
    """
    从URL中提取查询参数，更新固定参数字典，并返回JSON字符串
    
    参数:
        url: 待解析的URL
        fixed_params: 固定参数字典（会被更新）
    
    返回:
        格式化后的JSON字符串
    """
    # 1. 解析URL，提取查询参数
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)  # 解析后的值是列表格式
    
    # 2. 处理参数：把列表转成单个字符串
    processed_params = {}
    for key, value in query_params.items():
        processed_params[key] = value[0] if isinstance(value, list) else value
    
    # 3. 只更新 fixed_params 中**已存在**的键（核心逻辑）
    updated_params = fixed_params.copy()  # 复制原字典，不修改原值
    for param_key in updated_params:
        if param_key in processed_params:
            updated_params[param_key] = processed_params[param_key]
    
    # 4. 转为格式化的JSON字符串
    return json.dumps(updated_params, ensure_ascii=False, indent=4)

def get_agent_catid(category_name):
    # 品类 => 编号 对应关系（你可以无限加）
    category_map = {
        "衣柜": 70,
        "门窗": 276,
        "地板": 32,
        "集成灶": 393,
        "卫浴": 244,
        "顶墙": 33,
        "木门": 477,
        "净水器": 387,
    }

    # 返回对应编号，找不到默认返回70
    return category_map.get(category_name.strip(), 70)

def parse_phones(phone_str):
    """
    把字符串 "13800138000,13900139000" 转成 phone 和 phone2
    :return: (phone, phone2)
    """
    if not phone_str:
        return "", ""

    # 1. 按逗号分割成数组
    phone_list = phone_str.split(",")

    # 2. 去除空字符串 + 去前后空格
    phone_list = [p.strip() for p in phone_list if p.strip()]

    # 3. 去重（保持顺序）
    unique_list = []
    for p in phone_list:
        if p not in unique_list:
            unique_list.append(p)

    # 4. 取值：第一个给phone，第二个给phone2，没有就为空
    phone = unique_list[0] if len(unique_list) >= 1 else ""
    phone2 = unique_list[1] if len(unique_list) >= 2 else ""

    return phone, phone2
def baoming(data, to_user = ''):
    if not to_user:
        to_user = '骆云飞'
    if to_user == '骆云飞':
        chinaoausername = '抖音拓展09'
    
    url = "https://api2.chinabm.cn/ajax.php"
    hangye = data.get('hangye', '')
    agentcatid = get_agent_catid(hangye)
    phone, phone2 = parse_phones(data.get('phone'))
    if not agentcatid:
        return False
    params = {
        'moduleid': 23,
        'action': 'agent',
        'dosubmit': 1,
        'comefrom': 'https://m.chinabm.cn/tool/1/jmgw3.php?time=1',
        'source': 'M工具-专属加盟管家',
        'hidetitle': '立即咨询',
        'agentcatid': agentcatid,
        'title': data.get('nickname','匿名'),
        'phone': phone,
        'content_phone2': phone2,
        'douyin_url': data.get('douyin_url',''),
        'douyin_inputtime': data.get('douyin_inputtime',''),
        'content_auto':'',
        'content_brand':'无',
        'content':data.get('content',''),
        'cometype':data.get('cometype','') or '品牌/厂家',
        'chinaoausername': chinaoausername
    }
    
    try:
        # 禁用不安全请求警告
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        # 发送请求
        # response = requests.post(url, data=params, verify=False, timeout=10)
        response = requests.get(url, params=params, verify=False, timeout=10)
        
        # ==========================================
        # 👇 这里直接打印 **完整带所有参数的 URL**
        # ==========================================
        print("✅ 完整 GET 请求 URL：")
        print(response.url)

        print("=== 请求URL ===")
        print(url)
        print("=== 请求参数 ===")
        print(params)
        print("=== 响应状态码 ===")
        print(response.status_code)
        print("=== 原始响应内容 ===")
        print(response.text)  # 这里能看到真实返回，方便你排查
        
        # 只有状态码200 且 内容不为空 才尝试解析JSON
        if response.status_code == 200:
            return True
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
        
    except requests.RequestException as e:
        print(f"请求发生异常: {e}")
        return None