import os
import copy
import os
import time
from interval import Interval

#####
# 剔除tunnel附近10秒的数据
# 找出tunnel
# 提取kml中的时间和误差

utc = 0
tunnels_list = []


share_user = 'mengfo.wang'

share_password = 'w980910wmfv2'

share_file_host = '\\\\192.168.60.72'

share_dir_path= '\\\\192.168.60.72\\Test\\TestData(72)\\166022351'
	# '\\\\192.168.60.72\\Test\\TestData(72)\\166022361\\data_spp_replay'#总文件夹地址
	# \\192.168.60.72\Test\TestData(72)\166022351\case_FILE040_Dynamic\Compared

target_dir_path='D:\\mfw\\练习\\test_kml'

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
		split_line = line.split(',')
		if float(split_line[1]) > max_error:
			max_error = float(split_line[1])
			data_max_error = line

	return max_error

	f_in.close()


def expended_tunnel(infile, outfile):
	"输出剔除tunnel附近数据后的剩余数据"
	f_in = open(infile, encoding='UTF-8')
	f_out = open(outfile[3], mode="w")
	if_in_tunnel = 0

	################################
	for line in f_in.readlines():
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
			# f_out.write("In tunnel: " + line)
			if_in_tunnel = 0
		else:
			f_out.write(line)
			continue
	################################

	f_out.close()
	f_in.close()


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
	f_in = open(infile, encoding='UTF-8')
	f_out = open(outfile[2], mode='w')

	global utc
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
									f_out.write("Long Tunnel! Check: " + list_out[1])
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

	# OutputTunnel###############################输出到log
	# for tunnel in tunnels_list:
	# 	for data in tunnel:
	# 		f_out.write(data)
	# 		if data != tunnel[-1]:
	# 			f_out.write(',')
	# 	f_out.write("\n")

	f_in.close()
	f_out.close()
	print("Tunnels: [start time, end time, tunnel time, count tunnels]")
	print(tunnels_list)
	return tunnels_list


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


def run(dir_path, in_file_type, out_file_type):
	# 从kml提取数据
	print("Reading kml")
	for dir in dir_names:
		dir_path += "\\" + dir

		# 从kml中提取数据至info文件
		files = get_files(dir_path, in_file_type)
		for file in files:
			try:
				infile = os.path.join(dir_path, file)
			except:
				print("Error reading file.")

			# Output_Files
			# 输出到原文件文件夹下
			# 此处添加输出的文件
			f_nmea = infile[0:-3] + "nmea"
			f_satnum = infile[0:-3] + "SNum"
			f_data_from_kml = infile[0:-3] + "info"
			f_exclude_tunnel = infile[0:-4] + "ex_t"
			# f_test = infile[0:-4] + out_file_type

			# 在此添加输出文件到out_file_list
			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel]

			split_infile = infile.split('.')
			if split_infile[1] == "kml":
				try:
					print("Reading kml...")
					find_tunnel(infile, out_file_list)
					print("Done reading kml.")
				except:
					print("Error read kml.")

		# 从info文件中剔除特定场景数据：tunnel，回放结束（未完成），大误差（未完成）
		files = get_files(dir_path, "info")
		for file in files:
			try:
				infile = os.path.join(dir_path, file)
			except:
				print("Error reading file.")

			# Output_Files
			# 此处添加输出的文件
			f_nmea = infile[0:-3] + "nmea"
			f_satnum = infile[0:-3] + "SNum"
			f_data_from_kml = infile[0:-3] + "info"
			f_exclude_tunnel = infile[0:-4] + "ex_t"
			# f_test = infile[0:-4] + out_file_type

			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel]

			try:
				# 统计原始info的误差
				# 剔除指定场景数据
				max_error = get_max_error(infile)
				expended_tunnel(infile, out_file_list)
				print("Origin max error: " + str(max_error))
				print("Done exclude tunnel")
			except:
				print("Error read info.")

		# print剔除指定场景后的max error
		files = get_files(dir_path, "ex_t")
		for file in files:
			try:
				infile = os.path.join(dir_path, file)
			except:
				print("Error reading file.")

			try:
				max_error = get_max_error(infile)
				print("Changed max error: " + str(max_error))
			except:
				print("Error get max error")


def count_running_time():
	"""计算运行时间"""
	running_time = end - start
	print("Running time: " + str(running_time))


if __name__ == '__main__':
	start = time.perf_counter()
	"""以下为主要代码"""

	# copy
	try:
		print("Start copying file...")
		copy_share_file()
		print(dir_names)

	except:
		print("Error copying file!")

	# 处理
	try:
		print("Start processing...")
		dir_path = target_dir_path
			#r"D:\mfw\练习\kml\38"
		in_file_type = "kml"
		out_file_type = "blank"
		run(dir_path, in_file_type, out_file_type)
		print("End processing.")

	except:
		print("Error processing!")

	"""主要代码到此为止"""
	end = time.perf_counter()
	count_running_time()

