import os
import time

# a = os.path.getmtime("D:\\mfw\\1_test\\1009_113718_sf_com9_0015.txt")
# b = os.path.getctime("D:\\mfw\\1_test\\1009_113718_sf_com9_0015.txt")
# print(a)
# print(b)
#
# print(((a-b)/3600))
#
# c = os.path.getsize("D:\\mfw\\1_test\\1008_114303_df_com8_005.txt")
# print(c)
#
# # 1008_000000_sf_com8_005
# print(time.localtime(a))
# print(time.localtime(b))
# print(time.localtime(time.time()))
#
# print(len(os.listdir("D:\\mfw\\1_test\cont\\raw")))


def count_running_time():
	"""计算运行时间"""
	Running_time = end - start
	print("Running time: " + str(Running_time))


def run(files, test_file_type):
	for file in files:
		infile = os.path.join(target_path, file)
		outfile = os.path.join(result_path, file)
		# 输出的文件
		f_nmea = outfile[0:-3] + "nmea"
		f_satnum = outfile[0:-3] + "SNum"
		f_test = outfile[0:-3] + test_file_type
		out_file_list = [f_nmea, f_satnum, f_test]

		read_nmea(infile, out_file_list, command_list)

		transformer(infile, hashcode_path)


def read_nmea(infile, out_f_list, mode_list=[0]):
	global fp_out
	for mode in mode_list:
		match mode:

			case 0:#提取nmea
				fp = open(infile, encoding='ISO-8859-1')

				out_nmea = out_f_list[0]
				fp_out = open(out_nmea, mode="w")

				################################
				for line in fp.readlines():
					try:
						out_str = get_nmea(line, 0)
						if out_str != "":
							fp_out.write(out_str)
					except:
						continue
				################################

				fp_out.close()
				fp.close()

			case 1:
				fp = open(infile, encoding='ISO-8859-1')
				out_Snum = out_f_list[1]
				fp_out = open(out_Snum, mode="w")
				first_fixed_time = "0"
				last_SatNum = "0"


				################################
				for line in fp.readlines():
					try:
						if get_nmea(line, 1) == "":
							continue

						out_str = get_nmea(line, 1)

						if out_str.count(",") != 14:
							fp_out.write("Data lost[1]: " + out_str)
							continue

						else:
							splited_gga = out_str.split(",")
							now_time = splited_gga[1]  ####UTC,时间不能直接int(now_time)
							QI = splited_gga[6]  ####Quality Indicator 1-8
							SatNum = splited_gga[7]  ####GGA卫星数
							#	简单的检测丢数

							if len(QI) != 1 or int(QI) == 0:  # 不定位或QI丢数
								fp_out.write("Not fixed or Data lost[2]: " + out_str)
								continue

							# 以下为定位的情况下
							else:
								try:
									if first_fixed_time == "0":
										first_fixed_time = now_time
										fp_out.write("First fixed here: " + first_fixed_time + "\n")
									if SatNum == "" or SatNum == "0":  # fixed but satnum error
										fp_out.write("Data lost[3]: " + now_time + "\n")
										continue

									if last_SatNum == "0":
										last_SatNum = SatNum
										fp_out.write("First fine data: " + str(now_time) + ", SatNum: " + str(SatNum) + "\n")
										continue

									else:  # 以下为正常定位且卫星数量不为0的情况下
										try:
											if int(SatNum) in list(range(1, 100)):
												dif_SatNum = int(SatNum) - int(last_SatNum)

										except:
											fp_out.write("count SatNum error")

										if dif_SatNum in list(range(-3, 4)):
											last_SatNum = SatNum
											continue

										if dif_SatNum >= 4:
											fp_out.write("Sat num increase rapidly\n" + "SatNum change: " + str(dif_SatNum) + "\n")
											fp_out.write("UTC: " + now_time + "		SatNum change: " + str(dif_SatNum) + "\n")
											fp_out.write("Last Satnum: " + last_SatNum + "		Now SatNum: " + SatNum + "\n")
											last_SatNum = SatNum
											continue

										if dif_SatNum <= -4:
											fp_out.write("Sat num decrease rapidly\n" + "SatNum change: " + str(dif_SatNum) + "\n")
											fp_out.write("UTC: " + now_time + "		SatNum change: " + str(dif_SatNum) + "\n")
											fp_out.write("Last Satnum: " + last_SatNum + "		Now SatNum: " + SatNum + "\n")
											last_SatNum = SatNum

								except:
									fp_out.write("Count sat change error! \n")

					except:
						if get_nmea(line, 1) == "":
							continue
						else:
							continue



				################################

				fp_out.close()
				fp.close()


			case _:
				fp_out.write("Something wrong dealing raw data")


