import copy
import os
import time
from interval import Interval

#####
# 第一版，未处理问题：
# 0909记录
# 1.一个是tunnel需要独立返回或者写入到和case对应的独立文件中；按照最开始的写法，tunnel的总数可能会有问题。
# 	处理：尝试ruturn传值。tunnels_list是否还需要global？
# 2.在运行方法的时候，只能处理一个文件夹中的数据，case文件夹的循环没有生效，需要调试。
# 3.剔除开头和结尾的数据，独立进行统计分析。
# 4.重新统计剔除后的误差，进行后续处理，判断误差是否到达一个容忍范围
# 剔除tunnel附近10秒的数据
# 找出tunnel
# 提取kml中的时间和误差

utc = 0

count_kml_file = 0

tunnels_list = []


share_user = 'mengfo.wang'

share_password = 'w980910wmfv2'

share_file_host = '\\\\192.168.60.72'

share_dir_path = '\\\\192.168.60.72\\Test\\TestData(72)\\166022351'
# '\\\\192.168.60.72\\Test\\TestData(72)\\166022361\\data_spp_replay'#总文件夹地址
# \\192.168.60.72\Test\TestData(72)\166022351\case_FILE040_Dynamic\Compared

target_dir_path = 'D:\\mfw\\练习\\test_kml'

dir_names = []

excluded_case = ['FILE068', 'FILE069', 'FILE070', 'FILE071', 'FILE076', 'FILE077', 'FILE078', 'FILE079', 'FILE080',
				 'FILE083', 'FILE084', 'FILE085', 'FILE086', 'FILE087']


def create_dirs():
	"在指定路径下创建同名文件夹"
	print("Creating subDirs!")
	global dir_names
	print("Excluded case: ")
	print(excluded_case)
	if os.path.exists(share_dir_path):
		if os.path.exists(target_dir_path):
			for curDir, dirs, files in os.walk(share_dir_path):
				for dir in dirs:
					if dir.startswith("case_FILE") and dir.split('_')[1] not in excluded_case:

						if dir not in dir_names:
							dir_names.append(copy.deepcopy(dir))

						try:

							os.mkdir(target_dir_path + "./" + dir)
							print(target_dir_path + "\\" + dir + " created!")

						except:
							print("Target directory already exist!")
		else:
			print("Target directory path not exist, check: " + target_dir_path)
	else:
		print("Source directory path not exist! Check: " + share_dir_path)

	print("End of Creating subDirs!")


def copy_share_file():
	"拷贝指定文件到指定路径"
	permission_cmd=f'net use {share_file_host} {share_user} /user:{share_password}'

	print(permission_cmd)

	permission_result=os.popen(permission_cmd)

	print(permission_result.read())

	create_dirs()

	for dir in dir_names:

		share_file_path = share_dir_path + "\\" + dir + "\\Compared\\*.kml"

		target_file_path = target_dir_path + "\\" + dir

		copy_cmd = f'xcopy /y {share_file_path} {target_file_path}'

		print(copy_cmd)

		copy_result = os.popen(copy_cmd)

		print(copy_result.read())


######################################################################################################
def get_max_error(infile):
	"统计最大误差，输入文件格式：utc, error"
	f_in = open(infile, encoding='UTF-8')
	max_error = 0

	for line in f_in.readlines():
		line = line.strip('\n')

		if line.startswith('$'):
			continue
		else:
			split_line = line.split(',')

			if float(split_line[1]) > max_error:
				max_error = float(split_line[1])
				data_max_error = line
	f_in.close()
	return max_error


