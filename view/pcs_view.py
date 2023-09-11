import dearpygui.dearpygui as dpg


class PcsPowerStockData:
    def __init__(self):
        self.x = []
        self.ac_active_power = []
        self.ac_reactive_power = []

    def add(self, x_value, ac_active_power, ac_reactive_power):
        self.x.append(x_value)
        self.ac_active_power.append(ac_active_power)
        self.ac_reactive_power.append(ac_reactive_power)


class PcsTemperatureStockData:
    def __init__(self):
        self.x = []
        self.module_temperature = []
        self.environment_temperature = []

    def add(self, x_value, module_temperature, environment_temperature):
        self.x.append(x_value)
        self.module_temperature.append(module_temperature)
        self.environment_temperature.append(environment_temperature)


power_stock_data = PcsPowerStockData()
power_stock_data.add(0, 0, 0)
temperature_stock_data = PcsTemperatureStockData()
temperature_stock_data.add(0, 0, 0)


def refresh_pcs_text(modbus_server):
    # dpg.configure_item("pcsStatus", default_value=modbus_server.pcs_status)
    # dpg.configure_item("on-gridStatus", default_value=modbus_server.on_grid_status)
    # dpg.configure_item("deviceStatus", default_value=modbus_server.device_status)
    # dpg.configure_item("controlStatus", default_value=modbus_server.control_status)

    dpg.configure_item("totalAcPower", default_value="%.1fV" % (modbus_server.pcs.totalAcPower * 0.01))
    dpg.configure_item("totalAcReactivePower", default_value="%.1fV" % (modbus_server.pcs.totalAcReactivePower * 0.01))
    dpg.configure_item("totalAcApparentPower", default_value="%.1fV" % (modbus_server.pcs.totalApparentPower * 0.01))
    dpg.configure_item("totalAcApparentPowerFactor",
                       default_value="%.1f" % (modbus_server.pcs.totalPowerFactor * 0.01))

    dpg.configure_item("todayAcCharge", default_value="%.1fKwh" % (modbus_server.pcs.todayAcChargeEnergy * 0.01))
    dpg.configure_item("todayAcDischarge", default_value="%.1fKwh" % (modbus_server.pcs.todayAcDischargeEnergy * 0.01))
    dpg.configure_item("pcsModuleTemperature", default_value="%.1f摄氏度" % (modbus_server.pcs.pcsTemperature * 0.01))
    dpg.configure_item("pcsEnvironmentTemperature",
                       default_value="%.1f摄氏度" % (modbus_server.pcs.environmentTemperature * 0.01))

    dpg.configure_item("aVoltage", default_value="%.1fV" % (modbus_server.pcs.phaseAVoltage * 0.01))
    dpg.configure_item("bVoltage", default_value="%.1fV" % (modbus_server.pcs.phaseBVoltage * 0.01))
    dpg.configure_item("cVoltage", default_value="%.1fV" % (modbus_server.pcs.phaseCVoltage * 0.01))

    dpg.configure_item("aCurrent", default_value="%.1fA" % (modbus_server.pcs.phaseACurrent * 0.01))
    dpg.configure_item("bCurrent", default_value="%.1fA" % (modbus_server.pcs.phaseBCurrent * 0.01))
    dpg.configure_item("cCurrent", default_value="%.1fA" % (modbus_server.pcs.phaseCCurrent * 0.01))

    dpg.configure_item("acFrequency", default_value="%.1fHz" % (modbus_server.pcs.acFrequency * 0.01))

    if modbus_server.simulation_thread is not None and modbus_server.simulation_thread.is_alive():
        power_stock_data.add(power_stock_data.x[-1] + 1,
                             modbus_server.pcs.totalAcPower * 0.01,
                             modbus_server.pcs.totalAcReactivePower * 0.01)
        temperature_stock_data.add(temperature_stock_data.x[-1] + 1,
                                   modbus_server.pcs.pcsTemperature * 0.01,
                                   modbus_server.pcs.environmentTemperature * 0.01)
        while len(power_stock_data.x) > 30:
            power_stock_data.x.pop(0)
            power_stock_data.ac_active_power.pop(0)
            power_stock_data.ac_reactive_power.pop(0)

        while len(temperature_stock_data.x) > 30:
            temperature_stock_data.x.pop(0)
            temperature_stock_data.module_temperature.pop(0)
            temperature_stock_data.environment_temperature.pop(0)

    # print(power_stock_data.x, power_stock_data.ac_active_power, power_stock_data.ac_reactive_power)
    dpg.configure_item("ac_active_power_series", x=power_stock_data.x,
                       y=power_stock_data.ac_active_power)
    dpg.configure_item("ac_reactive_power_series", x=power_stock_data.x,
                       y=power_stock_data.ac_reactive_power)

    dpg.set_axis_limits("power_plot_x_axis", power_stock_data.x[0], power_stock_data.x[-1])

    dpg.configure_item("module_temperature_series", x=temperature_stock_data.x,
                       y=temperature_stock_data.module_temperature)
    dpg.configure_item("environment_temperature_series", x=temperature_stock_data.x,
                       y=temperature_stock_data.environment_temperature)

    dpg.set_axis_limits("temperature_plot_x_axis", temperature_stock_data.x[0], temperature_stock_data.x[-1])


