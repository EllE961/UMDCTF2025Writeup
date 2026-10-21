# Gambling2

UMDCTF 2025, pwn. A 32-bit guessing game with a stack buffer overflow in its input parser.

## The bug

`gamble()` declares `float f[4]` but reads seven values into it:

```c
float f[4];
float target = rand_float();
scanf(" %lf %lf %lf %lf %lf %lf %lf", f, f+1, f+2, f+3, f+4, f+5, f+6);
```

Two problems compound. The format is `%lf` (an 8-byte double) writing into a 4-byte `float`
array, and there are seven of them for a four-element array. Writing the 7th double at `f+6`
lands on the saved return address of `gamble()`. `print_money()` is compiled in and calls
`system("/bin/sh")`, even though the win path has its call commented out, so overwriting the
return address with its address is enough.

`scanf("%lf")` copies the raw IEEE-754 bytes of whatever number you type, so any address can be
delivered by choosing the double with that bit pattern.

## Solve

`print_money` is at `0x080492c0`. Packing it into the high 32 bits of a double (with padding in
the low 32) gives a value `scanf` will write verbatim onto the return slot. `solve.py` builds
it and checks the encoding against the binary's own symbols:

```text
$ python3 solve.py gambling
print_money = 0x080492c0
crafted double = 4.8678447495872505e-270
payload = 0 0 0 0 0 0 4.8678447495872505e-270
encoded address matches print_money
remote: nc challs.umdctf.io 31005, send the payload, then `cat flag.txt`
```

The payload is six throwaway doubles and the crafted one. Six benign guesses miss `target`, the
game prints `Aww dang it!`, and then `gamble()` returns into `print_money` for a shell. The
UMDCTF server is offline now, so this is the verified payload rather than a live capture; the
binary is 32-bit and needs 32-bit libraries to run locally.

## Flag

```text
UMDCTF{99_percent_of_pwners_quit_before_they_get_a_shell_congrats_on_being_the_1_percent}
```

## Files

```text
gambling     the challenge binary (Linux x86, 32-bit, not stripped)
gambling.c   the provided source
solve.py     builds the payload and verifies the encoded return address
play.py      the pwntools version I ran against the live server
```