def exclude_tunnel(infile, outfile):
	"输出剔除tunnel附近数据后的剩余数据"
	try:
		f_in = open(infile, encoding='UTF-8')
		f_out = open(outfile[3], mode="w")
		if_in_tunnel = 0
		tunnels_list = []
		global count_kml_file

		count_kml_file += 1
		print("Start exclude_tunnel: " + "Round" + str(count_kml_file))
		print("Now excluding tunnel: " + infile)

		################################
		for line in f_in.readlines():
			if line.startswith("$T"):
				line = line.rstrip("\n")
				line = line.lstrip("$Tunnel: ")
				tunnel = line.split(',')
				tunnels_list.append(copy.deepcopy(tunnel))
		################################

		f_in.seek(0)

		################################
		for line in f_in.readlines():
			if line.startswith("$T"):
				continue
			else:
				for tunnel in tunnels_list:
					if int(str(int(float(tunnel[0])))[-2:]) < 10:
						ex_tunnel_start = float(tunnel[0]) - 50
					else:
						ex_tunnel_start = float(tunnel[0]) - 10

					if int(str(int(float(tunnel[1])))[-2:]) > 50:
						ex_tunnel_end = float(tunnel[1]) + 50
					else:
						ex_tunnel_end = float(tunnel[1]) + 10

					if float(line.split(',')[0]) not in Interval(ex_tunnel_start, ex_tunnel_end):
						continue
					else:
						if_in_tunnel = 1
				if if_in_tunnel == 1:
					#f_out.write("In tunnel: " + line)
					if_in_tunnel = 0
				else:
					f_out.write(line)
					continue
		################################
		print("End excluding tunnel: " + infile)

		f_out.close()
		f_in.close()
	except:
		print("error exclude tunnel")


def get_info(raw_str):
	"返回kml文件中的数据"
	if raw_str.count("<TR", 3, 6) and len(raw_str) > 21:
		rmv_head_tail = raw_str[33:-11]
		info_list = rmv_head_tail.split("</TD><TD>")
		return info_list
	else:
		return 0


def find_tunnel(infile, outfile):
	"从kml提取数据到.info文件中"
	# start_time; end_time 是为了截取起止时间附近的大误差。
	f_in = open(infile, encoding='UTF-8')
	f_out = open(outfile[2], mode='w')
	start_time = 0
	end_time =0

	global utc
	utc = 0

	global tunnels_list

	# 清空tunnels_list
	tunnels_list = []

	count_tunnel = 0

	# 提取数据并找到tunnel
	for line in f_in.readlines():
		tunnel_time = 0
		try:
			list_out = get_info(line)
			if list_out == 0:
				continue
			else:
				try:
					#提取数据
					if "Time:" in list_out:
						if utc == 0:
							start_time = list_out[1]

						not_tunnel_time = float(list_out[1]) - float(utc)
						# tunnel内的时间：
						if not_tunnel_time not in [41, 4041] and not_tunnel_time >= 2:

							if not_tunnel_time <= 5:
								print("data lost here: " + list_out[1])
							elif utc != 0:
								print("tunnel here: " + list_out[1])

								if len(str(int(not_tunnel_time))) in [1, 2]:
									sec = int(str(int(not_tunnel_time))[-2:])
									if sec > 60:
										tunnel_time = sec - 40
									else:
										tunnel_time = sec

								if len(str(int(not_tunnel_time))) in [3, 4]:
									sec = int(str(int(not_tunnel_time))[-2:])
									min = int(str(int(not_tunnel_time))[:-2])
									if sec > 60:
										tunnel_time = min * 60 + sec - 40
									else:
										tunnel_time = min * 60 + sec

								if len(str(int(not_tunnel_time))) in [5, 6]:
									if utc == 0:
										# 排除开始的第一个时间
										pass
									else:
										f_out.write("Long Tunnel! Check: " + "now time" + list_out[1] +
													"	start time: " + str(utc) + "\n")

										# 发现长隧道后，要继续统计ex_t，则注释此条
										tunnel_time = "Error"

								tunnel_start = utc
								tunnel_end = list_out[1]
								count_tunnel += 1
								tunnel = [tunnel_start, tunnel_end, str(tunnel_time), str(count_tunnel)]
								tunnels_list.append(copy.deepcopy(tunnel))

							utc = list_out[1]
							f_out.write(utc[:] + ",")
						# 非tunnel时间：
						else:
							utc = list_out[1]
							f_out.write(utc[:] + ",")

					if "Error:" in list_out:
						H_error = list_out[1]
						f_out.write(H_error[2:] + "\n")
				except:
					f_out.write("error[1],check: " + line)

		except:
			f_out.write("error[1],check: " + line)

	end_time = utc

	# OutputTunnel###############################输出到log
	for tunnel in tunnels_list:
		f_out.write("$Tunnel: ")
		for data in tunnel:
			f_out.write(data)
			if data != tunnel[-1]:
				f_out.write(',')
		f_out.write("\n")

	f_in.close()
	f_out.close()
	print("Tunnel: [start time, end time, tunnel time, count tunnels]")
	print(tunnels_list)
	# return tunnels_list


