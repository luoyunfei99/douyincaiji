from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
from datetime import datetime, timedelta
import time
from my_sql import MySQLHandler
import cfun
import sys,json,re
import random
from config.mysql_config import mysql_config

def extract_json(raw_string):
    """从混合文本中提取所有有效JSON对象或数组"""
    results = []
    remaining = raw_string.strip()
    
    while remaining:
        # 匹配JSON对象或数组的起始
        json_start_pattern = r'(\{|\[)'
        json_start_match = re.search(json_start_pattern, remaining)
        
        if not json_start_match:
            break  # 没有更多JSON
        
        # 确定JSON的起始类型和位置
        start_char = json_start_match.group(1)
        end_char = '}' if start_char == '{' else ']'
        start_idx = json_start_match.start(1)
        
        # 跳过起始标记前的非JSON内容
        remaining = remaining[start_idx:]
        count = 1
        current_idx = 1  # 从起始标记后的字符开始
        
        # 寻找匹配的结束标记
        valid = False
        while current_idx < len(remaining):
            char = remaining[current_idx]
            
            # 处理转义字符（如 \" 或 \\）
            if char == '\\' and current_idx + 1 < len(remaining):
                current_idx += 2  # 跳过转义字符
                continue
                
            if char == start_char:
                count += 1
            elif char == end_char:
                count -= 1
                
            if count == 0:
                json_str = remaining[:current_idx + 1].strip()
                try:
                    # 验证JSON格式
                    parsed = json.loads(json_str)
                    results.append(parsed)
                    valid = True
                except json.JSONDecodeError:
                    print(f"JSON格式错误: {json_str[:50]}...")
                
                break
                
            current_idx += 1
        
        # 移动到剩余文本
        if valid:
            remaining = remaining[current_idx + 1:].strip()
        else:
            # 如果未找到有效的结束标记，尝试从下一个可能的起始位置继续
            remaining = remaining[1:].strip()
    
    return results

def is_within_seven_days(timestamp,days):
     # 获取当前时间戳（以秒为单位）
    current_timestamp = datetime.now().timestamp()
    
    # 计算7天对应的秒数（7天 * 24小时 * 60分钟 * 60秒）
    seven_days_in_seconds = days * 24 * 60 * 60
    
    # 计算时间差（秒）
    time_difference = current_timestamp - timestamp
    
    # 判断时间差是否在7天内（即差值小于等于7天的总秒数，且差值非负）
    return 0 <= time_difference <= seven_days_in_seconds

#获取关键非广告视频，自动入库B级资源
def getKeywordMinfo(page,keyword,pid):
    tab = page.new_tab()
    time.sleep(1)
    # /aweme/v1/web/general/search/single/
    listen_url2 = 'douyin.com/aweme/v1/web/general/search/single'
    tab.listen.start(listen_url2)  # 开始监听
    flag = tab.get(f'https://www.douyin.com/root/search/{keyword}&type=general')
    # ele = tab('x://*[@id="search-result-container"]/div[1]/div/div/')
    # print(ele)
    # tab.actions.move_to(ele_or_loc=ele).click(f'x://*[contains(text(), "{rz_str}")]')
    time.sleep(1)
    if not flag:
        return False
    time.sleep(1)
    # e = tab.ele('x://*[@class="_tawtVou"]/span[2]')
    # e.scroll.to_bottom()
    # time.sleep(2)
    results = []
    for w in range(10):
        print(str(w)+'#######\n')
        try:
            res = tab.listen.wait(timeout=2)  # 等待并获取一个数据包
            # print(res)
            if not isinstance(res, bool):
                # json_datas = extract_json(res.response.body)
                # print(len(json_datas))
                json_datas = res.response.body['data']
                if len(json_datas) > 0:
                    now = datetime.now()
                    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                    for i, result in enumerate(json_datas, 1):
                        try:
                            # print(f"  数据: {result.get('data')[0]['aweme_info']}")
                            aweme_id = result['aweme_info']['aweme_id']
                            desc = result['aweme_info']['desc']
                            create_time = result['aweme_info']['create_time']
                            uid = result['aweme_info']['author']['uid']
                            nickname = result['aweme_info']['author']['nickname']
                            url = 'https://www.douyin.com/video/'+aweme_id #视频地址
                            last_runtime = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S") #抓取视频一周内的留言
                            #采集到的视频插入视频留言采集表
                            tdata = {
                                'keyword':nickname,
                                'url':url,
                                'level':'B',
                                'last_runtime':last_runtime,
                                'addtime':nowtime,
                                'hangye':'其他',
                                'hangye_type':'弱行业',
                                'type':'周期抓取',
                            }
                            if is_within_seven_days(create_time,7):
                                print(tdata)
                                results.append(tdata)
                            db.insert('craw_douyin_url', tdata)
                        except Exception as e:
                            print(f'报错：{e}') 
                            # print(f'数据格式:{result}')
                            pass            
                else:
                    print('未获取到视频数据')
            time.sleep(3)
            tab.scroll.to_bottom()  # 滚动到底部
            
        except KeyboardInterrupt:
            print("程序被用户中断，已停止更新操作")
            return
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            pass
    print(keyword, '已经搜索完毕')
    tab.close()
    return results

# 关键词 非广告视频采集
if __name__ == '__main__':
    args = cfun.parse_arguments()
    # tpage = cfun.getGoolePage(args.port,args.datapath,False)
    # tpage = cfun.randPage(9111, r'C:/Program Files/Google/Chrome/Application', False)
    # rs = getKeywordMinfo(tpage,'全屋定制加盟',1)
    # print(rs)
    # exit()
    while True: 
        db = MySQLHandler(**mysql_config)
        db.connect()
            
        pid = 0
        tmpinfo = None
        tmpinfo=db.execute_query(f'select * from craw_douyin_keyword where status=1 and (next_runtime is null or next_runtime<=now()) and is_run = 0 order by id asc limit 1')
        if not tmpinfo:
            if i==0:
                print('没有要操作的数据')
            time.sleep(60)
        else:
            ids = [row['id'] for row in tmpinfo]
            if ids:
                # 将id列表转换为适合SQL的字符串格式
                id_str = ','.join(map(str, ids))
                # 执行SQL更新语句
                db.execute_query(f'UPDATE craw_douyin_keyword SET is_run=1 WHERE id IN ({id_str})')    

            # tpage = cfun.randPage(9111, r'C:/Program Files/Google/Chrome/Application', False)
            tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
            for tdata in tmpinfo:
                pid = tdata['id']
                kwyword = tdata['keyword']
                print(pid)     
                rs = getKeywordMinfo(tpage,kwyword,pid)
                if rs:
                    now = datetime.now()
                    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                    next_runtime = cfun.get_next_runtime(now,'B',0)
                    last_count = len(rs)
                    #更新最后处理时间
                    r = db.update('craw_douyin_keyword',{'last_runtime':nowtime,'last_count':last_count,'next_runtime':next_runtime,'is_run':0},f'id="{pid}"')
                    if not r:
                        break
                else:
                    break    
    db.disconnect()    
    time.sleep(1)