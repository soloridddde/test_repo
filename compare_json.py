import json
import os.path

from Fuction import utc_to_sec
from Fuction import sec_to_utc
from interval import Interval
from loguru import logger


def read_json_cfg(config_path):
	try:
		with open(config_path) as f:
			ret = json.load(f)
	except Exception as e:
		logger.exception(e)
		print("配置文件格式错误，请检查！")
		return -1
	return ret


def compare_json(ref_json_fpath, test_json_path):
	"""
	将生成的json file与参考ref_json_fpath对比
	:param test_json_path: 测试文件
	:param ref_json_fpath: 参考文件
	:return: none
	"""
	ref_info = read_json_cfg(ref_json_fpath)

	test_info = read_json_cfg(test_json_path)

	for case in test_info["cases"]:
		for chip in test_info["cases"][case]:
			if 'BK' in chip or 'bk' in chip:  # 只比较bk数据
				pass
			else:
				continue

			for error_info in test_info["cases"][case][chip]:
				if error_info == 'pass':
					continue

				total_score = 0  		# init

				duration_score = 0  	# init

				max_error_score = 0  	# init

				temp_error_info = str(error_info).split(',')

				test_start_time = temp_error_info[0]

				test_end_time = temp_error_info[1]

				test_duration = float(temp_error_info[2])

				test_max_err_at = temp_error_info[3]

				test_max_error = float(temp_error_info[4])

				mid_time_sec = (utc_to_sec(test_start_time) + utc_to_sec(test_end_time)) / 2

				mid_time_utc = sec_to_utc(mid_time_sec)

				for ref_error_info in ref_info["cases"][case][chip]:
					if ref_error_info == 'pass':
						continue

					temp_ref_error_info = str(ref_error_info).split(',')

					ref_start_time = temp_ref_error_info[0]

					ref_end_time = temp_ref_error_info[1]

					ref_duration = float(temp_ref_error_info[2])

					ref_max_err_at = temp_ref_error_info[3]

					ref_max_error = float(temp_ref_error_info[4])

					if mid_time_utc in Interval(ref_start_time, ref_end_time):  # match
						if test_duration <= ref_duration:  # score duration
							pass
						else:
							if test_duration <= 1.1*ref_duration:  		# slight
								duration_score += 0.5

							elif test_duration <= 1.2:  				# medium
								duration_score += 1

							else:  										# terrible
								duration_score += 10

						if test_max_error <= ref_max_error:  # score max_error
							pass
						else:
							if test_max_error <= 1.2*ref_max_error:		# slight
								max_error_score += 0.5

							elif test_max_error <= 1.4*ref_max_error:   # medium
								max_error_score += 1

							else:  										# terrible
								max_error_score += 10

						# if test_avr_error < ref_avr_error:

						total_score = duration_score + max_error_score
					else:  												# not match
						if ref_info["cases"][case][chip].index(ref_error_info) + 1 == len(
								ref_info["cases"][case][chip]):
							total_score = 100
						else:
							continue

					temp_test_info = error_info

					index_cur_error_info = test_info["cases"][case][chip].index(error_info)

					if total_score == 0:
						temp_test_info = temp_test_info + f'    {duration_score},{max_error_score},{total_score},pass'
						test_info["cases"][case][chip][index_cur_error_info] = temp_test_info
						break
					elif total_score < 10:
						temp_test_info = temp_test_info + f'    {duration_score},{max_error_score},{total_score},slight'
						test_info["cases"][case][chip][index_cur_error_info] = temp_test_info
						break
					elif total_score <= 20:
						temp_test_info = temp_test_info + f'    {duration_score},{max_error_score},{total_score},medium'
						test_info["cases"][case][chip][index_cur_error_info] = temp_test_info
						break
					elif total_score <= 200:
						temp_test_info = temp_test_info + f'    {duration_score},{max_error_score},{total_score},terrible'
						test_info["cases"][case][chip][index_cur_error_info] = temp_test_info
						break
					else:
						print('unexpercted failure')
						break

	compare_result = json.dumps(test_info, indent=4)

	compare_result_fpath = os.path.splitext(test_json_path)[0] + 'compare_result.json'

	compare_result_file = open(compare_result_fpath, mode='w', encoding='utf-8')

	compare_result_file.write(compare_result)
	print('end of compar_json')
				# "134752,134818,27,134810,16.868"

ref_json_fpath = r"D:\mfw\练习\test_kml_backup\0.2.3.3\505\test.json"

test_json_fpath = r"D:\mfw\练习\test_kml\info.json"
# test_json_fpath = r"D:\mfw\练习\test_kml_backup\0.2.3.3\495\test.json"

try:
	compare_json(ref_json_fpath, test_json_fpath)
except Exception as error:
	logger.exception(error)