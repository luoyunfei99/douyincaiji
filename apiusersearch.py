import requests
import urllib.parse
import hashlib
import random
import time
import json

# ==============================================
# 固定配置（直接使用你提供的参数）
# ==============================================
KEYWORD = "长沙索菲亚"  # 你的视频ID
BASE_URL = "https://www.douyin.com/aweme/v1/web/discover/search/"

# 你浏览器的真实 UA（必须和你抓包时一致）
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
COOKIE = "enter_pc_once=1; UIFID_TEMP=5a0fbbb49c6c57acd77ca86d66dd2e8e2f1fcf7b3fa6b8a56e480f684bd0858960f7fd30186218b604f1aa03a80d6bcf30f99252e4728b84d4493ddf33e6e2f542ef3f0384c522a3bbf7c4cdf5de4454; hevc_supported=true; fpk1=U2FsdGVkX19BuSu3u6Zk7U4o4ouVXJrYLgPXwX4lIxPDnmtO5Vcv6/lvNgBY1GM1mLa2dWEw+O/PfQDXEZufGg==; fpk2=41770e408d453f0e18b6cf535e220c84; UIFID=5a0fbbb49c6c57acd77ca86d66dd2e8e2f1fcf7b3fa6b8a56e480f684bd0858931441a18914e9b09abeb9b2fda1d98e94e3c72a8542ecdf2cd4c5dcc272e03ebfd18c80a8782ab73d3c42af5478ad6d6e163b0afc763ae93116ab5b4e983270a57b22e408b8dbcd344ef79468296b824b2f0310f74dca4c183ed6b51c4ae50534c8150d7217a021f35bc2b640ee886a91441906b7042c1537957f906ed8c3e37; s_v_web_id=verify_mntyqetf_KUN4BO46_No8T_4omQ_ArTl_NxDK43TnNmS7; dy_swidth=1920; dy_sheight=1200; is_dash_user=1; passport_csrf_token=9aab0217fa655867f6bcb339c8e689fe; passport_csrf_token_default=9aab0217fa655867f6bcb339c8e689fe; bd_ticket_guard_client_web_domain=2; passport_mfa_token=CjWmgIRcj9zkIOKqVbZ6f0ACNInuyrFcJmHH8S%2FHKjxXBrmWKV%2FB1NZYq0Qjh7WggFIUrXmt6hpKCjwAAAAAAAAAAAAAUEouyYlsBTv%2F1BqGxnVvrrst4yC74OXLPJiy%2F3%2FbmnB5KFQkMCU5TU%2BPhTZQc79Hm7sQisKODhj2sdFsIAIiAQNLcI9F; d_ticket=c61d732c4251f08791d78410fec3102e65d00; n_mh=PSEQnnuFafsxSORT4aCywzet62TVVsHqkix96KnjznQ; has_biz_token=false; __security_server_data_status=1; SEARCH_RESULT_LIST_TYPE=%22single%22; publish_badge_show_info=%220%2C0%2C0%2C1775893016295%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; download_guide=%223%2F20260411%2F1%22; my_rd=2; playRecommendGuideTagCount=2; totalRecommendGuideTagCount=2; strategyABtestKey=%221776321320.235%22; douyin.com; device_web_cpu_core=4; device_web_memory_size=8; architecture=amd64; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1200%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A4%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; SEARCH_UN_LOGIN_PV_CURR_DAY=%7B%22date%22%3A1776331756018%2C%22count%22%3A2%7D; ttwid=1%7CUddC5kyXbt2rVyeNZ4fp8Ln1Cvqp0puNhLzbkIdrTsI%7C1776331764%7Cde97551c42ac86340c6825e3b168366c49b637588fa80567bf6ff3a6809eb10c; passport_assist_user=CjzhMnKl9OQ1lXt2JVqkWFVSoQ7LD-7AP3gIFagrL7g6Kg97TFMf-fb1MQtvifHSoq1MM47EiO68r7eZc9UaSgo8AAAAAAAAAAAAAFBPuCIvW-TT29js8nBw5RdPk77Mts0DdjJOIi3DMhR2wu04UwSBAkAev5a1kY43A3SeEO_7jg4Yia_WVCABIgED6vdBDg%3D%3D; sid_guard=8ea23b9a4951706859de9c274d6cd09a%7C1776331797%7C5184000%7CMon%2C+15-Jun-2026+09%3A29%3A57+GMT; uid_tt=4ac2738dcbe744c70b2b268871063819; uid_tt_ss=4ac2738dcbe744c70b2b268871063819; sid_tt=8ea23b9a4951706859de9c274d6cd09a; sessionid=8ea23b9a4951706859de9c274d6cd09a; sessionid_ss=8ea23b9a4951706859de9c274d6cd09a; session_tlb_tag=sttt%7C11%7CjqI7mklRcGhZ3pwnTWzQmv_________xpf7ILhZPnVLiuI-8n3q-6K6VKVRmyrEPu930z2bAA2Q%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KDk4Njc0MjFkMGVmZDBhYTVhMzg5Y2NmODZhZTUxNTQ2MjY0NjgzMDUKHwjhw_-U2wIQldiCzwYY7zEgDDDpvpbUBTgHQPQHSAQaAmhsIiA4ZWEyM2I5YTQ5NTE3MDY4NTlkZTljMjc0ZDZjZDA5YQ; ssid_ucp_v1=1.0.0-KDk4Njc0MjFkMGVmZDBhYTVhMzg5Y2NmODZhZTUxNTQ2MjY0NjgzMDUKHwjhw_-U2wIQldiCzwYY7zEgDDDpvpbUBTgHQPQHSAQaAmhsIiA4ZWEyM2I5YTQ5NTE3MDY4NTlkZTljMjc0ZDZjZDA5YQ; _bd_ticket_crypt_cookie=b804f799a514cd0db31442a62108952b; __security_mc_1_s_sdk_sign_data_key_web_protect=ab9c51ec-403f-8ec1; __security_mc_1_s_sdk_cert_key=c331d518-4667-8ca7; __security_mc_1_s_sdk_crypt_sdk=5d4ae437-41e4-baca; login_time=1776331798258; __ac_nonce=069e0ac16001e422c8b49; __ac_signature=_02B4Z6wo00f01j2nRMQAAIDD4vy3isQBpkI9h0BAAOaX87; csrf_session_id=396cef9ab5c3e8798af8c2835ae05a36; SelfTabRedDotControl=%5B%7B%22id%22%3A%227613331940631906330%22%2C%22u%22%3A46%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227598987562694215706%22%2C%22u%22%3A5%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227626431936633767976%22%2C%22u%22%3A12%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227565134449445177394%22%2C%22u%22%3A12%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227572178869994653730%22%2C%22u%22%3A24%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227592631332983818292%22%2C%22u%22%3A11%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227403702394410534927%22%2C%22u%22%3A628%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227399518990248183862%22%2C%22u%22%3A480%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227615126557769599003%22%2C%22u%22%3A11%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227594096664508368948%22%2C%22u%22%3A33%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227611356423145916457%22%2C%22u%22%3A27%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227603608418011760646%22%2C%22u%22%3A19%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227489387672155195404%22%2C%22u%22%3A121%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227582545816422713378%22%2C%22u%22%3A120%2C%22c%22%3A0%7D%5D; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA2YVJCY2a9-dpBEN28Io7m4Ap899IiAo8za2FAXSgVn0%2F1776355200000%2F0%2F0%2F1776332406528%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA2YVJCY2a9-dpBEN28Io7m4Ap899IiAo8za2FAXSgVn0%2F1776355200000%2F0%2F1776331806529%2F0%22; home_can_add_dy_2_desktop=%221%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQmdQaDNOOWFlY3J2NzhETlQvcFB3cGFVNHBXRFY2OVpmb2MxZHE2Z25BNm8xYzlmYUZ4NWZYeWUxTDdDOTM2d2FFMEZROUFqUXhaQ3EyN3lmeXVCNkU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; biz_trace_id=43139de6; IsDouyinActive=true; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f2735373534303136363633323234272927676c715a75776a716a666a69273f2763646976602778; bit_env=cHK_sD7XfS3pQ6rozQHzBW8i7WdNt-ULoxVbhPv1mRvnmlyhE9yN5Ox4xaiNl9ooOHqWK-fM29R4tD1HJoByQL0dulHhxGCjGc3uxB04LwpSrP3I9z7sQOm-gWBFhysADzmH-iv1_NkDW1QjflMZIliIBCPdSBnlQP84nsEM47xDog-9S3Oi8zPV2_N5fCC-gTKYK_GsvZl78ptvEO7SmfIxPQ_L8_LrKRm4fphapa6PRwqltsiTgLXa9r7MKA_8gdES9_TYzcnPsHdDE6VFE9h3h293XSDiNOZhs7CovNy1n76kMJWMuqkS5t0bRKU5lLIHznZe-g-61Nk718pMJ76gD_vR_RHonjYQ32pPymQGc8nDDeLK9oM9GkxRHFlYYwE5qVuxVN_xH12pPoGGxd5FMSyA1EtY0yyL--RA4HSk9tr_-gpaSzp6Eq-3_GiYeh4fvhwQxtBX8GvaFYgVVoCho8gg3MoA83NbWl08Q78Ih9zVGr_jHa8vOEi59Ln7; gulu_source_res=eyJwX2luIjoiMGFlMWE3M2ZhMmUzMjFiMWEzNDkxZGU4MDQ1ZTY3ZTk1N2ExNDAzNmVkYjc3ZmY5YTk5ZTQ2Yjg0NDdjYWM5ZCJ9; passport_auth_mix_state=w490m38mbozsr28vsfualeajud9eihwxn0qbe3xpbwomz5z6; odin_tt=625b3920adc38bf3911a36a40b40d0af48f00e53cd975ce319145e785939467603d67c2820833fb63d78c8ae72446c77; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJCZ1BoM045YWVjcnY3OEROVC9wUHdwYVU0cFdEVjY5WmZvYzFkcTZnbkE2bzFjOWZhRng1Zlh5ZTFMN0M5MzZ3YUUwRlE5QWpReFpDcTI3eWZ5dUI2RT0iLCJ0c19zaWduIjoidHMuMi42ZGYxMGMxMjc3NWYxMDhjMjY1NGI3NzM2NzNjOWVkMGEzZGViNTFlZjk3YzZhM2JjMmFlODBjOWE1MTcxM2MxYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJYVHBUYldWRXVPdUlmd25oa2xVRE9SMUh0UXFxRjlud1ZFZS9GZGNodk5ZPSIsInNlY190cyI6IiNtUVdHc3JDVjhRcnJLb2gwdW1PRHh3ZnhOZDBCWFJ4VFR5NGJQWnBaeDlydStTNHQyZGRpc1RNZTN2NisifQ%3D%3D"

