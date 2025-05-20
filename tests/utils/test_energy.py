import pytest

import numpy as np

from sophys.common.utils.energy import (
    _create_energy_configuration,
    create_energy_trajectory,
    EnergyRangeType,
)


@pytest.mark.parametrize(
    ("in_e_ranges", "in_k_ranges", "e0", "expected_config_list"),
    [
        pytest.param([], [], 0, [{}], id="empty ranges"),
        pytest.param(
            [(10, 30, 5)],
            [],
            0,
            [{"type": EnergyRangeType.ENERGY, "start": 10, "stop": 30, "step": 5}],
            id="simple energy range, without idx",
        ),
        pytest.param(
            [(0, 10, 30, 5)],
            [],
            0,
            [
                {
                    "type": EnergyRangeType.ENERGY,
                    "start": 10,
                    "stop": 30,
                    "step": 5,
                    "idx": 0,
                }
            ],
            id="simple energy range, with idx",
        ),
        pytest.param(
            [(10, 40, 10), (30, 60, 10)],
            [],
            0,
            [
                {"type": EnergyRangeType.ENERGY, "start": 10, "stop": 40, "step": 10},
                {"type": EnergyRangeType.ENERGY, "start": 30, "stop": 60, "step": 10},
            ],
            id="multiple energy ranges, without idx",
        ),
        pytest.param(
            [(0, 10, 40, 10), (1, 30, 60, 10)],
            [],
            0,
            [
                {
                    "type": EnergyRangeType.ENERGY,
                    "start": 10,
                    "stop": 40,
                    "step": 10,
                    "idx": 0,
                },
                {
                    "type": EnergyRangeType.ENERGY,
                    "start": 30,
                    "stop": 60,
                    "step": 10,
                    "idx": 1,
                },
            ],
            id="multiple energy ranges, with idx",
        ),
        pytest.param(
            [(30, 60, 10), (10, 40, 10)],
            [],
            0,
            [
                {"type": EnergyRangeType.ENERGY, "start": 30, "stop": 60, "step": 10},
                {"type": EnergyRangeType.ENERGY, "start": 10, "stop": 40, "step": 10},
            ],
            id="overriding energy ranges",
        ),
        pytest.param(
            [],
            [(1, 2, 0.5)],
            10,
            [
                {
                    "type": EnergyRangeType.K_SPACE,
                    "start": 1,
                    "stop": 2,
                    "step": 0.5,
                    "edge": 10,
                }
            ],
            id="simple k-space range, without idx",
        ),
        pytest.param(
            [],
            [(0, 1, 2, 0.5)],
            10,
            [
                {
                    "type": EnergyRangeType.K_SPACE,
                    "start": 1,
                    "stop": 2,
                    "step": 0.5,
                    "edge": 10,
                    "idx": 0,
                }
            ],
            id="simple k-space range, with idx",
        ),
        pytest.param(
            [],
            [(1, 2, 3, 0.5), (0, 1, 2, 0.5)],
            10,
            [
                {
                    "type": EnergyRangeType.K_SPACE,
                    "start": 1,
                    "stop": 2,
                    "step": 0.5,
                    "edge": 10,
                    "idx": 0,
                },
                {
                    "type": EnergyRangeType.K_SPACE,
                    "start": 2,
                    "stop": 3,
                    "step": 0.5,
                    "edge": 10,
                    "idx": 1,
                },
            ],
            id="multiple k-space range, with idx",
        ),
        pytest.param(
            [(1, 20, 30, 10)],
            [(0, 1, 2, 0.5)],
            10,
            [
                {
                    "type": EnergyRangeType.K_SPACE,
                    "start": 1,
                    "stop": 2,
                    "step": 0.5,
                    "edge": 10,
                    "idx": 0,
                },
                {
                    "type": EnergyRangeType.ENERGY,
                    "start": 20,
                    "stop": 30,
                    "step": 10,
                    "idx": 1,
                },
            ],
            id="mixed ranges, with idx",
        ),
        pytest.param(
            [(0, 10.81, 13.81, 1)],
            [(1, None, 2, 0.5)],
            10,
            [
                {
                    "type": EnergyRangeType.ENERGY,
                    "start": 10.81,
                    "stop": 13.81,
                    "step": 1,
                    "idx": 0,
                },
                {
                    "type": EnergyRangeType.K_SPACE,
                    "start": None,
                    "stop": 2,
                    "step": 0.5,
                    "edge": 10,
                    "idx": 1,
                },
            ],
            id="mixed ranges, with 2-parameter k-space range",
        ),
    ],
)
def test_create_energy_configuration(
    in_e_ranges, in_k_ranges, e0, expected_config_list
):
    configurations = _create_energy_configuration(in_e_ranges, in_k_ranges, e0)

    for range_config, expected_config in zip(configurations, expected_config_list):
        for key in expected_config.keys():
            assert range_config[key] == expected_config[key], key


@pytest.mark.parametrize(
    ("in_e_ranges", "in_k_ranges", "e0", "out_range"),
    [
        pytest.param([], [], 0, np.array([]), id="empty ranges"),
        pytest.param(
            [(10, 30, 5)],
            [],
            0,
            np.array([10, 15, 20, 25]),
            id="simple energy range, without idx",
        ),
        pytest.param(
            [(0, 10, 30, 5)],
            [],
            0,
            np.array([10, 15, 20, 25]),
            id="simple energy range, with idx",
        ),
        pytest.param(
            [(10, 40, 10), (30, 60, 10)],
            [],
            0,
            np.array([10, 20, 30, 40, 50]),
            id="multiple energy ranges, without idx",
        ),
        pytest.param(
            [(0, 10, 40, 10), (1, 30, 60, 10)],
            [],
            0,
            np.array([10, 20, 30, 40, 50]),
            id="multiple energy ranges, with idx",
        ),
        pytest.param(
            [(30, 60, 10), (10, 40, 10)],
            [],
            0,
            np.array([10, 20, 30, 40, 50]),
            marks=pytest.mark.xfail,
            id="overriding energy ranges",
        ),
        pytest.param(
            [(0, 30, 60, 10)],
            [(1, None, 2, 0.5)],
            0,
            np.array([]),
            marks=pytest.mark.xfail,
            id="invalid automatic k-space range (start > stop)",
        ),
        pytest.param(
            [],
            [(1, 2, 0.5)],
            10,
            np.array([13.81, 18.57]),
            id="simple k-space range, without idx",
        ),
        pytest.param(
            [],
            [(0, 1, 2, 0.5)],
            10,
            np.array([13.81, 18.57]),
            id="simple k-space range, with idx",
        ),
        pytest.param(
            [],
            [(1, 2, 3, 0.5), (0, 1, 2, 0.5)],
            10,
            np.array([13.81, 18.57, 25.24, 33.81]),
            id="multiple k-space range, with idx",
        ),
        pytest.param(
            [(1, 20, 30, 10)],
            [(0, 1, 2, 0.5)],
            10,
            np.array([13.81, 18.57, 20]),
            id="mixed ranges, with idx",
        ),
        pytest.param(
            [(0, 10.81, 13.81, 1)],
            [(1, None, 2, 0.5)],
            10,
            np.array([10.81, 11.81, 12.81, 13.81, 18.57]),
            id="mixed ranges, with 2-parameter k-space range",
        ),
    ],
)
def test_create_energy_trajectory(in_e_ranges, in_k_ranges, e0, out_range):
    energies = create_energy_trajectory(in_e_ranges, in_k_ranges, e0)

    assert np.all(np.isclose(energies, out_range, atol=1e-2))
