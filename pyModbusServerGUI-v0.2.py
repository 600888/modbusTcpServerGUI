import os
import threading
import time
from typing import List

from config.pcs_config import PcsConfig
from config.simulation_thread import SimulationThread
from device.modbus_server import ModbusPcsServerGUI, ModbusBmsServerGUI
import dearpygui.dearpygui as dpg
import random
import csv
from view.battery_stack_view import initBatteryStackInfoView, refresh_battery_text
from view.battery_cluster_view import initBatteryClusterInfoView, refresh_battery_cluster_text
from view.pcs_view import initPcsInfoView, refresh_pcs_text

development = False
if development:
    from pyModbusTCP.logger import log
else:
    import my_log

# 隐藏控制台
# if sys.platform == "win32":
#     import ctypes
#
#     ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

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

log = None


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
    startModbusServer("uNF", "uNF", "uNF")
    global registerList

    for i in range(1, NUMREGISTERS):
        dpg.configure_item("registers" + str(i), default_value="0")

    registerList = False
    registerList = [0] * MAXREGISTERS

    # debugLog("ClearCoils: " + str(coilList))
    modbusServer.clearRegisterValues("input")


def refreshRegisters(sender, app_data, user_data):
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

    def bmsSimulationThread(sender, app_data, user_data):
        dpg.configure_item("batteryStatus", default_value="运行")
        dpg.bind_item_theme("batteryStatus", green_bg_theme)
        while not modbusServer.simulation_thread.stop_event.is_set():
            setRandomCellValues(sender, app_data, user_data)
            refreshRegisters(sender, app_data, user_data)
            refreshOutputRegistersTable(sender, app_data, user_data)
            refresh_battery_text(modbusServer)
            refresh_battery_cluster_text(modbusServer)
            time.sleep(0.1)
        print("bms thread stopped")

    def pcsSimulationThread(sender, app_data, user_data):
        count = 0
        while not modbusServer.simulation_thread.stop_event.is_set():
            setRandomPcsValues(sender, app_data, user_data)
            refreshRegisters(sender, app_data, user_data)
            # refresh_pcs_text(modbusServer)
            time.sleep(0.1)
            count += 1
        print("pcs thread stopped")

    # 开启一个python线程每秒刷新一次
    global modbusServer
    modbusServer.simulation_thread.stop_event.clear()
    modbusServer.simulation_thread.thread = None
    if modbusServer.getType() == "Modbus PCS":
        modbusServer.simulation_thread.set_thread(
            threading.Thread(target=pcsSimulationThread, args=(sender, app_data, user_data)))
    else:
        modbusServer.simulation_thread.set_thread(
            threading.Thread(target=bmsSimulationThread, args=(sender, app_data, user_data)))
    modbusServer.simulation_thread.start()


# 停止自动刷新输入寄存器
def stopAutoSimulation(sender, app_data, user_data):
    log.debug("stopRefreshRegisters")
    global simulation_thread
    modbusServer.simulation_thread.stopAutoSimulation(sender, app_data, user_data, dpg, red_bg_theme)


def randomiseOutputRegisters(sender, app_data, user_data):
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
    log.debug("setCellValues")
    with dpg.window(label="设置单个电芯值", show=False, tag="setSingleCellWindow", no_title_bar=True, pos=[200, 200]):
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
                           callback=lambda: dpg.delete_item("setSingleCellWindow"))
    dpg.configure_item("setSingleCellWindow", show=True)


def clearOutputRegisters(sender, app_data, user_data):
    startModbusServer("uNF", "uNF", "uNF")
    global outputRegisterList

    for i in range(1, NUMREGISTERS):
        dpg.configure_item("outputregisters" + str(i), default_value="0")

    outputRegisterList = False
    outputRegisterList = [0] * MAXREGISTERS

    # debugLog("ClearCoils: " + str(coilList))
    modbusServer.clearRegisterValues("output")


def outputRegisterTextChanged(sender, app_data, user_data):
    startModbusServer("uNF", "uNF", "uNF")
    global outputRegisterList
    if len(app_data) == 0:
        app_data = 0
        dpg.configure_item(sender, default_value="0")

    outputRegisterList[user_data] = app_data
    modbusServer.setRegisterValues(outputRegisterList, "output")


