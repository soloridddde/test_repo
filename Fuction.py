import os
import time
import math


def file_status():
	"""
	先找出时间最新（时间最大）的文件，再监测该文件是否在持续更新
	:return: return 0: error; return 1 normal
	"""
	# 使用场景：像strsvr一样，每隔一段时间生成一个新的txt文件，始终监测最新生成的文件是否在持续更新
	# 自定义：文件类型，文件路径
	in_file_type = "txt"
	target_path = "D:\\mfw\\1_test\\cont\\raw"

	pathNtime = []
	files_list = []
	all_files_list = os.listdir(target_path)

	for file in all_files_list:
		if in_file_type in file:
			files_list.append(file)

		else:
			continue

	for file in files_list:
		path = os.path.join(target_path, file)
		mtime = os.path.getmtime(path)
		pathNtime.append([path, mtime])
	# 找出时间最新的一个文件路径
	max_time = 0
	for data in pathNtime:
		if float(data[1]) > max_time:
			max_time = data[1]

		else:
			continue
	max_locate = pathNtime.index(data)
	monitor_path = pathNtime[max_locate][0]

	former_t = os.path.getmtime(monitor_path)
	print(former_t)

	time.sleep(3)

	now_t = os.path.getmtime(monitor_path)
	print(now_t)

	if former_t == now_t:
		print("error, check")
		return 0
	else:
		print("normal")
		return 1


def log(info):
	"""
	在指定地址下生成log文件
	:param info: 需要写入log的内容
	:return: 无
	"""
	# 自定义：log路径
	report_path = "D:\\mfw\\1_test\\cont\\report"

	local_time = time.strftime("%Y-%M-%D %H:%M:%S")

	if os.path.exists(report_path + "\\" + "run_log.txt"):
		f_out = open(os.path.join(report_path, "run_log.txt"), mode='a')
	else:
		f_out = open(os.path.join(report_path, "run_log.txt"), mode='w')

	f_out.write(f"{local_time}	{str(info)}")
	f_out.close()


def utc_to_sec(utc):
	"""
	输入utc时间，转换为对应的秒。
	:param utc: utc(string)
	:return: seconds(int)
	"""
	utc_decimal = 0

	if isinstance(utc, str):
		if ':' in utc:  # 剔除数据中的“：”
			temp_utc = utc.split(':')
			# utc = temp_utc[0] + temp_utc[1] + str(int(float(temp_utc[2])))
			utc = temp_utc[0] + temp_utc[1] + str(float(temp_utc[2]))

		if '.' in utc:
			if len(utc.split('.')[0]) != 6:
				print(f"utc_to_sec转换错误{utc}")

		now_hr, now_min, now_sec = int(utc[:2]), int(utc[2:4]), float(utc[4:])

	else:
		utc = str(utc)
		if '.' in utc:
			utc_decimal = int(float('0.' + utc.split('.')[1]))
			utc = utc.split('.')[0]

		elif len(utc) < 6:
			while True:
				if len(utc) < 6:
					utc = '0' + utc
				else:
					break
		now_hr, now_min, now_sec = int(utc[:2]), int(utc[2:4]), int(utc[4:])

	total_sec = now_hr * 3600 + now_min * 60 + now_sec + utc_decimal

	return total_sec


def sec_to_utc(sec, mode=1):
	"""
	秒转化为utc
	:param sec:周内秒
	:param mode:
	:return:
	"""
	utc_decimal = ''

	sec = str(sec)
	if '.' in sec:
		utc_decimal = float('0.' + sec.split('.')[-1])

		if utc_decimal == 0:

			utc_decimal = ''
		else:
			utc_decimal = '.' + sec.split('.')[-1]

	sec = int(float(sec))

	utc_hr = int(sec/3600)

	utc_min = int((sec % 3600)/60)

	utc_sec = sec % 60

	if utc_hr < 10:

		utc_hr = '0' + str(utc_hr)

	if utc_min < 10:

		utc_min = '0' + str(utc_min)

	if utc_sec < 10:

		utc_sec = '0' + str(utc_sec)

	utc = str(utc_hr) + str(utc_min) + str(utc_sec) + str(utc_decimal)

	return utc


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
