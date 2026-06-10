from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
import time
# import pandas as pd
# from openpyxl.styles import PatternFill
# import numpy as np
import re
# from openpyxl import load_workbook
# from playwright.sync_api import sync_playwright
from my_sql import MySQLHandler
import random
from config.mysql_config import mysql_config

def getDataByKeyword(page, keyword,rz_str):
    time.sleep(1)
    tab = page.new_tab()
    tab.get(f'https://www.douyin.com/search/{keyword}?type=user')
    time.sleep(1.5)
    tab.listen.start('douyin.com/aweme/v1/web/discover/search/')  # 开始监听
    ele = tab('x://*[@id="search-content-area"]/div/div[1]/div[1]/div/div/div/div/span')
    tab.actions.move_to(ele_or_loc=ele).click(f'x://*[contains(text(), "{rz_str}")]')
    time.sleep(1)
    try:
        break_str = tab.ele('x://*[contains(text(), "搜索结果为空")]')
        if break_str:
            print(keyword, rz_str, "搜索结果为空")
            tab.close()
            return []
    except:
        pass

    # res_list = []


    for w in range(100):
        try:
            res = tab.listen.wait(timeout=10)  # 等待并获取一个数据包
            for i in res.response.body['user_list']:
                uid = i['user_info']['uid']  # id
                unique_id = i['user_info']['unique_id']  # unique_id
                short_id = i['user_info']['short_id']  # 短id
                nickname = i['user_info']['nickname']  # 用户名
                signature = i['user_info']['signature']  # 用户介绍
                enterprise_verify_reason = i['user_info']['enterprise_verify_reason']
                sec_uid = 'https://www.douyin.com/user/'+ i['user_info']['sec_uid']+'?from_tab_name=main'  # 加密id
                follower_count = i['user_info']['follower_count']  # 粉丝量
                total_favorited = i['user_info']['total_favorited']  # 获赞
                phone = extract_and_join_phone_numbers(str(unique_id)+sec_uid)
                # res_list.append([rz_str, keyword, uid,unique_id, short_id, nickname, signature, sec_uid, enterprise_verify_reason, follower_count, total_favorited,phone])
                tdata = {
                        'type':rz_str,
                        'keyword':keyword,
                        'uid':uid,
                        'unique_id':unique_id,
                        'short_id':short_id,
                        'nickname':nickname,
                        'signature':signature,
                        'sec_uid':sec_uid,
                        'enterprise_verify_reason':enterprise_verify_reason,
                        'follower_count':follower_count,
                        'total_favorited':total_favorited,
                        'phone':phone
                    }
                print(tdata)
                db.insert('craw_douyin_user',tdata)

            # tab.scroll.down(800)     # 向下滚动 200 像素
            time.sleep(1)
            tab.scroll.to_bottom()  # 滚动到底部
            time.sleep(1)
        except Exception as e:
            print(str(e))
            break_str = tab.ele('x://*[contains(text(), "暂时没有更多了")]')
            if break_str:
                print('暂时没有更多了')
                break
    print(keyword, rz_str, '已经搜索完毕')
    tab.close()
    return True

def extract_and_join_phone_numbers(input_string):
    # 定义手机号的正则表达式
    phone_pattern = re.compile(r'1[3-9]\d{9}')
    # 查找所有匹配的手机号
    phone_numbers = re.findall(phone_pattern, input_string)
    # 用逗号拼接手机号
    result = ",".join(phone_numbers)
    return result
