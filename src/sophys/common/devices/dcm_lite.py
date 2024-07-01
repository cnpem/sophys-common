from ophyd import Component, FormattedComponent, DynamicDeviceComponent, \
    Device, EpicsSignal, EpicsSignalRO, PVPositionerIsClose


class Goniometer(PVPositionerIsClose):

    readback = FormattedComponent(EpicsSignal, "{prefix}DCM01:GonRx{device_number}_SP_RBV", kind="hinted")
    setpoint = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:GonRx{device_number}_SP", kind="config")
    actuate = Component(EpicsSignal, "GonRxUpdate_SP", kind="omitted")

    def __init__(self, prefix, device_number, **kwargs):
        self.device_number = device_number
        super().__init__(prefix=prefix, **kwargs)


class ShortStroke(PVPositionerIsClose):

    readback = FormattedComponent(EpicsSignal, "{prefix}Shs{shs_axis}_S_RBV", kind="hinted")
    setpoint = FormattedComponent(EpicsSignalRO, "{prefix}Shs{shs_axis}_SP", kind="config")
    actuate = FormattedComponent(EpicsSignal, "ShsUpdate_{shs_axis}_SP", kind="omitted")

    def __init__(self, prefix, shs_axis, **kwargs):
        self.shs_axis = shs_axis
        super().__init__(prefix=prefix, **kwargs)


class DcmLite(Device):

    gonio1 = Component(Goniometer, "1")
    gonio2 = Component(Goniometer, "2")
    
    gap = Component(ShortStroke, "Uy")
    pitch = Component(ShortStroke, "Rx") 
    roll = Component(ShortStroke, "Rz")


dcm_suffixes = {
    "motors": {
        "leveler1": "PB01:m1",
        "leveler2": "PB01:m2",
        "leveler3": "PB01:m3",
        "u_x": "PB01:m4",
        "spindle_x_plus": "PB01:m5",
        "spindle_x_minus": "PB01:m6",
        "granite_x": "PB01:CS2:m7",
        "granite_y": "PB01:CS1:m8"
    }
}

# Get device class
def _getDeviceInstance(device):
    if device == "motors":
        return ControllableMotor
    elif "actuator" in device:
        return createDCMTriggerDevice

def _formatPvname(tempKwags, suffix):
    tempKwags["name"] = f"dcm_{key}"
    if isinstance(suffix, list):
        tempKwags["prefix"] = dcm_prefix + suffix[0]
        tempKwags["device"] = suffix[1]
        tempKwags["isGonio"] = "gonio" in key
    else:  
        tempKwags["prefix"] = suffix 
    return tempKwags

# Create Motors or Actuator Devices for every element of the DCM
dcmDevices = {}
componentsDict = {}
for device, elements in dcm_suffixes.items():
    kwargs = {}
    deviceClass = _getDeviceInstance(device)
    for key, suffix in elements.items():
        tempKwags = _formatPvname(kwargs.copy(), suffix)

        dcmDevices[tempKwags["name"]] = deviceClass(**tempKwags)
        componentsDict[key] = Component(deviceClass, **tempKwags)


dcmDeviceClass = create_device_from_components(name="dcm", **componentsDict)
dcmDevices["dcm"] = dcmDeviceClass(name="dcm")

