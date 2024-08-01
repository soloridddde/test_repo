import copy
import json
import os
import time
from Fuction import utc_to_sec
from Fuction import sec_to_utc
from interval import Interval
from loguru import logger
# from Create_json_file import write_json_file

#####
# 能完成基本的统计判断，能进行基本的对比，暂不支持和对比机对比；tunnel附近的数据未参加对比
utc = 0

count_kml_file = 0

tunnels_list = []

share_user = 'mengfo.wang'

share_password = 'w980910wmfv6'

share_file_host = r'\\192.168.60.72'

share_dir_path = r'\\192.168.60.72\Test\TestData(72)\166023085\data_spp_replay'
# '\\\\192.168.60.72\\Test\\TestData(72)\\166022361\\data_spp_replay'#总文件夹地址
# \\192.168.60.72\Test\TestData(72)\166022351\case_FILE040_Dynamic\Compared

target_dir_path = r'D:\mfw\练习\test_kml'

dir_names = []

excluded_case = ['FILE068', 'FILE069', 'FILE070', 'FILE071', 'FILE076', 'FILE077', 'FILE078', 'FILE079', 'FILE080',
				 'FILE083', 'FILE084', 'FILE085', 'FILE086', 'FILE087']


def access_to_host(target_ip):
	"""
	连接至target_ip，获取远程共享权限
	parm: target_ip:远程共享IP地址
	"""
	if target_ip == '192.168.60.162' or target_ip == r'\\192.168.60.152':
		share_file_host = r'\\192.168.60.152'
		share_user = 'labsat'
		share_password = 'GnssData.02'
	elif target_ip == '192.168.60.161' or target_ip == r'\\192.168.60.152':
		share_file_host = r'\\192.168.60.152'
		share_user = 'labsat'
		share_password = 'GnssData.01'
	else:
		if r'\\' in target_ip:
			share_file_host = fr'{target_ip}'
		else:
			share_file_host = fr'\\{target_ip}'

		share_user = 'mengfo.wang'

		share_password = 'w980910wmfv6'

	permission_cmd = f'net use {share_file_host}  {share_password} /user:{share_user}'

	permission_result = os.popen(permission_cmd)

	print(permission_result.read())


def copy_file(file_path, copy_to):
	"""
	拷贝文件到指定路径下
	:param file_path: 被拷贝的文件路径（包括后缀的绝对路径）
	:param copy_to: 目标文件夹的路径
	:return: 无
	"""
	access_to_host(share_file_host)

	copy_cmd = f'xcopy /y {file_path} {copy_to}'

	# print(copy_cmd)

	copy_result = os.popen(copy_cmd)

	# print(copy_result.read())


def copy_TruthAndExcel(remote_root, local_root):
	for root, dirs, files in os.walk(local_root):
		for dir in dirs:
			try:
				cur_local_dir = os.path.join(local_root, dir, 'Compare')
				cur_remodir = os.path.join(remote_root, dir, 'Compared')
			except Exception as e:
				logger.exception(e)
				continue  #路径拼接失败，预计为local_root, dir下无'Compare'文件夹

			if os.path.exists(cur_local_dir):
				existed_lf = os.listdir(cur_local_dir)  # existed local file
				existed_remof = os.listdir(cur_remodir)  # existed remote file

				for file in existed_remof:
					if file in existed_lf:
						continue
					else:
						file_path = os.path.join(cur_remodir, file)
						copy_file(file_path, cur_local_dir)


def process_kml(dir_path):
	"""
	修改kml文件
	:param dir_path: 在此文件夹路径下创建一个Compare文件夹用于存放结果
	:return: 无
	"""
	bk_kml_fpaths = list()

	kml_files_names = os.listdir(dir_path)

	for name in kml_files_names:  # 剔除对比机结果，只处理bk
		# 如果本程序不从拷贝开始处理，则会因当前路径下没有kml文件而报错
		if 'bk' in name or 'BK' in name:
			if '.kml' in name:
				bk_kml_fpath = os.path.join(dir_path, name)

				bk_kml_fpaths.append(bk_kml_fpath)

	for path in bk_kml_fpaths:  # 开始处理

		del_folder(path)

		insert_name(path)