def _log(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")


def on_modbus_type_selected(sender, data):
    global modbusServer, simulation_thread
    modbus_type = dpg.get_value(sender)
    if modbus_type == "Modbus PCS":
        modbusServer = ModbusPcsServerGUI()
        modbusServer.setType("Modbus PCS")
        log.info("Modbus PCS")
        # 执行 Modbus PCS 相关逻辑
        pass
    else:
        modbusServer = ModbusBmsServerGUI()
        modbusServer.set_cluster_data()
        modbusServer.setType("Modbus BMS")
        log.info("Modbus BMS")
        # 执行 Modbus BMS 相关逻辑
        pass


def setRandomCellValues(sender, app_data, user_data):
    global modbusServer
    if modbusServer is None or not modbusServer.checkRunning() or modbusServer.getType() != "Modbus BMS":
        # 弹窗警告没有开启BMS服务
        with dpg.window(label="警告", modal=True, show=False, no_close=True, tag="warningWindow", pos=[500, 300]):
            dpg.add_text("Modbus BMS服务未开启")
            log.warning("Modbus BMS服务未开启")
            dpg.add_button(label="确定", width=100,
                           callback=lambda: dpg.delete_item("warningWindow"))
            dpg.configure_item("warningWindow", show=True)

    modbusServer.setRandomCellValues()


import tkinter as tk
from tkinter import filedialog


# 导入CSV文件
def import_csv(sender, app_data, user_data):
    dataList = []
    global modbusServer

    log.debug("import_csv")
    fTyp = [("", "*")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    file_name = tk.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
    log.debug("file_name: " + file_name)

    if modbusServer.getType() == "Modbus PCS":
        modbusServer.pcs.importDataPointCsv(file_name)
        # 弹窗提示导入成功
        with dpg.window(label="提示", modal=True, show=False, no_close=True, tag="successWindow", pos=[500, 300]):
            dpg.add_text("导入成功")
            log.info("导入成功")
            dpg.add_button(label="确定", width=100,
                           callback=lambda: dpg.delete_item("successWindow"))
            dpg.configure_item("successWindow", show=True)
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
pcs_config_list: List[PcsConfig] = []
select_all_pcs_config_flag = False


def get_pcs_id_list():
    pcs_id_list = []
    for check_box in pcs_check_box_list:
        if dpg.get_value(check_box):
            pcs_id_list.append(int(dpg.get_item_label(check_box)))
    return pcs_id_list


def clearConfigWindow():
    if dpg.does_item_exist("pcsMainWindow"):
        dpg.delete_item("pcsMainWindow")


def select_all_pcs_config():
    global select_all_pcs_config_flag
    select_all_pcs_config_flag = not select_all_pcs_config_flag
    for check_box in pcs_check_box_list:
        dpg.set_value(check_box, select_all_pcs_config_flag)


import json
from config.pcs_config import Strategy


def import_pcs_config():
    global pcs_config_list
    # 创建一个 Tkinter 窗口
    root = tk.Tk()
    # 隐藏窗口
    root.withdraw()
    file_path = tk.filedialog.askopenfilename(title=u'选择文件', defaultextension='.json',
                                              filetypes=[("json格式", ".json")])
    log.debug("file_path: " + file_path)
    # 如果用户选择了文件名，则保存文件
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
            log.debug("data: " + str(data))
            length = len(data)
            log.debug("length: " + str(length))
            for obj in data:
                pcs_config = PcsConfig(obj["id"], obj["偏移量"], obj["pcs服务开启"], obj["运行模式"],
                                       obj["电压"], obj["电流"], obj["功率"]["类型"], obj["功率"]["值"])
                pcs_config_list.append(pcs_config)

            if not Strategy.check_strategy(pcs_config_list):
                for i in range(length):
                    pcs_config_list.pop()
                # 弹窗警告
                with dpg.window(label="警告", modal=True, show=False, no_close=True, tag="warningWindow",
                                pos=[500, 300]):
                    dpg.add_text("导入配置文件失败！")
                    log.warning("导入配置文件失败！")
                    dpg.add_button(label="确定", width=100,
                                   callback=lambda: dpg.delete_item("warningWindow"))
                    dpg.configure_item("warningWindow", show=True)
                    return
        initPcsConfig()
        log.info("导入json配置文件成功")


def export_pcs_config():
    # 创建一个 Tkinter 窗口
    root = tk.Tk()

    # 隐藏窗口
    root.withdraw()
    file_path = tk.filedialog.asksaveasfilename(title=u'保存文件', defaultextension='.json',
                                                filetypes=[("json格式", ".json")])
    log.debug("file_path: " + file_path)
    # 如果用户选择了文件名，则保存文件
    if file_path:
        open(file_path, 'w').close()
        # 打开CSV文件并写入数据
        with open(file_path, 'w', newline="", encoding="utf-8") as output_file:
            json.dump([obj.__dict__() for obj in pcs_config_list], output_file, ensure_ascii=False)
        log.info("导出json配置文件成功")


def applyConfig(sender, app_data, user_data):
    # 如果服务没开启，弹窗警告
    if modbusServer is None or not modbusServer.checkRunning() or modbusServer.getType() != "Modbus PCS":
        with dpg.window(label="错误", tag="error", autosize=True, pos=[500, 400]):
            dpg.add_text("Modbus PCS 服务未开启")
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error"))
        log.info("Modbus PCS 服务未开启")
        return

    global pcs_config_list

    def get_pcs_config_list(loop_count):
        config_list = []
        for i in range(loop_count):
            for j in range(len(pcs_config_list)):
                pcs_config = PcsConfig(pcs_config_list[j].id + i * len(pcs_config_list),
                                       str(int(pcs_config_list[j].time_offset) + i * int(
                                           pcs_config_list[-1].time_offset)),
                                       pcs_config_list[j].server_status, pcs_config_list[j].run_mode,
                                       pcs_config_list[j].voltage, pcs_config_list[j].current,
                                       pcs_config_list[j].power_type, pcs_config_list[j].power)
                config_list.append(pcs_config)
        return config_list

    def pcsApplyConfigThread(sender, app_data, user_data):
        log.info("pcs thread started")
        count = 0
        i = 0
        config_list = get_pcs_config_list(dpg.get_value("loopCount"))
        while not modbusServer.simulation_thread.stop_event.is_set():
            if i < len(config_list):
                if int(config_list[i].time_offset) == count:
                    modbusServer.setPcsConfig(config_list[i])
                    refresh_pcs_text(modbusServer)
                    log.info("设置第" + str(i + 1) + "个配置"
                             + " 偏移量：" + str(config_list[i].time_offset +
                                                " pcs服务开启：" + str(config_list[i].server_status) +
                                                " 运行模式：" + str(config_list[i].run_mode) +
                                                " 电压：" + str(config_list[i].voltage) +
                                                " 电流：" + str(config_list[i].current) +
                                                " 功率类型：" + str(config_list[i].power_type) +
                                                " 功率值：" + str(config_list[i].power)))
                    i += 1
            refreshRegisters(sender, app_data, user_data)
            time.sleep(1)
            count += 1
        log.warning("pcs thread stopped")

    # 开启一个python线程每秒刷新一次
    modbusServer.simulation_thread.stop_event.clear()
    modbusServer.simulation_thread.thread = None
    if modbusServer.getType() == "Modbus PCS":
        modbusServer.simulation_thread.thread = threading.Thread(target=pcsApplyConfigThread,
                                                                 args=(sender, app_data, user_data))
    modbusServer.simulation_thread.start()

    if modbusServer.simulation_thread.thread is not None and modbusServer.simulation_thread.thread.is_alive():
        dpg.configure_item("configStatus", default_value="应用中")
        dpg.bind_item_theme("configStatus", green_bg_theme)
    else:
        dpg.configure_item("configStatus", default_value="停止")
        dpg.bind_item_theme("configStatus", red_bg_theme)


def initPcsConfig():
    pcs_check_box_list.clear()
    clearConfigWindow()
    with dpg.child_window(autosize_x=True, autosize_y=True, horizontal_scrollbar=True, tag="pcsMainWindow",
                          parent="pcsConfig"):
        with dpg.group(horizontal=True):
            dpg.add_button(label="全选", callback=select_all_pcs_config, tag="selectAllPcsConfigButton")
            dpg.add_button(label="添加配置", callback=addConfigWindow, tag="addConfigButton")
            dpg.add_button(label="修改配置", callback=updateConfigWindow, tag="updateConfigButton")
            dpg.add_button(label="删除配置", callback=deleteConfig, tag="deleteConfigButton")
            dpg.add_button(label="导入配置", callback=import_pcs_config, tag="importPcsConfig")
            dpg.add_button(label="导出配置", callback=export_pcs_config, tag="exportPcsConfig")
        with dpg.group(horizontal=True):
            dpg.add_input_int(label="循环次数", tag="loopCount", width=150, default_value=1, min_clamped=True,
                              min_value=1)
            dpg.add_input_text(default_value="", tag="configStatus", indent=298, width=108, readonly=True)
            dpg.configure_item("configStatus", default_value="停止")
            dpg.bind_item_theme("configStatus", red_bg_theme)
            dpg.add_button(label="应用配置", callback=applyConfig, tag="applyConfigButton")
            dpg.add_button(label="停止应用", callback=stopAutoSimulation, tag="stopApplyConfigButton")
        with dpg.child_window(autosize_x=True, autosize_y=True, horizontal_scrollbar=True, tag="pcsConfigWindow"):
            with dpg.table(tag="pcsConfigTable", header_row=True, row_background=False,
                           borders_innerH=True, borders_outerH=True, policy=dpg.mvTable_SizingFixedFit,
                           borders_innerV=True, scrollX=True, scrollY=True, freeze_rows=1,
                           borders_outerV=True, delay_search=True, no_host_extendX=True, resizable=True,
                           width=1800) as pcsConfig_Table:
                dpg.add_table_column(label="id")
                dpg.add_table_column(label="时间偏移量")
                dpg.add_table_column(label="PCS服务开启")
                dpg.add_table_column(label="运行模式")
                dpg.add_table_column(label="电压（V）")
                dpg.add_table_column(label="电流（A）")
                dpg.add_table_column(label="功率（KW）")
                for i in range(0, len(pcs_config_list)):
                    with dpg.table_row():
                        checkbox_id = dpg.add_checkbox(label=str(i), tag="pcs_config_check_box" + str(i))
                        pcs_check_box_list.append(checkbox_id)
                        dpg.highlight_table_cell(pcsConfig_Table, i, 0, (31, 31, 31))
                        dpg.add_text(tag="pcs_config" + str(i * 20 + 1), default_value=pcs_config_list[i].time_offset)
                        dpg.add_text(tag="pcs_config" + str(i * 20 + 2), default_value=pcs_config_list[i].server_status)
                        dpg.add_text(tag="pcs_config" + str(i * 20 + 3), default_value=pcs_config_list[i].run_mode)
                        dpg.add_text(tag="pcs_config" + str(i * 20 + 4), default_value=pcs_config_list[i].voltage)
                        dpg.add_text(tag="pcs_config" + str(i * 20 + 5), default_value=pcs_config_list[i].current)
                        dpg.add_text(tag="pcs_config" + str(i * 20 + 6),
                                     default_value=PcsConfig.power_itoa_map[pcs_config_list[i].power_type] + "：" +
                                                   str(pcs_config_list[i].power))
                dpg.configure_item(pcsConfig_Table, height=500)


def addConfig(time_offset, server_status, run_mode, voltage, current, power_type, power):
    pcs_config = PcsConfig(len(pcs_config_list), time_offset, server_status, "恒功率" if run_mode == 0 else "恒流",
                           voltage, current, PcsConfig.power_atoi_map[power_type], power)

    pcs_config_list.append(pcs_config)
    if not Strategy.check_strategy(pcs_config_list):
        pcs_config_list.pop()
        # 弹窗警告
        with dpg.window(label="警告", modal=True, show=False, no_close=True, tag="warningWindow", pos=[500, 300]):
            dpg.add_text("添加配置失败！")
            log.warning("添加配置失败！")
            dpg.add_button(label="确定", width=100,
                           callback=lambda: dpg.delete_item("warningWindow"))
            dpg.configure_item("warningWindow", show=True)
        return
    dpg.delete_item("addConfigWindow")
    dpg.delete_item("pcsMainWindow")
    initPcsConfig()
    log.info("pcs配置添加成功！")


def updateConfig(pcs_config_id, time_offset, server_status, run_mode, voltage, current, power_type, power):
    id = pcs_config_id
    log.debug("修改的id号为：" + str(id))
    pcs_config_list[id].time_offset = time_offset
    pcs_config_list[id].server_status = server_status
    pcs_config_list[id].run_mode = "恒功率" if run_mode == 0 else "恒流"
    pcs_config_list[id].voltage = voltage
    pcs_config_list[id].current = current
    if power_type == "有功功率":
        pcs_config_list[id].power_type = "0"
    else:
        pcs_config_list[id].power_type = "1"
    pcs_config_list[id].power = power

    dpg.delete_item("updateConfigWindow")
    dpg.delete_item("pcsMainWindow")
    initPcsConfig()
    log.info("pcs配置修改成功！")


def setPcsConfigWindow(pcs_label, window, method):
    global modbusServer
    if modbusServer.simulation_thread is not None and modbusServer.simulation_thread.is_alive():
        # 弹窗警告
        with dpg.window(label="警告", modal=True, show=False, no_close=True, tag="warningWindow", pos=[500, 300]):
            dpg.add_text("请先停止应用配置！")
            log.warning("请先停止应用配置！")
            dpg.add_button(label="确定", width=100,
                           callback=lambda: dpg.delete_item("warningWindow"))
            dpg.configure_item("warningWindow", show=True)
        return
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
            time_offset = dpg.add_input_text(tag="time_offset", indent=start_indent, width=input_width, hint="单位：秒")
            dpg.add_text("PCS服务开启：", indent=text_indent)
            server_status = dpg.add_checkbox(tag="server_status", indent=second_input_indent, default_value=True)
        with dpg.group(horizontal=True):
            dpg.add_text("运行模式：")
            run_mode = dpg.add_input_text(tag="run_mode", indent=start_indent, width=input_width,
                                          hint="0：恒功率；1：恒流")
            dpg.add_text("电压：", indent=text_indent)
            voltage = dpg.add_input_text(tag="voltage", indent=second_input_indent, width=input_width, hint="单位：V")
        with dpg.group(horizontal=True):
            dpg.add_text("电流：")
            current = dpg.add_input_text(tag="current", indent=start_indent, width=input_width, hint="单位：A")
            dpg.add_text("功率：", indent=text_indent)
            power_combo = dpg.add_combo(["有功功率", "无功功率"], default_value="有功功率", tag="power_type",
                                        indent=second_input_indent, width=input_width)
            power_text = dpg.add_input_text(tag="power", width=input_width, hint="单位：KW")

        if method == "update":
            log.debug("pcs配置列表长度：" + str(len(pcs_config_list)))
            log.debug("pcs配置id：" + str(len(pcs_id_list)))
            pcs_config_id = pcs_id_list[0]
            dpg.set_value(time_offset, pcs_config_list[pcs_id_list[-1]].time_offset)
            dpg.set_value(server_status, pcs_config_list[pcs_id_list[-1]].server_status)
            dpg.set_value(run_mode, pcs_config_list[pcs_id_list[-1]].run_mode)
            dpg.set_value(voltage, pcs_config_list[pcs_id_list[-1]].voltage)
            dpg.set_value(current, pcs_config_list[pcs_id_list[-1]].current)
            dpg.set_value(power_combo, PcsConfig.power_itoa_map[pcs_config_list[pcs_id_list[-1]].power_type])
            dpg.set_value(power_text, pcs_config_list[pcs_id_list[-1]].power)

        if method == "add":
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
        else:
            with dpg.group(horizontal=True):
                dpg.add_button(label="确定", width=100,
                               callback=lambda: updateConfig(pcs_config_id,
                                                             dpg.get_value("time_offset"),
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
    if modbusServer.simulation_thread is not None and modbusServer.simulation_thread.is_alive():
        # 弹窗警告
        with dpg.window(label="警告", modal=True, show=False, no_close=True, tag="warningWindow", pos=[500, 300]):
            dpg.add_text("请先停止应用配置！")
            log.warning("请先停止应用配置！")
            dpg.add_button(label="确定", width=100,
                           callback=lambda: dpg.delete_item("warningWindow"))
            dpg.configure_item("warningWindow", show=True)
        return
    with dpg.window(label="删除PCS配置", modal=True, no_close=True, show=False, tag="confirmDeletePcsConfig",
                    pos=[600, 300]):
        def delete_pcs_config_by_id(sender, app_data, user_data):
            for counter, index in enumerate(pcs_id_list):
                index = index - counter
                pcs_config_list.pop(index)
            dpg.delete_item("confirmDeletePcsConfig")
            dpg.delete_item("pcsMainWindow")
            initPcsConfig()
            log.info("删除PCS配置成功！")

        pcs_id_list = get_pcs_id_list()
        dpg.add_text("确认删除PCS配置" + str(pcs_id_list) + "吗？")
        with dpg.group(horizontal=True):
            dpg.add_button(label="确定", width=100,
                           callback=delete_pcs_config_by_id)
            dpg.add_button(label="取消", width=100,
                           callback=lambda: dpg.delete_item("confirmDeletePcsConfig"))
        dpg.configure_item("confirmDeletePcsConfig", show=True)


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

with dpg.theme(tag="series_theme1"):
    with dpg.theme_component(0):
        dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 0, 255, 255), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_Fill, (0, 0, 255, 255), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 10, category=dpg.mvThemeCat_Plots)

with dpg.theme(tag="series_theme2"):
    with dpg.theme_component(0):
        dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 0, 0, 255), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_Fill, (255, 0, 0, 255), category=dpg.mvThemeCat_Plots)

