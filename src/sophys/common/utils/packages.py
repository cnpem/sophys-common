"""Utilities for dealing with packages and project dependencies in Python."""

from collections.abc import Sequence

import logging
from pathlib import Path
import importlib.util
import subprocess
import sys
import typing

from urllib.parse import urlsplit, SplitResult
from requests import get as http_get, Response as HttpResponse
import tempfile

from typing_extensions import Unpack, cast

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum


if sys.version_info < (3, 15, 0):
    frozendict = dict


logger = logging.getLogger(__file__)  # noqa: GL08


class PackageManagementBackend(StrEnum):
    """Supported python packaging backends."""

    PIP = "pip"
    UV = "uv"


class LockfileFormat(StrEnum):
    """Supported lockfile formats for python projects."""

    REQUIREMENTS = "requirements.txt"
    PYLOCK = "pylock.toml"


def _run_command(
    command: Sequence[str], *, debug: bool = False, **kwargs
) -> subprocess.CompletedProcess | None:
    """
    Run a command through a subprocess.

    Parameters
    ----------
    command : sequence of str
        The command to be executed in a subprocess, in the same format as used by
        ``subprocess.Popen`` and ``subprocess.run``.
    debug : bool, optional
        Enable debug mode, in which all the output from the backend subprocess
        is printed in real-time.
    **kwargs : dict, optional
        Additional arguments to pass to ``subprocess.Popen`` or ``subprocess.run``.

    Returns
    -------
    subprocess.CompletedProcess
        When using ``debug=False``, the ran process's results are returned.
    None
        When using ``debug=True``, nothing is returned.

    Raises
    ------
    RuntimeError
        If any error happens in the subprocess execution.
    """
    if debug:
        _proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            **kwargs,
        )

        if _proc.stdout is not None:
            for line in _proc.stdout:
                print(line, end="")

        return_code = _proc.wait()
        if return_code != 0:
            raise RuntimeError

        return

    try:
        _proc = subprocess.run(
            command, check=True, capture_output=True, text=True, **kwargs
        )
    except subprocess.CalledProcessError as e:
        print(str(e))
        print("  Standard output:")
        print(e.stdout)
        print("  Standard error:")
        print(e.stderr)

        raise RuntimeError

    return _proc


StrSequenceType: typing.TypeAlias = typing.Tuple[str, ...]


def install_packages(
    *package_specs: Unpack[StrSequenceType],
    extra_index_url: typing.Optional[list[str]] = None,
    force_reinstall: bool = False,
    disable_cache: bool = False,
    debug: bool = False,
    backend: PackageManagementBackend | str = PackageManagementBackend.PIP,
    custom_python_executable: typing.Optional[str] = None,
):
    """
    Install a package in the current environment.

    Parameters
    ----------
    *package_specs : str or sequence of strs
        Name of the packages to be installed, as is found on the package registry,
        together with an optional version specifier for each of them.
        Also accepts Git URLs (i.e. git+https://...).
    extra_index_url : list of str, optional
        Extra package registry index locations to search the package in.
    force_reinstall : bool, optional
        Force reinstallation of the package in case it's already installed.
    disable_cache : bool, optional
        Disable caching of package wheels and HTTP responses by the backend.
    debug : bool, optional
        Enable debug mode, in which all the output from the backend subprocess
        is printed in real-time.
    backend : PackageManagementBackend, optional
        Select which backend to use for package installation. Defaults to pip.
    custom_python_executable : str, optional
        Use a python executable other than the one currently running. Useful for tests.
    """

    from sys import executable as _python_exec

    python_exec = custom_python_executable or _python_exec

    match backend:
        case PackageManagementBackend.PIP:
            command = [python_exec, "-m", "pip", "install"]
        case PackageManagementBackend.UV:
            if importlib.util.find_spec("uv") is None:
                raise RuntimeError(
                    "The 'uv' package is not installed in the current environment."
                )
            command = [python_exec, "-m", "uv", "pip", "install"]

    if extra_index_url is not None:
        for url in extra_index_url:
            command.extend(["--extra-index-url", url])
    if force_reinstall:
        command.append("--force-reinstall")
    if disable_cache:
        # NOTE: Both pip and uv can deal with this option like that.
        command.append("--no-cache")

    for spec in package_specs:
        command.append(spec)

    try:
        _run_command(command, debug=debug)
    except RuntimeError as e:
        packages_str = " ".join(package_specs)
        raise RuntimeError(f"Package installation failed: {packages_str}") from e


