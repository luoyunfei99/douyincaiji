import requests
import re
import json
import time
import random
from urllib.parse import urlparse
import warnings
warnings.filterwarnings("ignore")

from my_sql import MySQLHandler
import random
import sys
import cfun
from config.mysql_config import mysql_config
from config.common_config import cfg_user_agent,cfg_is_slow,cfg_cookie
import datetime

# 【必须填写】浏览器里复制的抖音 Cookie（必须包含 ttwid）
# COOKIE = "enter_pc_once=1; UIFID_TEMP=5a0fbbb49c6c57acd77ca86d66dd2e8e2f1fcf7b3fa6b8a56e480f684bd0858960f7fd30186218b604f1aa03a80d6bcf30f99252e4728b84d4493ddf33e6e2f542ef3f0384c522a3bbf7c4cdf5de4454; hevc_supported=true; fpk1=U2FsdGVkX19BuSu3u6Zk7U4o4ouVXJrYLgPXwX4lIxPDnmtO5Vcv6/lvNgBY1GM1mLa2dWEw+O/PfQDXEZufGg==; fpk2=41770e408d453f0e18b6cf535e220c84; UIFID=5a0fbbb49c6c57acd77ca86d66dd2e8e2f1fcf7b3fa6b8a56e480f684bd0858931441a18914e9b09abeb9b2fda1d98e94e3c72a8542ecdf2cd4c5dcc272e03ebfd18c80a8782ab73d3c42af5478ad6d6e163b0afc763ae93116ab5b4e983270a57b22e408b8dbcd344ef79468296b824b2f0310f74dca4c183ed6b51c4ae50534c8150d7217a021f35bc2b640ee886a91441906b7042c1537957f906ed8c3e37; s_v_web_id=verify_mntyqetf_KUN4BO46_No8T_4omQ_ArTl_NxDK43TnNmS7; dy_swidth=1920; dy_sheight=1200; is_dash_user=1; passport_csrf_token=9aab0217fa655867f6bcb339c8e689fe; passport_csrf_token_default=9aab0217fa655867f6bcb339c8e689fe; bd_ticket_guard_client_web_domain=2; passport_mfa_token=CjWmgIRcj9zkIOKqVbZ6f0ACNInuyrFcJmHH8S%2FHKjxXBrmWKV%2FB1NZYq0Qjh7WggFIUrXmt6hpKCjwAAAAAAAAAAAAAUEouyYlsBTv%2F1BqGxnVvrrst4yC74OXLPJiy%2F3%2FbmnB5KFQkMCU5TU%2BPhTZQc79Hm7sQisKODhj2sdFsIAIiAQNLcI9F; d_ticket=c61d732c4251f08791d78410fec3102e65d00; n_mh=PSEQnnuFafsxSORT4aCywzet62TVVsHqkix96KnjznQ; is_staff_user=false; has_biz_token=false; __security_server_data_status=1; SEARCH_RESULT_LIST_TYPE=%22single%22; publish_badge_show_info=%220%2C0%2C0%2C1775893016295%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; download_guide=%223%2F20260411%2F1%22; my_rd=2; SEARCH_UN_LOGIN_PV_CURR_DAY=%7B%22date%22%3A1776157352514%2C%22count%22%3A3%7D; playRecommendGuideTagCount=2; totalRecommendGuideTagCount=2; passport_assist_user=CjxC2fQrhLwLKN7F5ZLrQz0UgCJVf2y8QCLlwsj9AuE8-Zzvx-3FD0jI9YAWu1BrKlFuhVCJdMUJlpi2kpcaSgo8AAAAAAAAAAAAAFBNALh2PilmfuIjRGdEOSBCd-m3_xZwRD7hAGc_AYLt-HFvGkut2xgw-X1C4EHaUvmpEKTljg4Yia_WVCABIgED_8ev1g%3D%3D; sid_guard=3ccd4c12a04fe69abe9577e9693991ed%7C1776159699%7C5184000%7CSat%2C+13-Jun-2026+09%3A41%3A39+GMT; uid_tt=1b0f7a5c93a456921174ef9d8d33796e; uid_tt_ss=1b0f7a5c93a456921174ef9d8d33796e; sid_tt=3ccd4c12a04fe69abe9577e9693991ed; sessionid=3ccd4c12a04fe69abe9577e9693991ed; sessionid_ss=3ccd4c12a04fe69abe9577e9693991ed; session_tlb_tag=sttt%7C11%7CPM1MEqBP5pq-lXfpaTmR7f________-3BArgptGw28q4JciYqPO8vfN_2-7xsMmGVZmzk9FBGgc%3D; sid_ucp_v1=1.0.0-KDM4ZDI3N2QxY2QyMjY5NWM4YzMyZmQ1NTQ4MmJiMTQ1ZGQ2YzRmZTAKHwjhw_-U2wIQ05f4zgYY7zEgDDDpvpbUBTgHQPQHSAQaAmhsIiAzY2NkNGMxMmEwNGZlNjlhYmU5NTc3ZTk2OTM5OTFlZA; ssid_ucp_v1=1.0.0-KDM4ZDI3N2QxY2QyMjY5NWM4YzMyZmQ1NTQ4MmJiMTQ1ZGQ2YzRmZTAKHwjhw_-U2wIQ05f4zgYY7zEgDDDpvpbUBTgHQPQHSAQaAmhsIiAzY2NkNGMxMmEwNGZlNjlhYmU5NTc3ZTk2OTM5OTFlZA; _bd_ticket_crypt_cookie=ddb28924c0a9561c174c1a3643941a03; __security_mc_1_s_sdk_sign_data_key_web_protect=df03659c-4635-bf0a; __security_mc_1_s_sdk_cert_key=b9bd7e28-4434-9ffb; __security_mc_1_s_sdk_crypt_sdk=729383d6-4266-84d0; login_time=1776159699869; strategyABtestKey=%221776214739.323%22; ttwid=1%7CUddC5kyXbt2rVyeNZ4fp8Ln1Cvqp0puNhLzbkIdrTsI%7C1776214747%7Cc0f2c4663125afcd2ded100e92629cecab2e665dbc8dc1b6e21c8574958b075b; __ac_nonce=069df46950039f44e3a35; __ac_signature=_02B4Z6wo00f01DiKhUAAAIDB59F2D9Xsiuw4qoHAAGgE3d; douyin.com; device_web_cpu_core=4; device_web_memory_size=8; architecture=amd64; SelfTabRedDotControl=%5B%7B%22id%22%3A%227565134449445177394%22%2C%22u%22%3A12%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227613331940631906330%22%2C%22u%22%3A43%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227626431936633767976%22%2C%22u%22%3A11%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227572178869994653730%22%2C%22u%22%3A24%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227598987562694215706%22%2C%22u%22%3A3%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227592631332983818292%22%2C%22u%22%3A11%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227403702394410534927%22%2C%22u%22%3A628%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227399518990248183862%22%2C%22u%22%3A480%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227615126557769599003%22%2C%22u%22%3A11%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227594096664508368948%22%2C%22u%22%3A33%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227611356423145916457%22%2C%22u%22%3A27%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227603608418011760646%22%2C%22u%22%3A19%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227489387672155195404%22%2C%22u%22%3A121%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227582545816422713378%22%2C%22u%22%3A120%2C%22c%22%3A0%7D%5D; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA2YVJCY2a9-dpBEN28Io7m4Ap899IiAo8za2FAXSgVn0%2F1776268800000%2F0%2F0%2F1776240881911%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA2YVJCY2a9-dpBEN28Io7m4Ap899IiAo8za2FAXSgVn0%2F1776268800000%2F0%2F1776240281911%2F0%22; biz_trace_id=da2467d6; IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1200%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A4%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A100%7D%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQmdQaDNOOWFlY3J2NzhETlQvcFB3cGFVNHBXRFY2OVpmb2MxZHE2Z25BNm8xYzlmYUZ4NWZYeWUxTDdDOTM2d2FFMEZROUFqUXhaQ3EyN3lmeXVCNkU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJCZ1BoM045YWVjcnY3OEROVC9wUHdwYVU0cFdEVjY5WmZvYzFkcTZnbkE2bzFjOWZhRng1Zlh5ZTFMN0M5MzZ3YUUwRlE5QWpReFpDcTI3eWZ5dUI2RT0iLCJ0c19zaWduIjoidHMuMi45MmM0M2ViM2M5YTY1YWVhZmI0N2I2MzM0YWQ0MjMyYzBiY2Q2MDhjMGZmYWQ4ZjYzMWIzMDhjZmI2ZWI2YWQxYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJSd1lxVU1GTUUrOUNsYjQ5eVNpcnVPNjY2TzhMK2xPT2l1ckhKT2JnOUQ4PSIsInNlY190cyI6IiNibEFPYkdoL2pYUFV3T2NUOThUTnVMWHU1Qys2cXlxNHBQM3FqcmxONEdnWkE3TVFCRkxJczJiRFJTeGoifQ%3D%3D; home_can_add_dy_2_desktop=%221%22; odin_tt=0cdd3369acde7f635b61303c9213105f35eb8944de054f0196e10ef0f450419d1598634e4b7feccb4e42a84f70cda187b7c6139a9d5cd3341de02cfeaabdf4a9057da11e63acb0fae2cc9111609c527c"
COOKIE = cfg_cookie
# User-Agent 必须和 Cookie 同一个浏览器
# UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
UA = cfg_user_agent
# ===================== 【核心：防风控 频率控制】 =====================
# 超级安全，不会被封的节奏（实测长期稳定）
MIN_DELAY = 1.2        # 最小间隔秒
MAX_DELAY = 2.8        # 最大间隔秒
BATCH_PAUSE = 10       # 每爬5个休息10秒（防高频）
BATCH_SIZE = 5
NAV_BATCH_SIZE = 50
# ======================================================================

