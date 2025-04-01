import pytest

import sys

from unittest.mock import patch

from sophys.common.utils.pip import install_package


@pytest.fixture
def mocked_subprocess():
    with patch("subprocess.run") as mock:
        yield mock


@pytest.mark.parametrize(
    ("in_kwargs", "out_args"),
    (
        ({}, []),
        ({"version": "==1.2.3"}, []),
        ({"version": "~=1.2.3"}, []),
        ({"extra_index_url": ["www.com"]}, ["--extra-index-url", "www.com"]),
        (
            {"extra_index_url": ["www.com", "www.org"]},
            ["--extra-index-url", "www.com", "--extra-index-url", "www.org"],
        ),
        ({"force_reinstall": True}, ["--force-reinstall"]),
        ({"disable_cache": True}, ["--no-cache-dir"]),
        (
            {"version": "==1.2.3", "force_reinstall": True, "disable_cache": True},
            ["--force-reinstall", "--no-cache-dir"],
        ),
    ),
)
def test_simple_installation(mocked_subprocess, in_kwargs, out_args):
    target = "sophys-common"

    install_package(target, **in_kwargs)

    target_with_ver = target + in_kwargs.get("version", "")
    expected_command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        *out_args,
        target_with_ver,
    ]

    mocked_subprocess.assert_called_once_with(
        expected_command, check=True, capture_output=True, text=True
    )
