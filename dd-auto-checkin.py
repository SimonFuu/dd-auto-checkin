# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Simon Fu
# www.fushupeng.com
# contact@fushupeng.com
# Life is short, and world is wide.
import configparser
import datetime
import json
import os
import random
import subprocess
import threading
import time
from queue import Queue

import paho.mqtt.client as mqtt


def with_open_close_dd(func):
    def wrapper(self, *args, **kwargs):
        print("打开DD")
        # 开启新线程
        operation_list = [self.adb_power_btn, self.adb_unlock, self.adb_open_dd]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
        time.sleep(20)
        print("打开DD成功")
        print("打开打卡界面")
        operation_list = [self.adb_tap_work_tab, self.adb_tap_checkin_func]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
        time.sleep(20)
        print("打开打卡页面成功")
        # 包装函数
        func(self, *args, **kwargs)
        print("关闭DD")
        operation_list = [self.adb_close_dd, self.adb_power_btn]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        print("关闭DD成功")
    return wrapper


class CheckIn:
    def __init__(self, config):
        # 电源键
        adb_path = config.get('adb', 'path')
        unlock_towards = config.get('screen', 'unlock_towards')
        screen_h = int(config.get('screen', 'height'))
        screen_w = int(config.get('screen', 'width'))
        if unlock_towards == 'horizon':
            # 水平方向解锁
            start_x = screen_w * 5 / 100
            start_y = screen_h * 50 / 100
            end_x = screen_w * 95 / 100
            end_y = screen_h * 50 / 100
        else:
            # 竖直方向
            start_x = screen_w * 50 / 100
            start_y = screen_h * 60 / 100
            end_x = screen_w * 50 / 100
            end_y = screen_h * 90 / 100
        # 电源按钮
        self.adb_power_btn = '"%sadb" shell input keyevent 26' % adb_path
        # 解锁屏幕
        self.adb_unlock = '%sadb shell input swipe %s %s %s %s' % (adb_path, start_x, start_y, end_x, end_y)
        # 打开钉钉
        self.adb_open_dd = '%sadb shell monkey -p com.alibaba.android.rimet -c android.intent.category.LAUNCHER 1' % adb_path
        # 关闭钉钉
        self.adb_close_dd = '%sadb shell am force-stop com.alibaba.android.rimet' % adb_path
        # 屏幕截图
        self.adb_screen_cap = '%sadb shell screencap -p sdcard/screen.png' % adb_path
        # 删除截图
        self.adb_remove_screen_cap = '%sadb shell rm -r sdcard/screen.png' % adb_path
        # 拉取截图
        # self.adb_pull_screen_cap = '%sadb pull sdcard/screen.png %s' % (adb_path, config.get('screen', 'local_path'))
        self.adb_pull_screen_cap = '%sadb pull sdcard/screen.png %s' % (adb_path, os.getcwd())
        # 点击work tab
        self.adb_tap_work_tab = '%sadb shell input tap %s' % (adb_path, config.get("screen", "work_tab"))
        # 点击签到 Function
        self.adb_tap_checkin_func = '%sadb shell input tap %s' % (adb_path, config.get("screen", "checkin_func"))
        # 点击签到 btn
        self.adb_tap_checkin = '%sadb shell input tap %s' % (adb_path, config.get("screen", "checkin_btn"))
        # 点击签退 btn
        self.adb_tap_checkout = '%sadb shell input tap %s' % (adb_path, config.get("screen", "checkout_btn"))
        # 返回桌面
        self.adb_to_desktop = '%sadb shell input keyevent 3' % adb_path

    @with_open_close_dd
    def check(self, action):
        action_list = []
        # if action == 'checkin':
        #     action_list.append(self.adb_tap_checkin)
        # else:
        #     action_list.append(self.adb_tap_checkout)
        action_list.append(self.adb_screen_cap)
        action_list.append(self.adb_pull_screen_cap)
        for item in action_list:
            process = subprocess.Popen(item, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)


def random_delay():
    """
    自动延迟时间 10 - 300秒
    :return: 延迟时间 10 - 300 秒
    """
    return random.randint(10, 300)


def is_weekend():
    """
    周末判断
    :return:
    """
    return False


def time_check(now, conf):
    now_time = now.strftime('%H:%M')
    if now_time == '00:00' or now_time == '12:00':
        global checked
        checked = False
    if checked:
        return False
    else:
        if now_time == conf.get('check_time', 'checkin'):
            return 'checkin'
        elif now_time == conf.get('check_time', 'checkout'):
            return 'checkout'
        else:
            return False


def checkin_main():
    """
    启动签到线程
    :return:
    """
    global config
    global checked
    global checking
    while 1:
        now = datetime.datetime.now()
        check_action = time_check(now, config)
        if check_action:
            # 触发DD打卡
            if not checking:
                checking = True
                delay = random_delay()
                print("准备进行打卡从奥做，延迟 %s 后执行" % delay)
                time.sleep(delay)
                print("%s 开始执行打卡操作" % datetime.datetime.now())
                dd = CheckIn(config)
                dd.check(check_action)
                print("%s 打卡完成" % datetime.datetime.now())
                checked = True
                checking = False
        time.sleep(0.5)


def manual_check():
    global queue
    global config
    while 1:
        time.sleep(0.05)
        item = queue.get()
        if item is None:
            continue
        else:
            print("manual check %s" % item)
            dic = json.loads(item)
            dd = CheckIn(config)
            dd.check(dic['action'])
            queue.task_done()


def on_message(client, userdata, message):
    global queue
    print("on message %s %s" % (message.topic, message.payload))
    queue.put(message.payload)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def service_main():
    """
    启动服务线程，用于与服务端通信，接受服务端返回的命令
    :return:
    """
    global config
    global queue
    client = mqtt.Client(config.get('mqtt', 'uid'))
    client.username_pw_set(config.get('mqtt', 'username'), config.get('mqtt', 'password'))
    client.will_set(config.get('mqtt', 'will_topic'), json.dumps({'id': config.get('mqtt', 'uid')}))
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.get('mqtt', 'server'), int(config.get('mqtt', 'port')), 60)
    client.subscribe(config.get('mqtt', 'recv_topic') % config.get('mqtt', 'uid'))
    client.loop_forever()


def main():
    print('开始运行，准备启动子线程')
    checkin_thread = threading.Thread(target=checkin_main, name='CheckinThread')
    service_thread = threading.Thread(target=service_main, name='ServiceThread')
    manual_check_thread = threading.Thread(target=manual_check, name='ManualCheckThread')
    checkin_thread.start()
    service_thread.start()
    manual_check_thread.start()
    checkin_thread.join()
    service_thread.join()
    manual_check_thread.join()


if __name__ == '__main__':
    checked = False
    checking = False
    queue = Queue(1024)
    config = configparser.ConfigParser(allow_no_value=False)
    config.read(os.path.dirname(__file__).replace('\\', '/') + "/config.cfg")
    main()