def modify_point_info(point_info_list):
	"""
	增删改point相关信息
	:param point_info_list: 从<Placemark>到</Placemark>的kml点信息，句尾带\n
	:return:修改后的列表mpinfo_list
	"""
	if 1:
		for line in point_info_list:
			if 'UTC时间' in line:
				utc_time = line.split("时间：")[1][9:17]

				if ":" in utc_time:
					utc_time = utc_time.replace(':', '')

				insert_info = f"\t\t\t<name>{utc_time}</name>\n"  # 插入点名

				insert_pos = point_info_list.index(line) - 5

				point_info_list.insert(insert_pos, insert_info)

				break

	if 1:
		for line in point_info_list:
			if '<name></name>' in line:
				index_line = point_info_list.index(line)
				break

		try:
			del point_info_list[index_line]
		except:
			pass

	if 1:
		for line in point_info_list:
			if 'visibility' in line:
				temp_pos = point_info_list.index(line)
				del point_info_list[temp_pos]

		for line in point_info_list:
			if '<Placemark>' in line:
				# insert_info = f"\t\t\t<visibility>0</visibility>\n"  # 使点不可见
				insert_info = f"\t\t<visibility>1</visibility>\n"  # 使点可见

				insert_pos = point_info_list.index(line) + 1

				point_info_list.insert(insert_pos, insert_info)

				break

	return point_info_list


def create_dir(dirpath):
	"""
	功能：创建文件夹，若存在则跳过，不存在则创建
	:param dirpath:
	"""
	if not os.path.exists(dirpath):
		# os.mkdir(dirpath)
		os.makedirs(dirpath)
		# pass


def del_folder(source_kml_path):
	"""
	删除指定路径的kml文件中的第一个folder，目前有两个folder：1.Point；2.Point_Detail
	:param source_kml_path:kml文件路径
	:return:none
	"""
	result_kml_root = os.path.split(source_kml_path)[0] + '\\Compare'

	result_kml_name = os.path.split(source_kml_path)[1]

	result_kml_path = result_kml_root + '\\' +result_kml_name

	create_dir(result_kml_root)

	sc_file = open(source_kml_path, encoding='utf-8')

	res_file = open(result_kml_path, encoding='utf-8', mode='w')

	count_header = 0

	for line in sc_file.readlines():
		if '<Folder>' in line:
			count_header += 1

		if count_header == 1:
			continue

		else:
			res_file.write(line)

	sc_file.close()
	res_file.close()
	print('del_folder completed')


def insert_name(source_kml_path):
	"""
	插入信息：将utc作为点名，方便搜索。如121200
	:param source_kml_path: kml文件路径
	:return: none
	"""
	result_kml_root = os.path.split(source_kml_path)[0] + '\\Compare'

	result_kml_name = os.path.split(source_kml_path)[1]

	result_kml_path = result_kml_root + '\\' + result_kml_name

	create_dir(result_kml_root)

	res_list = list()

	is_point_info = 0

	sc_file = open(result_kml_path, mode='r', encoding='utf-8')

	lines_list = sc_file.readlines()

	for line in lines_list:
		if "<Placemark>" in line:
			is_point_info = 1

			point_info_list = list()

			point_info_list.append(line)

			continue

		if "</Placemark>" in line:
			is_point_info = 0

			point_info_list.append(line)

			modify_point_info(point_info_list)

			for temp_line in point_info_list:
				res_list.append(temp_line)

			continue

		if is_point_info == 0:
			res_list.append(line)

		elif is_point_info == 1:
			point_info_list.append(line)

	sc_file.close()

	res_file = open(result_kml_path, mode='w', encoding='utf-8')

	for res_line in res_list:
		res_file.write(res_line)

	res_file.close()
	print('Insert_name completed')


