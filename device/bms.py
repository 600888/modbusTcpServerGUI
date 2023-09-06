from dataclasses import dataclass


class DataPoint:
    def __init__(self):
        self.value = 0
        self.pack_id = 0
        self.cell_id = 0

    def set_value(self, value, pack_id, cell_id):
        self.value = value
        self.pack_id = pack_id
        self.cell_id = cell_id


@dataclass
class Cluster:
    cluster_id = 0
    PackList = []

    # 簇的值
    voltage = 0
    current = 0
    temperature = 0
    soc = 0

    # 簇的寄存器地址
    vol_address = 0
    current_address = 0
    temperature_address = 0
    soc_address = 0

    def __init__(self):
        self.max_voltage_point = DataPoint()
        self.min_voltage_point = DataPoint()
        self.max_temperature_point = DataPoint()
        self.min_temperature_point = DataPoint()

    # 获取簇总电压
    def getVoltage(self):
        return sum([pack.voltage for pack in self.PackList])
        # return int(self.PackList[0].voltage)

    # 获取簇平均电压
    def getAverageVoltage(self):
        voltage = 0
        for pack in self.PackList:
            for cell in pack.CellList:
                voltage += cell.voltage
        count = len(self.PackList) * len(self.PackList[0].CellList)
        voltage = voltage / count
        return int(voltage)

    # 获取簇总电流
    def getCurrent(self):
        current = 0
        for pack in self.PackList:
            current += pack.current
        return int(current)

    def getTemperature(self):
        # 假设簇的温度为所有模组的温度的平均值
        temperature = 0
        for pack in self.PackList:
            temperature += pack.temperature
        temperature = temperature / len(self.PackList)
        return int(temperature)

    def getSoc(self):
        # 假设簇的soc为所有模组的soc的平均值
        soc = 0
        for pack in self.PackList:
            soc += pack.soc
        soc = soc / len(self.PackList)
        return int(soc)

    # 获取簇的单体最大电压
    def getMaxVoltage(self):
        # 找到所有模组中的最大电压
        max_voltage = -100000000
        for pack in self.PackList:
            if pack.getMaxVoltage() > max_voltage:
                max_voltage = pack.getMaxVoltage()
        return int(max_voltage)
        # return int(max(self.PackList, key=lambda x: x.getMaxVoltage()).getMaxVoltage())

    # 获取簇的单体最小电压
    def getMinVoltage(self):
        return int(min(self.PackList, key=lambda x: x.getMinVoltage()).getMinVoltage())

    # 获取簇的单体最大电流
    def getMaxCurrent(self):
        # 每个模组的最大电流的最大值
        return int(max(self.PackList, key=lambda x: x.getMaxCurrent()).getMaxCurrent())

    # 获取簇的单体最小电流
    def getMinCurrent(self):
        # 每个模组的最小电流的最小值
        return int(min(self.PackList, key=lambda x: x.getMinCurrent()).getMinCurrent())

    # 获取簇的单体最大温度
    def getMaxTemperature(self):
        # 每个模组的最大温度的最大值
        return int(max(self.PackList, key=lambda x: x.getMaxTemperature()).getMaxTemperature())

    # 获取簇的单体最小温度
    def getMinTemperature(self):
        # 每个模组的最小温度的最小值
        return int(min(self.PackList, key=lambda x: x.getMinTemperature()).getMinTemperature())

    # 获取簇的单体最大soc
    def getMaxSoc(self):
        # 每个模组的最大soc的最大值
        return int(max(self.PackList, key=lambda x: x.getMaxSoc()).getMaxSoc())

    # 获取簇的单体最小soc
    def getMinSoc(self):
        # 每个模组的最小soc的最小值
        return int(min(self.PackList, key=lambda x: x.getMinSoc()).getMinSoc())

    # 获取最大电压测点
    def getDataPoint(self):
        max_voltage = -100000000
        max_voltage_pack_id = 0
        max_voltage_cell_id = 0

        min_voltage = 100000000
        min_voltage_pack_id = 0
        min_voltage_cell_id = 0

        max_temperature = -100000000
        max_temperature_pack_id = 0
        max_temperature_cell_id = 0

        min_temperature = 100000000
        min_temperature_pack_id = 0
        min_temperature_cell_id = 0

        for pack in self.PackList:
            for cell in pack.CellList:
                if cell.voltage > max_voltage:
                    max_voltage = cell.voltage
                    max_voltage_pack_id = pack.pack_id
                    max_voltage_cell_id = cell.cell_id
                if cell.voltage < min_voltage:
                    min_voltage = cell.voltage
                    min_voltage_pack_id = pack.pack_id
                    min_voltage_cell_id = cell.cell_id
                if cell.temperature > max_temperature:
                    max_temperature = cell.temperature
                    max_temperature_pack_id = pack.pack_id
                    max_temperature_cell_id = cell.cell_id
                if cell.temperature < min_temperature:
                    min_temperature = cell.temperature
                    min_temperature_pack_id = pack.pack_id
                    min_temperature_cell_id = cell.cell_id

        self.max_voltage_point.set_value(max_voltage, max_voltage_pack_id, max_voltage_cell_id)
        self.min_voltage_point.set_value(min_voltage, min_voltage_pack_id, min_voltage_cell_id)
        self.max_temperature_point.set_value(max_temperature, max_temperature_pack_id, max_temperature_cell_id)
        self.min_temperature_point.set_value(min_temperature, min_temperature_pack_id, min_temperature_cell_id)
        return [self.max_voltage_point, self.min_voltage_point, self.max_temperature_point, self.min_temperature_point]

    def setValue(self):
        self.voltage = self.getVoltage()
        self.current = self.getCurrent()
        self.temperature = self.getTemperature()
        self.soc = self.getSoc()

    def setClusterId(self, cluster_id):
        self.cluster_id = cluster_id

    def setValAddress(self):
        self.vol_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 1000 + 1
        self.current_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 1000 + 2
        self.temperature_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 1000 + 3
        self.soc_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 1000 + 4
        # self.vol_address = 30000 + 750 + self.cluster_id + 1
        # self.current_address = 31000 + 750 + self.cluster_id + 1
        # self.temperature_address = 32000 + 750 + self.cluster_id + 1
        # self.soc_address = 33000 + 750 + self.cluster_id + 1


