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

class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    pass

class Pilatus(SingleTrigger, PilatusDetector):
    
    image = Component(ImagePlugin, 'image1:')
    cam = Component(PilatusDetectorCam, 'cam1:')

    hdf5 = Component(HDF5PluginWithFileStore, 'HDF1:',
             write_path_template=PATH_TO_WRITE_PILATUS_FILES,
             read_path_template=PATH_TO_WRITE_PILATUS_FILES,
             read_attrs=[],
             root='/')
    
    def __init__(self, *args, write_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hdf5.write_path_template = write_path
        self.hdf5.read_path_template = write_path
        
#     stats1 = Component(StatsPlugin, 'Stats1:')
#     stats2 = Component(StatsPlugin, 'Stats2:')
#     stats3 = Component(StatsPlugin, 'Stats3:')
#     stats4 = Component(StatsPlugin, 'Stats4:')
#     stats5 = Component(StatsPlugin, 'Stats5:')
#     roi1 = Component(ROIPlugin, 'ROI1:')
#     roi2 = Component(ROIPlugin, 'ROI2:')
#     roi3 = Component(ROIPlugin, 'ROI3:')
#     roi4 = Component(ROIPlugin, 'ROI4:')
#     proc1 = Component(ProcessPlugin, 'Proc1:')

class Pilatus6ROIs(Device):
    roi1_rbv = Component(EpicsSignalRO, 'ROIStat1:1:Net_RBV')
    roi2_rbv = Component(EpicsSignalRO, 'ROIStat1:2:Net_RBV')
    roi3_rbv = Component(EpicsSignalRO, 'ROIStat1:3:Net_RBV')
    roi4_rbv = Component(EpicsSignalRO, 'ROIStat1:4:Net_RBV')
    roi5_rbv = Component(EpicsSignalRO, 'ROIStat1:5:Net_RBV')
    roi6_rbv = Component(EpicsSignalRO, 'ROIStat1:6:Net_RBV')

if __name__ == "__main__":
    camera = Pilatus(name="camera", prefix="EMA:B:P300K01:", write_path = '/usr/local/ema_proposals/test_ophyd/', read_attrs=["hdf5"])
    rois = PilatusROIs(name="ROIs", prefix="EMA:B:P300K01:")