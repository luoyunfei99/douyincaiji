import requests
import re
import json
import time
import random
from urllib.parse import urlparse
import warnings
warnings.filterwarnings("ignore")

from my_sql import MySQLHandler
import sys
import cfun
from config.mysql_config import mysql_config
from config.common_config import cfg_user_agent, cfg_is_slow, cfg_cookie
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue

# ===================== 核心配置 =====================
COOKIE = cfg_cookie
UA = cfg_user_agent

MAX_WORKERS = 2
TASK_QUEUE = Queue(maxsize=10)
DB_LOCK = threading.Lock()
EXIT_FLAG = threading.Event()

MIN_DELAY = 1.5
MAX_DELAY = 3.0
BATCH_PAUSE = 10
BATCH_SIZE = 10
NAV_BATCH_SIZE = 30

GLOBAL_REQUEST_COUNT = 0
COUNT_LOCK = threading.Lock()

# 全局数据库连接
GLOBAL_DB = None

# ===================== 数据库单例连接 =====================
def get_db():
    global GLOBAL_DB
    try:
        if GLOBAL_DB is None:
            GLOBAL_DB = MySQLHandler(**mysql_config)
            GLOBAL_DB.connect()
        return GLOBAL_DB
    except:
        GLOBAL_DB = None
        time.sleep(1)
        GLOBAL_DB = MySQLHandler(**mysql_config)
        GLOBAL_DB.connect()
        return GLOBAL_DB

# ===================== 工具函数 =====================
def extract_sec_uid(url):
    path = urlparse(url).path
    match = re.search(r"/user/([A-Za-z0-9_-]+)", path)
    return match.group(1) if match else None

def smooth_sleep():
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)

def _check_keywords(content):
    keywords = ["加盟", "上样", "哪里", "联系", "电话", "手机"]
    for kw in keywords:
        if kw in str(content):
            return True
    return False

# ===================== 请求接口（防风控） =====================
def get_user_info(sec_uid, userurl):
    global GLOBAL_REQUEST_COUNT

    with COUNT_LOCK:
        GLOBAL_REQUEST_COUNT += 1
        if GLOBAL_REQUEST_COUNT % NAV_BATCH_SIZE == 0:
            print(f"\n🌍 防风控导航 → {userurl}")
            try:
                cfun.navigate_to_url(userurl, True, True)
            except:
                pass
            time.sleep(3)

        if GLOBAL_REQUEST_COUNT % BATCH_SIZE == 0:
            print(f"\n⏳ 批次休息 {BATCH_PAUSE}s")
            time.sleep(BATCH_PAUSE)

    url = "https://www.douyin.com/aweme/v1/web/user/profile/other/"
    params = {
        "sec_user_id": sec_uid,
        "aid": 6383,
        "device_platform": "webapp",
        "channel": "channel_pc_web",
        "version_code": 170400,
        "platform": "PC",
    }
    headers = {
        "User-Agent": UA,
        "Cookie": COOKIE.strip(),
        "Referer": "https://www.douyin.com/",
        "Accept": "application/json, text/plain, */*",
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=12, verify=False)
        smooth_sleep()
        return resp.json() if resp.status_code == 200 else {"status_code": -1}
    except:
        smooth_sleep()
        return {"status_code": -1}

# ===================== 处理任务 =====================
def process_user_task(task):
    tid = task["id"]
    userurl = task["sec_uid"]
    touser = task.get("touser")
    pid = task.get("pid", 0)
    name = task.get("name")
    liveid = task.get("liveid")
    type = task.get("type")
    issend = task.get("issend", 0)
    liveurl = f"https://live.douyin.com/{liveid}"

    if EXIT_FLAG.is_set():
        return

    try:
        sec_uid = extract_sec_uid(userurl)
        if not sec_uid:
            with DB_LOCK:
                db = get_db()
                db.update("craw_douyin_live_user", {"status": -1}, f"id={tid}")
            return

        data = None
        for _ in range(3):
            data = get_user_info(sec_uid, userurl)
            if data.get("status_code") == 0:
                break
            time.sleep(random.uniform(2, 4))

        if not data or data.get("status_code") != 0:
            with DB_LOCK:
                db = get_db()
                db.update("craw_douyin_live_user", {"status": -2}, f"id={tid}")
            return

        user = data["user"]
        nickname = user.get("nickname", "")
        unique_id = user.get("unique_id", "")
        signature = cfun.replace_special_chars(user.get("signature", ""))
        phone = cfun.extract_and_join_phone_numbers(str(unique_id) + signature)
        avatar = user["avatar_larger"]["url_list"][0] if user.get("avatar_larger") else ""
        cover = user["cover_url"][0]["url_list"][0].replace("\u0026", "&") if user.get("cover_url") else ""
        address = f"{user.get('province','')}{user.get('city','')}"
        if "ip_location" in user:
            address += "|" + user["ip_location"]

        with DB_LOCK:
            db = get_db()
            db.update("craw_douyin_live_user", {
                "nickname": nickname,
                "unique_id": unique_id,
                "signature": signature,
                "phone": phone,
                "avatar": avatar,
                "cover": cover,
                "address": address,
                "status": 1
            }, f"id={tid}")

            text = task.get("text", "")
            if not issend and(phone or _check_keywords(text)):
                if not touser:
                    touser = cfun.getToUser(db, "直播")
                content = f"抖音直播间【{name}】：{liveurl}\n时间：{task.get('create_time')}\n昵称：{nickname}\n类型：{text}\n手机号：{phone}\n主页：{userurl}"
                touser = "骆云飞"
                if touser:
                    cfun.send_youdu_message(21, touser, content)
                    db.insert("craw_douyin_comment_touser", {
                        "pid": pid,
                        "hangye_type": "直播",
                        "touser": touser,
                        "msg": content
                    })
                    db.update("craw_douyin_live_user", {
                        "issend": 1
                    }, f"id={tid}")

        print(f"✅ 完成：{nickname} | 队列剩余：{TASK_QUEUE.qsize()}")

    except Exception as e:
        print(f"❌ 处理失败 ID={tid}: {str(e)[:40]}")
        with DB_LOCK:
            db = get_db()
            db.update("craw_douyin_live_user", {"status": -3}, f"id={tid}")

