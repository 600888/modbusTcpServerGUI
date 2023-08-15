from device.modbus_server import ModbusPcsServerGUI, ModbusBmsServerGUI

if __name__ == "__main__":
    modbusServer = ModbusPcsServerGUI()
    modbusServer.setPort(10502)
    modbusServer.startServer()
    while True:
        continue