def create_dirs(source_dir, target_dir):
	"""
	在指定路径下创建同名文件夹
	:return: 无return
	"""

	print("Creating subDirs!")
	global dir_names
	print("Excluded case: ")
	print(excluded_case)
	if os.path.exists(source_dir):
		if os.path.exists(target_dir):
			for curDir, dirs, files in os.walk(source_dir):
				for dir in dirs:
					if dir.startswith("case_FILE") and dir.split('_')[1] not in excluded_case:

						if dir not in dir_names:
							dir_names.append(copy.deepcopy(dir))

						try:
							os.mkdir(target_dir + "./" + dir)
							print(target_dir + "\\" + dir + " created!")

						except:
							print("Target directory already exist!")
		else:
			print("Target directory path not exist, check: " + target_dir)
	else:
		print("Source directory path not exist! Check: " + source_dir)

	print("End of Creating subDirs!")


def copy_share_file():
	"""
	拷贝指定文件到指定路径
	:return: 无return
	"""

	access_to_host(share_file_host)

	create_dirs(share_dir_path, target_dir_path)

	for dir in dir_names:
		share_file_path = share_dir_path + "\\" + dir + "\\Compared\\*.kml"

		target_file_path = target_dir_path + "\\" + dir

		copy_file(share_file_path, target_file_path)


def get_max_error(infile):
	"""
	输入文件或者行列表，统计最大误差, 文件中$开头的数据将被跳过
	:param infile: 数据格式：utc, error
	:return:max position error(horizontal)
	"""
	# 输入为文件
	try:
		if os.path.exists(infile):
			print("get_max_error(file)")
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
						data_max_error = line  # 备用
			f_in.close()

	# 输入为行列表
	except:
		print("get_max_error(lines_list)")
		lines_list = infile
		max_error = 0

		for line in lines_list:
			line = line.strip('\n')

			if line.startswith('$'):
				continue
			else:
				split_line = line.split(',')

				if float(split_line[1]) > max_error:
					max_error = float(split_line[1])
					data_max_error = line

	return max_error


def exclude_tunnel(infile, outfile):
	"""
	输出剔除tunnel附近数据后的剩余数据（需要对剔除的tunnel数据做进一步分析）
	:param infile: 经find_tunnel处理生成的info文件
	:param outfile: 剔除tunnel附近数据的剩余数据
	:return: 无return
	"""
	try:
		f_in = open(infile, encoding='UTF-8')
		f_out = open(outfile[3], mode="w")
		if_near_tunnel = 0
		tunnels_list = []
		global count_kml_file

		count_kml_file += 1
		print("Start exclude_tunnel: " + "Round" + str(count_kml_file))
		print("Now excluding tunnel: " + infile)

		# 遍历文件获取tunnel信息
		for line in f_in.readlines():
			if line.startswith("$Tunnel"):
				line = line.rstrip("\n")
				line = line.lstrip("$Tunnel: ")
				tunnel = line.split(',')
				tunnels_list.append(copy.deepcopy(tunnel))

		f_in.seek(0)  # 指针归零，方便再次使用f_in.readlines()

		# 剔除tunnel前后十秒的数据
		for line in f_in.readlines():
			if line.startswith("$"):  # 剔除非数据信息
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
						if_near_tunnel = 1
				if if_near_tunnel == 1:
					# f_out.write("Near tunnel: " + line)
					if_near_tunnel = 0
				else:
					f_out.write(line)
					continue

		print(f"End excluding tunnel: {infile}\n")

		f_out.close()
		f_in.close()
	except:
		print(f"Failed exclude tunnel: {infile}\n")


def get_info(raw_str):
	"返回kml文件中的数据"
	if raw_str.count("<TR", 3, 6) and len(raw_str) > 21:
		if "UTC时间：" in raw_str:
			info_list = raw_str.split("时间：")[1][9:17]
			if ":" in info_list:
				info_list = info_list.replace(':', '')
				return info_list

			print(raw_str.split("UTC")[1][0:2])
		# 取[0:20]目的是保证能取到全部想要的信息，之后再把多余的剔除
		if "位置误差" in raw_str:
			info_list = raw_str.split("水平:")[1][0:20]
			info_list = info_list.split("</TD>")[0]
			return info_list

		return 0
	else:
		return 0


