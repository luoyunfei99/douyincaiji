import time
from DrissionPage import ChromiumOptions, ChromiumPage

class ProxyManager:
    def __init__(self, extension_path = '',page = None):
        if page is None:
            # 初始化浏览器选项
            self.co = ChromiumOptions()
            # 添加SwitchyOmega扩展
            self.co.add_extension(extension_path)
            # 初始化页面
            self.page = ChromiumPage(self.co)
        else:
            self.page = page
        # SwitchyOmega选项页面URL
        self.switchyomega_options_url = "chrome-extension://padekgcemlokbadohgkifijomclgjgif/options.html"
        self.switchyomega_options_url_proxy = "chrome-extension://padekgcemlokbadohgkifijomclgjgif/options.html#!/profile/proxy"
        self.switchyomega_options_ui = "chrome-extension://padekgcemlokbadohgkifijomclgjgif/options.html#!/ui"
        
    def open_switchyomega_options(self):
        """打开SwitchyOmega选项页面"""
        self.page.get(self.switchyomega_options_url)
        time.sleep(2)  # 等待页面加载
    def open_switchyomega_options_proxy(self):
        """打开SwitchyOmega选项页面"""
        self.page.get(self.switchyomega_options_url_proxy)
        time.sleep(2)  # 等待页面加载
    def open_switchyomega_options_ui(self):
        """打开SwitchyOmega选项页面"""
        self.page.get(self.switchyomega_options_ui)
        time.sleep(2)  # 等待页面加载

    def set_proxy_profile_proxy(self, proxy_type, proxy_host, proxy_port, username=None, password=None):
        """添加新的代理配置文件，支持账号密码认证"""
        self.open_switchyomega_options_proxy()
        
        # 设置代理协议和服务器信息
        self._set_proxy_server(proxy_type, proxy_host, proxy_port)
        
        # 如果提供了用户名和密码，则设置认证信息
        if username and password:
            # 设置代理认证信息
            self._set_proxy_auth(username, password)
        
        # 保存设置
        self.page.ele('text:应用选项').click()
        time.sleep(1)

    def add_proxy_profile(self, profile_name, proxy_type, proxy_host, proxy_port, username=None, password=None):
        """添加新的代理配置文件，支持账号密码认证"""
        self.open_switchyomega_options()
        
        # 点击"新建情景模式"按钮
        self.page.ele('text:新建情景模式').click()
        time.sleep(1)
        
        # 输入配置文件名称
        self.page.ele('tag:input@name:profileNewName').input(profile_name)
        
        # 选择代理类型 - 改进定位方式
        proxy_type_mapping = {
            "HTTP": "FixedProfile",
            "SOCKS5": "FixedProfile",  # SOCKS5也使用FixedProfile，但需要在后续步骤中选择
            "AUTO": "SwitchProfile",
            "PAC": "PacProfile",
            "VIRTUAL": "VirtualProfile"
        }
        
        # 检查代理类型是否在映射中
        if proxy_type in proxy_type_mapping:
            profile_value = proxy_type_mapping[proxy_type]
            # 尝试多种定位方式
            try:
                # 先尝试使用更精确的定位
                radio_btn = self.page.ele(f'tag:input@name:profile-new-type@value:{profile_value}', timeout=5)
                radio_btn.click()
            except:
                # 如果失败，尝试使用包含文本的方式定位
                text_mapping = {
                    "FixedProfile": "代理服务器",
                    "SwitchProfile": "自动切换模式",
                    "PacProfile": "PAC情景模式",
                    "VirtualProfile": "虚情景模式"
                }
                
                if profile_value in text_mapping:
                    # 找到包含特定文本的label，然后找到其子元素input
                    label = self.page.ele(f'text:{text_mapping[profile_value]}').parent('tag:label')
                    if label:
                        label.ele('tag:input').click()
        
        # 点击"创建"按钮
        self.page.ele('text:创建').click()
        time.sleep(1)
        
        # 设置代理协议和服务器信息
        self._set_proxy_server(proxy_type, proxy_host, proxy_port)
        
        # 如果提供了用户名和密码，则设置认证信息
        if username and password:
            # 设置代理认证信息
            self._set_proxy_auth(username, password)
        
        # 保存设置
        self.page.ele('text:应用选项').click()
        time.sleep(1)



    def _set_proxy_server(self, proxy_type, proxy_host, proxy_port):
        """设置代理服务器信息"""
        # 找到代理服务器表格
        try:
            # 改进表格定位方式 - 先找到section，再找到table
            proxy_section = self.page.ele('tag:section@class:settings-group settings-group-fixed-servers')
            if proxy_section:
                proxy_table = proxy_section.ele('tag:table@class:fixed-servers')
                
                if proxy_table:
                    # 找到第一行(默认协议行)
                    default_row = proxy_table.eles('tag:tr')[1]  # 索引1是因为thead占了一行
                    
                    # 设置代理协议
                    proxy_protocol_mapping = {
                        "HTTP": "HTTP",
                        "HTTPS": "HTTPS",
                        "SOCKS4": "SOCKS4",
                        "SOCKS5": "SOCKS5"
                    }
                    
                    # 确保代理类型在映射中
                    if proxy_type in proxy_protocol_mapping:
                        protocol_name = proxy_protocol_mapping[proxy_type]
                        
                        # 找到代理协议下拉框并选择对应选项
                        protocol_select = default_row.eles('tag:td')[1].ele('tag:select')
                        protocol_select.select(protocol_name)
                        
                        # 等待输入框变为可编辑状态
                        time.sleep(0.5)
                        
                        # 找到服务器输入框，清空默认值，然后输入新值
                        server_input = default_row.eles('tag:td')[2].ele('tag:input')
                        server_input.clear()  # 清空默认值
                        server_input.input(proxy_host)
                        
                        # 找到端口输入框，清空默认值，然后输入新值
                        port_input = default_row.eles('tag:td')[3].ele('tag:input')
                        port_input.clear()  # 清空默认值
                        port_input.input(str(proxy_port))
                    else:
                        print(f"警告: 不支持的代理类型 {proxy_type}")
                else:
                    print("错误: 在section中找不到代理服务器表格")
            else:
                print("错误: 找不到代理服务器section")
        except Exception as e:
            print(f"设置代理服务器时出错: {e}")
    
    def _set_proxy_auth(self, username, password):
        """设置代理认证信息"""
        try:
            # 找到代理服务器表格
            proxy_section = self.page.ele('tag:section@class:settings-group settings-group-fixed-servers')
            if proxy_section:
                proxy_table = proxy_section.ele('tag:table@class:fixed-servers')
                
                if proxy_table:
                    # 找到第一行(默认协议行)
                    default_row = proxy_table.eles('tag:tr')[1]  # 索引1是因为thead占了一行
                    
                    # 点击认证按钮
                    auth_button = default_row.ele('tag:button@class:proxy-auth-toggle')
                    auth_button.click()
                    
                    # 等待认证对话框出现
                    time.sleep(0.5)
                    
                    # 找到用户名输入框，清空默认值，然后输入新值
                    # 用户名输入框没有name属性，通过ng-model定位
                    username_input = self.page.ele('tag:input@placeholder:用户名')
                    username_input.clear()
                    username_input.input(username)
                    
                    # 找到密码输入框，清空默认值，然后输入新值
                    password_input = self.page.ele('tag:input@name:password')
                    password_input.clear()
                    password_input.input(password)
                    
                    # 点击确定按钮
                    confirm_button = self.page.ele('text:保存更改')
                    confirm_button.click()
                    
                    # 等待对话框关闭
                    time.sleep(0.5)
                else:
                    print("错误: 在section中找不到代理服务器表格")
            else:
                print("错误: 找不到代理服务器section")
        except Exception as e:
            print(f"设置代理认证信息时出错: {e}")

    def switch_to_profile(self, profile_name):
        """切换到指定的代理配置文件"""
        try:
            # 打开SwitchyOmega选项页面
            self.open_switchyomega_options_ui()
            
            # 直接找到"初始情景模式"的下拉菜单
            dropdown = self.page.ele('tag:div@class:omega-profile-select')
            
            # 点击下拉菜单按钮
            dropdown_btn = dropdown.ele('tag:button@class:dropdown-toggle')
            dropdown_btn.click()
            
            # 等待下拉菜单展开
            time.sleep(0.5)
            
            # 查找目标配置文件
            target_profile = None
            
            # 尝试多种定位方式
            try:
                # 方式1: 通过文本精确匹配
                target_profile = dropdown.ele(f'text:{profile_name}')
            except:
                try:
                    # 方式2: 通过包含文本的a标签
                    target_profile = dropdown.ele(f'tag:a@text:{profile_name}')
                except:
                    try:
                        # 方式3: 通过包含文本的li标签
                        profiles = dropdown.eles('tag:li')
                        for profile in profiles:
                            if profile_name in profile.text:
                                target_profile = profile
                                break
                    except:
                        pass
            
            # 如果找到目标配置文件，则点击它
            if target_profile:
                try:
                    # 尝试直接点击找到的元素
                    target_profile.click()
                except:
                    try:
                        # 如果直接点击失败，尝试查找子元素a并点击
                        a_tag = target_profile.ele('tag:a')
                        a_tag.click()
                    except:
                        print(f"错误: 无法点击代理配置 {profile_name}")
                        return
                
                print(f"已切换到代理配置: {profile_name}")
            else:
                print(f"错误: 找不到代理配置 {profile_name}")
                # 关闭下拉菜单
                dropdown_btn.click()
                return
            
            # 保存设置
            self.page.ele('text:应用选项').click()
            time.sleep(1)
            # 关闭选项页面
            # self.page.close()
            time.sleep(1)
            tab = self.page.new_tab()
            tab.get("chrome-extension://padekgcemlokbadohgkifijomclgjgif/popup/index.html#")
            time.sleep(1)
            tab.ele(f'x://span[text()="{profile_name}"]').click()
            time.sleep(2)
        except Exception as e:
            print(f"切换代理配置文件时出错: {e}")
  
    def delete_proxy_profile(self, profile_name):
        """删除指定的代理配置文件"""
        self.open_switchyomega_options()
        
        # 找到要删除的配置文件
        profile_element = self.page.ele(f'text:{profile_name}')
        if profile_element:
            # 点击配置文件旁边的删除按钮
            profile_element.parent().ele('tag:button@text:×').click()
            time.sleep(1)
            
            # 确认删除
            self.page.ele('text:确定').click()
            time.sleep(1)
            
            # 保存设置
            self.page.ele('text:应用选项').click()
            time.sleep(1)
    
    def close(self):
        """关闭浏览器"""
        self.page.quit()