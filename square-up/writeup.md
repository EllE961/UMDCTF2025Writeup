# square-up (crypto) — UMDCTF 2024  
flag: `UMDCTF{e=3_has_many_attacks_and_e=2_has_its_own_problems...maybe_we_should_try_e=1_next?}`

---
### TL;DR
The organiser's decrypt function flips the wrong square root for `q`, so the value they printed (`M_bug`) is only a valid √c mod *p*.  
`gcd(M_bug² − c, N)` therefore leaks *p*, we get *q = N/p* and can decrypt with the fixed branch.

---
### Steps
1. Copy the bogus plaintext from `output.txt` and turn it into an integer:
   ```python
   M_bug = int(b"1b52…380f", 16)
   ```
2. One line factorisation:
   ```python
   p = gcd((M_bug*M_bug - c) % N, N)
   q = N // p
   ```
3. Patch the bug (should use `mq = q - mq`, not `q - mp`) and decrypt:
   ```python
   …
   if (pow(mq,(q-1)//2,q)-lq) % q:  mq = q - mq
   m = (yp*p*mq + yq*q*mp) % N
   ```
4. Convert `m` to bytes – the flag pops out.

Whole exploit fits in 15 lines of Python; no heavy math required, just a `gcd`. 