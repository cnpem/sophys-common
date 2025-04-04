import enum
import importlib
import typing


class PackageManagementBackend(enum.StrEnum):
    PIP = "pip"
    UV = "uv"


StrSequenceType: typing.TypeAlias = typing.Tuple[str, ...]


def install_packages(
    *package_specs: *StrSequenceType,
    extra_index_url: typing.Optional[list[str]] = None,
    force_reinstall: bool = False,
    disable_cache: bool = False,
    debug: bool = False,
    backend: PackageManagementBackend = PackageManagementBackend.PIP,
    custom_python_executable: typing.Optional[str] = None,
):
    """
    Installs a package in the current environment.

    Parameters
    ----------
    package_specs : str or sequence of strs
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
    """

    import subprocess
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

    if debug:
        _proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        if _proc.stdout is not None:
            for line in _proc.stdout:
                print(line, end="")

        return_code = _proc.wait()
        if return_code != 0:
            packages_str = " ".join(package_specs)
            raise RuntimeError(f"Package installation failed: {packages_str}")

        return

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(str(e))
        print("  Standard output:")
        print(e.stdout)
        print("  Standard error:")
        print(e.stderr)

        packages_str = " ".join(package_specs)
        raise RuntimeError(f"Package installation failed: {packages_str}") from e
