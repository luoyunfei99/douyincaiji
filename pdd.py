from DrissionPage import Chromium, ChromiumPage, ChromiumOptions
import time
import cfun
import sys
import random
# 测试


def getdetail(page, url):
    tab = page.new_tab()
    # listen_url2 = 'douyin.com/aweme/v1/web/user/profile/other/'
    # tab.listen.start(listen_url2)  # 开始监听
    time.sleep(1)
    flag = tab.get(url)
    if not flag:
        return False
    time.sleep(1)

    return True


if __name__ == '__main__':
    args = cfun.parse_arguments()
    i = 0
    # 慢速模式
    is_slow = 1
    while i == 0:
        try:
            # 定期重置监听
            # reset_listenstatus(db)
            pid = 0
            tmpinfo = None
            tmpinfo = [
                {'url': "https://mobile.yangkeduo.com/goods.html?goods_id=597300248710&uin=I6GSE6UJQCXMY3E427GJAQJGOY_GEXDA"}
                ]
            if not tmpinfo:
                if i == 0:
                    print('没有要操作的数据')
                time.sleep(60)

            else:
                tpage = cfun.getGoolePage(
                    args.port, args.datapath, args.useproxy)
                for tdata in tmpinfo:
                    if is_slow:
                        time.sleep(random.randint(3, 5))
                    url = tdata['url']
                    print(url+'\n')
                    rs = getdetail(tpage, url)
                    if rs:
                        print('抓取了')
                    else:
                        # tpage.quit()
                        break
                # tpage.quit()
            time.sleep(1)
            i += 1
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"发生异常: {exc_type.__name__}, 错误信息: {exc_value}")
            time.sleep(10)
            pass
