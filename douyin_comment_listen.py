from DrissionPage import Chromium, ChromiumPage, ChromiumOptions
import time
import datetime
import re
from my_sql import MySQLHandler
import random
import sys
import cfun
from config.mysql_config import mysql_config

def getDataByUrl(page, url, pid, last_runtime,keyword = '',hangye_type = '辅行业',db_comment_count = 0):
    time.sleep(1)
    tab = page.new_tab()
    tab.listen.start('www.douyin.com/aweme/v1/web/comment/list/')  # 开始监听
    time.sleep(1)
    flag = tab.get(url)
    if not flag:
        return False
    print(url)
    time.sleep(2)

    # 获取数据库最后的时间
    count = 0
    phoneuserarr = []
    commentarr = []
    for w in range(10):
        print(str(w)+'#######\n')
        try:
            res = tab.listen.wait(timeout=5)  # 等待并获取一个数据包
            if not isinstance(res, bool):
                new_comment_count = res.response.body['total']
                if new_comment_count == db_comment_count:
                    print('暂无最新的评论信息')
                    break
                for i in res.response.body['comments']:
                    text = i['text']
                    create_time = i['create_time']
                    dt_object = datetime.datetime.fromtimestamp(create_time)
                    create_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")

                    uid = i['user']['uid']  # id
                    unique_id = i['user']['unique_id']  # unique_id
                    short_id = i['user']['short_id']  # 短id
                    nickname = i['user']['nickname']  # 用户名
                    signature = str(i['user']['signature'])  # 用户介绍
                    enterprise_verify_reason = i['user']['enterprise_verify_reason']
                    sec_uid = 'https://www.douyin.com/user/' + \
                        i['user']['sec_uid']+'?from_tab_name=main'  # 加密id
                    follower_count = i['user']['follower_count']  # 粉丝量
                    total_favorited = i['user']['total_favorited']  # 获赞
                    phone = cfun.extract_and_join_phone_numbers(
                        str(unique_id)+sec_uid)
                    # res_list.append([rz_str, keyword, uid,unique_id, short_id, nickname, signature, sec_uid, enterprise_verify_reason, follower_count, total_favorited,phone])
                    tdata = {
                        'pid': pid,
                        'uid': uid,
                        'unique_id': unique_id,
                        'short_id': short_id,
                        'nickname': nickname,
                        'signature': signature,
                        'sec_uid': sec_uid,
                        'enterprise_verify_reason': enterprise_verify_reason,
                        'follower_count': follower_count,
                        'total_favorited': total_favorited,
                        'phone': phone,
                        'text': text,
                        'create_time': create_time
                    }
                    print(tdata)
                    if not last_runtime or i['create_time'] > last_runtime:
                        count += 1
                        commentarr.append(tdata);
                        db.insert('craw_douyin_comment_user', tdata)
                        if phone:
                            phoneuserarr.append({'userurl': sec_uid, 'phone': phone, 'nickname': nickname, 'text': text,'create_time':create_time})
                reply_comments = i['reply_comment']
                # 回复
                if reply_comments:
                    for i in reply_comments:
                        text = i['text']
                        label_type = int(i['label_type'] if i['label_type'] else 0)
                        # 作者回复跳过
                        if label_type == 1:
                            continue
                        create_time = i['create_time']
                        dt_object = datetime.datetime.fromtimestamp(create_time)
                        create_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")

                        uid = i['user']['uid']  # id
                        unique_id = i['user']['unique_id']  # unique_id
                        short_id = i['user']['short_id']  # 短id
                        nickname = i['user']['nickname']  # 用户名
                        signature = str(i['user']['signature'])  # 用户介绍
                        enterprise_verify_reason = i['user']['enterprise_verify_reason']
                        sec_uid = 'https://www.douyin.com/user/' + \
                            i['user']['sec_uid']+'?from_tab_name=main'  # 加密id
                        follower_count = i['user']['follower_count']  # 粉丝量
                        total_favorited = i['user']['total_favorited']  # 获赞
                        phone = cfun.extract_and_join_phone_numbers(
                            str(unique_id)+sec_uid)
                        # res_list.append([rz_str, keyword, uid,unique_id, short_id, nickname, signature, sec_uid, enterprise_verify_reason, follower_count, total_favorited,phone])
                        tdata = {
                            'pid': pid,
                            'uid': uid,
                            'unique_id': unique_id,
                            'short_id': short_id,
                            'nickname': nickname,
                            'signature': signature,
                            'sec_uid': sec_uid,
                            'enterprise_verify_reason': enterprise_verify_reason,
                            'follower_count': follower_count,
                            'total_favorited': total_favorited,
                            'phone': phone,
                            'text': text,
                            'create_time': create_time
                        }
                        print(tdata)
                        if not last_runtime or i['create_time'] > last_runtime:
                            count += 1
                            commentarr.append(tdata);
                            db.insert('craw_douyin_comment_user', tdata)
                            if phone:
                                phoneuserarr.append({'userurl': sec_uid, 'phone': phone, 'nickname': nickname, 'text': text,'create_time':create_time})
                
                # if count==0 and w==0:
                #     print('暂无最新的评论信息')
                #     break

            else:
                element = tab.ele('x://*[contains(text(), "暂时没有更多评论")]')
                if element:
                    print('暂时没有更多评论')
                    break
                else:
                    continue
            time.sleep(3)
            e = tab.ele('x://*[@id="douyin-right-container"]/div[2]')
            e.scroll.to_bottom()
            tab.scroll.to_bottom()  # 滚动到底部
            time.sleep(1)

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            pass
    try:
        if new_comment_count:
            db.update('craw_douyin_url', {'comment_count': new_comment_count}, f"id={pid}")
        if count>0:
            sorted_tdata = sorted(commentarr, key=lambda x: x['create_time'])
            tcontent = f'抖音视频链接：{url} 留言信息更新了\n\n'
            for i in sorted_tdata:
                content = tcontent+f'品牌：{keyword}，用户名：{i["nickname"]}，用户链接：{i["sec_uid"]},时间：{i["create_time"]}，留言内容：{i["text"]}'
                if i["phone"]:
                    content += f'，手机号：{i["phone"]}\n'   
                touser = cfun.getToUser(db,hangye_type)
                if touser:
                    cfun.send_youdu_message(21,touser,content)
                    tdata = {
                        'pid': pid,
                        'hangye_type':hangye_type,
                        'touser':touser,
                        'msg':content
                    }
                    db.insert('craw_douyin_comment_touser', tdata)

            # if phoneuserarr:
            #     content += f'\n\n匹配手机号信息：\n'
            #     for i in phoneuserarr:
            #         content += f'链接：{i["userurl"]}，昵称：{i["nickname"]} ，手机号：{i["phone"]}，评论时间：{i["create_time"]}，评论内容：{i["text"]}\n'
                

        tab.close()
    except:
        pass
    return True


