#!/usr/bin/env python3
"""Recover the find-the-seeds flag by brute-forcing the RNG seed.

secret.py XORs the flag with a keystream from Python's `random`, seeded with
`int(time.time())` at generation time. The seed is therefore a Unix timestamp near when
the file was made (UMDCTF 2025, late April). Only the first 7 bytes of the keystream need
checking, since the plaintext starts with "UMDCTF{".

    python3 solve.py                       # search the event window
    python3 solve.py 1745400000 1745500000 # custom [start, end)
"""
import random
import sys

CT = open("secret.bin", "rb").read()
START = int(sys.argv[1]) if len(sys.argv) > 2 else 1_745_400_000   # 2025-04-23
END = int(sys.argv[2]) if len(sys.argv) > 2 else 1_745_500_000     # 2025-04-24


def main():
    for seed in range(START, END):
        random.seed(seed)
        prefix = bytes(random.getrandbits(8) for _ in range(7))
        if bytes(c ^ k for c, k in zip(CT[:7], prefix)) != b"UMDCTF{":
            continue
        rest = bytes(random.getrandbits(8) for _ in range(len(CT) - 7))
        flag = bytes(c ^ k for c, k in zip(CT, prefix + rest))
        if flag.endswith(b"}"):
            print(f"seed = {seed}")
            print(flag.decode())
            return
    print("no seed in range")


if __name__ == "__main__":
    main()
