from pathlib import Path
import pytest

import shutil
import sys

from unittest.mock import patch

from sophys.common.utils.packages import (
    install_packages,
    install_lockfile,
    PackageManagementBackend,
    LockfileFormat,
)


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
    assert "pytest" not in mocked_venv.installed_packages()
    install_packages("pytest", custom_python_executable=mocked_venv.python)
    assert "pytest" in mocked_venv.installed_packages()

    assert "requests" not in mocked_venv.installed_packages()
    assert "numpy" not in mocked_venv.installed_packages()
    install_packages("requests", "numpy", custom_python_executable=mocked_venv.python)
    assert "requests" in mocked_venv.installed_packages()
    assert "numpy" in mocked_venv.installed_packages()


def test_install_package_uv(mocked_venv):
    with patch("importlib.util.find_spec") as mock:
        # Anything other than None should suffice.
        mock.return_value = True

        assert "pytest" not in mocked_venv.installed_packages()
        install_packages(
            "pytest", custom_python_executable=mocked_venv.python, backend="uv"
        )
        assert "pytest" in mocked_venv.installed_packages()

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


def test_install_failure(mocked_subprocess):
    from subprocess import CalledProcessError

    mocked_subprocess.side_effect = CalledProcessError(1, "pip install")

    with pytest.raises(
        RuntimeError, match="Package installation failed: sophys-common"
    ):
        install_packages("sophys-common")


def test_lockfile_requirements_pip(mocked_venv, tmp_path):
    with open(tmp_path / "requirements.txt", "w") as _f:
        _f.writelines(["pytest"])

    assert "pytest" not in mocked_venv.installed_packages()
    install_lockfile(
        str(tmp_path),
        format=LockfileFormat.REQUIREMENTS,
        custom_python_executable=mocked_venv.python,
    )
    assert "pytest" in mocked_venv.installed_packages()

    (tmp_path / "requirements.txt").unlink()

    req_file = tmp_path / "requirements_other.txt"
    with open(req_file, "w") as _f:
        _f.writelines(["requests\n", "numpy>2\n"])

    assert "requests" not in mocked_venv.installed_packages()
    assert "numpy" not in mocked_venv.installed_packages()
    install_lockfile(
        str(req_file),
        format=LockfileFormat.REQUIREMENTS,
        custom_python_executable=mocked_venv.python,
    )
    assert "requests" in mocked_venv.installed_packages()
    assert "numpy" in mocked_venv.installed_packages()


def test_lockfile_requirements_uv(mocked_venv, tmp_path):
    with patch("importlib.util.find_spec") as mock:
        # Anything other than None should suffice.
        mock.return_value = True

        with open(tmp_path / "requirements.txt", "w") as _f:
            _f.writelines(["importlib-metadata\n", "pytest"])

        assert "pytest" not in mocked_venv.installed_packages()
        install_lockfile(
            str(tmp_path),
            format=LockfileFormat.REQUIREMENTS,
            backend=PackageManagementBackend.UV,
            custom_python_executable=mocked_venv.python,
        )
        assert "pytest" in mocked_venv.installed_packages()

        (tmp_path / "requirements.txt").unlink()

        req_file = tmp_path / "requirements_other.txt"
        with open(req_file, "w") as _f:
            _f.writelines(["importlib-metadata\n", "requests\n", "numpy>2\n"])

        assert "requests" not in mocked_venv.installed_packages()
        assert "numpy" not in mocked_venv.installed_packages()
        install_lockfile(
            str(req_file),
            format=LockfileFormat.REQUIREMENTS,
            backend=PackageManagementBackend.UV,
            custom_python_executable=mocked_venv.python,
        )
        assert "requests" in mocked_venv.installed_packages()
        assert "numpy" in mocked_venv.installed_packages()


def test_lockfile_pylock_pip(mocked_venv, tmp_path):
    source_path = Path(__file__).parent / "test.pylock.toml"
    test_path: Path = tmp_path / "pylock.toml"
    shutil.copyfile(source_path, test_path)

    assert "numpy" not in mocked_venv.installed_packages()
    install_lockfile(str(test_path), custom_python_executable=mocked_venv.python)
    assert "numpy" in mocked_venv.installed_packages()


def test_lockfile_pylock_uv(mocked_venv, tmp_path):
    with patch("importlib.util.find_spec") as mock:
        # Anything other than None should suffice.
        mock.return_value = True

        source_path = Path(__file__).parent / "test.pylock.toml"
        test_path = tmp_path / "pylock.toml"
        shutil.copyfile(source_path, test_path)

        assert "numpy" not in mocked_venv.installed_packages()
        install_lockfile(
            str(test_path),
            backend=PackageManagementBackend.UV,
            custom_python_executable=mocked_venv.python,
        )
        assert "numpy" in mocked_venv.installed_packages()


def test_lockfile_http(mocked_venv):
    from io import BytesIO
    from requests import Response

    mock_res = Response()
    mock_res.status_code = 200
    mock_res.headers["Content-Type"] = "plain/text"
    mock_res.raw = BytesIO(b"requests==2.34.2")

    with patch("sophys.common.utils.packages.http_get") as mock:
        mock.return_value = mock_res

        assert "requests" not in mocked_venv.installed_packages()
        install_lockfile(
            "http://localhost:1234/api/get_requirements?type=plain",
            format=LockfileFormat.REQUIREMENTS,
            custom_python_executable=mocked_venv.python,
        )
        assert "requests" in mocked_venv.installed_packages()