def initPcsInfoView(red_bg_theme, green_bg_theme):
    with dpg.tab(label="PCS信息", tag="pcsInfo", parent="tabBar"):
        dpg.add_spacer(height=10)
        with dpg.group(horizontal=True):
            text_indent1 = 50
            input_text_indent1 = 180
            text_indent2 = 400
            input_text_indent2 = 530
            text_indent3 = 750
            input_text_indent3 = 880
            text_indent4 = 1100
            input_text_indent4 = 1230
            dpg.add_text("工作状态：", indent=text_indent1)
            dpg.add_input_text(default_value="运行", indent=input_text_indent1, width=80, readonly=True,
                               tag="pcsStatus")
            dpg.configure_item("pcsStatus", default_value="停止")
            dpg.bind_item_theme("pcsStatus", red_bg_theme)

            dpg.add_text("并网状态：", indent=text_indent2)
            dpg.add_input_text(default_value="离网", indent=input_text_indent2, width=80, readonly=True,
                               tag="on-gridStatus")
            dpg.configure_item("on-gridStatus", default_value="离网")
            dpg.bind_item_theme("on-gridStatus", red_bg_theme)

            dpg.add_text("设备状态：", indent=text_indent3)
            dpg.add_input_text(default_value="正常", indent=input_text_indent3, width=80, readonly=True,
                               tag="deviceStatus")
            dpg.configure_item("deviceStatus", default_value="正常")
            dpg.bind_item_theme("deviceStatus", green_bg_theme)

            dpg.add_text("控制状态：", indent=text_indent4)
            dpg.add_input_text(default_value="远程", indent=input_text_indent4, width=80, readonly=True,
                               tag="controlStatus")
            dpg.configure_item("controlStatus", default_value="远程")
            dpg.bind_item_theme("controlStatus", green_bg_theme)
        dpg.add_spacer(height=10)
        with dpg.child_window(width=-1, height=235, no_scrollbar=True):
            text_indent1 = 40
            input_text_indent1 = 300
            text_indent2 = 480
            input_text_indent2 = 680
            text_indent3 = 900
            input_text_indent3 = 1030
            text_indent4 = 1230
            input_text_indent4 = 1350
            input_text_width = 150
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_text("总交流有功功率：", indent=text_indent1)
                dpg.add_input_text(default_value="0.0KW", indent=input_text_indent1, width=input_text_width,
                                   readonly=True,
                                   tag="totalAcPower")
                dpg.add_text("当天交流充电量：", indent=text_indent2)
                dpg.add_input_text(default_value="0.0", indent=input_text_indent2, width=input_text_width,
                                   readonly=True,
                                   tag="todayAcCharge")
                dpg.add_text("A相电压：", indent=text_indent3)
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent3, width=input_text_width,
                                   readonly=True,
                                   tag="aVoltage")
                dpg.add_text("A相电流：", indent=text_indent4)
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent4, width=input_text_width,
                                   readonly=True,
                                   tag="aCurrent")
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_text("总交流无功功率：", indent=text_indent1)
                dpg.add_input_text(default_value="0.0KW", indent=input_text_indent1, width=input_text_width,
                                   readonly=True,
                                   tag="totalAcReactivePower")
                dpg.add_text("当天交流放电量：", indent=text_indent2)
                dpg.add_input_text(default_value="0.0", indent=input_text_indent2, width=input_text_width,
                                   readonly=True,
                                   tag="todayAcDischarge")
                dpg.add_text("B相电压：", indent=text_indent3)
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent3, width=input_text_width,
                                   readonly=True,
                                   tag="bVoltage")
                dpg.add_text("B相电流：", indent=text_indent4)
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent4, width=input_text_width,
                                   readonly=True,
                                   tag="bCurrent")
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_text("总交流视在功率：", indent=text_indent1)
                dpg.add_input_text(default_value="0.0KW", indent=input_text_indent1, width=input_text_width,
                                   readonly=True,
                                   tag="totalAcApparentPower")
                dpg.add_text("Pcs模块温度：", indent=text_indent2)
                dpg.add_input_text(default_value="0.0摄氏度", indent=input_text_indent2, width=input_text_width,
                                   readonly=True,
                                   tag="pcsModuleTemperature")
                dpg.add_text("C相电压：", indent=text_indent3)
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent3, width=input_text_width,
                                   readonly=True,
                                   tag="cVoltage")
                dpg.add_text("C相电流：", indent=text_indent4)
                dpg.add_input_text(default_value="0.0V", indent=input_text_indent4, width=input_text_width,
                                   readonly=True,
                                   tag="cCurrent")
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_text("总交流视在功率因数：", indent=text_indent1)
                dpg.add_input_text(default_value="0.0", indent=input_text_indent1, width=input_text_width,
                                   readonly=True,
                                   tag="totalAcApparentPowerFactor")
                dpg.add_text("Pcs环境温度：", indent=text_indent2)
                dpg.add_input_text(default_value="0.0摄氏度", indent=input_text_indent2, width=input_text_width,
                                   readonly=True,
                                   tag="pcsEnvironmentTemperature")
                dpg.add_text("交流频率：", indent=text_indent3)
                dpg.add_input_text(default_value="0.0Hz", indent=input_text_indent3, width=input_text_width,
                                   readonly=True,
                                   tag="acFrequency")
        with dpg.child_window(width=-1, height=-1, no_scrollbar=True):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=880, height=-1):
                    with dpg.plot(label="30分钟功率曲线", width=-1, height=-1, crosshairs=True,
                                  tag="30min_power_plot"):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, tag="power_plot_x_axis")
                        with dpg.plot_axis(dpg.mvYAxis):
                            dpg.add_line_series(x=power_stock_data.x, y=power_stock_data.ac_active_power,
                                                label="有功功率", tag="ac_active_power_series")
                            dpg.bind_item_theme(dpg.last_item(), "series_theme1")
                            dpg.add_line_series(x=power_stock_data.x, y=power_stock_data.ac_reactive_power,
                                                label="无功功率", tag="ac_reactive_power_series")
                            dpg.bind_item_theme(dpg.last_item(), "series_theme2")
                with dpg.child_window(width=-1, height=-1):
                    with dpg.plot(label="30分钟温度曲线", width=-1, height=-1, crosshairs=True,
                                  tag="30min_temperature_plot"):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, tag="temperature_plot_x_axis")
                        with dpg.plot_axis(dpg.mvYAxis):
                            dpg.add_line_series(x=temperature_stock_data.x,
                                                y=temperature_stock_data.module_temperature,
                                                label="模块温度", tag="module_temperature_series")
                            dpg.bind_item_theme(dpg.last_item(), "series_theme1")
                            dpg.add_line_series(x=temperature_stock_data.x,
                                                y=temperature_stock_data.environment_temperature,
                                                label="环境温度", tag="environment_temperature_series")
                            dpg.bind_item_theme(dpg.last_item(), "series_theme2")
