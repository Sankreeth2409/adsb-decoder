import numpy as np
import matplotlib.pyplot as plt
from frame_gen import make_frame, PREAMBLE


def make_stream(bits, snr_db, offset, rng):
    """Frame at a random position inside a noisy stream."""
    frame = make_frame(bits)
    noise_std = np.sqrt(np.mean(frame ** 2) / 10 ** (snr_db / 10))
    stream = np.concatenate([np.zeros(offset), frame, np.zeros(100)])
    return stream + rng.normal(0, noise_std, len(stream))


def find_preamble(stream):
    """Return the index in `stream` where the preamble most likely starts."""
    template = 2 * np.array(PREAMBLE) - 1          # +1 where a pulse is expected, -1 where it is not
    scores = np.correlate(stream, template, mode="valid")
    scores = scores[: len(stream) - 240 + 1]       # only positions where a whole 240-sample frame fits
    return int(np.argmax(scores))


def read_bits(stream, start):
    """Read 112 bits that begin right after the 16-sample preamble at `start`."""
    bits = []
    first = start + 16
    for i in range(112):
        a = stream[first + 2 * i]       # first half of the microsecond
        b = stream[first + 2 * i + 1]   # second half
        if a > b:
            bits.append(1)
        else:
            bits.append(0)
    return bits


def bit_errors(sent, received):
    """How many positions differ between the two lists."""
    return sum(1 for s, r in zip(sent, received) if s != r)


if __name__ == "__main__":
    rng = np.random.default_rng(5)
    snrs = [20, 15, 12, 10, 8, 6, 4, 2]
    results = []
    for snr in snrs:
        errors = 0
        frames = 300
        for _ in range(frames):
            bits = rng.integers(0, 2, 112).tolist()
            offset = int(rng.integers(20, 200))
            stream = make_stream(bits, snr, offset, rng)
            start = find_preamble(stream)
            errors += bit_errors(bits, read_bits(stream, start))
        ber = errors / (frames * 112)
        results.append(ber)
        print(f"SNR {snr:2d} dB -> bit error rate {ber:.4f}")

    plt.semilogy(snrs, np.maximum(results, 1e-5), "o-")
    plt.xlabel("SNR (dB)")
    plt.ylabel("bit error rate")
    plt.grid(True)
    plt.show()