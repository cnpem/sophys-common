from ophyd import Component
from ophyd.areadetector import DetectorBase, SingleTrigger
from ophyd.areadetector.plugins import ROIStatNPlugin_V25
from ophyd.device import create_device_from_components
from ..utils import HDF5PluginWithFileStoreV34
from .cam import Xspress3DetectorCamV33


class XpressBase(SingleTrigger, DetectorBase):
    pass


def Xpress(prefix: str, roi_num: int = 1, **kwargs):
    xpressComponents = {
        "hdf5": Component(
            HDF5PluginWithFileStoreV34,
            "HDF1:",
            write_path_template="/tmp",
            read_attrs=[]
        ),
        "cam": Component(Xspress3DetectorCamV33, "det1:")
    }
    for num in range(1, roi_num + 1):
        for mca_num in range(1, 5):
            xpressComponents.update({
                f"mca{mca_num}roi_{num}": Component(ROIStatNPlugin_V25, f"MCA{mca_num}ROI:{num}:")
            })

    xpress = create_device_from_components(
        name="xpress", base_class=XpressBase, **xpressComponents)
    return xpress(prefix=prefix, **kwargs)