from crc import hex_to_bits, bits_to_int, crc_ok

CHARSET = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######"


def get_df(bits):
    """Downlink format: the first 5 bits (17 = ADS-B)."""
    return bits_to_int(bits[0:5])


def get_icao(bits):
    """24-bit aircraft address, as a 6-digit hex string."""
    return format(bits_to_int(bits[8:32]), "06X")


def get_type_code(bits):
    """First 5 bits of the 56-bit data part (which starts at bit 32)."""
    return bits_to_int(bits[32:37])


def decode_callsign(bits):
    """Aircraft identification (type codes 1-4): eight 6-bit characters after the first 8 data bits."""
    chars = []
    for i in range(8):
        start = 40 + 6 * i
        chars.append(CHARSET[bits_to_int(bits[start:start + 6])])
    return "".join(chars).replace("_", "").replace("#", "").strip()


def decode_altitude(bits):
    """Altitude in feet for airborne position messages (type codes 9-18), or None."""
    alt_field = bits[40:52]                    # 12 bits
    q_bit = alt_field[7]
    if q_bit == 1:
        n = bits_to_int(alt_field[:7] + alt_field[8:])   # remove the Q bit, 11 bits left
        return n * 25 - 1000
    return None                                # older Gillham coding, not handled here


def describe(hex_string):
    bits = hex_to_bits(hex_string)
    if not crc_ok(bits):
        return "rejected: CRC failed"
    if get_df(bits) != 17:
        return f"not ADS-B (DF {get_df(bits)})"
    tc = get_type_code(bits)
    text = f"ICAO {get_icao(bits)}, type code {tc}"
    if 1 <= tc <= 4:
        text += f", callsign {decode_callsign(bits)}"
    elif 9 <= tc <= 18:
        text += f", altitude {decode_altitude(bits)} ft"
    elif tc == 19:
        text += ", velocity message (not decoded yet)"    
    return text


if __name__ == "__main__":
    for msg in ["8D4840D6202CC371C32CE0576098",   # identification message
                "8D40621D58C382D690C8AC2863A7",   # airborne position message
                "8D4840D6202CC371C32CE0576099",   # same as the first, last digit damaged
                "8D485020994409940838175B284F"]:  # velocity message
        print(msg, "->", describe(msg))