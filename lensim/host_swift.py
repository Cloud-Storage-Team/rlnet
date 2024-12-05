import numpy as np


class Host:
    def __init__(self, ptr, cfg):
        self.ptr = ptr
        self.bandwidth = cfg["bandwidth"]
        self.processing_time = cfg["processing_time"]
        self.lifetime = cfg["lifetime"]
        self.packet_size = cfg["packet_size"]
        self.cwnd = cfg["initial_cwnd"]
        self.inflight = 0

    def process_event(self, event):
        pass

    def _info(self):
        print(self.ptr)
        print(self.bandwidth)
        print(type(self.bandwidth))
        print(self.processing_time)
        print(type(self.processing_time))
        print(self.lifetime)
        print(type(self.lifetime))
        print(self.packet_size)
        print(type(self.packet_size))
