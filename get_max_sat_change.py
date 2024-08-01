import os
import time
result_path = "D:\\mfw\\1_test\\cont\\nmea"
report_path = "D:\\mfw\\1_test\\cont\\report"


def get_change_duration():
	fname_list = []
	two_hr_list = []

	files_list = os.listdir(result_path)
	for file in files_list:
		if "SNum" in file:
			fname_list.append(file)
	if not fname_list:
			log("failure: get_max_sat_change()\n")
			print("failure: get_max_sat_change()")

	for file in fname_list:
		f_path = os.path.join(result_path, file)
		f_in = open(f_path, encoding="utf-8")
		for line in f_in.readlines():
			if "UTC" in line:
				utc_time = (line.split())[1]
				if len(utc_time) == 9:
					utc_hour = utc_time[:2]
					if int(utc_hour) < 1:
						start_time = utc_time.replace(utc_hour, "23")
						end_time = utc_time.replace(utc_time[:2, "00"])
						two_hr_list.append([start_time, end_time])

					elif 23 > int(utc_hour) >= 1:
						start_time = utc_time.replace(utc_hour, str(int(utc_hour) - 1).zfill(2))
						end_time = utc_time.replace(utc_hour, str(int(utc_hour) + 1).zfill(2))
						two_hr_list.append([start_time, end_time])

					elif int(utc_hour) >= 23:
						start_time = utc_time.replace(utc_hour, str(int(utc_hour) - 1).zfill(2))
						end_time = utc_time.replace(utc_time[0:2], "00")
						two_hr_list.append([start_time, end_time])

				else:
					log(f"failure, check utc length: {utc_time}\n")
	print(two_hr_list)


def log(info):
	local_time = time.strftime("%Y-%M-%D %H:%M:%S")

	if os.path.exists(report_path + "\\" + "run_log.txt"):
		f_out = open(os.path.join(report_path, "run_log.txt"), mode='a')
	else:
		f_out = open(os.path.join(report_path, "run_log.txt"), mode='w')

	f_out.write(f"{local_time}	{str(info)}")
	f_out.close()


get_change_duration()