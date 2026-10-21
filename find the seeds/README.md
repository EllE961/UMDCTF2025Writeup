# Find the seeds

UMDCTF 2025, crypto. The flag is XORed with a keystream from Python's `random`, and the whole
key is one integer: the seed.

## The weakness

`secret.py` seeds the RNG with the wall clock and XORs the flag with 34 keystream bytes:

```python
seed = int(time.time())
random.seed(seed)
keystream = bytes([random.getrandbits(8) for _ in range(len(plaintext))])
ciphertext = bytes([p ^ k for p, k in zip(plaintext, keystream)])
```

`int(time.time())` is a Unix timestamp, so the seed is not secret, it is a number near when the
file was generated. UMDCTF 2025 ran in late April, which pins the seed to a window of a few
hundred thousand values. Only the first 7 bytes need checking, because the plaintext starts
with `UMDCTF{`.

## Solve

`solve.py` walks one day of timestamps, testing the 7-byte prefix and only expanding the full
keystream on a hit:

```python
for seed in range(START, END):
    random.seed(seed)
    prefix = bytes(random.getrandbits(8) for _ in range(7))
    if bytes(c ^ k for c, k in zip(CT[:7], prefix)) != b"UMDCTF{":
        continue
    rest = bytes(random.getrandbits(8) for _ in range(len(CT) - 7))
    flag = bytes(c ^ k for c, k in zip(CT, prefix + rest))
```

```text
$ python3 solve.py
seed = 1745447710
UMDCTF{pseudo_entropy_hidden_seed}
```

The search covers 100,000 seeds and finishes in under three seconds. The matching seed,
1745447710, is 2025-04-23 20:15 UTC.

## Flag

```text
UMDCTF{pseudo_entropy_hidden_seed}
```

## Files

```text
secret.py     the challenge generator (seed = int(time.time()), XOR keystream)
secret.bin    the 34-byte ciphertext
solve.py      brute-forces the seed over the event window
brute.py      the wider-range version I ran during the event
```
