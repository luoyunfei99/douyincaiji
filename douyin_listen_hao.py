from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
import time
import re
from my_sql import MySQLHandler
import random
import cfun
import datetime
import sys
from config.mysql_config import mysql_config

def getUserVideos(page,pid,url,keyword = '',level='',hangye='',hangye_type='',last_runtime = None,db_video_count = 0,is_private = 0,touser = ''):
    tab = page.new_tab()
    tab.listen.start('www.douyin.com/aweme/v1/web/aweme/post/')  # 开始监听
    time.sleep(1)
    flag = tab.get(url)
    if not flag:
        return False
    time.sleep(2)
    try:
        break_str = tab.ele('x://*[contains(text(), "用户不存在")]')
        if break_str:
            print("用户不存在")
            tab.close()
            return []
        break_str = tab.ele('x://*[contains(text(), "暂无内容")]')
        if break_str:
            print("暂无内容")
            tab.close()
            return []
        break_str2 = tab.ele('x://*[contains(text(), "私密账号")]')
        if break_str2:
            print("私密账号")
            tab.close()
            return []
    except:
        pass
    
    element = tab.ele('x://*[@id="semiTabpost"]/div/h2/span[2]')
    if element:
        new_count = element.text
        if int(new_count) > int(db_video_count):
            db.execute_update(f'update craw_douyin_listen_user set video_count={new_count} where id={pid}')
        else:
            print('没有新的视频')
            tab.close()
            return True

    before_day = 5
    dt_obj = datetime.datetime.now() - datetime.timedelta(days=before_day)
        
    # 将 datetime 对象转换为时间戳
    needtime = int(dt_obj.timestamp())
    for w in range(3):
        print(str(w)+'\n')
        try:
            res = tab.listen.wait(timeout=5)  # 等待并获取一个数据包
            if not isinstance(res, bool):
                for i in res.response.body['aweme_list']:
                    aweme_id = i['aweme_id']
                    item_title = i['item_title']
                    turl = 'https://www.douyin.com/video/'+aweme_id
                    desc = i['desc']
                    create_time = i['create_time']
                    print(str(create_time)+'|'+str(needtime))
                    if create_time < needtime:
                        continue

                    phone = cfun.extract_and_join_phone_numbers(desc)
                    print(aweme_id, "\t",item_title,"\t",turl,"\t",desc,"\t",phone)
                    if not last_runtime or i['create_time'] > last_runtime:
                        dt_object = datetime.datetime.fromtimestamp(create_time)
                        create_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                        tdata = {
                            'pid':pid,
                            'url':turl,
                            'keyword':keyword,
                            'level':level,
                            'hangye':hangye,
                            'hangye_type':hangye_type,
                            'last_runtime':create_time,
                            'create_time':create_time,
                            'status':1,
                            'type':'实时监听',
                            'is_private':is_private,
                            'touser':touser
                        }
                        db.insert('craw_douyin_url',tdata)
                tab.close()
                return True
                                
            else:    
                element = tab.ele('x://*[contains(text(), "暂时没有更多了")]')
                if element:
                    print('暂时没有更多了')
                    break
                else:
                    continue
            
        except KeyboardInterrupt:
            if pid is not None:
                db.execute_query(f'UPDATE craw_douyin_listen_user SET is_run=0 WHERE id = {pid}')   
            print("程序被用户中断，已停止更新操作")
            exit()
        except:
            # pass
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
    tab.close()
    return True

#重置数据状态
def reset_runstatus(db):
    db.execute_update(
        f'update craw_douyin_listen_user set is_run=0 where is_run=1 and level = "S" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -1 hour)')
    db.execute_update(
        f'update craw_douyin_listen_user set is_run=0 where is_run=1 and level = "A" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -1 day)')
    db.execute_update(
        f'update craw_douyin_listen_user set is_run=0 where is_run=1 and level = "B" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -7 day)')

if __name__ == '__main__':
    i=0
    args = cfun.parse_arguments()
    while True: 
        try:
            nowhour = datetime.datetime.now().hour
            if nowhour < 7 or nowhour >= 23:
                time.sleep(60)
                continue
            db = MySQLHandler(**mysql_config)
            db.connect()
            # 定期重置监听
            reset_runstatus(db)
            pid = 0
            tmpinfo = None
            tmpinfo=db.execute_query(f'select * from craw_douyin_listen_user where status=1 and (next_runtime is null or next_runtime<=now()) and is_run = 0  order by last_runtime,field(level,"S","A","B","") limit 1')

            if not tmpinfo:
                print('没有要操作的数据')
                time.sleep(60)
                
            else:
                pid = tmpinfo[0]['id']
                db.execute_query(f'UPDATE craw_douyin_listen_user SET is_run=1 WHERE id = {pid}')    

                userurl = tmpinfo[0]['url']
                #提醒人
                keyword = tmpinfo[0]['keyword']
                level = tmpinfo[0]['level']
                hangye = tmpinfo[0]['hangye']
                hangye_type = tmpinfo[0]['hangye_type']
                last_runtime = tmpinfo[0]['last_runtime']
                db_video_count = tmpinfo[0]['video_count']
                is_private = tmpinfo[0]['is_private']
                touser = tmpinfo[0]['touser']
                
                if last_runtime:
                    last_runtime = last_runtime.timestamp()
                else:
                    last_runtime = 0
                print(userurl+'\n')
                tpage = cfun.getemptypage(True)
                if not tpage:
                    time.sleep(10)
                    continue

                print('getUserVideos')
                rs = getUserVideos(tpage,pid,userurl,keyword,level,hangye,hangye_type,last_runtime,db_video_count,is_private,touser)
                if rs:
                    #更新最后处理时间
                    now = datetime.datetime.now()
                    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
            
                    next_runtime = cfun.get_next_runtime(now,level,3)
                    db.update('craw_douyin_listen_user',{'last_runtime':nowtime,'next_runtime':next_runtime,'is_run':0},f'id="{pid}"')
                # tpage.quit()
            db.disconnect()    
            time.sleep(3)
            i += 1
        except KeyboardInterrupt:
            if pid is not None:
                db.execute_query(f'UPDATE craw_douyin_listen_user SET is_run=0 WHERE id = {pid}')   
            print("程序被用户中断，已停止更新操作")
            exit()
        except:
            if pid is not None:
                db.execute_query(f'UPDATE craw_douyin_listen_user SET is_run=0 WHERE id = {pid}')   

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            time.sleep(10)
            pass


        
            


