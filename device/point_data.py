class Yc:
    def __init__(self, address, func_code, name, code, value, mul_coe, add_coe, frame_type):
        self.address = address  # 测点地址
        self.func_code = func_code  # 功能码
        self.name = name  # 测名称
        self.code = code  # 测点编码
        self.value = value  # 测点值
        self.mul_coe = mul_coe  # 测点值乘积系数
        self.add_coe = add_coe  # 测点值加法系数
        self.frame_type = frame_type  # 帧类型


class Yx:
    def __init__(self, address, func_code, name, code, value, frame_type):
        self.address = address  # 测点地址
        self.func_code = func_code  # 功能码
        self.name = name  # 测名称
        self.code = code  # 测点编码
        self.value = value  # 测点值
        self.frame_type = frame_type  # 帧类型
