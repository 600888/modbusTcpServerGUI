import random

import dearpygui.dearpygui as dpg

my_modbus_server = None


class StockData:
    def __init__(self):
        self.cluster_id = 0
        self.x = []
        self.max_value = []
        self.min_value = []
        self.average_value = []

    def add(self, x_value, max_value, min_value, average_value):
        self.x.append(x_value)
        self.max_value.append(max_value)
        self.min_value.append(min_value)
        self.average_value.append(average_value)


stock_voltage = []
stock_temperature = []
for i in range(3):
    voltage = StockData()
    voltage.add(0, 0, 0, 0)
    stock_voltage.append(voltage)

    temperature = StockData()
    temperature.add(0, 0, 0, 0)
    stock_temperature.append(temperature)


def refresh_battery_cluster_text(modbus_server):
    cluster_str = dpg.get_value("cluster_combo")
    cluster_id = modbus_server.cluster_atoi_map[cluster_str]
    dpg.configure_item("clusterVoltage",
                       default_value="%.1fV" % (modbus_server.clusterList[cluster_id].getVoltage() * 0.01))
    dpg.configure_item("maxChargeCurrent",
                       default_value="%.1fA" % (random.random() * 100 * 0.01))
    dpg.configure_item("clusterCurrent",
                       default_value="%.1fA" % (modbus_server.clusterList[cluster_id].getCurrent() * 0.01))
    dpg.configure_item("maxDischargeCurrent", default_value="%.1fA" % (random.random() * 100 * 0.01))
    dpg.configure_item("clusterSOC", default_value="%.1f%%" % (modbus_server.clusterList[cluster_id].getSoc() * 0.01))
    dpg.configure_item("averageVoltage",
                       default_value="%.3fV" % (modbus_server.clusterList[cluster_id].getAverageVoltage() * 0.01))
    dpg.configure_item("clusterSOH", default_value="%.1f%%" % (modbus_server.clusterList[cluster_id].getSoc() * 0.01))
    dpg.configure_item("averageTemperature",
                       default_value="%.1f摄氏度" % (modbus_server.clusterList[cluster_id].getTemperature() * 0.01))

    max_voltage_point, min_voltage_point, max_temperature_point, min_temperature_point = modbus_server.clusterList[
        cluster_id].getDataPoint()
    dpg.configure_item("singleClusterMaxVoltage",
                       default_value="%.3fV" % (max_voltage_point.value * 0.01))
    dpg.configure_item("singleClusterMaxVoltageModule",
                       default_value="%d" % max_voltage_point.pack_id)
    dpg.configure_item("singleClusterMaxVoltageCell",
                       default_value="%d" % max_voltage_point.cell_id)

    dpg.configure_item("singleClusterMinVoltage",
                       default_value="%.3fV" % (min_voltage_point.value * 0.01))
    dpg.configure_item("singleClusterMinVoltageModule",
                       default_value="%d" % min_voltage_point.pack_id)
    dpg.configure_item("singleClusterMinVoltageCell",
                       default_value="%d" % min_voltage_point.cell_id)

    dpg.configure_item("singleClusterMaxTemperature",
                       default_value="%.1f摄氏度" % (max_temperature_point.value * 0.01))
    dpg.configure_item("singleClusterMaxTemperatureModule",
                       default_value="%d" % max_temperature_point.pack_id)
    dpg.configure_item("singleClusterMaxTemperatureCell",
                       default_value="%d" % max_temperature_point.cell_id)

    dpg.configure_item("singleClusterMinTemperature",
                       default_value="%.1f摄氏度" % (min_temperature_point.value * 0.01))
    dpg.configure_item("singleClusterMinTemperatureModule",
                       default_value="%d" % min_temperature_point.pack_id)
    dpg.configure_item("singleClusterMinTemperatureCell",
                       default_value="%d" % min_temperature_point.cell_id)

    if modbus_server.simulation_thread is not None and modbus_server.simulation_thread.is_alive():
        for i in range(3):
            stock_voltage[i].x.append(stock_voltage[i].x[-1] + 1)
            stock_voltage[i].max_value.append(max_voltage_point.value * 0.01)
            stock_voltage[i].min_value.append(min_voltage_point.value * 0.01)
            stock_voltage[i].average_value.append(modbus_server.clusterList[i].getAverageVoltage() * 0.01)

            while len(stock_voltage[i].x) > 100:
                stock_voltage[i].x.pop(0)
                stock_voltage[i].max_value.pop(0)
                stock_voltage[i].min_value.pop(0)
                stock_voltage[i].average_value.pop(0)

            stock_temperature[i].x.append(stock_temperature[cluster_id].x[-1] + 1)
            stock_temperature[i].max_value.append(max_temperature_point.value * 0.01)
            stock_temperature[i].min_value.append(min_temperature_point.value * 0.01)
            stock_temperature[i].average_value.append(
                modbus_server.clusterList[i].getTemperature() * 0.01)

            while len(stock_temperature[i].x) > 100:
                stock_temperature[i].x.pop(0)
                stock_temperature[i].max_value.pop(0)
                stock_temperature[i].min_value.pop(0)
                stock_temperature[i].average_value.pop(0)

    dpg.configure_item("cluster_max_voltage_series", x=stock_voltage[cluster_id].x,
                       y=stock_voltage[cluster_id].max_value)
    dpg.configure_item("cluster_min_voltage_series", x=stock_voltage[cluster_id].x,
                       y=stock_voltage[cluster_id].min_value)
    dpg.configure_item("cluster_average_voltage_series", x=stock_voltage[cluster_id].x,
                       y=stock_voltage[cluster_id].average_value)

    dpg.set_axis_limits("cluster_voltage_x_axis", stock_voltage[cluster_id].x[0], stock_voltage[cluster_id].x[-1] + 1)

    dpg.configure_item("cluster_max_temperature_series", x=stock_temperature[cluster_id].x,
                       y=stock_temperature[cluster_id].max_value)
    dpg.configure_item("cluster_min_temperature_series", x=stock_temperature[cluster_id].x,
                       y=stock_temperature[cluster_id].min_value)
    dpg.configure_item("cluster_average_temperature_series", x=stock_temperature[cluster_id].x,
                       y=stock_temperature[cluster_id].average_value)

    dpg.set_axis_limits("cluster_temperature_x_axis", stock_temperature[cluster_id].x[0],
                        stock_temperature[cluster_id].x[-1] + 1)


