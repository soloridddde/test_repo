# encoding=utf-8
import copy
import json
import os
import shutil
import time
import Fuction
import logging
from interval import Interval
# from loguru import logger

#####
# 能完成基本的统计判断，能进行基本的对比，暂不支持和对比机对比；tunnel附近的数据未参加对比
# 增加了rms


# 设置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 常量定义
SHARE_FILE_HOST = r'\\192.168.60.217'
SHARE_DIR = r'\\192.168.60.217\Exchang_in\Common\WTR_LOG\24.03.30_166024135\data_spp_replay'
LOCAL_RESULTS_DIR = r'C:\mengfo.wang\test\data\SPPReplayAnalyze\test_kml'

COPY_T = 5  # 假设的拷贝等待时间
DIR_NAMES = []  # 假设的目录名称列表
share_user = 'mengfo.wang'
share_password = 'w980910wmfv8'

# 当if_copy为True时进行拷贝远程数据到本地进行处理；False则不拷贝，处理本地数据
if_copy = True  # 是否从share_dir拷贝
process_local_cases = True
print_runlog = True
copy_t = 120

# for replay




# for debug
# share_file_host = r'\\192.168.60.81'
# share_dir = r'C:\mengfo.wang\test\data\SPPReplayAnalyze\test_data_src'
# local_results_dir = r'C:\mengfo.wang\test\data\SPPReplayAnalyze\test_data_reslt'

# for INS
# share_file_host = r'\\192.168.60.81'
# share_dir = r'C:\Users\12587\Desktop\路测数据'
# local_results_dir = r'C:\mengfo.wang\test\data\SPPReplayAnalyze\test_data_reslt'

excluded_case = ['FILE068', 'FILE069', 'FILE070', 'FILE071', 'FILE076', 'FILE077', 'FILE078', 'FILE079', 'FILE080',
                 'FILE083', 'FILE084', 'FILE085', 'FILE086', 'FILE087']
local_existed_cases = []
utc = 0
tunnels_list = []


def myprint(log_str):
    if print_runlog is False:
        pass
    else:
        print(log_str)


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

        share_password = 'w980910wmfv8'

    permission_cmd = f'net use {share_file_host}  {share_password} /user:{share_user}'

    permission_result = os.popen(permission_cmd)

    print(permission_result.read())


def copy_file(file_path, target_dir):
    """
    拷贝文件到指定路径下
    :param file_path: 被拷贝的文件路径（包括后缀的绝对路径）
    :param target_dir: 目标文件夹的路径
    :return: 无
    """
    if not os.path.exists(os.path.dirname(file_path)):
        raise Exception(f"Source directory not exist! Check:{file_path}")

    copy_cmd = f'xcopy /y {file_path} {target_dir}'

    # print(copy_cmd)

    copy_result = os.popen(copy_cmd)


# print(copy_result.read())


def copy_TruthAndExcel(remote_dir, local_dir):
    for item in os.listdir(local_dir):
        item_path = os.path.join(local_dir, item)
        if os.path.isdir(item_path):
            try:
                cur_local_dir = os.path.join(local_dir, item, 'Compare')

                cur_remodir = os.path.join(remote_dir, item, 'Compared')
            except Exception as e:
                logger.exception(e)
                continue  # 路径拼接失败，预计为local_root, dir下无'Compare'文件夹

            if os.path.exists(cur_local_dir):
                existed_lf = os.listdir(cur_local_dir)  # existed local file
                existed_remof = os.listdir(cur_remodir)  # existed remote file
                for file in existed_remof:
                    if file in existed_lf:
                        continue
                    else:
                        file_path = os.path.join(cur_remodir, file)
                        copy_file(file_path, cur_local_dir)
        else:
            pass


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

        # del_folder(path)
        # copy_file(path, os.path.join(dir_path, 'Compare'))

        insert_name(path)
    myprint('\nDone processing process_kml().\n')


