import numpy as np
import matplotlib.pyplot as plt

PREAMBLE = [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]  # 16 samples = 8 us at 2 MS/s


def make_frame(bits):
    """bits: list of 112 ones/zeros. Returns a NumPy array of 16 + 2*112 samples."""
    samples = list(PREAMBLE)
    for bit in bits:
        if bit == 1:
            samples.extend([1, 0])   # pulse in the first half = 1
        else:
            samples.extend([0, 1])   # pulse in the second half = 0
    return np.array(samples, dtype=float)


def add_noise(samples, snr_db):
    """Return samples plus Gaussian noise so the signal-to-noise ratio is snr_db."""
    signal_power = np.mean(samples ** 2)
    noise_power = signal_power / 10 ** (snr_db / 10)
    noise_std = np.sqrt(noise_power)
    return samples + np.random.normal(0, noise_std, len(samples))


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    bits = rng.integers(0, 2, 112).tolist()
    frame = make_frame(bits)
    print("frame length:", len(frame), "(should be 240)")

    fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    for ax, snr in zip(axes, [None, 20, 10, 3]):
        y = frame if snr is None else add_noise(frame, snr)
        ax.plot(y)
        ax.set_ylabel("clean" if snr is None else f"{snr} dB")
    axes[-1].set_xlabel("sample number")
    plt.tight_layout()
    plt.show()

# OBSERVATION (3 dB): write one or two sentences here in your own words