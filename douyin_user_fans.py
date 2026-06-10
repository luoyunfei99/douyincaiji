from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
from datetime import datetime, timedelta
import time
from my_sql import MySQLHandler
import cfun
import sys,json,re
import random
from config.mysql_config import mysql_config

def getUserFans(page,url,hid,touser=None):
    time.sleep(1)
    tab = page.new_tab()
    tab.listen.start('www.douyin.com/aweme/v1/web/user/follower/list/')  # 开始监听
    time.sleep(1)
    flag = tab.get(url)
    if not flag:
        return False
    print(url)
    tab.wait.load_start()
    target_div = tab.ele('css:div[data-e2e="user-info-fans"]')
    # print(target_div)
    if target_div:
        target_div.click()
    time.sleep(1)
    now = datetime.now()
    for w in range(10):
        print(str(w)+'#######\n')
        try:
            res = tab.listen.wait(timeout=2)  # 等待并获取一个数据包
            # print(res)
            if not isinstance(res, bool):
                followers = res.response.body['followers']
                # print(followers)
                # 提取粉丝信息
                if len(followers) > 0 :
                    for i, follower in enumerate(followers, 1):
                        nickname = follower['nickname']  # 用户名
                        sec_uid = follower['sec_uid']
                        uid = follower['uid']
                        unique_id = follower['unique_id']  # unique_id
                        enterprise_verify_reason = follower['enterprise_verify_reason']
                        addtime = now.strftime("%Y-%m-%d %H:%M:%S")
                        signature = cfun.replace_special_chars(follower['signature'])  # 用户介绍
                        phone = cfun.extract_and_join_phone_numbers(str(unique_id)+signature)
                        url = f'https://www.douyin.com/user/{sec_uid}?from_tab_name=main' #抖音主页链接
                        tdata = {
                            'url':url,
                            'nickname':nickname,
                            'sec_uid':sec_uid,
                            'signature':signature,
                            'uid':uid,
                            'enterprise_verify_reason':enterprise_verify_reason,
                            'phone':phone,
                            'addtime':addtime,
                            'unique_id':unique_id,
                            'hid':hid
                        }
                        # print(f'插入数据')
                        # print(tdata) 
                        db.insert('craw_douyin_hao_fans', tdata)
                        # 当抓取到号码的时候提醒
                        if phone:
                            content = f'抖音主页链接：{url}'
                            if phoneuserarr:
                                content += f'\n\手机号：{phone}\n'
                            if touser:
                                cfun.send_youdu_message(21,touser,content)                       
                else:
                    print(f'未获取到数据')      
            else:
                element = tab.ele('x://*[contains(text(), "由于该用户隐私设置，粉丝列表不可见")]')
                if element:
                    print('用户隐私设置，粉丝列表不可见')                         
        except KeyboardInterrupt:
            print("程序被用户中断，已停止更新操作")
            return    
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            pass
        time.sleep(3)
        # 滚动到粉丝列表底部
        container = tab.ele('css:div[data-e2e="user-fans-container"]')
        if container:
            last_height = tab.run_js('return arguments[0].scrollHeight', container)
            while True:
                tab.run_js('arguments[0].scrollTo(0, arguments[0].scrollHeight)', container)
                time.sleep(1)
                new_height = tab.run_js('return arguments[0].scrollHeight', container)
                if new_height == last_height:
                    break
                last_height = new_height       
    try:
        tab.close() 
    except:
        pass
    return True

if __name__ == '__main__':
    args = cfun.parse_arguments()
    # 慢速模式
    is_slow = 1
    while True: 
        db = MySQLHandler(**mysql_config)
        db.connect()
        tmpinfo=db.execute_query(f'select * from craw_douyin_hao_url where is_fans = 1')
        if not tmpinfo:
            print('没有要操作的数据')
            time.sleep(60)
        ids = [row['id'] for row in tmpinfo]
        if ids:
            # 将id列表转换为适合SQL的字符串格式
            id_str = ','.join(map(str, ids))
            # 执行SQL更新语句
            db.execute_query(f'UPDATE craw_douyin_hao_url SET is_fans=0 WHERE id IN ({id_str})')    
        tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
        # tpage = cfun.randPage(9111, r'C:/Program Files/Google/Chrome/Application', False)
        for tdata in tmpinfo:
            url = tdata['url']
            hid = tdata['id']
            touser = tdata['touser']
            rs = getUserFans(tpage, url, hid, touser)
        db.disconnect()    
        time.sleep(1)