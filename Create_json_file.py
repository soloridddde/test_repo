# 自动生成脚本

import os


target_dir_path = 'D:\\mfw\\练习\\test_kml'
json_file_path = os.path.join(target_dir_path, "Error.json")
cases_in_json = list()  # 脚本中的所有case


def get_file_names():
	case_names = list()
	for root, dirs, files in os.walk(target_dir_path):
		for dir in dirs:
			if dir not in case_names:
				case_names.append(dir)
	return case_names


def write_json_file(infile, error_dict):
	"""
	写error脚本文件
	:param infile:
	:param error_dict:
	:return:
	"""

	case_name = infile.split('\\')[-2]
	chip_name = os.path.splitext(infile.split('\\')[-1])[0]

	write_file = open(json_file_path, encoding='UTF-8', mode="w")
	for part_n in error_dict:
		max_error = error_dict[part_n]['max_error']
		max_error_time = error_dict[part_n]['max_error_time']
		duration = error_dict[part_n]['duration']
		error_info = [max_error_time, max_error, duration]  # [起始时间，结束时间，时长，最大误差]



if __name__ == '__main__':
	try:
		write_json_file()
	except Exception as e:
		print("Failed creating json file!")
		print(e)
		print(e.__traceback__.tb_frame.f_globals["__file__"])
		print(e.__traceback__.tb_lineno)