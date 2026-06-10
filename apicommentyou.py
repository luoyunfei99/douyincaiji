import requests
import urllib.parse
import hashlib
import random
import time
import json
import sys
import re
import datetime
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from threading import Lock
from queue import Queue

from DrissionPage import Chromium, ChromiumPage, ChromiumOptions
import cfun
from my_sql import MySQLHandler
from config.mysql_config import mysql_config
from config.common_config import cfg_user_agent, cfg_is_slow, cfg_cookie

# ==============================================
# 全局配置（多线程+防风控）
# ==============================================
MAX_WORKERS = 3
TASK_QUEUE = Queue()
DB_LOCK = Lock()
BASE_URL = "https://www.douyin.com/aweme/v1/web/comment/list/"
USER_AGENT = cfg_user_agent
NAV_BATCH_SIZE = 5  # 每5个任务打开一次浏览器（和你原来一致）

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
    FIXED_PARAMS = cfun.update_params_from_url(test_url, FIXED_PARAMS)

# ==============================================
# 工具函数（含你原来的 navigate_to_url）
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

def build_url(aweme_id, cursor):
    params = FIXED_PARAMS.copy()
    params["aweme_id"] = aweme_id
    params["cursor"] = str(cursor)
    params["count"] = "5" if cursor == 0 else "10"
    sorted_params = sorted(params.items())
    qs = urllib.parse.urlencode(sorted_params, safe="=")
    a_bogus = generate_a_bogus(qs, USER_AGENT)
    return f"{BASE_URL}?{qs}&a_bogus={urllib.parse.quote(a_bogus)}"

def get_headers(video_id):
    return {
        "User-Agent": USER_AGENT,
        "Referer": f"https://www.douyin.com/video/{video_id}",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="132", "Not A Brand";v="99", "Google Chrome";v="132"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": cfg_cookie
    }

def fetch_comments(aweme_id, cursor):
    url = build_url(aweme_id, cursor)
    headers = get_headers(aweme_id)
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"[爬取失败] 视频ID:{aweme_id} 状态码:{resp.status_code}")
            return None
        data = resp.json()
        if data.get("status_code") != 0:
            print(f"[风控拦截] 视频ID:{aweme_id} 提示:{data.get('status_msg')}")
            return None
        return data
    except Exception as e:
        print(f"[请求异常] 视频ID:{aweme_id} 错误:{str(e)}")
        return None

def get_douyin_video_id(url):
    clean_url = urllib.parse.urlparse(url).path
    match = re.search(r'/video/(\d+)', clean_url)
    if match:
        return match.group(1)
    return None


