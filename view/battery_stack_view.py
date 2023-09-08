import random

import dearpygui.dearpygui as dpg

stock_datax = []
stock_datay = []
stock_data1 = []
stock_data2 = []
stock_data3 = []


def refresh_battery_text(modbus_server):
    dpg.configure_item("systemVoltage", default_value="%.1fV" % (modbus_server.getTotalSystemVoltage() * 0.01))
    dpg.configure_item("systemCurrent", default_value="%.1fA" % (modbus_server.getTotalSystemCurrent() * 0.01))
    dpg.configure_item("systemSOC", default_value="%.2f%%" % (modbus_server.getSystemSoc() * 0.01))
    dpg.configure_item("systemSOH", default_value="%.2f%%" % (modbus_server.getSystemSoc() * 0.01))
    dpg.configure_item("chargeableCapacity", default_value="%.1fkWh" % (random.random() * 100))
    dpg.configure_item("dischargeableCapacity", default_value="%.1fkWh" % (random.random() * 100))
    dpg.configure_item("maxChargeableCurrent", default_value="%.1fA" % (random.random() * 100.0))
    dpg.configure_item("maxDischargeableCurrent", default_value="%.1fA" % (random.random() * 100.0))
    dpg.configure_item("clusterCurrentDifference",
                       default_value="%.1fA" % (modbus_server.getCurrentDifference() * 0.01))
    dpg.configure_item("clusterVoltageDifference",
                       default_value="%.1fV" % (modbus_server.getVoltageDifference() * 0.01))
    dpg.configure_item("singleVoltageAverage", default_value="%.3fV" % (modbus_server.getAverageVoltage() * 0.01))
    dpg.configure_item("singleTemperatureAverage",
                       default_value="%.1f摄氏度" % (modbus_server.getAverageTemperature() * 0.01))

    max_volatage_point, min_voltage_point, max_temperature_point, min_temperature_point = modbus_server.getDataPoint()

    dpg.configure_item("singleMaxVoltage", default_value="%.3fV" % (max_volatage_point.value * 0.01))
    dpg.configure_item("singleMaxVoltageCluster", default_value="%d" % max_volatage_point.cluster_id)
    dpg.configure_item("singleMaxVoltageModule", default_value="%d" % max_volatage_point.pack_id)
    dpg.configure_item("singleMaxVoltageCell", default_value="%d" % max_volatage_point.cell_id)

    dpg.configure_item("singleMinVoltage", default_value="%.3fV" % (min_voltage_point.value * 0.01))
    dpg.configure_item("singleMinVoltageCluster", default_value="%d" % min_voltage_point.cluster_id)
    dpg.configure_item("singleMinVoltageModule", default_value="%d" % min_voltage_point.pack_id)
    dpg.configure_item("singleMinVoltageCell", default_value="%d" % min_voltage_point.cell_id)

    dpg.configure_item("singleMaxTemperature", default_value="%.1f摄氏度" % (max_temperature_point.value * 0.01))
    dpg.configure_item("singleMaxTemperatureCluster", default_value="%d" % max_temperature_point.cluster_id)
    dpg.configure_item("singleMaxTemperatureModule", default_value="%d" % max_temperature_point.pack_id)
    dpg.configure_item("singleMaxTemperatureCell", default_value="%d" % max_temperature_point.cell_id)

    dpg.configure_item("singleMinTemperature", default_value="%.1f摄氏度" % (min_temperature_point.value * 0.01))
    dpg.configure_item("singleMinTemperatureCluster", default_value="%d" % min_temperature_point.cluster_id)
    dpg.configure_item("singleMinTemperatureModule", default_value="%d" % min_temperature_point.pack_id)
    dpg.configure_item("singleMinTemperatureCell", default_value="%d" % min_temperature_point.cell_id)

    stock_datax.append(stock_datax[-1] + 1)
    stock_data1.append(int(modbus_server.getTotalSystemVoltage() * 0.01))
    stock_data2.append(int(modbus_server.getTotalSystemCurrent() * 0.01))
    stock_data3.append(int(modbus_server.getSystemSoc() * 0.01))

    while len(stock_datax) > 100:
        stock_datax.pop(0)
        stock_data1.pop(0)
        stock_data2.pop(0)
        stock_data3.pop(0)

    # 向曲线里动态添加数据
    dpg.configure_item("series1", x=stock_datax, y=stock_data1)
    dpg.configure_item("series2", x=stock_datax, y=stock_data2)
    dpg.configure_item("series3", x=stock_datax, y=stock_data3)

    dpg.set_axis_limits("x_axis", stock_datax[0], stock_datax[-1] + 1)


def refresh_plot():
    print("refresh_plot")
    pass


