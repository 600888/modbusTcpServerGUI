import threading


class SimulationThread:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def is_alive(self):
        if self.thread is not None:
            return self.thread.is_alive()
        else:
            return False

    def set_thread(self, thread):
        self.thread = thread

    def start(self):
        self.thread.start()

    def stopAutoSimulation(self, sender, app_data, user_data, dpg, red_bg_theme):
        if self.thread is not None and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join()
            dpg.configure_item("configStatus", default_value="停止")
            dpg.bind_item_theme("configStatus", red_bg_theme)
            dpg.configure_item("batteryStatus", default_value="停止")
            dpg.bind_item_theme("batteryStatus", red_bg_theme)
