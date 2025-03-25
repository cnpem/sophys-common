import pytest
from sophys.common.devices.picolo import (
    EnumAcquisitionTimeValidator,
    PicoloAcquisitionTimeBase,
    PicoloAcquisitionTimeBaseMixin,
)


@pytest.fixture
def enum_validator():
    """Fixture for EnumAcquisitionTimeValidator."""
    return EnumAcquisitionTimeValidator(
        (
            "200 ms",
            "100 ms",
            "6.25 ms",
            "25 ms",
            "12.5 ms",
            "50 ms",
            "3.125 ms",
            "1.5625 ms",
            "1 ms",
            "0.5 ms",
        )
    )


@pytest.fixture
def picolo_base(enum_validator):
    """Fixture for PicoloAcquisitionTimeBase."""
    return PicoloAcquisitionTimeBase(enum_validator)


def test_enum_acquisition_time_validator_valid_value(enum_validator):
    """Test if valid acquisition time is correctly validated."""
    assert enum_validator.is_valid(0.2)
    assert enum_validator.is_valid(0.1)
    assert enum_validator.is_valid(0.0005)


def test_enum_acquisition_time_validator_invalid_value(enum_validator):
    """Test if invalid acquisition time is correctly rejected."""
    assert not enum_validator.is_valid(30.0)  # Invalid value


def test_format_acquisition_time_with_whole_number(picolo_base):
    """Test if the time is formatted correctly for whole numbers."""
    assert picolo_base.format_acquisition_time(0.01) == "10 ms"  # 10ms (0.01 seconds)


def test_format_acquisition_time_with_decimal(picolo_base):
    """Test if the time is formatted correctly for decimal values."""
    assert picolo_base.format_acquisition_time(0.015) == "15 ms"  # 15ms (0.015 seconds)


def test_format_acquisition_time_with_integer_seconds(picolo_base):
    """Test if an integer seconds value gets formatted without decimal."""
    assert picolo_base.format_acquisition_time(1) == "1000 ms"  # 1 second = 1000ms


def test_validate_and_format_valid_time(picolo_base):
    """Test if valid acquisition time is validated and formatted correctly."""
    valid_time = 0.1  # 100 ms
    formatted_time = picolo_base.validate_and_format(valid_time)
    assert formatted_time == "100 ms"


def test_validate_and_format_invalid_time(picolo_base):
    """Test if invalid acquisition time raises an error."""
    invalid_time = 0.03  # Not in enum values
    with pytest.raises(ValueError):
        picolo_base.validate_and_format(invalid_time)
