#!/usr/bin/python
# coding:utf-8

# @FileName:    liveMan.py
# @Time:        2024/1/2 21:51
# @Author:      bubu
# @Project:     douyinLiveWebFetcher

import codecs
import gzip
import hashlib
import random
import re
import string
import subprocess
import urllib.parse
from contextlib import contextmanager
from unittest.mock import patch

import requests
import websocket
from py_mini_racer import MiniRacer

from protobuf.douyin import *
import traceback
from my_sql import MySQLHandler
import sys
from pathlib import Path
# 获取当前文件所在目录的父目录，并添加到系统路径
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.mysql_config import mysql_config
import os
@contextmanager
def patched_popen_encoding(encoding='utf-8'):
    original_popen_init = subprocess.Popen.__init__
    
    def new_popen_init(self, *args, **kwargs):
        kwargs['encoding'] = encoding
        original_popen_init(self, *args, **kwargs)
    
    with patch.object(subprocess.Popen, '__init__', new_popen_init):
        yield


def generateSignature(wss, script_file='sign.js'):
    """
    出现gbk编码问题则修改 python模块subprocess.py的源码中Popen类的__init__函数参数encoding值为 "utf-8"
    """
    params = ("live_id,aid,version_code,webcast_sdk_version,"
              "room_id,sub_room_id,sub_channel_id,did_rule,"
              "user_unique_id,device_platform,device_type,ac,"
              "identity").split(',')
    wss_params = urllib.parse.urlparse(wss).query.split('&')
    wss_maps = {i.split('=')[0]: i.split("=")[-1] for i in wss_params}
    tpl_params = [f"{i}={wss_maps.get(i, '')}" for i in params]
    param = ','.join(tpl_params)
    md5 = hashlib.md5()
    md5.update(param.encode())
    md5_param = md5.hexdigest()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_file = f'{script_dir}\{script_file}'
    with codecs.open(script_file, 'r', encoding='utf8') as f:
        script = f.read()
    
    ctx = MiniRacer()
    ctx.eval(script)
    
    try:
        signature = ctx.call("get_sign", md5_param)
        return signature
    except Exception as e:
        print(e)
    
    # 以下代码对应js脚本为sign_v0.js
    # context = execjs.compile(script)
    # with patched_popen_encoding(encoding='utf-8'):
    #     ret = context.call('getSign', {'X-MS-STUB': md5_param})
    # return ret.get('X-Bogus')


def generateMsToken(length=107):
    """
    产生请求头部cookie中的msToken字段，其实为随机的107位字符
    :param length:字符位数
    :return:msToken
    """
    random_str = ''
    base_str = string.ascii_letters + string.digits + '=_'
    _len = len(base_str) - 1
    for _ in range(length):
        random_str += base_str[random.randint(0, _len)]
    return random_str


