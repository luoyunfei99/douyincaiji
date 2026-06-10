import requests
import urllib.parse
import hashlib
import random
import time
import json

from DrissionPage import Chromium, ChromiumPage, ChromiumOptions
import time
import datetime
import re
from my_sql import MySQLHandler
import random
import sys
import cfun
from config.mysql_config import mysql_config
from config.common_config import cfg_user_agent,cfg_is_slow,cfg_cookie


# ==============================================
# 固定配置（直接使用你提供的参数）
# ==============================================
# VIDEO_ID = "7453393028636560690"  # 你的视频ID
BASE_URL = "https://www.douyin.com/aweme/v1/web/comment/list/"

# 你浏览器的真实 UA（必须和你抓包时一致）
USER_AGENT = cfg_user_agent

# 固定请求参数
FIXED_PARAMS = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "item_type": "0",
    "whale_cut_token": "",
    "cut_version": "1",
    "rcFT": "",
    "update_version_code": "170400",
    "pc_client_type": "1",
    "pc_libra_divert": "Windows",
    "support_h265": "1",
    "support_dash": "1",
    "cpu_core_num": "4",
    "version_code": "170400",
    "version_name": "17.4.0",
    "cookie_enabled": "true",
    "screen_width": "1920",
    "screen_height": "1200",
    "browser_language": "zh-CN",
    "browser_platform": "Win32",
    "browser_name": "Chrome",
    "browser_version": "132.0.0.0",
    "browser_online": "true",
    "engine_name": "Blink",
    "engine_version": "132.0.0.0",
    "os_name": "Windows",
    "os_version": "10",
    "device_memory": "8",
    "platform": "PC",
    "downlink": "10",
    "effective_type": "4g",
    "round_trip_time": "50",
    "webid": "7627387120927999507",
    "uifid": "5a0fbbb49c6c57acd77ca86d66dd2e8e2f1fcf7b3fa6b8a56e480f684bd0858931441a18914e9b09abeb9b2fda1d98e94e3c72a8542ecdf2cd4c5dcc272e03ebfd18c80a8782ab73d3c42af5478ad6d6e163b0afc763ae93116ab5b4e983270a57b22e408b8dbcd344ef79468296b824b2f0310f74dca4c183ed6b51c4ae50534c8150d7217a021f35bc2b640ee886a91441906b7042c1537957f906ed8c3e37",
    "msToken": "G5QRQ_A-KhABrJ4Sf55CwlJ7tUprR5offE86FV5WN780QDY5n72N3JdcO4feU-u8ENxc6E3sGgZ3rnXZlEZLuOiX3PxMKhFyTpRpYWNM7zBc-eEmUcxBzV99y9uDSYZOCy-XMyLzAyfJs1PF8iab7le67TDHRmrzW8nefClZDc_EezdbmRkprQ==",
    "verifyFp": "verify_mntyqetf_KUN4BO46_No8T_4omQ_ArTl_NxDK43TnNmS7",
    "fp": "verify_mntyqetf_KUN4BO46_No8T_4omQ_ArTl_NxDK43TnNmS7"
}

test_url = ""
if test_url:
    # 调用方法
    FIXED_PARAMS = cfun.update_params_from_url(test_url, FIXED_PARAMS)
# ==============================================
# a_bogus 签名生成算法（抖音网页版最新）
# ==============================================
def generate_a_bogus(query: str, ua: str):
    s1 = "abcdefghijklmnopqrstuvwxyz0123456789"
    s2 = "Dkfd129fAxCE03Fn7dRbVGHspqLJZuYTIWeNcXjvBOSrmthgKloyQ"
    data = query + ua
    md5 = hashlib.md5(data.encode()).digest()
    xor_val = 0x83
    res = []
    for b in md5:
        res.append(b ^ xor_val)
    final = []
    for num in res:
        idx1 = (num >> 4) & 0x0F
        idx2 = num & 0x0F
        final.append(s2[idx1])
        final.append(s2[idx2])
    rand_char = random.choice(s1)
    return "".join(final) + rand_char

# ==============================================
# 构造带签名的 URL
# ==============================================
def build_url(aweme_id, cursor):
    params = FIXED_PARAMS.copy()
    params["aweme_id"] = aweme_id
    params["cursor"] = str(cursor)
    params["count"] = "5" if cursor == 0 else "10"
    sorted_params = sorted(params.items())
    qs = urllib.parse.urlencode(sorted_params, safe="=")
    a_bogus = generate_a_bogus(qs, USER_AGENT)
    return f"{BASE_URL}?{qs}&a_bogus={urllib.parse.quote(a_bogus)}"

