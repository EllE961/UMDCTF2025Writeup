# Alien transmission

UMDCTF 2025, misc. A flag image blurred by a random convolution kernel, with the kernel's seed
sitting in the generator script.

<img src="../docs/assets/alien-recovered.png" alt="Deblurred transmission: a sphynx cat with the text UMDCTF{gl33p_gl0rp} across the middle" width="60%">

## The blur

`gen.py` reads `flag.png`, builds a 19x19 kernel from `random.seed(420)`, normalizes it, and
convolves the green channel:

```python
random.seed(420)
kernel = [[float(random.randint(-10, 10)) for _ in range(19)] for _ in range(19)]
kernel = [[a / q for a in r] for r in kernel]   # q = sum of all entries
# ... convolve, map (-10, 10) -> (0, 256), save output.png
```

The kernel is fully determined by the seed, which is printed right there in the script, so it
can be rebuilt exactly.

## Solve

`kernel_final.py` reconstructs the same kernel, then sharpens `output.png` by convolving the
green channel with a center-boosted copy of the kernel (the center 3x3 scaled up), inverting
(`255 - pixel`), and raising contrast. Boosting the center counteracts the blur's spread and
pulls the strokes back together. The flag text and a sphynx cat come out of the noise, shown
above (`final_auto.png`). The threshold sweeps in the folder are the same result binarized at
different cutoffs to make the text pop.

The challenge download was `output.png`; it is not in this repo, so `kernel_final.py` needs that
file to rerun. The recovered image is kept as `final_auto.png`.

## Flag

```text
UMDCTF{gl33p_gl0rp}
```

## Files

```text
gen.py                 the challenge generator (seed 420 kernel, convolve, save output.png)
kernel_final.py        rebuilds the kernel and sharpens output.png
boost_kernel_center.py the center-boost experiments
final_auto.png         the recovered image with the flag
center_boost_*.png     kernel and contrast sweeps
final_pattern_*.png    threshold sweeps of the recovered text
```