def find_tunnel(infile, outfile):
	"""
	从kml提取数据到.info文件中
	:param infile:kml file
	:param outfile:需要的info.	time, error. $Tunnel, $data_lost
	:return:无
	"""
	global utc
	global tunnels_list
	utc = 0
	tunnels_list = []
	count_tunnel = 0
	data_lost_list = []
	count_data_lost = 0

	f_in = open(infile, encoding='UTF-8')
	f_out = open(outfile[2], mode='w')

	# 提取数据并找到tunnel
	for line in f_in.readlines():
		tunnel_time = 0
		try:
			if 'Point_Detail' not in line:  # 滤过重复的Point_Detail信息
				pass
			else:
				break

			list_out = get_info(line)
			if list_out == 0:
				continue

			else:
				try:
					# 提取数据
					if "UTC时间：" in line:
						list_out = get_info(line)

						if utc != 0:
							noe_total_sec = utc_to_sec(list_out)
							last_total_sec = utc_to_sec(utc)
							time_gap = float(noe_total_sec) - float(last_total_sec)

							if time_gap >= 2:  # tunnel内的时间
								if time_gap <= 5:  # 小于5s的tunnel按丢数处理
									print("data lost here: " + list_out)
									tunnel_start = utc
									tunnel_end = list_out
									tunnel_time = time_gap
									count_data_lost += 1
									tunnel = [tunnel_start, tunnel_end, str(tunnel_time), str(count_tunnel)]
									data_lost_list.append(copy.deepcopy(tunnel))
								else:
									print("tunnel here: " + list_out)
									if time_gap > 0:
										tunnel_time = time_gap
									elif time_gap < 0:
										tunnel_time = 24 * 3600 + time_gap
									tunnel_start = utc
									tunnel_end = list_out
									count_tunnel += 1
									tunnel = [tunnel_start, tunnel_end, str(tunnel_time), str(count_tunnel)]
									tunnels_list.append(copy.deepcopy(tunnel))

								utc = list_out
								f_out.write(utc[:] + ",")

							else:  # 非tunnel时间
								utc = list_out
								f_out.write(utc[:] + ",")
						elif utc == 0:
							utc = list_out
							f_out.write(utc[:] + ",")

					if "位置误差" in line:
						list_out = get_info(line)
						H_error = list_out
						f_out.write(str(H_error) + "\n")

				except:
					f_out.write("error[1],check: " + line)
		except:
			f_out.write("error[1],check: " + line)

	# Output Tunnel输出到log
	for tunnel in tunnels_list:
		f_out.write("$Tunnel: ")
		for data in tunnel:
			f_out.write(data)
			if data != tunnel[-1]:
				f_out.write(',')
		f_out.write("\n")

	for tunnel in data_lost_list:
		f_out.write("$data_lost: ")
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


