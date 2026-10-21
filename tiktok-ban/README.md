# TikTok ban

UMDCTF 2025, misc. A DNS proxy that blocks lookups of tiktok.com, where the flag lives in a TXT
record. The block is case-sensitive but DNS names are not.

## The filter

The proxy forwards a DNS query to a backend only if the query does not contain the exact bytes
`tiktok\x03com` (a label-length byte, "tiktok", then "com"). The check is a case-sensitive
`in` test, but DNS treats names case-insensitively, so the backend resolves `TiKToK.com` and
`tiktok.com` to the same record.

## Solve

Encode the name as `TiKToK` instead of `tiktok`. The literal `tiktok\x03com` never appears in
the request bytes, but the resolver still answers for tiktok.com:

```python
domain_parts = ["TiKToK", "com"]   # qname becomes \x06TiKToK\x03com\x00
```

```text
>>> qname = b'\x06TiKToK\x03com\x00'
>>> b'tiktok\x03com' in qname            # the filter's case-sensitive check
False
>>> b'tiktok\x03com' in qname.lower()    # what it should have checked
True
```

`solve.py` sends a TXT query for that name over TCP and reads the flag out of the answer. The
UMDCTF service is offline now, so the local check above is the part that reproduces; the query
itself is a standard TXT lookup.

## Flag

```text
UMDCTF{W31C0M3_84CK_4ND_7H4NK5_F0r_Y0Ur_P4713NC3_4ND_5UPP0r7_45_4_r35U17_0F_Pr351D3N7_7rUMP_71K70K_15_84CK_1N_7H3_U5}
```

## Files

```text
solve.py   builds the TiKToK TXT query and reads the flag from the response
```
