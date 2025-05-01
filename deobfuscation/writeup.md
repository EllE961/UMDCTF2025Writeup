# Deobfuscation

## Challenge
> Someone sent us this suspicious binary that asks for a password. We believe it contains a hidden flag, but the code appears to be obfuscated. Can you reverse engineer it and extract the flag?

## Files
- `flag` - Binary that asks for a password

## Solution
The binary compares our input with an expected value after XORing it with a specific key.

Used GDB to dump the memory:
```
$ gdb ./flag
pwndbg> break *0x401000
pwndbg> run
pwndbg> x/52xb 0x402000  # Expected value
pwndbg> x/52xb 0x402034  # XOR key
```

Created a Python script to XOR the values:
```python
expected = [
    0x20, 0x22, 0x20, 0x26, 0x35, 0x37, 0x14, 0x07,
    # ... (rest of the bytes)
]

key = [
    0x75, 0x6f, 0x64, 0x65, 0x61, 0x71, 0x6f, 0x75,
    # ... (rest of the bytes)
]

flag = ''
for i in range(min(len(expected), len(key))):
    flag += chr(expected[i] ^ key[i])

print(flag)
```

## Flag
`UMDCTF{r3v3R$E-i$_Th3_#B3ST#_4nT!-M@lW@r3_t3chN!Qu3}` 