from ophyd import Component, Device, EpicsSignalRO
from ophyd.areadetector import PilatusDetector, SingleTrigger
from ophyd.areadetector.plugins import (
    ImagePlugin,
    ProcessPlugin,
)

from ..utils import HDF5PluginWithFileStore


class PilatusWithoutHDF5(SingleTrigger, PilatusDetector):
    image = Component(ImagePlugin, "image1:")
    proc1 = Component(ProcessPlugin, "Proc1:")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Pilatus(PilatusWithoutHDF5):
    hdf5 = Component(
        HDF5PluginWithFileStore,
        "HDF1:",
        write_path_template="/tmp",
        read_attrs=[],
    )

    def __init__(self, *args, write_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hdf5.write_path_template = write_path


class Pilatus6ROIs(Device):
    roi1_rbv = Component(EpicsSignalRO, "ROIStat1:1:Net_RBV")
    roi2_rbv = Component(EpicsSignalRO, "ROIStat1:2:Net_RBV")
    roi3_rbv = Component(EpicsSignalRO, "ROIStat1:3:Net_RBV")
    roi4_rbv = Component(EpicsSignalRO, "ROIStat1:4:Net_RBV")
    roi5_rbv = Component(EpicsSignalRO, "ROIStat1:5:Net_RBV")
    roi6_rbv = Component(EpicsSignalRO, "ROIStat1:6:Net_RBV")
    hints = {"fields": []}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hints["fields"] = [self.name + "_roi1_rbv"]
