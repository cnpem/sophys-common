import typing


def install_package(
    package_name: str,
    version: typing.Optional[str] = None,
    extra_index_url: typing.Optional[list[str]] = None,
    force_reinstall: bool = False,
    disable_cache: bool = False,
):
    """
    Installs a package via pip.

    Parameters
    ----------
    package_name : str
        Name of the package, as is found on the package registry. Also
        accepts Git URLs (i.e. git+https://...).
    version : str, optional
        Version of the package. Specified with the limiter.
        e.g.: '==1.6.4', '>= 0.7.0', '~=1.10.0'
    extra_index_url : list of str, optional
        Extra package registry index locations to search the package in.
    force_reinstall : bool, optional
        Force reinstallation of the package in case it's already installed.
    disable_cache : bool, optional
        Disable caching of package wheels and HTTP responses by pip.
    """

    import subprocess
    from sys import executable as _python_exec

    command = [_python_exec, "-m", "pip", "install"]
    if extra_index_url is not None:
        for url in extra_index_url:
            command.extend(["--extra-index-url", url])
    if force_reinstall:
        command.append("--force-reinstall")
    if disable_cache:
        command.append("--no-cache-dir")
    command.append("{}{}".format(package_name, version or ""))

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(str(e))
        print("  Standard output:")
        print(e.stdout)
        print("  Standard error:")
        print(e.stderr)

        raise RuntimeError(f"Package installation failed: {package_name}") from e
