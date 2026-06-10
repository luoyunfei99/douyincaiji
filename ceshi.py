import cfun

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
# 测试URL
test_url = "https://www.douyin.com/aweme/v1/web/comment/list/?device_platform=sdfsdfsdfsdfds&aid=6383&channel=channel_pc_web&aweme_id=7483314320152022322&cursor=0&count=5&item_type=0&whale_cut_token=&cut_version=1&rcFT=&update_version_code=170400&pc_client_type=1&pc_libra_divert=Windows&support_h265=1&support_dash=1&cpu_core_num=4&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1920&screen_height=1200&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=132.0.0.0&browser_online=true&engine_name=Blink&engine_version=132.0.0.0&os_name=Windows&os_version=10&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid=7627387120927999507&uifid=5a0fbbb49c6c57acd77ca86d66dd2e8e2f1fcf7b3fa6b8a56e480f684bd0858931441a18914e9b09abeb9b2fda1d98e94e3c72a8542ecdf2cd4c5dcc272e03ebfd18c80a8782ab73d3c42af5478ad6d6e163b0afc763ae93116ab5b4e983270a57b22e408b8dbcd344ef79468296b824b2f0310f74dca4c183ed6b51c4ae50534c8150d7217a021f35bc2b640ee886a91441906b7042c1537957f906ed8c3e37&msToken=G5QRQ_A-KhABrJ4Sf55CwlJ7tUprR5offE86FV5WN780QDY5n72N3JdcO4feU-u8ENxc6E3sGgZ3rnXZlEZLuOiX3PxMKhFyTpRpYWNM7zBc-eEmUcxBzV99y9uDSYZOCy-XMyLzAyfJs1PF8iab7le67TDHRmrzW8nefClZDc_EezdbmRkprQ%3D%3D&a_bogus=dysjDqUwm2WnaV%2FtmKJ7C-3lW1glrTuyA1T%2FbzOP9NPba7eYgmPguOS%2FaxLr-Iffaup0hCVHFxeMYEdcmsUkZKrkLmpvuuzSUT5n980ohqqsGFJQLHDECzXzqw0rU5GqeQVfilsI0Ut9gnxAkrQE%2FplJt%2FxKQRSBMZxRk2zbE9iXZzLAg3nlPdSkxwrOUvc7&verifyFp=verify_mntyqetf_KUN4BO46_No8T_4omQ_ArTl_NxDK43TnNmS7&fp=verify_mntyqetf_KUN4BO46_No8T_4omQ_ArTl_NxDK43TnNmS7"

# 调用方法
result_json = cfun.update_params_from_url(test_url, FIXED_PARAMS)

# 输出结果
print("更新后的JSON数据：")
print(result_json)
