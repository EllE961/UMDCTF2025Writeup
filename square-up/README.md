# Square up

UMDCTF 2025, crypto. Rabin encryption where the organizer's own decrypt function has a
copy-paste bug, and the bug leaks the factorization of N.

## The bug

`main.py` encrypts the flag as `c = m^2 mod N` with `N = p*q`, both primes `3 mod 4`, and ships
two Legendre-symbol hints `lp`, `lq`. Decryption uses the CRT to pick the right square root in
each prime:

```python
if (pow(mp, (p-1)//2, p) - lp) % p != 0: mp = p - mp
if (pow(mq, (q-1)//2, q) - lq) % q != 0: mq = q - mq
```

Those two lines look identical, and that is the problem. The `output.txt` was produced by this
code with one branch flipped: the printed "plaintext" is a valid square root of `c` modulo `p`
but not modulo `q`. Call it `M_bug`. Then `M_bug^2 == c (mod p)` but `M_bug^2 != c (mod q)`, so
`M_bug^2 - c` is a multiple of `p` but not of `q`:

```text
gcd(M_bug^2 - c, N) = p
```

## Solve

`dec.py` reads the bogus plaintext from `output.txt`, factors N with one `gcd`, then runs the
correct decryption:

```python
Mbug = int(hexstr, 16)
p = gcd(pow(Mbug, 2, N) - c, N)
q = N // p
# ... correct CRT square-root recombination
m = (yp*p*mq + yq*q*mp) % N
```

```text
$ python3 dec.py
p 34711555674628372935877870485835537391965309871231041302486152071221601049400693172940376921292242854663584986631327
q 37413789950213192073940436937314328134246348255889223903991743662572864462102604110127423471348237792553585637291579
check True
b'UMDCTF{e=3_has_many_attacks_and_e=2_has_its_own_problems...maybe_we_should_try_e=1_next?}'
```

## Flag

```text
UMDCTF{e=3_has_many_attacks_and_e=2_has_its_own_problems...maybe_we_should_try_e=1_next?}
```

## Files

```text
main.py      the challenge: Rabin encrypt/decrypt with the buggy branch
output.txt   N, (c, lp, lq), and the bogus plaintext
dec.py       factors N from the bogus root and decrypts
```