def get_files(path, file_suffix=".csv"):
	"""获取 目录下 指定后缀 的 带后缀文件名"""
	# 获取所有raw文件
	file_names = []
	len_suffix = len(file_suffix)
	files = os.listdir(path)
	for file in files:
		fi_d = os.path.join(path, file)
		if os.path.isfile(fi_d) and file[-len_suffix:] == file_suffix:
			file_names.append(file)
	return file_names


def run(dir_path, in_file_type = "kml"):
	# 从kml提取数据
	print("Reading kml")
	print(dir_path)
	for temp_dir in dir_names:
		temp_dir_path = dir_path + "\\" + temp_dir
		# 1.从kml中提取数据至info文件
		files = get_files(temp_dir_path, in_file_type)
		for file in files:
			try:
				infile = os.path.join(temp_dir_path, file)
			except:
				print("Error reading file.")
			# Output_Files
			# 1.必须更新，否则无法生成文件 2.输出到原文件文件夹下 3.此处添加输出的文件
			f_nmea = infile[0:-3] + "nmea"
			f_satnum = infile[0:-3] + "SNum"
			f_data_from_kml = infile[0:-3] + "info"
			f_exclude_tunnel = infile[0:-3] + "ex_t"
			f_exclude_mxer1 = infile[0:-3] + "inte1"
			f_exclude_mxer2 = infile[0:-3] + "inte2"
			# f_test = infile[0:-4] + out_file_type

			# 在此添加输出文件到out_file_list
			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel, f_exclude_mxer1, f_exclude_mxer2]

			split_infile = infile.split('.')
			if split_infile[1] == "kml":
				try:
					print("Reading kml: " + file)
					find_tunnel(infile, out_file_list)
					print("Done reading kml.\n")
				except:
					print("Error read kml.")

		# 2.从info文件中剔除特定场景数据：tunnel，回放结束（未完成），大误差（未完成）
		files = get_files(temp_dir_path, "info")
		for file in files:
			try:
				infile = os.path.join(temp_dir_path, file)
			except:
				print("Error reading file.")

			# Output_Files
			# 输出到原文件文件夹下
			# 此处添加输出的文件
			f_nmea = infile[0:-4] + "nmea"
			f_satnum = infile[0:-4] + "SNum"
			f_data_from_kml = infile[0:-4] + "info"
			f_exclude_tunnel = infile[0:-4] + "ex_t"
			f_exclude_mxer1 = infile[0:-4] + "inte1"
			f_exclude_mxer2 = infile[0:-4] + "inte2"
			# f_test = infile[0:-4] + out_file_type

			# 在此添加输出文件到out_file_list
			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel, f_exclude_mxer1, f_exclude_mxer2]

			try:
				# 统计原始info的误差
				# 剔除指定场景数据
				max_error = get_max_error(infile)
				exclude_tunnel(infile, out_file_list)
				print("Origin max error: " + str(max_error))
				print("Done exclude tunnel.")
			except:
				print("Error reading info.")

		# 3.print剔除指定场景后的max error
		files = get_files(temp_dir_path, "ex_t")
		for file in files:
			try:
				infile = os.path.join(temp_dir_path, file)

			except:
				print("Error reading file.")

			# Output_Files
			# 输出到原文件文件夹下
			# 此处添加输出的文件
			f_nmea = infile[0:-4] + "nmea"
			f_satnum = infile[0:-4] + "SNum"
			f_data_from_kml = infile[0:-4] + "info"
			f_exclude_tunnel = infile[0:-4] + "ex_t"
			f_exclude_mxer1 = infile[0:-4] + "inte1"
			f_exclude_mxer2 = infile[0:-4] + "inte2"
			f_report = target_dir_path + "\\" + "report.txt"
			# f_test = infile[0:-4] + out_file_type

			# 在此添加输出文件到out_file_list
			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel, f_exclude_mxer1, f_exclude_mxer2, f_report]

			try:
				max_error = get_max_error(infile)
				print("Exclusion 1: ")
				print("Max error before exclusion 1: " + str(max_error))
				print("now processing " + infile)
				duration_info = exclude_max_error(infile, out_file_list)
				# 仅统计BK的情况
				if file.startswith('1') or file.startswith('2'):
					try:
						if_pass(max_error, duration_info, out_file_list, file, temp_dir)
					except:
						print("Error excluding max error")
			except:
				print("Error getting max error.")

		# 4.重新统计一遍MAX ERROR
		files = get_files(temp_dir_path, "inte1")
		for file in files:
			try:
				infile = os.path.join(temp_dir_path, file)

			except:
				print("Error reading file.")
			# Output_Files
			# 输出到原文件文件夹下
			# 此处添加输出的文件
			f_nmea = infile[0:-5] + "nmea"
			f_satnum = infile[0:-5] + "SNum"
			f_data_from_kml = infile[0:-5] + "info"
			f_exclude_tunnel = infile[0:-5] + "ex_t"
			f_exclude_mxer1 = infile[0:-5] + "inte1"
			f_exclude_mxer2 = infile[0:-5] + "inte2"
			# f_test = infile[0:-4] + out_file_type

			# 在此添加输出文件到out_file_list
			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel, f_exclude_mxer1, f_exclude_mxer2]

			try:
				# 加个判断，仅统计BK的结果
				max_error = get_max_error(infile)
				print("Changed max error2: " + str(max_error))

			except:
				print("Error getting max error.")


