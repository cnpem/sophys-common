import copy
import typing

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum

import numpy as np
from numpy.typing import NDArray


class EnergyRangeType(StrEnum):
    ENERGY = "energy"
    K_SPACE = "k-space"


def _create_energy_configuration(
    energy_ranges: typing.Optional[list[tuple]] = None,
    k_ranges: typing.Optional[list[tuple]] = None,
    edge_energy: typing.Optional[float] = None,
) -> list[dict[str, float]]:
    """
    Join the energy ranges and k-space ranges into a single, more easily usable data structure.

    Arguments
    ---------
    energy_ranges : list of tuples, optional
        A list of energy range specifications, which can be either of form
        (start pos, end pos, step) or (index, start pos, end pos, step).
    k_ranges : list of tuples, optional
        A list of k-space range specifications, which can be either of form
        (start pos, end pos, step) or (index, start pos or None, end pos, step).
    edge_energy : float, optional
        The edge energy for k-space to energy calculations.

    Returns
    -------
    list of dicts
        A list of dictionaries specifying each range. If the original ranges
        specified an index for each range, the list is populated in-order.
        Each entry necessarily contains the following keys:
            `type`: Type of range (see EnergyRangeType)
            `start`: Start position of the range (can be None)
            `stop`: End position of the range
            `step`: Step size between each point in the range
        Additionally, in ranges with the index specified, the key `idx`
        contains the index of that range. In k-space ranges, an `edge`
        key is also added with the specified `edge_energy` value.
    """

    if energy_ranges is None:
        energy_ranges = []
    if k_ranges is None:
        k_ranges = []

    # Pre-fill all needed indexes
    energy_conf = [None] * (len(energy_ranges) + len(k_ranges))

    # Auxiliary index for old-style range specification.
    _aux_index = 0

    def populate_range(
        range_params: tuple,
        range_type: EnergyRangeType,
        extra_metadata: typing.Optional[dict] = None,
    ):
        nonlocal _aux_index

        if extra_metadata is None:
            extra_metadata = {}

        index = None
        start, stop, step = None, None, None
        extras = copy.copy(extra_metadata)

        if len(range_params) == 3:
            index = _aux_index
            start, stop, step = range_params[0], range_params[1], range_params[2]
        else:
            index = range_params[0]
            start, stop, step = range_params[1], range_params[2], range_params[3]
            extras["idx"] = range_params[0]

        energy_conf[index] = {
            "type": range_type,
            "start": start,
            "stop": stop,
            "step": step,
            **extras,
        }
        _aux_index += 1

    for r in energy_ranges:
        populate_range(r, EnergyRangeType.ENERGY, {})

    for r in k_ranges:
        populate_range(r, EnergyRangeType.K_SPACE, {"edge": edge_energy})

    return energy_conf


def k2energy(k: float) -> float:
    """Convert a k-space measure to energy."""
    return np.round(3.81 * (np.power(k, 2)), 4)


def energy2k(e: float) -> float:
    """Convert an energy value to k-space."""
    if e < 0:
        return 0
    return np.round(np.sqrt(e / 3.81), 4)


def create_energy_trajectory(
    energy_ranges: typing.Optional[list[tuple]] = None,
    k_ranges: typing.Optional[list[tuple]] = None,
    edge_energy: typing.Optional[float] = None,
) -> NDArray[np.float64]:
    """
    Create a full energy trajectory from energy and k-space ranges.

    Arguments
    ---------
    energy_ranges : list of tuples, optional
        A list of energy range specifications, which can be either of form
        (start pos, end pos, step) or (index, start pos, end pos, step).
    k_ranges : list of tuples, optional
        A list of k-space range specifications, which can be either of form
        (start pos, end pos, step) or (index, start pos or None, end pos, step).
    edge_energy : float, optional
        The edge energy for k-space to energy calculations.
    """

    def handle_energy_range(all_ranges, range_config):
        start = range_config["start"]
        stop = range_config["stop"]
        step = range_config["step"]

        return np.arange(start, stop, step)

    def handle_k_range(all_ranges, range_config):
        start = range_config["start"]
        stop = range_config["stop"]
        step = range_config["step"]

        if start is None:
            if "idx" not in range_config:
                raise ValueError(
                    f"Using k-space ranges without a start position requires index information, but it's missing: {range_config}"
                )

            previous_range = all_ranges[range_config["idx"] - 1]
            start = previous_range["stop"]

            previous_range_type = previous_range["type"]
            if previous_range_type == EnergyRangeType.ENERGY:
                # NOTE: This assumes every range's 'edge' is the same. It should be, right?
                start = energy2k(start - range_config["edge"])

            assert (
                start < stop
            ), f"Could not generate a k-space range, as the calculated starting position {start} is greater than the end position {stop}."

        return range_config["edge"] + k2energy(np.arange(start, stop, step))

    energy_conf = _create_energy_configuration(energy_ranges, k_ranges, edge_energy)

    energy = np.array([], dtype=np.float64)
    arg_cut = -1
    for config in energy_conf:
        if config["type"] == EnergyRangeType.ENERGY:
            energy_calc = handle_energy_range(energy_conf, config)
        elif config["type"] == EnergyRangeType.K_SPACE:
            energy_calc = handle_k_range(energy_conf, config)
        else:
            raise ValueError(
                f"Error, could not find right parameters for energy. Check: {config}"
            )

        # Example:
        # Before: energy = [10, 20, 30, 40], energy_calc = [25, 35, 45, 55]
        # After:  energy = [10, 20, 25, 35, 45, 55]
        if energy.shape[0] > 0:
            arg_cut = np.argmin(np.abs(energy - energy_calc.min()))
            # If they're equal, remove one of them. Otherwise, keep everything.
            if energy[arg_cut] != energy_calc[0]:
                arg_cut += 1
        energy = np.append(energy[:arg_cut], energy_calc)
    return energy
