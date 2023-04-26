from ophyd.areadetector import Xspress3Detector, Xspress3DetectorCam, SingleTrigger
from ophyd.areadetector.plugins import (
    StatsPlugin,
    ImagePlugin,
    ROIPlugin,
    HDF5Plugin,
    ProcessPlugin,
)
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd import Component, Device, EpicsSignal, EpicsSignalRO


class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    pass


class Vortex(SingleTrigger, Xspress3Detector):

    cam = Component(Xspress3DetectorCam, "")
    hdf5 = Component(
        HDF5PluginWithFileStore,
        "HDF5:",
        write_path_template="/tmp",
        read_attrs=[],
        # root="/usr/local/ema_proposals/",
    )

    def __init__(self, *args, write_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hdf5.write_path_template = write_path

# class Pilatus6ROIs(Device):
#     roi1_rbv = Component(EpicsSignalRO, "ROIStat1:1:Net_RBV")
#     roi2_rbv = Component(EpicsSignalRO, "ROIStat1:2:Net_RBV")
#     roi3_rbv = Component(EpicsSignalRO, "ROIStat1:3:Net_RBV")
#     roi4_rbv = Component(EpicsSignalRO, "ROIStat1:4:Net_RBV")
#     roi5_rbv = Component(EpicsSignalRO, "ROIStat1:5:Net_RBV")
#     roi6_rbv = Component(EpicsSignalRO, "ROIStat1:6:Net_RBV")
#     hints = {"fields": []}

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.hints["fields"] = [self.name + "_roi1_rbv"]


if __name__ == "__main__":
    pilatus300k = Vortex(
        name="Vortex",
        prefix="EMA:B:VORTEX01:",
        write_path="test_ophyd",
        read_attrs=["hdf5"],
    )
    # rois_pilatus300k = Pilatus6ROIs(name="rois_pilatus300k", prefix="EMA:B:P300K01:")
