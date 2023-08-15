from dataclasses import dataclass


@dataclass
class Cluster:
    cluster_id = 0
    PackList = []
    pass


@dataclass
class Pack:
    pack_id = 0
    CellList = []
    pass


@dataclass
class Cell:
    cell_id = 0
    voltage = 0
    temperature = 0
    soc = 0
    vol_address = 0
    temperature_address = 0

    def setValue(self, cell_id, voltage, temperature, vol_address, temperature_address, soc=0):
        self.cell_id = cell_id
        self.voltage = voltage
        self.temperature = temperature
        self.vol_address = vol_address
        self.temperature_address = temperature_address
        self.soc = soc
