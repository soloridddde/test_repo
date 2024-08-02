import serial


cold_cmd = "42 4b 49 c4 02 0c 00 04 00 00 ff ff"
factory_cmd = "42 4b 4a 3b 02 0c 00 04 00 00 00 ff"

b_cold_cmd = bytes.fromhex(cold_cmd)
print(b_cold_cmd)

b_factory_cmd = bytes.fromhex(factory_cmd)
print(b_factory_cmd)

ser = serial.Serial('com73', 2000000)

if ser.isOpen():
    print("Serial port is open")

while True:
    # data = ser.readline()
    # cmd_pos1 = data.find(b_factory_cmd)
    # cmd_pos2 = data.find(b_cold_cmd)

    data = ser.read()
    print(data)

    # if cmd_pos1:
    #     data = data[8:]
    #     print(data)okkkkkk
    #     print("Factory command found")
    #     continue
    #
    # print(data)


    # this is a test message