# ==============================================
# 请求头（防封）
# ==============================================
def get_headers():
    return {
        "User-Agent": USER_AGENT,
        "Referer": f"https://www.douyin.com/video/{VIDEO_ID}",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="132", "Not A Brand";v="99", "Google Chrome";v="132"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie":cfg_cookie
    }

# ==============================================
# 爬取一页评论
# ==============================================
def fetch_comments(aweme_id, cursor):
    url = build_url(aweme_id, cursor)
    headers = get_headers()

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"请求失败 {resp.status_code}")
            return None

        data = resp.json()
        if data.get("status_code") != 0:
            print("风控/无权限：", data.get("status_msg"))
            return None

        return data

    except Exception as e:
        print("请求异常：", e)
        return None

# ==============================================
# 自动翻页爬取全部评论（带防封）
# ==============================================
def crawl_all_comments(aweme_id,pid =0, last_runtime = '',keyword='',hangye_type='辅行业', db_comment_count=0):
    
    cursor = 0
    page = 1

    count = 0
    new_comment_count = 0
    phoneuserarr = []

    time_str = "2026-04-01 00:00:00"
    time_format = "%Y-%m-%d %H:%M:%S"
    # 将时间字符串转换为 datetime 对象
    dt_obj = datetime.datetime.strptime(time_str, time_format)
    # 将 datetime 对象转换为时间戳
    needtime = int(dt_obj.timestamp())
    uids = []
    while True:
        all_comments = []
        print(f"\n正在爬取第 {page} 页，cursor = {cursor}")

        # 防封：随机延时 1.5~4 秒
        wait = random.uniform(1.5, 4.0)
        time.sleep(wait)

        data = fetch_comments(aweme_id, cursor)
        if not data:
            print("结束或被风控，停止爬取")
            break
        new_comment_count = data.get("total", 0)
        if new_comment_count == db_comment_count:
            print('暂无最新的评论信息')
            break
        comments = data.get("comments", [])
        if not comments:
            print("无更多评论")
            break
        
        # 提取评论内容
        for c in comments:
            text = c.get("text")
            if not text or cfun.is_filter_keywords(text):
                continue
            create_time = c.get("create_time")
            print(str(create_time)+'|'+str(needtime))
            if create_time < needtime:
                continue
            dt_object = datetime.datetime.fromtimestamp(create_time)
            t_create_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")

            uid = c.get("user", {}).get("uid")  # id

            unique_id = c.get("user", {}).get("unique_id")  # unique_id
            short_id = c.get("user", {}).get("short_id")  # 短id
            nickname = c.get("user", {}).get("nickname")  # 用户名
            sec_uid = c.get("user", {}).get("sec_uid")
            enterprise_verify_reason = c.get("user", {}).get("enterprise_verify_reason")
            sec_uid = 'https://www.douyin.com/user/' + \
                sec_uid+'?from_tab_name=main'  # 加密id
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
                'create_time': t_create_time,
                'level': level
            }
            print(tdata)
            
            if pid and (not last_runtime or create_time > last_runtime):
                count += 1
                if uid not in uids:
                    uids.append(uid)  # 不存在则追加
                    print(uids)
                    all_comments.append(tdata)
                    db.insert('craw_douyin_comment_user', tdata)
                    if phone:
                        phoneuserarr.append(
                            {'userurl': sec_uid, 'phone': phone, 'nickname': nickname, 'text': text, 'create_time': create_time})
                else:
                    continue
                


            reply_comments = c.get("reply_comment", [])
            
            # 回复
            if reply_comments:
                print('reply_comments:')
                print(reply_comments)
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
                    if create_time < needtime:
                        continue
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
                        if uid not in uids:
                            uids.append(uid)  # 不存在则追加
                            all_comments.append(tdata)
                            print(uids)
                            db.insert('craw_douyin_comment_user', tdata)
                            if phone:
                                phoneuserarr.append(
                                    {'userurl': sec_uid, 'phone': phone, 'nickname': nickname, 'text': text, 'create_time': create_time})

                        else:
                            continue
                        


        print(f"本页获取 {len(comments)} 条，累计：{len(all_comments)}")


        try:
            print(all_comments);
            if pid and new_comment_count:
                db.update('craw_douyin_url', {
                        'comment_count': new_comment_count}, f"id={pid}")
            if pid and count > 0:
                url = f'https://www.douyin.com/video/{aweme_id}'
                sorted_tdata = sorted(all_comments, key=lambda x: x['create_time'])
                print(sorted_tdata)
                tcontent = f'抖音视频链接：{url} 留言信息更新了\n\n'
                for i in sorted_tdata:
                    content = tcontent + \
                        f'时间：{i["create_time"]}；昵称：{i["nickname"]}；评论文字：{i["text"]}，品牌：{keyword}；来源链接：{i["sec_uid"]}，评论内容分级：{hangye_type}-{i["level"]}级留言'
                    if i["phone"]:
                        content += f'，手机号：{i["phone"]}\n'
                    touser = cfun.getToUser(db, hangye_type)
                    # touser = '骆云飞'
                    if touser:
                        cfun.send_youdu_message(21, touser, content)
                        tdata = {
                            'pid': pid,
                            'hangye_type': hangye_type,
                            'touser': touser,
                            'msg': content
                        }
                        db.insert('craw_douyin_comment_touser', tdata)
        except:
            pass

        # 是否还有下一页
        has_more = data.get("has_more", 0)
        next_cursor = data.get("cursor", cursor + (5 if cursor == 0 else 10))

        if not has_more:
            print("全部评论爬取完成！")
            break

        cursor = next_cursor
        page += 1

        # 超级防封：每爬 10 页多停一会儿
        if page % 10 == 0:
            print("\n每10页休息 1~3 秒...")
            time.sleep(random.uniform(1, 3))

    return True