class DouyinLiveWebFetcher:
    
    def __init__(self, live_id):
        """
        直播间弹幕抓取对象
        :param live_id: 直播间的直播id，打开直播间web首页的链接如：https://live.douyin.com/261378947940，
                        其中的261378947940即是live_id
        """
        self.__ttwid = None
        self.__room_id = None
        self.live_id = live_id
        self.live_url = "https://live.douyin.com/"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                          "Chrome/120.0.0.0 Safari/537.36"
        self.db = None                  
    
    def start(self):
        self.dbconnect()
        self._connectWebSocket()

    def dbconnect(self):    
        try:
            self.db = MySQLHandler(**mysql_config)
            self.db.connect()
        except Exception as e:
            # 获取详细的错误堆栈信息
            error_info = traceback.format_exc()
            print(f"数据库连接发生异常: {type(e).__name__}, 详细错误信息:\n{error_info}")
            self.stop()
            raise
    def stop(self):
        self.ws.close()
        self.db.disconnect()    
    
    @property
    def ttwid(self):
        """
        产生请求头部cookie中的ttwid字段，访问抖音网页版直播间首页可以获取到响应cookie中的ttwid
        :return: ttwid
        """
        if self.__ttwid:
            return self.__ttwid
        headers = {
            "User-Agent": self.user_agent,
        }
        try:
            response = requests.get(self.live_url, headers=headers)
            response.raise_for_status()
        except Exception as err:
            print("【X】Request the live url error: ", err)
        else:
            self.__ttwid = response.cookies.get('ttwid')
            return self.__ttwid
    
    @property
    def room_id(self):
        """
        根据直播间的地址获取到真正的直播间roomId，有时会有错误，可以重试请求解决
        :return:room_id
        """
        if self.__room_id:
            return self.__room_id
        url = self.live_url + self.live_id
        headers = {
            "User-Agent": self.user_agent,
            "cookie": f"ttwid={self.ttwid}&msToken={generateMsToken()}; __ac_nonce=0123407cc00a9e438deb4",
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except Exception as err:
            print("【X】Request the live room url error: ", err)
        else:
            match = re.search(r'roomId\\":\\"(\d+)\\"', response.text)
            if match is None or len(match.groups()) < 1:
                print("【X】No match found for roomId")
            
            self.__room_id = match.group(1)
            
            return self.__room_id
    
    def _connectWebSocket(self):
        """
        连接抖音直播间websocket服务器，请求直播间数据
        """
        wss = ("wss://webcast5-ws-web-hl.douyin.com/webcast/im/push/v2/?app_name=douyin_web"
               "&version_code=180800&webcast_sdk_version=1.0.14-beta.0"
               "&update_version_code=1.0.14-beta.0&compress=gzip&device_platform=web&cookie_enabled=true"
               "&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32"
               "&browser_name=Mozilla"
               "&browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,"
               "%20like%20Gecko)%20Chrome/126.0.0.0%20Safari/537.36"
               "&browser_online=true&tz_name=Asia/Shanghai"
               "&cursor=d-1_u-1_fh-7392091211001140287_t-1721106114633_r-1"
               f"&internal_ext=internal_src:dim|wss_push_room_id:{self.room_id}|wss_push_did:7319483754668557238"
               f"|first_req_ms:1721106114541|fetch_time:1721106114633|seq:1|wss_info:0-1721106114633-0-0|"
               f"wrds_v:7392094459690748497"
               f"&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&endpoint=live_pc&support_wrds=1"
               f"&user_unique_id=7319483754668557238&im_path=/webcast/im/fetch/&identity=audience"
               f"&need_persist_msg_count=15&insert_task_id=&live_reason=&room_id={self.room_id}&heartbeatDuration=0")
        
        signature = generateSignature(wss)
        wss += f"&signature={signature}"
        
        headers = {
            "cookie": f"ttwid={self.ttwid}",
            'user-agent': self.user_agent,
        }
        self.ws = websocket.WebSocketApp(wss,
                                         header=headers,
                                         on_open=self._wsOnOpen,
                                         on_message=self._wsOnMessage,
                                         on_error=self._wsOnError,
                                         on_close=self._wsOnClose)
        try:
            self.ws.run_forever()
        except Exception:
            self.stop()
            raise
    
    def _wsOnOpen(self, ws):
        """
        连接建立成功
        """
        print("WebSocket connected.")
    
    def _wsOnMessage(self, ws, message):
        """
        接收到数据
        :param ws: websocket实例
        :param message: 数据
        """
        
        # 根据proto结构体解析对象
        package = PushFrame().parse(message)
        response = Response().parse(gzip.decompress(package.payload))
        
        # 返回直播间服务器链接存活确认消息，便于持续获取数据
        if response.need_ack:
            ack = PushFrame(log_id=package.log_id,
                            payload_type='ack',
                            payload=response.internal_ext.encode('utf-8')
                            ).SerializeToString()
            ws.send(ack, websocket.ABNF.OPCODE_BINARY)
        
        # 根据消息类别解析消息体
        for msg in response.messages_list:
            method = msg.method
            try:
                {
                    'WebcastChatMessage': self._parseChatMsg,  # 聊天消息
                    'WebcastGiftMessage': self._parseGiftMsg,  # 礼物消息
                    'WebcastLikeMessage': self._parseLikeMsg,  # 点赞消息
                    'WebcastMemberMessage': self._parseMemberMsg,  # 进入直播间消息
                    'WebcastSocialMessage': self._parseSocialMsg,  # 关注消息
                    'WebcastRoomUserSeqMessage': self._parseRoomUserSeqMsg,  # 直播间统计
                    'WebcastFansclubMessage': self._parseFansclubMsg,  # 粉丝团消息
                    'WebcastControlMessage': self._parseControlMsg,  # 直播间状态消息
                    'WebcastEmojiChatMessage': self._parseEmojiChatMsg,  # 聊天表情包消息
                    'WebcastRoomStatsMessage': self._parseRoomStatsMsg,  # 直播间统计信息
                    'WebcastRoomMessage': self._parseRoomMsg,  # 直播间信息
                    'WebcastRoomRankMessage': self._parseRankMsg,  # 直播间排行榜信息
                    'WebcastRoomStreamAdaptationMessage': self._parseRoomStreamAdaptationMsg,  # 直播间流配置
                }.get(method)(msg.payload)
            except Exception:
                pass
    
    def _wsOnError(self, ws, error):
        print("WebSocket error: ", error)
    
    def _wsOnClose(self, ws, *args):
        print("WebSocket connection closed.")
        file_path = f'live/{self.live_id}.txt'
        self.write_to_file(file_path,'close')
        

    def write_to_file(self,file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"内容2已成功写入 {file_path}")
        except Exception as e:
            print(f"写入2文件时出错: {e}")

    def _parseChatMsg(self, payload):
        """聊天消息"""
        message = ChatMessage().parse(payload)
        #print(message.user)
        user_name = message.user.nick_name
        user_id = message.user.id
        content = message.content
        print(f"【聊天msg】{user_name}: {content}")
        if self._check_keywords(content):
            tdata = self._transuser(message.user)
            if tdata:
                tdata['text'] = f"【聊天】: {content}"
                tdata['text'] = self.replace_special_chars(tdata['text'])
                tdata['type'] = '聊天'
                self.db.insert('craw_douyin_live_message',tdata)
            
        
    
    def _parseGiftMsg(self, payload):
        """礼物消息"""
        message = GiftMessage().parse(payload)
        #print(message.user)
        user_name = message.user.nick_name
        gift_name = message.gift.name
        gift_cnt = message.combo_count
        print(f"【礼物msg】{user_name} 送出了 {gift_name}x{gift_cnt}")
        tdata = self._transuser(message.user)
        if tdata:
                tdata['text'] = f"【礼物】送出了 {gift_name}x{gift_cnt}"
                tdata['text'] = self.replace_special_chars(tdata['text'])
                tdata['type'] = '礼物'
                self.db.insert('craw_douyin_live_message',tdata)
        
    
    def _parseLikeMsg(self, payload):
        '''点赞消息'''
        message = LikeMessage().parse(payload)
        #print(message.user)
        user_name = message.user.nick_name
        count = message.count
        print(f"【点赞msg】{user_name} 点了{count}个赞")
        tdata = self._transuser(message.user)
        if tdata:
                tdata['text'] = f"【点赞】点了{count}个赞"
                tdata['text'] = self.replace_special_chars(tdata['text'])
                tdata['type'] = '点赞'
                self.db.insert('craw_douyin_live_message',tdata)
        
    
    def _parseMemberMsg(self, payload):
        '''进入直播间消息'''
        message = MemberMessage().parse(payload)
        #print(message.user)
        user_name = message.user.nick_name
        user_id = message.user.id
        gender = ["女", "男"][message.user.gender]
        print(f"【进场msg】[{gender}]{user_name} 进入了直播间")
        # print(message.user)
        tdata = self._transuser(message.user)
        try:
            if tdata:
                    tdata['text'] = f"【进场】"
                    tdata['text'] = self.replace_special_chars(tdata['text'])
                    tdata['type'] = '进场'
                    self.db.insert('craw_douyin_live_message',tdata)
            
        except Exception as e:
            # 获取详细的错误堆栈信息
            # error_info = traceback.format_exc()
            # print(f"数据库连接发生异常: {type(e).__name__}, 详细错误信息:\n{error_info}")
            # self.stop()
            # raise
            pass
    
    def _parseSocialMsg(self, payload):
        '''关注消息'''
        message = SocialMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        print(f"【关注msg】{user_name} 关注了主播")
        tdata = self._transuser(message.user)
        if tdata:
                tdata['text'] = f"【关注】关注了主播"
                tdata['text'] = self.replace_special_chars(tdata['text'])
                tdata['type'] = '关注'
                self.db.insert('craw_douyin_live_message',tdata)
        
    
    def _parseRoomUserSeqMsg(self, payload):
        '''直播间统计'''
        message = RoomUserSeqMessage().parse(payload)
        current = message.total
        total = message.total_pv_for_anchor
        print(f"【统计msg】当前观看人数: {current}, 累计观看人数: {total}")
    
    def _parseFansclubMsg(self, payload):
        '''粉丝团消息'''
        message = FansclubMessage().parse(payload)
        content = message.content
        print(f"【粉丝团msg】 {content}")
    
    def _parseEmojiChatMsg(self, payload):
        '''聊天表情包消息'''
        message = EmojiChatMessage().parse(payload)
        #print(message.user)
        emoji_id = message.emoji_id
        user = message.user
        common = message.common
        default_content = message.default_content
        print(f"【聊天表情包id】 {emoji_id},user：{user},common:{common},default_content:{default_content}")
        tdata = self._transuser(user)
        if tdata:
                tdata['text'] = f"【表情包】 {emoji_id}"
                tdata['text'] = self.replace_special_chars(tdata['text'])
                tdata['type'] = '聊天表情包'
                self.db.insert('craw_douyin_live_message',tdata)
        
        
    
    def _parseRoomMsg(self, payload):
        message = RoomMessage().parse(payload)
        common = message.common
        room_id = common.room_id
        print(f"【直播间msg】直播间id:{room_id}")
        # print(message)
    
    def _parseRoomStatsMsg(self, payload):
        message = RoomStatsMessage().parse(payload)
        display_long = message.display_long
        print(f"【直播间统计msg】{display_long}")
        # print(message)
    
    def _parseRankMsg(self, payload):
        message = RoomRankMessage().parse(payload)
        ranks_list = message.ranks_list
        # print(f"【直播间排行榜msg】{ranks_list}")
        print(f"【直播间排行榜msg】")
        # print(f"【直播间排行榜msg】")
        userlist = []
        try:
            for rank in ranks_list:
                user = rank.user
                tdata = self._transuser(user)
                if tdata:
                        tdata['type'] = '直播间排行榜'
                        self.db.insert('craw_douyin_live_message',tdata)
        except Exception as e:
            # 获取详细的错误堆栈信息
            # error_info = traceback.format_exc()
            # print(f"发生异常: {type(e).__name__}, 详细错误信息:\n{error_info}")
            # self.stop()
            # raise
            pass


    
    def _parseControlMsg(self, payload):
        '''直播间状态消息'''
        message = ControlMessage().parse(payload)
        
        if message.status == 3:
            print("直播间已结束")
            self.stop()
    
    def _parseRoomStreamAdaptationMsg(self, payload):
        message = RoomStreamAdaptationMessage().parse(payload)
        adaptationType = message.adaptation_type
        print(f'直播间adaptation: {adaptationType}')
    def _transuser(self,user):
        try:
            # print(user.sec_uid)
            if not user.sec_uid:
                return {}
            sec_uid = 'https://www.douyin.com/user/' + user.sec_uid
            avatar = user.avatar_large.url_list_list[0] if user.avatar_large.url_list_list else ''
            tdata = {
                'liveid': self.live_id,
                'uid': user.id,
                'short_id': user.short_id,
                'nickname': user.nick_name,
                'signature': user.signature,
                'sec_uid': sec_uid,
                'avatar': avatar,
            }
            print(tdata)
            return tdata
            
        except Exception as e:
            # 获取详细的错误堆栈信息
            # error_info = traceback.format_exc()
            # print(f"发生异常: {type(e).__name__}, 详细错误信息:\n{error_info}")
            # self.stop()
            # raise
            pass
    def _check_keywords(self,content):
        return True
        keywords = ["加盟", "上样", "哪里", "联系"]
        for keyword in keywords:
            if keyword in content:
                return True
        return False   
    def replace_special_chars(self,input_string):
        # 定义正则表达式模式，包含英文标点
        pattern = r'[^a-zA-Z0-9\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef.,?!:;\'"()<>/\\-]'
        # 使用 re.sub() 方法替换匹配到的特殊字符为空字符串
        result = re.sub(pattern, '', input_string)
        return result 

    
