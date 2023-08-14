from pyModbusTCP.server import ModbusServer, ModbusServerDataBank
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
            self.debugLog("Invalid port number!")
            raise ValueError("Invalid port number!")

    def checkRunning(self):
        if not self.serverObj:
            self.debugLog("Server not running")
            return False

        if self.serverObj.is_run:
            self.running = True
            self.debugLog("Server Running")
            return True
        else:
            self.running = False
            self.debugLog("Server not running")
            return False

    @staticmethod
    def debugLog(data=None):
        print(data)


class ModbusPcsServerGUI(ModbusServerGUI):
    pass


class ModbusBmsServerGUI(ModbusServerGUI):
    pass
