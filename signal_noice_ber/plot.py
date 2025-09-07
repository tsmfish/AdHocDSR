import numpy as np
from signal_noice_ber.bpsk import calculate_ber_bpsk
import matplotlib.pyplot as plt


calculate_ber = calculate_ber_bpsk

# Compute for plotting
snr_values_db = np.linspace(0, 12, 100)  # Finer range for smooth curve
ber_values = calculate_ber(snr_values_db)

# Plot
plt.figure(figsize=(8, 5))
plt.semilogy(snr_values_db, ber_values, label="BPSK BER")
plt.xlabel("SNR (dB)")
plt.ylabel("Bit Error Rate (BER)")
plt.title("BER vs. SNR for BPSK in AWGN Channel")
plt.grid(True)
plt.legend()
plt.show()