def set_cluster_combo_callback(sender):
    dpg.set_value(sender, value=dpg.get_value(sender))
    global my_modbus_server
    refresh_battery_cluster_text(my_modbus_server)


def initBatteryClusterInfoView(red_by_theme, modbus_server):
    global my_modbus_server
    my_modbus_server = modbus_server
    with dpg.tab(label="电池簇信息", tag="batteryClusterInfo", parent="tabBar"):
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_text("电池簇：")
            cluster_combo = dpg.add_combo(items=["电池簇1", "电池簇2", "电池簇3"], width=150, default_value="电池簇1",
                                          tag="cluster_combo")
            dpg.set_item_callback(cluster_combo, set_cluster_combo_callback)

        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            with dpg.child_window(width=880, height=220):
                text_indent1 = 20
                input_text_width = 150
                input_text_indent1 = 150
                text_indent2 = 380
                input_text_indent2 = 560
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text("簇总电压：", indent=text_indent1)
                    dpg.add_input_text(default_value="0.0 V", readonly=True, indent=input_text_indent1,
                                       width=input_text_width,
                                       tag="clusterVoltage")
                    dpg.add_text("最大可充电流：", indent=text_indent2)
                    dpg.add_input_text(default_value="0.0 A", readonly=True, indent=input_text_indent2,
                                       width=input_text_width,
                                       tag="maxChargeCurrent")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text("簇总电流：", indent=text_indent1)
                    dpg.add_input_text(default_value="0.0 A", readonly=True, indent=input_text_indent1,
                                       width=input_text_width,
                                       tag="clusterCurrent")
                    dpg.add_text("最大可放电流：", indent=text_indent2)
                    dpg.add_input_text(default_value="0.0 A", readonly=True, indent=input_text_indent2,
                                       width=input_text_width,
                                       tag="maxDischargeCurrent")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text("簇总SOC：", indent=text_indent1)
                    dpg.add_input_text(default_value="0.00 %", readonly=True, indent=input_text_indent1,
                                       width=input_text_width,
                                       tag="clusterSOC")
                    dpg.add_text("单体平均电压：", indent=text_indent2)
                    dpg.add_input_text(default_value="0.0 V", readonly=True, indent=input_text_indent2,
                                       width=input_text_width,
                                       tag="averageVoltage")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text("簇总SOH：", indent=text_indent1)
                    dpg.add_input_text(default_value="0.00 %", readonly=True, indent=input_text_indent1,
                                       width=input_text_width,
                                       tag="clusterSOH")
                    dpg.add_text("单体平均温度：", indent=text_indent2)
                    dpg.add_input_text(default_value="0 摄氏度", readonly=True, indent=input_text_indent2,
                                       width=input_text_width,
                                       tag="averageTemperature")
            with dpg.child_window(width=880, height=220):
                text_indent1 = 10
                input_text_indent1 = 500
                input_text_indent2 = 650
                with dpg.group(horizontal=True):
                    dpg.add_text("位于", indent=400)
                    dpg.add_text("模组号", indent=input_text_indent1)
                    dpg.add_text("电芯号", indent=input_text_indent2)
                with dpg.group(horizontal=True):
                    dpg.add_text("单体最高电压：", indent=text_indent1)
                    dpg.add_input_text(default_value="0.000V", width=150, readonly=True, tag="singleClusterMaxVoltage")
                    dpg.add_input_text(default_value="0", indent=input_text_indent1, width=80, readonly=True,
                                       tag="singleClusterMaxVoltageModule")
                    dpg.add_input_text(default_value="0", indent=input_text_indent2, width=80, readonly=True,
                                       tag="singleClusterMaxVoltageCell")
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text("单体最低电压：", indent=text_indent1)
                    dpg.add_input_text(default_value="0.000V", width=150, readonly=True, tag="singleClusterMinVoltage")
                    dpg.add_input_text(default_value="0", indent=input_text_indent1, width=80, readonly=True,
                                       tag="singleClusterMinVoltageModule")
                    dpg.add_input_text(default_value="0", indent=input_text_indent2, width=80, readonly=True,
                                       tag="singleClusterMinVoltageCell")
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text("单体最高温度：", indent=text_indent1)
                    dpg.add_input_text(default_value="0.0 摄氏度", width=150, readonly=True,
                                       tag="singleClusterMaxTemperature")
                    dpg.add_input_text(default_value="0", indent=input_text_indent1, width=80, readonly=True,
                                       tag="singleClusterMaxTemperatureModule")
                    dpg.add_input_text(default_value="0", indent=input_text_indent2, width=80, readonly=True,
                                       tag="singleClusterMaxTemperatureCell")
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text("单体最低温度：", indent=text_indent1)
                    dpg.add_input_text(default_value="0.0 摄氏度", width=150, readonly=True,
                                       tag="singleClusterMinTemperature")
                    dpg.add_input_text(default_value="0", indent=input_text_indent1, width=80, readonly=True,
                                       tag="singleClusterMinTemperatureModule")
                    dpg.add_input_text(default_value="0", indent=input_text_indent2, width=80, readonly=True,
                                       tag="singleClusterMinTemperatureCell")
        cluster_str = dpg.get_value("cluster_combo")
        cluster_id = modbus_server.cluster_atoi_map[cluster_str]
        with dpg.child_window(autosize_x=True, height=300):
            # 簇内单体电压对比实时曲线
            with dpg.plot(label="簇内单体电压对比曲线", width=-1, height=-1, crosshairs=True,
                          tag="cluster_voltage_plot"):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, tag="cluster_voltage_x_axis")
                with dpg.plot_axis(dpg.mvYAxis):
                    dpg.add_line_series(x=stock_voltage[cluster_id].x, y=stock_voltage[cluster_id].max_value,
                                        label="单体最高电压",
                                        tag="cluster_max_voltage_series")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme1")
                    dpg.add_line_series(x=stock_voltage[cluster_id].x, y=stock_voltage[cluster_id].min_value,
                                        label="单体最低电压",
                                        tag="cluster_min_voltage_series")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme2")
                    dpg.add_line_series(x=stock_voltage[cluster_id].x, y=stock_voltage[cluster_id].average_value,
                                        label="单体平均电压",
                                        tag="cluster_average_voltage_series")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme3")
        with dpg.child_window(autosize_x=True, autosize_y=True):
            # 簇内单体温度对比
            with dpg.plot(label="簇内单体温度对比曲线", width=-1, height=-1, crosshairs=True,
                          tag="cluster_temperature_plot"):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, tag="cluster_temperature_x_axis")
                with dpg.plot_axis(dpg.mvYAxis):
                    dpg.add_line_series(x=stock_temperature[cluster_id].x, y=stock_temperature[cluster_id].max_value,
                                        label="单体最高温度",
                                        tag="cluster_max_temperature_series")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme1")
                    dpg.add_line_series(x=stock_temperature[cluster_id].x, y=stock_temperature[cluster_id].min_value,
                                        label="单体最低温度",
                                        tag="cluster_min_temperature_series")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme2")
                    dpg.add_line_series(x=stock_temperature[cluster_id].x,
                                        y=stock_temperature[cluster_id].average_value, label="单体平均温度",
                                        tag="cluster_average_temperature_series")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme3")