def install_lockfile(
    url: str,
    format: LockfileFormat | str = LockfileFormat.PYLOCK,
    *,
    backend: PackageManagementBackend | str = PackageManagementBackend.PIP,
    disable_cache: bool = False,
    debug: bool = False,
    custom_python_executable: str | None = None,
):
    """
    Install packages from a lockfile in the current environment.

    Parameters
    ----------
    url : str
        The URL on which to find the lockfile. It supports the following schemas:
            'file': Use a locally available lockfile.
            'http' / 'https': Fetch from a HTTP API using a GET request.
        If no schema is specified, it defaults to 'file'.
    format : LockfileFormat, optional
        The lockfile format to parse the file as. Defaults to pylock (PEP 751).
    backend : PackageManagementBackend, optional
        Select which backend to use for package installation. Defaults to pip.
    disable_cache : bool, optional
        Disable caching of package wheels and HTTP responses by the backend.
    debug : bool, optional
        Enable debug mode, in which all the output from the backend subprocess
        is printed in real-time.
    custom_python_executable : str, optional
        Use a python executable other than the one currently running. Useful for tests.
    """
    backend_file_name = str(format)

    file_path = None
    match urlsplit(url, scheme="file", allow_fragments=False):
        case SplitResult("file", _, path, _, _):
            file_path = Path(path)
            if not file_path.is_file():
                file_path = file_path / backend_file_name
        case SplitResult(schema, _, _, _, _) if schema in {"http", "https"}:
            result: HttpResponse = http_get(url)

            if (status_code := result.status_code) != 200:
                logger.error(
                    "Invalid status code received. Expected: 200. Got: %d", status_code
                )
                logger.debug("Response body: %s", str(result.json()))

                raise RuntimeError(f"Lockfile installation failed: {url}")

            if (content_type := result.headers.get("Content-Type")) not in {
                "plain/text",
                "application/octet-stream",
            }:
                logger.error(
                    "Invalid Content-Type received. Expected: plain/text or application/octet-stream. Got: %s",
                    str(content_type),
                )
                logger.debug("Response body: %s", str(result.content))

                raise RuntimeError(f"Lockfile installation failed: {url}")

            temp_dir = tempfile.mkdtemp()
            file_path = Path(temp_dir) / backend_file_name
            with open(file_path, "wb") as _f:
                file_path = Path(_f.name)
                for _content in result.iter_content():
                    _f.write(_content)

    if not isinstance(file_path, Path):
        logger.error(
            "Failed to parse a valid lockfile path. Got '%s', of type %s.",
            str(file_path),
            str(type(file_path)),
        )

        raise RuntimeError(f"Lockfile installation failed: {url}")

    if file_path.name != backend_file_name:
        logger.warning(
            "Creating hardlink of '%s' with name '%s', so tools can properly parse the file.",
            file_path.name,
            backend_file_name,
        )

        original_file_path = file_path
        effective_file_path = original_file_path.with_name(backend_file_name)
        if effective_file_path.exists():
            logger.error(
                "File with name '%s' in '%s' already exists. Cannot continue.",
                effective_file_path.name,
                str(effective_file_path.parent),
            )
            raise RuntimeError(f"Lockfile installation failed: {url}")
        effective_file_path.hardlink_to(original_file_path)

        file_path = effective_file_path

    if not file_path.exists():
        logger.error("Specified lockfile path '%s' does not exist.", str(file_path))

        raise RuntimeError(f"Lockfile installation failed: {url}")

    import subprocess
    from sys import executable as _python_exec

    python_exec = custom_python_executable or _python_exec

    match backend:
        case PackageManagementBackend.PIP:
            command = [
                python_exec,
                "-m",
                "pip",
                "install",
                "-r",
                str(file_path),
            ]

            if disable_cache:
                command.insert(4, "--no-cache-dir")
        case PackageManagementBackend.UV:
            if importlib.util.find_spec("uv") is None:
                raise RuntimeError(
                    "The 'uv' package is not installed in the current environment."
                )

            command = [
                python_exec,
                "-m",
                "uv",
                "pip",
                "install",
                "--no-python-downloads",
                "--directory",
                str(file_path.resolve().parent),
                "-r",
                file_path.name,
            ]

            if disable_cache:
                command.insert(5, "--no-cache")

    project_env_proc = _run_command(
        [
            python_exec,
            "-c",
            """'import sysconfig; print(sysconfig.get_config_var("prefix"))'""",
        ],
    )
    project_env = cast(subprocess.CompletedProcess, project_env_proc).stdout

    try:
        _run_command(command, debug=debug, env={"UV_PROJECT_ENVIRONMENT": project_env})
    except RuntimeError as e:
        raise RuntimeError(f"Lockfile installation failed: {url}") from e