with dpg.theme(tag="series_theme3"):
    with dpg.theme_component(0):
        dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 255, 0, 255), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_Fill, (0, 255, 0, 255), category=dpg.mvThemeCat_Plots)

with dpg.window(tag="Primary Window", width=1500):
    with dpg.tab_bar(tag="tabBar"):
        with dpg.tab(label="主界面"):
            log = my_log.MyCustomLogger()
            dpg.bind_font(default_font)

            # get list of all available IPs and offer to user in a dropdown list
            from netifaces import interfaces, ifaddresses, AF_INET

            ip_list = []
            for interface in interfaces():
                for link in ifaddresses(interface).get(AF_INET, ()):
                    ip_list.append(link['addr'])
            dpg.add_spacer(height=3)
            with dpg.group(horizontal=True):
                dpg.add_text("Modbus/TCP 服务器地址:", tag="serverText")
                dpg.add_combo(ip_list, default_value=ip_list[0], tag="serverAddress", width=250, indent=300)

            dpg.add_spacer(height=3)
            with dpg.group(horizontal=True):
                dpg.add_text("端口号:", tag="serverPortText")
                dpg.add_input_text(default_value="10502", tag="serverPort", width=100, indent=300)

            dpg.add_spacer(height=3)
            with dpg.group(horizontal=True):
                dpg.add_text("设备类型:", tag="deviceTypeText")
                # 设置MODBUS的下拉框选项
                modbus_combo = dpg.add_combo(("Modbus PCS", "Modbus BMS"), default_value="Modbus BMS", tag="modbusType",
                                             width=250,
                                             indent=300)
                on_modbus_type_selected(modbus_combo, None)
                dpg.set_item_callback(modbus_combo, on_modbus_type_selected)

            dpg.add_spacer(height=3)
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
            dpg.add_spacer(height=3)
            with dpg.group(horizontal=True, tag="setDataGroup"):
                # dpg.add_button(label="设置单个电芯值", callback=setCellValues,
                #                tag="setCellValuesButton")
                dpg.add_button(label="随机设置所有电芯值", callback=setRandomCellValues,
                               tag="randomiseAllCellButton")
                dpg.add_button(label="随机设置所有PCS值", callback=setRandomPcsValues,
                               tag="randomiseAllPcsValuesButton")
            dpg.add_spacer(height=3)
            with dpg.group(horizontal=True):
                dpg.add_button(label="自动模拟", callback=autoSimulation, tag="autoSimulationButton")
                dpg.add_button(label="停止模拟", callback=stopAutoSimulation, tag="stopRefreshRegistersButton")

                # 导入CSV文件
                dpg.add_button(label="导入CSV文件", callback=import_csv, tag="importCSVButton")

                # 导出CSV文件
                dpg.add_button(label="导出CSV文件", callback=export_csv, tag="exportCSVButton")
            dpg.add_spacer(height=3)

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

            with dpg.collapsing_header(label="PCS配置", tag="pcsConfig"):
                initPcsConfig()
        # initPcsInfoView(red_bg_theme, green_bg_theme)
        initBatteryStackInfoView(red_bg_theme)
        initBatteryClusterInfoView(red_bg_theme, modbus_server=modbusServer)

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
