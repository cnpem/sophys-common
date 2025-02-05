from ophyd import Component
from ophyd.areadetector import DetectorBase, SingleTrigger
from ..utils import HDF5PluginWithFileStore
from .cam import Xspress3DetectorCamV33


class Xpress(SingleTrigger, DetectorBase):
    hdf5 = Component(
        HDF5PluginWithFileStore,
        "HDF5:",
        write_path_template="/tmp",
        read_attrs=[],
    )

    cam = Component(Xspress3DetectorCamV33, "det1:")

    def __init__(self, *args, write_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hdf5.write_path_template = write_path
