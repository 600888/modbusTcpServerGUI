import dearpygui.dearpygui as dpg


# Because the built in logger was made completely from dpg commands you can reimplement it and customize it yourself!
class MyCustomLogger:

    def __init__(self):
        self.log_level = 0
        self._auto_scroll = True
        self.filter_id = None
        self.window_id = dpg.add_window(label="日志", tag="logWindow", pos=(1000, 100), width=500, height=800)
        self.count = 0
        self.flush_count = 1000
        self.level_options = {"all": 0, "Trace": 1, "Debug": 2, "Info": 3, "Warning": 4, "Error": 5, "Critical": 6}

        with dpg.group(horizontal=True, parent=self.window_id):
            dpg.add_checkbox(label="自动滚动", default_value=True,
                             callback=lambda sender: self.auto_scroll(dpg.get_value(sender)))
            dpg.add_button(label="清空", callback=lambda: dpg.delete_item(self.filter_id, children_only=True))
        dpg.add_input_text(label="搜索", callback=lambda sender: dpg.set_value(self.filter_id, dpg.get_value(sender)),
                           parent=self.window_id)
        dpg.add_radio_button(list(self.level_options.keys()), parent=self.window_id,
                             callback=lambda sender: self.set_level(self.level_options[dpg.get_value(sender)]))
        dpg.add_spacer(parent=self.window_id)
        self.child_id = dpg.add_child_window(parent=self.window_id, autosize_x=True, autosize_y=True
                                             , horizontal_scrollbar=True)
        self.filter_id = dpg.add_filter_set(parent=self.child_id)

        with dpg.theme() as self.trace_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 255), category=dpg.mvThemeCat_Core)

        with dpg.theme() as self.debug_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (64, 255, 255), category=dpg.mvThemeCat_Core)

        with dpg.theme() as self.info_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 0), category=dpg.mvThemeCat_Core)

        with dpg.theme() as self.warning_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 165, 0), category=dpg.mvThemeCat_Core)

        with dpg.theme() as self.error_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0), category=dpg.mvThemeCat_Core)

        with dpg.theme() as self.critical_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 255), category=dpg.mvThemeCat_Core)

    def auto_scroll(self, value):
        self._auto_scroll = value

    def _log(self, message, level):

        if level < self.log_level:
            return

        self.count += 1

        if self.count > self.flush_count:
            self.clear()

        theme = self.info_theme

        if level == 0:
            message = "[TRACE] " + str(message)
            theme = self.trace_theme
        elif level == 1:
            message = "[DEBUG] " + str(message)
            theme = self.debug_theme
        elif level == 2:
            message = "[INFO] " + str(message)
            theme = self.info_theme
        elif level == 3:
            message = "[WARNING] " + str(message)
            theme = self.warning_theme
        elif level == 4:
            message = "[ERROR] " + str(message)
            theme = self.error_theme
        elif level == 5:
            message = "[CRITICAL] " + str(message)
            theme = self.critical_theme

        new_log = dpg.add_text(message, parent=self.filter_id, filter_key=message)
        dpg.bind_item_theme(new_log, theme)
        if self._auto_scroll:
            scroll_max = dpg.get_y_scroll_max(self.child_id)
            dpg.set_y_scroll(self.child_id, -1.0)

    def log(self, message):
        self._log(message, 0)

    def debug(self, message):
        self._log(message, 1)

    def info(self, message):
        self._log(message, 2)

    def warning(self, message):
        self._log(message, 3)

    def error(self, message):
        self._log(message, 4)

    def critical(self, message):
        self._log(message, 5)

    def clear(self):
        dpg.delete_item(self.filter_id, children_only=True)
        self.count = 0

    def set_level(self, level):
        # 过滤对应等级的日志
        if level == self.level_options["all"]:
            dpg.set_value(self.filter_id, "")
        else:
            dpg.set_value(self.filter_id, list(self.level_options.keys())[level])
        self.log_level = level
