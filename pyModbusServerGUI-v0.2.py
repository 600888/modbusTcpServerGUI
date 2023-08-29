import threading
import time

from device.modbus_server import ModbusPcsServerGUI, ModbusBmsServerGUI
import dearpygui.dearpygui as dpg
import random
import csv

from pyModbusTCP.logger import log

NUMCOILS = 4000  # number of coils we allow user to configure in the GUI, if this is too large then the display is unusable
COILSPERROW = 40  # how many coil tickboxes to display in each table row
MAXCOILROWS = int(NUMCOILS / COILSPERROW)
MAXCOILS = 9999  # maximum size of coil list that can be imported
coilList = [0] * MAXCOILS

NUMREGISTERS = 4000  # number of registers that can be entered in the GUI
REGISTERSPERROW = 20  # how many to display on one row of the table
MAXREGISTERROWS = int(NUMREGISTERS / REGISTERSPERROW)
MAXREGISTERS = 9999
registerList = [0] * MAXREGISTERS
outputRegisterList = [0] * MAXREGISTERS

dpg.create_context()

modbusServer = None

thread = None
stop_event = threading.Event()


# print any debug info text into console
def debugLog(text):
    log.debug(text)


def setItemDisabled():
    dpg.disable_item("serverAddress")
    dpg.disable_item("serverPort")
    dpg.disable_item("modbusType")


def setItemEnabled():
    dpg.enable_item("serverAddress")
    dpg.enable_item("serverPort")
    dpg.enable_item("modbusType")


def startModbusServer(sender, app_data, user_data):
    global modbusServer
    try:
        modbusServer.setAddress(dpg.get_value("serverAddress"))
        modbusServer.setPort(dpg.get_value("serverPort"))
    except ValueError as e:
        with dpg.window(label="Error Window", tag="error", width=300, height=200):
            dpg.add_text(str(e))
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error"))
        return

    setItemDisabled()

    if modbusServer.startServer():
        dpg.configure_item("serverStatus", default_value="运行中")
        dpg.bind_item_theme("serverStatus", green_bg_theme)
    else:
        dpg.configure_item("serverStatus", default_value="停止")
        dpg.bind_item_theme("serverStatus", red_bg_theme)


def stopModbusServer(sender, app_data, user_data):
    setItemEnabled()
    stopAutoSimulation("uNF", "uNF", "uNF")
    if modbusServer.checkRunning():  # if it's not running then don't do anything
        if modbusServer.stopServer():  # try to stop the server
            dpg.configure_item("serverStatus", default_value="停止")
            dpg.bind_item_theme("serverStatus", red_bg_theme)
        else:
            dpg.configure_item("serverStatus", default_value="Error stopping server")


# modbusTCP 服务器收到消息后自动刷新界面

def checkModbusServer(sender, app_data):
    modbusServer.checkRunning()


