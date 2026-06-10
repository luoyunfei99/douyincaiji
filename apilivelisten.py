from DrissionPage import Chromium, ChromiumPage, ChromiumOptions
from datetime import datetime, timedelta
import time
import re
from my_sql import MySQLHandler
import random
import sys
import cfun
from config.mysql_config import mysql_config
from config.common_config import cfg_is_slow
import traceback
import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 直播开启监听
def getDouyinLiveState(page,liveid):
    tab = page.new_tab()
    time.sleep(1)
    url = f'https://live.douyin.com/{liveid}'
    flag = tab.get(url)
    time.sleep(1)
    if not flag:
        return False
    time.sleep(1)
    isopen = False
    try:
        element = tab.ele('x://*[contains(text(), "直播已结束")]')
        if element:
            print('直播已结束')
        else:
            isopen = True
            content = f'抖音直播开启啦！{url}'
            print(content)
    except KeyboardInterrupt:
        print("程序被用户中断，已停止更新操作")
        return False
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
        pass
    print(f'{url}，检查完毕')
    try:
        tab.close()
    except:
        pass
    return isopen

if __name__ == '__main__':
    args = cfun.parse_arguments()
    while True:
        try:
            db = MySQLHandler(**mysql_config)
            db.connect()
            tmpinfo = db.execute_query(f'select * from craw_lives where status =0 and islisten=1 and (lastlistentime IS NULL or lastlistentime < DATE_SUB(NOW(), INTERVAL 5 minute))')
            print(tmpinfo)
            if not tmpinfo:
                print('没有要操作的数据')
                time.sleep(60)
            else:
                tpage = cfun.getemptypage(False)
                if tpage:
                    for tdata in tmpinfo:
                        liveid = tdata['liveid']
                        touser = tdata['touser']
                        pid = tdata['id']
                        # print(f'{liveid} 检查直播间是否开启')
                        re =  getDouyinLiveState(tpage,liveid)
                        data = {}
                        now = datetime.now()
                        nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                        data['lastlistentime']=nowtime
                        if re:
                            data['status'] = 1
                        db.update('craw_lives',data,f'id="{pid}"')
            db.disconnect()  
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            pass
        time.sleep(60)   