# 从链接提取 sec_user_id（自动去参数）
def extract_sec_uid(url):
    path = urlparse(url).path
    match = re.search(r"/user/([A-Za-z0-9_-]+)", path)
    return match.group(1) if match else None

# 请求用户信息接口（官方主页接口）
def get_user_info(sec_uid):
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
        "Cookie": COOKIE.strip().replace("\n", "").replace("  ", " "),
        "Referer": "https://www.douyin.com/",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
        return resp.json()
    except Exception as e:
        return {"status_code": -1, "error": str(e)}

# 平滑延时（防风控核心）
def smooth_sleep():
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)


def getUserInfo(tid,commentinfo):
    url = commentinfo['url']
    sec_uid = extract_sec_uid(url)
    if not sec_uid:
        print("❌ 无法解析:", url)
        return True
    data = get_user_info(sec_uid)

    if data.get("status_code") == 0:
        user = data["user"]
        room_data = user.get("room_data")
        if not room_data:
            return True
        room_data = json.loads(room_data)
        web_rid = room_data["owner"]["web_rid"]
        if not web_rid:
            return True
        print(f'直播中，直播id：{web_rid}')
        tmpdata = {
            'liveid': web_rid,
            'name':commentinfo.get('nickname'),
            'status':1,
            'islisten':1,
            'touser': commentinfo.get('touser',''),
        }
        db.insert('craw_lives', tmpdata)
        db.update('craw_douyin_listen_user', {'liveid': web_rid}, f"id={tid}")
    else:
        print(f"❌ 失败 status={data.get('status_code')}")

    # ============= 【关键：频率控制】 =============
    smooth_sleep()

    return True
