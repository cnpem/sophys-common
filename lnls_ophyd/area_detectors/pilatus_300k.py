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
    proc1 = Component(ProcessPlugin, 'Proc1:')
    hdf5 = Component(HDF5PluginWithFileStore, 'HDF1:',
             write_path_template="/tmp",
             read_attrs=[],
             root='/usr/local/ema_proposals/')
    
    def __init__(self, *args, write_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hdf5.write_path_template = write_path

    # def stage(self):
    #     status = super().stage()
    #     self.wait_for_plugins = 0
    #     return status
        
#     stats1 = Component(StatsPlugin, 'Stats1:')
#     stats2 = Component(StatsPlugin, 'Stats2:')
#     stats3 = Component(StatsPlugin, 'Stats3:')
#     stats4 = Component(StatsPlugin, 'Stats4:')
#     stats5 = Component(StatsPlugin, 'Stats5:')
#     roi1 = Component(ROIPlugin, 'ROI1:')
#     roi2 = Component(ROIPlugin, 'ROI2:')
#     roi3 = Component(ROIPlugin, 'ROI3:')
#     roi4 = Component(ROIPlugin, 'ROI4:')

class Pilatus6ROIs(Device):
    roi1_rbv = Component(EpicsSignalRO, 'ROIStat1:1:Net_RBV')
    roi2_rbv = Component(EpicsSignalRO, 'ROIStat1:2:Net_RBV')
    roi3_rbv = Component(EpicsSignalRO, 'ROIStat1:3:Net_RBV')
    roi4_rbv = Component(EpicsSignalRO, 'ROIStat1:4:Net_RBV')
    roi5_rbv = Component(EpicsSignalRO, 'ROIStat1:5:Net_RBV')
    roi6_rbv = Component(EpicsSignalRO, 'ROIStat1:6:Net_RBV')

if __name__ == "__main__":
    pilatus300k = Pilatus(name="pilatus300k", prefix="EMA:B:P300K01:", write_path='test_ophyd', read_attrs=["hdf5"])
    rois_pilatus300k = Pilatus6ROIs(name="rois_pilatus300k", prefix="EMA:B:P300K01:")