def coilClicked(sender, app_data, user_data):
    debugLog(f"coilClicked - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global coilList

    if (user_data < COILSPERROW):
        row = 0
        col = user_data
    else:
        if ((user_data % COILSPERROW) == 0):
            col = COILSPERROW
            row = int(user_data / COILSPERROW) - 1
        else:
            col = user_data % COILSPERROW
            row = int(user_data / COILSPERROW)

    # debugLog("row: " + str(row) + " col: " + str(col))
    if (app_data == True):  # the box was ticked
        dpg.highlight_table_cell(coil_table_id, row, col, [0, 230, 0, 100])
        coilList[user_data] = 1
    else:  # the box was unticked from previously being selected
        dpg.highlight_table_cell(coil_table_id, row, col, [230, 0, 0, 100])
        coilList[user_data] = 0

    # debugLog("coilClicked:" + str(coilList)   )

    modbusServer.setCoilBits(coilList)


def randomiseCoils(sender, app_data, user_data):
    debugLog(f"randomiseCoils - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global coilList

    for i in range(1, MAXCOILROWS * COILSPERROW):
        if (i < COILSPERROW):
            row = 0
            col = i
        else:
            if ((i % COILSPERROW) == 0):
                col = COILSPERROW
                row = int(i / COILSPERROW) - 1
            else:
                col = i % COILSPERROW
                row = int(i / COILSPERROW)

        if random.randint(0, 100) > 50:
            dpg.highlight_table_cell(coil_table_id, row, col, [0, 230, 0, 100])
            coilList[i] = 1
            # print("coils" + str(i))
            # no idea why these sometimes fail, catch the exception and ignore it as it doesn't really impact much
            try:
                dpg.configure_item("coils" + str(i), default_value=True)
            except:
                debugLog("failed to update coil value to true for:" + str(i))
        else:
            try:
                dpg.configure_item("coils" + str(i), default_value=False)
                dpg.highlight_table_cell(coil_table_id, row, col, [230, 0, 0, 100])
            except:
                debugLog("failed to update coil value to false for:" + str(i))
            coilList[i] = 0

    # debugLog("RandomiseCoils array:" + str(coilList))
    modbusServer.setCoilBits(coilList)


def clearCoils(sender, app_data, user_data):
    debugLog(f"clearCoils - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global coilList

    for i in range(1, MAXCOILROWS * COILSPERROW):
        if i < COILSPERROW:
            row = 0
            col = i
        else:
            if (i % COILSPERROW) == 0:
                col = COILSPERROW
                row = int(i / COILSPERROW) - 1
            else:
                col = i % COILSPERROW
                row = int(i / COILSPERROW)

        dpg.configure_item("coils" + str(i), default_value=False)
        dpg.highlight_table_cell(coil_table_id, row, col, [230, 0, 0, 100])

    coilList = False
    coilList = [0] * MAXCOILS

    # debugLog("ClearCoils: " + str(coilList))
    modbusServer.clearCoilBits()


def setManualCoils(sender, app_data, user_data):
    debugLog(f"setManualCoils - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    # clear out the GUI options incase they were set before
    clearCoils("uNF", "uNF", "uNF")
    global coilList

    # convert list of numbers to correct format (list of size 9999 that's either 0 or 1)
    # assume values are between 0-9999 for the moment

    origList = dpg.get_value("coilValueInputText")
    if len(origList) < 1:  # no data provided
        dpg.configure_item("coilValueStatusText", default_value="Invalid List Format - Must be CSV")
        dpg.bind_item_theme("coilValueStatusText", red_bg_theme)
    else:
        # no format checking - possible future amendment
        origList = dpg.get_value("coilValueInputText").split(",")
        coilList = [0] * MAXCOILS

        for i in range(0, len(origList)):

            if origList[i] != ",":
                # debugLog("setting value for " + origList[i])
                val = int(origList[i])
                coilList[val] = 1

        modbusServer.setCoilBits(coilList)
        dpg.configure_item("coilValueStatusText", default_value="List Set")
        dpg.bind_item_theme("coilValueStatusText", green_bg_theme)


def randomiseRegisters(sender, app_data, user_data):
    debugLog(f"randomiseRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global registerList

    for i in range(1, NUMREGISTERS):
        randRegisterValue = random.randint(0, 4000)
        registerList[i] = randRegisterValue
        try:
            dpg.configure_item("registers" + str(i), default_value=randRegisterValue)  # set table entry to zero
        except:  # not sure why this sometimes fails
            debugLog("failed to update GUI field: registers" + str(i))
    modbusServer.setRegisterValues(registerList)


def clearRegisters(sender, app_data, user_data):
    debugLog(f"clearRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global registerList

    for i in range(1, NUMREGISTERS):
        dpg.configure_item("registers" + str(i), default_value="0")

    registerList = False
    registerList = [0] * MAXREGISTERS

    # debugLog("ClearCoils: " + str(coilList))
    modbusServer.clearRegisterValues("input")


def refreshRegisters(sender, app_data, user_data):
    debugLog(f"refreshRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global registerList
    tempRegisterList = modbusServer.readRegisterValues("input")
    for i in range(0, 9999):
        registerList[i] = tempRegisterList[i]
    for i in range(1, NUMREGISTERS):
        try:
            dpg.configure_item("registers" + str(i), default_value=registerList[i])
        except:  # not sure why this sometimes fails
            debugLog("failed to update GUI field: registers" + str(i))
    modbusServer.setRegisterValues(registerList)


def registerTextChanged(sender, app_data, user_data):
    debugLog(f"registerTextChangedsender - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global registerList
    if len(app_data) == 0:
        app_data = 0
        dpg.configure_item(sender, default_value="0")

    registerList[user_data] = app_data
    # debugLog("registerTextChanged: " + str(registerList))
    modbusServer.setRegisterValues(registerList, "input")


# 自动刷新输入寄存器
def autoSimulation(sender, app_data, user_data):
    startModbusServer("uNF", "uNF", "uNF")
    global stop_event
    stop_event = threading.Event()

    def bmsSimulationThread(sender, app_data, user_data):
        while not stop_event.is_set():
            setRandomCellValues(sender, app_data, user_data)
            refreshRegisters(sender, app_data, user_data)
            time.sleep(1)
        print("bms thread stopped")

    def pcsSimulationThread(sender, app_data, user_data):
        count = 0
        while not stop_event.is_set():
            if modbusServer.pcs.isStart == 1:
                setRandomPcsValues(sender, app_data, user_data)
            refreshRegisters(sender, app_data, user_data)
            time.sleep(1)
            count += 1
            # 设置pcs每运行五分钟关机五秒
            if count % 300 == 0:
                modbusServer.pcs.isStart = 0
            elif count % 305 == 0:
                modbusServer.pcs.isStart = 1
        print("pcs thread stopped")

    # 开启一个python线程每秒刷新一次
    global thread
    if modbusServer.getType() == "Modbus PCS":
        thread = threading.Thread(target=pcsSimulationThread, args=(sender, app_data, user_data))
    else:
        thread = threading.Thread(target=bmsSimulationThread, args=(sender, app_data, user_data))
    thread.start()


# 停止自动刷新输入寄存器
def stopAutoSimulation(sender, app_data, user_data):
    log.debug("stopRefreshRegisters")
    global thread, stop_event
    if thread is not None and thread.is_alive():
        stop_event.set()
        thread.join()


def randomiseOutputRegisters(sender, app_data, user_data):
    debugLog(f"randomiseOutputRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global outputRegisterList

    for i in range(1, NUMREGISTERS):
        randRegisterValue = random.randint(0, 4000)
        outputRegisterList[i] = randRegisterValue
        try:
            dpg.configure_item("outputregisters" + str(i), default_value=randRegisterValue)
        except:  # not sure why this sometimes fails
            debugLog("failed to update GUI field: outputregisters" + str(i))
    modbusServer.setRegisterValues(outputRegisterList, "output")


def refreshOutputRegistersTable(sender, app_data, user_data):
    debugLog(f"refreshCoils - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global outputRegisterList
    tempRegisterList = modbusServer.readRegisterValues("output")
    for i in range(0, 9999):
        outputRegisterList[i] = tempRegisterList[i]
    for i in range(1, NUMREGISTERS):
        try:
            dpg.configure_item("outputregisters" + str(i), default_value=outputRegisterList[i])
        except:  # not sure why this sometimes fails
            debugLog("failed to update GUI field: outputregisters" + str(i))
    modbusServer.setRegisterValues(outputRegisterList, "output")


# 设置单个电芯值
def setCellValues(sender, app_data, user_data):
    startModbusServer("uNF", "uNF", "uNF")
    with dpg.window(label="设置单个电芯值", modal=True, show=False, tag="cell", no_title_bar=True):
        dpg.add_text("设置单个电芯值!")
        dpg.add_separator()

        # 3个电池簇
        cluster_group = dpg.add_group(horizontal=True)
        cluster_id_list = ['0', '1', '2']
        dpg.add_text("电池簇ID:", tag="cluster_id_text", parent=cluster_group)
        dpg.add_combo(cluster_id_list, default_value=cluster_id_list[0], tag="cluster_id", width=250, indent=300)
        dpg.move_item("cluster_id", parent=cluster_group)

        # 10个电池模组
        pack_group = dpg.add_group(horizontal=True)
        pack_id_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        dpg.add_text("电池模组ID:", tag="pack_id_text", parent=pack_group)
        dpg.add_combo(pack_id_list, default_value=pack_id_list[0], tag="pack_id", width=250, indent=300)
        dpg.move_item("pack_id", parent=pack_group)

        # 24个电芯
        cell_group = dpg.add_group(horizontal=True)
        cell_id = []
        for i in range(0, 24):
            cell_id.append(str(i))
        dpg.add_text("电芯ID:", tag="cell_id_text", parent=cell_group)
        dpg.add_combo(cell_id, default_value=cell_id[0], tag="cell_id", width=250, indent=300)
        dpg.move_item("cell_id", parent=cell_group)

        # 电芯电压
        cell_vol_group = dpg.add_group(horizontal=True)
        dpg.add_input_text(label="电芯电压", tag="cell_voltage", width=100)
        dpg.move_item("cell_voltage", parent=cell_vol_group)

        # 电芯电流
        cell_current_group = dpg.add_group(horizontal=True)
        dpg.add_input_text(label="电芯电流", tag="cell_current", width=100)
        dpg.move_item("cell_current", parent=cell_current_group)

        # 电芯温度
        cell_temp_group = dpg.add_group(horizontal=True)
        dpg.add_input_text(label="电芯温度", tag="cell_temperature", width=100)
        dpg.move_item("cell_temperature", parent=cell_temp_group)

        # 电芯SOC
        cell_soc_group = dpg.add_group(horizontal=True)
        dpg.add_input_text(label="电芯SOC", tag="cell_soc", width=100)
        dpg.move_item("cell_soc", parent=cell_soc_group)

        def setCellOK(sender, app_data, user_data):
            cluster_id = int(dpg.get_value("cluster_id"))
            pack_id = int(dpg.get_value("pack_id"))
            cell_id = int(dpg.get_value("cell_id"))
            log.debug("cluster_id: " + str(cluster_id) + " pack_id: " + str(pack_id) + " cell_id: " + str(cell_id))
            cell = modbusServer.getSingleCellValues(cluster_id, pack_id, cell_id)
            log.debug("vol_address: " + str(cell.vol_address) + " temperature_address: " + str(
                cell.temperature_address) + " soc_address: " + str(cell.soc_address))
            cell_voltage = str(dpg.get_value("cell_voltage"))
            cell_current = str(dpg.get_value("cell_current"))
            cell_temperature = str(dpg.get_value("cell_temperature"))
            cell_soc = str(dpg.get_value("cell_soc"))
            cell.setValue(cell_voltage, cell_current, cell_temperature, cell_soc)
            modbusServer.setSingleCellValues(cell)
            dpg.delete_item("cell")

        with dpg.group(horizontal=True):
            dpg.add_button(label="确定", tag="ok", width=100, callback=setCellOK)
            dpg.add_button(label="取消", tag="cancel", width=100,
                           callback=lambda: dpg.delete_item("cell"))
    dpg.configure_item("cell", show=True)


def clearOutputRegisters(sender, app_data, user_data):
    debugLog(f"clearOutputRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global outputRegisterList

    for i in range(1, NUMREGISTERS):
        dpg.configure_item("outputregisters" + str(i), default_value="0")

    outputRegisterList = False
    outputRegisterList = [0] * MAXREGISTERS

    # debugLog("ClearCoils: " + str(coilList))
    modbusServer.clearRegisterValues("output")


def outputRegisterTextChanged(sender, app_data, user_data):
    debugLog(f"outputRegisterTextChanged - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF", "uNF", "uNF")
    global outputRegisterList
    if len(app_data) == 0:
        app_data = 0
        dpg.configure_item(sender, default_value="0")

    outputRegisterList[user_data] = app_data;
    modbusServer.setRegisterValues(outputRegisterList, "output")


def _log(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")


def on_modbus_type_selected(sender, data):
    global modbusServer
    modbus_type = dpg.get_value(sender)
    if modbus_type == "Modbus PCS":
        modbusServer = ModbusPcsServerGUI()
        modbusServer.setType("Modbus PCS")
        log.info("Modbus PCS")
        # 执行 Modbus PCS 相关逻辑
        pass
    else:
        modbusServer = ModbusBmsServerGUI()
        modbusServer.setType("Modbus BMS")
        log.info("Modbus BMS")
        # 执行 Modbus BMS 相关逻辑
        pass


def setRandomCellValues(sender, app_data, user_data):
    global modbusServer
    modbusServer.setRandomCellValues()


import tkinter as tk
from tkinter import filedialog


# 导出CSV文件
def export_csv(sender, app_data, user_data):
    dataList = []
    global modbusServer
    if modbusServer.getType() == "Modbus PCS":
        pcsDataPointHeader = ["地址", "16进制地址", "测点名", "测点值", "乘法系数"]
        dataList.append(pcsDataPointHeader)
        modbusServer.exportDataPoint(dataList)
    else:
        cellDataPointHeader = ["簇id", "模组id", "电芯id", "测点类型", "地址", "16进制地址", "测点值", "乘法系数"]
        dataList.append(cellDataPointHeader)
        # 导出电芯数据
        # modbusServer.exportCellDataPointByCell(dataList)
        modbusServer.exportCellDataPointByAddress(dataList)
        systemDataPointHeader = ["地址", "16进制地址", "测点名", "测点值", "乘法系数"]
        dataList.append(systemDataPointHeader)
        # 导出系统数据
        modbusServer.exportSystemDataPoint(dataList)

    # 创建一个 Tkinter 窗口
    root = tk.Tk()

    # 隐藏窗口
    root.withdraw()
    file_path = tk.filedialog.asksaveasfilename(title=u'保存文件', defaultextension='.csv',
                                                filetypes=[("csv格式", ".csv")])
    log.debug("file_path: " + file_path)
    # 如果用户选择了文件名，则保存文件
    if file_path:
        open(file_path, 'w').close()
        # 打开CSV文件并写入数据
        with open(file_path, 'w', newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            for row in dataList:
                writer.writerow(row)
        log.info("导出CSV文件成功")


########################################################################################################################
# PCS 配置相关
def setRandomPcsValues(sender, app_data, user_data):
    global modbusServer
    if modbusServer is None or not modbusServer.checkRunning() or modbusServer.getType() != "Modbus PCS":
        # 弹框提示
        with dpg.window(label="错误", tag="error", autosize=True, pos=[500, 400]):
            dpg.add_text("Modbus PCS 服务未开启")
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error"))
        log.info("Modbus PCS 服务未开启")
        return
    modbusServer.setSimulatePcsValues()


def pop_update_warning_window():
    with dpg.window(label="警告", modal=True, show=False, no_close=True, tag="warningWindow", pos=[500, 300]):
        dpg.add_text("只能选择一项修改！")
        log.warning("只能选择一项修改！")
        dpg.add_button(label="确定", width=100,
                       callback=lambda: dpg.delete_item("warningWindow"))
        dpg.configure_item("warningWindow", show=True)


pcs_check_box_list = []
pcs_config_list = []


def get_pcs_id_list():
    pcs_id_list = []
    for i in range(0, len(pcs_check_box_list)):
        if dpg.get_value(pcs_check_box_list[i]):
            pcs_id_list.append(i)
    return pcs_id_list

def clearConfigWindow():
    if dpg.does_item_exist("pcsConfigTable"):
        dpg.delete_item("pcsConfigTable")

def initPcsConfigTable():
    # addConfig("1", "1", "1", "1", "1", "有功功率", "1")
    clearConfigWindow()
    with dpg.child_window(autosize_x=True, horizontal_scrollbar=True, tag="pcsConfigWindow"):
        with dpg.table(tag="pcsConfigTable", header_row=True, row_background=False,
                       borders_innerH=True, borders_outerH=True, policy=dpg.mvTable_SizingFixedFit,
                       borders_innerV=True, scrollX=True, scrollY=True, freeze_rows=1,
                       borders_outerV=True, delay_search=True, no_host_extendX=True, resizable=True,
                       width=1800) as pcsConfig_Table:
            dpg.add_table_column(label="id")
            dpg.add_table_column(label="时间偏移量")
            dpg.add_table_column(label="PCS服务状态")
            dpg.add_table_column(label="运行模式")
            dpg.add_table_column(label="电压")
            dpg.add_table_column(label="电流")
            dpg.add_table_column(label="功率")
            for i in range(0, len(pcs_config_list)):
                with dpg.table_row():
                    checkbox_id = dpg.add_checkbox(label=str(i), tag="config_check_box" + str(i))
                    pcs_check_box_list.append(checkbox_id)
                    dpg.highlight_table_cell(pcsConfig_Table, i, 0, (31, 31, 31))
                    dpg.add_text(tag="pcs_config" + str(i * 20 + 1), default_value=pcs_config_list[i][1])
                    dpg.add_text(tag="pcs_config" + str(i * 20 + 2), default_value=pcs_config_list[i][2])
                    dpg.add_text(tag="pcs_config" + str(i * 20 + 3), default_value=pcs_config_list[i][3])
                    dpg.add_text(tag="pcs_config" + str(i * 20 + 4), default_value=pcs_config_list[i][4])
                    dpg.add_text(tag="pcs_config" + str(i * 20 + 5), default_value=pcs_config_list[i][5])
                    dpg.add_text(tag="pcs_config" + str(i * 20 + 6), default_value=pcs_config_list[i][6])
            dpg.configure_item(pcsConfig_Table, height=500)


def addConfig(time_offset, server_status, run_mode, voltage, current, power_type, power):
    if power_type == "有功功率":
        power_text = "有功功率：" + str(power) + "kw"
    else:
        power_text = "无功功率：" + str(power) + "kw"

    pcs_config = [len(pcs_config_list), time_offset, server_status, run_mode, voltage, current, power_text]
    pcs_config_list.append(pcs_config)
    dpg.delete_item("addConfigWindow")
    dpg.delete_item("pcsConfigWindow")
    initPcsConfigTable()
    log.info("pcs配置添加成功！")


def setPcsConfigWindow(pcs_label, window, method):
    pcs_id_list = get_pcs_id_list()
    if method == "update":
        if len(pcs_id_list) != 1:
            # 弹出警告框提示
            pop_update_warning_window()
            return

    with dpg.window(label=pcs_label, show=False, no_collapse=True, tag=window, pos=[300, 200],
                    no_close=True):
        start_indent = 150
        input_width = 300
        text_indent = 480
        second_input_indent = 650
        with dpg.group(horizontal=True):
            dpg.add_text("时间偏移量：")
            time_offset = dpg.add_input_text(tag="time_offset", indent=start_indent, width=input_width,
                                             default_value="5")
            dpg.add_text("PCS服务状态：", indent=text_indent)
            server_status = dpg.add_checkbox(tag="server_status", indent=second_input_indent)
        with dpg.group(horizontal=True):
            dpg.add_text("运行模式：")
            run_mode = dpg.add_input_text(tag="run_ode", indent=start_indent, width=input_width,hint="0：恒功率；1：恒流")
            dpg.add_text("电压：", indent=text_indent)
            voltage = dpg.add_input_text(tag="voltage", indent=second_input_indent, width=input_width)
        with dpg.group(horizontal=True):
            dpg.add_text("电流：")
            current = dpg.add_input_text(tag="current", indent=start_indent, width=input_width)
            dpg.add_text("功率：", indent=text_indent)
            power_combo = dpg.add_combo(["有功功率", "无功功率"], default_value="有功功率", tag="power_type",
                                        indent=second_input_indent, width=input_width)
            power_text = dpg.add_input_text(tag="power", width=input_width)

        if method == "update":
            dpg.set_value(time_offset, pcs_config_list[pcs_id_list[-1]][1])
            dpg.set_value(server_status, pcs_config_list[pcs_id_list[-1]][2])
            dpg.set_value(run_mode, pcs_config_list[pcs_id_list[-1]][3])
            dpg.set_value(voltage, pcs_config_list[pcs_id_list[-1]][4])
            dpg.set_value(current, pcs_config_list[pcs_id_list[-1]][5])
            dpg.set_value(power_combo, pcs_config_list[pcs_id_list[-1]][6])

        with dpg.group(horizontal=True):
            dpg.add_button(label="确定", width=100,
                           callback=lambda: addConfig(dpg.get_value("time_offset"),
                                                      bool(dpg.get_value("server_status")),
                                                      dpg.get_value("run_mode"), dpg.get_value("voltage"),
                                                      dpg.get_value("current"), dpg.get_value("power_type"),
                                                      dpg.get_value("power")))
            dpg.add_button(label="取消", width=100,
                           callback=lambda: dpg.delete_item(window))
        dpg.configure_item(window, show=True)


def addConfigWindow():
    setPcsConfigWindow("添加配置", "addConfigWindow", "add")


def updateConfigWindow():
    setPcsConfigWindow("修改配置", "updateConfigWindow", "update")


def deleteConfig():
    pass


# 注册字体，自选字体
with dpg.font_registry():
    with dpg.font("resources/Adobe Fangsong Std.otf", 25) as font:  # 增加中文编码范围，防止问号
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
    default_font = font

with dpg.theme() as green_bg_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 153, 0), category=dpg.mvThemeCat_Core)

with dpg.theme() as red_bg_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (230, 0, 0), category=dpg.mvThemeCat_Core)

with dpg.window(tag="Primary Window", width=1500):
    dpg.bind_font(default_font)
    dpg.add_text("Modbus/TCP 服务器地址:", tag="serverText")

    # get list of all available IPs and offer to user in a dropdown list
    from netifaces import interfaces, ifaddresses, AF_INET

    ip_list = []
    for interface in interfaces():
        debugLog("Address Found: " + str(ifaddresses(interface)))
        for link in ifaddresses(interface).get(AF_INET, ()):
            ip_list.append(link['addr'])

    dpg.add_combo(ip_list, default_value=ip_list[0], tag="serverAddress", width=250, indent=300)
    serverAddressGroup = dpg.add_group(horizontal=True)
    dpg.move_item("serverText", parent=serverAddressGroup)
    dpg.move_item("serverAddress", parent=serverAddressGroup)

    dpg.add_text("端口号:", tag="serverPortText")
    dpg.add_input_text(default_value="10502", tag="serverPort", width=100, indent=300)

    deviceTypeGroup = dpg.add_group(horizontal=True)
    dpg.add_text("设备类型:", tag="deviceTypeText", parent=deviceTypeGroup)
    # 设置MODBUS的下拉框选项
    modbus_combo = dpg.add_combo(("Modbus PCS", "Modbus BMS"), default_value="Modbus BMS", tag="modbusType", width=250,
                                 indent=300, parent=deviceTypeGroup)
    on_modbus_type_selected(modbus_combo, None)
    dpg.set_item_callback(modbus_combo, on_modbus_type_selected)

    serverPortGroup = dpg.add_group(horizontal=True)
    dpg.move_item("serverPortText", parent=serverPortGroup)
    dpg.move_item("serverPort", parent=serverPortGroup)

    dpg.add_button(label="开启服务", callback=startModbusServer, tag="startServerButton")
    dpg.add_button(label="停止服务", callback=stopModbusServer, tag="stopServerButton")
    dpg.add_button(label="确认服务", callback=checkModbusServer, tag="checkServerButton")
    dpg.add_text("状态:", tag="serverStatusText")
    dpg.add_input_text(default_value="停止", tag="serverStatus", width=150, readonly=True, indent=300)
    serverStatusGroup = dpg.add_group(horizontal=True)
    dpg.move_item("serverStatusText", parent=serverStatusGroup)
    dpg.move_item("serverStatus", parent=serverStatusGroup)
    dpg.move_item("startServerButton", parent=serverStatusGroup)
    dpg.move_item("stopServerButton", parent=serverStatusGroup)
    dpg.move_item("checkServerButton", parent=serverStatusGroup)

    # 设置电芯数据
    with dpg.group(horizontal=True):
        dpg.add_button(label="设置单个电芯值", callback=setCellValues,
                       tag="setCellValuesButton")
        dpg.add_button(label="随机设置所有电芯值", callback=setRandomCellValues,
                       tag="randomiseAllCellButton")
        dpg.add_button(label="随机设置所有PCS值", callback=setRandomPcsValues,
                       tag="randomiseAllPcsValuesButton")

        # 导出CSV文件
        dpg.add_button(label="导出CSV文件", callback=export_csv, tag="exportCSVButton")

    # 1-9999 - discrete output coils R/W - binary
    # At the moment it is R/O, the backend server library may let clients write values but they won't be reflected in the GUI
    with dpg.collapsing_header(label="离散输出线圈值"):
        with dpg.child_window(autosize_x=True, horizontal_scrollbar=True) as _coil_child_window:

            dpg.add_button(label="随机生成线圈值", callback=randomiseCoils, tag="randomiseCoilsButton")
            dpg.add_button(label="清空线圈值", callback=clearCoils, tag="clearCoilsButton")
            # dpg.add_button(label="Refresh Table", callback=refreshCoils, tag="refreshCoilsButton")
            coilValueGroup = dpg.add_group(horizontal=True)
            dpg.move_item("randomiseCoilsButton", parent=coilValueGroup)
            dpg.move_item("clearCoilsButton", parent=coilValueGroup)
            # dpg.move_item("refreshCoilsButton", parent=coilValueGroup)

            with dpg.table(tag="coilsTable", header_row=True, row_background=False,
                           borders_innerH=True, borders_outerH=True, policy=dpg.mvTable_SizingFixedFit,
                           borders_innerV=True, scrollX=True, scrollY=True, freeze_rows=1,
                           borders_outerV=True, delay_search=True, no_host_extendX=True, resizable=True,
                           width=1800) as coil_table_id:
                for i in range(COILSPERROW + 1):
                    if i == 0:
                        dpg.add_table_column()
                    else:
                        dpg.add_table_column(label=i)

                for i in range(MAXCOILROWS):
                    with dpg.table_row():
                        for j in range(0, COILSPERROW + 1):
                            if j == 0:
                                rowval = COILSPERROW * i
                                dpg.add_text(f"{rowval}")
                            else:
                                dpg.add_checkbox(tag="coils" + str(i * COILSPERROW + j), callback=coilClicked,
                                                 user_data=(COILSPERROW * i + j))
                                dpg.highlight_table_cell(coil_table_id, i, j, [230, 0, 0, 100])

    with dpg.collapsing_header(label="导入CSV设置离散输入寄存器"):
        dpg.add_text("输入以逗号分隔的线圈值列表作为1-9999地址范围内的整数值")
        dpg.add_input_text(default_value="", tag="coilValueInputText", multiline=True)
        dpg.add_button(label="设置离散量输入值", callback=setManualCoils, tag="setManualCoilsButton")
        dpg.add_input_text(default_value="状态", tag="coilValueStatusText", readonly=True)

    # 30001 - 39999 - 输入寄存器 - R/O - 16 bit int
    with dpg.collapsing_header(
            label="模拟输入寄存器值GUI，如果客户端更改了值，需手动点击刷新按钮才能更新GUI"):
        with dpg.group(horizontal=True):
            dpg.add_button(label="随机生成输入寄存器值", callback=randomiseRegisters,
                           tag="randomiseRegistersButton")
            dpg.add_button(label="清空输入寄存器值", callback=clearRegisters, tag="clearRegistersButton")
            dpg.add_button(label="刷新", callback=refreshRegisters, tag="refreshRegistersButton")
            dpg.add_button(label="自动模拟", callback=autoSimulation, tag="autoSimulationButton")
            dpg.add_button(label="停止模拟", callback=stopAutoSimulation, tag="stopRefreshRegistersButton")
        with dpg.child_window(autosize_x=True, horizontal_scrollbar=True) as _register_child_window:
            # grid allowing entry of values 1-MAXREGISTERS

            with dpg.table(tag="registersTable", header_row=True, row_background=False,
                           borders_innerH=True, borders_outerH=True, policy=dpg.mvTable_SizingFixedFit,
                           borders_innerV=True, scrollX=True, scrollY=True, freeze_rows=1,
                           borders_outerV=True, delay_search=True, no_host_extendX=True, resizable=True,
                           width=1800) as register_table_id:
                for i in range(REGISTERSPERROW + 1):
                    if i == 0:
                        dpg.add_table_column()
                    else:
                        dpg.add_table_column(label=i)

                for i in range(MAXREGISTERROWS):
                    with dpg.table_row():
                        for j in range(0, REGISTERSPERROW + 1):
                            if j == 0:
                                rowval = 30000 + (REGISTERSPERROW * i)
                                dpg.add_text(f"{rowval}")
                            else:
                                dpg.add_input_text(tag="registers" + str(i * REGISTERSPERROW + j),
                                                   callback=registerTextChanged, decimal=True, width=75,
                                                   user_data=i * REGISTERSPERROW + j)

    # 40001 - 49999 - 输出保持寄存器 - R/W - 16 bit int
    with dpg.collapsing_header(
            label="模拟输出寄存器值GUI，如果客户端更改了值，需手动点击刷新按钮才能更新GUI"):
        with dpg.child_window(autosize_x=True, horizontal_scrollbar=True) as _output_register_child_window:
            with dpg.group(horizontal=True):
                dpg.add_button(label="随机生成输出寄存器值", callback=randomiseOutputRegisters,
                               tag="randomiseOutputRegistersButton")
                dpg.add_button(label="清空输出寄存器值", callback=clearOutputRegisters,
                               tag="clearOutputRegistersButton")
                dpg.add_button(label="刷新界面", callback=refreshOutputRegistersTable,
                               tag="refreshOutputRegistersTableButton")
            # grid allowing entry of values 1-MAXREGISTERS

            with dpg.table(tag="outputRegistersTable", header_row=True, row_background=False,
                           borders_innerH=True, borders_outerH=True, policy=dpg.mvTable_SizingFixedFit,
                           borders_innerV=True, scrollX=True, scrollY=True, freeze_rows=1,
                           borders_outerV=True, delay_search=True, no_host_extendX=True, resizable=True,
                           width=1800) as output_register_table_id:
                for i in range(REGISTERSPERROW + 1):
                    if i == 0:
                        dpg.add_table_column()
                    else:
                        dpg.add_table_column(label=i)

                for i in range(MAXREGISTERROWS):
                    with dpg.table_row():
                        for j in range(0, REGISTERSPERROW + 1):
                            if j == 0:
                                rowval = 40000 + (REGISTERSPERROW * i)
                                dpg.add_text(f"{rowval}")
                            else:
                                dpg.add_input_text(tag="outputregisters" + str(i * REGISTERSPERROW + j),
                                                   callback=outputRegisterTextChanged, decimal=True, width=75,
                                                   user_data=i * REGISTERSPERROW + j)

    with dpg.collapsing_header(label="PCS配置"):
        with dpg.group(horizontal=True):
            dpg.add_button(label="添加配置", callback=addConfigWindow, tag="addConfigButton")
            dpg.add_button(label="修改配置", callback=updateConfigWindow, tag="updateConfigButton")
            dpg.add_button(label="删除配置", callback=deleteConfig, tag="deleteConfigButton")
        initPcsConfigTable()

dpg.create_viewport(title='pyModbusServerGUI', width=1800, height=1000)

# 设置主窗口图标
dpg.set_viewport_large_icon("resources/m.ico")
# 设置任务栏图标
dpg.set_viewport_small_icon("resources/m.ico")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.set_exit_callback(stopAutoSimulation)
dpg.start_dearpygui()
dpg.destroy_context()