def initBatteryStackInfoView(red_bg_theme):
    with dpg.tab(label="电池堆信息", tag="batteryStackInfo", parent="tabBar"):
        dpg.add_spacer(height=3)
        with dpg.group(horizontal=True):
            dpg.add_text("状态标志：")
            dpg.add_input_text(default_value="运行", width=80, readonly=True, tag="batteryStatus")
            dpg.configure_item("batteryStatus", default_value="停止")
            dpg.bind_item_theme("batteryStatus", red_bg_theme)
        dpg.add_spacer(height=3)
        dpg.add_separator()
        dpg.add_text("电池堆信息")
        input_text_indent = 180
        text_indent = 380
        input_text_indent1 = 560
        text_indent1 = 750
        input_text_indent2 = 930
        text_indent2 = 1100
        input_text_indent3 = 1280
        with dpg.child_window(autosize_x=True, height=330):
            input_text_width = 150
            with dpg.group(horizontal=True):
                dpg.add_text("系统总电压：")
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent, width=input_text_width,
                                   readonly=True, tag="systemVoltage")
                dpg.add_text("系统总电流：", indent=text_indent)
                dpg.add_input_text(default_value="0.0A", indent=input_text_indent1, width=input_text_width,
                                   readonly=True, tag="systemCurrent")
                dpg.add_text("系统SOC：", indent=text_indent1)
                dpg.add_input_text(default_value="0.0%", indent=input_text_indent2, width=input_text_width,
                                   readonly=True, tag="systemSOC")
                dpg.add_text("系统SOH：", indent=text_indent2)
                dpg.add_input_text(default_value="0.0%", indent=input_text_indent3, width=input_text_width,
                                   readonly=True, tag="systemSOH")
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("可充电量：")
                dpg.add_input_text(default_value="0.0kWh", indent=input_text_indent, width=input_text_width,
                                   readonly=True, tag="chargeableCapacity")
                dpg.add_text("可放电量：", indent=text_indent)
                dpg.add_input_text(default_value="0.0kWh", indent=input_text_indent1, width=input_text_width,
                                   readonly=True, tag="dischargeableCapacity")
                dpg.add_text("最大可充电流：", indent=text_indent1)
                dpg.add_input_text(default_value="0.0A", indent=input_text_indent2, width=input_text_width,
                                   readonly=True, tag="maxChargeableCurrent")
                dpg.add_text("最大可放电流：", indent=text_indent2)
                dpg.add_input_text(default_value="0.0A", indent=input_text_indent3, width=input_text_width,
                                   readonly=True, tag="maxDischargeableCurrent")
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("簇间电流差异：")
                dpg.add_input_text(default_value="0.0A", indent=input_text_indent, width=input_text_width,
                                   readonly=True, tag="clusterCurrentDifference")
                dpg.add_text("簇间电压差异：", indent=text_indent)
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent1, width=input_text_width,
                                   readonly=True, tag="clusterVoltageDifference")
                dpg.add_text("单体平均电压：", indent=text_indent1)
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent2, width=input_text_width,
                                   readonly=True, tag="singleVoltageAverage")
                dpg.add_text("单体平均温度：", indent=text_indent2)
                dpg.add_input_text(default_value="0.0摄氏度", indent=input_text_indent3, width=input_text_width,
                                   readonly=True, tag="singleTemperatureAverage")
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("位于", indent=360)
                dpg.add_text("簇号", indent=450)
                dpg.add_text("模组号", indent=600)
                dpg.add_text("电芯号", indent=750)
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("单体最高电压：")
                dpg.add_input_text(default_value="0.0V", width=150, readonly=True, tag="singleMaxVoltage")
                dpg.add_input_text(default_value="0", indent=450, width=80, readonly=True,
                                   tag="singleMaxVoltageCluster")
                dpg.add_input_text(default_value="0", indent=600, width=80, readonly=True, tag="singleMaxVoltageModule")
                dpg.add_input_text(default_value="0", indent=750, width=80, readonly=True, tag="singleMaxVoltageCell")
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("单体最低电压：")
                dpg.add_input_text(default_value="0.0V", width=150, readonly=True, tag="singleMinVoltage")
                dpg.add_input_text(default_value="0", indent=450, width=80, readonly=True,
                                   tag="singleMinVoltageCluster")
                dpg.add_input_text(default_value="0", indent=600, width=80, readonly=True, tag="singleMinVoltageModule")
                dpg.add_input_text(default_value="0", indent=750, width=80, readonly=True, tag="singleMinVoltageCell")
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("单体最高温度：")
                dpg.add_input_text(default_value="0.0摄氏度", width=150, readonly=True, tag="singleMaxTemperature")
                dpg.add_input_text(default_value="0", indent=450, width=80, readonly=True,
                                   tag="singleMaxTemperatureCluster")
                dpg.add_input_text(default_value="0", indent=600, width=80, readonly=True,
                                   tag="singleMaxTemperatureModule")
                dpg.add_input_text(default_value="0", indent=750, width=80, readonly=True,
                                   tag="singleMaxTemperatureCell")
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("单体最低温度：")
                dpg.add_input_text(default_value="0.0摄氏度", width=150, readonly=True, tag="singleMinTemperature")
                dpg.add_input_text(default_value="0", indent=450, width=80, readonly=True,
                                   tag="singleMinTemperatureCluster")
                dpg.add_input_text(default_value="0", indent=600, width=80, readonly=True,
                                   tag="singleMinTemperatureModule")
                dpg.add_input_text(default_value="0", indent=750, width=80, readonly=True,
                                   tag="singleMinTemperatureCell")
        with dpg.child_window(autosize_x=True, autosize_y=True):
            stock_datax.append(0)
            stock_data1.append(0)
            stock_data2.append(0)
            stock_data3.append(0)
            # 30分钟总电压、总电流、SOC实时曲线
            with dpg.plot(label="30分钟总电压、总电流、SOC实时曲线", width=-1, height=-1, crosshairs=True,
                          anti_aliased=True, use_24hour_clock=True, tag="my_plot"):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, tag="x_axis")
                with dpg.plot_axis(dpg.mvYAxis):
                    dpg.add_line_series(x=stock_datax, y=stock_data1, label="总电压", tag="series1",
                                        parent="30分钟总电压、总电流、SOC实时曲线")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme1")
                    dpg.add_line_series(x=stock_datax, y=stock_data2, label="总电流", tag="series2",
                                        parent="30分钟总电压、总电流、SOC实时曲线")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme2")
                    dpg.add_line_series(x=stock_datax, y=stock_data3, label="SOC", tag="series3",
                                        parent="30分钟总电压、总电流、SOC实时曲线")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme3")
                    dpg.set_axis_limits_auto("x_axis")
