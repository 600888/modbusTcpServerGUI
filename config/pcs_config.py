from dataclasses import dataclass


class Strategy:
    pcs_config_list = []

    def set_pcs_config(self, pcs_config_list):
        self.pcs_config_list = pcs_config_list

    def get_pcs_config(self):
        return self.pcs_config_list

    # 检查策略是否正确
    @staticmethod
    def check_strategy(pcs_config_list):
        return True
        # 如果后面的时间偏移量比前面的时间偏移量小，返回False
        for i in range(len(pcs_config_list) - 1):
            if int(pcs_config_list[i].time_offset) > int(pcs_config_list[i + 1].time_offset):
                return False


class PcsConfig:
    id = 0
    time_offset = 0
    server_status = 0
    run_mode = 0
    voltage = 0
    current = 0
    power_type = 0
    power = 0
    power_map = {"0": "有功功率", "1": "无功功率"}

    def __init__(self, id, time_offset, server_status, run_mode, voltage, current, power_type, power):
        self.id = id
        self.time_offset = time_offset if time_offset is not None else 0
        self.server_status = server_status
        self.run_mode = run_mode if run_mode is not None else 0
        self.voltage = voltage if voltage is not None else 0
        self.current = current if current is not None else 0
        self.power_type = "0" if power_type == "有功功率" else "1"
        self.power = power if power is not None else 0

    def __dict__(self):
        return {
            "id": self.id,
            "偏移量": self.time_offset,
            "pcs服务开启": self.server_status,
            "运行模式": self.run_mode,
            "电压": self.voltage,
            "电流": self.current,
            "功率": {
                "类型": self.power_type,
                "值": self.power
            },
        }
