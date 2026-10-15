import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from receiver import MESSAGES, build_stream, receive

rng = np.random.default_rng(7)
snrs = [4, 6, 8, 10, 12, 14, 16, 20]
trials = 200
rates = []
wrong_total = 0
for snr in snrs:
    recovered = 0
    for _ in range(trials):
        got = [h for _, h in receive(build_stream(MESSAGES, snr, rng))]
        recovered += sum(1 for m in MESSAGES if m in got)
        wrong_total += sum(1 for h in got if h not in MESSAGES)
    rates.append(100 * recovered / (trials * len(MESSAGES)))
    print(f"SNR {snr:2d} dB: {rates[-1]:5.1f}% recovered")
print(f"wrong messages accepted in total: {wrong_total}")

os.makedirs("docs", exist_ok=True)
plt.figure(figsize=(7, 4.5))
plt.plot(snrs, rates, "o-", color="black")
plt.xlabel("Signal-to-noise ratio (dB)")
plt.ylabel("Messages recovered (%)")
plt.title(f"ADS-B receiver: recovery vs noise ({trials} streams per point)")
plt.grid(True, alpha=0.3)
plt.ylim(0, 105)
plt.tight_layout()
plt.savefig("docs/recovery_curve.png", dpi=150)
print("saved docs/recovery_curve.png")