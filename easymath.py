# import os
# from loguru import logger
#
# # file = r"D:\mfw\tool\断电TTFF\runMain.bat"
# import time
#
#
# # @logger.catch
# def test():
# 	cmd_list = list()
# 	exe_path = r"D:\mfw\tool\TaskClientMonitor\TaskClientMonitor.exe"
#
# 	target_dir = exe_path.replace('\TaskClientMonitor.exe', '')
#
# 	os.chdir(target_dir)
#
# 	retval = os.getcwd()
#
# 	print(retval)
#
# 	run_exe = os.popen(r"TaskClientMonitor.exe")
# # res = os.system(file)
#
# try:
# 	test()
# except Exception as e:
# 	logger.exception(e)
# -*- coding: utf-8 -*-

import math


def get_average(records):
	"""
	平均值
	"""
	return sum(records) / len(records)


def get_variance(records):
	"""
	方差 反映一个数据集的离散程度
	"""
	average = get_average(records)
	return sum([(x - average) ** 2 for x in records]) / len(records)


def get_standard_deviation(records):
	"""
	标准差 == 均方差 反映一个数据集的离散程度
	"""
	variance = get_variance(records)
	return math.sqrt(variance)


def get_rms(records):
	"""
	均方根值 反映的是有效值而不是平均值
	"""
	return math.sqrt(sum([x ** 2 for x in records]) / len(records))


def get_mse(records_real, records_predict):
	"""
	均方误差 估计值与真值 偏差
	"""
	if len(records_real) == len(records_predict):
		return sum([(x - y) ** 2 for x, y in zip(records_real, records_predict)]) / len(records_real)
	else:
		return None


def get_rmse(records_real, records_predict):
	"""
	均方根误差：是均方误差的算术平方根
	"""
	mse = get_mse(records_real, records_predict)
	if mse:
		return math.sqrt(mse)
	else:
		return None


def get_mae(records_real, records_predict):
	"""
	平均绝对误差
	"""
	if len(records_real) == len(records_predict):
		return sum([abs(x - y) for x, y in zip(records_real, records_predict)]) / len(records_real)
	else:
		return None

