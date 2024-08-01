# encoding=utf-8
import json
import os
import copy
import Fuction

from Fuction import utc_to_sec
from Fuction import sec_to_utc
from interval import Interval
from loguru import logger


def add_rms(info_dic):
	"""
	在info_dic中计算并添加rms信息
	:param info_dic: duration_info dict
	:return: duration_info dict with rms info
	"""
	for part_n in info_dic:  # 每一段误差集合
		error_list = list()
		for epoch in info_dic[part_n]['epochs']:
			# epoch_time = epoch[0]
			epoch_error = float(epoch[1])
			error_list.append(epoch_error)
		cur_rms = Fuction.get_rms(error_list)
		if cur_rms:
			info_dic[part_n]['rms'] = cur_rms
		else:
			info_dic[part_n]['rms'] = -1


def get_error_info(infile, start_time, end_time):
	"""
	# 迭代，分割出大误差出现的区间
	:param infile: ex_t文件
	:return: epochs,max_error,max_error_time,duration(count_each_epochs)
	"""
	print("Now processing " + infile)

	error_data_dic = dict()

	raw_data = list()

	f_in = open(infile, encoding='UTF-8')

	data_lines = f_in.readlines()  # 数据

	# 找出指定时间段的数据加入raw_data
	for line in data_lines:
		line = line.strip('\n')
		now_time = float((line.split(','))[0])
		now_error = float((line.split(','))[1])

		if now_time in Interval(start_time, end_time):
			raw_data.append(line)

	# 开始剔除
	header = True
	for line in raw_data:
		line = line.strip('\n')
		now_error = float((line.split(','))[1])

		if header:
			header = False
			key_num = len(error_data_dic) + 1
			temp_key = f"Part {key_num}"
			error_data_dic[temp_key] = dict()
			error_data_dic[temp_key]['epochs'] = list()

		line_list = line.split(',')
		error_data_dic[temp_key]['epochs'].append(line_list)
		# error_data_dic[temp_key]['epochs'].append(line)

	# 求最大值
	for part_n in error_data_dic:
		for epoch in error_data_dic[part_n]['epochs']:
			error_value = float(epoch[1])
			error_time = epoch[0]
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

	f_in.close()
	# 添加rms信息
	add_rms(error_data_dic)

	print("End processing " + infile)
	return error_data_dic


def check_other_chip(start_time, end_time, case, chip):
	if '_L1L5_' in chip:  # 区分单双频,此时输入的chip为BK chip，需要重新遍历当前case下的目录，确定infile，然后还要统计infile的情况：比如 对比机的名称：对应的max_error, rms
		fq_type = 2
	elif '_L1_' in chip:
		fq_type = 1
	else:
		print('failed check_other_chip, chip name error.')
	# 遍历当前case文件夹，匹配对比机单双频
	cur_path = os.path.join(test_root, case)
	for file in os.listdir(cur_path):
		if fq_type == 1:
			if '_L1_' in file:
				if '.ex_t' in file and 'BK' not in file:
					infile = os.path.join(cur_path, file)

					error_info = get_error_info(infile, float(start_time), float(end_time))
					if error_info.__len__() == 1:
						max_error = error_info['Part 1']['max_error']
					else:
						raise Exception(f'error_info字典长度异常:{cur_path},长度：{error_info.__len__()},'
										f'起止时间：{start_time}-{end_time}')

		elif fq_type == 2:
			if '_L1L5_' in file or '_L1L2_' in file:
				if '.ex_t' in file and 'BK' not in file:  # 为什么要用ex_t
					infile = os.path.join(cur_path, file)

					error_info = get_error_info(infile, float(start_time), float(end_time))
					if error_info.__len__() == 1:
						max_error = error_info['Part 1']['max_error']
					else:
						raise Exception(f'error_info字典长度异常:{cur_path},长度：{error_info.__len__()},'
										f'起止时间：{start_time}-{end_time}')



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

				for ref_error_info in ref_info["cases"][case][chip]:
					if ref_error_info == 'pass':
						continue

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
									check_other_chip(test_start_time, test_end_time, case, chip)
									max_error_score += 10

							elif test_max_error <= 30:
								if test_max_error <= 1.3 * ref_max_error:  # slight
									max_error_score += 0.5

								elif test_max_error <= 1.6 * ref_max_error:  # medium
									max_error_score += 1

								else:  # terrible
									check_other_chip(test_start_time, test_end_time, case, chip)
									max_error_score += 10

							else:
								if test_max_error <= 1.2 * ref_max_error:  # slight
									max_error_score += 0.5

								elif test_max_error <= 1.4 * ref_max_error:  # medium
									max_error_score += 1

								else:  # terrible
									check_other_chip(test_start_time, test_end_time, case, chip)
									max_error_score += 10

						# 检查对比机

						# 对比rmse
						# if test_avr_error < ref_avr_error:

						total_score = duration_score + max_error_score
					else:  												# not match
						if ref_info["cases"][case][chip].index(ref_error_info) + 1 == len(
								ref_info["cases"][case][chip]):  # 若已经遍历到最后一个还是不匹配，则打分100
							check_other_chip(test_start_time, test_end_time, case, chip)
							total_score = 100
						else:  # 若还没遍历完，继续尝试匹配
							continue

					temp_test_info = error_info

					index_cur_error_info = test_info["cases"][case][chip].index(error_info)

					# 评价
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

	compare_result_fpath = os.path.splitext(test_json_path)[0] + 'compare_result.json'

	compare_result_file = open(compare_result_fpath, mode='w', encoding='utf-8')

	compare_result_file.write(compare_result)
	print('end of compar_json')
				# "134752,134818,27,134810,16.868"

ref_json_fpath = r"D:\mfw\练习\test_kml_backup\0.2.3.3\505\test.json"

test_json_fpath = r"D:\mfw\练习\test_kml\info.json"
# test_json_fpath = r"D:\mfw\练习\test_kml_backup\0.2.3.3\495\test.json"
test_root = test_json_fpath.replace('info.json', '')

try:
	compare_json(ref_json_fpath, test_json_fpath)
except Exception as error:
	logger.exception(error)