def if_pass(max_error, dur_info_list, outfiles, filename, case_file_name):
	# 判断文件是否存在，确定打开文件的mode（覆写w或追加a）
	if os.path.exists(target_dir_path + "\\" + "report.txt"):
		f_out = open(outfiles[6], mode='a')
	else:
		f_out = open(outfiles[6], mode='w')
	f_out.write(case_file_name + "\n")
	f_out.write(filename + "\n")

	for info in dur_info_list[1:]:
		duration = info[0]
		# 判断
		if max_error < 5:
			f_out.write("Pass\n")

		elif max_error <= 20:
			if duration > 10:
				f_out.write("Max error " + str(max_error) + ", Problem found: " + filename + "\n")

			elif duration <= 10:
				f_out.write("Pass\n")

		elif max_error > 20:
			f_out.write("Max error " + str(max_error) + ", Problem found: " + filename + "\n")

	f_out.write("\n\n")



def count_running_time():
	"""计算运行时间"""
	running_time = end - start
	print("Running time: " + str(running_time))


def exclude_max_error(infile, outfile):
	# 迭代，重复剔除最大误差出现的区间
	# 输入ex_t文件
	f_in = open(infile, encoding='UTF-8')
	# 剔除最大误差附近的数据后的文件
	f_out = open(outfile[4], mode='w')
	# 剔除出来的最大误差
	f_out2 = open(outfile[5], mode='w')
	# 统计持续时间
	duration = 0

	temp_duration = 0

	#duration次数
	count_duration = 0
	#duration list
	durations = []
	#上次时间（UTC）
	last_time = 0
	# 统计最大误差
	max_error = get_max_error(infile)
	# 剔除max_error,剔除至值到一定的区间内，暂定为：
	# <5(暂时不统计)
	# 5-10
	# 10-50
	# 50-100, (20 or 30)
	# >100, (50)
	#

	if max_error < 5:
		f_out2.write("Done Interation, max error: " + str(max_error) + "\n")

	elif 5 <= max_error < 10:
		f_out2.write("Done Interation, max error: " + str(max_error) + "\n")
		f_out2.write("MAX_ERROR 0: [,10)\n")
		# f_in.seek(0)
		for line in f_in.readlines():
			line = line.strip('\n')
			now_error = float((line.split(','))[1])
			if now_error not in Interval(5, 10, upper_closed=False):
				f_out.write(line + "\n")
			else:
				now_time = float((line.split(','))[0])
				if now_time - last_time > 2:
					temp_duration = duration

					durations.append(copy.deepcopy([temp_duration, count_duration]))

					count_duration += 1
				last_time = now_time

				f_out2.write(line + "\n")
				duration += 1

	elif 10 <= max_error < 20:
		f_out2.write("Done Interation, max error: " + str(max_error) + "\n")
		f_out2.write("MAX_ERROR 0: [10,20)\n")
		f_in.seek(0)
		for line in f_in.readlines():
			line = line.strip('\n')
			now_error = float((line.split(','))[1])
			if now_error not in Interval(10, 20, upper_closed=False):
				f_out.write(line + "\n")
			else:
				now_time = float((line.split(','))[0])
				if now_time - last_time > 2:
					temp_duration = duration

					durations.append(copy.deepcopy([temp_duration, count_duration]))

					count_duration += 1
				last_time = now_time

				f_out2.write(line + "\n")
				duration += 1

	elif 20 <= max_error < 50:
		f_out2.write("Done Interation, max error: " + str(max_error) + "\n")
		f_out2.write("MAX_ERROR 1: [20,50)\n")
		f_in.seek(0)
		for line in f_in.readlines():
			line = line.strip('\n')
			now_error = float((line.split(','))[1])
			if now_error not in Interval(20, 50, upper_closed=False):
				f_out.write(line + "\n")
			else:
				now_time = float((line.split(','))[0])
				if now_time - last_time > 2:
					temp_duration = duration

					durations.append(copy.deepcopy([temp_duration, count_duration]))

					count_duration += 1
				last_time = now_time

				f_out2.write(line + "\n")
				duration += 1

	elif 50 <= max_error < 100:
		f_out2.write("Done Interation, max error: " + str(max_error) + "\n")
		f_out2.write("MAX_ERROR 2: [50,100)\n")
		f_in.seek(0)

		for line in f_in.readlines():
			line = line.strip('\n')
			now_error = float((line.split(','))[1])
			if now_error not in Interval(50, 100, upper_closed=False):
				f_out.write(line + "\n")
			else:
				# 在区间中
				now_time = float((line.split(','))[0])
				if now_time - last_time > 2:
					temp_duration = duration

					durations.append(copy.deepcopy([temp_duration, count_duration]))

					count_duration += 1
				last_time = now_time

				f_out2.write(line + "\n")
				duration += 1

	elif max_error >= 100:
		f_out2.write("Done Interation, max error: " + str(max_error) + "\n")
		f_out2.write("MAX_ERROR 3: [100,max_error)\n")
		f_in.seek(0)
		for line in f_in.readlines():
			line = line.strip('\n')
			now_error = float((line.split(','))[1])
			if now_error < 100:
				f_out.write(line + "\n")
			else:
				now_time = float((line.split(','))[0])
				if now_time - last_time > 2:
					temp_duration = duration

					durations.append(copy.deepcopy([temp_duration, count_duration]))

					count_duration += 1
				last_time = now_time

				f_out2.write(line + "\n")
				duration += 1

	else:
		f_out2.write("Unexpected error in exclude_max_error, max_error: " + str(max_error) + "\n")

	temp_duration = duration - temp_duration

	durations.append(copy.deepcopy([temp_duration, count_duration]))

	# 最后一段的duration
	for data in durations[1:]:
		f_out2.write("Duration: " + str(data) + '\n')

	f_out2.close()
	f_out.close()
	f_in.close()

	return durations

if __name__ == '__main__':
	start = time.perf_counter()
	"""以下为主要代码"""

	# copy
	try:
		print("Start copying file...")
		copy_share_file()
		print(dir_names)

	except Exception as e:
		print("Error copying file!")
		print(e)
		print(e.__traceback__.tb_frame.f_globals["__file__"])
		print(e.__traceback__.tb_lineno)

	# 处理
	try:
		print("Start processing...")
		dir_path = target_dir_path
			#r"D:\mfw\练习\kml\38"
		in_file_type = "kml"
		run(dir_path, in_file_type)
		print("End processing.")

	except Exception as e:
		print("Error processing!")
		print(e)
		print(e.__traceback__.tb_frame.f_globals["__file__"])
		print(e.__traceback__.tb_lineno)

	"""主要代码到此为止"""
	end = time.perf_counter()
	count_running_time()
