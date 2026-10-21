#!/usr/bin/env python3
"""Recover the deobfuscation flag straight from the binary, no debugger needed.

The password check XORs 52 expected bytes at .data 0x402000 with a 52-byte key at 0x402034
and compares against the input. XOR the two blocks and the flag falls out.

    python3 solve.py          # reads ./flag
"""
import struct
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "flag"
EXPECTED, KEY, LENGTH = 0x402000, 0x402034, 52


def read_elf(path, vaddr, n):
    data = open(path, "rb").read()
    e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
    e_shentsize, e_shnum = struct.unpack_from("<HH", data, 0x3A)
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        sh_addr, sh_offset, sh_size = struct.unpack_from("<QQQ", data, off + 0x10)
        if sh_addr <= vaddr < sh_addr + sh_size:
            start = sh_offset + (vaddr - sh_addr)
            return data[start:start + n]
    raise ValueError(f"no section contains {vaddr:#x}")


def main():
    expected = read_elf(PATH, EXPECTED, LENGTH)
    key = read_elf(PATH, KEY, LENGTH)
    flag = bytes(a ^ b for a, b in zip(expected, key))
    print(flag.decode())


if __name__ == "__main__":
    main()
