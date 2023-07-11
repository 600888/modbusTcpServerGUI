import server


class PcsServer(server.ModbusServer):
    def __init__(self):
        super().__init__()