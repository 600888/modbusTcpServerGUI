import random
import time

import dearpygui.dearpygui as dpg
from device.modbus_server import ModbusPcsServerGUI, ModbusBmsServerGUI


def initBatteryStackInfoView():
    with dpg.tab(label="电池堆信息", tag="batteryStackInfo", parent="tabBar"):
        with dpg.group(horizontal=True):
            dpg.add_text("状态标志：")
            dpg.add_input_text(default_value="运行", width=80, readonly=True)
        dpg.add_separator()
        dpg.add_text("电池堆信息")
        with dpg.child_window(autosize_x=True, height=330):
            input_text_width = 150
            with dpg.group(horizontal=True):
                dpg.add_text("系统总电压：")
                dpg.add_input_text(default_value="0.0V", width=input_text_width, readonly=True)
                dpg.add_text("系统总电流：")
                dpg.add_input_text(default_value="0.0A", width=input_text_width, readonly=True)
                dpg.add_text("系统SOC：")
                dpg.add_input_text(default_value="0.0%", width=input_text_width, readonly=True)
                dpg.add_text("系统SOH：")
                dpg.add_input_text(default_value="0.0%", width=input_text_width, readonly=True)
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("可充电量：")
                dpg.add_input_text(default_value="0.0kWh", width=input_text_width, readonly=True)
                dpg.add_text("可放电量：")
                dpg.add_input_text(default_value="0.0kWh", width=input_text_width, readonly=True)
                dpg.add_text("最大可充电流：")
                dpg.add_input_text(default_value="0.0A", width=input_text_width, readonly=True)
                dpg.add_text("最大可放电流：")
                dpg.add_input_text(default_value="0.0A", width=input_text_width, readonly=True)
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("簇间电流差异：")
                dpg.add_input_text(default_value="0.0A", width=input_text_width, readonly=True)
                dpg.add_text("簇间电压差异：")
                dpg.add_input_text(default_value="0.0V", width=input_text_width, readonly=True)
                dpg.add_text("单体平均电压：")
                dpg.add_input_text(default_value="0.0V", width=input_text_width, readonly=True)
                dpg.add_text("单体平均温度：")
                dpg.add_input_text(default_value="0.0摄氏度", width=input_text_width, readonly=True)
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("位于", indent=350)
                dpg.add_text("簇号", indent=450)
                dpg.add_text("模组号", indent=600)
                dpg.add_text("电芯号", indent=750)
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("单体最高电压：")
                dpg.add_input_text(default_value="0.0V", width=150, readonly=True)
                dpg.add_input_text(default_value="0", indent=450, width=80, readonly=True)
                dpg.add_input_text(default_value="0", indent=600, width=80, readonly=True)
                dpg.add_input_text(default_value="0", indent=750, width=80, readonly=True)
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("单体最低电压：")
                dpg.add_input_text(default_value="0.0V", width=150, readonly=True)
                dpg.add_input_text(default_value="0", indent=450, width=80, readonly=True)
                dpg.add_input_text(default_value="0", indent=600, width=80, readonly=True)
                dpg.add_input_text(default_value="0", indent=750, width=80, readonly=True)
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("单体最高温度：")
                dpg.add_input_text(default_value="0.0摄氏度", width=150, readonly=True)
                dpg.add_input_text(default_value="0", indent=450, width=80, readonly=True)
                dpg.add_input_text(default_value="0", indent=600, width=80, readonly=True)
                dpg.add_input_text(default_value="0", indent=750, width=80, readonly=True)
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_text("单体最低温度：")
                dpg.add_input_text(default_value="0.0摄氏度", width=150, readonly=True)
                dpg.add_input_text(default_value="0", indent=450, width=80, readonly=True)
                dpg.add_input_text(default_value="0", indent=600, width=80, readonly=True)
                dpg.add_input_text(default_value="0", indent=750, width=80, readonly=True)
        with dpg.child_window(autosize_x=True, autosize_y=True):
            with dpg.theme(tag="series_theme1"):
                with dpg.theme_component(0):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 0, 255), category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_color(dpg.mvPlotCol_Fill, (0, 0, 255, 64), category=dpg.mvThemeCat_Plots)

            with dpg.theme(tag="series_theme2"):
                with dpg.theme_component(0):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_color(dpg.mvPlotCol_Fill, (255, 0, 0, 64), category=dpg.mvThemeCat_Plots)

            with dpg.theme(tag="series_theme3"):
                with dpg.theme_component(0):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 255, 0), category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_color(dpg.mvPlotCol_Fill, (0, 255, 0, 64), category=dpg.mvThemeCat_Plots)

            stock_datax = []
            stock_datay = []
            stock_data1 = []
            stock_data2 = []
            stock_data3 = []
            for i in range(100):
                stock_datax.append(i)
                stock_datay.append(i)
                stock_datay.append(0)
                stock_data1.append(400 + 50 * abs(random.random()))
                stock_data2.append(275 + 75 * abs(random.random()))
                stock_data3.append(150 + 75 * abs(random.random()))
            # 30分钟总电压、总电流、SOC实时曲线
            with dpg.plot(label="30分钟总电压、总电流、SOC实时曲线", width=-1, height=-1, crosshairs=True,tag="my_plot"):
                dpg.add_plot_legend()
                xaxis = dpg.add_plot_axis(dpg.mvXAxis)
                dpg.set_axis_limits(xaxis, ymin=0, ymax=120)
                with dpg.plot_axis(dpg.mvYAxis):
                    dpg.add_line_series(x=stock_datax, y=stock_data1, label="总电压",
                                        parent="30分钟总电压、总电流、SOC实时曲线")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme1")
                    dpg.add_line_series(x=stock_datax, y=stock_data2, label="总电流",
                                        parent="30分钟总电压、总电流、SOC实时曲线")
                    dpg.bind_item_theme(dpg.last_item(), "series_theme2")
                    dpg.add_line_series(x=stock_datax, y=stock_data3, label="SOC",
                                        parent="30分钟总电压、总电流、SOC实时曲线")
                # dpg.add_line_series(x=[0, 1, 2, 3, 4, 5], y=[0, 1, 2, 3, 4, 5], label="总电流",
                #                     parent="30分钟总电压、总电流、SOC实时曲线")
                # dpg.add_line_series(x=[0, 1, 2, 3, 4, 5], y=[0, 1, 2, 3, 4, 5], label="SOC",
                #                     parent="30分钟总电压、总电流、SOC实时曲线")
