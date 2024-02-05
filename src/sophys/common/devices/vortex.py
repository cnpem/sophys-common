from ophyd import Component
from ophyd.areadetector import Xspress3Detector, SingleTrigger

from ..utils import HDF5PluginWithFileStore


class Vortex(SingleTrigger, Xspress3Detector):
    hdf5 = Component(
        HDF5PluginWithFileStore,
        "HDF5:",
        write_path_template="/tmp",
        read_attrs=[],
    )

    def __init__(self, *args, write_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hdf5.write_path_template = write_path