#重置数据状态
def reset_urlstatus(db):
    nowhour = datetime.datetime.now().hour
    if nowhour > 7 and nowhour < 23:
        db.execute_update(
            f'update craw_douyin_url set status=0 where pid>0 and level = "S" and status=1 and last_runtime<date_add(now(),INTERVAL -60 minute)')
        db.execute_update(
            f'update craw_douyin_url set status=0 where pid>0 and level IN("A") and status=1 and last_runtime<date_add(now(),INTERVAL -1 day)')
        db.execute_update(
            f'update craw_douyin_url set status=0 where pid>0 and level IN("B") and status=1 and last_runtime<date_add(now(),INTERVAL -1 day)')


if __name__ == '__main__':
    args = cfun.parse_arguments()
    # 慢速模式
    is_slow = 1
    while True:
        try:
            db = MySQLHandler(**mysql_config)
            db.connect()
            #定期重置查询操作
            # reset_urlstatus(db)
            brandid = 0
            keyword = ''
            last_runtime = ''
            #查询存在要处理数据
            turlinfo = db.execute_query(
                f'select * from craw_douyin_url where pid>0 order by last_runtime limit 10')
            if not turlinfo:
                if i==0:
                    print('没有要操作的数据')
                time.sleep(10)
            else:
                tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
                if not tpage:
                    time.sleep(10)
                    continue
                for tdata in turlinfo:
                    if is_slow:
                        time.sleep(random.randint(10, 20))
                    turl = tdata['url']
                    tid = tdata['id'] 
                    #最后执行时间
                    last_runtime = tdata['last_runtime']
                    #提醒人
                    touser = tdata['touser']
                    # 主行业（门窗/全屋定制/橱柜）		
                    # 辅行业（卫浴/顶墙/地板/集成灶/厨电）		
                    # 弱行业（木门/净水器）
                    hangye_type = tdata['hangye_type'] if tdata['hangye_type'] else '辅行业'
                    db_comment_count = tdata['comment_count']
                    keyword = tdata['keyword']
                    print('id:'+str(tid))
                    time.sleep(3)
                    if last_runtime:
                        last_runtime = last_runtime.timestamp()
                    else:
                        last_runtime = 0
                    #获取评论数据    
                    rs = getDataByUrl(tpage, turl, tid, last_runtime,keyword,hangye_type,db_comment_count)
                    if rs:
                        #更新最后处理时间
                        now = datetime.datetime.now()
                        nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                        r = db.update('craw_douyin_url', {'status': 1,'last_runtime':nowtime}, f"id={tid}")
                        if not r:
                            break
                    else:
                        #tpage.quit() 
                        break   
                    time.sleep(random.randint(3, 5))
                #tpage.quit()
            db.disconnect()
            i += 1
        except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
                time.sleep(10)
                pass