# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Simon Fu
# www.fushupeng.com
# contact@fushupeng.com
# Life is short, and world is wide.
import random


class CheckIn:
    def __init__(self, config):
        # 电源键
        adb_path = config.get('adb', 'path')
        self.adb_power_btn = '"%s\\adb" shell input keyevent 26' % adb_path
        # 打开钉钉
        self.adb_open_dd = ''
        # 关闭钉钉
        self.adb_close_dd = ''
        # 屏幕截图
        self.adb_screen_cap = ''
        # 删除截图
        self.adb_remove_screen_cap = ''
        # 拉取截图
        self.adb_pull_screen_cap = ''
        # 点击work tab
        self.adb_tap_work_tab = ''
        # 点击签到 Function
        self.adb_tap_checkin_func = ''
        # 点击签到 btn
        self.adb_tap_checkin = ''
        # 点击签退 btn
        self.adb_tap_checkout = ''


    def open_dd(self):
        pass

    def close_dd(self):
        pass

    def open_checkin_function(self):
        pass

    def checkin(self):
        pass

    def send_notification(self):
        pass


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


def command_receive():

    pass


def main():
    pass


if __name__ == '__main__':
    main()