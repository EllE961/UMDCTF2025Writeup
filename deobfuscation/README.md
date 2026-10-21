# Deobfuscation

UMDCTF 2025, rev. A statically linked, stripped ELF that asks for a password and prints the
flag when you get it right. The whole program is hand-written syscalls, so there is nothing to
deobfuscate once you read the `.text`.

## The check

`objdump -d` shows the entire logic in about 50 instructions. It writes a prompt, reads up to
0x80 bytes of input with a `read` syscall into `0x40209c`, then runs two loops:

```asm
; loop 1: transform the input
401039:  mov al, [rcx+0x40209c]   ; input byte
40103f:  cmp al, 0xa              ; stop at newline
401043:  xor al, [rcx+0x402034]   ; XOR with the key at 0x402034
401049:  mov [rcx+0x40211c], al   ; store the transformed input

; loop 2: compare against the expected block at 0x402000
401057:  mov al, [rcx+0x402000]
401061:  mov bl, [rcx+0x40211c]
401067:  cmp al, bl               ; must match for all 0x34 bytes
```

So the program computes `input XOR key` and compares it with a fixed 52-byte block. The input
that passes is `expected XOR key`, and that is the flag itself. Both blocks sit in `.data`:
`expected` at `0x402000` and `key` at `0x402034`.

## Solve

No debugger needed. `solve.py` reads the two 52-byte blocks straight out of the ELF `.data`
section and XORs them:

```python
expected = read_elf(PATH, 0x402000, 52)
key      = read_elf(PATH, 0x402034, 52)
flag = bytes(a ^ b for a, b in zip(expected, key))
```

```text
$ python3 solve.py
UMDCTF{r3v3R$E-i$_Th3_#B3ST#_4nT!-M@lW@r3_t3chN!Qu3}
```

## Flag

```text
UMDCTF{r3v3R$E-i$_Th3_#B3ST#_4nT!-M@lW@r3_t3chN!Qu3}
```

## Files

```text
flag       the challenge binary (Linux x86-64, static, stripped)
solve.py   reads the expected and key blocks from .data and XORs them
```
