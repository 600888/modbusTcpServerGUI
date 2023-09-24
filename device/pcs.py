import csv
import logging
import random
from config.pcs_config import PcsConfig
from device.point_data import Yc, Yx


class Pcs:
    codeToDataPointMap = {}
    addressDict = {}

    def __init__(self):
        self.yc_list = []
        self.yx_list = []
        for i in (30000, 30016):
            self.addressDict[i] = True
        for i in (40000, 40006):
            self.addressDict[i] = True
        # 读数据
        self.totalAcPower = 0.0  # 总交流有功功率
        self.totalAcReactivePower = 0.0  # 总交流无功功率
        self.totalApparentPower = 0.0  # 总交流视在功率
        self.totalPowerFactor = 0.0  # 总交流功率因数
        self.todayAcChargeEnergy = 0.0  # 当天交流充电量
        self.todayAcDischargeEnergy = 0.0  # 当天交流放电量
        self.pcsTemperature = 0.0  # pcs模块温度
        self.environmentTemperature = 0.0  # pcs环境温度
        self.phaseAVoltage = 0.0  # A相电压
        self.phaseBVoltage = 0.0  # B相电压
        self.phaseCVoltage = 0.0  # C相电压
        self.phaseACurrent = 0.0  # A相电流
        self.phaseBCurrent = 0.0  # B相电流
        self.phaseCCurrent = 0.0  # C相电流
        self.acFrequency = 0.0  # 交流频率

        # 写数据
        self.isStart = 0  # pcs开关机设置
        self.isCharge = 0  # pcs充放电设置
        self.isManual = 0  # 手动并离网模式 0:离网 1:并网
        self.isPlan = 0  # 是否启用计划曲线运行
        self.runMode = 0  # 运行模式，恒定功率模式，恒定电流模式

    def importDataPointCsv(self, file_name):
        # 读取 modbus_point.csv 数据表
        with open(file_name, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, skipinitialspace=True)
            rows = [row for row in reader if any(field.strip() for field in row)]  # 去除没有数据的空行
            count = 0  # 记录读取到第几行
            group_code = ""  # 记录当前组号
            for row in rows:
                count += 1
                if str(row[0]).find("grp_type") != -1:
                    continue
                elif str(row[0]).find("yc") != -1:
                    break

                group_code = str(row[1])

            # 读取modbus_point数据,分别导入yc和yx
            is_yx = False
            modbus_rows = rows[count:]
            for row in modbus_rows:
                count += 1
                # 跳过yc开始标志
                if str(row[0]).find("yc") != -1:
                    continue
                elif str(row[0]).find("rtu_addr") != -1:
                    continue
                elif str(row[0]).find("yx") != -1:
                    is_yx = True
                    continue

            if not is_yx:
                yc_data = Yc(str(row[1]), str(row[2]), str(row[6]), str(row[5]), 0, float(row[8]), float(row[9]),
                             int(row[4]))
                self.yc_list.append(yc_data)
            else:
                yx_data = Yx(str(row[1]), str(row[2]), str(row[6]), str(row[5]), 0, int(row[4]))
                self.yx_list.append(yx_data)

        for yc in self.yc_list:
            self.codeToDataPointMap[yc.code] = yc

        for yx in self.yx_list:
            self.codeToDataPointMap[yx.code] = yx

    def checkImportCsv(self, pcs_point, data_list):
        pass

    # 获取总交流有功功率
    def getTotalAcPower(self):
        return self.totalAcPower

    # 获取总交流无功功率
    def getTotalAcReactivePower(self):
        return self.totalAcReactivePower

    # 获取总交流视在功率
    def getTotalApparentPower(self):
        return self.totalApparentPower

    # 获取总交流功率因数
    def getTotalPowerFactor(self):
        logging.debug("totalAcPower: %d, totalApparentPower: %d" % (self.totalAcPower, self.totalApparentPower))
        return self.totalAcPower * 1000 / self.totalApparentPower

    # 获取当天交流充电量
    def getTodayAcChargeEnergy(self):
        return self.todayAcChargeEnergy

    # 获取当天交流放电量
    def getTodayAcDischargeEnergy(self):
        return self.todayAcDischargeEnergy

    # 获取pcs模块温度
    def getPcsTemperature(self):
        return self.pcsTemperature

    # 获取pcs环境温度
    def getEnvironmentTemperature(self):
        return self.environmentTemperature

    # 获取A相电压
    def getPhaseAVoltage(self):
        return self.phaseAVoltage

    # 获取B相电压
    def getPhaseBVoltage(self):
        return self.phaseBVoltage

    # 获取C相电压
    def getPhaseCVoltage(self):
        return self.phaseCVoltage

    # 获取A相电流
    def getPhaseACurrent(self):
        return self.phaseACurrent

    # 获取B相电流
    def getPhaseBCurrent(self):
        return self.phaseBCurrent

    # 获取C相电流
    def getPhaseCCurrent(self):
        return self.phaseCCurrent

    # 获取交流频率
    def getAcFrequency(self):
        return self.acFrequency

    # 设置模拟随机数据
    def setRandomData(self):
        self.totalAcPower = random.randint(1000, 2000)
        self.totalAcReactivePower = random.randint(1000, 2000)
        self.totalApparentPower = random.randint(1000, 2000)
        self.totalPowerFactor = random.randint(1000, 2000)
        # self.totoalPowerFactor = int(self.totalAcPower * 1000 / self.totalApparentPower)
        # print("totoalPowerFactor: %d" % self.totoalPowerFactor)
        self.todayAcChargeEnergy = random.randint(1000, 2000)
        self.todayAcDischargeEnergy = random.randint(1000, 2000)
        self.pcsTemperature = random.randint(200, 300)
        self.environmentTemperature = random.randint(200, 300)
        self.phaseAVoltage = random.randint(100, 200)
        self.phaseBVoltage = random.randint(100, 200)
        self.phaseCVoltage = random.randint(100, 200)
        self.phaseACurrent = random.randint(100, 200)
        self.phaseBCurrent = random.randint(100, 200)
        self.phaseCCurrent = random.randint(100, 200)
        self.acFrequency = random.randint(1000, 2000)

        # 写数据
        self.isStart = random.randint(0, 1)
        self.isCharge = random.randint(0, 1)
        self.isManual = random.randint(0, 1)
        self.isPlan = random.randint(0, 1)
        self.runMode = random.randint(0, 1)

        for yc in self.yc_list:
            if yc.address not in self.addressDict:
                yc.val = random.randint(1000, 2000)

        for yx in self.yx_list:
            if yx.address not in self.addressDict:
                yx.val = random.randint(0, 1)

    def setPcsConfig(self, pcs_config):
        self.isStart = 1 if pcs_config.server_status else 0
        self.runMode = 1 if pcs_config.run_mode == "恒流" else 0
        self.phaseAVoltage = pcs_config.voltage
        self.phaseACurrent = pcs_config.current
        self.phaseBVoltage = pcs_config.voltage
        self.phaseBCurrent = pcs_config.current
        self.phaseCVoltage = pcs_config.voltage
        self.phaseCCurrent = pcs_config.current
        self.totalAcPower = pcs_config.power
        self.totalAcReactivePower = pcs_config.power
        self.totalApparentPower = pcs_config.power