def get_nmea(str, mode):

	"""取nmea语句,nmea_switch为一列表"""
	ret_str = ""

	match mode:
		case 0:#全部nmea
			if str.count("$"):
				if str.count("GGA"):
					pos_st = str.find("GGA")
					if pos_st > 2:
						ret_str += str[pos_st - 3:]

				if str.count("RMC"):
					pos_st = str.find("RMC")
					if pos_st > 2:
						ret_str += str[pos_st - 3:]

				if str.count("GSA"):
					pos_st = str.find("GSA")
					if pos_st > 2:
						ret_str += str[pos_st - 3:]

				if str.count("GSV"):
					pos_st = str.find("GSV")
					if pos_st > 2:
						ret_str += str[pos_st - 3:]

				if str.count("GLL"):
					pos_st = str.find("GLL")
					if pos_st > 2:
						ret_str += str[pos_st - 3:]

				if str.count("VTG"):
					pos_st = str.find("VTG")
					if pos_st > 2:
						ret_str += str[pos_st - 3:]

			return ret_str

		case 1:#only gga
			try:
				if str.count("$"):
					if str.count("GGA"):
						pos_st = str.find("GGA")
						if pos_st > 2:
							ret_str += str[pos_st - 3:]
				return ret_str
			except:
				global fp_out
				fp_out.write("error_get_nmea")
		#########################################
		# 以下global可能会出错，如果出错，则把fp_out当变量输入该函数
		case _:
			fp_out.write("Something wrong selecting nmea")


def file_status():
	# 先找出时间最大的文件，再监测该文件是否在持续更新
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


def get_change_duration():
	fname_list = []
	two_hr_list = []

	files_list = os.listdir(result_path)
	for file in files_list:
		if "SNum" in file:
			fname_list.append(file)
	if not fname_list:
			log("failure: get_max_sat_change()\n")
			print("failure: get_max_sat_change()")

	for file in fname_list:
		f_path = os.path.join(result_path, file)
		f_in = open(f_path, encoding="utf-8")
		for line in f_in.readlines():
			if "UTC" in line:
				utc_time = (line.split())[1]
				if len(utc_time) == 9:
					utc_hour = utc_time[:2]
					if int(utc_hour) < 1:
						start_time = utc_time.replace(utc_hour, "23")
						end_time = utc_time.replace(utc_time[:2, "00"])
						two_hr_list.append([start_time, end_time])

					elif 23 > int(utc_hour) >= 1:
						start_time = utc_time.replace(utc_hour, str(int(utc_hour) - 1).zfill(2))
						end_time = utc_time.replace(utc_hour, str(int(utc_hour) + 1).zfill(2))
						two_hr_list.append([start_time, end_time])

					elif int(utc_hour) >= 23:
						start_time = utc_time.replace(utc_hour, str(int(utc_hour) - 1).zfill(2))
						end_time = utc_time.replace(utc_time[0:2], "00")
						two_hr_list.append([start_time, end_time])

				else:
					log(f"failure, check utc length: {utc_time}\n")
	print(two_hr_list)
	return two_hr_list


