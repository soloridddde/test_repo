
# encoding=utf-8
# import subprocess
#
# cmd = r'C:\mengfo.wang\test\NavStarTool_240308\Transformer.exe'
#
# args = [r"C:\mengfo.wang\test\version\4166024125\Internal\Hash_file\FW_GNSS_PRINT_HASHCODE.txt",
#         r'C:\mengfo.wang\test\data\20240325_weekly-24A\data_ttff_replay\tmp',
#         'bin']
#
# results = subprocess.run([cmd] + args, capture_output=True, text=True)
#
# output =results.stdout
#
# print(output)
#
# print(results.returncode)


from pyrtcm import RTCMReader
# def decode_rtcm3(infile):
#     stream = open(infile, 'rb')
#     rtr = RTCMReader(stream)
#     for (raw_data, parsed_data) in rtr:
#         if 'GNSSEpoch=190667000,' in parsed_data:
#             print(raw_data)


def tmp(infile):
    stream = open(infile, 'r')
    get_lines = stream.readlines()
    stream.close()

    stream = open(infile, 'rb')
    get_bytes = stream.readlines()
    stream.close()

    for line in get_lines:
        if line:
            if line.startswith('<'):
                if 'GNSSEpoch=190667000,' in line:
                    print(line)
                    id = get_lines.index(line)
                    print(f"{get_bytes[id+1][2:].decode('utf-8')}")
        else:
            continue


def run():
    # infile = r"C:\mengfo.wang\tool\POTTFF-hotNcold\RTCM差异\new\RTCMfromRTK_20240326_020250.txt"
    # decode_rtcm3(infile)
    infile = r"C:\mengfo.wang\tool\POTTFF-hotNcold\RTCM差异\new\RTCMfromRTK_20240326_020250.txt.decode"
    tmp(infile)


if __name__ == '__main__':
        run()
        print("--------------[End]--------------")