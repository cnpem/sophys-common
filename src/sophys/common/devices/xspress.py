from ophyd import Component
from ophyd.areadetector import DetectorBase, SingleTrigger
from ophyd.areadetector.plugins import ROIStatNPlugin_V25
from ophyd.device import create_device_from_components
from ..utils import HDF5PluginWithFileStoreV34
from .cam import Xspress3DetectorCamV33


class XspressBase(SingleTrigger, DetectorBase):
    pass


def Xspress(prefix: str, rois_per_mca: int = 1, **kwargs):
    xspressComponents = {
        "hdf5": Component(HDF5PluginWithFileStoreV34, "HDF1:"),
        "cam": Component(Xspress3DetectorCamV33, "det1:"),
    }
    for mca_num in range(1, 5):
        for roi_num in range(1, rois_per_mca + 1):
            xspressComponents.update(
                {
                    f"mca{mca_num}roi_{roi_num}": Component(
                        ROIStatNPlugin_V25, f"MCA{mca_num}ROI:{roi_num}:"
                    )
                }
            )

    xspress = create_device_from_components(
        name="xspress", base_class=XspressBase, **xspressComponents
    )
    return xspress(prefix=prefix, **kwargs)
