import random


class Pcs:
    def __init__(self):
        self.totalAcPower = 0  # 总交流有功功率
        self.totalAcReactivePower = 0  # 总交流无功功率
        self.totalApparentPower = 0  # 总交流视在功率
        self.totalPowerFactor = 0  # 总交流功率因数
        self.todayAcChargeEnergy = 0  # 当天交流充电量
        self.todayAcDischargeEnergy = 0  # 当天交流放电量
        self.pcsTemperature = 0  # pcs模块温度
        self.environmentTemperature = 0  # pcs环境温度
        self.phaseAVoltage = 0  # A相电压
        self.phaseBVoltage = 0  # B相电压
        self.phaseCVoltage = 0  # C相电压
        self.phaseACurrent = 0  # A相电流
        self.phaseBCurrent = 0  # B相电流
        self.phaseCCurrent = 0  # C相电流
        self.acFrequency = 0  # 交流频率

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
        return self.totalAcPower / self.totalApparentPower

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
        self.totoalPowerFactor = self.getTotalPowerFactor()
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
