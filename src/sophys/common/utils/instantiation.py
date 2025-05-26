from typing import Callable, Optional, Any

from .registry import in_autoregister_context, remove_all_named


def warn_on_timeout(
    dev_class: type, logger: Optional[Callable[[str], Any]] = None, **kwargs
):
    """
    Warn instead of throwing an Exception when timing out during object instantiation.

    This calls `dev_class(**kwargs)` wrapped in an exception-handling logic.

    Parameters
    ----------
    dev_class : type
        The class of the object to be instantiated.
    logger : callable, optional
        A custom logger function to use when instantiation fails.
        Defaults to using logging.error.
    **kwargs : dict, optional
        Keyword arguments to pass onto `dev_class` in instantiation.
    """
    if logger is None:
        import logging

        logger = logging.error

    try:
        return dev_class(**kwargs)
    except TimeoutError as e:
        logger(
            f"Device '{dev_class.__name__}' with args ('{str(kwargs)}') failed to be instantiated:"
        )
        logger("\n".join(e.args))

        # Remove broken device from registry
        if in_autoregister_context() and "name" in kwargs:
            remove_all_named(kwargs["name"])
