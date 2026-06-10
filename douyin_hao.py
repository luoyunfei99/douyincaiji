from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
import time
import re
from my_sql import MySQLHandler
import random
import cfun
import datetime
import sys
from config.mysql_config import mysql_config

def getUserInfo(page,pid,url,touser,last_runtime=None,is_history=0,is_listen_user=0):
    tab = page.new_tab()
    listen_url2 = 'www.douyin.com/aweme/v1/web/user/profile/other/'
    tab.listen.start(listen_url2)  # 开始监听
    time.sleep(1)
    flag = tab.get(url)
    if not flag:
        return False
    time.sleep(2)

    phoneuserarr = []
    count = 0
    for w in range(10):
        try:
            res = tab.listen.wait(timeout=5)  # 等待并获取一个数据包
            if not isinstance(res, bool):
                user = res.response.body['user']
                nickname = user['nickname']  # 用户名
                unique_id = user['unique_id']  # unique_id
                signature = cfun.replace_special_chars(user['signature'])  # 用户介绍
                phone = cfun.extract_and_join_phone_numbers(str(unique_id)+signature)
                db.update('craw_douyin_hao_url',{'nickname':nickname,'unique_id':unique_id,'signature':signature,'phone':phone},f'id="{pid}"')
                if phone:
                    count += 1
                    phoneuserarr.append({'userurl': url, 'phone': phone, 'desc': signature})
            else:    
                pass
            break
            
        except:
            pass
    try:
        if not last_runtime and count>0:
            content = f'抖音主页链接：{url}'
            if phoneuserarr:
                content += f'\n\n匹配手机号信息：\n'
                for i in phoneuserarr:
                    content += f'手机号：{i["phone"]}，内容：{i["desc"]}\n'    
            if touser:
                cfun.send_youdu_message(21,touser,content)
        tab.close() 
    except:
        pass
    return True

def getUserVideos(page,pid,url,touser,keyword = '',level='',hangye='',hangye_type='',islisten=0,last_runtime = None,is_history = 0,is_listen_user = 0):
    time.sleep(1)
    tab = page.new_tab()
    if is_listen_user:
        tab.listen.start('www.douyin.com/aweme/v1/web/home/search/item/')  # 开始监听
    else:
        tab.listen.start('www.douyin.com/aweme/v1/web/aweme/post/')  # 开始监听
    
    time.sleep(1)
    flag = tab.get(url)
    if not flag:
        return False
    time.sleep(2)

    # 模拟点击搜索加盟字样
    if is_listen_user:
        search_input = tab.ele('x://*[@id="user_detail_element"]/div/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div/input');
        if search_input:
            search_input.input('加盟',True)
            tab.actions.key_down('ENTER')
        else:
            print("未找到搜索元素")
            tab.close()
            return []

    try:
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
  
    phoneuserarr = []
    count = 0
    before_day = 365
    if is_listen_user:
        dt_obj = datetime.datetime.now() - datetime.timedelta(days=before_day)
    else:
        time_str = "2024-04-30 00:00:00"
        time_format = "%Y-%m-%d %H:%M:%S"
        # 将时间字符串转换为 datetime 对象
        dt_obj = datetime.datetime.strptime(time_str, time_format)
    # 将 datetime 对象转换为时间戳
    needtime = int(dt_obj.timestamp())
    have_w = 0
    for w in range(100):
        print(str(w)+'\n')
        if w - have_w > 3:
            break;
        try:
            res = tab.listen.wait(timeout=5)  # 等待并获取一个数据包
            if not isinstance(res, bool):
                have_w = w
                # print(res.response.body['aweme_list'])
                for i in res.response.body['aweme_list']:
                    if is_listen_user:
                        i = i['item']
                    aweme_id = i['aweme_id']
                    item_title = i['item_title']
                    turl = 'https://www.douyin.com/video/'+aweme_id
                    desc = i['desc']
                    create_time = i['create_time']
                    print(str(create_time)+'|'+str(needtime))
                    if is_history and create_time < needtime:
                        continue
                    if is_listen_user and create_time < needtime:
                        continue

                    phone = cfun.extract_and_join_phone_numbers(desc)
                    print(aweme_id, "\t",item_title,"\t",turl,"\t",desc,"\t",phone)
                    if not last_runtime or i['create_time'] > last_runtime or is_history:
                        dt_object = datetime.datetime.fromtimestamp(create_time)
                        create_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                        tdata = {
                            'pid':pid,
                            'aweme_id':aweme_id,
                            'item_title':item_title,
                            'turl':turl,
                            'desc':desc,
                            'phone':phone,
                            'create_time':create_time
                        }
                        db.insert('craw_douyin_hao_video',tdata)
                        if islisten or is_history or is_listen_user:
                            current_time = datetime.datetime.now()
                            if is_listen_user:
                                one_day = datetime.timedelta(days=before_day)
                            else:
                                one_day = datetime.timedelta(days=1)
                            
                            new_time = current_time - one_day

                            # 格式化输出结果
                            yesterday = new_time.strftime("%Y-%m-%d %H:%M:%S")
                            tdata2 = {
                                'pid':pid,
                                'url':turl,
                                'keyword':keyword,
                                'level':level,
                                'hangye':hangye,
                                'hangye_type':hangye_type,
                                'last_runtime':yesterday,
                                'create_time':create_time
                            }
                            if is_history:
                                db.insert('craw_douyin_history_url',tdata2)
                            elif islisten or is_listen_user:
                                tdata2['type'] = '周期抓取'
                                db.insert('craw_douyin_url',tdata2)
                                

                        if phone:
                            count += 1
                            phoneuserarr.append({'userurl': turl, 'phone': phone, 'desc': desc})
            else:    
                element = tab.ele('x://*[contains(text(), "暂时没有更多了")]')
                if element:
                    print('暂时没有更多了')
                    break
                else:
                    continue
            time.sleep(3)
            
            # e = tab.ele('x://div[@class="parent-route-container route-scroll-container IhmVuo1S"]')
            e = tab.ele('x://*[@id="douyin-right-container"]/div[2]')
            
            
            print('scroll')
            e.scroll.to_bottom()
            tab.scroll.to_bottom()  # 滚动到底部
            time.sleep(1)
        except KeyboardInterrupt:
            if pid is not None:
                db.execute_query(f'UPDATE craw_douyin_hao_url SET is_run=0 WHERE id = {pid}')   
            print("程序被用户中断，已停止更新操作")
            exit()
        except:
            # pass
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
    try:
        if count>0 and not is_history and not is_listen_user:
            content = f'抖音视频链接：{url}'
            if phoneuserarr:
                content += f'\n\n匹配手机号信息：\n'
                for i in phoneuserarr:
                    content += f'链接：{i["userurl"]}，手机号：{i["phone"]}，内容：{i["desc"]}\n'
            if touser:
                cfun.send_youdu_message(21,touser,content)
                tdata = {
                        'pid': pid,
                        'hangye_type':'',
                        'touser':touser,
                        'msg':content
                    }
                db.insert('craw_douyin_comment_touser', tdata)
        tab.close() 
    except:
        pass
    return True

