#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import TestCaseRun

def main():
    path = r"D:\MemoryLeak"
    os.chdir(path)
    with open("config.json")as f:
        data = json.load(f)
    try:
        seconds = data["dumpsys_meminfo_seconds"]
        hours = data["case_run_hours"]
    except:
        print("配置文件错误")
    casePath = os.path.join(os.getcwd(), "TestCase")
    sys.path.append(casePath)
    os.system("python -m uiautomator2 init")
    #os.chdir(r"D:\MemoryLeak\TestResult")
    os.chdir(os.path.join(os.getcwd(), "TestResult"))
    for i in os.listdir(casePath):
        if i[-2:] == "py":
            caseName = os.path.splitext(i)[0]
            t = TestCaseRun.TestCaseRun(caseName, seconds, hours)
            t.run()

if __name__ == '__main__':
    main()