# 固定请求参数
FIXED_PARAMS = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "search_channel": "aweme_user_web",
    "search_source": "switch_tab",
    "query_correct_type": "1",
    "is_filter_search": "0",
    "from_group_id": "",
    "disable_rs": "0",
    "need_filter_settings": "1",
    "list_type": "single",
    "pc_search_top_1_params": {"enable_ai_search_top_1":1},
    "search_id": "2026041617301418974E00FE23CEBBC846",
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
    "msToken": "c3hVhCs2buyOUfeIK-rK9uZzfgJZFPNza9IWQRiNQX9xiXV4E-ll6OhJproctnc16RyVQL1Ja1gNctQ15AcBwZxpa45efUl8z-k4Onzj5_VTsqMlvMhSayhR-1xuzkdx2LHYQ39_rVfIAzzpb1mCO_VXkcWx5JKBiskuhsQ4kJSZt2CNrl8IXto%253D",
}

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


def build_url(keyword, cursor):
    params = FIXED_PARAMS.copy()
    params["keyword"] = keyword
    params["offset"] = str(cursor)
    params["count"] = "12" if cursor == 0 else "10"
    sorted_params = sorted(params.items())
    qs = urllib.parse.urlencode(sorted_params, safe="=")
    a_bogus = generate_a_bogus(qs, USER_AGENT)
    a_bogus = "xjUVDwywQ28jaV%2FbmKpG931U32f%2FrT8ybNTKb75lyxwvP7tYg8PzYrakrooO2cgUlYB0kFVHefTAYndcu0tkZKnkKmZvu0ibUG5VnX8ohqq4TzvQDrfkC8zFzwMnU5sqa55SilmIgUtH6jdAhrQ8%2Fd-Je%2FxCQ5SBB1xfk%2FubP9NhZMyAE1c-PQtpNhJG0fKj"
    return f"{BASE_URL}?{qs}&a_bogus={urllib.parse.quote(a_bogus)}"

