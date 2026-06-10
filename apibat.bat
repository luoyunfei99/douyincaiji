@echo off

rem 设置 Python 解释器的路径，如果你已经将 Python 添加到系统环境变量中，可以直接使用 python
set PYTHON_PATH=D:\python\Python310\python.exe

rem 设置 Python 脚本所在的目录
set SCRIPT_DIR=D:\python\douyin

@REM 依次为每个 Python 脚本开启新的 cmd 窗口执行，每次执行后停顿 3 秒



@REM 视频留言
start "Script 1" cmd /k %PYTHON_PATH% "%SCRIPT_DIR%\apicommentyou.py"
timeout /t 1

@REM 抖音主页
start "Script 2" cmd /k %PYTHON_PATH% "%SCRIPT_DIR%\apiuser.py"
timeout /t 1

@REM 抖音主页作品
start "Script 3" cmd /k %PYTHON_PATH% "%SCRIPT_DIR%\douyin_listen_hao.py"


echo 所有 Python 脚本执行完毕。

exit