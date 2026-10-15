import numpy as np
import matplotlib.pyplot as plt
from crc import add_crc, crc_ok
from decoder import make_stream, find_preamble, read_bits, bit_errors

if __name__ == "__main__":
    rng = np.random.default_rng(11)
    snrs = [20, 15, 12, 10, 8, 6, 4, 2]
    frames = 500
    valid_rate, wrong_but_valid = [], []
    for snr in snrs:
        valid = 0
        accepted_wrong = 0
        for _ in range(frames):
            bits = add_crc(rng.integers(0, 2, 88).tolist())      # 112 bits with a correct CRC
            offset = int(rng.integers(20, 200))
            stream = make_stream(bits, snr, offset, rng)
            start = find_preamble(stream)
            received = read_bits(stream, start)
            if crc_ok(received):
                valid += 1
                if bit_errors(bits, received) > 0:               # passed the CRC but is wrong
                    accepted_wrong += 1
        valid_rate.append(valid / frames)
        wrong_but_valid.append(accepted_wrong)
        print(f"SNR {snr:2d} dB -> frames accepted {valid / frames:6.1%}   accepted but wrong: {accepted_wrong}")

    plt.plot(snrs, [100 * v for v in valid_rate], "o-")
    plt.xlabel("SNR (dB)")
    plt.ylabel("frames accepted by the CRC (%)")
    plt.grid(True)
    plt.show()