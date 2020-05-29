#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import datetime
import importlib
import multiprocessing
import subprocess
import xlsxwriter
import uiautomator2
import traceback

class Process(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        multiprocessing.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = multiprocessing.Pipe()
        self._exception = None

    def run(self):
        try:
            multiprocessing.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

class TestCaseRun:
    def __init__(self, caseName, seconds=5, hours=2):
        self.caseName = caseName
        self.seconds = seconds
        self.hours = hours
        self.caseNameList = self.caseName.split("+")
        self.id = self.caseNameList[0]
        self.process = ""
        self.module = ""
        self.d = ""
        self.args = "adb shell dumpsys meminfo "
        self.file = ""
    
    def run(self):
        if self.check():
            self.process = ".".join(self.caseNameList[1].split("_"))
            self.module = importlib.import_module(self.caseName)
            self.args = self.args + self.process
            self.setUp()
            try:
                p = Process(target=self.module.test)
                p.start()
                startTime = datetime.datetime.now()
                endTime = startTime + datetime.timedelta(seconds = self.hours * 3600)
                self.setFile()
                while True:
                    time.sleep(self.seconds)
                    m = subprocess.Popen(self.args, stdout=subprocess.PIPE, shell=True)
                    now = datetime.datetime.now()
                    temp = now.strftime("%H:%M:%S")
                    result = (endTime - now).total_seconds()
                    if result > 0:
                        try:
                            out, err = m.communicate(timeout=2)
                            m.kill()
                        except subprocess.TimeoutExpired:
                            m.kill()
                            out, err = m.communicate()
                        kb = self.outMethod(out)
                        with open(self.file, "a", encoding="utf-8")as f:
                            f.write(temp + "," + kb + "\n")
                        if p.exception:
                            print(self.caseName, "测试用例执行异常，即将分析现有数据")
                            break
                    else:
                        break
                p.kill()
                self.tearDown()
            except:
                self.tearDown()
       
            
    def check(self):
        if len(self.caseNameList) == 3 and re.match(r"^[a-z_]+$", self.caseNameList[1]):
            return True
        else:
            print(self.caseName, "测试用例命名异常")
    
    def setUp(self):
        self.d = uiautomator2.connect()
        self.d.screen_on()
        print(self.caseName, "开始执行")

    def tearDown(self):
        self.d.app_stop_all()
        print(self.caseName, "执行完毕，分析中……")
        self.xlsxMethod()
        print(self.caseName, "分析完毕")

    def outMethod(self, out):
        list_outs = out.decode("utf-8").split("\n")
        for i in list_outs:
            if i.strip()[:5] == "TOTAL":
                kb = i.strip().split()[1]
                break
        return kb

    def setFile(self):
        self.file = self.id + "+" + self.process + ".txt"

    def setData(self):
        try:
            with open(self.file, encoding="utf-8")as g:
                data = g.readlines()
            return data
        except FileNotFoundError:
            print("内存数据未正确处理")
            return False

    def xlsxMethod(self):
        data = self.setData()
        if data:
            workbook = xlsxwriter.Workbook(os.path.splitext(self.file)[0] + ".xlsx")
            worksheet = workbook.add_worksheet(self.process)
            positionTime = "A"
            positionMeminfo = chr(ord(positionTime) + 1)
            positionChart = chr(ord(positionTime) + 3)
            for i in range(len(data)):
                tempTime = data[i].strip().split(",")[0]
                tempMeminfo = int(data[i].strip().split(",")[1])
                worksheet.write(positionTime + str(i+1), tempTime)
                worksheet.write(positionMeminfo + str(i+1), tempMeminfo)
            line_chart = workbook.add_chart({"type": "line"})
            line_chart.height = 600
            line_chart.width = 960
            categories = "=" + self.process + "!$" + positionTime + "$1:$" + positionTime + "$"
            values = "=" + self.process + "!$" + positionMeminfo + "$1:$" + positionMeminfo + "$"
            line_chart.add_series({
                "categories": categories + str(len(data)),
                "values": values + str(len(data))
            })
            worksheet.insert_chart(positionChart + "1", line_chart)
            workbook.close()