def run(dir_path, in_file_type="kml"):
	print(dir_path)

	error_info_to_json = dict()

	error_info_to_json['cases'] = dict()

	case_names = list()  # 全部case名字的列表，case名字如：case_FILE039_Dynamic

	for root, dirs, files in os.walk(target_dir_path):
		for dir in dirs:
			if dir not in case_names:
				case_names.append(dir)

	for case_name in case_names:
		temp_dir_path = dir_path + "\\" + case_name

		truth_file_name = case_name + ".kml"

		truth_file_path = os.path.join(temp_dir_path, truth_file_name)

		try:
			os.remove(truth_file_path)  # 删除用不到的真值kml文件
		except:
			print("Failed deleting truth file, continue.")
			pass

		# 1.从kml中提取数据至info文件
		files = get_files(temp_dir_path, in_file_type)

		for file in files:
			try:
				infile = os.path.join(temp_dir_path, file)
			except:
				print("Failed reading file.")
			# Output_Files
			# 1.必须更新，否则无法生成文件 2.输出到原文件文件夹下 3.此处添加输出的文件
			f_nmea = infile[0:-3] + "nmea"
			f_satnum = infile[0:-3] + "SNum"
			f_data_from_kml = infile[0:-3] + "info"  # 提取出的文件
			f_exclude_tunnel = infile[0:-3] + "ex_t"  # 剔除隧道后的数据

			# 在此添加输出文件到out_file_list
			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel]

			split_infile = infile.split('.')

			if split_infile[1] == "kml":
				try:
					print("Reading kml: " + file)
					find_tunnel(infile, out_file_list)
					print("Done reading kml.\n")
				except:
					print("Failed read kml.")

		# 2.从info文件中剔除特定场景数据：tunnel，回放结束（未完成），大误差（未完成）
		files = get_files(temp_dir_path, "info")

		for file in files:
			try:
				infile = os.path.join(temp_dir_path, file)
			except:
				print("Failed reading file.")

			# 此处添加输出的文件
			f_nmea = infile[0:-4] + "nmea"
			f_satnum = infile[0:-4] + "SNum"
			f_data_from_kml = infile[0:-4] + "info"
			f_exclude_tunnel = infile[0:-4] + "ex_t"

			# 在此添加输出文件到out_file_list
			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel]

			try:
				max_error = get_max_error(infile)  # 统计原始info的误差

				print("\nexclude_tunnel.")

				print("Origin max error: " + str(max_error))

				exclude_tunnel(infile, out_file_list)  # 剔除tunnel数据

			except:
				print("Failed reading info.")

		# 3.print剔除指定场景后的max error
		files = get_files(temp_dir_path, "ex_t")

		for file in files:
			try:
				infile = os.path.join(temp_dir_path, file)

			except:
				print("Failed reading file.")

			# 此处添加输出的文件
			f_nmea = infile[0:-4] + "nmea"
			f_satnum = infile[0:-4] + "SNum"
			f_data_from_kml = infile[0:-4] + "info"
			f_exclude_tunnel = infile[0:-4] + "ex_t"
			f_report = target_dir_path + "\\" + "report.txt"

			# 在此添加输出文件到out_file_list
			out_file_list = [f_nmea, f_satnum, f_data_from_kml, f_exclude_tunnel, f_report]

			try:
				print("\nexclude_max_error: ")

				print("Now processing " + infile)

				duration_info = exclude_max_error(infile, out_file_list)# 统计大误差信息

				error_info = list()

				if duration_info:
					for part_n in duration_info:
						max_error = duration_info[part_n]['max_error']

						max_error_time = duration_info[part_n]['max_error_time']

						duration = duration_info[part_n]['duration']

						start_time = duration_info[part_n]['epochs'][0]

						start_time = start_time.split(',')[0]

						end_time = duration_info[part_n]['epochs'][-1]

						end_time = end_time.split(',')[0]

						# [开始时间，停止时间，时长，最值时间，最大误差]
						error_info.append(f'{start_time},{end_time},{duration},{max_error_time},{max_error}')

				else:
					error_info.append('pass')

				case_name = infile.split('\\')[-2]

				chip_name = os.path.splitext(infile.split('\\')[-1])[0]

				if case_name not in error_info_to_json['cases']:
					error_info_to_json['cases'][case_name] = dict()

				error_info_to_json['cases'][case_name][chip_name] = list()

				error_info_to_json['cases'][case_name][chip_name] = error_info
			except Exception as e:
				logger.exception(e)
				print("Failed exclude_max_error.")

		print('processing process_kml...')

		process_kml(temp_dir_path)

		print('\ndone processing process_kml.\n')

		print('end\n')

	json_file_path = os.path.join(target_dir_path, 'info.json')
	# json_file_path = r'D:\mfw\练习\test_kml\test.json'

	write_file = open(json_file_path, encoding='UTF-8', mode="w")

	data = json.dumps(error_info_to_json, indent=4)

	write_file.write(data)

	write_file.close()

# # 4.重新统计一遍MAX ERROR