def modify_point_info(point_info_list):
    """
    增删改point相关信息
    :param point_info_list: 从<Placemark>到</Placemark>的kml点信息，句尾带换行符
    :return:修改后的列表mpinfo_list
    """

    # 插入时间作为点名
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

    # 修改点的可见性（折叠 or 展开）
    if 1:
        for line in point_info_list:
            if 'visibility' in line:
                temp_pos = point_info_list.index(line)
                del point_info_list[temp_pos]

        for line in point_info_list:
            if '<Placemark>' in line:
                insert_info = f"\t\t\t<visibility>0</visibility>\n"  # 使点不可见
                # insert_info = f"\t\t<visibility>1</visibility>\n"  # 使点可见

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
    result_kml_path = result_kml_root + '\\' + result_kml_name

    create_dir(result_kml_root)

    loopIndicator = 1
    while True:
        try:
            sc_file = open(source_kml_path, encoding='utf-8')
            res_file = open(result_kml_path, encoding='utf-8', mode='w')
            break
        except PermissionError:
            if loopIndicator:
                loopIndicator = 0
                print('In loop, waiting...')
            continue
    # 根据条件跳过第一个folder
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
    myprint('del_folder() completed!')


def insert_name(source_kml_path):
    """
    插入信息：将utc作为点名，方便搜索。如121200。逻辑：根据<Placemark>搜索点信息，对点进行操作
    :param source_kml_path: kml文件路径
    :return: none
    """

    # 新建kml文件，用于存放插入点名后的文件
    kml_name = os.path.split(source_kml_path)[1]  # 文件名
    src_kml_dir = os.path.split(source_kml_path)[0]  # 源文件目录
    src_kml_path = src_kml_dir + '\\' + kml_name  # 源文件路径
    result_kml_dir = os.path.join(src_kml_dir, 'Compare')  # 结果文件目录
    result_kml_path = result_kml_dir + '\\' + kml_name  # 结果文件路径
    create_dir(result_kml_dir)

    res_list = list()  # 结果list

    is_point_info = 0  # 状态开关，判断是否为点信息。1：是；2：不是。

    mark_pos = 0

    sc_file = open(src_kml_path, mode='r', encoding='utf-8')
    lines_list = sc_file.readlines()

    for line in lines_list:
        if 'Point_Detail' in line:
            mark_pos = lines_list.index(line)

    if mark_pos == 0:
        print("Warning: insert_name(),未找到关键字'Point_Detail',考虑是否因为kml文件格式修改了？")

    reached_mark = False
    marked_line = lines_list[mark_pos]
    for line in lines_list:
        if not reached_mark:
            cur_line = line
            if lines_list[mark_pos] == cur_line:
                reached_mark = True

        if reached_mark:
            # 以<Placemark>开头，</Placemark>结尾采集一个点的一整段数据，存到point_info_list
            if "<Placemark>" in line:  # <Placemark> 点数据起始 标志行

                is_point_info = 1

                point_info_list = list()

                point_info_list.append(line)
                continue

            # 到点的结尾，开始正式处理point_info_list中的数据
            if "</Placemark>" in line:  # </Placemark> 点数据终止 标志行

                is_point_info = 0

                point_info_list.append(line)

                modify_point_info(point_info_list)

                # 剔除错误设置的线条不可视
                for tmp_line in point_info_list:
                    if 'LinePath' in tmp_line:
                        del point_info_list[point_info_list.index(tmp_line) - 1]

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
    myprint('insert_name completed!')


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
            for item in os.listdir(source_dir):
                if os.path.isdir(source_dir + "\\" + item):
                    dir = item
                    # 对于固定格式的文件名
                    if '_' in dir:
                        # if dir.startswith("case_FILE") and dir.split('_')[1] not in excluded_case:
                        if dir.split('_')[1] not in excluded_case:  # 提取关键词"FILExxx"
                            if dir not in dir_names:
                                dir_names.append(copy.deepcopy(dir))

                                # 创建文件夹
                                cur_dir = os.path.join(target_dir, dir)
                                try:
                                    # os.mkdir(target_dir + "./" + dir)
                                    # print(target_dir + "\\" + dir + " created!")
                                    os.mkdir(cur_dir)
                                    print(cur_dir + " created!")
                                except:
                                    # print(f"{cur_dir} already existed: ")
                                    pass

                    # 对于随机的文件名
                    else:
                        dir_names.append(copy.deepcopy(dir))

                        # 创建文件夹
                        try:
                            os.mkdir(target_dir + "./" + dir)
                            print(target_dir + "\\" + dir + " created!")
                        except:
                            # print(f"{cur_dir} already existed: ")
                            pass
        else:
            print("Target directory path not exist, check: " + target_dir)
    else:
        print("Source directory path not exist! Check: " + source_dir)

    print("End of Creating subDirs!")