# ==============================================================================
if __name__ == "__main__":
    # UA,COOKIE = cfun.get_ua_and_cookie()
    # print(UA)
    # print(COOKIE)
    # import os
    # print(os.environ)
    args = cfun.parse_arguments()
    if args.url is not None:
        db = MySQLHandler(**mysql_config)
        db.connect()
        print("手动抓取")
        userurl = args.url
        print(userurl+'\n')
        tdata = {"url":userurl}
        rs = getUserInfo(0,tdata)
        db.disconnect()
    else:
        i = 0
        # 慢速模式
        is_slow = cfg_is_slow
        RUN = True
        while RUN: 
            try:
                db = MySQLHandler(**mysql_config)
                db.connect()
                tmpinfo = None
                tmpinfo=db.execute_query(f'select * from craw_douyin_listen_user where status=1 and is_haslive=1 and liveid="" and  (live_next_runtime is null or live_next_runtime<=now()) order by id asc limit 10')
                # tmpinfo = [{'pid':0,'id':0,'sec_uid':'https://www.douyin.com/user/MS4wLjABAAAAh9Y8BC2hlEIvlKQK0jd1bGQ766ktlR_jGZQjmPaKadA'}]
                if not tmpinfo:
                    if i==0:
                        print('没有要操作的数据')
                    time.sleep(60)
                    i += 1  
                    
                else:
                    for tdata in tmpinfo:
                        if is_slow:
                            time.sleep(random.randint(1, 3))
                        tid = tdata['id']
                        userurl = tdata['url']
                        print(userurl+'\n')
                        # 每 N 个强制打开浏览器，避免高频触发风控
                        if i % NAV_BATCH_SIZE == 0:
                            print(f"\n⏸ 每{NAV_BATCH_SIZE}个休息3秒...")
                            try:
                                RUN = cfun.navigate_to_url(userurl,True,True)
                                time.sleep(3)
                            except Exception as e:
                                pass   
                        rs = getUserInfo(tid,tdata)
                        if rs:
                            # 更新任务状态
                            now = datetime.datetime.now()
                            nowtime = now.strftime("%Y-%m-%d %H:%M:%S") 
                            next_runtime = cfun.get_next_runtime(now, tdata.get('level', 'S'))
        
                            r = db.update('craw_douyin_listen_user',{
                                    'live_last_runtime': nowtime,
                                    'live_next_runtime': next_runtime,
                                },f'id="{tid}"')
                            if not r:
                                break
                        else:
                            break
                        i += 1    
                db.disconnect()    

                # 每 N 个强制休息一段，避免高频触发风控
                if i % BATCH_SIZE == 0:
                    print(f"\n⏸ 每{BATCH_SIZE}个休息 {BATCH_PAUSE}秒...")
                    time.sleep(BATCH_PAUSE)
                
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
                time.sleep(10)
                pass