# ==============================================
# 单视频爬取逻辑（线程执行单元）
# ==============================================
def crawl_single_video(task_data):
    db = None
    try:
        db = MySQLHandler(**mysql_config)
        db.connect()
        
        tid = task_data['tid']
        turl = task_data['turl']
        last_runtime = task_data['last_runtime']
        keyword = task_data['keyword']
        hangye_type = task_data['hangye_type'] or '辅行业'
        hangye = task_data['hangye']
        db_comment_count = task_data['db_comment_count']
        touser = task_data['touser']
        pid = (int)(task_data['pid'])
        is_private = task_data.get('is_private', 0)
        
        video_id = get_douyin_video_id(turl)
        if not video_id:
            print(f"[任务失败] ID:{tid} 链接{turl} 无法提取视频ID")
            with DB_LOCK:
                db.update('craw_douyin_url', {'is_run': 0}, f"id={tid}")
            return False
        
        cursor = 0
        page = 1
        count = 0
        new_comment_count = 0
        phoneuserarr = []
        uids = []
        all_comments = []
        
        time_str = "2026-04-01 00:00:00"
        time_format = "%Y-%m-%d %H:%M:%S"
        dt_obj = datetime.datetime.strptime(time_str, time_format)
        needtime = int(dt_obj.timestamp())
        
        if last_runtime:
            last_runtime = last_runtime.timestamp() if isinstance(last_runtime, datetime.datetime) else last_runtime
        else:
            last_runtime = 0
        
        while True:
            wait_time = random.uniform(1.0, 3.0) if page > 1 else random.uniform(1.5, 4.0)
            time.sleep(wait_time)
            
            data = fetch_comments(video_id, cursor)
            if not data:
                print(f"[任务中断] 视频ID:{video_id} 爬取失败/风控")
                break
            
            new_comment_count = data.get("total", 0)
            if new_comment_count == db_comment_count:
                print(f"[无新评论] 视频ID:{video_id}")
                break
            
            comments = data.get("comments", [])
            if not comments:
                print(f"[爬取完成] 视频ID:{video_id} 无更多评论")
                break
            
            # 解析主评论
            for c in comments:
                text = c.get("text")
                if not text or cfun.is_filter_keywords(text):
                    continue
                create_time = c.get("create_time")
                if create_time < needtime:
                    continue
                
                dt_object = datetime.datetime.fromtimestamp(create_time)
                t_create_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                
                user = c.get("user", {})
                uid = user.get("uid")
                unique_id = user.get("unique_id")
                short_id = user.get("short_id")
                nickname = user.get("nickname")
                sec_uid = user.get("sec_uid")
                secret = user.get("secret",0)
                enterprise_verify_reason = user.get("enterprise_verify_reason")
                sec_uid = f'https://www.douyin.com/user/{sec_uid}?from_tab_name=main' if sec_uid else ''
                phone = cfun.extract_and_join_phone_numbers(f"{unique_id}{sec_uid}")
                level = cfun.get_comment_level(text)
                
                tdata = {
                    'pid': tid,
                    'uid': uid,
                    'unique_id': unique_id,
                    'short_id': short_id,
                    'nickname': nickname,
                    'sec_uid': sec_uid,
                    'enterprise_verify_reason': enterprise_verify_reason,
                    'phone': phone,
                    'text': text,
                    'create_time': t_create_time,
                    'level': level,
                }
                print(tdata)
                if tid and (not last_runtime or create_time > last_runtime) and (not secret or phone):
                    touser = cfun.getToUser(db, hangye_type,touser,is_private)
                    tdata['touser'] = touser
                    if uid not in uids:
                        uids.append(uid)
                        all_comments.append(tdata)
                        with DB_LOCK:
                            db.insert('craw_douyin_comment_user', tdata)
                        if phone:
                            phoneuserarr.append({
                                'userurl': sec_uid, 'phone': phone, 
                                'nickname': nickname, 'text': text, 
                                'create_time': create_time
                            })
                        count += 1
            is_get_reply_comments = 1
            # 解析回复评论
            if is_get_reply_comments:
                for c in comments:
                    reply_comments = c.get("reply_comment", [])
                    if not reply_comments:
                        continue
                    for i in reply_comments:
                        text = i.get('text')
                        label_type = int(i.get('label_type', 0))
                        if label_type == 1 or not text or cfun.is_filter_keywords(text):
                            continue
                        
                        create_time = i.get('create_time')
                        if create_time < needtime:
                            continue
                        
                        dt_object = datetime.datetime.fromtimestamp(create_time)
                        create_time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                        
                        user = i.get('user', {})
                        uid = user.get("uid")
                        unique_id = user.get("unique_id")
                        short_id = user.get("short_id")
                        nickname = user.get("nickname")
                        sec_uid = user.get("sec_uid")
                        secret = user.get("secret",0)
                        enterprise_verify_reason = user.get("enterprise_verify_reason")
                        sec_uid = f'https://www.douyin.com/user/{sec_uid}?from_tab_name=main' if sec_uid else ''
                        phone = cfun.extract_and_join_phone_numbers(f"{unique_id}{sec_uid}")
                        level = cfun.get_comment_level(text)
                        tdata = {
                            'pid': tid,
                            'uid': uid,
                            'unique_id': unique_id,
                            'short_id': short_id,
                            'nickname': nickname,
                            'sec_uid': sec_uid,
                            'enterprise_verify_reason': enterprise_verify_reason,
                            'phone': phone,
                            'text': text,
                            'create_time': create_time_str,
                            'level': level,
                        }
                        print(tdata)
                        if tid and (not last_runtime or create_time > last_runtime) and (not secret or phone):
                            touser = cfun.getToUser(db, hangye_type,touser,is_private)
                            tdata['touser'] = touser
                            if uid not in uids:
                                uids.append(uid)
                                all_comments.append(tdata)
                                with DB_LOCK:
                                    db.insert('craw_douyin_comment_user', tdata)
                                if phone:
                                    phoneuserarr.append({
                                        'userurl': sec_uid, 'phone': phone, 
                                        'nickname': nickname, 'text': text, 
                                        'create_time': create_time_str
                                    })
                                count += 1
            print(f"本页获取 {len(comments)} 条，累计：{len(all_comments)}")
            
            
            has_more = data.get("has_more", 0)
            next_cursor = data.get("cursor", cursor + (5 if cursor == 0 else 10))
            if not has_more:
                break
            
            cursor = next_cursor
            page += 1
            
            if page % 10 == 0:
                rest_time = random.uniform(1, 3)
                print(f"[防封休息] 视频ID:{video_id} 第{page}页，休息{rest_time:.1f}秒")
                time.sleep(rest_time)
        
        # 更新视频评论总数
        if tid and new_comment_count:
            with DB_LOCK:
                db.update('craw_douyin_url', {'comment_count': new_comment_count}, f"id={tid}")
        # 发送消息
        if tid and count > 0:
            url = f'https://www.douyin.com/video/{video_id}'
            sorted_tdata = sorted(all_comments, key=lambda x: x['create_time'])
            tcontent = f'抖音视频链接：{url} 留言信息更新了\n\n'
            for item in sorted_tdata:
                content = tcontent + f'时间：{item["create_time"]}；昵称：{item["nickname"]}；评论文字：{item["text"]}，品牌：{keyword}；来源链接：{item["sec_uid"]}，评论内容分级：{hangye_type}-{item["level"]}级留言'
                if item["phone"]:
                    content += f'，手机号：{item["phone"]}\n'
                touser = item.get('touser')
                if is_private and item["phone"]:
                    baoming_data = {
                        'phone': item["phone"],
                        'nickname': item["nickname"],
                        'douyin_url': item["sec_uid"],
                        'douyin_inputtime': item["create_time"],
                        'hangye': hangye,
                        'content': item["text"],
                        'cometype': '博主' if pid>0 else '品牌/厂家' 
                    }
                    cfun.baoming(baoming_data,touser)


                if not touser:
                    touser = cfun.getToUser(db, hangye_type,touser,is_private)
                if touser:
                    cfun.send_youdu_message(21, touser, content)
                    with DB_LOCK:
                        db.insert('craw_douyin_comment_touser', {
                            'pid': tid,
                            'hangye_type': hangye_type,
                            'touser': touser,
                            'msg': content
                        })
        # 更新任务状态
        now = datetime.datetime.now()
        nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
        tmp_type = 2 if pid>0 else 0
        next_runtime = cfun.get_next_runtime(now, task_data.get('level', ''), tmp_type)
        with DB_LOCK:
            db.update('craw_douyin_url', {
                'last_runtime': nowtime,
                'next_runtime': next_runtime,
                'is_run': 0
            }, f"id={tid}")
        
        print(f"[任务完成] 视频ID:{video_id} 累计爬取{len(all_comments)}条有效评论")
        return True
    
    except Exception as e:
        print(f"[线程异常] 任务ID:{task_data.get('tid')} 错误:{str(e)}")
        if db and task_data.get('tid'):
            with DB_LOCK:
                db.update('craw_douyin_url', {'is_run': 0}, f"id={task_data.get('tid')}")
        return False
    finally:
        if db:
            db.disconnect()