def start_copy_share_file():
    """
    从share_dir拷贝所有kml文件到local_results_dir
    :return: 无return
    """
    print("Start copying file...")

    access_to_host(share_file_host)  # 获取目标地址访问权限

    create_dirs(share_dir, local_results_dir)  # 创建同名的文件夹

    for dir in dir_names:
        if dir not in local_existed_cases:
            share_file_path = share_dir + "\\" + dir + "\\Compared\\*.kml"  # 拷贝所有kml文件

            target_file_path = local_results_dir + "\\" + dir

            copy_file(share_file_path, target_file_path)


def get_local_cases(target_dir):
    """
    获取路径下dir文件名
    :param target_dir: 目标路径
    :return: cases list
    """
    cases_list = list()

    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)

        if os.path.isdir(item_path):
            cases_list.append(item)

    return cases_list


def get_max_error(infile):
    """
    输入文件或者行列表，统计最大误差, 文件中$开头的数据将被跳过
    :param infile: 数据格式：utc, error
    :return:max position error(horizontal)
    """
    # 输入为文件
    try:
        if os.path.exists(infile):
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
        myprint("get_max_error(lines_list)")
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
        f_out = open(outfile[1], mode="w")
        if_near_tunnel = 0
        tunnels_list = []
        # global count_kml_file
        #
        # count_kml_file += 1
        # print("Start exclude_tunnel: " + "Round" + str(count_kml_file))
        myprint("Excluding tunnel: " + infile)

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

        myprint(f"End excluding tunnel: {infile}\n")

        f_out.close()
        f_in.close()
    except Exception as e:
        print(f"Failed excluding tunnel: {infile}\n")
        logger.exception(e)


