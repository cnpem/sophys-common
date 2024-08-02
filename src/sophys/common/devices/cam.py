from ophyd.areadetector.cam import CamBase, Xspress3DetectorCam


class CamBase_V33(CamBase):
    pool_max_buffers = None

class Xspress3DetectorCamV33(Xspress3DetectorCam):
    pool_max_buffers = None