# ===================== 生产者（无限循环、不退出） =====================
def task_producer():
    while not EXIT_FLAG.is_set():
        try:
            # 队列满了就等待
            if TASK_QUEUE.full():
                print("⌛ 队列已满，等待消费...")
                for _ in range(5):
                    if EXIT_FLAG.is_set():
                        return
                    time.sleep(1)
                continue

            # 加锁查询未处理任务
            with DB_LOCK:
                db = get_db()
                db.execute_query("""
                    UPDATE craw_douyin_live_user 
                    SET status=9 
                    WHERE id IN (
                        SELECT id FROM (
                            SELECT id FROM craw_douyin_live_user 
                            WHERE status=0 
                            ORDER BY id ASC 
                            LIMIT 10
                        ) AS temp
                    )
                """)

                tasks = db.execute_query("""
                    SELECT a.*, b.touser, b.id AS pid, b.name 
                    FROM craw_douyin_live_user a 
                    LEFT JOIN craw_lives b ON a.liveid = b.liveid 
                    WHERE a.status=9 
                    ORDER BY a.id ASC
                """)

            # 没有任务 → 等待5秒继续查（不退出）
            if not tasks:
                print("📭 暂无新任务，5秒后自动重试...")
                for _ in range(5):
                    if EXIT_FLAG.is_set():
                        return
                    time.sleep(1)
                continue

            # 加入队列
            added = 0
            for t in tasks:
                if EXIT_FLAG.is_set() or TASK_QUEUE.full():
                    break
                TASK_QUEUE.put(t, block=True, timeout=1)
                added += 1

            print(f"📥 加载任务：{added} 个 | 队列长度：{TASK_QUEUE.qsize()}")

        except Exception as e:
            print(f"🚨 生产者异常：{e}")
            time.sleep(3)

# ===================== 消费者 =====================
def task_consumer():
    while not EXIT_FLAG.is_set():
        try:
            task = TASK_QUEUE.get(timeout=2)
            if EXIT_FLAG.is_set():
                TASK_QUEUE.task_done()
                return
            process_user_task(task)
            TASK_QUEUE.task_done()
        except Queue.Empty:
            continue

# ===================== 退出 =====================
def graceful_exit(executor=None):
    print("\n🔌 正在退出...")
    EXIT_FLAG.set()
    if executor:
        executor.shutdown(wait=False, cancel_futures=True)
    print("✅ 已安全退出")
    sys.exit(0)

# ===================== 手动模式 =====================
def manual_crawl(url):
    task = {
        "id": 0, "sec_uid": url, "text": "", "create_time": "",
        "touser": "", "pid": 0, "name": "", "liveid": "","type":""
    }
    process_user_task(task)

# ===================== 主程序（永久运行） =====================
if __name__ == "__main__":
    args = cfun.parse_arguments()
    executor = None

    if args.url is not None:
        print("🔧 手动抓取模式")
        manual_crawl(args.url)
    else:
        try:
            print(f"🚀 启动成功 | 并发：{MAX_WORKERS} | 永久监听模式")
            producer_thread = threading.Thread(target=task_producer, daemon=True)
            producer_thread.start()

            executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
            for _ in range(MAX_WORKERS):
                executor.submit(task_consumer)

            # 永久运行，不退出
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            graceful_exit(executor)
        except Exception as e:
            print(f"主程序异常：{e}")
            graceful_exit(executor)