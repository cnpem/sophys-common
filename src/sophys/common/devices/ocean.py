from ophyd import Component, Device, EpicsSignal, EpicsSignalRO, \
    PVPositionerIsClose


class OceanInterestRegion(Device):

    waveform = Component(EpicsSignal, "")
    luminescence = Component(EpicsSignal, ":Luminescence")
    upper_limit = Component(EpicsSignal, ":UpperLimit")
    lower_limit = Component(EpicsSignal, ":LowerLimit")


class OceanIntegrationTime(Device):

    resolution = Component(EpicsSignal, "Resolution")
    driver_low = Component(EpicsSignal, "Value:DRVL")
    driver_high = Component(EpicsSignal, "Value:DRVH")
    value = Component(EpicsSignal, "Value")
    calc = Component(EpicsSignal, "Calc")


class OceanDetectorTemperature(PVPositionerIsClose):
    
    readback = Component(EpicsSignalRO, "")
    setpoint = Component(EpicsSignal, ":SetPoint")
    actuate_value = Component(EpicsSignalRO, ":SetPoint:fbk")


class OceanOpticsSpectrometer(Device):

    index = Component(EpicsSignal, "SetIndex")
    channel = Component(EpicsSignal, "SetChannel")
    integration = Component(EpicsSignal, "SetIntegration")
    averages = Component(EpicsSignal, "SetAverages")
    boxcar = Component(EpicsSignal, "SetBoxcar")

    spectra = Component(EpicsSignalRO, "Spectra")
    dark_corrected_spectra = Component(EpicsSignalRO, "DarkCorrectedSpectra")
    processed_spectra = Component(EpicsSignalRO, "Spectra:Processed")
    spectra_axis = Component(EpicsSignalRO, "SpectraAxis")

    electrical_dark = Component(EpicsSignal, "ElectricalDark")
    dark_spectrum = Component(EpicsSignalRO, "GetDarkSpectrum")
    external_trigger_mode = Component(
        EpicsSignal, read_pv="ExternalTriggerMode", write_pv="ExternalTriggerMode:Set")
    strobe = Component(EpicsSignal, "SetStrobe")
    total_luminescence = Component(EpicsSignal, "TotalLuminescence")
    acquisition_mode = Component(EpicsSignal, "AcquisitionMode")
    acquire = Component(EpicsSignal, "Acquire")
    acquiring = Component(EpicsSignalRO, "Acquiring")

    region_full = Component(EpicsSignal, "RegionFull")

    region1 = Component(OceanInterestRegion, "Region1")
    region2 = Component(OceanInterestRegion, "Region2")
    region3 = Component(OceanInterestRegion, "Region3")
    region4 = Component(OceanInterestRegion, "Region4")
    region5 = Component(OceanInterestRegion, "Region5")


    index = Component(EpicsSignal, "IntegrationTime:")


    external_trigger = Component(EpicsSignal, "ExternalTrigger")
    external_trigger_invert = Component(EpicsSignal, "ExternalTrigger:Invert")
    progress_bar = Component(EpicsSignal, "ProgressBar")

    file_path = Component(EpicsSignal, "fileDirectory")
    file_root = Component(EpicsSignal, "fileRoot")
    file_index = Component(EpicsSignal, "fileIndex")

    script_path = Component(EpicsSignal, "scriptDirectory")
    script_name = Component(EpicsSignal, "scriptName")
    script_status = Component(EpicsSignal, "scriptStatus")

    det_temperature = Component(OceanDetectorTemperature, "DetectorTemp")    