# ==============================================
# 保存结果
# ==============================================
def save_to_file(comments):
    filename = f"抖音评论_{VIDEO_ID}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    print(f"\n已保存到：{filename}，共 {len(comments)} 条评论")

def get_douyin_video_id(url):
    """
    从抖音视频链接中提取视频ID
    支持：
    https://www.douyin.com/video/7483314320152022322
    https://www.douyin.com/video/7483314320152022322?xxx=yyy
    """
    # 先去掉 ? 后面的参数
    clean_url = urllib.parse.urlparse(url).path
    
    # 正则提取数字ID
    match = re.search(r'/video/(\d+)', clean_url)
    if match:
        return match.group(1)
    return None
#重置数据状态
def reset_runstatus(db):
    db.execute_update(
        f'update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "S" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -10 minute)')
    db.execute_update(
        f'update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "A" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -1 day)')
    db.execute_update(
        f'update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "B" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -7 day)')

# ==============================================
# 主程序
# ==============================================
if __name__ == "__main__":
    # print("开始爬取抖音视频评论，视频ID：", VIDEO_ID)
    # comments = crawl_all_comments(VIDEO_ID)
    # save_to_file(comments)
    # 慢速模式
    NAV_BATCH_SIZE = 5
    args = cfun.parse_arguments()
    is_slow = cfg_is_slow
    i = 0
    if args.url is not None:
        print("手动抓取")
        db = MySQLHandler(**mysql_config)
        db.connect()
        # tpage = cfun.getGoolePage(args.port,args.datapath,args.useproxy)
        VIDEO_ID = get_douyin_video_id(args.url)
        rs = crawl_all_comments(VIDEO_ID)
        db.disconnect

    else:
        RUN = True
        while RUN: 
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
                #     f'select * from craw_douyin_url where id=6')
                turlinfo = db.execute_query(
                    f'select * from craw_douyin_url where type="实时监听" and status=1 and pid=0 and (next_runtime is null or next_runtime<=now()) and is_run = 0 order by last_runtime,field(level,"S","A","B","") limit 1')
                if not turlinfo:
                    if i == 0:
                        print('没有要操作的数据')
                    time.sleep(10)
                    i += 1  
                else:
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
                         # 每 N 个强制打开浏览器，避免高频触发风控
                        if i % NAV_BATCH_SIZE == 0:
                            print(f"\n⏸ 每{NAV_BATCH_SIZE}个休息3秒...")
                            RUN = cfun.navigate_to_url(turl)
                            time.sleep(3)
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
                        VIDEO_ID = get_douyin_video_id(turl)
                        rs = crawl_all_comments(VIDEO_ID,tid, last_runtime, keyword, hangye_type, db_comment_count)
                        # getDataByUrl(
                            # tpage, turl, tid, last_runtime, keyword, hangye_type, db_comment_count)
                        # 更新最后处理时间
                        if rs:
                            now = datetime.datetime.now()
                            nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
                            next_runtime = cfun.get_next_runtime(now,level,0)
                            db.update('craw_douyin_url', {
                                    'last_runtime': nowtime,'next_runtime':next_runtime,'is_run':0}, f"id={tid}")
                        time.sleep(random.randint(1, 3))
                        if not rs:
                            break
                        i += 1
                db.disconnect()
                
            except KeyboardInterrupt:
                if id_str is not None:
                    db.execute_query(f'UPDATE craw_douyin_url SET is_run=0 WHERE id IN ({id_str})')    
                print("程序被用户中断，已停止更新操作")
                exit()
            except:
                if id_str is not None:
                    db.execute_query(f'UPDATE craw_douyin_url SET is_run=0 WHERE id IN ({id_str})')    

                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
                time.sleep(10)
                pass