#重置数据状态
def reset_runstatus(db):
    db.execute_update(
        f'update craw_douyin_hao_url set is_run=0 where is_run=1 and level = "S" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -8 hour)')
    db.execute_update(
        f'update craw_douyin_hao_url set is_run=0 where is_run=1 and level = "A" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -1 day)')
    db.execute_update(
        f'update craw_douyin_hao_url set is_run=0 where is_run=1 and level = "B" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -7 day)')

if __name__ == '__main__':

    
    # 在连接数据库之后添加以下代码
    # try:
    #     # 设置事务隔离级别为读已提交
    #     set_isolation_level_query = "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"
    #     db.cursor.execute(set_isolation_level_query)
    # except pymysql.Error as e:
    #     print(f"设置事务隔离级别时出错: {e}")
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
            tmpinfo=db.execute_query(f'select * from craw_douyin_hao_url where (status=0 or is_listen_user=1 and (next_runtime is null or next_runtime<=now()) and is_run = 0) order by last_runtime,field(level,"S","A","B","") limit 1')

            if not tmpinfo:
                if i==0:
                    print('没有要操作的数据')
                time.sleep(60)
                
            else:
                pid = tmpinfo[0]['id']
                db.execute_query(f'UPDATE craw_douyin_hao_url SET is_run=1 WHERE id = {pid}')    

                userurl = tmpinfo[0]['url']
                #提醒人
                touser = tmpinfo[0]['touser']
                touser = touser if touser else '骆云飞'
                keyword = tmpinfo[0]['keyword']
                level = tmpinfo[0]['level']
                hangye = tmpinfo[0]['hangye']
                hangye_type = tmpinfo[0]['hangye_type']
                islisten = tmpinfo[0]['islisten']
                last_runtime = tmpinfo[0]['last_runtime']
                is_history = tmpinfo[0]['is_history']
                is_listen_user = tmpinfo[0]['is_listen_user']
                
                if last_runtime:
                    last_runtime = last_runtime.timestamp()
                else:
                    last_runtime = 0
                print(userurl+'\n')
                # tpage = cfun.randPage(9111,r'D:\googledata\data1',True)
                tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
                if not tpage:
                    time.sleep(10)
                    continue
                rs = getUserInfo(tpage,pid,userurl,touser,last_runtime,is_history,is_listen_user)
                if rs:
                    print('getUserVideos')
                    rs = getUserVideos(tpage,pid,userurl,touser,keyword,level,hangye,hangye_type,islisten,last_runtime,is_history,is_listen_user)
                    if rs:
                        #更新最后处理时间
                        now = datetime.datetime.now()
                        nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                
                        next_runtime = cfun.get_next_runtime(now,level,1) if is_listen_user else None
                        db.update('craw_douyin_hao_url',{'status':1,'last_runtime':nowtime,'next_runtime':next_runtime,'is_run':0},f'id="{pid}"')
                    else:
                        #tpage.quit() 
                        break    
                    tpage.quit()
                else:
                    #tpage.quit() 
                    break    
            db.disconnect()    
            time.sleep(3)
            i += 1
        except KeyboardInterrupt:
            if pid is not None:
                db.execute_query(f'UPDATE craw_douyin_hao_url SET is_run=0 WHERE id = {pid}')   
            print("程序被用户中断，已停止更新操作")
            exit()
        except:
            if pid is not None:
                db.execute_query(f'UPDATE craw_douyin_hao_url SET is_run=0 WHERE id = {pid}')   

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            time.sleep(60)
            pass


        
            


