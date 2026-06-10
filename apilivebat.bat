@echo off

rem 设置 Python 解释器的路径，如果你已经将 Python 添加到系统环境变量中，可以直接使用 python
set PYTHON_PATH=D:\python\Python310\python.exe

rem 设置 Python 脚本所在的目录
set SCRIPT_DIR=D:\python\douyin

@REM 依次为每个 Python 脚本开启新的 cmd 窗口执行，每次执行后停顿 3 秒



@REM 直播间是否开启监听
start "Script 1" cmd /k %PYTHON_PATH% "%SCRIPT_DIR%\apilivelisten.py"
timeout /t 1

@REM 直播数据
start "Script 2" cmd /k %PYTHON_PATH% "%SCRIPT_DIR%\DouyinLiveWebFetcher-main\lives.py"
timeout /t 1

@REM 直播用户
start "Script 3" cmd /k %PYTHON_PATH% "%SCRIPT_DIR%\apiuserlive.py"

@REM 用户是否有直播
start "Script 4" cmd /k %PYTHON_PATH% "%SCRIPT_DIR%\apiuserhaslive.py"

echo 所有 Python 脚本执行完毕。

exit