def get_max_change():
	duration_list = get_change_duration()
	for duration in duration_list:
		for start_time, end_time in duration:
			if int(end_time) > int(start_time):
				duration_1 = [0, int(end_time)]
				duration_2 = [int(start_time), 235959]

			elif int(start_time) < int(end_time):
				duration = [start_time, end_time]


def transformer(file, hashcode):
	log("开始转换文件：{}".format(file))
	try:
		cmd = transformer_path + ' ' + file + ' ' + hashcode
		log(cmd)
		os.popen(cmd)
	except:
		log("Transfor failure:{}".format(file))
		return 0


def report(info):
	local_time = time.strftime("%Y-%M-%D %H:%M:%S")

	if os.path.exists(report_path + "\\" + "report.txt"):
		f_out = open(os.path.join(report_path, "report.txt"), mode='a')
	else:
		f_out = open(os.path.join(report_path, "report.txt"), mode='w')

	f_out.write(f"{local_time}	{str(info)}")
	f_out.close()


def log(info):
	local_time = time.strftime("%Y-%M-%D %H:%M:%S")

	if os.path.exists(report_path + "\\" + "run_log.txt"):
		f_out = open(os.path.join(report_path, "run_log.txt"), mode='a')
	else:
		f_out = open(os.path.join(report_path, "run_log.txt"), mode='w')

	f_out.write(f"{local_time}	{str(info)}")
	f_out.close()

if __name__ == '__main__':
	start = time.perf_counter()
	"""以下为主要代码"""
	count_round = 0
	count_files = 0
	last_count_files = 1
	files_list = []
	last_files_list = []
	task_file_list = []
	excluded_files = []
	target_path = "D:\\mfw\\1_test\\cont\\raw"
	# for 81:"D:\\mfw\\1_test\\cont\\raw"
	# for 23:"E:\\mengfo.wang\\test\\continuous_test\\raw"
	result_path = target_path
	# for 81:"D:\\mfw\\1_test\\cont\\nmea"
	# for 23:"E:\\mengfo.wang\\test\\continuous_test\\nmea"
	report_path = "D:\\mfw\\1_test\\cont\\report"
	# for 81:"D:\\mfw\\1_test\\cont\\report"
	# for 23:"E:\\mengfo.wang\\test\\continuous_test\\report"
	hashcode_path = "D:\\mfw\\1_test\\cont\\BkMessageTransformer64\\BX1_RTOS_PRINT_HASHCODE.txt"

	transformer_path = r"D:\mfw\1_test\cont\BkMessageTransformer64\BkMessageTransformer.exe"
	in_file_type = "txt"
	test_file_type = "change"
	command_list = [0, 1]  # 0:提取nmea		1：检测掉星

	while True:
		# 初始化task file list
		task_file_list = []
		files_list = []

		count_round += 1
		# 传递上次文件数
		if count_files:
			last_count_files = count_files
		#
		all_files_list = os.listdir(target_path)

		for file in all_files_list:
			if in_file_type in file:
				files_list.append(file)

			else:
				continue

		count_files = len(files_list)

		# # 防止无限循环（调试用）
		# if count_round > 100:
		# 	break

		# 文件数量发生变化时，运行run()
		if last_count_files != count_files:
			# 此处需要加入一个files_list,对比已经处理过的files_list，循环处理需要处理的files
			print("processing...")
			for file in last_files_list:
				if file in excluded_files:
					continue
				else:
					task_file_list.append(file)
			run(task_file_list, test_file_type)
			# 更新数据excluded_files，last_files_list
			for file in task_file_list:
				excluded_files.append(file)

			last_files_list = files_list

		# 数量未变化，一小时后重试
		else:
			print("FILE NOT CHANGE, SLEEP 1 SEC")
			time.sleep(1)

			last_files_list = files_list

		# 查看是否正常工作
		file_status()

		"""主要代码到此为止"""
		end = time.perf_counter()
		count_running_time()