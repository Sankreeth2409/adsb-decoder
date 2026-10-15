import numpy as np

POLY = 0xFFF409          # ADS-B CRC-24 generator polynomial (the x^24 term is implicit)


def crc24(bits):
    """Remainder of dividing `bits` (a list of 0/1, most significant bit first) by the generator."""
    reg = 0
    for bit in bits:
        top = (reg >> 23) & 1                  # the bit about to fall off the left end
        reg = ((reg << 1) | bit) & 0xFFFFFF    # shift left and bring in the next message bit
        if top:
            reg ^= POLY                        # "subtract" the generator
    return reg


def hex_to_bits(hex_string):
    return [int(b) for b in bin(int(hex_string, 16))[2:].zfill(len(hex_string) * 4)]


def bits_to_int(bits):
    value = 0
    for b in bits:
        value = (value << 1) | b
    return value


def int_to_bits(value, width):
    return [(value >> (width - 1 - i)) & 1 for i in range(width)]


def add_crc(bits88):
    """Append the 24-bit CRC to an 88-bit message. Returns 112 bits."""
    return bits88 + int_to_bits(crc24(bits88 + [0] * 24), 24)


def crc_ok(bits112):
    """True if the 112-bit frame is consistent (remainder is zero)."""
    return crc24(bits112) == 0


if __name__ == "__main__":
    # A real ADS-B message (aircraft identification) published in "The 1090 MHz Riddle"
    real = hex_to_bits("8D4840D6202CC371C32CE0576098")
    print("real message length:", len(real))
    print("real message passes CRC:", crc_ok(real))

    # Flip each single bit: the CRC must catch every one
    caught = 0
    for i in range(112):
        damaged = list(real)
        damaged[i] ^= 1
        if not crc_ok(damaged):
            caught += 1
    print(f"single-bit errors caught: {caught} of 112")

    # Build a message from scratch and check it
    rng = np.random.default_rng(3)
    msg = rng.integers(0, 2, 88).tolist()
    frame = add_crc(msg)
    print("random message with CRC added passes:", crc_ok(frame))
    frame[40] ^= 1
    print("same message with one bit flipped passes:", crc_ok(frame))