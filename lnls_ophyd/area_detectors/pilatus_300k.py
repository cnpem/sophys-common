from ophyd.areadetector import PilatusDetector, PilatusDetectorCam, SingleTrigger
from ophyd.areadetector.plugins import (
    StatsPlugin,
    ImagePlugin,
    ROIPlugin,
    HDF5Plugin,
    ProcessPlugin,
)
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd import Component
from ophyd import Component, Device, EpicsSignal, EpicsSignalRO

PATH_TO_WRITE_PILATUS_FILES = "/usr/local/ema_proposals/test_ophyd/"


class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    pass


class Detector(SingleTrigger, PilatusDetector):
    image = Component(ImagePlugin, "image1:")
    cam = Component(PilatusDetectorCam, "cam1:")
    transform_type = 0
    hdf5 = Component(
        HDF5PluginWithFileStore,
        "HDF1:",
        write_path_template=PATH_TO_WRITE_PILATUS_FILES,
        read_path_template=PATH_TO_WRITE_PILATUS_FILES,
        read_attrs=[],
        root="/",
    )
    stats1 = Component(StatsPlugin, "Stats1:")
    stats2 = Component(StatsPlugin, "Stats2:")
    stats3 = Component(StatsPlugin, "Stats3:")
    stats4 = Component(StatsPlugin, "Stats4:")
    stats5 = Component(StatsPlugin, "Stats5:")
    roi1 = Component(ROIPlugin, "ROI1:")
    roi2 = Component(ROIPlugin, "ROI2:")
    roi3 = Component(ROIPlugin, "ROI3:")
    roi4 = Component(ROIPlugin, "ROI4:")
    proc1 = Component(ProcessPlugin, "Proc1:")


if __name__ == "__main__":
    camera = Detector(name="camera", prefix="EMA:B:P300K01:")