@dataclass
class Pack:
    CellList = []

    # 模组id
    cluster_id = 0
    pack_id = 0

    # 模组的值
    voltage = 0
    current = 0
    temperature = 0
    soc = 0

    # 模组值的寄存器地址
    vol_address = 0
    current_address = 0
    temperature_address = 0
    soc_address = 0

    # 串并联数量，几串几并
    series = 24
    parallel = 1

    def setSeriesParallel(self, series, parallel):
        self.series = series
        self.parallel = parallel

    def getVoltage(self):
        voltage = 0
        # 根据串并联数量计算模组的电压
        if self.parallel == 0:
            for cell in self.CellList:
                voltage += cell.voltage
        else:
            count = int(len(self.CellList) / self.parallel)
            for i in range(0, count):
                voltage += self.CellList[i].voltage
        return int(voltage)

    def getCurrent(self):
        current = 0
        # 根据串并联数量计算模组的电流
        if self.series == 0:
            return self.CellList[0].current
        else:
            count = int(len(self.CellList) / self.series)
            for i in range(0, count):
                current += self.CellList[i].current
        return int(current)

    def getTemperature(self):
        # 假设模组的温度为所有电芯的温度的平均值
        temperature = 0
        for cell in self.CellList:
            temperature += cell.temperature
        temperature = temperature / len(self.CellList)
        return int(temperature)

    def getSoc(self):
        # 假设模组的soc为所有电芯的soc的平均值
        soc = 0
        for cell in self.CellList:
            soc += cell.soc
        soc = soc / len(self.CellList)
        return int(soc)

    def getMaxVoltage(self):
        # 找到所有电芯中的最大电压
        max_voltage = -100000000
        for cell in self.CellList:
            if cell.voltage > max_voltage:
                max_voltage = cell.voltage
        return int(max_voltage)
        # return int(max(self.CellList, key=lambda x: x.voltage).voltage)

    def getMinVoltage(self):
        return int(min(self.CellList, key=lambda x: x.voltage).voltage)

    def getMaxCurrent(self):
        return int(max(self.CellList, key=lambda x: x.current).current)

    def getMinCurrent(self):
        return int(min(self.CellList, key=lambda x: x.current).current)

    def getMaxTemperature(self):
        return int(max(self.CellList, key=lambda x: x.temperature).temperature)

    def getMinTemperature(self):
        return int(min(self.CellList, key=lambda x: x.temperature).temperature)

    def getMaxSoc(self):
        return int(max(self.CellList, key=lambda x: x.soc).soc)

    def getMinSoc(self):
        return int(min(self.CellList, key=lambda x: x.soc).soc)

    def setValue(self):
        self.voltage = self.getVoltage()
        self.current = self.getCurrent()
        self.temperature = self.getTemperature()
        self.soc = self.getSoc()

    def setPackId(self, cluster_id, pack_id):
        self.cluster_id = cluster_id
        self.pack_id = pack_id

    def setValAddress(self):
        self.vol_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 960 + self.pack_id + 1
        self.current_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 970 + self.pack_id + 1
        self.temperature_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 980 + self.pack_id + 1
        self.soc_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 990 + self.pack_id + 1
        # self.vol_address = 30000 + 720 + self.cluster_id * 10 + self.pack_id + 1
        # self.current_address = 31000 + 720 + self.cluster_id * 10 + self.pack_id + 1
        # self.temperature_address = 32000 + 720 + self.cluster_id * 10 + self.pack_id + 1
        # self.soc_address = 33000 + 720 + self.cluster_id * 10 + self.pack_id + 1


@dataclass
class Cell:
    # 电芯的id
    cluster_id = 0
    pack_id = 0
    cell_id = 0

    # 电芯的值
    voltage = 0
    current = 0
    temperature = 0
    soc = 0

    # 电芯值的寄存器地址
    vol_address = 0
    current_address = 0
    temperature_address = 0
    soc_address = 0

    def setValue(self, voltage, current, temperature, soc):
        self.voltage = voltage
        self.current = current
        self.temperature = temperature
        self.soc = soc

    def setCellId(self, cluster_id, pack_id, cell_id):
        self.cluster_id = cluster_id
        self.pack_id = pack_id
        self.cell_id = cell_id

    def setValAddress(self):
        self.vol_address = 30000 + (2 * self.cluster_id + 2) * 1000 + self.pack_id * 24 + self.cell_id + 1
        self.current_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 240 + self.pack_id * 24 + self.cell_id + 1
        self.temperature_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 480 + self.pack_id * 24 + self.cell_id + 1
        self.soc_address = 30000 + (2 * self.cluster_id + 2) * 1000 + 720 + self.pack_id * 24 + self.cell_id + 1
        # self.vol_address = 30000 + self.cluster_id * 240 + self.pack_id * 24 + self.cell_id + 1
        # self.current_address = 31000 + self.cluster_id * 240 + self.pack_id * 24 + self.cell_id + 1
        # self.temperature_address = 32000 + self.cluster_id * 240 + self.pack_id * 24 + self.cell_id + 1
        # self.soc_address = 33000 + self.cluster_id * 240 + self.pack_id * 24 + self.cell_id + 1
