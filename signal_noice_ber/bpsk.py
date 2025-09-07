import numpy as np
from scipy.special import erfc


def calculate_ber_bpsk(snr_db: float | list[float]) -> float:
    """
    Calculate BER for BPSK modulation in AWGN channel.

    Args:
    snr_db (float or array-like): SNR in dB.

    Returns:
    float or array-like: Corresponding BER value(s).
    """
    snr_linear = 10 ** (np.array(snr_db) / 10.0)  # Convert dB to linear
    ber = 0.5 * erfc(np.sqrt(snr_linear))
    return ber
