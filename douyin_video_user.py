from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
import time
from my_sql import MySQLHandler
import cfun
import sys
import random
from config.mysql_config import mysql_config
from config.common_config import cfg_is_slow

def getUserInfo(page,pid,commentinfo):
    url = commentinfo['sec_uid']
    tab = page.new_tab()
    listen_url2 = 'douyin.com/aweme/v1/web/user/profile/other/'
    tab.listen.start(listen_url2)  # 开始监听
    time.sleep(1)
    flag = tab.get(url)
    if not flag:
        return False
    time.sleep(1)
    have_w = 0
    for w in range(10):
        if w - have_w > 3:
            break;
        print(str(w)+'#######\n')
        try:
            res = tab.listen.wait(timeout=2)  # 等待并获取一个数据包
            # print(res)
            if not isinstance(res, bool):
                have_w = w
                user = res.response.body['user']
                # print(user)
                nickname = user['nickname']  # 用户名
                unique_id = user['unique_id']  # unique_id
                signature = cfun.replace_special_chars(user['signature'])  # 用户介绍
                phone = cfun.extract_and_join_phone_numbers(str(unique_id)+signature)
                avatar = user['avatar_larger']['url_list'][0]  # 头像
                cover = user['cover_url'][0]['url_list'][0].replace("\u0026", "&")
                address = str(user['province'])+ str(user['city'])
                if 'ip_location' in user:
                    address = address +'|' + user['ip_location']
                data = {'nickname':nickname,'unique_id':unique_id,'signature':signature,'phone':phone,'avatar':avatar,'cover':cover,'address':address}
                print(data)
                db.update('craw_douyin_comment_user',data,f'id="{pid}"')
                if phone and pid:
                    videoinfo= db.execute_query(f'select * from craw_douyin_url where id={pid}')
                    
                    if videoinfo:
                        videoinfo = videoinfo[0]
                        print(videoinfo)
                        tcontent = f'抖音视频链接：{videoinfo["url"]} 留言信息更新了\n\n'
                        content = tcontent + \
                        f'时间：{commentinfo["create_time"]}；评论文字：{commentinfo["text"]}，品牌：{videoinfo["keyword"]}；来源链接：{videoinfo["url"]}，评论内容分级：{videoinfo["hangye_type"]}-{commentinfo["level"]}级留言'
                        print(content)
                        touser = cfun.getToUser(db, videoinfo['hangye_type'])
                        if touser:
                            cfun.send_youdu_message(21, touser, content)
                            tdata = {
                                'pid': commentinfo['pid'],
                                'hangye_type': videoinfo['hangye_type'],
                                'touser': touser,
                                'msg': content
                            }
                            db.insert('craw_douyin_comment_touser', tdata)

                break
            else:
                element = tab.ele('x://*[contains(text(), "用户不存在")]')
                if element:
                    print('用户不存在')
                    break        
                continue
            # break
        except KeyboardInterrupt:
            print("程序被用户中断，已停止更新操作")
            return    
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            pass
    try:
        tab.close() 
    except:
        pass
    return True


if __name__ == '__main__':
    import os
    print(os.environ)
    args = cfun.parse_arguments()
    # print(f"端口号: {args.port}")
    # print(f"URL地址: {args.url}")
    # print(f"数据路径: {args.datapath}")
    # print(f"使用代理: {args.useproxy}")
    if args.url is not None:
        db = MySQLHandler(**mysql_config)
        db.connect()
        print("手动抓取")
        userurl = args.url
        tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
        
        print(userurl+'\n')
        tdata = {"sec_uid":userurl}
        rs = getUserInfo(tpage,0,tdata)
        db.disconnect()
    else:
        i = 0
        # 慢速模式
        is_slow = cfg_is_slow
        while True: 
            try:
                db = MySQLHandler(**mysql_config)
                db.connect()
                #定期重置监听
                # reset_listenstatus(db)
                pid = 0
                tmpinfo = None
                tmpinfo=db.execute_query(f'select * from craw_douyin_comment_user where status=0 and phone="" order by id asc limit 10')
                if not tmpinfo:
                    if i==0:
                        print('没有要操作的数据')
                    time.sleep(60)
                    
                else:
                    tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
                    for tdata in tmpinfo:
                        if is_slow:
                            time.sleep(random.randint(3, 5))
                        pid = tdata['pid']
                        tid = tdata['id']
                        userurl = tdata['sec_uid']
                        print(pid)
                        print(userurl+'\n')
                        # tpage = cfun.randPage(9115,r'D:\googledata\data5',False)
                        rs = getUserInfo(tpage,pid,tdata)
                        if rs:
                            #更新最后处理时间
                            r = db.update('craw_douyin_comment_user',{'status':1},f'id="{tid}"')
                            if not r:
                                break
                        else:
                            #tpage.quit() 
                            break    
                    tpage.quit()
                db.disconnect()    
                time.sleep(1)
                i += 1
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
                time.sleep(10)
                pass


        
            


