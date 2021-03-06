#code from www.361way.com
#coding: utf-8
import time
import os
import socket
import urllib2
import json

class alarmhandler(object):
    def __init__(self):
        self.url = "https://oapi.dingtalk.com/robot/send?access_token=80ab5cb49bb8b09ed1d5119289ea651461546b7670caffb75a98e3384f81d007"
        self.file = '/home/ubuntu/config.py'
        self.logfile = "/home/ubuntu/log.py"  # 定义日志目录
        self.list_process =  self.init_file()
        self.time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


    # 定义日志
    def log(self,logfile, content):
        f = open(logfile, 'a')
        f.write(time.strftime("\n%Y-%m-%d %H:%M:%S   ") + content)
        f.flush()
        f.close()

    def init_file(self):
        with open(self.file, "r") as f:  # 写入日志文件
            process_list = f.readlines()
        return process_list

    def isRunning(self,process_name):  # 检查进程是否存在，存在为True，不存在为False
        try:
            process = len(os.popen('ps axu | grep "' + process_name + '" | grep -v grep | grep root ').readlines())
            if process >= 1:
                return True
            else:
                return False
        except:
            print("Chect process ERROR!!!")
            return False

    def startProcess(self,process_script):  # 启动进程脚本，启动成功返回0，不成功返回其他为False
        try:
            result_code = os.system(process_script)
            if result_code == 0:
                return True
            else:
                return False
        except:
            print("Process start Error!!!")
            return False
    def process_check(self):
        with open(self.logfile, 'a') as f:
            f.write('-----------------------------------------\n')
        for process in  self.list_process:
            process_name = process.split(":")[0].strip()  # 定义进程名称
            process_script = process.split(":")[1].strip()  # 定义启动脚本
            isrunning = self.isRunning(process_name)  # 运行检查进程
            hostname = socket.gethostname()
            ipList = socket.gethostbyname_ex(hostname)
            cmd = []
            cmd.append(ipList[-1][-1])
            if isrunning == False:  # 如果进程不存在
                content = process_name + "     ERROR \n"  # 把这条字符串追加到log日志文件
                self.log(self.logfile, content)  # 写入日志
                data = {
                            "msgtype": "markdown",
                            "markdown": {
                                "title": "监控信息：\n",
                                "text": "#### %s \n" % self.time_now +
                                        "> #### 服务器：%s \n\n" % cmd +
                                        "> #### 服务名： %s \n\n" % process_name +
                                        "> ##### 状态: 进程崩溃 \n" +
                                        "> #### 正在尝试重新启动"
                            },
                            "at": {
                                "isAtAll": True,
                            },
                        }
                self.run(data)
                print("第一次发送信息")
                isstart = self.startProcess(process_script)  # 执行启动脚本函数，接收最后的返回值
                print(isstart)
                if isstart == True:  # 如果返回值是True，进程重启成功
                    content = process_name + "   restart  SUCCESS \n"  # 追加这条字符串到日志
                    self.log(self.logfile, content)  # 写入日志
                    data ={
                                "msgtype": "markdown",
                                "markdown": {
                                    "title": "监控信息：\n",
                                    "text": "#### %s \n" % self.time_now +
                                            "> #### 服务器：%s \n\n" % cmd +
                                            "> #### 服务名： %s \n\n" % process_name +
                                            "> ##### 状态: 进程存在 \n" +
                                            "> #### 进程重启成功"
                                },
                                "at": {
                                    "isAtAll": True,
                                },
                            }
                    self.run(data)
                    print("第二次发送信息")
            else:
                content = process_name + "    running \n"
                self.log(self.logfile, content)
    def run(self,data):
        req = urllib2.Request(self.url, json.dumps(data))  # 需要是json格式的参数
        req.add_header('Content-Type', 'application/json')  # 要非常注意这行代码的写法
        response = urllib2.urlopen(req)
        result = json.loads(response.read())
if __name__ == '__main__':
    vc = alarmhandler()
    vc.process_check()
