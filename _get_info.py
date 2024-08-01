import copy


def get_info(raw_str):
	"返回kml文件中的数据"
	if raw_str.count("<TR", 3, 6) and len(raw_str) > 21:
		if "UTC时间：" in raw_str:
			info_list = raw_str.split("时间：")[1][9:17]
			if ":" in info_list:
				info_list = info_list.replace(':', '')
				return info_list

			print(raw_str.split("UTC")[1][0:2])
		# 取[0:20]目的是保证能取到全部想要的信息，之后再想办法把多余的剔除
		if "位置误差" in raw_str:
			info_list = raw_str.split("水平:")[1][0:20]
			info_list = info_list.split("</TD>")[0]
			return info_list

		# if "XXXX" in raw_str:
		#
		return 0
	else:
		return 0


def find_tunnel(infile, outfile):
	"从kml提取数据到.info文件中"
	# start_time; end_time 是为了截取起止时间附近的大误差。
	f_in = open(infile, encoding='UTF-8')
	# 合并入大代码时要把outfile改为outfile[2],即.info文件
	f_out = open(outfile, mode='w')
	start_time = 0
	end_time = 0

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
					if "UTC时间：" in line:
						list_out = get_info(line)
						if utc == 0:
							start_time = list_out

						not_tunnel_time = float(list_out) - float(utc)
						# tunnel内的时间：
						if not_tunnel_time not in [41, 4041] and not_tunnel_time >= 2:

							if not_tunnel_time <= 5:
								print("data lost here: " + list_out)
							elif utc != 0:
								print("tunnel here: " + list_out)

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
										f_out.write("Long Tunnel! Check: " + "now time" + list_out +
													"	start time: " + str(utc) + "\n")

										# 发现长隧道后，要继续统计ex_t，则注释此条
										tunnel_time = "Error"

								tunnel_start = utc
								tunnel_end = list_out
								count_tunnel += 1
								tunnel = [tunnel_start, tunnel_end, str(tunnel_time), str(count_tunnel)]
								tunnels_list.append(copy.deepcopy(tunnel))

							utc = list_out
							f_out.write(utc[:] + ",")
						# 非tunnel时间：
						else:
							utc = list_out
							f_out.write(utc[:] + ",")

					if "位置误差" in line:
						list_out = get_info(line)
						H_error = list_out
						f_out.write(H_error + "\n")
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


if __name__ == '__main__':
	#infile = r"D:\mfw\练习\test_kml\1_BK_L1_Diff.kml"
	infile = r"D:\mfw\练习\test_kml\1_BK_L1_Diff.kml"
	outfile = r"D:\mfw\练习\test_kml\1_BK_L1.info"
	find_tunnel(infile, outfile)