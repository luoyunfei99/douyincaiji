from DrissionPage import Chromium, ChromiumPage, ChromiumOptions
import time
import datetime
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

def getDataByUrl(page, url, pid = 0, last_runtime = '', keyword='', hangye_type='辅行业', db_comment_count=0):
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
    new_comment_count = 0
    phoneuserarr = []
    commentarr = []
    have_w = 0

    time_str = "2025-06-01 00:00:00"
    time_format = "%Y-%m-%d %H:%M:%S"
    # 将时间字符串转换为 datetime 对象
    dt_obj = datetime.datetime.strptime(time_str, time_format)
    # 将 datetime 对象转换为时间戳
    needtime = int(dt_obj.timestamp())

    for w in range(10):
        print(str(w)+'#######\n')
        if w > 1 and not new_comment_count:
            break
        if w - have_w > 3:
            break;
        try:
            res = tab.listen.wait(timeout=3)  # 等待并获取一个数据包
            if not isinstance(res, bool):
                have_w = w
                new_comment_count = res.response.body['total']
                if new_comment_count == db_comment_count:
                    print('暂无最新的评论信息')
                    break
                for i in res.response.body['comments']:
                    text = i['text']
                    # 过滤词
                    if not text or cfun.is_filter_keywords(text):
                        continue
                    create_time = i['create_time']
                    print(str(create_time)+'|'+str(needtime))
                    if create_time < needtime:
                        continue

                    dt_object = datetime.datetime.fromtimestamp(create_time)
                    create_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")

                    uid = i['user']['uid']  # id
                    unique_id = i['user']['unique_id']  # unique_id
                    short_id = i['user']['short_id']  # 短id
                    nickname = i['user']['nickname']  # 用户名
                    # signature = str(i['user']['signature'])  # 用户介绍
                    enterprise_verify_reason = i['user']['enterprise_verify_reason']
                    sec_uid = 'https://www.douyin.com/user/' + \
                        i['user']['sec_uid']+'?from_tab_name=main'  # 加密id
                    # follower_count = i['user']['follower_count']  # 粉丝量
                    # total_favorited = i['user']['total_favorited']  # 获赞
                    phone = cfun.extract_and_join_phone_numbers(
                        str(unique_id)+sec_uid)
                    # res_list.append([rz_str, keyword, uid,unique_id, short_id, nickname, signature, sec_uid, enterprise_verify_reason, follower_count, total_favorited,phone])
                    level = cfun.get_comment_level(text)
                    tdata = {
                        'pid': pid,
                        'uid': uid,
                        'unique_id': unique_id,
                        'short_id': short_id,
                        'nickname': nickname,
                        # 'signature': signature,
                        'sec_uid': sec_uid,
                        'enterprise_verify_reason': enterprise_verify_reason,
                        # 'follower_count': follower_count,
                        # 'total_favorited': total_favorited,
                        'phone': phone,
                        'text': text,
                        'create_time': create_time,
                        'level': level
                    }
                    print(tdata)
                    if pid and (not last_runtime or i['create_time'] > last_runtime):
                        count += 1
                        commentarr.append(tdata)
                        db.insert('craw_douyin_comment_user', tdata)
                        if phone:
                            phoneuserarr.append(
                                {'userurl': sec_uid, 'phone': phone, 'nickname': nickname, 'text': text, 'create_time': create_time})
                reply_comments = i['reply_comment']
                # 回复
                if reply_comments:
                    for i in reply_comments:
                        text = i['text']
                        label_type = int(
                            i['label_type'] if i['label_type'] else 0)
                        # 作者回复跳过
                        if label_type == 1:
                            continue
                        # 过滤词
                        if not text or cfun.is_filter_keywords(text):
                            continue
                        create_time = i['create_time']
                        dt_object = datetime.datetime.fromtimestamp(
                            create_time)
                        create_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")

                        uid = i['user']['uid']  # id
                        unique_id = i['user']['unique_id']  # unique_id
                        short_id = i['user']['short_id']  # 短id
                        nickname = i['user']['nickname']  # 用户名
                        # signature = str(i['user']['signature'])  # 用户介绍
                        enterprise_verify_reason = i['user']['enterprise_verify_reason']
                        sec_uid = 'https://www.douyin.com/user/' + \
                            i['user']['sec_uid']+'?from_tab_name=main'  # 加密id
                        # follower_count = i['user']['follower_count']  # 粉丝量
                        # total_favorited = i['user']['total_favorited']  # 获赞
                        phone = cfun.extract_and_join_phone_numbers(
                            str(unique_id)+sec_uid)
                        # res_list.append([rz_str, keyword, uid,unique_id, short_id, nickname, signature, sec_uid, enterprise_verify_reason, follower_count, total_favorited,phone])
                        level = cfun.get_comment_level(text)
                        tdata = {
                            'pid': pid,
                            'uid': uid,
                            'unique_id': unique_id,
                            'short_id': short_id,
                            'nickname': nickname,
                            # 'signature': signature,
                            'sec_uid': sec_uid,
                            'enterprise_verify_reason': enterprise_verify_reason,
                            # 'follower_count': follower_count,
                            # 'total_favorited': total_favorited,
                            'phone': phone,
                            'text': text,
                            'create_time': create_time,
                            'level': level
                        }
                        print(tdata)
                        if pid and ( not last_runtime or i['create_time'] > last_runtime):
                            count += 1
                            commentarr.append(tdata)
                            db.insert('craw_douyin_comment_user', tdata)
                            if phone:
                                phoneuserarr.append(
                                    {'userurl': sec_uid, 'phone': phone, 'nickname': nickname, 'text': text, 'create_time': create_time})

                # if count==0 and w==0:
                #     print('暂无最新的评论信息')
                #     break

            else:
                element = tab.ele('x://*[contains(text(), "你要观看的视频不存在")]')
                if element:
                    if pid:
                        db.update('craw_douyin_url', {'status': -1}, f"id={pid}")
                    print('你要观看的视频不存在')
                    return False
                    break

                element = tab.ele('x://*[contains(text(), "暂时没有更多评论")]')
                if element:
                    print('暂时没有更多评论')
                    break
                else:
                    continue
            time.sleep(3)
            e = tab.ele('x://*[@id="douyin-right-container"]/div[2]')
            #print(e)
            e.scroll.to_bottom()
            tab.scroll.to_bottom()  # 滚动到底部
            time.sleep(1)
        except KeyboardInterrupt:
            print("程序被用户中断，已停止更新操作")
            return
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_info = traceback.format_exc()
            print(f"发生异常: {exc_type.__name__}, 详细错误信息:\n{error_info}")
            pass
    try:
        if pid and new_comment_count:
            db.update('craw_douyin_url', {
                      'comment_count': new_comment_count}, f"id={pid}")
        if pid and count > 0:
            sorted_tdata = sorted(commentarr, key=lambda x: x['create_time'])
            tcontent = f'抖音视频链接：{url} 留言信息更新了\n\n'
            for i in sorted_tdata:
                content = tcontent + \
                    f'时间：{i["create_time"]}；评论文字：{i["text"]}，品牌：{keyword}；来源链接：{i["sec_uid"]}，评论内容分级：{hangye_type}-{i["level"]}级留言'
                # if i["phone"]:
                #     content += f'，手机号：{i["phone"]}\n'
                touser = cfun.getToUser(db, hangye_type)
                if touser:
                    cfun.send_youdu_message(21, touser, content)
                    tdata = {
                        'pid': pid,
                        'hangye_type': hangye_type,
                        'touser': touser,
                        'msg': content
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
def reset_runstatus(db):
    db.execute_update(
        f'update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "S" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -10 minute)')
    db.execute_update(
        f'update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "A" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -1 day)')
    db.execute_update(
        f'update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "B" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -7 day)')

if __name__ == '__main__':
    # 创建 ChromiumOptions 对象
    # co = ChromiumOptions()

    # 设置代理，这里以 HTTP 代理为例，你可以根据实际情况修改
    # proxy = 'http://60.188.79.113:20073'
    # co.set_argument('--no-sandbox')
    # co.set_proxy(proxy)

    # 创建 ChromiumPage 对象并传入设置好代理的选项
    # page = ChromiumPage(co)

    # 打开一个测试页面，这里使用 httpbin.org 来验证代理是否生效
    # page.get('https://httpbin.org/ip')

    # 打印页面 HTML 内容，查看返回的 IP 是否为代理 IP
    # print(page.html)
    # exit()

    # tpage = cfun.randPage(9112,r'D:\googledata\data2')
    # tpage.get('https://httpbin.org/ip')
    # exit()
    # print(page.html)
    # 3、账号名称：门窗盟小哥
    #   注册手机：19073185175
    #   秘密：mcxg1996
    i = 0
    # 慢速模式
    args = cfun.parse_arguments()
    is_slow = cfg_is_slow
    if args.url is not None:
        print("手动抓取")
        db = MySQLHandler(**mysql_config)
        db.connect()
        tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
        rs = getDataByUrl(tpage, args.url)
        db.disconnect

    else:
        while True:
            nowhour = datetime.datetime.now().hour
            if nowhour < 7 or nowhour >= 23:
                time.sleep(60)
                continue

            try:
                db = MySQLHandler(**mysql_config)
                db.connect()
                # 定期重置监听
                reset_runstatus(db)
                brandid = 0
                keyword = ''
                last_runtime = ''
                # 查询存在要处理数据
                # turlinfo = db.execute_query(
                    # f'select * from craw_douyin_url where type="实时监听" and status=1 and pid=0 and (next_runtime is null or next_runtime<=now()) and is_run = 0 order by last_runtime,field(level,"S","A","B","") limit 10')
                turlinfo = db.execute_query(
                    f'select * from craw_douyin_url where id = 44 and pid=0 order by pid,field(level,"S","A","B"),last_runtime limit 1')
                if not turlinfo:
                    if i == 0:
                        print('没有要操作的数据')
                    time.sleep(10)
                else:
                    tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
                    if not tpage:
                        time.sleep(10)
                        continue
                    ids = [row['id'] for row in turlinfo]
                    if ids:
                        # 将id列表转换为适合SQL的字符串格式
                        id_str = ','.join(map(str, ids))
                        # 执行SQL更新语句
                        db.execute_query(f'UPDATE craw_douyin_url SET is_run=1 WHERE id IN ({id_str})')    
                    for tdata in turlinfo:
                        if is_slow:
                            time.sleep(random.randint(10, 20))
                        turl = tdata['url']
                        tid = tdata['id']
                        # 最后执行时间
                        last_runtime = tdata['last_runtime']
                        # 提醒人
                        touser = tdata['touser']
                        level = tdata['level']
                        # 主行业（门窗/全屋定制/橱柜）
                        # 辅行业（卫浴/顶墙/地板/集成灶/厨电）
                        # 弱行业（木门/净水器）
                        hangye_type = tdata['hangye_type'] if tdata['hangye_type'] else '辅行业'
                        db_comment_count = tdata['comment_count']
                        keyword = tdata['keyword']
                        print(touser)
                        # exit
                        print('id:'+str(tid))
                        # time.sleep(3)
                        if last_runtime:
                            last_runtime = last_runtime.timestamp()
                        else:
                            last_runtime = 0
                        # 获取评论数据
                        rs = getDataByUrl(
                            tpage, turl, tid, last_runtime, keyword, hangye_type, db_comment_count)
                        # 更新最后处理时间
                        if rs:
                            now = datetime.datetime.now()
                            nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                            next_runtime = cfun.get_next_runtime(now,level,0)
                            db.update('craw_douyin_url', {
                                    'last_runtime': nowtime,'next_runtime':next_runtime,'is_run':0}, f"id={tid}")
                        time.sleep(random.randint(1, 3))
                        if not rs:
                            # tpage.quit()
                            break
                    tpage.quit()
                db.disconnect()
                i += 1
            except KeyboardInterrupt:
                if id_str is not None:
                    db.execute_query(f'UPDATE craw_douyin_url SET is_run=0 WHERE id IN ({id_str})')    
                print("程序被用户中断，已停止更新操作")
                exit()
            except:
                # if 'tpage' in globals():
                #     #tpage.quit()
                if id_str is not None:
                    db.execute_query(f'UPDATE craw_douyin_url SET is_run=0 WHERE id IN ({id_str})')    

                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
                time.sleep(10)
                pass
