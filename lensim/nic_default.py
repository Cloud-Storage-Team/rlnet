class NIC:
    def __init__(self, ptr, cfg):
        self.ptr = ptr
        self.bandwidth = cfg["bandwidth"]
        self.processing_time = cfg["processing_time"]

    def process_event(self, event):
        pass

    def _info(self):
        print(self.ptr)
        print(self.bandwidth)
        print(type(self.bandwidth))
        print(self.processing_time)
        print(type(self.processing_time))
