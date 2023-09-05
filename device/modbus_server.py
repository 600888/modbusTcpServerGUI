import random

from pyModbusTCP.server import ModbusServer, ModbusServerDataBank, log
from device.bms import Cluster, Pack, Cell
from device.pcs import Pcs
import time


class ModbusServerGUI:
    running = False
    address = "127.0.0.1"
    port = 10502
    serverObj = False  # server object from pyModbusTCP library
    dataBank = False
    type = None

    def __init__(self):
        # databank object is used by pyModbusTCP to store the response values
        self.dataBank = ModbusServerDataBank()

    def startServer(self):
        if self.checkRunning():
            return True

        self.serverObj = ModbusServer(host=self.address, port=self.port, no_block=True, data_bank=self.dataBank)
        self.serverObj.start()

        # Wait 1 seconds for everything to settle and then check our status
        time.sleep(1)
        return self.checkRunning()

    def stopServer(self):
        self.serverObj.stop()
        time.sleep(1)  # wait 1 seconds for it to settle
        if not self.checkRunning():
            self.serverObj = False
            return True
        else:
            return False

    def setCoilBits(self, coilList):
        # self.debugLog("array: " + str(coilList))

        if not self.checkRunning():
            self.debugLog("set coils called without live server")
            return False

        # self.data_hdl.dataBank.set_coils(0, coilList)
        self.serverObj.data_hdl.write_coils(0, coilList, "None")

    def setRegisterValues(self, registerList, type="input"):
        if not self.checkRunning():
            self.debugLog("set registers called without live server")
            return False

        if type == "output":
            self.serverObj.data_hdl.data_bank.set_holding_registers(40000, registerList)
        else:
            self.serverObj.data_hdl.data_bank.set_input_registers(30000, registerList)

    def readRegisterValues(self, type="input"):
        if not self.checkRunning():
            self.debugLog("read registers called without live server")
            return False

        if type == "output":
            return self.serverObj.data_hdl.data_bank.get_holding_registers(40000, 9999)
        else:
            return self.serverObj.data_hdl.data_bank.get_input_registers(30000, 9999)

    def clearRegisterValues(self, type="input"):
        if type == "output":
            self.serverObj.data_hdl.data_bank.set_holding_registers(40000, [0] * 9999)
        else:
            self.serverObj.data_hdl.data_bank.set_input_registers(30000, [0] * 9999)

    def clearCoilBits(self):
        self.serverObj.data_hdl.write_coils(0, [0] * 9999, "None")

    def setAddress(self, data):
        self.address = data

    def setPort(self, data):
        try:
            self.port = int(data)
        except ValueError as e:
            self.warningLog("Invalid port number!")
            raise ValueError("Invalid port number!")

    def checkRunning(self):
        if not self.serverObj:
            self.warningLog("Server not running")
            return False

        if self.serverObj.is_run:
            self.running = True
            self.debugLog("Server Running")
            return True
        else:
            self.running = False
            self.warningLog("Server not running")
            return False

    # 根据地址设置值
    def setValueByAddress(self, address, value, type="output"):
        # 如果值为空，则设置一个默认值
        if not address:
            address = "30000"
        if not value:
            value = "0"
        val = [str(value)]
        if type == "output":
            self.serverObj.data_hdl.write_h_regs(int(str(address), 10), val, None)
        else:
            self.serverObj.data_hdl.write_i_regs(int(str(address), 10), val)

    def setType(self, type):
        self.type = type

    def getType(self):
        return self.type

    @staticmethod
    def debugLog(data=None):
        log.info(data)

    @staticmethod
    def errorLog(data=None):
        log.error(data)

    @staticmethod
    def warningLog(data=None):
        log.warning(data)