def info_filter(raw_str):
    """
    返回特定数据
    :param raw_str: kml行
    :return: 0：无效数据； info_list：有效数据
    """
    if raw_str.count("<TR", 3, 6) and len(raw_str) > 21:
        if "UTC时间：" in raw_str:
            info_list = raw_str.split("时间：")[1]  # 取字段"时间："的右边
            info_list = info_list.split('</TD><TD>')[1]  # 取目标字段
            if ":" in info_list:
                info_list = info_list.replace(':', '')
                info_list = info_list.split('+')[0]  # 临时修改20230529一周后注释掉
                return info_list

            myprint(raw_str.split("UTC")[1][0:2])
        # 取[0:20]目的是保证能取到全部想要的信息，之后再把多余的剔除
        if "位置误差" in raw_str:
            info_list = raw_str.split("水平:")[1]
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
    count_tunnel = 0
    count_data_lost = 0
    tunnels_list = []
    data_lost_list = []

    loopIndicator = 1
    while True:
        try:
            f_in = open(infile, encoding='UTF-8')
            f_out = open(outfile[0], mode='w', encoding='utf-8')
            break
        except PermissionError:
            if loopIndicator:
                loopIndicator = 0
                print('In loop, waiting...')
            continue

    # 提取数据并找到tunnel
    lines = f_in.readlines()
    for line in lines:
        tunnel_time = 0
        try:
            # if 'Point_Detail' not in line:  # 滤过folder下Point_Detail信息（与Point重复）,由于Point在前，顺序读到Point_Detail
            # 	pass						# 时break即可剔除所有Point_Detail数据。
            # else:
            # 	break

            list_out = info_filter(line)

            if list_out == 0:
                continue
            else:
                try:
                    # 提取数据
                    if "UTC时间：" in line:
                        list_out = info_filter(line)

                        if utc != 0:  # 若为第一个utc数据，则走else；否则走if，计算time_gap
                            now_total_sec = Fuction.utc_to_sec(list_out)
                            last_total_sec = Fuction.utc_to_sec(utc)
                            time_gap = float(now_total_sec) - float(last_total_sec)

                            if time_gap > 1.5:  # tunnel内的时间  20230413修改，刚定位的时候time_gap可能大于1,1.5比较合理
                                if time_gap <= 5:  # 小于5s的tunnel按丢数处理
                                    myprint("outage here: " + list_out)
                                    tunnel_start = utc
                                    tunnel_end = list_out
                                    tunnel_time = time_gap
                                    count_data_lost += 1
                                    tunnel = [tunnel_start, tunnel_end, str(tunnel_time), str(count_tunnel)]
                                    data_lost_list.append(copy.deepcopy(tunnel))
                                else:
                                    myprint("tunnel here: " + list_out)
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
                        list_out = info_filter(line)
                        H_error = list_out
                        f_out.write(str(H_error) + "\n")

                except Exception as e:
                    print("Failed[1],check: " + line)
                    logger.exception(e)
        except Exception as e:
            print("Failed[1],check: " + line)
            logger.exception(e)
    # 区分tunnel和（定位中断，丢数）
    f_in.seek(0)  # 指针回到初始位置
    for tunnel in tunnels_list:
        scene_info = ''
        tn_start_time = tunnel[0]
        tn_start_time = f'{tn_start_time[0:2]}:{tn_start_time[2:4]}:{tn_start_time[4:]}'

        # tn_end_time = tunnel[1]
        # tn_end_time = f'{tn_end_time[0:2]}:{tn_end_time[2:4]}:{tn_end_time[4:]}'

        f_in.seek(0)  # 初始化指针
        kml_lines = f_in.readlines()
        for line in kml_lines:
            if 'UTC时间' not in line:
                continue
            else:
                # if tn_start_time not in line and tn_end_time not in line:
                if tn_start_time not in line:  # 按照tn_start_time来识别tunnel
                    continue
                else:
                    cur_line_index = kml_lines.index(line)
                    scene_line_index = cur_line_index + 5  # 当表格格式修改的时候会存在问题
                    scene_line = kml_lines[scene_line_index]
                    if '场景' not in scene_line:
                        print('Failed：本行无关键字‘场景’')
                        break
                    else:
                        scene_info = scene_line.split('场景：')[1]
                        scene_info = scene_info.split('</TD><TD>')[0]
                        break
        if not scene_info:
            print('Failed: Empty scene info!')

        if scene_info == '隧道':
            f_out.write("$Tunnel: ")
            for data in tunnel:
                f_out.write(data)
                if data != tunnel[-1]:
                    f_out.write(',')
            f_out.write("\n")
        else:
            f_out.write("$Outage: ")
            for data in tunnel:
                f_out.write(data)
                if data != tunnel[-1]:
                    f_out.write(',')
            f_out.write(f",{scene_info}\n")

    for tunnel in data_lost_list:
        f_out.write("$Data lost: ")
        for data in tunnel:
            f_out.write(data)
            if data != tunnel[-1]:
                f_out.write(',')
        f_out.write("\n")

    f_in.close()
    f_out.close()
    myprint("Tunnel: [start time, end time, tunnel time, count tunnels]")
    myprint(tunnels_list)
    myprint("Done reading kml.\n")


# return tunnels_list


def get_files(path, file_suffix=".csv"):
    """获取 目录下 指定后缀 的 带后缀文件名
    :param path:文件夹路径
    :param file_suffix:后缀
    """
    # 获取所有raw文件
    file_names = []
    len_suffix = len(file_suffix)
    files = os.listdir(path)
    for file in files:
        fl_dir = os.path.join(path, file)
        if os.path.isfile(fl_dir) and file[-len_suffix:] == file_suffix:
            file_names.append(file)
    return file_names


