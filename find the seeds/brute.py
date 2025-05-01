import random, os, sys

ct = open('secret.bin', 'rb').read()
# search range of seeds across few years
start = 1600000000  # Sep 2020
end = 1800000000    # 2027

for seed in range(start, end):
    random.seed(seed)
    ks_prefix = bytes(random.getrandbits(8) for _ in range(7))
    # quickly discard seeds whose first 7 bytes don't match
    if bytes(c ^ k for c, k in zip(ct[:7], ks_prefix)) != b'UMDCTF{':
        continue
    # If prefix matches, generate full keystream
    ks_full = ks_prefix + bytes(random.getrandbits(8) for _ in range(len(ct)-7))
    pt = bytes(c ^ k for c, k in zip(ct, ks_full))
    if pt.startswith(b'UMDCTF{') and pt.endswith(b'}'):
        print('Found seed:', seed)
        print('Flag:', pt.decode())
        break
else:
    print('Seed not found in range') 