class ModbusPcsServerGUI(ModbusServerGUI):
    config_list = []
    pcs = Pcs()

    # 设置PCS配置数据
    def setPcsConfig(self, pcs_config):
        self.pcs.setPcsConfig(pcs_config)
        self.setAllRegisterValues()
        if self.pcs.isStart == 0:
            self.stopServer()

    # 设置PCS模拟数据
    def setSimulatePcsValues(self):
        self.pcs.setRandomData()
        self.setAllRegisterValues()

    def setAllRegisterValues(self):
        # 读数据
        self.setValueByAddress(30001, self.pcs.totalAcPower, "input")
        self.setValueByAddress(30002, self.pcs.totalAcReactivePower, "input")
        self.setValueByAddress(30003, self.pcs.totalApparentPower, "input")
        log.debug("totalPowerFactor: %d" % self.pcs.totalPowerFactor)
        self.setValueByAddress(30004, self.pcs.totalPowerFactor, "input")
        self.setValueByAddress(30005, self.pcs.todayAcChargeEnergy, "input")
        self.setValueByAddress(30006, self.pcs.todayAcDischargeEnergy, "input")
        self.setValueByAddress(30007, self.pcs.pcsTemperature, "input")
        self.setValueByAddress(30008, self.pcs.environmentTemperature, "input")
        self.setValueByAddress(30009, self.pcs.phaseAVoltage, "input")
        self.setValueByAddress(30010, self.pcs.phaseBVoltage, "input")
        self.setValueByAddress(30011, self.pcs.phaseCVoltage, "input")
        self.setValueByAddress(30012, self.pcs.phaseACurrent, "input")
        self.setValueByAddress(30013, self.pcs.phaseBCurrent, "input")
        self.setValueByAddress(30014, self.pcs.phaseCCurrent, "input")
        self.setValueByAddress(30015, self.pcs.acFrequency, "input")

        # 写数据
        self.setValueByAddress(40001, self.pcs.isStart, "output")
        self.setValueByAddress(40002, self.pcs.isCharge, "output")
        self.setValueByAddress(40003, self.pcs.isManual, "output")
        self.setValueByAddress(40004, self.pcs.isPlan, "output")
        self.setValueByAddress(40005, self.pcs.runMode, "output")

    def getDataPoint(self, address, hex_address, name, value, unit):
        point = [address, hex_address, name, value, unit]
        return point

    def exportDataPoint(self, dataList):
        # 读数据
        dataList.append(self.getDataPoint(30001, hex(30001), "总交流有功功率", self.pcs.totalAcPower, "0.1"))
        dataList.append(self.getDataPoint(30002, hex(30002), "总交流无功功率", self.pcs.totalAcReactivePower, "0.1"))
        dataList.append(self.getDataPoint(30003, hex(30003), "总交流视在功率", self.pcs.totalApparentPower, "0.1"))
        dataList.append(self.getDataPoint(30004, hex(30004), "总交流功率因数", self.pcs.totalPowerFactor, "0.01"))
        dataList.append(self.getDataPoint(30005, hex(30005), "当天交流充电量", self.pcs.todayAcChargeEnergy, "0.1"))
        dataList.append(self.getDataPoint(30006, hex(30006), "当天交流放电量", self.pcs.todayAcDischargeEnergy, "0.1"))
        dataList.append(self.getDataPoint(30007, hex(30007), "PCS模块温度", self.pcs.pcsTemperature, "0.1"))
        dataList.append(self.getDataPoint(30008, hex(30008), "PCS环境温度", self.pcs.environmentTemperature, "0.1"))
        dataList.append(self.getDataPoint(30009, hex(30009), "A相电压", self.pcs.phaseAVoltage, "0.1"))
        dataList.append(self.getDataPoint(30010, hex(30010), "B相电压", self.pcs.phaseBVoltage, "0.1"))
        dataList.append(self.getDataPoint(30011, hex(30011), "C相电压", self.pcs.phaseCVoltage, "0.1"))
        dataList.append(self.getDataPoint(30012, hex(30012), "A相电流", self.pcs.phaseACurrent, "0.1"))
        dataList.append(self.getDataPoint(30013, hex(30013), "B相电流", self.pcs.phaseBCurrent, "0.1"))
        dataList.append(self.getDataPoint(30014, hex(30014), "C相电流", self.pcs.phaseCCurrent, "0.1"))
        dataList.append(self.getDataPoint(30015, hex(30015), "交流频率", self.pcs.acFrequency, "0.1"))

        # 写数据
        dataList.append(self.getDataPoint(40001, hex(40001), "PCS开关机设置", self.pcs.isStart, "1"))
        dataList.append(self.getDataPoint(40002, hex(40002), "PCS充放电设置", self.pcs.isCharge, "1"))
        dataList.append(self.getDataPoint(40003, hex(40003), "手动并离网模式", self.pcs.isManual, "1"))
        dataList.append(self.getDataPoint(40004, hex(40004), "是否启用计划曲线运行", self.pcs.isPlan, "1"))
        dataList.append(self.getDataPoint(40005, hex(40005), "运行模式", self.pcs.runMode, "1"))


