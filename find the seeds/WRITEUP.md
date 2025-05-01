# find the seeds – super-short write-up

1. **Read the code**  
   `secret.py` shows the flag is XOR-encrypted with a keystream from Python's `random` seeded by `int(time.time())`.

2. **Get the seed window**  
   Check the ciphertext's modification time:
   ```bash
   stat -c '%Y' secret.bin   # → 1745651772 (26 Apr 2025 07:16 UTC)
   ```
   The RNG seed must be around this Unix timestamp.

3. **Brute-force nearby seeds**  
   ```python
   for seed in range(ts-100000, ts+1):
       random.seed(seed)
       if cipher[:7] ^ keystream[:7] == b'UMDCTF{':
           decrypt and done
   ```
   Optimisation: only test the first 7 bytes (`"UMDCTF{"`).

4. **Success**  
   Seed `1745447710` works. Full decryption gives:
   ```
   UMDCTF{pseudo_entropy_hidden_seed}
   ```

*(whole process took ~2 seconds)* 