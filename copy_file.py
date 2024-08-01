import os

share_user='mengfo.wang'

share_password='w980910wmfv3'

share_file_host='\\\\192.168.60.72'
#\\192.168.60.72\Test\TestData(72)

share_dir_path='\\\\192.168.60.72\\Test\\TestData(72)\\166022355'#总文件夹地址
#share_file_path='\\\\192.168.60.10\\mengfo.wang\\test_kml\\*.kml' \
				#1_BK_L1_Diff.kml'

target_dir_path='D:\\mfw\\练习\\test_kml'

dir_names = []

excluded_case = ['FILE068', 'FILE069', 'FILE070', 'FILE071', 'FILE076', 'FILE077', 'FILE078', 'FILE079', 'FILE080',
				 'FILE083', 'FILE084', 'FILE085', 'FILE086', 'FILE087'
				 ]


def create_dirs():
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
							dir_names.append(dir)

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

	permission_cmd=f'net use {share_file_host} {share_user} /user:{share_password}'

	print(permission_cmd)

	permission_result=os.popen(permission_cmd)

	print(permission_result.read())

	create_dirs()

	for dir in dir_names:

		share_file_path = share_dir_path + "\\" + dir + "\\Compared\\*.kml"

		target_file_path = target_dir_path + "\\" + dir

		copy_cmd=f'xcopy /y {share_file_path} {target_file_path}'

		print(copy_cmd)

		copy_result=os.popen(copy_cmd)

		print(copy_result.read())

if __name__ == '__main__':
	copy_share_file()
	print(dir_names)