class ModbusBmsServerGUI(ModbusServerGUI):
    clusterList = []

    def __init__(self):
        super().__init__()
        # 一个BMS中有3簇，每簇10个模组，每个pack有24个电芯
        self.cluster_list_count = 3
        self.pack_list_count = 10
        self.cell_count = 24

    def set_cluster_data(self):
        # 初始化三维列表
        for i in range(self.cluster_list_count):
            pack_list = []
            for j in range(self.pack_list_count):
                cell_list = []
                for k in range(self.cell_count):
                    cell = Cell()
                    cell.setCellId(i, j, k)
                    cell.setValAddress()
                    cell_list.append(cell)
                pack = Pack()
                pack.setPackId(i, j)
                pack.setValAddress()
                pack.CellList = cell_list
                pack_list.append(pack)
            cluster = Cluster()
            cluster.PackList = pack_list
            cluster.setClusterId(i)
            cluster.setValAddress()
            self.clusterList.append(cluster)
        # print(len(self.clusterList), len(self.clusterList[0].PackList), len(self.clusterList[0].PackList[0].CellList))

    # 设置单个电芯的值
    def setSingleCellValues(self, cell):
        self.setValueByAddress(cell.vol_address, cell.voltage, "input")
        self.setValueByAddress(cell.current_address, cell.current, "input")
        self.setValueByAddress(cell.temperature_address, cell.temperature, "input")
        self.setValueByAddress(cell.soc_address, cell.soc, "input")

    # 设置单个模组的值
    def setSinglePackValues(self, pack):
        self.setValueByAddress(pack.vol_address, pack.voltage, "input")
        self.setValueByAddress(pack.current_address, pack.current, "input")
        self.setValueByAddress(pack.temperature_address, pack.temperature, "input")
        self.setValueByAddress(pack.soc_address, pack.soc, "input")

    # 设置单个簇的值
    def setSingleClusterValues(self, cluster):
        self.setValueByAddress(cluster.vol_address, cluster.voltage, "input")
        self.setValueByAddress(cluster.current_address, cluster.current, "input")
        self.setValueByAddress(cluster.temperature_address, cluster.temperature, "input")
        self.setValueByAddress(cluster.soc_address, cluster.soc, "input")

    # 获取单个电芯的值
    def getSingleCellValues(self, cluster_id, pack_id, cell_id):
        return self.clusterList[cluster_id].PackList[pack_id].CellList[cell_id]

    def setRandomCellValues(self):
        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    vol = random.randint(3000, 6000)  # 系数乘以0.01
                    current = random.randint(1000, 2000)  # 系数乘以0.01
                    temp = random.randint(2000, 3000)  # 系数乘以0.01
                    soc = random.randint(8000, 9900)  # 系数乘以0.01
                    cell.setValue(vol, current, temp, soc)
                    self.setSingleCellValues(cell)
                pack.setValue()
                self.setSinglePackValues(pack)
            cluster.setValue()
            self.setSingleClusterValues(cluster)
        # 设置簇内系统值
        self.setClusterSystemValues()

    # 设置簇内系统值
    def setClusterSystemValues(self):
        self.setValueByAddress(31001, self.getTotalSystemVoltage(), "input")
        self.setValueByAddress(31002, self.getTotalSystemCurrent(), "input")
        self.setValueByAddress(31003, self.getSystemSoc(), "input")
        self.setValueByAddress(31009, self.getVoltageDifference(), "input")
        self.setValueByAddress(31010, self.getCurrentDifference(), "input")
        self.setValueByAddress(31011, self.getAverageTemperature(), "input")
        self.setValueByAddress(31012, self.getAverageVoltage(), "input")

        self.setValueByAddress(31013, self.getMaxVoltage(), "input")
        self.setValueByAddress(31014, self.getMaxVoltageClusterId(), "input")
        self.setValueByAddress(31015, self.getMaxVoltagePackId(), "input")
        self.setValueByAddress(31016, self.getMaxVoltageCellId(), "input")

        self.setValueByAddress(31017, self.getMinVoltage(), "input")
        self.setValueByAddress(31018, self.getMinVoltageClusterId(), "input")
        self.setValueByAddress(31019, self.getMinVoltagePackId(), "input")
        self.setValueByAddress(31020, self.getMinVoltageCellId(), "input")

        self.setValueByAddress(31021, self.getMaxTemperature(), "input")
        self.setValueByAddress(31022, self.getMaxTemperatureClusterId(), "input")
        self.setValueByAddress(31023, self.getMaxTemperaturePackId(), "input")
        self.setValueByAddress(31024, self.getMaxTemperatureCellId(), "input")

        self.setValueByAddress(31025, self.getMinTemperature(), "input")
        self.setValueByAddress(31026, self.getMinTemperatureClusterId(), "input")
        self.setValueByAddress(31027, self.getMinTemperaturePackId(), "input")
        self.setValueByAddress(31028, self.getMinTemperatureCellId(), "input")

    # 获取系统总电压
    def getTotalSystemVoltage(self):
        return int(self.clusterList[0].voltage)

    # 获取系统总电流
    def getTotalSystemCurrent(self):
        return int(sum([cluster.current for cluster in self.clusterList]))

    # 获取系统SOC,等于电池簇并联后的平均SOC
    def getSystemSoc(self):
        return int(sum([cluster.soc for cluster in self.clusterList]) / len(self.clusterList))

    # 获取系统平均温度
    def getAverageTemperature(self):
        return int(sum([cluster.temperature for cluster in self.clusterList]) / len(self.clusterList))

    # 获取系统平均电压
    def getAverageVoltage(self):
        return int(
            sum([cluster.voltage for cluster in self.clusterList]) / (self.cluster_list_count * self.pack_list_count
                                                                      * self.cell_count))

    # 获取系统单体最高温度
    def getMaxTemperature(self):
        return int(self.getMaxTemperatureIdPoint()[3])

    # 获取系统单体最低温度
    def getMinTemperature(self):
        return int(self.getMinTemperatureIdPoint()[3])

    # 获取系统单体最高电压
    def getMaxVoltage(self):
        return int(self.getMaxVoltageIdPoint()[3])

    # 获取系统单体最低电压
    def getMinVoltage(self):
        return int(self.getMinVoltageIdPoint()[3])

    # 获取系统簇间电压差异
    def getVoltageDifference(self):
        return int(self.getMaxVoltage() - self.getMinVoltage())

    # 获取系统单体最高电流
    def getMaxCurrent(self):
        return int(max([cluster.getMaxCurrent() for cluster in self.clusterList]))

    # 获取系统单体最低电流
    def getMinCurrent(self):
        return int(min([cluster.getMinCurrent() for cluster in self.clusterList]))

    # 获取系统簇间电流差异
    def getCurrentDifference(self):
        return int(self.getMaxCurrent() - self.getMinCurrent())

    # 获取单体最高电压簇号
    def getMaxVoltageClusterId(self):
        return int(self.getMaxVoltageIdPoint()[0])

    def getMaxVoltageIdPoint(self):
        cluster_id = 0
        pack_id = 0
        cell_id = 0
        max_voltage = -100000000
        # print(len(self.clusterList), len(self.clusterList[0].PackList), len(self.clusterList[0].PackList[0].CellList))
        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    # print(cell.voltage, max_voltage)
                    if cell.voltage > max_voltage:
                        max_voltage = cell.voltage
                        cluster_id = cluster.cluster_id
                        pack_id = pack.pack_id
                        cell_id = cell.cell_id
        return [cluster_id, pack_id, cell_id, max_voltage]

    # 获取单体最高电压模组号
    def getMaxVoltagePackId(self):
        return int(self.getMaxVoltageIdPoint()[1])

    # 获取单体最高电压电芯号
    def getMaxVoltageCellId(self):
        return int(self.getMaxVoltageIdPoint()[2])

    def getMinVoltageIdPoint(self):
        cluster_id = 0
        pack_id = 0
        cell_id = 0
        min_voltage = 100000000
        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    # print(cell.voltage, min_voltage)
                    if cell.voltage < min_voltage:
                        min_voltage = cell.voltage
                        cluster_id = cluster.cluster_id
                        pack_id = pack.pack_id
                        cell_id = cell.cell_id
        return [cluster_id, pack_id, cell_id, min_voltage]

    # 获取单体最低电压簇号
    def getMinVoltageClusterId(self):
        return int(self.getMinVoltageIdPoint()[0])

    # 获取单体最低电压模组号
    def getMinVoltagePackId(self):
        return int(self.getMinVoltageIdPoint()[1])

    # 获取单体最低电压电芯号
    def getMinVoltageCellId(self):
        return int(self.getMinVoltageIdPoint()[2])

    def getMaxTemperatureIdPoint(self):
        cluster_id = 0
        pack_id = 0
        cell_id = 0
        max_temperature = -100000000
        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    if cell.temperature > max_temperature:
                        max_temperature = cell.temperature
                        cluster_id = cluster.cluster_id
                        pack_id = pack.pack_id
                        cell_id = cell.cell_id
        return [cluster_id, pack_id, cell_id, max_temperature]

    # 获取单体最高温度簇号
    def getMaxTemperatureClusterId(self):
        return int(self.getMaxTemperatureIdPoint()[0])

    # 获取单体最高温度模组号
    def getMaxTemperaturePackId(self):
        return int(self.getMaxTemperatureIdPoint()[1])

    # 获取单体最高温度电芯号
    def getMaxTemperatureCellId(self):
        return int(self.getMaxTemperatureIdPoint()[2])

    def getMinTemperatureIdPoint(self):
        cluster_id = 0
        pack_id = 0
        cell_id = 0
        min_temperature = 100000000
        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    if cell.temperature < min_temperature:
                        min_temperature = cell.temperature
                        cluster_id = cluster.cluster_id
                        pack_id = pack.pack_id
                        cell_id = cell.cell_id
        return [cluster_id, pack_id, cell_id, min_temperature]

    # 获取单体最低温度簇号
    def getMinTemperatureClusterId(self):
        return int(self.getMinTemperatureIdPoint()[0])

    # 获取单体最低温度模组号
    def getMinTemperaturePackId(self):
        return int(self.getMinTemperatureIdPoint()[1])

    # 获取单体最低温度电芯号
    def getMinTemperatureCellId(self):
        return int(self.getMinTemperatureIdPoint()[2])

    @staticmethod
    def getSystemDataPoint(address, hex_address, name, value, unit):
        point = [address, hex_address, name, value, unit]
        return point

    @staticmethod
    def getCellDataPoint(cluster_id, pack_id, cell_id, value_type, address, hex_address, value, unit):
        pointList = [cluster_id, pack_id, cell_id, value_type, address, hex_address, value, unit]
        return pointList

    def exportSystemDataPoint(self, dataList):
        dataList.append(self.getSystemDataPoint(31001, hex(31001), "系统总电压", self.getTotalSystemVoltage(), "0.01"))
        dataList.append(self.getSystemDataPoint(31002, hex(31002), "系统总电流", self.getTotalSystemCurrent(), "0.01"))
        dataList.append(self.getSystemDataPoint(31003, hex(31003), "系统SOC", self.getSystemSoc(), "0.01"))
        dataList.append(
            self.getSystemDataPoint(31009, hex(31009), "系统簇间电压差异", self.getVoltageDifference(), "0.01"))
        dataList.append(
            self.getSystemDataPoint(31010, hex(31010), "系统簇间电流差异", self.getCurrentDifference(), "0.01"))
        dataList.append(
            self.getSystemDataPoint(31011, hex(31011), "系统平均温度", self.getAverageTemperature(), "0.01"))
        dataList.append(self.getSystemDataPoint(31012, hex(31012), "系统平均电压", self.getAverageVoltage(), "0.01"))

        # 单体最高电压
        dataList.append(self.getSystemDataPoint(31013, hex(31013), "系统单体最高电压", self.getMaxVoltage(), "0.01"))
        dataList.append(
            self.getSystemDataPoint(31014, hex(31014), "系统单体最高电压簇号", self.getMaxVoltageClusterId(), "1"))
        dataList.append(
            self.getSystemDataPoint(31015, hex(31015), "系统单体最高电压模组号", self.getMaxVoltagePackId(), "1"))
        dataList.append(
            self.getSystemDataPoint(31016, hex(31016), "系统单体最高电压电芯号", self.getMaxVoltageCellId(), "1"))

        # 单体最低电压
        dataList.append(self.getSystemDataPoint(31017, hex(31017), "系统单体最低电压", self.getMinVoltage(), "0.01"))
        dataList.append(
            self.getSystemDataPoint(31018, hex(31018), "系统单体最低电压簇号", self.getMinVoltageClusterId(), "1"))
        dataList.append(
            self.getSystemDataPoint(31019, hex(31019), "系统单体最低电压模组号", self.getMinVoltagePackId(), "1"))
        dataList.append(
            self.getSystemDataPoint(31020, hex(31020), "系统单体最低电压电芯号", self.getMinVoltageCellId(), "1"))

        # 单体最高温度
        dataList.append(self.getSystemDataPoint(31021, hex(31021), "系统单体最高温度", self.getMaxTemperature(), "0.01"))
        dataList.append(
            self.getSystemDataPoint(31022, hex(31022), "系统单体最高温度簇号", self.getMaxTemperatureClusterId(), "1"))
        dataList.append(
            self.getSystemDataPoint(31023, hex(31023), "系统单体最高温度模组号", self.getMaxTemperaturePackId(), "1"))
        dataList.append(
            self.getSystemDataPoint(31024, hex(31024), "系统单体最高温度电芯号", self.getMaxTemperatureCellId(), "1"))

        # 单体最低温度
        dataList.append(self.getSystemDataPoint(31025, hex(31025), "系统单体最低温度", self.getMinTemperature(), "0.01"))
        dataList.append(
            self.getSystemDataPoint(31026, hex(31026), "系统单体最低温度簇号", self.getMinTemperatureClusterId(), "1"))
        dataList.append(
            self.getSystemDataPoint(31027, hex(31027), "系统单体最低温度模组号", self.getMinTemperaturePackId(), "1"))
        dataList.append(
            self.getSystemDataPoint(31028, hex(31028), "系统单体最低温度电芯号", self.getMinTemperatureCellId(), "1"))

    # 根据电芯导出数据点
    def exportCellDataPointByCell(self, dataList):
        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    dataList.append(
                        self.getCellDataPoint(cluster.cluster_id, pack.pack_id, cell.cell_id, "电压", cell.vol_address,
                                              hex(cell.vol_address),
                                              cell.voltage, "0.1"))
                    dataList.append(
                        self.getCellDataPoint(cluster.cluster_id, pack.pack_id, cell.cell_id, "电流",
                                              cell.current_address, hex(cell.current_address),
                                              cell.current, "0.1"))
                    dataList.append(
                        self.getCellDataPoint(cluster.cluster_id, pack.pack_id, cell.cell_id, "温度",
                                              cell.temperature_address, hex(cell.temperature_address),
                                              cell.temperature, "0.1"))
                    dataList.append(
                        self.getCellDataPoint(cluster.cluster_id, pack.pack_id, cell.cell_id, "SOC", cell.soc_address,
                                              hex(cell.soc_address),
                                              cell.soc, "0.01"))

    # 根据地址顺序导出数据点
    def exportCellDataPointByAddress(self, dataList):
        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    dataList.append(
                        self.getCellDataPoint(cluster.cluster_id, pack.pack_id, cell.cell_id, "电压", cell.vol_address,
                                              hex(cell.vol_address),
                                              cell.voltage, "0.1"))

        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    dataList.append(
                        self.getCellDataPoint(cluster.cluster_id, pack.pack_id, cell.cell_id, "电流",
                                              cell.current_address, hex(cell.current_address),
                                              cell.current, "0.1"))

        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    dataList.append(
                        self.getCellDataPoint(cluster.cluster_id, pack.pack_id, cell.cell_id, "温度",
                                              cell.temperature_address, hex(cell.temperature_address),
                                              cell.temperature, "0.1"))

        for cluster in self.clusterList:
            for pack in cluster.PackList:
                for cell in pack.CellList:
                    dataList.append(
                        self.getCellDataPoint(cluster.cluster_id, pack.pack_id, cell.cell_id, "SOC", cell.soc_address,
                                              hex(cell.soc_address),
                                              cell.soc, "0.01"))