def run(dir_path, in_file_type="kml"):
    print(dir_path)

    error_info_to_json = dict()

    error_info_to_json['cases'] = dict()

    case_names = list()  # 即将被分析的所有case名字的列表，case名字如：case_FILE039_Dynamic

    # 获取被复制路径所有文件夹名，填入case_names.
    for obj in os.listdir(local_results_dir):
        obj_path = os.path.join(local_results_dir, obj)
        if os.path.isdir(obj_path):
            case_name = obj
        else:
            continue  # 路径不为文件夹
        if case_name not in case_names:
            case_names.append(case_name)

    if process_local_cases is False:
        while True:
            for case_name in local_existed_cases:
                if case_name in case_names:
                    case_names.remove(case_name)

            break

    for case_name in case_names:
        temp_dir_path = dir_path + "\\" + case_name
        if os.path.exists(temp_dir_path):
            pass
        else:
            print(f'路径不存在：{temp_dir_path}')
            continue

        if if_copy is True:
            truth_file_name = case_name + ".kml"
            truth_file_path = os.path.join(temp_dir_path, truth_file_name)
            try:
                os.remove(truth_file_path)  # 删除用不到的真值kml文件
            except:
                print(f"Failed deleting truth file, continue: {truth_file_path}")
                pass

        # 1.从kml中提取数据至info文件
        info_files = get_files(temp_dir_path, in_file_type)

        for file in info_files:

            infile = os.path.join(temp_dir_path, file)

            # Output_Files
            # 1.必须更新，否则无法生成文件 2.输出到原文件文件夹下 3.此处添加输出的文件
            f_data_from_kml = infile[0:-3] + "info"  # 提取出的文件
            f_exclude_tunnel = infile[0:-3] + "ex_t"  # 剔除隧道后的数据
            out_file_list = [f_data_from_kml, f_exclude_tunnel]  # 在此添加输出文件到out_file_list

            fname = os.path.basename(infile)
            ftype = fname.split('.')

            if ftype[-1] == "kml":
                try:
                    myprint("Reading kml: " + file)
                    find_tunnel(infile, out_file_list)

                except Exception as e:
                    myprint(f"Failed reading kml: {infile}")
                    logger.exception(e)

        # 2.从info文件中剔除特定场景数据：tunnel，回放结束（未完成），大误差（未完成）
        info_files = get_files(temp_dir_path, "info")
        for file in info_files:
            try:
                infile = os.path.join(temp_dir_path, file)
            except Exception as e:
                print("Failed reading file.")
                logger.exception(e)

            # 此处添加输出的文件
            f_data_from_kml = infile[0:-4] + "info"
            f_exclude_tunnel = infile[0:-4] + "ex_t"
            out_file_list = [f_data_from_kml, f_exclude_tunnel]  # 在此添加输出文件到out_file_list

            try:
                max_error = get_max_error(infile)  # 统计原始info的误差

                myprint("Origin max error: " + str(max_error))

                exclude_tunnel(infile, out_file_list)  # 剔除tunnel数据

            except Exception as e:
                logger.exception(e)
                print("Failed reading info.")

        # 3.print剔除指定场景后的max error
        files = get_files(temp_dir_path, "ex_t")

        for file in files:
            try:
                infile = os.path.join(temp_dir_path, file)
            except Exception as e:
                logger.exception(e)
                print("Failed reading file.")

            try:
                myprint("\nexclude_max_error: ")

                duration_info = exclude_max_error(infile)  # 统计大误差信息

                error_info = list()

                if duration_info:
                    for part_n in duration_info:
                        max_error = duration_info[part_n]['max_error']

                        max_error_time = duration_info[part_n]['max_error_time']

                        duration = duration_info[part_n]['duration']

                        start_time = duration_info[part_n]['epochs'][0][0]

                        end_time = duration_info[part_n]['epochs'][-1][0]

                        rms = int(duration_info[part_n]['rms'])

                        # [开始时间，停止时间，时长，最值时间，最大误差]
                        error_info.append(f'{start_time},{end_time},{duration},{max_error_time},{max_error},{rms}')

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

        # 修饰kml文件
        myprint('Start process_kml()...')
        process_kml(temp_dir_path)

    json_file_path = os.path.join(local_results_dir, 'info.json')
    # json_file_path = r'D:\mfw\练习\test_kml\test.json'

    write_file = open(json_file_path, encoding='UTF-8', mode="w")

    data = json.dumps(error_info_to_json, indent=4)

    write_file.write(data)

    write_file.close()


