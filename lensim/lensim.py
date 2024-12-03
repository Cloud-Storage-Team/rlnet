import importlib
import numpy as np
import toml

from heapq import heappop, heappush


class LenSim():
    
    def __init__(self, config_path="./lensim/config/exp_incast100.toml"):
        cfg = toml.load(config_path)
        nic = importlib.import_module(cfg['nic']['module'])
        self.nic_list = [nic.NIC(cfg['nic']) for _ in range(cfg['nic']['count'])]
        host = importlib.import_module(cfg['host']['module'])
        self.host_list = [host.Host(cfg['host']) for _ in range(cfg['host']['count'])]

    def _info(self):
        self.nic_list[0]._info()
        self.host_list[0]._info()

if __name__ == "__main__":
    exp = LenSim()
    exp._info() 