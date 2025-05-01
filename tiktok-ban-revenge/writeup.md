# TikTok Ban Revenge Write-up

## Challenge

President Trump's delay on the TikTok ban ran out! We need to bypass the filter to get the flag.

## Solution

Looking at the `filter.py` file, I noticed the server was checking for the string `tiktok.com` in DNS queries:

```python
if b'tiktok\x03com' in req.lower():
    print("Sorry, TikTok isn't available right now...")
else: 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(req, (dns_ip_addr, dns_port))
    resp = sock.recv(1024)
    print(resp)
```

The interesting thing was that the flag was stored in a TXT record for tiktok.com:

```python
subprocess.run(['/app/dnsmasq', '-x', 'dnsmasq.pid', '-p', f'{dns_port}', 
               '--txt-record', f'tiktok.com,{flag}'])
```

So I needed to query for tiktok.com without having the bytes `tiktok\x03com` in my request.

DNS has this neat feature called compression pointers that let you reference parts of a domain name instead of repeating them. I used this to split up the domain:

```python
header = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
qname_part1 = b'\x06tiktok'  # Label "tiktok"
pointer = b'\xc0\x1a'        # Pointer to offset 26
qtype = b'\x00\x10'          # TXT record
qclass = b'\x00\x01'         # IN class
padding = b'\x00'            # Padding byte
pointer_target = b'\x03com\x00'  # Label "com" at offset 26
```

When the DNS server processed this query, it would follow the pointer and reconstruct "tiktok.com", but the string `tiktok\x03com` never actually appears in the request bytes!

Running the script gave me the flag:

```
UMDCTF{we_remembered_pointer_compression_but_forgor_about_case_insensitivity_:skull:}
```

The flag name is kinda funny because it references the fact that the filter used `.lower()` to catch both uppercase and lowercase, but DNS compression pointers were a more effective bypass. 