# ==============================================
# 任务管理器（含每N个任务自动navigate_to_url）
# ==============================================
def reset_runstatus(db):
    with DB_LOCK:
        db.execute_update('update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "S" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -10 minute)')
        db.execute_update('update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "A" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -1 day)')
        db.execute_update('update craw_douyin_url set is_run=0 where is_run=1 and type="实时监听" and pid=0 and level = "B" and status=1 and ifnull(last_runtime,updatetime)<date_add(now(),INTERVAL -7 day)')

def produce_tasks():
    db = None
    try:
        db = MySQLHandler(**mysql_config)
        db.connect()
        reset_runstatus(db)
        
        sql = f'''
            select * from craw_douyin_url 
            where type="实时监听" and status=1 and (pid=0 or date_add(create_time,interval 5 day)>now()) 
            and (next_runtime is null or next_runtime<=now()) and is_run = 0 
            order by last_runtime,field(level,"S","A","B","") 
            limit {MAX_WORKERS * 2}
        '''
        turlinfo = db.execute_query(sql)
        if not turlinfo:
            return []
        
        ids = [row['id'] for row in turlinfo]
        if ids:
            id_str = ','.join(map(str, ids))
            with DB_LOCK:
                db.execute_update(f'UPDATE craw_douyin_url SET is_run=1 WHERE id IN ({id_str})')
        
        tasks = []
        for tdata in turlinfo:
            task = {
                'tid': tdata['id'],
                'turl': tdata['url'],
                'last_runtime': tdata['last_runtime'],
                'keyword': tdata['keyword'],
                'hangye_type': tdata.get('hangye_type'),
                'db_comment_count': tdata['comment_count'],
                'level': tdata.get('level', ''),
                'touser': tdata.get('touser'),
                'pid':tdata.get('pid'),
                'hangye':tdata.get('hangye'),
                'is_private':tdata.get('is_private')
            }
            tasks.append(task)
        
        return tasks
    except Exception as e:
        print(f"[任务生产异常] {str(e)}")
        return []
    finally:
        if db:
            db.disconnect()

