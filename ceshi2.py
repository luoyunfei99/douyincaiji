from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
import time
import re
from my_sql import MySQLHandler
import random
import cfun
import datetime
import sys
from config.mysql_config import mysql_config

if __name__ == '__main__':
    data = {
        'title': '测试',
        'phone': '13888888883',
        'douyin_url': 'https://www.douyin.com/user/MS4wLjABAAAA0iN56oT8I2MX46lfV8hLz0O8T8bA9vOyMwfW_SBdRl52kVadSFavaKl_ElLa419r?from_tab_name=main',
        'douyin_inputtime': '2026-04-25 09:05:05',
        'hangye':'门窗'
    }
    cfun.baoming(data)


        
            


