from ophyd import Component, Device, EpicsSignal, EpicsSignalRO, \
    PVPositionerIsClose


class OceanInterestRegion(Device):

    waveform = Component(EpicsSignal, "", lazy=True)
    luminescence = Component(EpicsSignal, ":Luminescence", lazy=True)
    upper_limit = Component(EpicsSignal, ":UpperLimit", lazy=True)
    lower_limit = Component(EpicsSignal, ":LowerLimit", lazy=True)


class OceanIntegrationTime(Device):

    resolution = Component(EpicsSignal, "Resolution", lazy=True)
    driver_low = Component(EpicsSignal, "Value:DRVL", lazy=True)
    driver_high = Component(EpicsSignal, "Value:DRVH", lazy=True)
    value = Component(EpicsSignal, "Value", lazy=True)
    calc = Component(EpicsSignal, "Calc", lazy=True)


class OceanDetectorTemperature(PVPositionerIsClose):
    
    readback = Component(EpicsSignalRO, "", lazy=True)
    setpoint = Component(EpicsSignal, ":SetPoint", lazy=True)
    actuate_value = Component(EpicsSignalRO, ":SetPoint:fbk", lazy=True)


class OceanOpticsSpectrometer(Device):

    index = Component(EpicsSignal, "SetIndex", lazy=True)
    channel = Component(EpicsSignal, "SetChannel", lazy=True)
    integration = Component(EpicsSignal, "SetIntegration", lazy=True)
    averages = Component(EpicsSignal, "SetAverages", lazy=True)
    boxcar = Component(EpicsSignal, "SetBoxcar", lazy=True)

    spectra = Component(EpicsSignalRO, "Spectra", lazy=True)
    dark_corrected_spectra = Component(EpicsSignalRO, "DarkCorrectedSpectra", lazy=True)
    processed_spectra = Component(EpicsSignalRO, "Spectra:Processed", lazy=True)
    spectra_axis = Component(EpicsSignalRO, "SpectraAxis", lazy=True)

    electrical_dark = Component(EpicsSignal, "ElectricalDark", lazy=True)
    dark_spectrum = Component(EpicsSignalRO, "GetDarkSpectrum", lazy=True)
    external_trigger_mode = Component(EpicsSignalRO, "ExternalTriggerMode", lazy=True)
    set_external_trigger_mode = Component(EpicsSignalRO, "ExternalTriggerMode:Set", lazy=True)
    strobe = Component(EpicsSignal, "SetStrobe", lazy=True)
    total_luminescence = Component(EpicsSignal, "TotalLuminescence", lazy=True)
    acquisition_mode = Component(EpicsSignal, "AcquisitionMode", lazy=True)
    acquire = Component(EpicsSignal, "Acquire", lazy=True)
    acquiring = Component(EpicsSignalRO, "Acquiring", lazy=True)

    region_full = Component(EpicsSignal, "RegionFull", lazy=True)

    region1 = Component(OceanInterestRegion, "Region1", lazy=True)
    region2 = Component(OceanInterestRegion, "Region2", lazy=True)
    region3 = Component(OceanInterestRegion, "Region3", lazy=True)
    region4 = Component(OceanInterestRegion, "Region4", lazy=True)
    region5 = Component(OceanInterestRegion, "Region5", lazy=True)


    index = Component(OceanIntegrationTime, "IntegrationTime:", lazy=True)


    external_trigger = Component(EpicsSignal, "ExternalTrigger", lazy=True)
    external_trigger_invert = Component(EpicsSignal, "ExternalTrigger:Invert", lazy=True)
    progress_bar = Component(EpicsSignal, "ProgressBar", lazy=True)

    file_path = Component(EpicsSignal, "fileDirectory", lazy=True)
    file_root = Component(EpicsSignal, "fileRoot", lazy=True)
    file_index = Component(EpicsSignal, "fileIndex", lazy=True)

    script_path = Component(EpicsSignal, "scriptDirectory", lazy=True)
    script_name = Component(EpicsSignal, "scriptName", lazy=True)
    script_status = Component(EpicsSignal, "scriptStatus", lazy=True)

    det_temperature = Component(OceanDetectorTemperature, "DetectorTemp", lazy=True)