import numpy as np
from crc import hex_to_bits, crc_ok
from frame_gen import make_frame, PREAMBLE
from fields import describe

# Real ADS-B messages (published examples)
MESSAGES = [
    "8D4840D6202CC371C32CE0576098",   # identification: KLM1023
    "8D40621D58C382D690C8AC2863A7",   # position, altitude 38000 ft
    "8D485020994409940838175B284F",   # velocity
    "8D40621D58C386435CC412692AD6",   # position (second frame, same aircraft)
]


def bits_to_hex(bits):
    value = 0
    for b in bits:
        value = (value << 1) | b
    return format(value, "028X")


def build_stream(hex_messages, snr_db, rng, first_gap=(50, 300), gap=(100, 400)):
    """Frames separated by random silent gaps, with noise over everything."""
    parts = [np.zeros(int(rng.integers(*first_gap)))]
    frame_power = None
    for h in hex_messages:
        frame = make_frame(hex_to_bits(h))
        frame_power = np.mean(frame ** 2)
        parts.append(frame)
        parts.append(np.zeros(int(rng.integers(*gap))))
    stream = np.concatenate(parts)
    noise_std = np.sqrt(frame_power / 10 ** (snr_db / 10))
    return stream + rng.normal(0, noise_std, len(stream))


def receive(stream, threshold=3.0):
    """Scan the stream; return (position, hex_string) for every CRC-valid frame."""
    template = 2 * np.array(PREAMBLE) - 1
    scores = np.correlate(stream, template, mode="valid")
    found = []
    i = 0
    last_start = len(stream) - 240
    while i <= last_start:
        if scores[i] >= threshold:
            window = scores[i:i + 6]
            j = i + int(np.argmax(window))
            if j <= last_start:
                bits = []
                first = j + 16
                for k in range(112):
                    bits.append(1 if stream[first + 2 * k] > stream[first + 2 * k + 1] else 0)
                if crc_ok(bits):
                    found.append((j, bits_to_hex(bits)))
                    i = j + 240
                    continue
        i += 1
    return found


if __name__ == "__main__":
    rng = np.random.default_rng(21)

    stream = build_stream(MESSAGES, snr_db=14, rng=rng)
    print(f"stream of {len(stream)} samples, 4 frames sent at 14 dB SNR\n")
    for position, hex_message in receive(stream):
        print(f"sample {position:5d}: {hex_message}  ->  {describe(hex_message)}")

    print("\nrecovery over 200 streams per SNR level:")
    for snr in [20, 14, 12, 10, 8]:
        recovered = 0
        wrong = 0
        for _ in range(200):
            result = receive(build_stream(MESSAGES, snr, rng))
            got = [h for _, h in result]
            recovered += sum(1 for m in MESSAGES if m in got)
            wrong += sum(1 for h in got if h not in MESSAGES)
        print(f"  SNR {snr:2d} dB: {recovered / (200 * len(MESSAGES)):6.1%} of messages recovered, "
              f"{wrong} wrong messages accepted")