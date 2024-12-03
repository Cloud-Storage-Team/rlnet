import numpy as np

class Host():
    def __init__(self, cfg):
        self.bandwidth = cfg['bandwidth']
        self.processing_time = cfg['processing_time']
        self.lifetime = cfg['lifetime']
        self.packet_size = cfg['packet_size']
    
    def _info(self):
        print(self.bandwidth)
        print(type(self.bandwidth))
        print(self.processing_time)
        print(type(self.processing_time))
        print(self.lifetime)
        print(type(self.lifetime))
        print(self.packet_size)
        print(type(self.packet_size))