# ==============================================
# 请求头（防封）
# ==============================================


def get_headers():
    return {
        "User-Agent": USER_AGENT,
        "Referer": f"https://www.douyin.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="132", "Not A Brand";v="99", "Google Chrome";v="132"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": "enter_pc_once=1; UIFID_TEMP=5a0fbbb49c6c57acd77ca86d66dd2e8e2f1fcf7b3fa6b8a56e480f684bd0858960f7fd30186218b604f1aa03a80d6bcf30f99252e4728b84d4493ddf33e6e2f542ef3f0384c522a3bbf7c4cdf5de4454; hevc_supported=true; fpk1=U2FsdGVkX19BuSu3u6Zk7U4o4ouVXJrYLgPXwX4lIxPDnmtO5Vcv6/lvNgBY1GM1mLa2dWEw+O/PfQDXEZufGg==; fpk2=41770e408d453f0e18b6cf535e220c84; UIFID=5a0fbbb49c6c57acd77ca86d66dd2e8e2f1fcf7b3fa6b8a56e480f684bd0858931441a18914e9b09abeb9b2fda1d98e94e3c72a8542ecdf2cd4c5dcc272e03ebfd18c80a8782ab73d3c42af5478ad6d6e163b0afc763ae93116ab5b4e983270a57b22e408b8dbcd344ef79468296b824b2f0310f74dca4c183ed6b51c4ae50534c8150d7217a021f35bc2b640ee886a91441906b7042c1537957f906ed8c3e37; s_v_web_id=verify_mntyqetf_KUN4BO46_No8T_4omQ_ArTl_NxDK43TnNmS7; douyin.com; device_web_cpu_core=4; device_web_memory_size=8; architecture=amd64; dy_swidth=1920; dy_sheight=1200; is_dash_user=1; passport_csrf_token=9aab0217fa655867f6bcb339c8e689fe; passport_csrf_token_default=9aab0217fa655867f6bcb339c8e689fe; bd_ticket_guard_client_web_domain=2; SEARCH_UN_LOGIN_PV_CURR_DAY=%7B%22date%22%3A1775892916330%2C%22count%22%3A3%7D; passport_mfa_token=CjWmgIRcj9zkIOKqVbZ6f0ACNInuyrFcJmHH8S%2FHKjxXBrmWKV%2FB1NZYq0Qjh7WggFIUrXmt6hpKCjwAAAAAAAAAAAAAUEouyYlsBTv%2F1BqGxnVvrrst4yC74OXLPJiy%2F3%2FbmnB5KFQkMCU5TU%2BPhTZQc79Hm7sQisKODhj2sdFsIAIiAQNLcI9F; d_ticket=c61d732c4251f08791d78410fec3102e65d00; n_mh=PSEQnnuFafsxSORT4aCywzet62TVVsHqkix96KnjznQ; is_staff_user=false; has_biz_token=false; __security_server_data_status=1; SEARCH_RESULT_LIST_TYPE=%22single%22; publish_badge_show_info=%220%2C0%2C0%2C1775893016295%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA2YVJCY2a9-dpBEN28Io7m4Ap899IiAo8za2FAXSgVn0%2F1775923200000%2F0%2F1775893079605%2F0%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; download_guide=%223%2F20260411%2F0%22; __ac_nonce=069dc4492005949dcc1a7; __ac_signature=_02B4Z6wo00f01rQoyUgAAIDDa3M6BmDzJ5q0CM3AAMTi0d; strategyABtestKey=%221776043156.145%22; ttwid=1%7CUddC5kyXbt2rVyeNZ4fp8Ln1Cvqp0puNhLzbkIdrTsI%7C1776043163%7C6363436a5cfc997031c5ba4fbca999ba82650124d1f683461f3f4ea1e4fdab02; gulu_source_res=eyJwX2luIjoiMGFlMWE3M2ZhMmUzMjFiMWEzNDkxZGU4MDQ1ZTY3ZTk1N2ExNDAzNmVkYjc3ZmY5YTk5ZTQ2Yjg0NDdjYWM5ZCJ9; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f27363c3236333436313533323234272927676c715a75776a716a666a69273f2763646976602778; bit_env=sFUG21uvumXyknvtod89EwbFo7ZOisGLEBxb7Mg9iUZc2XjeoNZZrufGjt-Thm6_FS0zTcM6WOC1u83toBI9PQySjnxzyhtlRDJfzg7BT_bJeY8UbtMCrXi41b2NFX8EQZpfmt0SzANtLWcJ82m6EkClga-sFUJVbupZthKxelhrWFAef1h5II8QrMYbV1AFrmkhvETTUMIErL-mwD8av_PJ5Do2ZHjEujJVEEALkPrsmdx1x8lHJAL0DCqq1K0lghiigs0vgzBa8L6UEIDly3VsjaaTDTUIwrfV6VWqrWIinDlrOngFZIvzKtcHY-q7yAci4bZu_un-HNrW-MS2-5juATM5f0gvcaAkC8nbc9fGKLoS9xuDG7HiAOTUzp26KiCV-QP2Lfo5F4XlB7I4a88oDDRtjkIODlmeJzpa93ZDQNAoBh6Y8vkV_Y0aJWwVCguCzrGXKU8J_9dWoS7Ea7yLArqz8ut9CadwIdHJPJig_udJ-j4VN3eO27KQUqJK; passport_auth_mix_state=jvr64irb0cxo7o54huvnusm0lqfdgfvvfheinbwy5xt9m695; biz_trace_id=e5cef0f2; passport_assist_user=CjyXyctvWx53GnOS8zwLW9gWYF_qDVKz-HWdDAxSD2-KsfwkDjOL1-4uYhX3_tFyZnUmrGS7NCeuguKOsr8aSgo8AAAAAAAAAAAAAFBL80CE1GgodrinIBW_2FYzFlPdnDlV-Oj2Ibcx_Ffedm9wkmBdsuqIFD4WxGpaEa4-EOvUjg4Yia_WVCABIgEDORjOAA%3D%3D; sid_guard=48ed3c1bdd0d8bfb1a07eeab4fe6fdb7%7C1776043252%7C5184000%7CFri%2C+12-Jun-2026+01%3A20%3A52+GMT; uid_tt=b8edab9d6ecd8fd6959de40062ba597f; uid_tt_ss=b8edab9d6ecd8fd6959de40062ba597f; sid_tt=48ed3c1bdd0d8bfb1a07eeab4fe6fdb7; sessionid=48ed3c1bdd0d8bfb1a07eeab4fe6fdb7; sessionid_ss=48ed3c1bdd0d8bfb1a07eeab4fe6fdb7; session_tlb_tag=sttt%7C19%7CSO08G90Ni_saB-6rT-b9t__________irkq6pZU5v8KdjRfomzwV8M1PV4k2JR_eRwJF6mZKJNU%3D; sid_ucp_v1=1.0.0-KGVkMGFmYzczZmM4ZDYxMTFjOTNkNmIyMjI4OTVjMjE3YTJmNzRjZjYKHwjhw_-U2wIQ9InxzgYY7zEgDDDpvpbUBTgHQPQHSAQaAmhsIiA0OGVkM2MxYmRkMGQ4YmZiMWEwN2VlYWI0ZmU2ZmRiNw; ssid_ucp_v1=1.0.0-KGVkMGFmYzczZmM4ZDYxMTFjOTNkNmIyMjI4OTVjMjE3YTJmNzRjZjYKHwjhw_-U2wIQ9InxzgYY7zEgDDDpvpbUBTgHQPQHSAQaAmhsIiA0OGVkM2MxYmRkMGQ4YmZiMWEwN2VlYWI0ZmU2ZmRiNw; _bd_ticket_crypt_cookie=a95da0e07a4512479d340a5594fa8175; __security_mc_1_s_sdk_sign_data_key_web_protect=0d7dfbb8-4b02-ac44; __security_mc_1_s_sdk_cert_key=79c4a7df-46a9-8624; __security_mc_1_s_sdk_crypt_sdk=61981a68-4e5c-a5e9; login_time=1776043250126; IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1200%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A4%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; SelfTabRedDotControl=%5B%7B%22id%22%3A%227613331940631906330%22%2C%22u%22%3A41%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227565134449445177394%22%2C%22u%22%3A13%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227598987562694215706%22%2C%22u%22%3A3%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227592631332983818292%22%2C%22u%22%3A11%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227403702394410534927%22%2C%22u%22%3A628%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227399518990248183862%22%2C%22u%22%3A480%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227572178869994653730%22%2C%22u%22%3A23%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227615126557769599003%22%2C%22u%22%3A11%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227594096664508368948%22%2C%22u%22%3A33%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227611356423145916457%22%2C%22u%22%3A27%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227603608418011760646%22%2C%22u%22%3A19%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227489387672155195404%22%2C%22u%22%3A121%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227582545816422713378%22%2C%22u%22%3A120%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227579292813171361838%22%2C%22u%22%3A24%2C%22c%22%3A0%7D%5D; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA2YVJCY2a9-dpBEN28Io7m4Ap899IiAo8za2FAXSgVn0%2F1776096000000%2F0%2F1776043253400%2F0%22; odin_tt=68a954b449d690502697d6c991cc39c909ed378be5ad89ba3d244d81ee606a068739f34c0720f2ea586c3cd8f387a59a495352d19cda16c1afe2a3c148f86c25; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQmdQaDNOOWFlY3J2NzhETlQvcFB3cGFVNHBXRFY2OVpmb2MxZHE2Z25BNm8xYzlmYUZ4NWZYeWUxTDdDOTM2d2FFMEZROUFqUXhaQ3EyN3lmeXVCNkU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJCZ1BoM045YWVjcnY3OEROVC9wUHdwYVU0cFdEVjY5WmZvYzFkcTZnbkE2bzFjOWZhRng1Zlh5ZTFMN0M5MzZ3YUUwRlE5QWpReFpDcTI3eWZ5dUI2RT0iLCJ0c19zaWduIjoidHMuMi4yM2JmYzJlNDQ5ZjM3OGRiM2NjN2U3NzJlY2UyMzY0ZWMxYTc5ZjJmNDAxNDNhMmQ2MzhhYmM5OTI1YTJhYjdhYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJQNVBvN2d3TksxMGR4YXlCUUlQd3VKaHNEZjhVaG5MaHN0NVZMYjRxaHhBPSIsInNlY190cyI6IiNkSlI5VnI3bnJJT3hRQXBEMWlhWTJGMDdtMmI1bnFlbFFtcHBWb3RrWVBtVFBxZGRqY1U1czZZKytDSm8ifQ%3D%3D"
    }

