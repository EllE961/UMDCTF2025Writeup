#!/usr/bin/env python3
"""Recover the obsidian-block flag with a key-cancelling differential.

The cipher runs 24 rounds of block = rotate_right(block + key, r_i) with the same key every
round. We have one known plaintext p1 with its ciphertext c1, and the flag's ciphertext c2.

Undo all the rotations on both ciphertexts. Just before each rotation both messages had the
same key added, so subtracting the two unrotated states cancels the key and leaves the
difference of the two plaintexts. Add that to the known plaintext to recover the flag. The
one wrinkle: rotation does not commute with mod-2^256 subtraction, so each rotation can flip a
few bits through carries. The recovered string is therefore right except for a handful of
bytes, which are clear from the UMDCTF{...} format and the challenge theme.

    python3 solve.py
"""
from Crypto.Util.number import bytes_to_long, long_to_bytes

ROUND_CONSTANTS = [3, 141, 59, 26, 53, 58, 97, 93, 23, 84, 62, 64, 33, 83,
                   27, 9, 50, 28, 84, 197, 169, 39, 93, 75]
M = 2 ** 256

# from output.txt
c1 = 19970192951896076587357270489167937916618022198129516743091736664525698125224
c2 = 78876026922201259108741049564691635166471597880603787944801336451046144103203
p1 = bytes_to_long(b"please like and subscribe!!!!!!!")


def inv_rot(n, r):
    return ((n << r) | (n >> (256 - r))) & (M - 1)


def main():
    a, b = c1, c2
    for r in reversed(ROUND_CONSTANTS):
        a, b = inv_rot(a, r % 256), inv_rot(b, r % 256)
    diff = (b - a) % M
    recovered = long_to_bytes((p1 + diff) % M)
    readable = "".join(chr(x) if 32 <= x < 127 else "." for x in recovered)
    print("recovered:", readable)


if __name__ == "__main__":
    main()
