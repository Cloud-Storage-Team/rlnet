class NIC():
    def __init__(self, cfg):
        self.bandwidth = cfg['bandwidth']
        self.processing_time = cfg['processing_time']
    
    def _info(self):
        print(self.bandwidth)
        print(type(self.bandwidth))
        print(self.processing_time)
        print(type(self.processing_time))
