import tkinter as tk
import subprocess
import sys
import threading
import json
import os
import time
from tkinter import scrolledtext, messagebox, ttk, filedialog, Listbox, Frame, Label, Entry, Button, Scrollbar
import queue
import webbrowser
import ast
import logging


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger('ScriptRunnerApp')


class ScriptRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("飞哥抖音数据抓取工具 v1.0")
        self.root.geometry("1400x450")
        self.root.resizable(True, True)

        # 设置中文字体支持
        self.font = ('SimHei', 9)
        self.small_font = ('SimHei', 8)
        self.bold_font = ('SimHei', 9, 'bold')

        # 配置文件路径
        self.config_dir = self.get_app_config_dir()
        self.config_file = self.get_resource_path("script_configs.json")
        self.proxy_config_file = self.get_resource_path("proxy.json")
        self.ip_list_file = self.get_resource_path("ip.json")
        self.current_proxy_file = self.get_resource_path("nowproxy.json")
        self.pre_proxy_file = self.get_resource_path("preproxy.json")

        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)

        # 存储脚本配置
        self.script_configs = self.load_script_configs()

        # 生成web界面URL
        self.weburl = self.get_resource_path('html/douyin/index.html')

        # 创建界面
        self.create_widgets()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_app_config_dir(self):
        """获取应用程序配置目录"""
        try:
            # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        except Exception:
            # 正常的开发环境
            base_path = os.path.dirname(os.path.abspath(__file__))

        # 配置目录 - 确保与应用程序在同一目录下
        config_dir = os.path.join(base_path, "config")
        return config_dir

    def get_resource_path(self, relative_path):
        """获取资源的绝对路径，支持打包后的环境"""
        try:
            # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        except Exception:
            # 正常的开发环境
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, relative_path)

    def on_close(self):
        """关闭窗口前停止所有脚本"""
        logger.info("关闭应用程序，停止所有脚本...")
        self.root.destroy()

    def load_script_configs(self):
        """加载脚本配置，若无配置文件则使用默认配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 默认配置 - 使用相对路径
                default_configs = [
                    {"name": "web界面服务", "path": "apiserver.py", "desc": "web界面服务", "args": ""},
                    {"name": "IP白名单", "path": "ipwhite.py", "desc": "IP白名单管理", "args": ""},
                    {"name": "代理ip获取", "path": "proxy.py", "desc": "代理IP获取服务", "args": ""},
                    {"name": "视频留言实时监听", "path": "douyin_comment.py", "desc": "实时监听视频留言",
                     "args": "-port 9111 -datapath tmp/googledata/videolisten -useproxy 1"},
                    {"name": "视频留言周期抓取", "path": "douyin_commment_zhouqi.py", "desc": "周期性视频留言抓取",
                     "args": "-port 9112 -datapath tmp/googledata/videozhouqi -useproxy 1"},
                    {"name": "留言主页抓取", "path": "douyin_video_user.py", "desc": "留言用户主页抓取",
                     "args": "-port 9113 -datapath tmp/googledata/videouser -useproxy 1"},
                    {"name": "抖音主页抓取", "path": "douyin_hao.py", "desc": "抖音账号主页信息抓取",
                     "args": "-port 9114 -datapath tmp/googledata/hao -useproxy 1"},
                    {"name": "历史视频留言抓取", "path": "douyin_comment_history.py", "desc": "历史视频留言抓取",
                     "args": "-port 9115 -datapath tmp/googledata/videohistory -useproxy 1"},
                    {"name": "历史视频留言主页抓取", "path": "douyin_comment_history_cover.py",
                     "desc": "历史视频留言主页抓取",
                     "args": "-port 9116 -datapath tmp/googledata/userhistory -useproxy 1"},
                    {"name": "直播间自动抓取", "path": "DouyinLiveWebFetcher-main/lives.py", "desc": "直播间自动抓取",
                     "args": ""},
                    {"name": "直播用户抓取", "path": "douyin_live_user.py",
                     "desc": "直播间用户列表抓取",
                     "args": "-port 9117 -datapath tmp/googledata/liveuser -useproxy 1"},
                    {"name": "指定直播id用户抓取", "path": "douyin_live_user.py",
                     "desc": "直播间用户列表抓取",
                     "args": "-port 9117 -datapath tmp/googledata/liveuser -useproxy 1 -liveid"},
                    {"name": "直播间手动抓取", "path": "DouyinLiveWebFetcher-main/main.py", "desc": "直播间手动抓取，参数输入直播id",
                     "args": ""},
                    {"name": "关键词抓取", "path": "douyin_keyword.py", "desc": "关键词非广告视频抓取",
                     "args": "-port 9118 -datapath tmp/googledata/videohistory -useproxy 1"},
                    {"name": "抖音主页粉丝抓取", "path": "douyin_user_fans.py", "desc": "抖音主页粉丝列表抓取",
                     "args": "-port 9119 -datapath tmp/googledata/videohistory -useproxy 1"},
                    {"name": "直播间监听", "path": "douyin_live_listen.py", "desc": "每分钟检查一直监听的直播间是否开播",
                     "args": "-port 9120 -datapath tmp/googledata/videohistory -useproxy 1"} 
                ]
                self.save_script_configs(default_configs)
                return default_configs
        except Exception as e:
            logger.error(f"加载脚本配置失败: {str(e)}")
            messagebox.showerror("配置加载错误", f"加载脚本配置失败: {str(e)}")
            return []

    def save_script_configs(self, configs):
        """保存脚本配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
            logger.info("脚本配置已保存")
        except Exception as e:
            logger.error(f"保存脚本配置失败: {str(e)}")
            messagebox.showerror("配置保存错误", f"保存脚本配置失败: {str(e)}")

    def create_widgets(self):
        """创建主界面组件"""
        # 创建顶部工具栏
        toolbar = ttk.Frame(self.root, style='Toolbar.TFrame')
        toolbar.pack(fill=tk.X, padx=5, pady=3, ipady=5)

        # 工具栏按钮
        ttk.Button(
            toolbar, text="刷新配置", command=self.refresh_configs,
            width=10, style='Refresh.TButton'
        ).pack(side=tk.LEFT, padx=3)

        ttk.Button(
            toolbar, text="保存配置", command=self.save_configs,
            width=10, style='Save.TButton'
        ).pack(side=tk.LEFT, padx=3)

        ttk.Button(
            toolbar, text="全部运行", command=self.run_all_scripts,
            width=10, style='Run.TButton'
        ).pack(side=tk.LEFT, padx=3)

        ttk.Button(
            toolbar, text="添加数据", command=self.open_url_in_browser,
            width=10, style='Add.TButton'
        ).pack(side=tk.RIGHT, padx=3)

        # 创建主选项卡控件
        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 为每个脚本创建选项卡
        for i, config in enumerate(self.script_configs):
            frame = ttk.Frame(self.notebook, style='TabFrame.TFrame')
            self.notebook.add(frame, text=config["name"])
            self.create_script_tab(frame, i, config)

        # 配置主题
        self.setup_theme()

    def setup_theme(self):
        """设置界面主题"""
        if hasattr(self.root, 'tk') and 'clam' in self.root.tk.call('ttk::themes'):
            self.root.tk.call('ttk::setTheme', 'clam')

        # 创建自定义样式
        style = ttk.Style()

        # 美化按钮样式
        style.configure('Refresh.TButton', foreground='black', background='#f0f0f0', font=self.bold_font)
        style.map('Refresh.TButton',
                  background=[('active', '#e0e0e0'), ('pressed', '#d0d0d0')],
                  foreground=[('active', '#333333')])

        style.configure('Save.TButton', foreground='black', background='#f0f0f0', font=self.bold_font)
        style.map('Save.TButton',
                  background=[('active', '#e0e0e0'), ('pressed', '#d0d0d0')],
                  foreground=[('active', '#333333')])

        style.configure('Run.TButton', foreground='white', background='#4CAF50', font=self.bold_font)
        style.map('Run.TButton',
                  background=[('active', '#45a049'), ('pressed', '#3d8b40')],
                  foreground=[('active', 'white')])

        style.configure('Add.TButton', foreground='white', background='#2196F3', font=self.bold_font)
        style.map('Add.TButton',
                  background=[('active', '#1976D2'), ('pressed', '#1565C0')],
                  foreground=[('active', 'white')])

        # 美化选项卡样式
        style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
        style.configure('TNotebook.Tab', font=self.bold_font, padding=[10, 5], background='#e0e0e0',
                        foreground='#333333', borderwidth=1)
        style.map('TNotebook.Tab',
                  background=[('selected', '#ffffff'), ('active', '#d0d0d0')],
                  foreground=[('selected', '#2196F3'), ('active', '#333333')],
                  expand=[('selected', [2, 2, 2, 0])])

        # 美化框架样式
        style.configure('TabFrame.TFrame', background='#ffffff')
        style.configure('Toolbar.TFrame', background='#e8e8e8')

    def create_script_tab(self, parent, script_index, config):
        """创建单个脚本的选项卡界面"""
        # 脚本基本信息框架
        info_frame = ttk.LabelFrame(parent, text=f"脚本信息", padding=5)
        info_frame.pack(fill=tk.X, pady=5)

        ttk.Label(info_frame, text="脚本名称:", font=self.bold_font).grid(row=0, column=0, sticky=tk.W, padx=3, pady=3)
        ttk.Label(info_frame, text=config["name"], font=self.font).grid(row=0, column=1, sticky=tk.W, padx=3, pady=3)

        ttk.Label(info_frame, text="脚本描述:", font=self.bold_font).grid(row=1, column=0, sticky=tk.W, padx=3, pady=3)
        ttk.Label(info_frame, text=config["desc"], font=self.font).grid(row=1, column=1, sticky=tk.W, padx=3, pady=3)

        # 脚本路径设置框架
        path_frame = ttk.LabelFrame(parent, text="脚本路径", padding=5)
        path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(path_frame, text="路径:", font=self.bold_font).grid(row=0, column=0, sticky=tk.W, padx=3, pady=3)
        path_var = tk.StringVar(value=config["path"])
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=50, font=self.font)
        path_entry.grid(row=0, column=1, sticky=tk.W, padx=3, pady=3)

        ttk.Button(
            path_frame, text="浏览...",
            command=lambda idx=script_index: self.browse_script_path(idx, path_var),
            width=8, style='Tool.TButton'
        ).grid(row=0, column=2, padx=3, pady=3)

        # 命令行参数设置
        ttk.Label(path_frame, text="参数:", font=self.bold_font).grid(row=1, column=0, sticky=tk.W, padx=3, pady=3)
        args_var = tk.StringVar(value=config.get("args", ""))
        args_entry = ttk.Entry(path_frame, textvariable=args_var, width=100, font=self.font)
        args_entry.grid(row=1, column=1, sticky=tk.W, padx=3, pady=3)
        ttk.Label(path_frame, text="(空格分隔多个参数)", font=self.small_font, foreground="gray").grid(row=1, column=2,
                                                                                                       sticky=tk.W,
                                                                                                       padx=3, pady=3)

        # 保存对控件变量的引用
        self.script_vars = getattr(self, 'script_vars', {})
        self.script_vars[script_index] = {
            'path_var': path_var,
            'args_var': args_var
        }

        # 运行按钮
        run_btn = ttk.Button(
            parent, text="运行", command=lambda idx=script_index: self.run_script_in_cmd(idx),
            width=8, style='Accent.TButton'
        )
        run_btn.pack(side=tk.LEFT, padx=3, pady=5)

    def browse_script_path(self, script_index, path_var):
        """浏览脚本文件路径"""
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            # 获取相对路径
            try:
                base_path = self.get_resource_path('')
                rel_path = os.path.relpath(file_path, base_path)
                path_var.set(rel_path)
            except ValueError:
                # 如果无法获取相对路径，使用绝对路径
                path_var.set(file_path)

    def run_script_in_cmd(self, script_index):
        """在cmd窗口中运行指定索引的脚本"""
        path_var = self.script_vars[script_index]['path_var']
        args_var = self.script_vars[script_index]['args_var']

        script_path = self.get_resource_path(path_var.get())
        args = args_var.get().split()

        cmd = [sys.executable, script_path] + args
        cmd_str = " ".join(cmd)

        try:
            subprocess.Popen(f'start cmd /k "{cmd_str}"', shell=True)
        except Exception as e:
            logger.error(f"启动脚本时发生异常: {str(e)}")
            messagebox.showerror("启动脚本错误", f"启动脚本时发生异常: {str(e)}")

    def run_all_scripts(self):
        """运行所有脚本"""
        logger.info("运行所有脚本...")
        for i in range(len(self.script_configs)):
            self.run_script_in_cmd(i)

    def refresh_configs(self):
        """刷新脚本配置"""
        logger.info("刷新脚本配置...")
        self.script_configs = self.load_script_configs()
        # 重新创建选项卡
        for i in range(self.notebook.index(tk.END)):
            self.notebook.forget(i)
        for i, config in enumerate(self.script_configs):
            frame = ttk.Frame(self.notebook, style='TabFrame.TFrame')
            self.notebook.add(frame, text=config["name"])
            self.create_script_tab(frame, i, config)

    def save_configs(self):
        """保存所有脚本配置"""
        logger.info("保存脚本配置...")
        new_configs = []
        for i, config in enumerate(self.script_configs):
            new_config = {
                "name": config["name"],
                "path": self.script_vars[i]['path_var'].get(),
                "desc": config["desc"],
                "args": self.script_vars[i]['args_var'].get()
            }
            new_configs.append(new_config)
        self.save_script_configs(new_configs)
        messagebox.showinfo("保存成功", "脚本配置已保存")

    # 添加缺失的方法
    def open_url_in_browser(self):
        """在浏览器中打开web界面"""
        try:
            if os.path.exists(self.weburl):
                webbrowser.open(f'file://{self.weburl}')
                logger.info(f"在浏览器中打开web界面: {self.weburl}")
            else:
                logger.error(f"web界面文件不存在: {self.weburl}")
                messagebox.showerror("文件不存在", f"web界面文件不存在:\n{self.weburl}")
        except Exception as e:
            logger.error(f"打开web界面时发生异常: {str(e)}")
            messagebox.showerror("打开web界面错误", f"打开web界面时发生异常:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptRunnerApp(root)
    root.mainloop()