# # 4.重新统计一遍MAX ERROR


def if_pass(dur_info_list, outfiles, filename, case_file_name):
    # 判断文件是否存在，确定打开文件的mode（覆写w或追加a）
    if os.path.exists(local_results_dir + "\\" + "report.txt"):
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
                    logger.info(f"Failed: Max err {str(max_error)}, duration {duration}, start time {start_time}\n")
                    f_out.write(f"Failed: Max err {str(max_error)}, duration {duration}, start time {start_time}\n")

                elif duration <= 20:
                    f_out.write("Pass\n")

            elif max_error > 50:
                logger.info(
                    f_out.write(f"Failed: Max err {str(max_error)}, duration {duration}, start time {start_time}\n"))
                f_out.write(f"Failed: Max err {str(max_error)}, duration {duration}, start time {start_time}\n")
    f_out.write("\n\n")


# def do_compare(mode, durations):
# 	"""输入durations，提取BK DF&SF duration的max err, 在对比机中进行匹配， 再进行之后的对比"""
# 	if mode == "sf":
#
#
# 	elif mode == "df":
#
# 	else:
# 		return "err"


def count_running_time():
    """计算运行时间"""
    running_time = end - start
    print("Running time: " + str(running_time))


def exclude_max_error(infile):
    """
    # 迭代，分割出大误差出现的区间
    :param infile: ex_t文件
    :return: epochs,max_error,max_error_time,duration(count_each_epochs)
    """
    myprint("Now processing " + infile)

    f_in = open(infile, encoding='UTF-8')

    data_lines = f_in.readlines()  # 数据

    max_error = get_max_error(infile)
    if max_error < 5:
        myprint("Done Interation, max error: " + str(max_error) + "\n")
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

                line_list = line.split(',')
                error_data_dic[temp_key]['epochs'].append(line_list)
            # error_data_dic[temp_key]['epochs'].append(line)
    else:
        print("Unexpected error in exclude_max_error, max_error: " + str(max_error) + "\n")
        raise Exception('Unexpected error')

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
    # 添加rms信息
    add_rms(error_data_dic)

    myprint("End processing " + infile)
    return error_data_dic


if __name__ == '__main__':
    start = time.perf_counter()

    # 是否清空结果文件夹
    if True:  # 假设 if_copy 为 True
        confirmation = input(f"Result directory: {LOCAL_RESULTS_DIR}\nClear analyze result directory? (y/n): ")
        if confirmation.lower() in ('y', 'yes'):
            print('Clear all...')
            try:
                shutil.rmtree(LOCAL_RESULTS_DIR)
            except Exception as error:
                logger.error("Failed to clear the directory:", error)
                print("Failed to clear the directory!")
                exit(1)
            while not os.path.exists(LOCAL_RESULTS_DIR):
                os.mkdir(LOCAL_RESULTS_DIR)
        else:
            print('Do not clear.')
    else:
        pass

    # Copy
    if True:  # 假设 if_copy 为 True
        try:
            # 假设 process_local_cases 为 False
            local_existed_cases = get_local_cases(LOCAL_RESULTS_DIR)

            start_copy_share_file()  # 拷贝 kml 文件

            print(DIR_NAMES)  #

            print('waiting for start_copy_share_file() to complete...')

            time.sleep(COPY_T)  # 等待拷贝完成
        except Exception as error:
            logger.exception(error)
            print("Failed copying file!")

    try:
        print("Start processing...")
        abandon_list = 0  # 假设
        in_file_type = "kml"
        dir_path = LOCAL_RESULTS_DIR

        run(dir_path, in_file_type)
        copy_TruthAndExcel(SHARE_DIR, LOCAL_RESULTS_DIR)
        print("End processing.")

    except Exception as error:
        logger.exception(error)

    end = time.perf_counter()
    count_running_time()


