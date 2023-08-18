import random
from binascii import unhexlify

from pymodbus.utilities import computeCRC


# 生成写的模拟命令
def write_simulation(test_cnt):
    print("write_simulation")
    str_list = []
    for i in range(test_cnt):
        str = ""
        str += "0106"  # 设备地址和功能码
        str += '{:04X}'.format(40001 + i)  # 寄存器地址
        data = random.randint(0, 4000)
        str += '{:04X}'.format(data)  # 数据
        crc_code = '{:04X}'.format(computeCRC(unhexlify(str)))
        str_list.append(str + crc_code)
        print(str + crc_code)


# 生成读的模拟命令
def read_simulation(test_cnt):
    print("read_simulation")
    str_list = []
    for i in range(test_cnt):
        str = ""
        str += "0103"  # 设备地址和功能码
        str += '{:04X}'.format(40001)  # 寄存器地址
        reg_cnt = random.randint(0, 10)
        str += '{:04X}'.format(reg_cnt)  # 数据
        crc_code = '{:04X}'.format(computeCRC(unhexlify(str)))
        str_list.append(str + crc_code)
        print(str + crc_code)


# 指定读取某个输入寄存器的值
def read_simulation_by_address(address):
    print("read_simulation_by_address")
    str = ""
    str += "0103"  # 设备地址和功能码
    str += '{:04X}'.format(address)  # 寄存器地址
    reg_cnt = 1
    str += '{:04X}'.format(reg_cnt)  # 数据
    crc_code = '{:04X}'.format(computeCRC(unhexlify(str)))
    print(str + crc_code)


if __name__ == '__main__':
    read_simulation_by_address(31001)
    # write_simulation(10)
    # read_simulation(10)