# ==============================================
# 爬取一页评论
# ==============================================


def fetch_users(keyword, cursor):
    url = build_url(keyword, cursor)
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


def crawl_all_users(aweme_id):
    all_users = []
    cursor = 0
    page = 1

    while True:
        print(f"\n正在爬取第 {page} 页，cursor = {cursor}")

        # 防封：随机延时 1.5~4 秒
        wait = random.uniform(1.5, 4.0)
        time.sleep(wait)

        data = fetch_users(aweme_id, cursor)
        if not data:
            print("结束或被风控，停止爬取")
            break
        print(data)
        users = data.get("user_list", [])
        if not users:
            print("无更多用户")
            break
        print(users)
        # # 提取评论内容
        # for c in users:
        #     item = {
        #         "user_id": c.get("user", {}).get("uid"),
        #         "nickname": c.get("user", {}).get("nickname"),
        #         "comment": c.get("text"),
        #         "create_time": c.get("create_time"),
        #         "like_count": c.get("digg_count"),
        #         "reply_id": c.get("reply_id"),
        #         "cid": c.get("cid")
        #     }
        #     all_users.append(item)

        print(f"本页获取 {len(users)} 条，累计：{len(all_users)}")

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
            print("\n每10页休息 5~8 秒...")
            time.sleep(random.uniform(5, 8))

    return all_users

# ==============================================
# 保存结果
# ==============================================


def save_to_file(users):
    filename = f"抖音评论_{KEYWORD}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print(f"\n已保存到：{filename}，共 {len(users)} 条评论")


# ==============================================
# 主程序
# ==============================================
if __name__ == "__main__":
    print("开始爬取抖音关键词：", KEYWORD)
    users = crawl_all_users(KEYWORD)
    save_to_file(users)