# ==============================================
# 主程序（恢复你原来的每N个任务自动navigate_to_url）
# ==============================================
def main():
    args = cfun.parse_arguments()
    if args.url is not None:
        print("=== 手动抓取模式 ===")
        video_id = get_douyin_video_id(args.url)
        if not video_id:
            print("无效的抖音链接")
            return
        task_data = {
            'tid': 0,
            'turl': args.url,
            'last_runtime': 0,
            'keyword': '',
            'hangye_type': '辅行业',
            'db_comment_count': 0,
            'level': '',
            'pid':0,
            'hangye':'',
            'is_private':0
        }
        crawl_single_video(task_data)
        return
    
    print("=== 多线程自动监听模式 ===")
    print(f"最大并发数：{MAX_WORKERS}")
    print(f"每{NAV_BATCH_SIZE}个任务自动浏览器访问（防风控）")
    
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    task_counter = 0  # 计数，每NAV_BATCH_SIZE触发navigate
    
    try:
        while True:
            nowhour = datetime.datetime.now().hour
            if nowhour < 7 or nowhour >= 23:
                print(f"非工作时间（当前{nowhour}点），休息60秒...")
                time.sleep(60)
                continue
            
            tasks = produce_tasks()
            if not tasks:
                print("暂无待处理任务，休息10秒...")
                time.sleep(10)
                continue
            
            futures = []
            for task in tasks:
                if cfg_is_slow:
                    time.sleep(random.uniform(2, 5))
                
                # 每NAV_BATCH_SIZE个任务，调用navigate_to_url（你原来的逻辑）
                task_counter += 1
                if task_counter % NAV_BATCH_SIZE == 0:
                    print(f"\n⏸ 每{NAV_BATCH_SIZE}个任务，自动浏览器访问：{task['turl']}")
                    try:
                        cfun.navigate_to_url(task['turl'],True,True)
                        time.sleep(3)
                    except Exception as e:
                        pass   
                
                future = executor.submit(crawl_single_video, task)
                futures.append(future)
            
            wait(futures, return_when=ALL_COMPLETED)
            
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"[任务结果异常] {str(e)}")
            
            time.sleep(random.uniform(3, 8))
    
    except KeyboardInterrupt:
        print("\n用户中断程序，关闭线程池...")
        executor.shutdown(wait=True)
        db = MySQLHandler(**mysql_config)
        db.connect()
        db.execute_update('UPDATE craw_douyin_url SET is_run=0 WHERE is_run=1')
        db.disconnect()
        sys.exit(0)
    except Exception as e:
        print(f"[主程序异常] {str(e)}")
        executor.shutdown(wait=True)
        db = MySQLHandler(**mysql_config)
        db.connect()
        db.execute_update('UPDATE craw_douyin_url SET is_run=0 WHERE is_run=1')
        db.disconnect()
        sys.exit(0)


if __name__ == "__main__":
    main()