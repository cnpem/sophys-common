from sophys.common.devices.shutters import (
    ShutterToggle,
    ShutterOpenClose,
    ShutterPermissionError,
)
from sophys.common.utils.status import PremadeStatus
from ophyd.status import AndStatus, MoveStatus
from caproto.threading.pyepics_compat import PV

TOGGLE_SHUTTER_PREFIX = "TOGGLE_SHUTTER:"
PERM_TOGGLE_SHUTTER_PREFIX = "PERM_TOGGLE_SHUTTER:"
SHUTTER_PREFIX = "SHUTTER:"
PERM_SHUTTER_PREFIX = "PERM_SHUTTER:"


def test_open_close_shutter(soft_ioc):
    shutter = ShutterOpenClose(
        prefix=soft_ioc,
        shutter_suffix=SHUTTER_PREFIX,
        ps_suffix=SHUTTER_PREFIX + "PS_STATUS",
        gs_suffix=SHUTTER_PREFIX + "GS_STATUS",
        name="test_shutter",
    )
    shutter.wait_for_connection(all_signals=True, timeout=2.0)

    st = shutter.set(1, timeout=5)  # The shutter softIOC starts closed, so open it
    st.wait()  # There's a settle time of 3 seconds
    assert st.done
    assert st.success
    assert isinstance(
        st, AndStatus
    )  # If there's a change in the shutter's state, an AndStatus is returned

    st = shutter.set(1, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(
        st, PremadeStatus
    )  # If the state of the shutter does not need to be changed, a sucessefull PremadeStatus is returned

    st = shutter.set(0, timeout=5)  # Close the shutter again
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(st, AndStatus)

    st = shutter.set(0, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(st, PremadeStatus)


def test_toggle_shutter(soft_ioc):
    shutter = ShutterToggle(
        prefix=soft_ioc,
        setpoint_suffix=TOGGLE_SHUTTER_PREFIX,
        readback_suffix=TOGGLE_SHUTTER_PREFIX + "STATUS",
        name="test_shutter_toggle",
    )
    shutter.wait_for_connection(all_signals=True, timeout=2.0)

    st = shutter.set(1, timeout=5)  # The shutter softIOC starts closed, so open it
    st.wait()  # There's a settle time of 3 seconds
    assert st.done
    assert st.success
    assert isinstance(
        st, MoveStatus
    )  # If there's a change in the shutter's state, a MoveStatus is returned

    st = shutter.set(1, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(
        st, PremadeStatus
    )  # If the state of the shutter does not need to be changed, a sucessefull PremadeStatus is returned

    st = shutter.set(0, timeout=5)  # Close the shutter again
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(st, MoveStatus)

    st = shutter.set(0, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(st, PremadeStatus)


def test_permission_shutter(soft_ioc):
    shutter = ShutterOpenClose(
        prefix=soft_ioc,
        shutter_suffix=PERM_SHUTTER_PREFIX,
        ps_suffix=PERM_SHUTTER_PREFIX + "PS_STATUS",
        gs_suffix=PERM_SHUTTER_PREFIX + "GS_STATUS",
        permission_pv=soft_ioc + PERM_SHUTTER_PREFIX + "PERM",
        name="test_shutter",
    )
    shutter.wait_for_connection(all_signals=True, timeout=2.0)

    assert (
        not shutter.permission_signal.get()
    )  # The shutter softIOC starts with the permission disabled
    st = shutter.set(1, timeout=5)
    assert st.done
    assert not st.success  # Assert failure as the permission is desabled
    exc = st.exception()
    assert isinstance(exc, ShutterPermissionError)  # Assert type excpetion

    permission_pv = PV(soft_ioc + PERM_SHUTTER_PREFIX + "PERM")
    permission_pv.put(1, wait=True)  # Enable the shutter

    assert shutter.permission_signal.get()
    st = shutter.set(1, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(
        st, AndStatus
    )  # If there's a change in the shutter's state, an AndStatus is returned

    st = shutter.set(1, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(
        st, PremadeStatus
    )  # If the state of the shutter does not need to be changed, a sucessefull PremadeStatus is returned

    permission_pv.put(0, wait=True)  # Disable the shutter
    st = shutter.set(0, timeout=5)
    assert st.done
    assert not st.success  # Assert failure as the permission is desabled
    exc = st.exception()
    assert isinstance(exc, ShutterPermissionError)  # Assert type excpetion

    permission_pv.put(1, wait=True)  # Enable the shutter
    st = shutter.set(0, timeout=5)  # Close the shutter again
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(st, AndStatus)

    st = shutter.set(0, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(st, PremadeStatus)


def test_permission_toggle_shutter(soft_ioc):
    shutter = ShutterToggle(
        prefix=soft_ioc,
        setpoint_suffix=PERM_TOGGLE_SHUTTER_PREFIX,
        readback_suffix=PERM_TOGGLE_SHUTTER_PREFIX + "STATUS",
        permission_pv=soft_ioc + PERM_TOGGLE_SHUTTER_PREFIX + "PERM",
        name="test_shutter_toggle",
    )
    shutter.wait_for_connection(all_signals=True, timeout=2.0)

    assert (
        not shutter.permission_signal.get()
    )  # The shutter softIOC starts with the permission disabled
    st = shutter.set(1, timeout=5)
    assert st.done
    assert not st.success  # Assert failure as the permission is desabled
    exc = st.exception()
    assert isinstance(exc, ShutterPermissionError)  # Assert type excpetion

    permission_pv = PV(soft_ioc + PERM_TOGGLE_SHUTTER_PREFIX + "PERM")
    permission_pv.put(1, wait=True)  # Enable the shutter

    assert shutter.permission_signal.get()
    st = shutter.set(1, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(
        st, MoveStatus
    )  # If there's a change in the shutter's state, a MoveStatus is returned

    st = shutter.set(1, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(
        st, PremadeStatus
    )  # If the state of the shutter does not need to be changed, a sucessefull PremadeStatus is returned

    permission_pv.put(0, wait=True)  # Disable the shutter
    st = shutter.set(0, timeout=5)
    assert st.done
    assert not st.success  # Assert failure as the permission is desabled
    exc = st.exception()
    assert isinstance(exc, ShutterPermissionError)  # Assert type excpetion

    permission_pv.put(1, wait=True)  # Enable the shutter
    st = shutter.set(0, timeout=5)  # Close the shutter again
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(st, MoveStatus)

    st = shutter.set(0, timeout=5)
    st.wait()
    assert st.done
    assert st.success
    assert isinstance(st, PremadeStatus)
