"""
references:
    - https://www.candelatech.com/courses-2023/Session2c_notes.pdf
        Module2: WLAN PHY Layer
        Session2c: MCS Table, PHY Data Rates and Throughput
    - https://mcsindex.net/
        OFDM 20/40 MHz with 0.8/0.4 Guard interval
"""

from typing import Any

WI_FI_4_MAX_RATES_PER_SPATIAL_STREAM = 150.0

# Base mapping for a single spatial stream (NSS=1) for 20 MHz channel
MCS_BASES = [
    {
        "mcs": 0,
        "modulation": "BPSK",
        "coding_rate": "1/2",
        "thresholds": 4,
        "channels": {
            20: {
                "guard_interval": {
                    800: {
                        "rate": 6.5,
                    },
                    400: {
                        "rate": 7.2,
                    },
                }
            },
            40: {
                "guard_interval": {
                    800: {
                        "rate": 13.5,
                    },
                    400: {
                        "rate": 15.0,
                    },
                }
            },
        },
    },
    {
        "mcs": 1,
        "modulation": "QPSK",
        "coding_rate": "1/2",
        "thresholds": 7,
        "channels": {
            20: {
                "guard_interval": {
                    800: {
                        "rate": 13.0,
                    },
                    400: {
                        "rate": 14.40,
                    },
                }
            },
            40: {
                "guard_interval": {
                    800: {
                        "rate": 27.0,
                    },
                    400: {
                        "rate": 30.0,
                    },
                }
            },
        },
    },
    {
        "mcs": 2,
        "modulation": "QPSK",
        "coding_rate": "3/4",
        "thresholds": 10,
        "channels": {
            20: {
                "guard_interval": {
                    800: {
                        "rate": 19.5,
                    },
                    400: {
                        "rate": 21.70,
                    },
                }
            },
            40: {
                "guard_interval": {
                    800: {
                        "rate": 40.50,
                    },
                    400: {
                        "rate": 45.0,
                    },
                }
            },
        },
    },
    {
        "mcs": 3,
        "modulation": "16-QAM",
        "coding_rate": "1/2",
        "thresholds": 13,
        "channels": {
            20: {
                "guard_interval": {
                    800: {
                        "rate": 26.0,
                    },
                    400: {
                        "rate": 28.90,
                    },
                }
            },
            40: {
                "guard_interval": {
                    800: {
                        "rate": 54.0,
                    },
                    400: {
                        "rate": 60.0,
                    },
                }
            },
        },
    },
    {
        "mcs": 4,
        "modulation": "16-QAM",
        "coding_rate": "3/4",
        "thresholds": 16,
        "channels": {
            20: {
                "guard_interval": {
                    800: {
                        "rate": 39.0,
                    },
                    400: {
                        "rate": 43.30,
                    },
                }
            },
            40: {
                "guard_interval": {
                    800: {
                        "rate": 81.0,
                    },
                    400: {
                        "rate": 90.0,
                    },
                }
            },
        },
    },
    {
        "mcs": 5,
        "modulation": "64-QAM",
        "coding_rate": "2/3",
        "thresholds": 19,
        "channels": {
            20: {
                "guard_interval": {
                    800: {
                        "rate": 52.0,
                    },
                    400: {
                        "rate": 57.80,
                    },
                }
            },
            40: {
                "guard_interval": {
                    800: {
                        "rate": 108.0,
                    },
                    400: {
                        "rate": 120.0,
                    },
                }
            },
        },
    },
    {
        "mcs": 6,
        "modulation": "64-QAM",
        "coding_rate": "3/4",
        "thresholds": 21,
        "channels": {
            20: {
                "guard_interval": {
                    800: {
                        "rate": 58.50,
                    },
                    400: {
                        "rate": 65.00,
                    },
                }
            },
            40: {
                "guard_interval": {
                    800: {
                        "rate": 121.50,
                    },
                    400: {
                        "rate": 135.0,
                    },
                }
            },
        },
    },
    {
        "mcs": 7,
        "modulation": "64-QAM",
        "coding_rate": "5/6",
        "thresholds": 24,
        "channels": {
            20: {
                "guard_interval": {
                    800: {
                        "rate": 65.0,
                    },
                    400: {
                        "rate": 72.20,
                    },
                }
            },
            40: {
                "guard_interval": {
                    800: {
                        "rate": 135.0,
                    },
                    400: {
                        "rate": 150.0,
                    },
                }
            },
        },
    },
]


def calculate_speed_degradation(
    snr_db: float,
    channel_width: int = 20,  # 20, 40 MHz
    guard_interval: int = 400,  # 400, 800 nano seconds
) -> float | None:
    """
    Return bandwidth degradation for 1 spread reference SNR, channel width and guard interval.

    :param snr_db: signal noice from 30..0
    :param channel_width: channel width 20, 40 MHz
    :param guard_interval: guard interval 400 ns, 800 ns
    :return: speed degradation level 1.0..0.0
    """
    mcss = mcs_lookup(snr_db)
    return (
        mcss[-1]["channels"][channel_width]["guard_interval"][guard_interval]["rate"]
        / WI_FI_4_MAX_RATES_PER_SPATIAL_STREAM
        if mcss
        else 0.0
    )


def mcs_lookup(snr_db: float) -> list[dict[str, Any]]:
    """

    :param snr_db: signal noice from 30..0
    :return: list of MCS
    """
    result = []
    for mcs in MCS_BASES:
        if mcs["thresholds"] <= snr_db:
            result.append(mcs)

    return result


if __name__ == "__main__":
    assert not mcs_lookup(0)
    assert mcs_lookup(4)
    assert mcs_lookup(7)
    assert mcs_lookup(10)
    assert mcs_lookup(13)
    assert mcs_lookup(16)
    assert mcs_lookup(19)
    assert mcs_lookup(21)
    assert mcs_lookup(24)
    assert mcs_lookup(30)

    assert not calculate_speed_degradation(0)
    assert calculate_speed_degradation(4)
    assert calculate_speed_degradation(7)
    assert calculate_speed_degradation(10)
    assert calculate_speed_degradation(13)
    assert calculate_speed_degradation(16)
    assert calculate_speed_degradation(19)
    assert calculate_speed_degradation(21)
    assert calculate_speed_degradation(24)
    assert calculate_speed_degradation(30)
