import os
import time

# 目前支持自定义文件后缀，自定义路径，直接运行即可


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


def get_files(path, file_suffix=".csv"):
	"""获取目录下的raw文件"""
	# 获取所有raw文件
	file_names = []
	len_suffix = len(file_suffix)
	files = os.listdir(path)
	for file in files:
		fi_d = os.path.join(path, file)
		if os.path.isfile(fi_d) and file[-len_suffix:] == file_suffix:
			file_names.append(file)
	return file_names


def run(dir_path, in_file_type, test_file_type):
	files = get_files(dir_path, in_file_type)
	for file in files:
		infile = os.path.join(dir_path, file)
		f_nmea = infile[0:-3] + "nmea"
		f_satnum = infile[0:-3] + "SNum"
		f_test = infile[0:-3] + test_file_type
		out_file_list = [f_nmea, f_satnum, f_test]

		read_nmea(infile, out_file_list, command_list)


def count_running_time():
	"""计算运行时间"""
	Running_time = end - start
	print("Running time: " + str(Running_time))


if __name__ == '__main__':
	start = time.perf_counter()
	"""以下为主要代码"""
	print("file path: ")
	# eg:"\\192.168.60.217\external exchange\common\WTR_LOG\22.10.24_166022425\稳定性测试"
	dir_path = input()
	print("file type: ")
	# eg:txt
	in_file_type = input()

	#dir_path = r"\\192.168.60.217\external exchange\common\WTR_LOG\22.10.24_166022425\稳定性测试"
	#"D:\mfw"
	#"D:\mfw\cut\0819_l1l5_10"
	#D:\mfw\练习\nmea\continuous_2

	#in_file_type = "log"

	test_file_type = "change"

	command_list = [0, 1]#0:提取nmea		1：检测掉星

	run(dir_path, in_file_type, test_file_type)

	"""主要代码到此为止"""
	end = time.perf_counter()
	count_running_time()