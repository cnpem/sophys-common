import pytest

import sys

from unittest.mock import patch

from sophys.common.utils.packages import install_packages, PackageManagementBackend


@pytest.fixture
def mocked_subprocess():
    with patch("subprocess.run") as mock:
        yield mock


@pytest.fixture
def mocked_venv(virtualenv):
    virtualenv.install_package("uv", installer="pip")

    return virtualenv


@pytest.mark.parametrize(
    ("in_args", "in_kwargs", "out_args"),
    (
        (["sophys-common"], {}, []),
        (["sophys_common==1.2.3"], {}, []),
        (["sophys-common~=1.2.3"], {}, []),
        (
            ["sophys-common"],
            {"extra_index_url": ["www.com"]},
            ["--extra-index-url", "www.com"],
        ),
        (
            ["sophys-common"],
            {"extra_index_url": ["www.com", "www.org"]},
            ["--extra-index-url", "www.com", "--extra-index-url", "www.org"],
        ),
        (["sophys-common"], {"force_reinstall": True}, ["--force-reinstall"]),
        (["sophys-common"], {"disable_cache": True}, ["--no-cache"]),
        (
            ["sophys-common==1.2.3"],
            {"force_reinstall": True, "disable_cache": True},
            ["--force-reinstall", "--no-cache"],
        ),
        (["sophys-common", "pytest"], {}, []),
    ),
)
def test_simple_pip_installation(mocked_subprocess, in_args, in_kwargs, out_args):
    install_packages(*in_args, **in_kwargs)

    expected_command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        *out_args,
        *in_args,
    ]

    mocked_subprocess.assert_called_once_with(
        expected_command, check=True, capture_output=True, text=True
    )


@pytest.mark.parametrize(
    ("in_args", "in_kwargs", "out_args"),
    (
        (["sophys-common"], {"backend": "uv"}, []),
        (["sophys-common"], {"backend": PackageManagementBackend.UV}, []),
        (["sophys-common==1.2.3"], {"backend": "uv"}, []),
        (["sophys-common~=1.2.3"], {"backend": "uv"}, []),
        (
            ["sophys-common"],
            {"backend": "uv", "extra_index_url": ["www.com"]},
            ["--extra-index-url", "www.com"],
        ),
        (
            ["sophys-common"],
            {"backend": "uv", "extra_index_url": ["www.com", "www.org"]},
            ["--extra-index-url", "www.com", "--extra-index-url", "www.org"],
        ),
        (
            ["sophys-common"],
            {"backend": "uv", "force_reinstall": True},
            ["--force-reinstall"],
        ),
        (["sophys-common"], {"backend": "uv", "disable_cache": True}, ["--no-cache"]),
        (
            ["sophys-common==1.2.3"],
            {
                "backend": "uv",
                "force_reinstall": True,
                "disable_cache": True,
            },
            ["--force-reinstall", "--no-cache"],
        ),
        (["sophys-common", "pytest"], {"backend": "uv"}, []),
    ),
)
def test_simple_uv_installation(mocked_subprocess, in_args, in_kwargs, out_args):
    with patch("importlib.util.find_spec") as mock:
        # Anything other than None should suffice.
        mock.return_value = True

        install_packages(*in_args, **in_kwargs)

        mock.assert_called_once_with("uv")

    expected_command = [
        sys.executable,
        "-m",
        "uv",
        "pip",
        "install",
        *out_args,
        *in_args,
    ]

    mocked_subprocess.assert_called_once_with(
        expected_command, check=True, capture_output=True, text=True
    )


def test_install_package_pip(mocked_venv):
    assert "setuptools" not in mocked_venv.installed_packages()
    install_packages("setuptools", custom_python_executable=mocked_venv.python)
    assert "setuptools" in mocked_venv.installed_packages()

    assert "requests" not in mocked_venv.installed_packages()
    assert "numpy" not in mocked_venv.installed_packages()
    install_packages("requests", "numpy", custom_python_executable=mocked_venv.python)
    assert "requests" in mocked_venv.installed_packages()
    assert "numpy" in mocked_venv.installed_packages()


def test_install_package_uv(mocked_venv):
    with patch("importlib.util.find_spec") as mock:
        # Anything other than None should suffice.
        mock.return_value = True

        assert "setuptools" not in mocked_venv.installed_packages()
        install_packages(
            "setuptools", custom_python_executable=mocked_venv.python, backend="uv"
        )
        assert "setuptools" in mocked_venv.installed_packages()

        assert "requests" not in mocked_venv.installed_packages()
        assert "numpy" not in mocked_venv.installed_packages()
        install_packages(
            "requests",
            "numpy",
            custom_python_executable=mocked_venv.python,
            backend="uv",
        )
        assert "requests" in mocked_venv.installed_packages()
        assert "numpy" in mocked_venv.installed_packages()
