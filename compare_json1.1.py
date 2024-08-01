# encoding=utf-8
import json
import os.path

from Fuction import utc_to_sec
from Fuction import sec_to_utc
from interval import Interval
from loguru import logger


excluded_case = ['FILE138', 'FILE140', 'FILE147', 'FILE149', 'FILE154', 'FILE156', 'FILE157', 'FILE160',
				 'FILE148', 'FILE149', 'FILE154', 'FILE155', 'FILE158','FILE159', 'FILE162', 'FILE163', 'FILE164',
				 'FILE165', 'FILE166', 'FILE167', 'FILE168', 'FILE169', 'FILE170', 'FILE177']


def read_json_cfg(config_path):
	try:
		with open(config_path) as f:
			ret = json.load(f)
	except Exception as e:
		logger.exception(e)
		print("配置文件格式错误，请检查！")
		return -1
	return ret


def compare_json(ref_json, test_json):
	"""
	将生成的json file与参考ref_json对比
	:param test_json: 测试文件
	:param ref_json: 参考文件
	:return: none
	"""
	ref_info = read_json_cfg(ref_json)

	test_info = read_json_cfg(test_json)

	for case in test_info["cases"]:

		# 剔除不对比的场景
		exflag = False  # False代表不跳过此case
		for ex_case in excluded_case:
			if ex_case in case:
				exflag = True
				break
		if exflag:  # 跳过此case
			continue

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

				# 初始化各项数据
				# ini test data
				temp_error_info = str(error_info).split(',')

				test_start_time = temp_error_info[0]  # 误差起始时间

				test_end_time = temp_error_info[1]  # 误差结束时间

				test_duration = float(temp_error_info[2])  # 持续时间

				test_max_err_at = temp_error_info[3]  # 最大误差出现时刻

				test_max_error = float(temp_error_info[4])  # 最大误差

				test_rms = float(temp_error_info[5])  # 均方根误差rmse

				mid_time_sec = (utc_to_sec(test_start_time) + utc_to_sec(test_end_time)) / 2

				mid_time_utc = sec_to_utc(mid_time_sec)

				# 对比某特定芯片的数据。使用场景：八块我们的板子进行compare某一块板子
				# for ref_error_info in ref_info["cases"][case]['4_BK_L1L5_23A_0006_diff']:
				# 	if ref_error_info == 'pass':
				# 		continue

				for ref_error_info in ref_info["cases"][case][chip]:

					if ref_error_info == 'pass':
						total_score = 100
					else:
						# ini ref data
						temp_ref_error_info = str(ref_error_info).split(',')

						ref_start_time = temp_ref_error_info[0]

						ref_end_time = temp_ref_error_info[1]

						ref_duration = float(temp_ref_error_info[2])

						ref_max_err_at = temp_ref_error_info[3]

						ref_max_error = float(temp_ref_error_info[4])

						# ref_rms = float(temp_ref_error_info[5])

						# 开始对比
						if mid_time_utc in Interval(ref_start_time, ref_end_time):  # match
							# 对比持续时长
							if test_duration <= ref_duration:  # score duration
								pass
							else:
								if test_duration <= 1.3 * ref_duration:  # slight
									duration_score += 0.5

								elif test_duration <= 1.5:  # medium
									duration_score += 1

								else:  # terrible
									duration_score += 10

							# 对比最大误差
							if test_max_error <= ref_max_error:  # score max_error
								pass
							else:
								if test_max_error <= 10:

									if test_max_error <= 1.5 * ref_max_error:  # slight
										max_error_score += 0.5

									# elif test_max_error <= 2 * ref_max_error:  # medium
									# 	max_error_score += 1
									else:  # terrible
										max_error_score += 10

								elif test_max_error <= 30:
									if test_max_error <= 1.3 * ref_max_error:  # slight
										max_error_score += 0.5

									elif test_max_error <= 1.6 * ref_max_error:  # medium
										max_error_score += 1

									else:  # terrible
										max_error_score += 10

								else:
									if test_max_error <= 1.2 * ref_max_error:  # slight
										max_error_score += 0.5

									elif test_max_error <= 1.4 * ref_max_error:  # medium
										max_error_score += 1

									else:  # terrible
										max_error_score += 10

							# 对比rmse
							# if test_avr_error < ref_avr_error:

							total_score = duration_score + max_error_score
						else:  												# not match
							# if ref_info["cases"][case]['4_BK_L1L5_23A_0006_diff'].index(ref_error_info) + 1 == len(
							# 		ref_info["cases"][case]['4_BK_L1L5_23A_0006_diff']):
							# 	total_score = 100
							if ref_info["cases"][case][chip].index(ref_error_info) + 1 == len(
									ref_info["cases"][case][chip]):  # 判断当前的ref_error_info是否已循环到最后
								total_score = 100  # 循环到最后还不匹配，则打分100分
							else:
								continue

					temp_test_info = error_info

					index_cur_error_info = test_info["cases"][case][chip].index(error_info)

					if total_score == 0:
						# temp_test_info = temp_test_info + f'    {duration_score},{max_error_score},{total_score},pass'
						# test_info["cases"][case][chip][index_cur_error_info] = temp_test_info
						break
					elif total_score < 10:
						# temp_test_info = temp_test_info + f'    {duration_score},{max_error_score},{total_score},slight'
						# test_info["cases"][case][chip][index_cur_error_info] = temp_test_info
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

	compare_result_fpath = os.path.splitext(test_json)[0] + 'compare_result23B.json'

	compare_result_file = open(compare_result_fpath, mode='w', encoding='utf-8')

	compare_result_file.write(compare_result)
	print('end of compare_json')

# 22A
# ref_json_fpath = r"D:\mfw\练习\ref\22A.json"
# test_json_fpath = r"D:\mfw\练习\test_kml\info.json"


# 23A
# ref_json_fpath = r"C:\mengfo.wang\test\data\SPPReplayAnalyze\ref\23A.json"
# test_json_fpath = r"C:\mengfo.wang\test\data\SPPReplayAnalyze\test_kml\info.json"

# 23A
ref_json_fpath = r"C:\mengfo.wang\test\data\SPPReplayAnalyze\ref\23B.json"
test_json_fpath = r"C:\mengfo.wang\test\data\SPPReplayAnalyze\test_kml\info.json"

try:
	compare_json(ref_json_fpath, test_json_fpath)
except Exception as error:
	logger.exception(error)