def getUserVideos(page,unique_id,url):
    time.sleep(1)
    tab = page.new_tab()
    tab.listen.start('www.douyin.com/aweme/v1/web/aweme/post/')  # 开始监听
    time.sleep(1)
    tab.get(url)
    time.sleep(2)

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
  
    for w in range(30):
        try:
            res = tab.listen.wait(timeout=5)  # 等待并获取一个数据包
            if not isinstance(res, bool):
                for i in res.response.body['aweme_list']:
                    aweme_id = i['aweme_id']
                    item_title = i['item_title']
                    turl = url+'&modal_id='+aweme_id
                    desc = i['desc']
                    phone = extract_and_join_phone_numbers(desc)
                    print(aweme_id, "\t",item_title,"\t",turl,"\t",desc,"\t",phone)
                    tdata = {
                        'unique_id':unique_id,
                        'aweme_id':aweme_id,
                        'item_title':item_title,
                        'turl':turl,
                        'desc':desc,
                        'phone':phone
                    }
                    db.insert('craw_douyin_user_video',tdata)
                    if phone:
                        break
                    # res_list.append([aweme_id,item_title, turl,desc,phone])
                # tab.scroll.down(800)     # 向下滚动 200 像素
            else:    
                element = tab.ele('x://*[contains(text(), "暂时没有更多了")]')
                if element:
                    print('暂时没有更多了')
                    break
                else:
                    continue
            time.sleep(3)
            e = tab.ele('x://div[@class="parent-route-container route-scroll-container IhmVuo1S"]')
            e.scroll.to_bottom()
            tab.scroll.to_bottom()  # 滚动到底部
            print(str(w)+'\n')
            time.sleep(1)
            
        except:
            pass
    try:
        tab.close() 
    except:
        pass
    return True


def validate_phone_number(string):
    # 手机号的正则表达式
    pattern = re.compile(r'1[3-9]\d{9}')
    # 在字符串中查找是否有匹配的手机号
    match = re.search(pattern, string)
    if match:
        return True
    else:
        return False

def getRandUserAgent():
    pc_user_agents = [
        # Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Firefox
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/119.0',
        # Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        # Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
    ]
    return random.choice(pc_user_agents)

def randPage():
    random_user_agent = getRandUserAgent()
    co = ChromiumOptions().set_argument('--no-sandbox').set_user_agent(random_user_agent)
    page = ChromiumPage(co)
    return page


if __name__ == '__main__':

    db = MySQLHandler(**mysql_config)
    db.connect()
    # turl = 'https://www.douyin.com/user/MS4wLjABAAAAGKRhEQ7CqVcbwFBgsOCSktJOPMvU2VvjgeG5ldUu4SE?from_tab_name=main'
    # random_user_agent = getRandUserAgent()
    # co = ChromiumOptions().set_argument('--no-sandbox').set_user_agent(random_user_agent)
    # page = ChromiumPage(co)
    # tab = page.new_tab()
    # tab.get(turl)
    # time.sleep(1.5)
    # exit()
    while True: 
        brandid = 0
        keyword = ''
        brandinfo=db.execute_query(f'select * from craw_brand where status=0 limit 1')
        if brandinfo:
            brandid = brandinfo[0]['id']
            keyword = brandinfo[0]['brand']
        else:
            print('没有要操作的品牌数据')
        # co = ChromiumOptions().set_argument('--no-sandbox').set_user_agent(random_user_agent)
        # page = ChromiumPage(co)
        if keyword:
            rz_arr = ['普通用户','个人认证','企业认证']
            for rz in rz_arr:
                tpage = randPage()
                time.sleep(3)
                getDataByKeyword(tpage, keyword,rz)
                #tpage.quit()
            db.update('craw_brand',{'status':1},f"id={brandid}")
            num = db.count('craw_douyin_user',f'status=0 and keyword="{keyword}"')
            if num>0:
                pagesize = 50
                for j in range(int(num/pagesize)+1):
                    datas=db.execute_query(f'select * from craw_douyin_user where status=0 and keyword="{keyword}" limit 0,{pagesize}')
                    for i in range(len(datas)):
                        time.sleep(3)
                        userurl = datas[i]['sec_uid']
                        unique_id =  datas[i]['unique_id']
                        id = datas[i]['id']
                        print(userurl+'\n')
                        tpage = randPage()
                        getUserVideos(tpage,unique_id,userurl)
                        #tpage.quit()
                        db.update('craw_douyin_user',{'status':1},f'id="{id}"')
        time.sleep(3)


        
            


