@echo off

rem 设置 Python 解释器的路径，如果你已经将 Python 添加到系统环境变量中，可以直接使用 python
@REM set PYTHON_PATH=D:\lyf\python\python.exe

rem 设置 Python 脚本所在的目录
@REM set SCRIPT_DIR=D:\lyf\douyin

start "Script 1" cmd /k python "gui_button_run_script.py"

echo 所有 Python 脚本执行完毕。

exit