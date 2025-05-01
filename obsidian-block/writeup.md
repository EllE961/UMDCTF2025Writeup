# Obsidian Block

## Challenge
> We've discovered a strange encryption scheme that seems to be inspired by Minecraft's toughest block. The creator left us a known plaintext/ciphertext pair along with an encrypted flag. Can you break the cipher and mine your way to the flag?

## Files
- Python script implementing a custom block cipher
- Known plaintext/ciphertext pair
- Encrypted flag

## Solution
The challenge featured a simple block cipher with 24 rounds of:
1. Adding a key (modulo 2^256)
2. Rotating the state by a constant amount

Key insight: Since the operations are just modular addition and rotations, there's a linear relationship between plaintexts and ciphertexts.

Instead of recovering the key, I:
1. Undid all rotations for both ciphertexts
2. Calculated the difference between them
3. Applied that difference to the known plaintext

After fixing some corrupted output bytes, I extracted the flag.

## Flag
`UMDCTF{diamond_pickaxe_no_way!!}` 