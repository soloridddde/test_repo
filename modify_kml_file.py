import os.path


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

				insert_pos = point_info_list.index(line) - 3

				point_info_list.insert(insert_pos, insert_info)

				break


	if 1:
		for line in point_info_list:
			if 'visibility' in line:
				temp_pos = point_info_list.index(line)
				del point_info_list[temp_pos]

		for line in point_info_list:
			if '<Placemark>' in line:
				# insert_info = f"\t\t\t<visibility>0</visibility>\n"  # 使点不可见
				insert_info = f"\t\t\t<visibility>1</visibility>\n"  # 使点可见

				insert_pos = point_info_list.index(line) + 1

				point_info_list.insert(insert_pos, insert_info)

				break



	return point_info_list


def create_dir_not_exist(dirpath):
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

	create_dir_not_exist(result_kml_root)

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

	create_dir_not_exist(result_kml_root)

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


del_folder(source_kml_path=r'C:\Users\Administrator\Desktop\1_BK_L1_0001_diff - 副本.kml')

insert_name(source_kml_path=r'C:\Users\Administrator\Desktop\1_BK_L1_0001_diff - 副本.kml')