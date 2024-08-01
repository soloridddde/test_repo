# -*- encoding: UTF-8 -*-
import os


def get_private_ip():
    """获取局域网IP"""
    permission_cmd = f'ipconfig'

    permission_result = os.popen(permission_cmd)

    for line in permission_result.readlines():
        if 'IPv4' in line:
            IP = line.split(': ')[1]
            print(IP)
            break


def get_ip():
    """获取公网IP"""
    permission_cmd = "curl ifconfig.me"

    permission_result = os.popen(permission_cmd)

    IP = permission_result.read()

    print(IP)


get_ip()