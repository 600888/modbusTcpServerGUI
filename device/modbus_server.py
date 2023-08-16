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
            self.errorLog("Invalid port number!")
            raise ValueError("Invalid port number!")

    def checkRunning(self):
        if not self.serverObj:
            self.errorLog("Server not running")
            return False

        if self.serverObj.is_run:
            self.running = True
            self.debugLog("Server Running")
            return True
        else:
            self.running = False
            self.errorLog("Server not running")
            return False

    # 根据地址设置值
    def setValueByAddress(self, address, value, type="output"):
        # 如果值为空，则设置一个默认值
        if not address:
            address = "40000"
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


class ModbusPcsServerGUI(ModbusServerGUI):
    pass


class ModbusBmsServerGUI(ModbusServerGUI):
    clusterList = []

    def __init__(self):
        super().__init__()
        # 一个BMS中有3簇，每簇10个模组，每个pack有24个电芯
        for i in range(0, 3):
            self.clusterList.append(Cluster())
            for j in range(0, 10):
                self.clusterList[i].PackList.append(Pack())
                for k in range(0, 24):
                    self.clusterList[i].PackList[j].CellList.append(Cell())

    # 设置单个电芯的值
    def setSingleCellValues(self, cluster_id, pack_id, cell_id, vol_address, voltage, temperature_address, temperature):
        self.clusterList[cluster_id].PackList[pack_id].CellList[cell_id].setValue(cell_id, voltage, temperature,
                                                                                  vol_address, temperature_address)
        log.debug("cluster_id: " + str(cluster_id) + " pack_id: " + str(pack_id) + " cell_id: " + str(
            cell_id) + " vol_address: " + str(vol_address) + " voltage: " + str(
            voltage) + " temperature_address: " + str(
            temperature_address) + " temperature: " + str(temperature))
        self.setValueByAddress(vol_address, voltage, "input")
        self.setValueByAddress(temperature_address, temperature, "input")

    # 获取单个电芯的值
    def getSingleCellValues(self, cluster_id, pack_id, cell_id):
        return self.clusterList[cluster_id].PackList[pack_id].CellList[cell_id]

    # 设置单个pack的值
    def setPackValues(self, address, voltage, temperature):
        pass

    # 设置单个簇的值
    def setClusterValues(self, cluster_id, pack_id, cell_id, address, voltage, temperature):
        pass
