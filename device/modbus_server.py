import random

from pyModbusTCP.server import ModbusServer, ModbusServerDataBank, log
from device.bms import Cluster, Pack, Cell
import time


class ModbusServerGUI:
    running = False
    address = "127.0.0.1"
    port = 10502
    serverObj = False  # server object from pyModbusTCP library
    dataBank = False

    def __init__(self):
        # databank object is used by pyModbusTCP to store the response values
        self.dataBank = ModbusServerDataBank()

    def startServer(self):
        if self.checkRunning():
            return True

        self.serverObj = ModbusServer(host=self.address, port=self.port, no_block=True, data_bank=self.dataBank)
        self.serverObj.start()

        # Wait 2 seconds for everything to settle and then check our status
        time.sleep(2)
        return self.checkRunning()

    def stopServer(self):
        self.serverObj.stop()
        time.sleep(2)  # wait 2 seconds for it to settle
        if not self.checkRunning():
            self.serverObj = False
            return True
        else:
            return False

    def setCoilBits(self, coilList):
        self.debugLog("setCoilBits with array size: " + str(len(coilList)))
        # self.debugLog("array: " + str(coilList))

        if not self.checkRunning():
            self.debugLog("set coils called without live server")
            return False

        # self.data_hdl.dataBank.set_coils(0, coilList)
        self.serverObj.data_hdl.write_coils(0, coilList, "None")

    def setRegisterValues(self, registerList, type="input"):
        self.debugLog("setRegisterValues with array size: " + str(len(registerList)))
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
    pass


class ModbusBmsServerGUI(ModbusServerGUI):
    clusterList = []

    def __init__(self):
        super().__init__()
        # 一个BMS中有3簇，每簇10个模组，每个pack有24个电芯
        cluster_list_count = 3
        pack_list_count = 10
        cell_count = 24
        # 初始化三维列表
        for i in range(cluster_list_count):
            pack_list = []
            for j in range(pack_list_count):
                cell_list = []
                for k in range(cell_count):
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
                    vol = random.randint(300, 600)  # 系数乘以0.1
                    current = random.randint(100, 200)  # 系数乘以0.1
                    temp = random.randint(200, 300)  # 系数乘以0.1
                    soc = random.randint(8000, 9900)  # 系数乘以0.01
                    cell.setValue(vol, current, temp, soc)
                    self.setSingleCellValues(cell)
                pack.setValue()
                self.setSinglePackValues(pack)
            cluster.setValue()
            self.setSingleClusterValues(cluster)

    def getTotalSystemVoltage(self):
        return sum([cluster.voltage for cluster in self.clusterList])