def if_pass(dur_info_list, outfiles, filename, case_file_name):
	# 判断文件是否存在，确定打开文件的mode（覆写w或追加a）
	if os.path.exists(target_dir_path + "\\" + "report.txt"):
		f_out = open(outfiles[6], mode='a')
	else:
		f_out = open(outfiles[6], mode='w')
	f_out.write(case_file_name + "\n")
	f_out.write(filename + "\n")

	for durations in dur_info_list:
		if durations == dur_info_list[1] or durations == dur_info_list[3] or durations == dur_info_list[5]:
			continue
		pos_durations = dur_info_list.index(durations)
		max_error = dur_info_list[pos_durations + 1]
		for info in durations:
			duration = info[0]
			start_time = info[2]
			# 判断
			if max_error < 5:
				f_out.write("Pass\n")

			elif max_error <= 50:
				if duration > 20:
					# f_out.write("Failed: " + "Max error " + str(max_error) + filename + "\n")
					f_out.write(f"Failed: Max err {str(max_error)}, duration {duration}, start time {start_time}\n")

				elif duration <= 20:
					f_out.write("Pass\n")

			elif max_error > 50:
				# f_out.write("Failed: " + "Max error " + str(max_error) + filename + "\n")
				f_out.write(f"Failed: Max err {str(max_error)}, duration {duration}, start time {start_time}\n")
	f_out.write("\n\n")


def count_running_time():
	"""计算运行时间"""
	running_time = end - start
	print("Running time: " + str(running_time))


def exclude_max_error(infile, outfile):
	"""
	# 迭代，剔除最大误差出现的区间
	:param infile: ex_t文件
	:param outfile: 剔除最大误差附近的数据后的文件
	:return: epochs,max_error,max_error_time,duration(count_each_epochs)
	"""
	f_in = open(infile, encoding='UTF-8')

	data_lines = f_in.readlines()  # 数据

	max_error = get_max_error(infile)
	if max_error < 5:
		print("Done Interation, max error: " + str(max_error) + "\n")
		return 0

	error_data_dic = dict()
	header = True

	if max_error >= 5:
		# 开始剔除
		for line in data_lines:
			line = line.strip('\n')
			now_error = float((line.split(','))[1])

			if now_error <= 5:
				header = True
			else:
				if header:
					header = False
					key_num = len(error_data_dic) + 1
					temp_key = f"Part {key_num}"
					error_data_dic[temp_key] = dict()
					error_data_dic[temp_key]['epochs'] = list()

				error_data_dic[temp_key]['epochs'].append(line)
	else:
		print("Unexpected error in exclude_max_error, max_error: " + str(max_error) + "\n")


	# 求最大值
	for part_n in error_data_dic:
		for epoch in error_data_dic[part_n]['epochs']:
			error_value = float(epoch.split(',')[1])
			error_time = epoch.split(',')[0]
			# 初次时，初始化
			if error_data_dic[part_n]['epochs'].index(epoch) == 0:
				last_error_value = 0
				part_n_max_error = 0

			if error_value > last_error_value:
				part_n_max_error = error_value
				last_error_value = error_value
				max_error_time = error_time

		if part_n_max_error:
			error_data_dic[part_n]['max_error'] = part_n_max_error
			error_data_dic[part_n]['max_error_time'] = max_error_time
			error_data_dic[part_n]['duration'] = len(error_data_dic[part_n]['epochs'])

	if 1:  # 删除问题较小的误差片段
		temp_dict = copy.deepcopy(error_data_dic)
		for part_n in temp_dict:
			max_error = error_data_dic[part_n]['max_error']
			duration = error_data_dic[part_n]['duration']
			if max_error <= 10 and duration <= 20:
				del error_data_dic[part_n]
				continue
			if max_error <= 20 and duration < 3:
				del error_data_dic[part_n]
				continue

	f_in.close()
	return error_data_dic


if __name__ == '__main__':
	start = time.perf_counter()
	"""以下为主要代码"""
	# copy
	try:
		print("Start copying file...")
		copy_share_file()
		print(dir_names)
		time.sleep(1)
		print('wating for copy_share_file() to complete...')
		time.sleep(60)
	except Exception as error:
		print("Failed copying file!")
		logger.exception(error)

	# 处理
	try:
		abandon_list = 0
		print("Start processing...")
		dir_path = target_dir_path
		# r"D:\mfw\练习\kml\38"
		in_file_type = "kml"
		run(dir_path, in_file_type)
		copy_TruthAndExcel(share_dir_path,target_dir_path)
		print("End processing.")

	except Exception as error:
		logger.exception(error)

	"""主要代码到此为止"""
	end = time.perf_counter()
	count_running_time()