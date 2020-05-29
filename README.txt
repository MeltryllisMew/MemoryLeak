case命名：CaseID+下划线分隔的进程名+描述.py
CaseID:英文数字下划线组合
进程名：因为python导入模块有格式要求，所以以_替代.，例如com_android_settings
描述：自定义，不要有+
例：MCR_24_102400+com_android_settings+WiFi开关.py

然后每5秒执行一次 subprocess
adb shell dumpsys meminfo com.xxx.xxx
结果以时间,KB格式存入CaseID+进程名.txt

执行2小时后，杀死case进程

